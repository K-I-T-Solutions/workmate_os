<script setup lang="ts">
import {
  CrmDashboardPage,
  CustomerDetailPage,
  ContactDetailPage,
  ContactListPage,
  CustomersListPage,
} from "./pages";

import CustomerFormPage from "./pages/CustomerFormPage.vue";
import ContactFormPage from "./pages/ContactFormPage.vue";

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
  openCreateContact,
  openCreateCustomer,
  goEditCustomer,
  goEditContact,
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
      @edit="goEditCustomer"
      @back="goCustomers"
    />

    <ContactListPage
      v-if="view === 'contacts'"
      :customerId="activeCustomerId!"
      @openContact="goContactDetail"
      @createContact="openCreateContact"
      @editContact="goEditContact(activeCustomerId!, $event)"
      @openDashboard="goDashboard"
      @back="goCustomerDetail(activeCustomerId!)"
    />

    <ContactDetailPage
      v-if="view === 'contact-detail'"
      :customerId="activeCustomerId!"
      :contactId="activeContactId!"
      @edit="goEditContact(activeCustomerId!, $event)"
      @back="goContacts"
    />

    <!-- Customer Create -->
    <CustomerFormPage
      v-if="view === 'customer-create'"
      @back="goCustomers"
      @saved="goCustomerDetail"
    />

    <!-- Customer Edit -->
    <CustomerFormPage
      v-if="view === 'customer-edit'"
      :customerId="activeCustomerId!"
      @back="goCustomerDetail(activeCustomerId!)"
      @saved="goCustomerDetail"
    />

    <!-- Contact Create -->
    <ContactFormPage
      v-if="view === 'contact-create'"
      :customerId="activeCustomerId!"
      @back="goContacts"
      @saved="goContactDetail"
    />

    <!-- Contact Edit -->
    <ContactFormPage
      v-if="view === 'contact-edit'"
      :customerId="activeCustomerId!"
      :contactId="activeContactId!"
      @back="goContactDetail(activeContactId!)"
      @saved="goContactDetail"
    />
  </div>
</template>
