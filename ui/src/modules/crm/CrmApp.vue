<script setup lang="ts">
import {
  CrmDashboardPage,
  CustomerDetailPage,
  ContactDetailPage,
  ContactListPage,
  CustomersListPage,
} from "./pages";

import { useCrmNavigation } from "./composables/useCrmNavigation";

const {
  view,
  activeCustomerId,
  activeContactId,
  goDashboard,
  goCustomers,
  goCustomerDetail,
  goContacts,
  goContactDetail,
} = useCrmNavigation();
</script>

<template>
  <div class="crm-app h-full">

   <CrmDashboardPage
      v-if="view === 'dashboard'"
      @openCustomers="goCustomers"
    />

    <CustomersListPage
      v-if="view === 'customers'"
      @openCustomer="goCustomerDetail"
      @openDashboard="goDashboard"
    />

    <CustomerDetailPage
      v-if="view === 'customer-detail'"
      :customerId="activeCustomerId!"
      @openContacts="goContacts"
      @openContact="goContactDetail"
      @back="goCustomers"
    />

    <ContactListPage
      v-if="view === 'contacts'"
      :customerId="activeCustomerId!"
      @openContact="goContactDetail"
      @openDashboard="goDashboard"
      @back="goCustomerDetail(activeCustomerId!)"
    />

    <ContactDetailPage
      v-if="view === 'contact-detail'"
      :customerId="activeCustomerId!"
      :contactId="activeContactId!"
      @back="goContacts"
    />


  </div>
</template>
