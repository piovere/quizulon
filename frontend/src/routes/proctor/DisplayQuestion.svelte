<script>
    let { question } = $props();
</script>

<div>
    <div class="question">{@html question.text}</div>
    {#each question.choices as choice}
    <div class="choice">{choice.text}</div>
    {/each}
</div>

<style>
    div.question {
        border-radius: 1rem;
        padding: 10px;
        margin: 5px;
        outline: 1px solid;
    }
    div.choice {
        border-radius: 1rem;
        padding: 10px;
        margin: 5px;
        outline: 1px solid;
    }
</style>