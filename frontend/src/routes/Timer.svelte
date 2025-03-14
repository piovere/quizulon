<script>
    let { time } = $props();
</script>

<svg xmlns="http://www.w3.org/2000/svg" height="30" width="95%" viewbox="0 0 100 1">
<rect width="100" height="1" rx="1" fill="gray"></rect>
<rect width="100" height="1" rx="1" fill="blue" transform="scale(1 1)">
    <animateTransform 
        attributeName="transform"
        attributeType="XML"
        type=scale
        from="0 1"
        to="1 1"
        dur="{time}ms"
        repeatCount=0 />
</rect>
</svg>
