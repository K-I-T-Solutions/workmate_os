/**
 * Projects Service
 * API-Calls für Projekte
 */

import { apiClient } from '@/services/api/client';
import type { Project, ProjectCreateRequest, ProjectUpdateRequest } from '../types/project';

const BASE_PATH = '/api/backoffice/projects';

export const projectsService = {
  /**
   * Alle Projekte laden
   */
  async getProjects(customerId?: string): Promise<Project[]> {
    const params = customerId ? { customer_id: customerId } : {};
    const response = await apiClient.get<Project[]>(BASE_PATH, { params });
    return response.data;
  },

  /**
   * Einzelnes Projekt laden
   */
  async getProject(id: string): Promise<Project> {
    const response = await apiClient.get<Project>(`${BASE_PATH}/${id}`);
    return response.data;
  },

  /**
   * Neues Projekt erstellen
   */
  async createProject(data: ProjectCreateRequest): Promise<Project> {
    const response = await apiClient.post<Project>(BASE_PATH, data);
    return response.data;
  },

  /**
   * Projekt aktualisieren
   */
  async updateProject(id: string, data: ProjectUpdateRequest): Promise<Project> {
    const response = await apiClient.put<Project>(`${BASE_PATH}/${id}`, data);
    return response.data;
  },

  /**
   * Projekt löschen
   */
  async deleteProject(id: string): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/${id}`);
  },
};
