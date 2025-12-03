import { ref } from 'vue';
import { apiClient } from '@/services/api/client';
import type { Project } from '@/types/api';

export function useProjects() {
  const projects = ref<Project[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchProjects = async () => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiClient.get('/api/backoffice/projects/');
      projects.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden der Projekte';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    projects,
    loading,
    error,
    fetchProjects,
  };
}
