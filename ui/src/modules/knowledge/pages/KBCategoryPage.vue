<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ChevronLeft, Plus, X, BookOpen, Pin, Eye } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';

const props = defineProps<{ categoryId: string }>();
const router = useRouter();

const loading = ref(true);
const category = ref<any>(null);
const articles = ref<any[]>([]);
const showCreateForm = ref(false);
const submitting = ref(false);
const filterStatus = ref('published');

const newArticle = ref({ title: '', excerpt: '', status: 'draft' });

onMounted(async () => {
  await Promise.all([loadCategory(), loadArticles()]);
  loading.value = false;
});

async function loadCategory() {
  try {
    const cats = await apiClient.get('/api/kb/categories');
    category.value = cats.data.find((c: any) => c.id === props.categoryId) || null;
  } catch { category.value = null; }
}

async function loadArticles() {
  const { data } = await apiClient.get('/api/kb/articles', {
    params: { category_id: props.categoryId, status: filterStatus.value || undefined, limit: 100 }
  });
  articles.value = data.items || [];
}

async function createArticle() {
  submitting.value = true;
  try {
    const { data } = await apiClient.post('/api/kb/articles', {
      ...newArticle.value,
      category_id: props.categoryId,
    });
    router.push(`/app/kb/articles/${data.id}`);
  } finally {
    submitting.value = false;
  }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}
</script>

<template>
  <div class="space-y-4 max-w-3xl">

    <!-- Header -->
    <div class="flex items-center gap-3">
      <button @click="router.push('/app/kb')"
        class="p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors">
        <ChevronLeft :size="20" />
      </button>
      <div class="flex-1">
        <h2 class="text-lg font-semibold text-white">{{ category?.name || 'Kategorie' }}</h2>
        <p v-if="category?.description" class="text-sm text-white/50">{{ category.description }}</p>
      </div>
      <button @click="showCreateForm = true"
        class="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/30 text-blue-300 rounded-lg transition-colors">
        <Plus :size="14" />Artikel
      </button>
    </div>

    <!-- Filter -->
    <div class="flex gap-2">
      <button v-for="s in [{ v: 'published', l: 'Veröffentlicht' }, { v: 'draft', l: 'Entwürfe' }, { v: '', l: 'Alle' }]"
        :key="s.v" @click="filterStatus = s.v; loadArticles()"
        :class="['px-3 py-1 text-xs rounded-lg border transition-colors',
          filterStatus === s.v ? 'bg-blue-500/20 border-blue-400/30 text-blue-300' : 'bg-white/5 border-white/10 text-white/50 hover:text-white']"
      >{{ s.l }}</button>
    </div>

    <!-- Create Form -->
    <div v-if="showCreateForm" class="p-4 rounded-xl bg-white/5 border border-blue-400/20 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-white">Neuer Artikel</h3>
        <button @click="showCreateForm = false" class="text-white/40 hover:text-white"><X :size="16" /></button>
      </div>
      <div>
        <label class="text-xs text-white/60 mb-1 block">Titel *</label>
        <input v-model="newArticle.title" type="text" class="kit-input w-full" placeholder="Artikeltitel..." />
      </div>
      <div>
        <label class="text-xs text-white/60 mb-1 block">Kurzbeschreibung</label>
        <input v-model="newArticle.excerpt" type="text" class="kit-input w-full" placeholder="Kurze Zusammenfassung..." />
      </div>
      <div class="flex items-center justify-between">
        <label class="flex items-center gap-2 text-sm text-white/60 cursor-pointer">
          <input type="checkbox" :checked="newArticle.status === 'published'"
            @change="newArticle.status = ($event.target as HTMLInputElement).checked ? 'published' : 'draft'" />
          Direkt veröffentlichen
        </label>
        <div class="flex gap-2">
          <button @click="showCreateForm = false" class="px-3 py-1.5 text-sm text-white/60 hover:text-white transition-colors">Abbrechen</button>
          <button @click="createArticle" :disabled="submitting || !newArticle.title"
            class="px-4 py-1.5 text-sm bg-blue-500/30 hover:bg-blue-500/40 border border-blue-400/30 text-blue-300 rounded-lg transition-colors disabled:opacity-50">
            Erstellen & Bearbeiten
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-10">
      <div class="w-7 h-7 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
    </div>

    <!-- Empty -->
    <div v-else-if="articles.length === 0" class="text-center py-10 text-white/40">
      <BookOpen :size="32" class="mx-auto mb-2 opacity-40" />
      <p>Keine Artikel vorhanden</p>
    </div>

    <!-- Articles -->
    <div v-else class="space-y-2">
      <div v-for="a in articles" :key="a.id"
        @click="router.push(`/app/kb/articles/${a.id}`)"
        class="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/8 cursor-pointer transition-colors"
      >
        <div class="flex items-start gap-3">
          <Pin v-if="a.pinned" :size="14" class="text-yellow-400/70 flex-shrink-0 mt-0.5" />
          <BookOpen v-else :size="14" class="text-white/30 flex-shrink-0 mt-0.5" />
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <div>
                <div class="text-sm font-medium text-white">{{ a.title }}</div>
                <div v-if="a.excerpt" class="text-xs text-white/50 mt-0.5 line-clamp-1">{{ a.excerpt }}</div>
                <div class="flex items-center gap-3 mt-1.5">
                  <span v-if="a.status === 'draft'" class="text-xs text-yellow-400/70">Entwurf</span>
                  <span class="text-xs text-white/30 flex items-center gap-1"><Eye :size="10" />{{ a.view_count }}</span>
                  <span class="text-xs text-white/30">{{ formatDate(a.updated_at) }}</span>
                  <div class="flex gap-0.5">
                    <span v-for="tag in (a.tags || []).slice(0,3)" :key="tag"
                      class="text-xs px-1.5 py-0.5 rounded bg-white/5 text-white/40">{{ tag }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
