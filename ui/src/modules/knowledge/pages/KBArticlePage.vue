<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ChevronLeft, Edit2, Check, X, ThumbsUp, ThumbsDown, Eye, Pin, Tag } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';

const props = defineProps<{ articleId: string }>();
const router = useRouter();

const loading = ref(true);
const article = ref<any>(null);
const editing = ref(false);
const saving = ref(false);
const voted = ref<boolean | null>(null);

const editData = ref({ title: '', content: '', excerpt: '', status: 'draft', pinned: false, tags: '' });

onMounted(async () => {
  await loadArticle();
  loading.value = false;
});

async function loadArticle() {
  try {
    const { data } = await apiClient.get(`/api/kb/articles/${props.articleId}`);
    article.value = data;
  } catch { article.value = null; }
}

function startEdit() {
  editData.value = {
    title: article.value.title,
    content: article.value.content || '',
    excerpt: article.value.excerpt || '',
    status: article.value.status,
    pinned: article.value.pinned,
    tags: (article.value.tags || []).join(', '),
  };
  editing.value = true;
}

async function saveEdit() {
  saving.value = true;
  try {
    const payload: any = {
      title: editData.value.title,
      content: editData.value.content,
      excerpt: editData.value.excerpt || null,
      status: editData.value.status,
      pinned: editData.value.pinned,
      tags: editData.value.tags.split(',').map((t: string) => t.trim()).filter(Boolean),
    };
    await apiClient.put(`/api/kb/articles/${props.articleId}`, payload);
    editing.value = false;
    await loadArticle();
  } finally {
    saving.value = false;
  }
}

async function deleteArticle() {
  if (!confirm('Artikel wirklich löschen?')) return;
  await apiClient.delete(`/api/kb/articles/${props.articleId}`);
  router.back();
}

