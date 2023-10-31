<script setup lang="ts">
const { state } = useStore()
</script>
<template>
<section class="overflow-auto h-full" v-if="state.user">
<TipTap :user="state.user"  />
</section>
</template>
