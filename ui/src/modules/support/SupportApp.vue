<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import TicketsListPage from './pages/TicketsListPage.vue';
import TicketDetailPage from './pages/TicketDetailPage.vue';

const route = useRoute();
const currentView = computed(() => (route.meta.view as string) || 'tickets');
const currentId = computed(() => route.params.id as string | undefined);
</script>

<template>
  <div class="support-app h-full overflow-auto p-4">
    <TicketsListPage v-if="currentView === 'tickets'" />
    <TicketDetailPage v-if="currentView === 'ticket-detail' && currentId" :ticket-id="currentId" />
  </div>
</template>

<style scoped>
.support-app {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}
</style>
