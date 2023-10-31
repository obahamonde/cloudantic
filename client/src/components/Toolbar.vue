<script setup lang="ts">

</script>
<template>
<div class="flex items-center justify-between rounded-full bg-zinc-800 p-2 max-w-max">
  <div class="flex space-x-2 border-r border-zinc-600 pr-1">
    <button class="inline-flex items-center justify-center text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 w-10 text-zinc-100 rounded-full hover:bg-gray-600 hover:text-zinc-100">
      <Icon icon="mdi:plus" class="x2"/>
      <span class="sr-only">Create a comment</span>
    </button>
    <div class="relative">
      <button class="inline-flex items-center justify-center text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 w-10 text-zinc-100 relative rounded-full hover:bg-gray-600 hover:text-zinc-100">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class=" h-6 w-6 stroke-1"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path></svg>
        <span class="sr-only">Open inbox</span>
        <span class="absolute top-2 right-2 block h-2 w-2 rounded-full bg-blue-500"></span>
      </button>
    </div>
    <button class="inline-flex items-center justify-center text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 w-10 text-zinc-100 rounded-full hover:bg-gray-600 hover:text-zinc-100">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class=" h-6 w-6 stroke-1"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
      <span class="sr-only">Edit</span>
    </button>
  </div>
  <div class="flex space-x-2 border-r border-zinc-600 px-3">
    <img src="/placeholder.jpg" width="32" height="32" class="rounded-full border-2 border-red-500 bg-gray-500" alt="Avatar 1">
    <img src="/placeholder.jpg" width="32" height="32" class="rounded-full border-2 border-green-500 bg-gray-500" alt="Avatar 2">
    <div class="relative">
      <img src="/placeholder.jpg" width="32" height="32" class="rounded-full border-2 border-[#666666] bg-gray-700 opacity-50" alt="Avatar 3">
      <span class="absolute top-0 left-0 flex items-center justify-center w-full h-full text-white text-xs font-bold">9+</span>
    </div>
  </div>
  <div class="flex items-center justify-center space-x-2 pl-1">
    <button class="inline-flex items-center justify-center text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 w-10 text-zinc-100 rounded-full hover:bg-gray-600 hover:text-zinc-100">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class=" h-6 w-6 stroke-1"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path><polyline points="16 6 12 2 8 6"></polyline><line x1="12" x2="12" y1="2" y2="15"></line></svg>
      <span class="sr-only">Open share UI</span>
    </button>
    <button class="inline-flex items-center justify-center text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 w-10 text-zinc-100 rounded-full hover:bg-gray-600 hover:text-zinc-100">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class=" h-6 w-6 stroke-1"><line x1="4" x2="20" y1="12" y2="12"></line><line x1="4" x2="20" y1="6" y2="6"></line><line x1="4" x2="20" y1="18" y2="18"></line></svg>
      <span class="sr-only">Open menu</span>
    </button>
  </div>
</div>
</template>