<script setup lang="ts">
import {
  CrmDashboardPage,
  CustomerDetailPage,
  ContactDetailPage,
  ContactListPage,
  CustomersListPage,
} from "./pages";

import { useCrmNavigation } from "./composables/useCrmNavigation";
import CustomerForm from "./components/customer/CustomerForm.vue";
import ContactForm from "./components/contacts/ContactForm.vue";

const {
  view,
  activeCustomerId,
  activeContactId,
  goDashboard,
  goCustomers,
  goCustomerDetail,
  goContacts,
  goContactDetail,
  openCreateContact,
  openCreateCustomer
} = useCrmNavigation();
</script>

<template>
  <div class="crm-app h-full">
   <CrmDashboardPage
  v-if="view === 'dashboard'"
  @openCustomers="goCustomers"
  @create-customer="openCreateCustomer"
  @create-contact="openCreateContact"
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
      <CustomerForm
      v-if="view === 'customer-create'"
      :customer="null"
      @close="goCustomers"
      @saved="goCustomers"
    />


    <ContactForm
      v-if="view === 'contact-create'"
      :contact="null"
      :customerId="activeCustomerId!"
      @close="goContacts"
      @saved="goContacts"
    />
  </div>
</template>
