import api from "@/services/api/client";
import type { Customer } from "../types/customer";
import type { Contact } from "../types/contact";

export const crmService = {
  //
  // CUSTOMERS
  //
  async getCustomers(): Promise<Customer[]> {
    const { data } = await api.get("/api/backoffice/crm/customers");
    return data;
  },

  async getCustomer(id: string): Promise<Customer> {
    const { data } = await api.get(`/api/backoffice/crm/customers/${id}`);
    return data;
  },

  async createCustomer(payload: Partial<Customer>) {
    return api.post("/api/backoffice/crm/customers", payload);
  },

  async updateCustomer(id: string, payload: Partial<Customer>) {
    return api.put(`/api/backoffice/crm/customers/${id}`, payload);
  },

  async deleteCustomer(id: string) {
    return api.delete(`/api/backoffice/crm/customers/${id}`);
  },

  //
  // CONTACTS (GLOBAL)
  //
  async getContacts(): Promise<Contact[]> {
    const { data } = await api.get("/api/backoffice/crm/contacts");
    return data;
  },

  async getContact(id: string): Promise<Contact> {
    const { data } = await api.get(`/api/backoffice/crm/contacts/${id}`);
    return data;
  },

  async createContact(payload: Partial<Contact>) {
    return api.post("/api/backoffice/crm/contacts", payload);
  },

  async updateContact(id: string, payload: Partial<Contact>) {
    return api.put(`/api/backoffice/crm/contacts/${id}`, payload);
  },

  async deleteContact(id: string) {
    return api.delete(`/api/backoffice/crm/contacts/${id}`);
  },

  //
  // PRIMARY CONTACT LOGIC
  //
  async getPrimaryContact(customerId: string): Promise<Contact | null> {
    const { data } = await api.get(
      `/api/backoffice/crm/customers/${customerId}/contacts/primary`
    );
    return data;
  },

  async setPrimaryContact(customerId: string, contactId: string) {
    return api.put(
      `/api/backoffice/crm/customers/${customerId}/contacts/${contactId}/set-primary`
    );
  },
};
