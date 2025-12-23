<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useContacts } from '../../composables/useContacts';
import { useCustomers } from '../../composables/useCustomers';
import { useCrmActivity } from '../../composables/useCrmActivity';
import {
  ChevronLeft,
  Edit,
  Trash2,
  Mail,
  Phone,
  User,
  CheckCircle,
  Phone as PhoneIcon,
  Mail as MailIcon,
  MapPin,
  MonitorPlay,
  FileText,
} from 'lucide-vue-next';

// Props
const props = defineProps<{
  customerId: string;
  contactId: string;
}>();

// Emits
const emit = defineEmits<{
  back: [];
  edit: [contactId: string];
}>();

// Composables
const { currentContact, loading: contactLoading, loadContact, deleteContact, setPrimaryContact } = useContacts();
const { currentCustomer, loadCustomer } = useCustomers();
const { activities, loading: activitiesLoading, fetchCustomerActivities } = useCrmActivity();

// State
const showDeleteConfirm = ref(false);

// Lifecycle
onMounted(async () => {
  await loadContact(props.contactId);
  await loadCustomer(props.customerId);
  await fetchCustomerActivities(props.customerId, { contactId: props.contactId, limit: 10 });
});

// Computed
const contact = computed(() => currentContact.value);
const customer = computed(() => currentCustomer.value);
const isPrimary = computed(() => contact.value?.is_primary || false);
const fullName = computed(() =>
  contact.value ? `${contact.value.firstname} ${contact.value.lastname}` : ''
);

// Actions
async function handleDelete() {
  if (!contact.value) return;

  const success = await deleteContact(contact.value.id);
  if (success) {
    emit('back');
  }
}

async function handleSetPrimary() {
  if (!contact.value) return;
  await setPrimaryContact(props.customerId, contact.value.id);
}

// Helpers
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
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="emit('back')" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <div v-if="contact">
          <h1 class="text-2xl font-bold text-white flex items-center gap-3">
            {{ fullName }}
            <span
              v-if="isPrimary"
              class="px-2 py-1 rounded text-sm font-medium border bg-emerald-500/20 border-emerald-400/30 text-emerald-200"
            >
              Primär
            </span>
          </h1>
          <p class="text-sm text-white/60 mt-1">
            {{ contact.position || 'Kontakt' }}
            <span v-if="contact.department"> · {{ contact.department }}</span>
            <span v-if="customer"> · {{ customer.name }}</span>
          </p>
        </div>
      </div>

      <div v-if="contact" class="flex gap-2">
        <button
          v-if="!isPrimary"
          @click="handleSetPrimary"
          class="kit-btn-ghost"
          title="Als Primärkontakt setzen"
        >
          <CheckCircle :size="18" />
          Als Primär
        </button>
        <button @click="emit('edit', contactId)" class="kit-btn-secondary">
          <Edit :size="18" />
          Bearbeiten
        </button>
        <button @click="showDeleteConfirm = true" class="kit-btn-danger">
          <Trash2 :size="18" />
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="contactLoading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Kontaktdaten...</p>
      </div>
    </div>

    <!-- Content -->
    <div v-else-if="contact" class="flex-1 overflow-auto space-y-4">
      <!-- Main Info Grid (3 Spalten) -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Kontaktdaten -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 text-white/60 mb-3">
            <Mail :size="16" />
            <h3 class="text-sm font-medium">Kontaktdaten</h3>
          </div>
          <div class="space-y-2 text-sm">
            <div v-if="contact.email">
              <div class="text-white/50 text-xs">E-Mail</div>
              <a
                :href="`mailto:${contact.email}`"
                class="text-blue-200 hover:text-blue-100 transition"
              >
                {{ contact.email }}
              </a>
            </div>
            <div v-if="contact.phone">
              <div class="text-white/50 text-xs">Telefon</div>
              <a
                :href="`tel:${contact.phone}`"
                class="text-blue-200 hover:text-blue-100 transition"
              >
                {{ contact.phone }}
              </a>
            </div>
            <div v-if="contact.mobile">
              <div class="text-white/50 text-xs">Mobil</div>
              <a
                :href="`tel:${contact.mobile}`"
                class="text-blue-200 hover:text-blue-100 transition"
              >
                {{ contact.mobile }}
              </a>
            </div>
            <div v-if="!contact.email && !contact.phone && !contact.mobile" class="text-white/40">
              Keine Kontaktdaten hinterlegt
            </div>
          </div>
        </div>

        <!-- Position & Abteilung -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 text-white/60 mb-3">
            <User :size="16" />
            <h3 class="text-sm font-medium">Position & Abteilung</h3>
          </div>
          <div class="space-y-2 text-sm">
            <div v-if="contact.position">
              <div class="text-white/50 text-xs">Position</div>
              <div class="text-white">{{ contact.position }}</div>
            </div>
            <div v-if="contact.department">
              <div class="text-white/50 text-xs">Abteilung</div>
              <div class="text-white">{{ contact.department }}</div>
            </div>
            <div v-if="!contact.position && !contact.department" class="text-white/40">
              Keine Position oder Abteilung hinterlegt
            </div>
          </div>
        </div>

        <!-- Statistiken -->
        <div class="rounded-lg border border-white/10 bg-white/5 p-4">
          <div class="flex items-center gap-2 text-white/60 mb-3">
            <CheckCircle :size="16" />
            <h3 class="text-sm font-medium">Status</h3>
          </div>
          <div class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-white/60">Primärkontakt:</span>
              <span :class="[
                'font-medium',
                isPrimary ? 'text-emerald-200' : 'text-white/60'
              ]">
                {{ isPrimary ? 'Ja' : 'Nein' }}
              </span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-white/60">Aktivitäten:</span>
              <span class="text-white font-medium">{{ activities?.length || 0 }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-white/60">Kunde:</span>
              <span class="text-white font-medium truncate">{{ customer?.name || '-' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Notizen -->
      <div v-if="contact.notes" class="rounded-lg border border-white/10 bg-white/5 p-4">
        <h3 class="text-sm font-medium text-white/60 mb-2">Notizen</h3>
        <p class="text-white text-sm whitespace-pre-wrap">{{ contact.notes }}</p>
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
        <h3 class="text-xl font-bold text-white mb-2">Kontakt löschen?</h3>
        <p class="text-white/60 mb-6">
          Möchten Sie {{ fullName }} wirklich löschen? Diese Aktion kann nicht rückgängig
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