async function vote(helpful: boolean) {
  if (voted.value !== null) return;
  voted.value = helpful;
  await apiClient.post(`/api/kb/articles/${props.articleId}/vote`, null, { params: { helpful } });
  await loadArticle();
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// Markdown-ähnliche Formatierung (einfach)
function renderContent(text: string): string {
  if (!text) return '';
  return text
    .replace(/^### (.+)$/gm, '<h3 class="text-base font-semibold text-white mt-4 mb-2">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-lg font-semibold text-white mt-5 mb-2">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-xl font-bold text-white mt-6 mb-3">$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-white">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em class="italic text-white/80">$1</em>')
    .replace(/`(.+?)`/g, '<code class="px-1.5 py-0.5 bg-white/10 rounded text-xs font-mono text-blue-300">$1</code>')
    .replace(/^- (.+)$/gm, '<li class="ml-4 text-white/70">• $1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4 text-white/70">$1. $2</li>')
    .replace(/\n\n/g, '</p><p class="text-white/70 leading-relaxed mb-3">')
    .replace(/\n/g, '<br>');
}
</script>

<template>
  <div class="space-y-4 max-w-3xl">

    <div v-if="loading" class="flex justify-center py-20">
      <div class="w-7 h-7 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
    </div>

    <template v-else-if="article">

      <!-- Header -->
      <div class="flex items-start gap-3">
        <button @click="router.back()"
          class="mt-1 p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors">
          <ChevronLeft :size="20" />
        </button>
        <div class="flex-1 min-w-0">
          <div v-if="!editing">
            <div class="flex items-center gap-2 flex-wrap">
              <Pin v-if="article.pinned" :size="13" class="text-yellow-400/80" />
              <span v-if="article.status === 'draft'"
                class="text-xs px-2 py-0.5 rounded bg-yellow-500/10 border border-yellow-500/20 text-yellow-300">Entwurf</span>
              <span class="text-xs text-white/30 flex items-center gap-1"><Eye :size="10" />{{ article.view_count }} Aufrufe</span>
            </div>
            <h1 class="text-xl font-bold text-white mt-1">{{ article.title }}</h1>
            <p v-if="article.excerpt" class="text-sm text-white/50 mt-1">{{ article.excerpt }}</p>
            <div class="flex items-center gap-3 mt-2 text-xs text-white/30 flex-wrap">
              <span>{{ formatDate(article.updated_at) }}</span>
              <div v-if="article.tags?.length" class="flex items-center gap-1">
                <Tag :size="10" />
                <span v-for="t in article.tags" :key="t" class="px-1.5 py-0.5 bg-white/5 rounded">{{ t }}</span>
              </div>
            </div>
          </div>
          <div v-else class="space-y-2">
            <input v-model="editData.title" type="text" class="kit-input w-full text-base font-semibold" placeholder="Titel..." />
            <input v-model="editData.excerpt" type="text" class="kit-input w-full text-sm" placeholder="Kurzbeschreibung..." />
          </div>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <template v-if="!editing">
            <button @click="startEdit"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-white/5 hover:bg-white/10 border border-white/10 text-white/60 hover:text-white rounded-lg transition-colors">
              <Edit2 :size="13" />Bearbeiten
            </button>
            <button @click="deleteArticle" class="p-1.5 text-white/30 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors">
              <X :size="14" />
            </button>
          </template>
          <template v-else>
            <button @click="saveEdit" :disabled="saving"
              class="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-green-500/20 hover:bg-green-500/30 border border-green-500/20 text-green-300 rounded-lg transition-colors disabled:opacity-50">
              <Check :size="13" />{{ saving ? 'Speichert...' : 'Speichern' }}
            </button>
            <button @click="editing = false" class="p-1.5 text-white/40 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
              <X :size="14" />
            </button>
          </template>
        </div>
      </div>

      <!-- Edit Options -->
      <div v-if="editing" class="flex items-center gap-4 px-2">
        <label class="flex items-center gap-2 text-xs text-white/60 cursor-pointer">
          <input type="checkbox" :checked="editData.status === 'published'"
            @change="editData.status = ($event.target as HTMLInputElement).checked ? 'published' : 'draft'" />
          Veröffentlicht
        </label>
        <label class="flex items-center gap-2 text-xs text-white/60 cursor-pointer">
          <input v-model="editData.pinned" type="checkbox" />Angepinnt
        </label>
        <div class="flex-1">
          <input v-model="editData.tags" type="text" class="kit-input w-full text-xs" placeholder="Tags (kommagetrennt)" />
        </div>
      </div>

      <!-- Content -->
      <div class="p-5 rounded-xl bg-white/5 border border-white/10">
        <div v-if="!editing">
          <div v-if="article.content"
            class="prose-custom text-sm text-white/70 leading-relaxed"
            v-html="'<p class=\'text-white/70 leading-relaxed mb-3\'>' + renderContent(article.content) + '</p>'"
          />
          <div v-else class="text-sm text-white/30 italic py-4 text-center">
            Noch kein Inhalt. Klicke auf Bearbeiten um Inhalt hinzuzufügen.
          </div>
        </div>
        <div v-else>
          <label class="text-xs text-white/60 mb-2 block">Inhalt (Markdown)</label>
          <textarea v-model="editData.content" rows="20"
            class="kit-input w-full resize-y font-mono text-sm"
            placeholder="# Überschrift&#10;&#10;Text hier...&#10;&#10;## Abschnitt&#10;&#10;- Listenpunkt&#10;- Listenpunkt" />
          <p class="text-xs text-white/30 mt-1">Markdown wird unterstützt: # Überschrift, **fett**, *kursiv*, `code`, - Liste</p>
        </div>
      </div>

      <!-- Feedback -->
      <div v-if="!editing" class="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10">
        <span class="text-sm text-white/50">War dieser Artikel hilfreich?</span>
        <div class="flex items-center gap-3">
          <button @click="vote(true)" :disabled="voted !== null"
            :class="['flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg border transition-colors',
              voted === true ? 'bg-green-500/20 border-green-500/20 text-green-300' : 'bg-white/5 border-white/10 text-white/50 hover:text-green-300 disabled:cursor-default']">
            <ThumbsUp :size="13" />{{ article.helpful_count }}
          </button>
          <button @click="vote(false)" :disabled="voted !== null"
            :class="['flex items-center gap-1.5 px-3 py-1.5 text-xs rounded-lg border transition-colors',
              voted === false ? 'bg-red-500/20 border-red-500/20 text-red-300' : 'bg-white/5 border-white/10 text-white/50 hover:text-red-300 disabled:cursor-default']">
            <ThumbsDown :size="13" />{{ article.not_helpful_count }}
          </button>
        </div>
      </div>

    </template>

    <div v-else class="text-center py-20 text-white/40">
      <p>Artikel nicht gefunden</p>
      <button @click="router.back()" class="mt-4 text-sm text-blue-400 hover:text-blue-300">Zurück</button>
    </div>

  </div>
</template>
