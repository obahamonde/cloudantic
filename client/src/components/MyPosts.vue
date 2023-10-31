<script setup lang="ts">
import { User, Post } from "../types";
const { response, request} = useRequest<Post[]>();
const { response:userResponse, request:userRequest} = useRequest<User>();
const props = defineProps({
	user: {
		type: Object as PropType<User>,
		required: true,
	}
});
const deletePost = async (post: Post) => {
	const sk = post.namespace ? `${post.namespace},${post.created_at}` : `${post.created_at}`;
	const url  = `/api/post/${post.user.sub}?sk=${sk}`;
	await request(url, {
		method: "DELETE",
	},true);
	await fetchPosts();
};
const fetchPosts = async()=>{
	await request("/api/post/" + props.user.sub, {
		method: "GET",
	},true);
	response.value.forEach(async(p, i) => {
		await fetchUser(p.user as string)
		response.value[i].user = userResponse.value
	});
}
const fetchUser = async(sub:string)=>{
	await userRequest("/api/user/" + sub, {
		method: "GET",
	},true)
}
onMounted(fetchPosts)
</script>
<template>

<h1 class="text-2xl font-bold text-center">All Posts</h1>
<div class="flex flex-col items-center">
	<div v-for="post in response" class="col center">
		<Icon icon="mdi-delete" class="text-warning cp scale" @click="deletePost(post)" v-if="post.user.sub = props.user.sub" />
		<div class="flex flex-col items-center justify-center space-y-2">
			<h2 class="text-xl font-bold">{{ post.title }}</h2>
			<p class="text-lg">Written by {{ post.user.name }}</p>
			<p class="text-md">{{ new Date(post.created_at).toLocaleString() }}</p>
			<div v-html="post.content" class="markdown-body bg-gray-500 text-white rounded sh max-w-lg text-xs p-4"></div>
		</div>
</div>
</div>

</template>