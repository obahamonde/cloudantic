<script setup lang="ts">
import type { User } from "~/types";
const showChat = ref(false);
const props = defineProps<{
	user: User;
}>();
const { modelValue } = defineModels<{
	modelValue: string;
}>();
</script>
<template>
<img src="/chatbot.svg" class="x4 br fixed cp scale m-4" @click="showChat = !showChat" />

<Modal v-if="showChat" @close="showChat = false">
<template #body>
  <ChatBotComponent :user="props.user" v-model="modelValue" />
</template>
</Modal>
</template>