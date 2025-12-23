/**
 * useProjects Composable
 * Verwaltet das Laden und Verarbeiten von Projekten
 */

import { ref, computed } from 'vue';
import { projectsService } from '../services/projects.service';
import type { Project, ProjectCreateRequest, ProjectUpdateRequest } from '../types/project';

export interface ProjectFilters {
  customerId?: string;
  status?: string;
  search?: string;
}

export function useProjects() {
  // ─── STATE ────────────────────────────────────────────────
  const projects = ref<Project[]>([]);
  const currentProject = ref<Project | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // ─── COMPUTED ─────────────────────────────────────────────
  const hasProjects = computed(() => projects.value.length > 0);
  const isEmpty = computed(() => !loading.value && projects.value.length === 0);

  // ─── ACTIONS ──────────────────────────────────────────────

  /**
   * Projekte laden mit Filtern
   */
  async function loadProjects(filters?: ProjectFilters) {
    loading.value = true;
    error.value = null;

    try {
      // API-Call mit Customer-Filter
      const response = await projectsService.getProjects(filters?.customerId);

      // Client-seitige Filterung
      let filtered = response;

      // Filter nach Status
      if (filters?.status) {
        filtered = filtered.filter((p) => p.status === filters.status);
      }

      // Filter nach Suchbegriff
      if (filters?.search) {
        const search = filters.search.toLowerCase();
        filtered = filtered.filter(
          (p) =>
            p.title.toLowerCase().includes(search) ||
            p.description?.toLowerCase().includes(search) ||
            p.project_number?.toLowerCase().includes(search)
        );
      }

      projects.value = filtered;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden der Projekte';
      console.error('Error loading projects:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Einzelnes Projekt laden
   */
  async function loadProject(id: string) {
    loading.value = true;
    error.value = null;

    try {
      currentProject.value = await projectsService.getProject(id);
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden des Projekts';
      console.error('Error loading project:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Neues Projekt erstellen
   */
  async function createProject(data: ProjectCreateRequest): Promise<Project | null> {
    loading.value = true;
    error.value = null;

    try {
      const project = await projectsService.createProject(data);

      // Zur Liste hinzufügen wenn bereits geladen
      if (projects.value.length > 0) {
        projects.value.unshift(project);
      }

      return project;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Erstellen des Projekts';
      console.error('Error creating project:', e);
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Projekt aktualisieren
   */
  async function updateProject(id: string, data: ProjectUpdateRequest): Promise<Project | null> {
    loading.value = true;
    error.value = null;

    try {
      const updated = await projectsService.updateProject(id, data);

      // In der Liste aktualisieren
      const index = projects.value.findIndex((p) => p.id === id);
      if (index !== -1) {
        projects.value[index] = updated;
      }

      // Current project aktualisieren
      if (currentProject.value?.id === id) {
        currentProject.value = updated;
      }

      return updated;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Aktualisieren des Projekts';
      console.error('Error updating project:', e);
      return null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Projekt löschen
   */
  async function deleteProject(id: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await projectsService.deleteProject(id);

      // Aus der Liste entfernen
      projects.value = projects.value.filter((p) => p.id !== id);

      // Current project zurücksetzen
      if (currentProject.value?.id === id) {
        currentProject.value = null;
      }

      return true;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Löschen des Projekts';
      console.error('Error deleting project:', e);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fehler zurücksetzen
   */
  function clearError() {
    error.value = null;
  }

  /**
   * State zurücksetzen
   */
  function reset() {
    projects.value = [];
    currentProject.value = null;
    loading.value = false;
    error.value = null;
  }

  // ─── EXPOSE API ───────────────────────────────────────────
  return {
    // State
    projects,
    currentProject,
    loading,
    error,

    // Computed
    hasProjects,
    isEmpty,

    // Actions
    loadProjects,
    loadProject,
    createProject,
    updateProject,
    deleteProject,
    clearError,
    reset,
  };
}
