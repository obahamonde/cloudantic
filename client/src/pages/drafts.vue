<script setup lang="ts">
const { state } = useStore();
</script>
<template>
<div v-if="!state.user">...</div>
<div v-else>
<MyPosts :user="state.user"/>
</div>
</template>