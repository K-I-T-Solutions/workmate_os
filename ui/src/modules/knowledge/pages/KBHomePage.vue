<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Search, BookOpen, Plus, X, ChevronRight, Pin } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';

const router = useRouter();

const loading = ref(true);
const error = ref<string | null>(null);
const categories = ref<any[]>([]);
const recentArticles = ref<any[]>([]);
const search = ref('');
const searchResults = ref<any[]>([]);
const searching = ref(false);
const showCategoryForm = ref(false);
const submitting = ref(false);

const colorOptions = ['blue', 'purple', 'green', 'orange', 'red', 'yellow', 'pink', 'indigo'];
const colorClasses: Record<string, string> = {
  blue: 'bg-blue-500/15 border-blue-400/20 text-blue-300',
  purple: 'bg-purple-500/15 border-purple-400/20 text-purple-300',
  green: 'bg-green-500/15 border-green-400/20 text-green-300',
  orange: 'bg-orange-500/15 border-orange-400/20 text-orange-300',
  red: 'bg-red-500/15 border-red-400/20 text-red-300',
  yellow: 'bg-yellow-500/15 border-yellow-400/20 text-yellow-300',
  pink: 'bg-pink-500/15 border-pink-400/20 text-pink-300',
  indigo: 'bg-indigo-500/15 border-indigo-400/20 text-indigo-300',
};

const newCategory = ref({ name: '', description: '', slug: '', icon: 'BookOpen', color: 'blue', order: 0 });

onMounted(async () => {
  error.value = null;
  try {
    await Promise.all([loadCategories(), loadRecent()]);
  } catch (e) {
    error.value = 'Daten konnten nicht geladen werden.';
  } finally {
    loading.value = false;
  }
});

async function loadCategories() {
  const { data } = await apiClient.get('/api/kb/categories');
  categories.value = data;
}

async function loadRecent() {
  const { data } = await apiClient.get('/api/kb/articles', { params: { status: 'published', limit: 5 } });
  recentArticles.value = data.items || [];
}

let searchTimer: any;
async function onSearch() {
  clearTimeout(searchTimer);
  if (!search.value.trim()) { searchResults.value = []; return; }
  searchTimer = setTimeout(async () => {
    searching.value = true;
    const { data } = await apiClient.get('/api/kb/articles', { params: { search: search.value, status: 'published', limit: 10 } });
    searchResults.value = data.items || [];
    searching.value = false;
  }, 300);
}

