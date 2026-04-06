<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Plus, X, Briefcase, Users, MapPin, Calendar, ChevronRight, Globe } from 'lucide-vue-next';
import { apiClient } from '@/services/api/client';

const router = useRouter();

const loading = ref(true);
const error = ref<string | null>(null);
const jobs = ref<any[]>([]);
const showCreateForm = ref(false);
const submitting = ref(false);
const departments = ref<any[]>([]);

const statusConfig: Record<string, { label: string; class: string }> = {
  draft:     { label: 'Entwurf',        class: 'badge badge-gray' },
  published: { label: 'Veröffentlicht', class: 'badge badge-green' },
  closed:    { label: 'Geschlossen',    class: 'badge badge-red' },
  archived:  { label: 'Archiviert',     class: 'badge badge-gray' },
};

const employmentLabels: Record<string, string> = {
  full_time: 'Vollzeit', part_time: 'Teilzeit', contract: 'Vertrag',
  intern: 'Praktikum', freelance: 'Freelance',
  fulltime: 'Vollzeit', parttime: 'Teilzeit',
};

const filterStatus = ref('');
const filteredJobs = computed(() =>
  filterStatus.value ? jobs.value.filter(j => j.status === filterStatus.value) : jobs.value
);

const newJob = ref({
  title: '', description: '', requirements: '', location: '',
  remote: false, employment_type: 'full_time', salary_min: null as number | null,
  salary_max: null as number | null, department_id: '', deadline: '', status: 'draft',
});

onMounted(async () => {
  await Promise.all([loadJobs(), loadDepartments()]);
});

async function loadJobs() {
  loading.value = true;
  error.value = null;
  try {
    const { data } = await apiClient.get('/api/hr/recruiting/jobs', { params: { limit: 100 } });
    jobs.value = data.items || data;
  } catch (e) {
    error.value = 'Daten konnten nicht geladen werden.';
  } finally {
    loading.value = false;
  }
}

async function loadDepartments() {
  try {
    const { data } = await apiClient.get('/api/departments');
    departments.value = data.items || data;
  } catch { /* ignore */ }
}

async function createJob() {
  submitting.value = true;
  try {
    const payload = { ...newJob.value };
    if (!payload.department_id) delete (payload as any).department_id;
    if (!payload.deadline) delete (payload as any).deadline;
    await apiClient.post('/api/hr/recruiting/jobs', payload);
    showCreateForm.value = false;
    resetForm();
    await loadJobs();
  } finally {
    submitting.value = false;
  }
}

async function updateStatus(job: any, status: string) {
  await apiClient.put(`/api/hr/recruiting/jobs/${job.id}`, { status });
  await loadJobs();
}

async function deleteJob(id: string) {
  if (!confirm('Stelle wirklich löschen?')) return;
  await apiClient.delete(`/api/hr/recruiting/jobs/${id}`);
  await loadJobs();
}

function resetForm() {
  newJob.value = { title: '', description: '', requirements: '', location: '', remote: false,
    employment_type: 'full_time', salary_min: null, salary_max: null, department_id: '', deadline: '', status: 'draft' };
}

function formatDate(d?: string) {
  if (!d) return null;
  return new Date(d).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}
</script>

