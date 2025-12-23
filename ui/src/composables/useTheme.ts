/**
 * useTheme Composable
 * Manages theme selection and application for WorkmateOS
 */

import { ref, watch } from 'vue';
import { apiClient } from '@/services/api/client';

export interface ThemeOption {
  id: string;
  name: string;
  description: string;
  preview: string; // CSS background for preview
}

export const AVAILABLE_THEMES: ThemeOption[] = [
  {
    id: 'kit-standard',
    name: 'K.I.T Standard',
    description: 'Standard dunkles Theme mit Orange-Akzenten',
    preview: 'linear-gradient(135deg, #232223 0%, #303030 100%)',
  },
  {
    id: 'kit-white',
    name: 'K.I.T White',
    description: 'Helles, professionelles Theme',
    preview: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
  },
  {
    id: 'kit-dark-blue',
    name: 'K.I.T Dark Blue',
    description: 'Dunkelblaues Theme für reduzierte Augenbelastung',
    preview: 'linear-gradient(135deg, #0d1b2a 0%, #263850 100%)',
  },
  {
    id: 'kit-midnight',
    name: 'K.I.T Midnight',
    description: 'Ultra-dunkles Theme für OLED-Displays',
    preview: 'linear-gradient(135deg, #000000 0%, #141414 100%)',
  },
];

const currentTheme = ref<string>('kit-standard');
const loading = ref(false);

export function useTheme() {
  /**
   * Apply theme to document
   */
  function applyTheme(themeId: string) {
    // Validate theme exists
    const theme = AVAILABLE_THEMES.find(t => t.id === themeId);
    if (!theme) {
      console.warn(`Theme ${themeId} not found, using kit-standard`);
      themeId = 'kit-standard';
    }

    console.log(`🎨 Applying theme: ${themeId}`);

    // Apply to document root
    document.documentElement.setAttribute('data-theme', themeId);
    currentTheme.value = themeId;

    // Store in localStorage for persistence
    localStorage.setItem('workmate-theme', themeId);

    // Log confirmation
    console.log(`✅ Theme applied. data-theme="${document.documentElement.getAttribute('data-theme')}"`);
  }

  /**
   * Initialize theme from user settings or localStorage
   */
  function initializeTheme(userTheme?: string) {
    let themeToApply = userTheme || localStorage.getItem('workmate-theme') || 'kit-standard';

    // Map old theme names to new ones
    if (themeToApply === 'catppuccin-frappe') {
      themeToApply = 'kit-standard';
    }

    applyTheme(themeToApply);
  }

  /**
   * Update user's theme preference in backend
   */
  async function updateUserTheme(themeId: string, userId: string): Promise<boolean> {
    loading.value = true;

    try {
      await apiClient.put(`/api/employees/${userId}`, {
        theme: themeId,
      });

      applyTheme(themeId);
      return true;
    } catch (error) {
      console.error('Error updating theme:', error);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Get theme option by ID
   */
  function getThemeById(themeId: string): ThemeOption | undefined {
    return AVAILABLE_THEMES.find(t => t.id === themeId);
  }

  /**
   * Get current theme option
   */
  function getCurrentTheme(): ThemeOption {
    return getThemeById(currentTheme.value) || AVAILABLE_THEMES[0];
  }

  return {
    // State
    currentTheme,
    loading,
    availableThemes: AVAILABLE_THEMES,

    // Actions
    applyTheme,
    initializeTheme,
    updateUserTheme,
    getThemeById,
    getCurrentTheme,
  };
}
