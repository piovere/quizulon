<script lang="ts">
    import { getAbsoluteUrl } from "$lib/absolute";
    import { onMount } from 'svelte';
    import QrCode from 'svelte-qrcode';
    import type { PageData } from './$types';

    import DisplayQuestion from './DisplayQuestion.svelte';

    var currentQuestionId: number = $state(1);
    let learnerURL: string = $state('');
    var messages: Message[] = $state([]);

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

    let currentQuestion: Question = $state(dumbq);

    let ws: WebSocket = new WebSocket(`ws:localhost:8000/ws/proctor/`);

    ws.onmessage = function(event) {
        let newQuestion: Question = JSON.parse(event.data);
        console.log(JSON.parse(event.data))
        currentQuestion = newQuestion;
        messages.push(newQuestion);
    }

    function sendMessage() {
        let msg = {
            message_type: "Question",
            id: currentQuestionId
        };
        ws.send(JSON.stringify(msg));
    }

    onMount(() => {
        learnerURL = getAbsoluteUrl('/learner/');
    });
</script>

<main>
    <h1>Hello There!</h1>
    <p>This webpage is at { learnerURL }</p>
    <div id='qr'>
        <QrCode value={learnerURL} />
        <p>Link to <a href={learnerURL}>quiz page</a></p>
    </div>
    <input type="number" id="messageText" autocomplete="off" min=1 max=6 bind:value={currentQuestionId} />
    <button onclick={sendMessage}>Send</button>
    <ul id="messages">
        {#each messages as question: Question}
        {@const qid = (question as Question)['id']}
        {@const qtext = (question as Question)['text']}
        {console.log(qid)}
        {console.log(qtext)}
        <li>{qid}: {qtext}</li>
        {/each}
    </ul>
    {#if messages.length > 0}
    {@const q = (messages[0] as Question)}
    <DisplayQuestion question={dumbq} />
    {/if}
</main>
