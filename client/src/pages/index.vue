<script setup lang="ts">
useTitle('Home')
useFavicon("/favicon.png")
</script>
<template>


<Request url="/api" v-slot="data">
<h1 class="text-title invert dark:filter-none">{{ data.message }}</h1>
</Request>
<Landing/>
</template>

<route lang="yaml">
  meta:
    layout: home
</route>