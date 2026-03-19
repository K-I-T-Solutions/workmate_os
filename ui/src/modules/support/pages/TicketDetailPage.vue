<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ChevronLeft, Send, Lock, Unlock, Trash2, User, Tag, Clock, MessageSquare } from 'lucide-vue-next';
import md5 from 'md5';
import { apiClient } from '@/services/api/client';

const props = defineProps<{ ticketId: string }>();
const router = useRouter();

const loading = ref(true);
const ticket = ref<any>(null);
const newComment = ref('');
const isInternal = ref(false);
const submittingComment = ref(false);

const descriptionHtml = computed(() => {
  if (!ticket.value?.description) return '';
  // Backend liefert bereits <a href="mailto:..."> – nur https-Links und Zeilenumbrüche ergänzen
  return ticket.value.description
    .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener" class="text-indigo-400 hover:text-indigo-300 underline">$1</a>')
    .replace(/\n/g, '<br>');
});

const statusConfig: Record<string, { label: string; class: string }> = {
  open:        { label: 'Offen',           class: 'text-blue-300 bg-blue-500/10 border-blue-500/20' },
  in_progress: { label: 'In Bearbeitung',  class: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/20' },
  resolved:    { label: 'Gelöst',          class: 'text-green-300 bg-green-500/10 border-green-500/20' },
  closed:      { label: 'Geschlossen',     class: 'text-white/30 bg-white/5 border-white/10' },
};

const priorityConfig: Record<string, { label: string; class: string }> = {
  low:      { label: 'Niedrig',  class: 'text-white/40 bg-white/5 border-white/10' },
  medium:   { label: 'Mittel',   class: 'text-blue-300 bg-blue-500/10 border-blue-500/20' },
  high:     { label: 'Hoch',     class: 'text-orange-300 bg-orange-500/10 border-orange-500/20' },
  critical: { label: 'Kritisch', class: 'text-red-300 bg-red-500/10 border-red-500/20' },
};

const statusFlow: Record<string, string> = {
  open: 'in_progress', in_progress: 'resolved', resolved: 'closed',
};

const categoryLabels: Record<string, string> = {
  general: 'Allgemein', technical: 'Technisch', billing: 'Abrechnung',
  feature_request: 'Feature-Wunsch', bug: 'Bug',
};

onMounted(async () => {
  await loadTicket();
  loading.value = false;
});

async function loadTicket() {
  try {
    const { data } = await apiClient.get(`/api/support/tickets/${props.ticketId}`);
    ticket.value = data;
  } catch { ticket.value = null; }
}

async function advanceStatus() {
  const next = statusFlow[ticket.value.status];
  if (!next) return;
  await apiClient.put(`/api/support/tickets/${props.ticketId}`, { status: next });
  await loadTicket();
}

async function setStatus(status: string) {
  await apiClient.put(`/api/support/tickets/${props.ticketId}`, { status });
  await loadTicket();
}

async function submitComment() {
  if (!newComment.value.trim()) return;
  submittingComment.value = true;
  try {
    await apiClient.post(`/api/support/tickets/${props.ticketId}/comments`, {
      content: newComment.value,
      is_internal: isInternal.value,
    });
    newComment.value = '';
    await loadTicket();
  } finally {
    submittingComment.value = false;
  }
}

async function deleteComment(commentId: string) {
  await apiClient.delete(`/api/support/tickets/${props.ticketId}/comments/${commentId}`);
  await loadTicket();
}

async function deleteTicket() {
  if (!confirm('Ticket wirklich löschen?')) return;
  await apiClient.delete(`/api/support/tickets/${props.ticketId}`);
  router.push('/app/support/tickets');
}

function gravatarUrl(userId?: string, size = 32): string {
  if (!userId) return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&s=${size}`;
  return `https://www.gravatar.com/avatar/${md5(userId.toLowerCase().trim())}?d=mp&s=${size}`;
}

function formatDate(d: string) {
  return new Date(d).toLocaleString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}
</script>

<template>
  <div class="space-y-4">

    <div v-if="loading" class="flex justify-center py-20">
      <div class="w-8 h-8 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
    </div>

    <template v-else-if="ticket">

      <!-- Header -->
      <div class="flex items-start gap-3">
        <button @click="router.push('/app/support/tickets')"
          class="mt-1 p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors">
          <ChevronLeft :size="20" />
        </button>
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-2">
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-xs font-mono text-white/30">{{ ticket.ticket_number }}</span>
                <span class="text-xs px-2 py-0.5 rounded border" :class="statusConfig[ticket.status]?.class">
                  {{ statusConfig[ticket.status]?.label }}
                </span>
                <span class="text-xs px-2 py-0.5 rounded border" :class="priorityConfig[ticket.priority]?.class">
                  {{ priorityConfig[ticket.priority]?.label }}
                </span>
              </div>
              <h2 class="text-lg font-semibold text-white mt-1">{{ ticket.title }}</h2>
              <p class="text-xs text-white/40 mt-0.5">
                {{ categoryLabels[ticket.category] }} · {{ formatDate(ticket.created_at) }}
              </p>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <button v-if="statusFlow[ticket.status]" @click="advanceStatus"
                class="px-3 py-1.5 text-xs bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/30 text-blue-300 rounded-lg transition-colors">
                → {{ statusConfig[statusFlow[ticket.status]]?.label }}
              </button>
              <button v-if="ticket.status !== 'closed'" @click="setStatus('closed')"
                class="px-3 py-1.5 text-xs bg-white/5 hover:bg-white/10 border border-white/10 text-white/50 rounded-lg transition-colors">
                Schließen
              </button>
              <button @click="deleteTicket" class="p-1.5 text-white/30 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors">
                <Trash2 :size="14" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Content Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">

        <!-- Description (2/3) -->
        <div class="sm:col-span-2 space-y-4">
          <div v-if="ticket.description" class="p-4 rounded-xl bg-white/5 border border-white/10">
            <div class="text-xs text-white/50 uppercase tracking-wide mb-2">Beschreibung</div>
            <p class="text-sm text-white/80 leading-relaxed" v-html="descriptionHtml"></p>
          </div>

          <!-- Comments -->
          <div class="space-y-2">
            <div class="text-xs text-white/50 uppercase tracking-wide flex items-center gap-2">
              <MessageSquare :size="12" />Kommentare ({{ ticket.comments?.length ?? 0 }})
            </div>

            <div v-if="!ticket.comments?.length" class="text-sm text-white/30 py-3">
              Noch keine Kommentare
            </div>

            <div v-for="comment in ticket.comments" :key="comment.id"
              :class="['p-3 rounded-xl border', comment.is_internal
                ? 'bg-yellow-500/5 border-yellow-500/15'
                : 'bg-white/5 border-white/10']"
            >
              <div class="flex items-start gap-2.5">
                <img :src="gravatarUrl(comment.author_id, 28)" class="w-7 h-7 rounded-lg border border-white/10 object-cover flex-shrink-0 mt-0.5" />
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span v-if="comment.is_internal" class="text-xs text-yellow-400/80 flex items-center gap-1">
                      <Lock :size="10" />Interne Notiz
                    </span>
                    <span class="text-xs text-white/30">{{ formatDate(comment.created_at) }}</span>
                    <button @click="deleteComment(comment.id)"
                      class="ml-auto text-white/20 hover:text-red-400 transition-colors">
                      <Trash2 :size="11" />
                    </button>
                  </div>
                  <p class="text-sm text-white/80 whitespace-pre-wrap">{{ comment.content }}</p>
                </div>
              </div>
            </div>

            <!-- New Comment -->
            <div class="p-3 rounded-xl bg-white/5 border border-white/10 space-y-2">
              <textarea v-model="newComment" rows="3" placeholder="Kommentar schreiben..."
                class="kit-input w-full resize-none text-sm" />
              <div class="flex items-center justify-between">
                <label class="flex items-center gap-1.5 text-xs text-white/50 cursor-pointer">
                  <input v-model="isInternal" type="checkbox" class="rounded" />
                  <Lock :size="11" />Interne Notiz
                </label>
                <button @click="submitComment" :disabled="submittingComment || !newComment.trim()"
                  class="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/30 text-blue-300 rounded-lg transition-colors disabled:opacity-50">
                  <Send :size="12" />Senden
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Meta (1/3) -->
        <div class="space-y-3">
          <div class="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
            <div class="text-xs text-white/50 uppercase tracking-wide">Details</div>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-white/50">Status</span>
                <span class="text-xs px-2 py-0.5 rounded border" :class="statusConfig[ticket.status]?.class">
                  {{ statusConfig[ticket.status]?.label }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-white/50">Priorität</span>
                <span class="text-xs px-2 py-0.5 rounded border" :class="priorityConfig[ticket.priority]?.class">
                  {{ priorityConfig[ticket.priority]?.label }}
                </span>
              </div>
              <div class="flex justify-between">
                <span class="text-white/50">Kategorie</span>
                <span class="text-white/70 text-xs">{{ categoryLabels[ticket.category] }}</span>
              </div>
              <div v-if="ticket.assignee_id" class="flex justify-between">
                <span class="text-white/50">Zugewiesen</span>
                <span class="text-white/70 text-xs truncate max-w-24">{{ ticket.assignee_id }}</span>
              </div>
            </div>
          </div>

          <div class="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2">
            <div class="text-xs text-white/50 uppercase tracking-wide">Zeitstempel</div>
            <div class="space-y-1.5 text-xs">
              <div class="flex justify-between gap-2">
                <span class="text-white/40">Erstellt</span>
                <span class="text-white/60">{{ formatDate(ticket.created_at) }}</span>
              </div>
              <div class="flex justify-between gap-2">
                <span class="text-white/40">Aktualisiert</span>
                <span class="text-white/60">{{ formatDate(ticket.updated_at) }}</span>
              </div>
              <div v-if="ticket.resolved_at" class="flex justify-between gap-2">
                <span class="text-white/40">Gelöst</span>
                <span class="text-green-400/70">{{ formatDate(ticket.resolved_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Status Actions -->
          <div class="p-4 rounded-xl bg-white/5 border border-white/10 space-y-2">
            <div class="text-xs text-white/50 uppercase tracking-wide mb-2">Status ändern</div>
            <button v-for="(cfg, s) in statusConfig" :key="s"
              @click="setStatus(s)"
              :disabled="ticket.status === s"
              :class="['w-full text-xs px-3 py-2 rounded-lg border transition-colors text-left',
                ticket.status === s ? 'opacity-50 cursor-default ' + cfg.class : 'bg-white/5 border-white/10 text-white/60 hover:bg-white/10']"
            >{{ cfg.label }}</button>
          </div>
        </div>
      </div>

    </template>

    <div v-else class="text-center py-20 text-white/40">
      <p>Ticket nicht gefunden</p>
      <button @click="router.push('/app/support/tickets')" class="mt-4 text-sm text-blue-400 hover:text-blue-300">Zurück</button>
    </div>

  </div>
</template>
