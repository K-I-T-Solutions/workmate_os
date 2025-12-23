/**
 * useProjects Composable
 * Lädt Projekt-Daten für Dropdowns
 */

import { ref } from 'vue';
import { apiClient } from '@/services/api/client';

interface Project {
  id: string;
  name: string;
  description?: string;
  status?: string;
}

export function useProjects() {
  const projects = ref<Project[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function loadProjects() {
    loading.value = true;
    error.value = null;

    try {
      const response = await apiClient.get<Project[]>('/api/backoffice/projects');
      projects.value = response.data;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden der Projekte';
      console.error('Error loading projects:', e);
    } finally {
      loading.value = false;
    }
  }

  return {
    projects,
    loading,
    error,
    loadProjects,
  };
}
