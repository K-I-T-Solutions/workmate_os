<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useCustomers } from '../../composables/useCustomers';
import type { CustomerFilters } from '../../composables/useCustomers';
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Filter,
  Users,
  Mail,
  Phone,
  MapPin,
  Trash2,
  Eye,
  X,
  Kanban,
  Upload,
  FileUp,
  CheckCircle,
  AlertCircle,
} from 'lucide-vue-next';
import { crmService } from '../../services/crm.service';
import type { CsvImportResult } from '../../types/customer';

// Props & Emits
const emit = defineEmits<{
  openCustomer: [id: string];
  openDashboard: [];
  openPipeline: [];
}>();

// Composables
const {
  customers,
  total,
  page: currentPage,
  pages,
  limit,
  loading,
  error,
  isEmpty,
  loadCustomers,
  deleteCustomer,
} = useCustomers();

// ─── FILTER STATE ─────────────────────────────────────────
const searchQuery = ref('');
const selectedStatus = ref<string>('');

// ─── LIFECYCLE ────────────────────────────────────────────
onMounted(() => {
  applyFilters();
});

// ─── COMPUTED ─────────────────────────────────────────────
const hasFilters = computed(() => {
  return !!(selectedStatus.value || searchQuery.value);
});

// ─── ACTIONS ──────────────────────────────────────────────
async function applyFilters() {
  const filters: CustomerFilters = {
    skip: (currentPage.value - 1) * limit.value,
    limit: limit.value,
  };

  if (selectedStatus.value) {
    filters.status = selectedStatus.value;
  }

  if (searchQuery.value) {
    filters.search = searchQuery.value;
  }

  await loadCustomers(filters);
}

function clearFilters() {
  selectedStatus.value = '';
  searchQuery.value = '';
  applyFilters();
}

function goToPage(pageNum: number) {
  if (pageNum >= 1 && pageNum <= pages.value) {
    applyFilters();
  }
}

// Delete confirmation
const deleteConfirmId = ref<string | null>(null);

function showDeleteConfirm(customerId: string) {
  deleteConfirmId.value = customerId;
}

async function confirmDelete() {
  if (deleteConfirmId.value) {
    const success = await deleteCustomer(deleteConfirmId.value);
    if (success) {
      deleteConfirmId.value = null;
      applyFilters();
    }
  }
}

// ─── CSV IMPORT ───────────────────────────────────────────
const showImportModal = ref(false);
const importStep = ref<'upload' | 'preview' | 'done'>('upload');
const importFile = ref<File | null>(null);
const importLoading = ref(false);
const importError = ref<string | null>(null);
const importPreview = ref<CsvImportResult | null>(null);
const importResult = ref<CsvImportResult | null>(null);

function openImportModal() {
  showImportModal.value = true;
  importStep.value = 'upload';
  importFile.value = null;
  importError.value = null;
  importPreview.value = null;
  importResult.value = null;
}

function closeImportModal() {
  showImportModal.value = false;
}

function onImportFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files?.[0]) {
    importFile.value = input.files[0];
    importError.value = null;
  }
}

function onImportFileDrop(event: DragEvent) {
  event.preventDefault();
  const file = event.dataTransfer?.files?.[0];
  if (file && file.name.endsWith('.csv')) {
    importFile.value = file;
    importError.value = null;
  }
}

async function runDryRun() {
  if (!importFile.value) return;
  importLoading.value = true;
  importError.value = null;
  try {
    importPreview.value = await crmService.importCsvDryRun(importFile.value);
    importStep.value = 'preview';
  } catch (e: any) {
    importError.value = e.response?.data?.detail || 'Fehler beim Analysieren der Datei.';
  } finally {
    importLoading.value = false;
  }
}

async function runImport() {
  if (!importFile.value) return;
  importLoading.value = true;
  importError.value = null;
  try {
    importResult.value = await crmService.importCsv(importFile.value, true);
    importStep.value = 'done';
    // Kundenliste neu laden
    await applyFilters();
  } catch (e: any) {
    importError.value = e.response?.data?.detail || 'Fehler beim Import.';
  } finally {
    importLoading.value = false;
  }
}

