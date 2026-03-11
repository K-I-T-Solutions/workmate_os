<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Plus, Search, X, Ticket, AlertCircle, Clock, CheckCircle, XCircle } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';

const router = useRouter();

const loading = ref(true);
const tickets = ref<any[]>([]);
const total = ref(0);
const showCreateForm = ref(false);
const submitting = ref(false);
const search = ref('');
const filterStatus = ref('');
const filterPriority = ref('');

const statusConfig: Record<string, { label: string; class: string; icon: any }> = {
  open:        { label: 'Offen',        class: 'text-blue-300 bg-blue-500/10 border-blue-500/20',   icon: Ticket },
  in_progress: { label: 'In Bearbeitung', class: 'text-yellow-300 bg-yellow-500/10 border-yellow-500/20', icon: Clock },
  resolved:    { label: 'Gelöst',       class: 'text-green-300 bg-green-500/10 border-green-500/20', icon: CheckCircle },
  closed:      { label: 'Geschlossen',  class: 'text-white/30 bg-white/5 border-white/10',           icon: XCircle },
};

const priorityConfig: Record<string, { label: string; class: string }> = {
  low:      { label: 'Niedrig',  class: 'text-white/40 bg-white/5 border-white/10' },
  medium:   { label: 'Mittel',   class: 'text-blue-300 bg-blue-500/10 border-blue-500/20' },
  high:     { label: 'Hoch',     class: 'text-orange-300 bg-orange-500/10 border-orange-500/20' },
  critical: { label: 'Kritisch', class: 'text-red-300 bg-red-500/10 border-red-500/20' },
};

const categoryLabels: Record<string, string> = {
  general: 'Allgemein', technical: 'Technisch', billing: 'Abrechnung',
  feature_request: 'Feature-Wunsch', bug: 'Bug',
};

const newTicket = ref({
  title: '', description: '', priority: 'medium', category: 'general',
});

onMounted(loadTickets);

async function loadTickets() {
  loading.value = true;
  try {
    const params: any = { limit: 100, skip: 0 };
    if (filterStatus.value) params.status = filterStatus.value;
    if (filterPriority.value) params.priority = filterPriority.value;
    if (search.value) params.search = search.value;
    const { data } = await apiClient.get('/api/support/tickets', { params });
    tickets.value = data.items || data;
    total.value = data.total || tickets.value.length;
  } finally {
    loading.value = false;
  }
}

async function createTicket() {
  submitting.value = true;
  try {
    const { data } = await apiClient.post('/api/support/tickets', newTicket.value);
    showCreateForm.value = false;
    newTicket.value = { title: '', description: '', priority: 'medium', category: 'general' };
    router.push(`/app/support/tickets/${data.id}`);
  } finally {
    submitting.value = false;
  }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

let searchTimeout: any;
function onSearch() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(loadTickets, 300);
}
</script>

<template>
  <div class="space-y-4">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-white">Support Tickets</h1>
        <p class="text-sm text-white/50 mt-0.5">{{ total }} Ticket(s) gesamt</p>
      </div>
      <button @click="showCreateForm = true"
        class="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/30 text-blue-300 rounded-lg transition-colors">
        <Plus :size="15" />Neues Ticket
      </button>
    </div>

    <!-- Filter Bar -->
    <div class="flex items-center gap-2 flex-wrap">
      <div class="relative flex-1 min-w-48">
        <Search :size="14" class="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
        <input v-model="search" @input="onSearch" type="text" placeholder="Suchen..."
          class="kit-input w-full pl-8 text-sm" />
      </div>
      <select v-model="filterStatus" @change="loadTickets" class="kit-input text-sm">
        <option value="">Alle Status</option>
        <option v-for="(cfg, key) in statusConfig" :key="key" :value="key">{{ cfg.label }}</option>
      </select>
      <select v-model="filterPriority" @change="loadTickets" class="kit-input text-sm">
        <option value="">Alle Prioritäten</option>
        <option v-for="(cfg, key) in priorityConfig" :key="key" :value="key">{{ cfg.label }}</option>
      </select>
    </div>

    <!-- Create Form -->
    <div v-if="showCreateForm" class="p-5 rounded-xl bg-white/5 border border-blue-400/20 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="font-semibold text-white">Neues Ticket</h3>
        <button @click="showCreateForm = false" class="text-white/40 hover:text-white"><X :size="16" /></button>
      </div>
      <div>
        <label class="text-xs text-white/60 mb-1 block">Titel *</label>
        <input v-model="newTicket.title" type="text" placeholder="Kurze Beschreibung des Problems" class="kit-input w-full" />
      </div>
      <div>
        <label class="text-xs text-white/60 mb-1 block">Beschreibung</label>
        <textarea v-model="newTicket.description" rows="3" placeholder="Detaillierte Beschreibung..." class="kit-input w-full resize-none" />
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-xs text-white/60 mb-1 block">Priorität</label>
          <select v-model="newTicket.priority" class="kit-input w-full">
            <option v-for="(cfg, key) in priorityConfig" :key="key" :value="key">{{ cfg.label }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">Kategorie</label>
          <select v-model="newTicket.category" class="kit-input w-full">
            <option v-for="(label, key) in categoryLabels" :key="key" :value="key">{{ label }}</option>
          </select>
        </div>
      </div>
      <div class="flex justify-end gap-2">
        <button @click="showCreateForm = false" class="px-3 py-1.5 text-sm text-white/60 hover:text-white transition-colors">Abbrechen</button>
        <button @click="createTicket" :disabled="submitting || !newTicket.title"
          class="px-4 py-1.5 text-sm bg-blue-500/30 hover:bg-blue-500/40 border border-blue-400/30 text-blue-300 rounded-lg transition-colors disabled:opacity-50">
          {{ submitting ? 'Wird erstellt...' : 'Ticket erstellen' }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
    </div>

    <!-- Empty -->
    <div v-else-if="tickets.length === 0" class="text-center py-14 text-white/40">
      <Ticket :size="36" class="mx-auto mb-3 opacity-40" />
      <p>Keine Tickets vorhanden</p>
    </div>

    <!-- Ticket List -->
    <div v-else class="space-y-2">
      <div v-for="ticket in tickets" :key="ticket.id"
        @click="router.push(`/app/support/tickets/${ticket.id}`)"
        class="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/8 transition-colors cursor-pointer"
      >
        <div class="flex items-start gap-3">
          <div class="p-1.5 rounded-lg border flex-shrink-0 mt-0.5"
            :class="statusConfig[ticket.status]?.class">
            <component :is="statusConfig[ticket.status]?.icon" :size="14" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="text-xs text-white/30 font-mono">{{ ticket.ticket_number }}</span>
                  <span class="text-sm font-medium text-white">{{ ticket.title }}</span>
                </div>
                <div class="flex items-center gap-2 mt-1 flex-wrap">
                  <span class="text-xs px-1.5 py-0.5 rounded border" :class="priorityConfig[ticket.priority]?.class">
                    {{ priorityConfig[ticket.priority]?.label }}
                  </span>
                  <span class="text-xs text-white/40">{{ categoryLabels[ticket.category] || ticket.category }}</span>
                  <span v-if="ticket.comment_count" class="text-xs text-white/30">
                    💬 {{ ticket.comment_count }}
                  </span>
                </div>
              </div>
              <span class="text-xs text-white/30 flex-shrink-0 whitespace-nowrap">{{ formatDate(ticket.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
