<script lang="ts">
    import { getAbsoluteUrl } from "$lib/absolute";
    import { onMount } from 'svelte';
    import QrCode from 'svelte-qrcode';
    import type { PageData } from './$types';

    import DisplayQuestion from './DisplayQuestion.svelte';

    var currentQuestionId: number = $state(1);
    let learnerURL: string = $state('');
    var messages: Message[] = $state([]);

    let time: number = 6 * 1000;

    let dumbq: Question = {
        "id": 42,
        "text": "<p>I hate this stuff</p><p>Don't you?</p>",
        "choices": [
            {
                "id": 99,
                "text": "Reassurance only",
                "correct": false
            },
            {
                "id": 101,
                "text": "Dalmations",
                "correct": true
            }
        ]
    }

    var currentQuestion = $derived(messages.length === 0 ? dumbq : messages[messages.length - 1]);

    let ws: WebSocket = new WebSocket(`ws:localhost:8000/ws/proctor/`);

    ws.onmessage = function(event) {
        let newQuestion: Question = JSON.parse(event.data) as Question;
        console.log(JSON.parse(event.data));
        messages.push(newQuestion);
        setTimeout(sendMessage, time);
    }

    function sendMessage() {
        let msg = {
            message_type: "Question",
            id: currentQuestionId
        };
        ws.send(JSON.stringify(msg));
        currentQuestionId += 1;
    }

    onMount(() => {
        learnerURL = getAbsoluteUrl('/learner/');
    });
</script>

<main>
    {#if messages.length === 0}
    <p>This webpage is at { learnerURL }</p>
    <div id='qr'>
        <QrCode value={learnerURL} />
        <p>Link to <a href={learnerURL}>quiz page</a></p>
    </div>
    <button onclick={sendMessage}>Start the quiz!</button>
    {:else}
    {@const q = (currentQuestion as Question)}
    <DisplayQuestion question={q} {time} />
    {/if}
</main>
