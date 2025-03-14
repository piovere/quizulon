<script lang="ts">
    import { getAbsoluteUrl } from "$lib/absolute";
    import { onMount } from 'svelte';
    import QrCode from 'svelte-qrcode';
    import type { PageData } from './$types';

    import DisplayQuestion from '../DisplayQuestion.svelte';

    var currentQuestionId: number = $state(1);
    let learnerURL: string = $state('');
    var messages: Message[] = $state([]);
    var questions: Question[] = $state([]);
    var learners: Learner[] = $state([]);
    var data: Data = $state();

    let time: number = 60 * 1000;

    let dumbq: Question = {
        "message_type": "Question",
        "id": 42,
        "text": "<p>I hate this stuff</p><p>Don't you?</p>",
        "choices": [
            {
                "id": 99,
                "text": "Reassurance only",
                "correct": false,
                "message_type": "Choice"
            },
            {
                "id": 101,
                "text": "Dalmations",
                "correct": true,
                "message_type": "Choice"
            }
        ]
    }

    var currentQuestion = $derived(questions.length === 0 ? dumbq : questions[questions.length - 1]);

    let ws: WebSocket = new WebSocket(`ws://localhost:8000/ws/proctor/`);

    ws.onmessage = function(event) {
        let msg: Message = JSON.parse(event.data);
        switch (msg.message_type) {
            case "Question":
                questions.push(msg as Question);
                break;
            case "Learner":
                learners.push(msg as Learner);
            case "Data":
                data = msg as Data;
        }
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
    <div>
        <ul>
        {#each learners as learner}
        <li>{learner.learner_name}</li>
        {/each}
        </ul>
    </div>
    <button onclick={sendMessage}>Start the quiz!</button>
    {:else}
    {@const q = (currentQuestion as Question)}
    <DisplayQuestion question={q} {time} />
    {/if}
    <div>{data}</div>
</main>
