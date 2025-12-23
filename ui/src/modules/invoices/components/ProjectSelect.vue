<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useProjects } from '../composables/useProjects';
import { Loader2 } from 'lucide-vue-next';

// Props & Emits
const props = defineProps<{
  modelValue: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

// Composables
const { projects, loading, loadProjects } = useProjects();

// Lifecycle
onMounted(() => {
  loadProjects();
});

// Computed
const selectedProject = computed(() => {
  return projects.value.find((p) => p.id === props.modelValue);
});
</script>

<template>
  <div class="relative">
    <label class="kit-label">Projekt (Optional)</label>

    <!-- Loading State -->
    <div v-if="loading" class="kit-input flex items-center gap-2">
      <Loader2 :size="16" class="animate-spin" />
      <span class="text-white/60">Lade Projekte...</span>
    </div>

    <!-- Dropdown -->
    <select
      v-else
      :value="modelValue"
      @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      class="kit-input"
    >
      <option value="">-- Kein Projekt --</option>
      <option
        v-for="project in projects"
        :key="project.id"
        :value="project.id"
      >
        {{ project.name }}
      </option>
    </select>

    <!-- Selected Project Info -->
    <p v-if="selectedProject?.description" class="text-xs text-white/60 mt-1">
      {{ selectedProject.description }}
    </p>
  </div>
</template>

<style scoped>
/* No custom styles needed - using kit-components */
</style>