function autoSlug() {
  newCategory.value.slug = newCategory.value.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

async function createCategory() {
  submitting.value = true;
  try {
    await apiClient.post('/api/kb/categories', newCategory.value);
    showCategoryForm.value = false;
    newCategory.value = { name: '', description: '', slug: '', icon: 'BookOpen', color: 'blue', order: 0 };
    await loadCategories();
  } finally {
    submitting.value = false;
  }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}
</script>

<template>
  <div class="space-y-6 max-w-3xl">

    <!-- Search -->
    <div>
      <div class="relative">
        <Search :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-white/30" />
        <input v-model="search" @input="onSearch" type="text"
          placeholder="Wissensdatenbank durchsuchen..."
          class="kit-input w-full pl-11 py-3 text-base" />
        <button v-if="search" @click="search = ''; searchResults = []"
          class="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white">
          <X :size="16" />
        </button>
      </div>

      <!-- Search Results -->
      <div v-if="search && (searchResults.length > 0 || searching)" class="kit-card mt-2 p-3 space-y-1">
        <div v-if="searching" class="text-sm text-white/40 py-2 text-center">Suche...</div>
        <div v-else-if="searchResults.length === 0" class="text-sm text-white/40 py-2 text-center">Keine Ergebnisse</div>
        <div v-for="a in searchResults" :key="a.id"
          @click="router.push(`/app/kb/articles/${a.id}`)"
          class="flex items-center gap-2 p-2 rounded-lg hover:bg-white/10 cursor-pointer transition-colors">
          <BookOpen :size="14" class="text-white/40 flex-shrink-0" />
          <span class="text-sm text-white">{{ a.title }}</span>
          <span v-if="a.pinned" class="ml-auto"><Pin :size="11" class="text-yellow-400/70" /></span>
        </div>
      </div>
    </div>

    <!-- Categories Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-base font-semibold text-white">Kategorien</h2>
      <button @click="showCategoryForm = true"
        class="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-white/5 hover:bg-white/10 border border-white/10 text-white/60 hover:text-white rounded-lg transition-colors">
        <Plus :size="13" />Kategorie
      </button>
    </div>

    <!-- Create Category Form -->
    <div v-if="showCategoryForm" class="kit-card p-4 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-white">Neue Kategorie</h3>
        <button @click="showCategoryForm = false" class="text-white/40 hover:text-white"><X :size="16" /></button>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div class="col-span-2">
          <label class="text-xs text-white/60 mb-1 block">Name *</label>
          <input v-model="newCategory.name" @input="autoSlug" type="text" class="kit-input w-full" placeholder="z.B. Einrichtung & Setup" />
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">Slug</label>
          <input v-model="newCategory.slug" type="text" class="kit-input w-full font-mono text-xs" />
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">Farbe</label>
          <div class="flex gap-1.5 flex-wrap">
            <button v-for="c in colorOptions" :key="c"
              @click="newCategory.color = c"
              :class="['w-6 h-6 rounded-md border-2 transition-all', colorClasses[c],
                newCategory.color === c ? 'border-white/60 scale-110' : 'border-transparent']"
            />
          </div>
        </div>
        <div class="col-span-2">
          <label class="text-xs text-white/60 mb-1 block">Beschreibung</label>
          <input v-model="newCategory.description" type="text" class="kit-input w-full" />
        </div>
      </div>
      <div class="flex justify-end gap-2">
        <button @click="showCategoryForm = false" class="px-3 py-1.5 text-sm text-white/60 hover:text-white transition-colors">Abbrechen</button>
        <button @click="createCategory" :disabled="submitting || !newCategory.name || !newCategory.slug"
          class="px-4 py-1.5 text-sm bg-blue-500/30 hover:bg-blue-500/40 border border-blue-400/30 text-blue-300 rounded-lg transition-colors disabled:opacity-50">
          Anlegen
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-10">
      <div class="w-7 h-7 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
    </div>

    <!-- Error State -->
    <div v-if="error && !loading" class="kit-card p-6 text-center">
      <p class="text-red-400 text-sm">{{ error }}</p>
      <button class="kit-btn-secondary mt-3 text-xs" @click="$router.go(0)">Erneut versuchen</button>
    </div>

    <!-- No Categories -->
    <div v-else-if="categories.length === 0" class="text-center py-10 text-white/40">
      <BookOpen :size="36" class="mx-auto mb-3 opacity-40" />
      <p>Noch keine Kategorien angelegt</p>
    </div>

    <!-- Category Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <div v-for="cat in categories" :key="cat.id"
        @click="router.push(`/app/kb/categories/${cat.id}`)"
        class="p-4 rounded-xl border cursor-pointer hover:scale-[1.01] transition-all"
        :class="colorClasses[cat.color] || colorClasses.blue"
      >
        <div class="flex items-start justify-between">
          <div>
            <div class="font-semibold text-sm">{{ cat.name }}</div>
            <div v-if="cat.description" class="text-xs opacity-70 mt-0.5 line-clamp-2">{{ cat.description }}</div>
          </div>
          <span class="text-xs opacity-60 flex-shrink-0 ml-2">{{ cat.article_count }} Artikel</span>
        </div>
        <div class="flex items-center justify-end mt-3 opacity-60">
          <ChevronRight :size="14" />
        </div>
      </div>
    </div>

    <!-- Recent Articles -->
    <div v-if="recentArticles.length > 0">
      <h2 class="text-base font-semibold text-white mb-3">Zuletzt aktualisiert</h2>
      <div class="space-y-1.5">
        <div v-for="a in recentArticles" :key="a.id"
          @click="router.push(`/app/kb/articles/${a.id}`)"
          class="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/8 cursor-pointer transition-colors">
          <Pin v-if="a.pinned" :size="12" class="text-yellow-400/70 flex-shrink-0" />
          <BookOpen v-else :size="12" class="text-white/30 flex-shrink-0" />
          <span class="text-sm text-white flex-1 truncate">{{ a.title }}</span>
          <span class="text-xs text-white/30 flex-shrink-0">{{ formatDate(a.updated_at) }}</span>
        </div>
      </div>
    </div>

  </div>
</template>
