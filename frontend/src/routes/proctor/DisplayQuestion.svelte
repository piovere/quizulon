<script>
    let { question } = $props();
</script>

<div>
    <div class="question">{@html question.text}</div>
    <div class="choicebox">
    {#each question.choices as choice}
    <button class="choice">{choice.text}</button>
    {/each}
    </div>
</div>

<style>
    div.question {
        border-radius: 1rem;
        border-width: 3px;
        padding: 10px;
        margin: 5px;
        outline: 1px solid;
        width: 90%;
        justify-content: space-evenly;
        font-size: x-large;
    }
    button.choice {
        border-radius: 1rem;
        padding: 10px;
        margin: 5px;
        outline: 1px solid;
        width: 45%;
        font-size: large;
    }
    button.choice:hover {
        background-color: rgb(0 0 0 / 0.4);
    }
    div.choicebox {
        display: flex;
        flex-direction: row;
        width: 90%;
        justify-content: space-evenly;
    }
</style>