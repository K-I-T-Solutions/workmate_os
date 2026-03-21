import api from "@/services/api/client";
import type { Customer, CsvImportResult } from "../types/customer";
import type { Contact } from "../types/contact";
import type { CrmStats } from "../types/stats";
import type { CrmActivity, CreateCrmActivity } from "../types/activity";

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
  /* Stats */
  async getCrmStats ():Promise<CrmStats>{

    const {data} = await api.get("/api/backoffice/crm/stats");
    return data;

  },

  /* activities */
  async getLastestActivities(limit: number): Promise<CrmActivity[]>{
    const {data} = await api.get(`/api/backoffice/crm/activities/latest?limit=${limit}`);
    return data;
  },
  async getCustomerActivities(customerId: string, opts?:{
    contactId?: string,
    limit?: number
  }):Promise<CrmActivity[]>{
    const params = new URLSearchParams();
    if (opts?.contactId){
      params.append("contact_id",opts.contactId);
    }
    if (opts?.limit){
      params.append("limit", String(opts.limit))
    }

    const query = params.toString();
    const url = `/api/backoffice/crm/customers/${customerId}/activities${query ? `?${query}` : ""}`;
    const {data} = await api.get(url);
    return data;
  },
   async createActivity(payload: CreateCrmActivity): Promise<CrmActivity> {
    const { data } = await api.post(
      "/api/backoffice/crm/activities",
      payload
    );
    return data;
  },
  async searchCustomers(search: string) {
    return api.get("/api/backoffice/crm/customers", {
      params: {
        search,
        limit: 5,
        skip: 0,
        status: "active",
      },
    });
  },

  //
  // PIPELINE
  //
  async getPipeline(): Promise<Record<string, Customer[]>> {
    const { data } = await api.get("/api/backoffice/crm/pipeline");
    return data;
  },

  async updatePipelineStage(customerId: string, stage: string): Promise<Customer> {
    const { data } = await api.patch(
      `/api/backoffice/crm/customers/${customerId}/pipeline-stage`,
      { stage }
    );
    return data;
  },

  //
  // CSV IMPORT
  //
  async importCsvDryRun(file: File): Promise<CsvImportResult> {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await api.post(
      "/api/backoffice/crm/customers/import-csv?dry_run=true",
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    return data;
  },

  async importCsv(file: File, skipDuplicates = true): Promise<CsvImportResult> {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await api.post(
      `/api/backoffice/crm/customers/import-csv?skip_duplicates=${skipDuplicates}`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    return data;
  },

};
