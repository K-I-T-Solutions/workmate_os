<script setup lang="ts">
import { useInvoicesNavigation } from './composables/useInvoicesNavigation';
import InvoicesDashboardPage from './pages/InvoicesDashboardPage.vue';
import InvoicesListPage from './pages/InvoicesListPage.vue';
import InvoiceDetailPage from './pages/InvoiceDetailPage.vue';
import InvoiceFormPage from './pages/InvoiceFormPage.vue';

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
