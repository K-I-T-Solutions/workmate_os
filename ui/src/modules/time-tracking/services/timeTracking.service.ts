/**
 * Time Tracking Service
 * API-Calls für Zeiterfassung
 */

import { apiClient } from '@/services/api/client';
import type {
  TimeEntry,
  TimeEntryCreateRequest,
  TimeEntryUpdateRequest,
  TimeEntryFilters,
  TimeTrackingStats,
  WeeklySummary,
} from '../types/timeEntry';

const BASE_PATH = '/api/backoffice/time-tracking';

export const timeTrackingService = {
  /**
   * Time Entries laden (mit optionalen Filtern)
   */
  async getTimeEntries(filters?: TimeEntryFilters): Promise<TimeEntry[]> {
    const response = await apiClient.get<TimeEntry[]>(BASE_PATH, {
      params: filters,
    });
    return response.data;
  },

  /**
   * Einzelnen Time Entry laden
   */
  async getTimeEntry(id: string): Promise<TimeEntry> {
    const response = await apiClient.get<TimeEntry>(`${BASE_PATH}/${id}`);
    return response.data;
  },

  /**
   * Time Entry erstellen (Timer starten)
   */
  async createTimeEntry(data: TimeEntryCreateRequest): Promise<TimeEntry> {
    const response = await apiClient.post<TimeEntry>(BASE_PATH, data);
    return response.data;
  },

  /**
   * Time Entry aktualisieren (Timer stoppen)
   */
  async updateTimeEntry(id: string, data: TimeEntryUpdateRequest): Promise<TimeEntry> {
    const response = await apiClient.put<TimeEntry>(`${BASE_PATH}/${id}`, data);
    return response.data;
  },

  /**
   * Time Entry löschen
   */
  async deleteTimeEntry(id: string): Promise<void> {
    await apiClient.delete(`${BASE_PATH}/${id}`);
  },

  /**
   * Statistiken laden
   */
  async getStats(employeeId?: string): Promise<TimeTrackingStats> {
    const response = await apiClient.get<TimeTrackingStats>(`${BASE_PATH}/stats`, {
      params: employeeId ? { employee_id: employeeId } : undefined,
    });
    return response.data;
  },

  /**
   * Wochen-Zusammenfassung laden
   */
  async getWeeklySummary(employeeId: string, week: string): Promise<WeeklySummary> {
    const response = await apiClient.get<WeeklySummary>(`${BASE_PATH}/summary`, {
      params: { employee_id: employeeId, week },
    });
    return response.data;
  },

  /**
   * Time Entry genehmigen
   */
  async approveEntry(id: string): Promise<TimeEntry> {
    const response = await apiClient.put<TimeEntry>(`${BASE_PATH}/${id}/approve`);
    return response.data;
  },

  /**
   * Genehmigung zurückziehen
   */
  async rejectEntry(id: string): Promise<TimeEntry> {
    const response = await apiClient.put<TimeEntry>(`${BASE_PATH}/${id}/reject`);
    return response.data;
  },
};
