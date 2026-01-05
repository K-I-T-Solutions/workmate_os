import axios, { type AxiosError, type AxiosInstance } from 'axios';
import type { APIErrorResponse, ErrorDetail } from '@/types/errors';
import { isStructuredError } from '@/types/errors';

// Base URL aus Environment oder Fallback
const API_BASE_URL = import.meta.env.VITE_API_BASE || 'https://api.workmate.intern.phudevelopement.xyz';

// Debug: Zeige geladene URL in Console
console.log('🔧 API Client Config:', {
  VITE_API_BASE: import.meta.env.VITE_API_BASE,
  API_BASE_URL: API_BASE_URL,
  mode: import.meta.env.MODE,
});

// Event emitter for auth errors
export const authEvents = {
  onUnauthorized: [] as Array<() => void>,

  subscribe(callback: () => void) {
    this.onUnauthorized.push(callback);
  },

  unsubscribe(callback: () => void) {
    this.onUnauthorized = this.onUnauthorized.filter(cb => cb !== callback);
  },

  emit() {
    this.onUnauthorized.forEach(cb => cb());
  }
};

// Axios Instance erstellen
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 Sekunden
  withCredentials: true, // For cookies/sessions if needed
});

// Request Interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Token is set via useAuth composable when logging in
    // and via apiClient.defaults.headers.common['Authorization']
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Helper: Zeigt User-Benachrichtigung an
 *
 * TODO: Integriere eine Toast Notification Library (z.B. vue-toastification)
 * Aktuell: Console-Ausgabe als Fallback
 */
function showUserNotification(errorDetail: ErrorDetail) {
  // TODO: Replace with actual toast notification
  // import { useToast } from 'vue-toastification';
  // const toast = useToast();
  // toast.error(errorDetail.message, {
  //   description: errorDetail.hint,
  //   timeout: 5000,
  // });

  // Fallback: Strukturierte Console-Ausgabe
  console.group(`🔴 ${errorDetail.message}`);
  if (errorDetail.hint) {
    console.info(`💡 ${errorDetail.hint}`);
  }
  console.info(`🔢 Error Code: ${errorDetail.error_code}`);
  console.groupEnd();
}

/**
 * Helper: Extrahiert Error Detail aus API Response
 */
function extractErrorDetail(error: AxiosError<APIErrorResponse>): ErrorDetail | null {
  const detail = error.response?.data?.detail;

  if (!detail) return null;

  // Strukturierter Error (neues Format)
  if (isStructuredError(detail)) {
    return detail;
  }

  // Legacy String Error (altes Format)
  if (typeof detail === 'string') {
    return {
      error_code: 'LEGACY_ERROR',
      message: detail,
    };
  }

  return null;
}

// Response Interceptor (Error Handling)
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<APIErrorResponse>) => {
    // Strukturierter Error aus Backend extrahieren
    const errorDetail = extractErrorDetail(error);

    // Globales Error Handling
    if (error.response) {
      const status = error.response.status;

      // Zeige User-Benachrichtigung wenn strukturierter Error vorhanden
      if (errorDetail) {
        showUserNotification(errorDetail);

        // Spezial-Handling für Auth Errors
        if (status === 401) {
          authEvents.emit(); // Trigger logout
        }
      } else {
        // Fallback für Errors ohne strukturierten Error
        switch (status) {
          case 401:
            console.error('❌ Unauthorized - Session expired or invalid token');
            authEvents.emit();
            break;
          case 403:
            console.error('❌ Forbidden - Insufficient permissions');
            break;
          case 404:
            console.error('❌ Not Found');
            break;
          case 500:
            console.error('❌ Server Error');
            break;
          default:
            console.error('❌ API Error:', status);
        }
      }

      // Debug-Log für Entwickler
      if (import.meta.env.DEV) {
        console.debug('API Error Details:', {
          status,
          errorCode: errorDetail?.error_code,
          message: errorDetail?.message,
          url: error.config?.url,
          method: error.config?.method,
        });
      }
    } else if (error.request) {
      console.error('❌ Network Error - keine Antwort vom Server');

      // TODO: Show user notification
      // showUserNotification({
      //   error_code: 'NETWORK_ERROR',
      //   message: 'Keine Verbindung zum Server',
      //   hint: 'Bitte überprüfen Sie Ihre Internetverbindung',
      // });
    } else {
      console.error('❌ Error:', error.message);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
