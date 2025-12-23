<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { useInvoicesNavigation } from './composables/useInvoicesNavigation';
import InvoicesDashboardPage from './pages/InvoicesDashboardPage.vue';
import InvoicesListPage from './pages/InvoicesListPage.vue';
import InvoiceDetailPage from './pages/InvoiceDetailPage.vue';
import InvoiceFormPage from './pages/InvoiceFormPage.vue';

// Props for deep-linking from other apps
const props = defineProps<{
  initialView?: string;
  initialInvoiceId?: string;
  prefilledCustomerId?: string;
}>();

const {
  view,
  activeInvoiceId,
  goDashboard,
  goList,
  goDetail,
  goCreate,
  goEdit,
  goBack,
} = useInvoicesNavigation();

// List reload trigger - increment when list should reload
const listKey = ref(0);

// Watch view changes and reload list when navigating to it
watch(view, (newView) => {
  if (newView === 'list') {
    listKey.value++;
  }
});

// Handle deep-linking on mount
onMounted(() => {
  if (props.initialView) {
    switch (props.initialView) {
      case 'detail':
        if (props.initialInvoiceId) {
          goDetail(props.initialInvoiceId);
        }
        break;
      case 'create':
        goCreate();
        break;
      case 'list':
        goList();
        break;
      default:
        break;
    }
  }
});
</script>

<template>
  <div class="invoices-app h-full">
    <!-- Dashboard View -->
    <InvoicesDashboardPage
      v-if="view === 'dashboard'"
      @openList="goList"
      @openCreate="goCreate"
    />

    <!-- List View -->
    <InvoicesListPage
      v-if="view === 'list'"
      :key="listKey"
      @openInvoice="goDetail"
      @openCreate="goCreate"
      @back="goDashboard"
    />

    <!-- Detail View -->
    <InvoiceDetailPage
      v-if="view === 'detail' && activeInvoiceId"
      :invoiceId="activeInvoiceId"
      @back="goBack"
      @edit="goEdit"
    />

    <!-- Create View -->
    <InvoiceFormPage
      v-if="view === 'create'"
      :prefilledCustomerId="prefilledCustomerId"
      @back="goBack"
      @saved="goDetail"
    />

    <!-- Edit View -->
    <InvoiceFormPage
      v-if="view === 'edit' && activeInvoiceId"
      :invoiceId="activeInvoiceId"
      @back="goBack"
      @saved="goDetail"
    />
  </div>
</template>

<style scoped>
.invoices-app {
  display: flex;
  flex-direction: column;
}
</style>
