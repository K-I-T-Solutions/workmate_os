/**
 * useCurrentUser Composable
 * Manages current logged-in user data
 */

import { ref, computed } from 'vue';
import { apiClient } from '@/services/api/client';
import md5 from 'md5';

export interface Employee {
  id: string;
  employee_code: string;
  first_name: string | null;
  last_name: string | null;
  email: string;
  phone: string | null;
  gender: string | null;
  birth_date: string | null;
  nationality: string | null;
  photo_url: string | null;
  bio: string | null;
  address_street: string | null;
  address_zip: string | null;
  address_city: string | null;
  address_country: string | null;
  department_id: string | null;
  department?: {
    id: string;
    name: string;
    code: string;
  };
  role_id: string | null;
  role?: {
    id: string;
    name: string;
    description: string | null;
  };
  employment_type: string;
  hire_date: string | null;
  status: string;
  timezone: string;
  language: string;
  theme: string;
  created_at: string;
  updated_at: string;
}

export interface EmployeeUpdate {
  email?: string;
  phone?: string;
  bio?: string;
  photo_url?: string;
  address_street?: string;
  address_zip?: string;
  address_city?: string;
  address_country?: string;
  timezone?: string;
  language?: string;
  theme?: string;
}

const currentUser = ref<Employee | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

export function useCurrentUser() {
  /**
   * Load current user data from /api/auth/me
   */
  async function loadCurrentUser() {
    loading.value = true;
    error.value = null;

    try {
      const response = await apiClient.get('/api/auth/me');
      const authUser = response.data;

      // Convert auth user to Employee format
      currentUser.value = {
        id: authUser.id,
        employee_code: authUser.employee_code,
        first_name: authUser.first_name,
        last_name: authUser.last_name,
        email: authUser.email,
        phone: authUser.phone || null,
        gender: authUser.gender || null,
        birth_date: authUser.birth_date || null,
        nationality: authUser.nationality || null,
        photo_url: authUser.photo_url || null,
        bio: authUser.bio || null,
        address_street: authUser.address_street || null,
        address_zip: authUser.address_zip || null,
        address_city: authUser.address_city || null,
        address_country: authUser.address_country || null,
        department_id: authUser.department?.id || null,
        department: authUser.department,
        role_id: authUser.role?.id || null,
        role: authUser.role,
        employment_type: authUser.employment_type || 'fulltime',
        hire_date: authUser.hire_date || null,
        status: authUser.status || 'active',
        timezone: authUser.timezone || 'Europe/Berlin',
        language: authUser.language || 'de',
        theme: authUser.theme || 'catppuccin-frappe',
        created_at: authUser.created_at || '',
        updated_at: authUser.updated_at || '',
      };
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Laden der Benutzerdaten';
      console.error('Error loading current user:', e);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Update current user profile
   */
  async function updateProfile(data: EmployeeUpdate): Promise<boolean> {
    if (!currentUser.value) return false;

    loading.value = true;
    error.value = null;

    try {
      const response = await apiClient.put(
        `/api/employees/${currentUser.value.id}`,
        data
      );
      currentUser.value = response.data;
      return true;
    } catch (e: any) {
      error.value = e.message || 'Fehler beim Aktualisieren des Profils';
      console.error('Error updating profile:', e);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Get Gravatar URL for user email
   */
  function getGravatarUrl(size: number = 80): string {
    if (!currentUser.value?.email) {
      return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&s=${size}`;
    }

    const hash = md5(currentUser.value.email.toLowerCase().trim());
    return `https://www.gravatar.com/avatar/${hash}?d=mp&s=${size}`;
  }

  /**
   * Get user's full name
   */
  const fullName = computed(() => {
    if (!currentUser.value) return 'Unbekannt';
    const { first_name, last_name } = currentUser.value;
    if (first_name && last_name) {
      return `${first_name} ${last_name}`;
    }
    return first_name || last_name || 'Unbekannt';
  });

  /**
   * Get user's display name with employee code
   */
  const displayName = computed(() => {
    if (!currentUser.value) return 'Unbekannt';
    return `${fullName.value} (${currentUser.value.employee_code})`;
  });

  /**
   * Logout user
   */
  async function logout() {
    // TODO: Implement actual logout logic (clear tokens, redirect, etc.)
    currentUser.value = null;
    console.log('Logout functionality needs to be implemented');
  }

  return {
    // State
    currentUser,
    loading,
    error,

    // Computed
    fullName,
    displayName,

    // Actions
    loadCurrentUser,
    updateProfile,
    getGravatarUrl,
    logout,
  };
}
