<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useCustomers } from '../../composables/useCustomers';
import { useContacts } from '../../composables/useContacts';
import { useCrmActivity } from '../../composables/useCrmActivity';
import { apiClient } from '@/services/api/client';
import { navigateToInvoice, createInvoiceForCustomer } from '@/services/navigation/crossAppNavigation';
import {
  ChevronLeft,
  Edit,
  Trash2,
  Plus,
  Mail,
  Phone,
  MapPin,
  Users,
  Briefcase,
  Euro,
  User,
  CheckCircle,
  Phone as PhoneIcon,
  Mail as MailIcon,
  MonitorPlay,
  FileText,
  FolderOpen,
  Receipt,
} from 'lucide-vue-next';

// Props
const props = defineProps<{
  customerId: string;
}>();

// Emits
const emit = defineEmits<{
  back: [];
  openContacts: [];
  openContact: [contactId: string];
  edit: [customerId: string];
}>();

// Composables
const { currentCustomer, loading: customerLoading, loadCustomer, deleteCustomer } = useCustomers();
const { contacts, loading: contactsLoading, loadContacts, setPrimaryContact } = useContacts();
const { activities, loading: activitiesLoading, fetchCustomerActivities } = useCrmActivity();

// State
const showDeleteConfirm = ref(false);
const projects = ref<any[]>([]);
const invoices = ref<any[]>([]);
const projectsLoading = ref(false);
const invoicesLoading = ref(false);

// Lifecycle
onMounted(async () => {
  await loadCustomer(props.customerId);
  await loadContacts({ customerId: props.customerId });
  await fetchCustomerActivities(props.customerId, { limit: 10 });
  await loadProjects();
  await loadInvoices();
});

// Computed
const customer = computed(() => currentCustomer.value);
const primaryContact = computed(() => contacts.value.find((c) => c.is_primary) || null);

const totalRevenue = computed(() => {
  return invoices.value
    .filter((inv: any) => inv.status === 'paid')
    .reduce((sum: number, inv: any) => sum + (inv.total || 0), 0);
});

// Data Loading Functions
async function loadProjects() {
  projectsLoading.value = true;
  try {
    const response = await apiClient.get('/api/backoffice/projects', {
      params: { customer_id: props.customerId }
    });
    projects.value = response.data || [];
  } catch (error) {
    console.error('Error loading projects:', error);
    projects.value = [];
  } finally {
    projectsLoading.value = false;
  }
}

async function loadInvoices() {
  invoicesLoading.value = true;
  try {
    const response = await apiClient.get('/api/backoffice/invoices', {
      params: { customer_id: props.customerId, limit: 100 }
    });
    invoices.value = response.data.items || [];
  } catch (error) {
    console.error('Error loading invoices:', error);
    invoices.value = [];
  } finally {
    invoicesLoading.value = false;
  }
}

// Actions
async function handleDelete() {
  if (!customer.value) return;

  const success = await deleteCustomer(customer.value.id);
  if (success) {
    emit('back');
  }
}

async function handleSetPrimary(contactId: string) {
  if (!customer.value) return;
  await setPrimaryContact(customer.value.id, contactId);
}

// Helpers
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

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Gerade eben';
  if (diffMins < 60) return `vor ${diffMins} Min`;
  if (diffHours < 24) return `vor ${diffHours} Std`;
  if (diffDays < 7) return `vor ${diffDays} Tagen`;

  return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function getActivityIcon(type: string) {
  const icons: Record<string, any> = {
    call: PhoneIcon,
    email: MailIcon,
    onsite: MapPin,
    remote: MonitorPlay,
    note: FileText,
  };
  return icons[type] || FileText;
}

function getActivityLabel(type: string): string {
  const labels: Record<string, string> = {
    call: 'Anruf',
    email: 'E-Mail',
    onsite: 'Vor-Ort-Besuch',
    remote: 'Remote-Meeting',
    note: 'Notiz',
  };
  return labels[type] || type;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value);
}

function getProjectStatusBadge(status: string) {
  const badges: Record<string, string> = {
    planning: 'bg-yellow-500/20 border-yellow-400/30 text-yellow-200',
    active: 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200',
    on_hold: 'bg-orange-500/20 border-orange-400/30 text-orange-200',
    completed: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    cancelled: 'bg-red-500/20 border-red-400/30 text-red-200',
  };
  return badges[status] || 'bg-white/5 border-white/10 text-white/60';
}

function getProjectStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    planning: 'Planung',
    active: 'Aktiv',
    on_hold: 'Pausiert',
    completed: 'Abgeschlossen',
    cancelled: 'Abgebrochen',
  };
  return labels[status] || status;
}

function getInvoiceStatusBadge(status: string) {
  const badges: Record<string, string> = {
    draft: 'bg-white/5 border-white/10 text-white/60',
    sent: 'bg-blue-500/20 border-blue-400/30 text-blue-200',
    paid: 'bg-emerald-500/20 border-emerald-400/30 text-emerald-200',
    partial: 'bg-yellow-500/20 border-yellow-400/30 text-yellow-200',
    overdue: 'bg-red-500/20 border-red-400/30 text-red-200',
    cancelled: 'bg-red-500/20 border-red-400/30 text-red-200',
  };
  return badges[status] || 'bg-white/5 border-white/10 text-white/60';
}

function getInvoiceStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    draft: 'Entwurf',
    sent: 'Versendet',
    paid: 'Bezahlt',
    partial: 'Teilweise bezahlt',
    overdue: 'Überfällig',
    cancelled: 'Storniert',
  };
  return labels[status] || status;
}

// Cross-App Navigation
function handleInvoiceClick(invoiceId: string) {
  navigateToInvoice(invoiceId);
}

