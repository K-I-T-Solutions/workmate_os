/**
 * useAuth Composable
 * Handles authentication state, login, logout, and token management
 */

import { ref, computed } from 'vue';
import { apiClient } from '@/services/api/client';
import { useTheme } from './useTheme';

export interface AuthUser {
  id: string;
  employee_code: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  role: {
    id: string;
    name: string;
    description?: string;
  } | null;
  department: {
    id: string;
    name: string;
    code: string;
  } | null;
  permissions: string[];
  photo_url: string | null;
  theme?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: AuthUser;
}

// Token storage keys
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

// Global state (singleton pattern)
const token = ref<string | null>(null);
const user = ref<AuthUser | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

export function useAuth() {
  /**
   * Initialize auth state from localStorage
   */
  function initializeAuth() {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedUser = localStorage.getItem(USER_KEY);

    if (storedToken && storedUser) {
      token.value = storedToken;
      try {
        user.value = JSON.parse(storedUser);
        // Set token in API client
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
      } catch (e) {
        // Invalid stored data, clear it
        clearAuthData();
      }
    }
  }

  /**
   * Login with email and password
   */
  async function login(credentials: LoginCredentials): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      const response = await apiClient.post<LoginResponse>('/api/auth/login', credentials);
      const data = response.data;

      // Store token and user
      token.value = data.access_token;
      user.value = data.user;

      localStorage.setItem(TOKEN_KEY, data.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));

      // Set authorization header for future requests
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;

      // Apply user's theme
      const { initializeTheme } = useTheme();
      initializeTheme(data.user.theme);

      return true;
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Login fehlgeschlagen';
      console.error('Login error:', e);
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Logout and clear auth data
   */
  async function logout() {
    loading.value = true;

    try {
      // Call logout endpoint (optional, for server-side cleanup)
      if (token.value) {
        await apiClient.post('/api/auth/logout');
      }
    } catch (e) {
      console.error('Logout error:', e);
    } finally {
      clearAuthData();
      loading.value = false;
    }
  }

  /**
   * Clear auth data from state and storage
   */
  function clearAuthData() {
    token.value = null;
    user.value = null;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    delete apiClient.defaults.headers.common['Authorization'];
  }

  /**
   * Check if user is authenticated
   */
  const isAuthenticated = computed(() => !!token.value && !!user.value);

  /**
   * Get current user
   */
  async function fetchCurrentUser(): Promise<boolean> {
    if (!token.value) return false;

    loading.value = true;
    error.value = null;

    try {
      const response = await apiClient.get<AuthUser>('/api/auth/me');
      user.value = response.data;
      localStorage.setItem(USER_KEY, JSON.stringify(response.data));
      return true;
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Fehler beim Laden der Benutzerdaten';
      console.error('Fetch user error:', e);

      // If unauthorized, clear auth data
      if (e.response?.status === 401) {
        clearAuthData();
      }

      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Check if user has a specific permission
   */
  function hasPermission(permission: string): boolean {
    if (!user.value || !user.value.permissions) return false;
    return user.value.permissions.includes(permission);
  }

  /**
   * Check if user has any of the given permissions
   */
  function hasAnyPermission(permissions: string[]): boolean {
    if (!user.value || !user.value.permissions) return false;
    return permissions.some(p => user.value!.permissions.includes(p));
  }

  /**
   * Check if user has all of the given permissions
   */
  function hasAllPermissions(permissions: string[]): boolean {
    if (!user.value || !user.value.permissions) return false;
    return permissions.every(p => user.value!.permissions.includes(p));
  }

  /**
   * Get user's full name
   */
  const fullName = computed(() => {
    if (!user.value) return '';
    const { first_name, last_name } = user.value;
    if (first_name && last_name) {
      return `${first_name} ${last_name}`;
    }
    return first_name || last_name || user.value.email;
  });

  return {
    // State
    token,
    user,
    loading,
    error,

    // Computed
    isAuthenticated,
    fullName,

    // Actions
    initializeAuth,
    login,
    logout,
    fetchCurrentUser,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    clearAuthData,
  };
}
