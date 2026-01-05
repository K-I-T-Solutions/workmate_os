<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useProducts } from '../composables/useProducts';
import type { Product } from '../types/product';
import { Loader2 } from 'lucide-vue-next';

// Props & Emits
const props = defineProps<{
  modelValue: string;
  error?: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
  'product-selected': [product: Product | null];
}>();

// Composables
const { products, loading, loadProducts } = useProducts();

// Lifecycle
onMounted(() => {
  loadProducts({ is_active: true });
});

// Computed
const selectedProduct = computed(() => {
  return products.value.find((p) => p.id === props.modelValue);
});

// Handlers
function handleChange(event: Event) {
  const productId = (event.target as HTMLSelectElement).value;
  emit('update:modelValue', productId);

  const product = products.value.find((p) => p.id === productId) || null;
  emit('product-selected', product);
}
</script>

<template>
  <div class="relative">
    <label class="kit-label">
      Produkt/Dienstleistung (Optional)
    </label>

    <!-- Loading State -->
    <div v-if="loading" class="kit-input flex items-center gap-2">
      <Loader2 :size="16" class="animate-spin" />
      <span class="text-white/60">Lade Produkte...</span>
    </div>

    <!-- Dropdown -->
    <select
      v-else
      :value="modelValue"
      @change="handleChange"
      class="kit-input"
      :class="{ 'border-red-400': error }"
    >
      <option value="">-- Produkt auswählen (oder manuell eingeben) --</option>
      <optgroup label="Privatkunden">
        <option
          v-for="product in products.filter(p => p.category === 'private_customer')"
          :key="product.id"
          :value="product.id"
        >
          {{ product.name }} - {{ product.unit_price }}€/{{ product.unit }}
        </option>
      </optgroup>
      <optgroup label="Kleine Unternehmen">
        <option
          v-for="product in products.filter(p => p.category === 'small_business')"
          :key="product.id"
          :value="product.id"
        >
          {{ product.name }} - {{ product.unit_price }}€/{{ product.unit }}
        </option>
      </optgroup>
      <optgroup label="Support & Services">
        <option
          v-for="product in products.filter(p => ['support', 'consulting'].includes(p.category))"
          :key="product.id"
          :value="product.id"
        >
          {{ product.name }} - {{ product.unit_price }}€/{{ product.unit }}
        </option>
      </optgroup>
      <optgroup label="Sonstiges">
        <option
          v-for="product in products.filter(p => !['private_customer', 'small_business', 'support', 'consulting'].includes(p.category))"
          :key="product.id"
          :value="product.id"
        >
          {{ product.name }} - {{ product.unit_price }}€/{{ product.unit }}
        </option>
      </optgroup>
    </select>

    <!-- Error Message -->
    <p v-if="error" class="text-xs text-red-300 mt-1">
      {{ error }}
    </p>

    <!-- Selected Product Info -->
    <p v-if="selectedProduct" class="text-xs text-white/60 mt-1">
      {{ selectedProduct.description || selectedProduct.short_description || 'Keine Beschreibung' }}
    </p>
  </div>
</template>

<style scoped>
/* No custom styles needed - using kit-components */
</style>
