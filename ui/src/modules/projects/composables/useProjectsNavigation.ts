/**
 * useProjectsNavigation Composable
 * Verwaltet die Navigation innerhalb des Projects-Moduls
 */

import { ref } from 'vue';

export type ProjectView =
  | 'dashboard'
  | 'projects'
  | 'project-detail'
  | 'project-create'
  | 'project-edit';

export function useProjectsNavigation() {
  // ─── STATE ────────────────────────────────────────────────
  const view = ref<ProjectView>('dashboard');
  const activeProjectId = ref<string | null>(null);

  // ─── NAVIGATION METHODS ───────────────────────────────────

  function goDashboard() {
    view.value = 'dashboard';
    activeProjectId.value = null;
  }

  function goProjects() {
    view.value = 'projects';
    activeProjectId.value = null;
  }

  function goProjectDetail(projectId: string) {
    view.value = 'project-detail';
    activeProjectId.value = projectId;
  }

  function goCreateProject() {
    view.value = 'project-create';
    activeProjectId.value = null;
  }

  function goEditProject(projectId: string) {
    view.value = 'project-edit';
    activeProjectId.value = projectId;
  }

  // ─── EXPOSE API ───────────────────────────────────────────
  return {
    // State
    view,
    activeProjectId,

    // Actions
    goDashboard,
    goProjects,
    goProjectDetail,
    goCreateProject,
    goEditProject,
  };
}
