import axios, { type AxiosError, type AxiosInstance } from 'axios';

// Base URL aus Environment oder Fallback
const API_BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// Axios Instance erstellen
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 Sekunden
});

// Request Interceptor (für später: JWT Token)
apiClient.interceptors.request.use(
  (config) => {
    // Später: JWT Token aus Store holen
    // const token = useAuthStore().token;
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
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
          console.error('Unauthorized - bitte einloggen');
          // Später: Redirect zu Login
          break;
        case 403:
          console.error('Forbidden - keine Berechtigung');
          break;
        case 404:
          console.error('Not Found');
          break;
        case 500:
          console.error('Server Error');
          break;
        default:
          console.error('API Error:', error.response.status);
      }
    } else if (error.request) {
      console.error('Network Error - keine Antwort vom Server');
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
