<script setup lang="ts">
import { onMounted } from 'vue';
import { useTimeTrackingNavigation } from './composables/useTimeTrackingNavigation';
import type { TimeTrackingView } from './composables/useTimeTrackingNavigation';

// Pages
import TimeTrackingDashboard from './pages/dashboard/TimeTrackingDashboard.vue';
import TimeEntriesListPage from './pages/entry/TimeEntriesListPage.vue';
import TimeEntryDetailPage from './pages/entry/TimeEntryDetailPage.vue';
import TimeEntryFormPage from './pages/entry/TimeEntryFormPage.vue';

// Props for deep-linking
const props = withDefaults(
  defineProps<{
    initialView?: TimeTrackingView;
    initialEntryId?: string;
  }>(),
  {
    initialView: 'dashboard',
  }
);

// Navigation
const { view, activeEntryId, goDashboard, goEntries, goEntryDetail, goCreateEntry, goEditEntry } =
  useTimeTrackingNavigation();

// Initialize view
onMounted(() => {
  if (props.initialView) {
    view.value = props.initialView;
  }

  if (props.initialEntryId) {
    activeEntryId.value = props.initialEntryId;
  }
});

// Navigation Handlers
function handleOpenDashboard() {
  goDashboard();
}

function handleOpenEntries() {
  goEntries();
}

function handleOpenEntry(id: string) {
  if (id === 'create') {
    goCreateEntry();
  } else {
    goEntryDetail(id);
  }
}

function handleEditEntry(id: string) {
  goEditEntry(id);
}

function handleEntrySaved(id: string) {
  goEntryDetail(id);
}
</script>

<template>
  <div class="time-tracking-app h-full">
    <!-- Dashboard View -->
    <TimeTrackingDashboard
      v-if="view === 'dashboard'"
      @open-entries="handleOpenEntries"
      @create-entry="goCreateEntry"
    />

    <!-- Entries List View -->
    <TimeEntriesListPage
      v-else-if="view === 'entries'"
      @open-entry="handleOpenEntry"
      @open-dashboard="handleOpenDashboard"
    />

    <!-- Entry Detail View -->
    <TimeEntryDetailPage
      v-else-if="view === 'entry-detail' && activeEntryId"
      :entry-id="activeEntryId"
      @back="handleOpenEntries"
      @edit="handleEditEntry"
    />

    <!-- Entry Create View -->
    <TimeEntryFormPage
      v-else-if="view === 'entry-create'"
      @back="handleOpenDashboard"
      @saved="handleEntrySaved"
    />

    <!-- Entry Edit View -->
    <TimeEntryFormPage
      v-else-if="view === 'entry-edit' && activeEntryId"
      :entry-id="activeEntryId"
      @back="(activeEntryId) => goEntryDetail(activeEntryId)"
      @saved="handleEntrySaved"
    />
  </div>
</template>