<template>
  <div class="space-y-4">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-white">Recruiting</h1>
        <p class="text-sm text-white/50 mt-0.5">Stellenausschreibungen & Bewerbungen</p>
      </div>
      <button @click="showCreateForm = true" class="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-500/20 hover:bg-blue-500/30 border border-blue-400/30 text-blue-300 rounded-lg transition-colors">
        <Plus :size="15" />Neue Stelle
      </button>
    </div>

    <!-- Filter -->
    <div class="flex gap-2">
      <button v-for="s in ['', 'published', 'draft', 'closed', 'archived']" :key="s"
        @click="filterStatus = s"
        :class="['px-3 py-1 text-xs rounded-lg transition-colors border',
          filterStatus === s ? 'bg-blue-500/20 border-blue-400/30 text-blue-300' : 'bg-white/5 border-white/10 text-white/50 hover:text-white']"
      >
        {{ s === '' ? 'Alle' : statusConfig[s]?.label }}
      </button>
    </div>

    <!-- Create Form -->
    <div v-if="showCreateForm" class="kit-card p-5 space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="font-semibold text-white">Neue Stellenausschreibung</h3>
        <button @click="showCreateForm = false; resetForm()" class="text-white/40 hover:text-white">
          <X :size="18" />
        </button>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div class="sm:col-span-2">
          <label class="text-xs text-white/60 mb-1 block">Stellentitel *</label>
          <input v-model="newJob.title" type="text" placeholder="z.B. Senior Frontend Developer" class="kit-input w-full" />
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">Beschäftigungsart</label>
          <select v-model="newJob.employment_type" class="kit-input w-full">
            <option value="full_time">Vollzeit</option>
            <option value="part_time">Teilzeit</option>
            <option value="contract">Vertrag</option>
            <option value="intern">Praktikum</option>
            <option value="freelance">Freelance</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">Abteilung</label>
          <select v-model="newJob.department_id" class="kit-input w-full">
            <option value="">Keine Abteilung</option>
            <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">Standort</label>
          <input v-model="newJob.location" type="text" placeholder="z.B. Koblenz" class="kit-input w-full" />
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">Bewerbungsfrist</label>
          <input v-model="newJob.deadline" type="date" class="kit-input w-full" />
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">Gehalt von (€)</label>
          <input v-model.number="newJob.salary_min" type="number" placeholder="z.B. 40000" class="kit-input w-full" />
        </div>
        <div>
          <label class="text-xs text-white/60 mb-1 block">Gehalt bis (€)</label>
          <input v-model.number="newJob.salary_max" type="number" placeholder="z.B. 60000" class="kit-input w-full" />
        </div>
        <div class="sm:col-span-2">
          <label class="text-xs text-white/60 mb-1 block">Beschreibung</label>
          <textarea v-model="newJob.description" rows="3" class="kit-input w-full resize-none" placeholder="Aufgaben, Anforderungen..." />
        </div>
        <div class="sm:col-span-2 flex items-center gap-4">
          <label class="flex items-center gap-2 text-sm text-white/70 cursor-pointer">
            <input v-model="newJob.remote" type="checkbox" class="rounded" />Remote möglich
          </label>
          <select v-model="newJob.status" class="kit-input">
            <option value="draft">Als Entwurf speichern</option>
            <option value="published">Direkt veröffentlichen</option>
          </select>
        </div>
      </div>
      <div class="flex justify-end gap-2">
        <button @click="showCreateForm = false; resetForm()" class="px-4 py-2 text-sm text-white/60 hover:text-white transition-colors">Abbrechen</button>
        <button @click="createJob" :disabled="submitting || !newJob.title"
          class="px-4 py-2 text-sm bg-blue-500/30 hover:bg-blue-500/40 border border-blue-400/30 text-blue-300 rounded-lg transition-colors disabled:opacity-50">
          {{ submitting ? 'Wird erstellt...' : 'Stelle anlegen' }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-8 h-8 border-2 border-blue-400/30 border-t-blue-400 rounded-full animate-spin" />
    </div>

    <!-- Error State -->
    <div v-if="error && !loading" class="kit-card p-6 text-center">
      <p class="text-red-400 text-sm">{{ error }}</p>
      <button class="kit-btn-secondary mt-3 text-xs" @click="loadJobs()">Erneut versuchen</button>
    </div>

    <!-- Empty -->
    <div v-else-if="filteredJobs.length === 0" class="text-center py-14 text-white/40">
      <Briefcase :size="36" class="mx-auto mb-3 opacity-40" />
      <p>Keine Stellenausschreibungen vorhanden</p>
    </div>

    <!-- Jobs List -->
    <div v-else class="space-y-3">
      <div v-for="job in filteredJobs" :key="job.id"
        class="kit-card p-4 hover:bg-white/10 transition-colors"
      >
        <div class="flex items-start gap-3">
          <div class="p-2 bg-blue-500/15 border border-blue-400/20 rounded-lg flex-shrink-0">
            <Briefcase :size="16" class="text-blue-300" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2">
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-medium text-white">{{ job.title }}</span>
                  <span :class="statusConfig[job.status]?.class">
                    {{ statusConfig[job.status]?.label }}
                  </span>
                </div>
                <div class="flex items-center gap-3 text-xs text-white/40 mt-1 flex-wrap">
                  <span v-if="employmentLabels[job.employment_type]">{{ employmentLabels[job.employment_type] }}</span>
                  <span v-if="job.location" class="flex items-center gap-1"><MapPin :size="11" />{{ job.location }}</span>
                  <span v-if="job.remote" class="flex items-center gap-1"><Globe :size="11" />Remote</span>
                  <span v-if="job.deadline" class="flex items-center gap-1"><Calendar :size="11" />Frist: {{ formatDate(job.deadline) }}</span>
                  <span v-if="job.salary_min || job.salary_max" class="text-white/50">
                    {{ job.salary_min ? `${job.salary_min.toLocaleString('de-DE')} €` : '' }}
                    {{ job.salary_min && job.salary_max ? '–' : '' }}
                    {{ job.salary_max ? `${job.salary_max.toLocaleString('de-DE')} €` : '' }}
                  </span>
                </div>
              </div>
              <!-- Bewerbungen Badge -->
              <button
                @click="router.push(`/app/hr/recruiting/jobs/${job.id}`)"
                class="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-colors flex-shrink-0"
              >
                <Users :size="13" class="text-white/50" />
                <span class="text-xs text-white/60">{{ job.application_count ?? 0 }}</span>
                <ChevronRight :size="13" class="text-white/30" />
              </button>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2 mt-3 flex-wrap">
              <button v-if="job.status === 'draft'" @click="updateStatus(job, 'published')"
                class="text-xs px-2 py-1 bg-green-500/10 hover:bg-green-500/20 border border-green-500/20 text-green-300 rounded-lg transition-colors">
                Veröffentlichen
              </button>
              <button v-if="job.status === 'published'" @click="updateStatus(job, 'closed')"
                class="text-xs px-2 py-1 bg-orange-500/10 hover:bg-orange-500/20 border border-orange-500/20 text-orange-300 rounded-lg transition-colors">
                Schließen
              </button>
              <button v-if="job.status === 'closed'" @click="updateStatus(job, 'archived')"
                class="text-xs px-2 py-1 bg-white/5 hover:bg-white/10 border border-white/10 text-white/50 rounded-lg transition-colors">
                Archivieren
              </button>
              <button @click="deleteJob(job.id)"
                class="text-xs px-2 py-1 text-red-400/70 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors ml-auto">
                Löschen
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