function handleCreateInvoice() {
  if (customer.value) {
    createInvoiceForCustomer(customer.value.id);
  }
}
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="emit('back')" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <div v-if="customer">
          <h1 class="text-2xl font-bold text-white flex items-center gap-3">
            {{ customer.name }}
            <span
              :class="[
                'px-2 py-1 rounded text-sm font-medium border',
                getStatusBadge(customer.status),
              ]"
            >
              {{ getStatusLabel(customer.status) }}
            </span>
            <span
              :class="[
                'px-2 py-1 rounded text-sm font-medium border',
                getTypeBadge(customer.type),
              ]"
            >
              {{ getTypeLabel(customer.type) }}
            </span>
          </h1>
          <p class="text-sm text-white/60 mt-1">
            Kunde seit {{ new Date(customer.created_at).toLocaleDateString('de-DE') }}
          </p>
        </div>
      </div>

      <div v-if="customer" class="flex gap-2">
        <button @click="$emit('openContacts')" class="kit-btn-ghost" title="Kontakte verwalten">
          <Users :size="18" />
          Kontakte
        </button>
        <button @click="emit('edit', customer.id)" class="kit-btn-secondary">
          <Edit :size="18" />
          Bearbeiten
        </button>
        <button @click="showDeleteConfirm = true" class="kit-btn-danger">
          <Trash2 :size="18" />
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="customerLoading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Kundendaten...</p>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="customer" class="flex-1 overflow-auto space-y-4">
      <!-- Main Info Grid (3 Spalten) -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Kontaktdaten -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 text-white/60 mb-3">
            <Mail :size="16" />
            <h3 class="text-sm font-medium">Kontaktdaten</h3>
          </div>
          <div class="space-y-2 text-sm">
            <div v-if="customer.email">
              <div class="text-white/50 text-xs">E-Mail</div>
              <a
                :href="`mailto:${customer.email}`"
                class="text-blue-200 hover:text-blue-100 transition"
              >
                {{ customer.email }}
              </a>
            </div>
            <div v-if="customer.phone">
              <div class="text-white/50 text-xs">Telefon</div>
              <a
                :href="`tel:${customer.phone}`"
                class="text-blue-200 hover:text-blue-100 transition"
              >
                {{ customer.phone }}
              </a>
            </div>
            <div v-if="customer.customer_number">
              <div class="text-white/50 text-xs">Kundennummer</div>
              <div class="text-white font-mono">{{ customer.customer_number }}</div>
            </div>
          </div>
        </div>

        <!-- Adresse -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 text-white/60 mb-3">
            <MapPin :size="16" />
            <h3 class="text-sm font-medium">Adresse</h3>
          </div>
          <div class="text-sm text-white">
            <div v-if="customer.address">{{ customer.address }}</div>
            <div v-if="customer.zip || customer.city">
              {{ customer.zip }} {{ customer.city }}
            </div>
            <div v-if="customer.country">{{ customer.country }}</div>
            <div v-if="!customer.address && !customer.city" class="text-white/40">
              Keine Adresse hinterlegt
            </div>
          </div>
        </div>

        <!-- Statistiken -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 text-white/60 mb-3">
            <Briefcase :size="16" />
            <h3 class="text-sm font-medium">Übersicht</h3>
          </div>
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-white/60">Kontakte:</span>
              <span class="text-white font-medium">{{ contacts.length }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-white/60">Projekte:</span>
              <span v-if="projectsLoading" class="text-white/40">...</span>
              <span v-else class="text-white font-medium">{{ projects.length }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-white/60">Rechnungen:</span>
              <span v-if="invoicesLoading" class="text-white/40">...</span>
              <span v-else class="text-white font-medium">{{ invoices.length }}</span>
            </div>
            <div class="flex justify-between text-sm pt-2 border-t border-white/10">
              <span class="text-white/60">Umsatz:</span>
              <span v-if="invoicesLoading" class="text-white/40">...</span>
              <span v-else class="text-white font-bold">{{ formatCurrency(totalRevenue) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Notizen -->
      <div v-if="customer.notes" class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-sm font-medium text-white/60 mb-2">Notizen</h3>
        <p class="text-white text-sm whitespace-pre-wrap">{{ customer.notes }}</p>
      </div>

      <!-- Kontakte Section -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">Kontakte</h3>
          <button @click="$emit('openContacts')" class="kit-btn-primary text-sm">
            <Plus :size="16" />
            Neuer Kontakt
          </button>
        </div>

        <!-- Loading -->
        <div v-if="contactsLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
          <p class="text-white/60 text-sm mt-2">Lade Kontakte...</p>
        </div>

        <!-- Contacts -->
        <div v-else-if="contacts.length > 0" class="space-y-2">
          <div
            v-for="contact in contacts"
            :key="contact.id"
            class="flex items-center justify-between p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 transition cursor-pointer"
            @click="emit('openContact', contact.id)"
          >
            <div class="flex items-center gap-3">
              <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
                <User :size="16" class="text-blue-200" />
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-medium text-white">
                    {{ contact.firstname }} {{ contact.lastname }}
                  </span>
                  <span
                    v-if="contact.is_primary"
                    class="text-xs font-medium text-emerald-200 bg-emerald-500/20 px-2 py-0.5 rounded border border-emerald-400/30"
                  >
                    Primär
                  </span>
                </div>
                <div class="text-xs text-white/60">
                  {{ contact.position || 'Keine Position' }}
                  <span v-if="contact.email"> · {{ contact.email }}</span>
                </div>
              </div>
            </div>

            <button
              v-if="!contact.is_primary"
              @click.stop="handleSetPrimary(contact.id)"
              class="text-xs text-white/60 hover:text-emerald-200 transition"
            >
              Als Primär setzen
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-8 text-white/40">
          <Users :size="40" class="mx-auto mb-2 opacity-50" />
          <p>Keine Kontakte vorhanden</p>
        </div>
      </div>

      <!-- Projekte Section -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">Projekte</h3>
        </div>

        <!-- Loading -->
        <div v-if="projectsLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
          <p class="text-white/60 text-sm mt-2">Lade Projekte...</p>
        </div>

        <!-- Projects -->
        <div v-else-if="projects.length > 0" class="space-y-2">
          <div
            v-for="project in projects"
            :key="project.id"
            class="flex items-center justify-between p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 transition cursor-pointer"
          >
            <div class="flex items-center gap-3">
              <div class="p-2 bg-orange-500/20 rounded-lg border border-orange-400/30">
                <FolderOpen :size="16" class="text-orange-200" />
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-medium text-white">
                    {{ project.title }}
                  </span>
                  <span
                    :class="[
                      'text-xs font-medium px-2 py-0.5 rounded border',
                      getProjectStatusBadge(project.status)
                    ]"
                  >
                    {{ getProjectStatusLabel(project.status) }}
                  </span>
                </div>
                <div class="text-xs text-white/60">
                  <span v-if="project.project_number">{{ project.project_number }}</span>
                  <span v-if="project.start_date"> · Start: {{ new Date(project.start_date).toLocaleDateString('de-DE') }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-8 text-white/40">
          <FolderOpen :size="40" class="mx-auto mb-2 opacity-50" />
          <p>Keine Projekte vorhanden</p>
        </div>
      </div>

      <!-- Rechnungen Section -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white">Rechnungen</h3>
          <button @click="handleCreateInvoice" class="kit-btn-primary text-sm">
            <Plus :size="16" />
            Neue Rechnung
          </button>
        </div>

        <!-- Loading -->
        <div v-if="invoicesLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
          <p class="text-white/60 text-sm mt-2">Lade Rechnungen...</p>
        </div>

        <!-- Invoices -->
        <div v-else-if="invoices.length > 0" class="space-y-2">
          <div
            v-for="invoice in invoices"
            :key="invoice.id"
            class="flex items-center justify-between p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 transition cursor-pointer"
            @click="handleInvoiceClick(invoice.id)"
          >
            <div class="flex items-center gap-3">
              <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
                <Receipt :size="16" class="text-blue-200" />
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <span class="font-medium text-white">
                    {{ invoice.invoice_number }}
                  </span>
                  <span
                    :class="[
                      'text-xs font-medium px-2 py-0.5 rounded border',
                      getInvoiceStatusBadge(invoice.status)
                    ]"
                  >
                    {{ getInvoiceStatusLabel(invoice.status) }}
                  </span>
                </div>
                <div class="text-xs text-white/60">
                  <span v-if="invoice.issued_date">{{ new Date(invoice.issued_date).toLocaleDateString('de-DE') }}</span>
                  <span v-if="invoice.total"> · {{ formatCurrency(invoice.total) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-8 text-white/40">
          <Receipt :size="40" class="mx-auto mb-2 opacity-50" />
          <p>Keine Rechnungen vorhanden</p>
        </div>
      </div>

      <!-- Aktivitäten Timeline -->
      <div class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-lg font-semibold text-white mb-4">Letzte Aktivitäten</h3>

        <!-- Loading -->
        <div v-if="activitiesLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mx-auto"></div>
          <p class="text-white/60 text-sm mt-2">Lade Aktivitäten...</p>
        </div>

        <!-- Activities -->
        <div v-else-if="activities && activities.length > 0" class="space-y-3">
          <div
            v-for="activity in activities"
            :key="activity.id"
            class="flex items-start gap-3 p-3 rounded-lg border border-white/5 bg-white/5"
          >
            <div class="p-2 bg-blue-500/20 rounded-lg border border-blue-400/30 flex-shrink-0">
              <component :is="getActivityIcon(activity.type)" :size="16" class="text-blue-200" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <span
                    class="text-xs font-medium text-blue-200 bg-blue-500/20 px-2 py-0.5 rounded border border-blue-400/30"
                  >
                    {{ getActivityLabel(activity.type) }}
                  </span>
                  <p class="text-white mt-1">{{ activity.description }}</p>
                </div>
                <span class="text-xs text-white/40 whitespace-nowrap">
                  {{ formatRelativeTime(activity.occurred_at) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="text-center py-8 text-white/40">
          <FileText :size="40" class="mx-auto mb-2 opacity-50" />
          <p>Keine Aktivitäten vorhanden</p>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click="showDeleteConfirm = false"
    >
      <div class="rounded-lg border border-white/10 bg-stone-900 p-6 max-w-md" @click.stop>
        <h3 class="text-xl font-bold text-white mb-2">Kunde löschen?</h3>
        <p class="text-white/60 mb-6">
          Möchten Sie {{ customer?.name }} wirklich löschen? Diese Aktion kann nicht rückgängig
          gemacht werden.
        </p>
        <div class="flex gap-3 justify-end">
          <button @click="showDeleteConfirm = false" class="kit-btn-ghost">Abbrechen</button>
          <button @click="handleDelete" class="kit-btn-danger">
            <Trash2 :size="18" />
            Löschen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Zusätzliche Styles falls benötigt */
</style>
