<script setup lang="ts">
const text= ref("");
</script>

<template>
<Auth v-slot="{ user }">
<img :src="user.picture" class="x4 tr m-4 fixed rf sh scale cp" />
<Chatbot :user="user" v-model="text" />
<SideBar />
 <main class="flex min-h-screen overflow-auto flex-col items-center justify-between p-4">
    <RouterView />
   </main>
</Auth>
</template>
