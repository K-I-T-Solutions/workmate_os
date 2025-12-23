import axios, { type AxiosError, type AxiosInstance } from 'axios';

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

// Response Interceptor (Error Handling)
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Globales Error Handling
    if (error.response) {
      switch (error.response.status) {
        case 401:
          console.error('❌ Unauthorized - Session expired or invalid token');
          // Emit unauthorized event to trigger logout
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
          console.error('❌ API Error:', error.response.status);
      }
    } else if (error.request) {
      console.error('❌ Network Error - keine Antwort vom Server');
    } else {
      console.error('❌ Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
