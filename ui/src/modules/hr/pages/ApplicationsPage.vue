<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ChevronLeft, Plus, X, User, Mail, Phone, Star, Calendar, FileText } from 'lucide-vue-next';
import md5 from 'md5';
import { apiClient } from '@/services/api/client';

const props = defineProps<{ jobId: string }>();
const router = useRouter();

const loading = ref(true);
const error = ref<string | null>(null);
const job = ref<any>(null);
const applications = ref<any[]>([]);
const showCreateForm = ref(false);
const submitting = ref(false);
const filterStatus = ref('');

const statusConfig: Record<string, { label: string; class: string }> = {
  received:   { label: 'Eingegangen',   class: 'badge badge-blue' },
  screening:  { label: 'Screening',     class: 'badge badge-amber' },
  interview:  { label: 'Interview',     class: 'badge badge-cyan' },
  assessment: { label: 'Assessment',    class: 'badge badge-orange' },
  offer:      { label: 'Angebot',       class: 'badge badge-green' },
  accepted:   { label: 'Angenommen',    class: 'badge badge-green' },
  rejected:   { label: 'Abgelehnt',     class: 'badge badge-red' },
  withdrawn:  { label: 'Zurückgezogen', class: 'badge badge-gray' },
};

const nextStatus: Record<string, string> = {
  received: 'screening', screening: 'interview', interview: 'assessment',
  assessment: 'offer', offer: 'accepted',
};

const filteredApps = computed(() =>
  filterStatus.value ? applications.value.filter(a => a.status === filterStatus.value) : applications.value
);

const newApp = ref({ first_name: '', last_name: '', email: '', phone: '', cover_letter: '', cv_url: '', linkedin_url: '' });

onMounted(async () => {
  await Promise.all([loadJob(), loadApplications()]);
});

async function loadJob() {
  try {
    const { data } = await apiClient.get(`/api/hr/recruiting/jobs/${props.jobId}`);
    job.value = data;
  } catch { job.value = null; }
}

async function loadApplications() {
  loading.value = true;
  error.value = null;
  try {
    const { data } = await apiClient.get('/api/hr/recruiting/applications', { params: { job_posting_id: props.jobId, limit: 200 } });
    applications.value = data.items || data;
  } catch (e) {
    error.value = 'Daten konnten nicht geladen werden.';
  } finally {
    loading.value = false;
  }
}

async function createApplication() {
  submitting.value = true;
  try {
    await apiClient.post('/api/hr/recruiting/applications', { ...newApp.value, job_posting_id: props.jobId });
    showCreateForm.value = false;
    newApp.value = { first_name: '', last_name: '', email: '', phone: '', cover_letter: '', cv_url: '', linkedin_url: '' };
    await loadApplications();
  } finally {
    submitting.value = false;
  }
}

async function advanceStatus(app: any) {
  const next = nextStatus[app.status];
  if (!next) return;
  await apiClient.put(`/api/hr/recruiting/applications/${app.id}`, { status: next });
  await loadApplications();
}

async function rejectApplication(app: any) {
  await apiClient.put(`/api/hr/recruiting/applications/${app.id}`, { status: 'rejected' });
  await loadApplications();
}

async function setRating(app: any, rating: number) {
  await apiClient.put(`/api/hr/recruiting/applications/${app.id}`, { rating });
  await loadApplications();
}

function gravatarUrl(email?: string, size = 36): string {
  if (!email) return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&s=${size}`;
  return `https://www.gravatar.com/avatar/${md5(email.toLowerCase().trim())}?d=mp&s=${size}`;
}

function formatDate(d?: string) {
  if (!d) return '–';
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}
</script>

