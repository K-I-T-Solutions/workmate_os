<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import KBHomePage from './pages/KBHomePage.vue';
import KBCategoryPage from './pages/KBCategoryPage.vue';
import KBArticlePage from './pages/KBArticlePage.vue';

const route = useRoute();
const currentView = computed(() => (route.meta.view as string) || 'home');
const currentId = computed(() => route.params.id as string | undefined);
</script>

<template>
  <div class="kb-app h-full overflow-auto p-5">
    <KBHomePage v-if="currentView === 'home'" />
    <KBCategoryPage v-if="currentView === 'category' && currentId" :category-id="currentId" />
    <KBArticlePage v-if="currentView === 'article' && currentId" :article-id="currentId" />
  </div>
</template>

<style scoped>
.kb-app {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}
</style>
