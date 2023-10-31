<script setup lang="ts">
import type { User, Message } from "~/types";

const props = defineProps<{
	user: User;
}>();
const { state } = useStore();
const { modelValue } = defineModels<{
	modelValue: string;
}>();

const handleSend = ( data:string) => {
	state.messages[0].content = data
};

onMounted(async()=>{
  const res = await fetch('/api/chatlist/' + props.user.sub)
  const data = await res.json() as Message[]
  state.messages = data.reverse()
}
)

const handleEnter = () => {
	state.messages.unshift({ role: "user", content: unref(modelValue) });
	state.messages.unshift({ role: "assistant", content: "" });
	showEvent.value = true
};
const handleDone = async() => {
  modelValue.value = ""; 
  showEvent.value = false
};

const showEvent = ref(false)
</script>
<template>
<section class="col center">
<div class="sticky top-4 dark:bg-black bg-white sh rounded w-96">
<Input v-model:modelValue="modelValue" :onEnter="handleEnter" :disabled="showEvent"  />	
</div>
<div class="chat-wrapper w-full  max-w-168">
    <div class="message-wrapper  max-w-168">
      <div class="chat-wrapper  min-w-128">
        <ServerEvent
          :url="
            '/api/chat/' +
            props.user.sub +
            '?text=' +
            modelValue 
          "
          v-if="showEvent"
          @done="handleDone()"
          @close="showEvent = false"
          @send="handleSend($event)"
        >

        </ServerEvent>
      </div>
    </div>
	</div>
<div class="flex flex-col items-center justify-center space-y-2" v-for="message in state.messages">
<ChatMessage :content="message.content" :reverse="message.role === 'user'" :image="message.role === 'user' ? props.user.picture! : '/chatbot.svg'" />
</div>
</section>
</template>