// ─── HELPERS ──────────────────────────────────────────────
function getStatusBadge(status: string) {
  const badges = {
    active: 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200',
    inactive: 'bg-white/5 border-white/10 text-white/60',
    lead: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    blocked: 'bg-red-500/20 border-red-400/30 text-red-200',
  };
  return badges[status as keyof typeof badges] || badges.inactive;
}

function getStatusLabel(status: string): string {
  const labels = {
    active: 'Aktiv',
    inactive: 'Inaktiv',
    lead: 'Lead',
    blocked: 'Blockiert',
  };
  return labels[status as keyof typeof labels] || 'Inaktiv';
}

function getTypeBadge(type: string | null) {
  const badges = {
    creator: 'bg-purple-500/20 border-purple-400/30 text-purple-200',
    individual: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    business: 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200',
    government: 'bg-orange-500/20 border-orange-400/30 text-orange-200',
  };
  return type ? (badges[type as keyof typeof badges] || badges.business) : badges.business;
}

function getTypeLabel(type: string | null): string {
  const labels = {
    creator: 'Creator',
    individual: 'Privatperson',
    business: 'Unternehmen',
    government: 'Behörde',
  };
  return type ? (labels[type as keyof typeof labels] || 'Unternehmen') : 'Unternehmen';
}
</script>

