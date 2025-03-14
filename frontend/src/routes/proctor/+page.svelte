<script lang="ts">
    import { getAbsoluteUrl } from "$lib/absolute";
    import { onMount } from 'svelte';
    import QrCode from "svelte-qrcode";

    import DisplayQuestion from './DisplayQuestion.svelte';

    var currentQuestionId: number = $state(1);
    let learnerURL: string = $state('');
    var messages: Message[] = $state([]);

    let ws: WebSocket = new WebSocket(`ws:localhost:8000/ws/proctor/`);

    ws.onmessage = function(event) {
        let newQuestion: Question = JSON.parse(event.data);
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
</main>
