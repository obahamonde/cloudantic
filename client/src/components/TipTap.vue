<script setup lang="ts">
import { useEditor, EditorContent } from "@tiptap/vue-3";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import Image from "@tiptap/extension-image";
import { User, Post } from "../types";
const { request } = useRequest<Post>()

const props = defineProps({
  user: {
    type: Object as PropType<User>,
    required: true,
  },
});

const body = reactive<Post>({
  title: "",
  content: computed(() => editor.value?.getHTML() ?? ""),
  user: props.user.sub,
  namespace:"",
  created_at: new Date().toISOString(),
});




const editor= useEditor({
  extensions: [
    StarterKit,
    Link.configure({ openOnClick: true }),
    Image.configure(),
  ],
  content: '',
});


const onTab = (e: KeyboardEvent) => {
  e.preventDefault();
  if (!editor.value) return;
  editor.value.chain().insertContent("    ").run();
};

const savePost = async ()=>{
  if (!editor.value) return;
  if (!body.title) return;
  if (!body.namespace) return;
  if (!body.content) return;
    await request("/api/post",{
     method: "POST",
      body: JSON.stringify(body),
      headers: {
        "Content-Type": "application/json",
      },
  },true)
}
</script>
<template>  
<div class="m-4 w-auto text-center ">
  <p class="col center w-full ">
  
  <Input v-model:model-value="body.namespace" placeholder="Namespace" />
    <Input v-model:model-value="body.title" placeholder="Title" />
  
  <Icon icon="mdi-floppy" class="btn-icon" @click="savePost"/> 
</p>
  <EditorContent
       class="tiptap min-w-256 max-w-300 overflow-auto h-60vh markdown-body text-black p-4 rounded"
      :editor="editor"
      @keydown.tab="onTab"
      />
  </div>
</template>
<style lang="scss">

/* Basic editor styles */
.tiptap {
  > * + * {
    margin-top: 0.75em;
    overflow: auto;
  }
  img {
    max-width: 20%;
  }
}


</style>