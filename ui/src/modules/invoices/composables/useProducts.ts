import { ref } from 'vue';
import type { Product, ProductListResponse } from '../types/product';
import { apiClient } from '@/services/api/client';

export function useProducts() {
  const products = ref<Product[]>([]);
  const currentProduct = ref<Product | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function loadProducts(params?: {
    category?: string;
    is_active?: boolean;
    search?: string;
    skip?: number;
    limit?: number;
  }) {
    loading.value = true;
    error.value = null;

    try {
      const queryParams = new URLSearchParams();
      if (params?.category) queryParams.append('category', params.category);
      if (params?.is_active !== undefined) queryParams.append('is_active', String(params.is_active));
      if (params?.search) queryParams.append('search', params.search);
      if (params?.skip !== undefined) queryParams.append('skip', String(params.skip));
      if (params?.limit !== undefined) queryParams.append('limit', String(params.limit));

      const response = await apiClient.get<ProductListResponse>(
        `/api/backoffice/products?${queryParams.toString()}`
      );

      products.value = response.data.items;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden der Produkte';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function loadProduct(id: string) {
    loading.value = true;
    error.value = null;

    try {
      const response = await apiClient.get<Product>(`/api/backoffice/products/${id}`);
      currentProduct.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden des Produkts';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function loadProductBySku(sku: string) {
    loading.value = true;
    error.value = null;

    try {
      const response = await apiClient.get<Product>(`/api/backoffice/products/by-sku/${sku}`);
      currentProduct.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Fehler beim Laden des Produkts';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    products,
    currentProduct,
    loading,
    error,
    loadProducts,
    loadProduct,
    loadProductBySku,
  };
}
