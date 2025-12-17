<script setup lang="ts">
import { ref } from "vue";
import { CrmDashboardPage,CustomerDetailPage,ContactDetailPage,ContactListPage,CustomersListPage } from "./pages";

type View =
      | "dashboard"
      | "customers"
      | "customer-detail"
      | "contacts"
      | "contact-detail";

const view = ref<View>("dashboard");
const activeCustomerId = ref<string | null>(null);
const activeContactId = ref<string | null>(null);
function openCustomer(id: string){
  activeCustomerId.value=id;
  view.value = "customer-detail"
}
function openContacts(customerId: string){
  activeCustomerId.value = customerId;
  view.value = "contacts";
}
function openContact(contactId: string) {
  activeContactId.value = contactId;
  view.value = "contact-detail";
}


function backToContacts(){
  view.value = "contacts"
  activeContactId.value= null;
}
</script>

<template>
  <div class="crm-app h-full">

    <CrmDashboardPage
      v-if="view === 'dashboard'"
      @openCustomers="view = 'customers'"
    />

    <CustomersListPage
      v-if="view === 'customers'"
      @openCustomer="openCustomer"
    />

    <CustomerDetailPage
      v-if="view === 'contact-detail'"
      :customerId="activeCustomerId!"
      :contactId="activeContactId!"
      @openContacts="openContacts"
      @back="backToContacts"
      @deleted="backToContacts"
    />


    <ContactListPage
      v-if="view === 'contacts'"
      :customerId="activeCustomerId!"
      @openContact="openContact"
      @back="view = 'customer-detail'"
    />

    <ContactDetailPage
      v-if="view === 'contact-detail'"
      :customerId="activeCustomerId!"
      :contactId="activeContactId!"
      @back="backToContacts"
      @deleted="backToContacts"
    />


  </div>
</template>
