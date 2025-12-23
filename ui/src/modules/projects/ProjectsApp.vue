<script setup lang="ts">
import { onMounted } from 'vue';
import ProjectsDashboardPage from './pages/dashboard/ProjectsDashboardPage.vue';
import ProjectsListPage from './pages/project/ProjectsListPage.vue';
import ProjectDetailPage from './pages/project/ProjectDetailPage.vue';
import ProjectFormPage from './pages/ProjectFormPage.vue';
import { useProjectsNavigation } from './composables/useProjectsNavigation';

// Props for deep-linking from other apps
const props = defineProps<{
  initialView?: string;
  initialProjectId?: string;
  initialCustomerId?: string;
}>();

const {
  view,
  activeProjectId,
  goDashboard,
  goProjects,
  goProjectDetail,
  goCreateProject,
  goEditProject,
} = useProjectsNavigation();

// Handle deep-linking on mount
onMounted(() => {
  if (props.initialView && props.initialProjectId) {
    switch (props.initialView) {
      case 'detail':
        goProjectDetail(props.initialProjectId);
        break;
      case 'edit':
        goEditProject(props.initialProjectId);
        break;
      default:
        break;
    }
  } else if (props.initialView === 'create') {
    goCreateProject();
  }
});
</script>

<template>
  <div class="projects-app h-full">
    <!-- Dashboard -->
    <ProjectsDashboardPage
      v-if="view === 'dashboard'"
      @openProjects="goProjects"
      @createProject="goCreateProject"
    />

    <!-- Projects List -->
    <ProjectsListPage
      v-if="view === 'projects'"
      @openProject="(id) => id === 'create' ? goCreateProject() : goProjectDetail(id)"
      @openDashboard="goDashboard"
    />

    <!-- Project Detail -->
    <ProjectDetailPage
      v-if="view === 'project-detail'"
      :projectId="activeProjectId!"
      @edit="goEditProject"
      @back="goProjects"
    />

    <!-- Project Create -->
    <ProjectFormPage
      v-if="view === 'project-create'"
      :initialCustomerId="initialCustomerId"
      @back="goProjects"
      @saved="goProjectDetail"
    />

    <!-- Project Edit -->
    <ProjectFormPage
      v-if="view === 'project-edit'"
      :projectId="activeProjectId!"
      @back="() => goProjectDetail(activeProjectId!)"
      @saved="goProjectDetail"
    />
  </div>
</template>

<style scoped>
.projects-app {
  /* Ensure full height for internal scrolling */
  overflow: hidden;
}
</style>
