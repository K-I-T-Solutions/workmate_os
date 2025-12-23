<script setup lang="ts">
import { RouterView } from 'vue-router';
import { onMounted } from 'vue';
import { useAuth } from '@/composables/useAuth';
import { useTheme } from '@/composables/useTheme';

const { user } = useAuth();
const { initializeTheme } = useTheme();

// Initialize theme on app mount
onMounted(() => {
  const userTheme = user.value?.theme;
  initializeTheme(userTheme);
});
</script>

<template>
<RouterView />
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