<template>
  <div class="space-y-4">

    <!-- Back + Header -->
    <div class="flex items-start gap-3">
      <button @click="router.push('/app/hr/recruiting')" class="mt-1 p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors">
        <ChevronLeft :size="20" />
      </button>
      <div class="flex-1">
        <h2 class="text-lg font-semibold text-white">{{ job?.title || 'Bewerbungen' }}</h2>
        <p class="text-sm text-white/50">{{ applications.length }} Bewerbung(en)</p>
      </div>
      <button @click="showCreateForm = true" class="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/30 text-blue-300 rounded-lg transition-colors">
        <Plus :size="14" />Bewerbung
      </button>
    </div>

    <!-- Status Filter -->
    <div class="flex gap-1.5 flex-wrap">
      <button v-for="s in ['', ...Object.keys(statusConfig)]" :key="s"
        @click="filterStatus = s"
        :class="['px-2.5 py-1 text-xs rounded-lg transition-colors border',
          filterStatus === s ? 'bg-blue-500/20 border-blue-400/30 text-blue-300' : 'bg-white/5 border-white/10 text-white/50 hover:text-white']"
      >{{ s === '' ? 'Alle' : statusConfig[s]?.label }}</button>
    </div>

    <!-- Create Form -->
    <div v-if="showCreateForm" class="kit-card p-4 space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-white">Neue Bewerbung erfassen</h3>
        <button @click="showCreateForm = false" class="text-white/40 hover:text-white"><X :size="16" /></button>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label class="text-xs text-white/60 mb-1 block">Vorname *</label>
          <input v-model="newApp.first_name" type="text" class="kit-input w-full" />
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">Nachname *</label>
          <input v-model="newApp.last_name" type="text" class="kit-input w-full" />
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">E-Mail *</label>
          <input v-model="newApp.email" type="email" class="kit-input w-full" />
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">Telefon</label>
          <input v-model="newApp.phone" type="tel" class="kit-input w-full" />
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">LinkedIn URL</label>
          <input v-model="newApp.linkedin_url" type="url" class="kit-input w-full" />
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">CV URL</label>
          <input v-model="newApp.cv_url" type="url" class="kit-input w-full" />
        </div>
      </div>
      <div class="flex justify-end gap-2">
        <button @click="showCreateForm = false" class="px-3 py-1.5 text-sm text-white/60 hover:text-white transition-colors">Abbrechen</button>
        <button @click="createApplication" :disabled="submitting || !newApp.first_name || !newApp.email"
          class="px-3 py-1.5 text-sm bg-blue-500/30 hover:bg-blue-500/40 border border-blue-400/30 text-blue-300 rounded-lg transition-colors disabled:opacity-50">
          Hinzufügen
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-8 h-8 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
    </div>

    <!-- Error State -->
    <div v-if="error && !loading" class="kit-card p-6 text-center">
      <p class="text-red-400 text-sm">{{ error }}</p>
      <button class="kit-btn-secondary mt-3 text-xs" @click="loadApplications()">Erneut versuchen</button>
    </div>

    <!-- Empty -->
    <div v-else-if="filteredApps.length === 0" class="text-center py-12 text-white/40">
      <User :size="32" class="mx-auto mb-2 opacity-40" />
      <p>Keine Bewerbungen vorhanden</p>
    </div>

    <!-- Applications -->
    <div v-else class="space-y-2">
      <div v-for="app in filteredApps" :key="app.id"
        class="kit-card p-3 hover:bg-white/10 transition-colors"
      >
        <div class="flex items-start gap-3">
          <img :src="gravatarUrl(app.email, 36)" :alt="app.first_name"
            class="w-9 h-9 rounded-lg border border-white/10 object-cover flex-shrink-0 mt-0.5" />

          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="text-sm font-medium text-white">{{ app.first_name }} {{ app.last_name }}</span>
                  <span :class="statusConfig[app.status]?.class">
                    {{ statusConfig[app.status]?.label }}
                  </span>
                </div>
                <div class="flex items-center gap-3 text-xs text-white/40 mt-0.5 flex-wrap">
                  <span class="flex items-center gap-1"><Mail :size="10" />{{ app.email }}</span>
                  <span v-if="app.phone" class="flex items-center gap-1"><Phone :size="10" />{{ app.phone }}</span>
                  <span class="flex items-center gap-1"><Calendar :size="10" />{{ formatDate(app.created_at) }}</span>
                </div>
              </div>

              <!-- Rating -->
              <div class="flex items-center gap-0.5 flex-shrink-0">
                <button v-for="n in 5" :key="n"
                  @click="setRating(app, n)"
                  :class="['transition-colors', n <= (app.rating || 0) ? 'text-yellow-400' : 'text-white/20 hover:text-yellow-300']"
                >
                  <Star :size="13" :fill="n <= (app.rating || 0) ? 'currentColor' : 'none'" />
                </button>
              </div>
            </div>

            <div v-if="app.notes" class="mt-1.5 text-xs text-white/50 flex items-center gap-1">
              <FileText :size="10" />{{ app.notes }}
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2 mt-2.5">
              <button v-if="nextStatus[app.status]"
                @click="advanceStatus(app)"
                class="text-xs px-2 py-1 bg-blue-500/10 hover:bg-blue-500/20 border border-blue-500/20 text-blue-300 rounded-lg transition-colors"
              >→ {{ statusConfig[nextStatus[app.status]]?.label }}</button>
              <button v-if="!['rejected','withdrawn','accepted'].includes(app.status)"
                @click="rejectApplication(app)"
                class="text-xs px-2 py-1 text-red-400/60 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
              >Ablehnen</button>
              <a v-if="app.linkedin_url" :href="app.linkedin_url" target="_blank"
                class="text-xs text-blue-400/60 hover:text-blue-300 ml-auto">LinkedIn</a>
              <a v-if="app.cv_url" :href="app.cv_url" target="_blank"
                class="text-xs text-white/40 hover:text-white">CV</a>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