<template>
  <div class="h-full flex flex-col gap-3 sm:gap-4 p-3 sm:p-4">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
      <div class="flex items-center gap-3">
        <button @click="emit('openDashboard')" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <div>
          <h1 class="text-2xl font-bold text-white">Kunden</h1>
          <p class="text-sm text-white/60 mt-1">{{ total }} Kunden insgesamt</p>
        </div>
      </div>
      <div class="flex gap-2 w-full sm:w-auto flex-wrap">
        <button @click="emit('openPipeline')" class="kit-btn-ghost">
          <Kanban :size="18" />
          Pipeline
        </button>
        <button @click="openImportModal" class="kit-btn-ghost">
          <Upload :size="18" />
          Importieren
        </button>
        <button @click="$emit('openCustomer', 'create')" class="kit-btn-primary">
          <Plus :size="18" />
          Neuer Kunde
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="rounded-lg border border-white/10 bg-white/5 p-4">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <!-- Status Filter -->
        <div>
          <label class="kit-label flex items-center gap-1">
            <Filter :size="14" />
            Status
          </label>
          <select
            v-model="selectedStatus"
            @change="applyFilters"
            class="kit-input"
          >
            <option value="">Alle Status</option>
            <option value="active">Aktiv</option>
            <option value="inactive">Inaktiv</option>
            <option value="lead">Lead</option>
            <option value="blocked">Blockiert</option>
          </select>
        </div>

        <!-- Search -->
        <div class="sm:col-span-2">
          <label class="kit-label">Suche</label>
          <input
            v-model="searchQuery"
            @input="applyFilters"
            type="text"
            placeholder="Name, E-Mail oder Kundennummer..."
            class="kit-input"
          />
        </div>
      </div>

      <!-- Clear Filters -->
      <button
        v-if="hasFilters"
        @click="clearFilters"
        class="kit-btn-ghost mt-3 text-sm"
      >
        <X :size="16" />
        Filter zurücksetzen
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Kunden...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1">
      <div class="rounded-lg border border-red-400/30 bg-red-500/20 p-4">
        <p class="text-red-200">{{ error }}</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <Users :size="64" class="mx-auto text-white/20 mb-4" />
        <h3 class="text-xl font-semibold text-white mb-2">Keine Kunden gefunden</h3>
        <p class="text-white/60 mb-6">
          {{ hasFilters ? 'Keine Kunden entsprechen den Filterkriterien' : 'Erstellen Sie Ihren ersten Kunden' }}
        </p>
        <button v-if="!hasFilters" @click="$emit('openCustomer', 'create')" class="kit-btn-primary">
          <Plus :size="18" />
          Ersten Kunden erstellen
        </button>
      </div>
    </div>

    <!-- Customer List -->
    <div v-else class="flex-1 overflow-auto">
      <div class="space-y-3">
        <div
          v-for="customer in customers"
          :key="customer.id"
          class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition cursor-pointer"
          @click="emit('openCustomer', customer.id)"
        >
          <div class="flex items-start justify-between gap-4">
            <!-- Left: Customer Info -->
            <div class="flex-1 min-w-0">
              <!-- Name + Status Badge -->
              <div class="flex items-center flex-wrap gap-2 sm:gap-3 mb-3">
                <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
                  <Users :size="18" class="text-blue-200" />
                </div>
                <span class="font-semibold text-lg text-white truncate">
                  {{ customer.name }}
                </span>
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium border',
                    getStatusBadge(customer.status),
                  ]"
                >
                  {{ getStatusLabel(customer.status) }}
                </span>
                <span
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium border',
                    getTypeBadge(customer.type),
                  ]"
                >
                  {{ getTypeLabel(customer.type) }}
                </span>
              </div>

              <!-- 3-column info grid -->
              <div class="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-3 text-sm">
                <div v-if="customer.email">
                  <div class="text-white/50 text-xs flex items-center gap-1">
                    <Mail :size="12" />
                    E-Mail
                  </div>
                  <div class="font-medium text-white truncate">{{ customer.email }}</div>
                </div>

                <div v-if="customer.phone">
                  <div class="text-white/50 text-xs flex items-center gap-1">
                    <Phone :size="12" />
                    Telefon
                  </div>
                  <div class="font-medium text-white">{{ customer.phone }}</div>
                </div>

                <div v-if="customer.city">
                  <div class="text-white/50 text-xs flex items-center gap-1">
                    <MapPin :size="12" />
                    Stadt
                  </div>
                  <div class="font-medium text-white">{{ customer.city }}</div>
                </div>

                <div v-if="customer.customer_number">
                  <div class="text-white/50 text-xs">Kundennummer</div>
                  <div class="font-medium text-white font-mono text-xs">
                    {{ customer.customer_number }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Right: Actions -->
            <div class="flex items-start gap-1 sm:gap-2">
              <button
                @click.stop="emit('openCustomer', customer.id)"
                class="p-2 min-w-[44px] min-h-[44px] flex items-center justify-center hover:bg-blue-500/20 rounded-lg transition"
                title="Details anzeigen"
              >
                <Eye :size="18" class="text-blue-200" />
              </button>
              <button
                @click.stop="showDeleteConfirm(customer.id)"
                class="p-2 min-w-[44px] min-h-[44px] flex items-center justify-center hover:bg-red-500/20 rounded-lg transition"
                title="Kunde löschen"
              >
                <Trash2 :size="18" class="text-red-200" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div
      v-if="!loading && !isEmpty"
      class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0 text-sm text-white/60"
    >
      <div>
        Seite {{ currentPage }} von {{ pages }} ({{ total }} Kunden)
      </div>

      <div class="flex gap-2 w-full sm:w-auto">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          :class="[
            'flex-1 sm:flex-none px-3 py-2 rounded-lg transition flex items-center justify-center gap-1',
            currentPage === 1
              ? 'opacity-30 cursor-not-allowed text-white/40'
              : 'kit-btn-ghost',
          ]"
        >
          <ChevronLeft :size="16" />
          Zurück
        </button>
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === pages"
          :class="[
            'flex-1 sm:flex-none px-3 py-2 rounded-lg transition flex items-center justify-center gap-1',
            currentPage === pages
              ? 'opacity-30 cursor-not-allowed text-white/40'
              : 'kit-btn-ghost',
          ]"
        >
          Weiter
          <ChevronRight :size="16" />
        </button>
      </div>
    </div>

    <!-- CSV Import Modal -->
    <div
      v-if="showImportModal"
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-50"
      @click.self="closeImportModal"
    >
      <div class="rounded-xl border border-white/10 bg-stone-900 p-6 w-full max-w-lg mx-4">
        <!-- Modal Header -->
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-lg font-bold text-white flex items-center gap-2">
            <FileUp :size="20" class="text-blue-300" />
            Kunden importieren
          </h3>
          <button @click="closeImportModal" class="kit-btn-ghost p-1">
            <X :size="18" />
          </button>
        </div>

        <!-- Step 1: Upload -->
        <div v-if="importStep === 'upload'">
          <p class="text-sm text-white/60 mb-4">
            CSV-Datei mit Kundendaten hochladen. Pflichtfeld: <code class="text-blue-300">name</code>.<br />
            Optionale Felder: email, phone, city, zip_code, street, country, type, status, notes.
          </p>

          <!-- Dropzone -->
          <div
            class="rounded-lg border-2 border-dashed border-white/20 p-8 text-center hover:border-blue-400/50 transition cursor-pointer"
            @dragover.prevent
            @drop="onImportFileDrop"
            @click="($refs.csvFileInput as HTMLInputElement)?.click()"
          >
            <Upload :size="32" class="mx-auto text-white/30 mb-3" />
            <p class="text-white/60 text-sm">
              <span class="text-blue-300 font-medium">Datei auswählen</span> oder hierhin ziehen
            </p>
            <p class="text-white/30 text-xs mt-1">CSV (Semikolon oder Komma getrennt)</p>
            <input
              ref="csvFileInput"
              type="file"
              accept=".csv"
              class="hidden"
              @change="onImportFileChange"
            />
          </div>

          <div v-if="importFile" class="mt-3 p-3 rounded-lg bg-white/5 border border-white/10 flex items-center gap-3">
            <FileUp :size="16" class="text-blue-300 shrink-0" />
            <span class="text-sm text-white truncate">{{ importFile.name }}</span>
          </div>

          <div v-if="importError" class="mt-3 p-3 rounded-lg bg-red-500/20 border border-red-400/30 text-red-200 text-sm">
            {{ importError }}
          </div>

          <div class="mt-5 flex gap-3 justify-end">
            <button @click="closeImportModal" class="kit-btn-ghost">Abbrechen</button>
            <button
              @click="runDryRun"
              :disabled="!importFile || importLoading"
              class="kit-btn-primary"
              :class="(!importFile || importLoading) ? 'opacity-50 cursor-not-allowed' : ''"
            >
              <div v-if="importLoading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Vorschau anzeigen
            </button>
          </div>
        </div>

        <!-- Step 2: Preview -->
        <div v-else-if="importStep === 'preview' && importPreview">
          <div class="mb-4 grid grid-cols-2 gap-3">
            <div class="p-3 rounded-lg bg-emerald-500/10 border border-emerald-400/30">
              <div class="text-2xl font-bold text-emerald-300">{{ importPreview.imported }}</div>
              <div class="text-xs text-white/60">Werden importiert</div>
            </div>
            <div class="p-3 rounded-lg bg-white/5 border border-white/10">
              <div class="text-2xl font-bold text-white/60">{{ importPreview.skipped }}</div>
              <div class="text-xs text-white/60">Duplikate (übersprungen)</div>
            </div>
          </div>

          <!-- Fehler -->
          <div v-if="importPreview.errors.length > 0" class="mb-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-400/30">
            <p class="text-xs font-semibold text-yellow-300 mb-1 flex items-center gap-1">
              <AlertCircle :size="12" /> Hinweise
            </p>
            <ul class="text-xs text-yellow-200 space-y-0.5">
              <li v-for="err in importPreview.errors.slice(0, 5)" :key="err">{{ err }}</li>
              <li v-if="importPreview.errors.length > 5" class="text-yellow-400/60">
                + {{ importPreview.errors.length - 5 }} weitere...
              </li>
            </ul>
          </div>

          <!-- Preview-Tabelle -->
          <div v-if="importPreview.preview && importPreview.preview.length > 0" class="overflow-x-auto rounded-lg border border-white/10 mb-4">
            <table class="w-full text-xs">
              <thead>
                <tr class="bg-white/5 border-b border-white/10">
                  <th class="text-left p-2 text-white/60">Name</th>
                  <th class="text-left p-2 text-white/60">E-Mail</th>
                  <th class="text-left p-2 text-white/60">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, i) in importPreview.preview.slice(0, 5)"
                  :key="i"
                  class="border-b border-white/5 last:border-0"
                >
                  <td class="p-2 text-white truncate max-w-[120px]">{{ row.name }}</td>
                  <td class="p-2 text-white/60 truncate max-w-[140px]">{{ row.email || '–' }}</td>
                  <td class="p-2 text-white/60">{{ row.status || 'lead' }}</td>
                </tr>
              </tbody>
            </table>
            <p v-if="(importPreview.preview?.length ?? 0) > 5" class="text-xs text-white/30 p-2 text-center">
              + {{ (importPreview.preview?.length ?? 0) - 5 }} weitere Einträge
            </p>
          </div>

          <div v-if="importError" class="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-400/30 text-red-200 text-sm">
            {{ importError }}
          </div>

          <div class="flex gap-3 justify-end">
            <button @click="importStep = 'upload'" class="kit-btn-ghost">Zurück</button>
            <button
              @click="runImport"
              :disabled="importLoading || importPreview.imported === 0"
              class="kit-btn-primary"
              :class="(importLoading || importPreview.imported === 0) ? 'opacity-50 cursor-not-allowed' : ''"
            >
              <div v-if="importLoading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              {{ importPreview.imported }} Kunden importieren
            </button>
          </div>
        </div>

        <!-- Step 3: Done -->
        <div v-else-if="importStep === 'done' && importResult">
          <div class="text-center py-4">
            <CheckCircle :size="48" class="mx-auto text-emerald-400 mb-4" />
            <h4 class="text-xl font-bold text-white mb-2">Import abgeschlossen</h4>
            <p class="text-white/60 text-sm">
              <span class="text-emerald-300 font-semibold">{{ importResult.imported }}</span> Kunden importiert,
              <span class="text-white/40">{{ importResult.skipped }}</span> übersprungen.
            </p>
            <ul v-if="importResult.errors.length > 0" class="mt-3 text-xs text-yellow-200 text-left space-y-0.5">
              <li v-for="err in importResult.errors.slice(0, 5)" :key="err">{{ err }}</li>
            </ul>
          </div>
          <div class="flex justify-end mt-4">
            <button @click="closeImportModal" class="kit-btn-primary">Fertig</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="deleteConfirmId"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click="deleteConfirmId = null"
    >
      <div
        class="rounded-lg border border-white/10 bg-stone-900 p-6 max-w-md"
        @click.stop
      >
        <h3 class="text-xl font-bold text-white mb-2">Kunde löschen?</h3>
        <p class="text-white/60 mb-6">
          Möchten Sie diesen Kunden wirklich löschen? Diese Aktion kann nicht
          rückgängig gemacht werden.
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="deleteConfirmId = null" class="kit-btn-ghost">
            Abbrechen
          </button>
          <button @click="confirmDelete" class="kit-btn-danger">
            <Trash2 :size="18" />
            Löschen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Mobile Optimizations */
@media (max-width: 640px) {
  .rounded-lg.border.bg-white\/5 {
    padding: 0.75rem;
  }

  .flex.items-center.gap-3.mb-3 {
    align-items: flex-start;
  }
}

@media (max-width: 1024px) {
  .p-2.hover\:bg-blue-500\/20,
  .p-2.hover\:bg-red-500\/20 {
    min-width: 44px;
    min-height: 44px;
  }
}
</style>
