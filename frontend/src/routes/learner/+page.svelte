<script lang="ts">
    import type { PageData } from './$types';
    import { v4 as uuidv4} from 'uuid';

    let { data }: { data: PageData } = $props();

    let id = uuidv4();
    let name: string = $state('');
    let registered = $state(false);
    let message = $state({"learner_id": id})
    let connected = $state(false)

    let ws: WebSocket = new WebSocket(`ws://localhost:8000/ws/learner/${id}`);

    ws.onopen = (event) => {
        connected = true;
    };

    let register = function() {
        ws.send(JSON.stringify({
            message_type: "Learner",
            learner_id: id,
            learner_name: name
        }));
        registered = true;
    };

    ws.onmessage = function(event) {
        // if !registered {}
    }
</script>

<div>
    <input type="text" bind:value={name} />
    <button onclick={register}>Register</button>
</div>


