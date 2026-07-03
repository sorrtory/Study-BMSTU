<script setup lang="ts">
import { ref, onMounted } from "vue";
import Config from "../config";

const message = ref("Loading...");

onMounted(async () => {
  const res = await fetch(`${Config.VITE_API_URL}/api/hello`);
  const data = await res.json();
  message.value = data.message;
});
</script>

<template>
  <main> 
    <h1>Hello Vue</h1>
    <p>{{ message }}</p>
  </main>
</template>