/**
 * useUserSettings Composable
 * Manages user settings (language, timezone, notifications)
 */

import { ref } from 'vue';
import { apiClient } from '@/services/api/client';

export interface UserSettings {
  id: string;
  owner_id: string;
  language: string;
  timezone: string;
  notifications_enabled: boolean;
}

export interface UserSettingsUpdate {
  language?: string;
  timezone?: string;
  notifications_enabled?: boolean;
}

const settings = ref<UserSettings | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

// For demo purposes, we're using a hardcoded user ID
// In production, this would come from authentication context
const CURRENT_USER_ID = 'c5bc47a5-16eb-4f84-8c22-2d6ad0b31f5d';

export function useUserSettings() {
  /**
   * Load user settings
   * Note: Backend endpoint needs to be created for this
   */
  async function loadSettings() {
    loading.value = true;
    error.value = null;

    try {
      // TODO: Backend needs to implement this endpoint
      // For now, we'll use default values
      const response = await apiClient.get(`/api/users/${CURRENT_USER_ID}/settings`);
      settings.value = response.data;
    } catch (e: any) {
      // Fallback to defaults if endpoint doesn't exist yet
      settings.value = {
        id: 'default-settings-id',
        owner_id: CURRENT_USER_ID,
        language: 'de-DE',
        timezone: 'Europe/Berlin',
        notifications_enabled: true,
      };
      console.warn('Settings endpoint not available, using defaults:', e.message);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Update user settings
   */
  async function updateSettings(data: UserSettingsUpdate): Promise<boolean> {
    if (!settings.value) return false;

    loading.value = true;
    error.value = null;

    try {
      const response = await apiClient.put(
        `/api/users/${CURRENT_USER_ID}/settings`,
        data
      );
      settings.value = response.data;
      return true;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Aktualisieren der Einstellungen';
      console.error('Error updating settings:', e);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Reset settings to default values
   */
  async function resetToDefaults(): Promise<boolean> {
    return updateSettings({
      language: 'de-DE',
      timezone: 'Europe/Berlin',
      notifications_enabled: true,
    });
  }

  return {
    // State
    settings,
    loading,
    error,

    // Actions
    loadSettings,
    updateSettings,
    resetToDefaults,
  };
}
