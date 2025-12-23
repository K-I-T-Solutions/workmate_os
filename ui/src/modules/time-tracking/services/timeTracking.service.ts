/**
 * Time Tracking Service
 * API-Calls für Zeiterfassung
 */

import { apiClient } from '@/services/api/client';
import type { TimeEntry, TimeEntryCreateRequest, TimeEntryUpdateRequest } from '../types/timeEntry';

const BASE_PATH = '/api/backoffice/time-tracking';

export const timeTrackingService = {
  /**
   * Alle Time Entries laden
   */
  async getTimeEntries(): Promise<TimeEntry[]> {
    const response = await apiClient.get<TimeEntry[]>(BASE_PATH);
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
};
