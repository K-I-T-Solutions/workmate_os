<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-white">Audit Trail</h1>
      <p class="text-white/60 mt-2">
        Lückenlose Nachvollziehbarkeit aller Änderungen (GoBD Compliance)
      </p>
    </div>

    <!-- Filters -->
    <div class="rounded-lg border border-white/10 bg-white/5 p-6">
      <h2 class="text-lg font-semibold text-white mb-4">Filter</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Entity Type Filter -->
        <div>
          <label class="kit-label">Entitätstyp</label>
          <select
            v-model="filters.entity_type"
            @change="applyFilters"
            class="kit-input"
          >
            <option value="">Alle</option>
            <option value="Invoice">Rechnungen</option>
            <option value="Payment">Zahlungen</option>
            <option value="Expense">Ausgaben</option>
          </select>
        </div>

        <!-- Action Filter -->
        <div>
          <label class="kit-label">Aktion</label>
          <select
            v-model="filters.action"
            @change="applyFilters"
            class="kit-input"
          >
            <option value="">Alle</option>
            <option value="create">Erstellt</option>
            <option value="update">Aktualisiert</option>
            <option value="delete">Gelöscht</option>
            <option value="status_change">Status geändert</option>
          </select>
        </div>

        <!-- Entity ID Filter -->
        <div>
          <label class="kit-label">Entitäts-ID</label>
          <input
            v-model="filters.entity_id"
            @input="applyFiltersDebounced"
            type="text"
            placeholder="UUID filtern..."
            class="kit-input"
          />
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="rounded-lg border border-red-500/20 bg-red-500/10 p-4">
      <p class="text-red-400">{{ error }}</p>
    </div>

    <!-- Audit Logs List -->
    <div v-else-if="auditLogs.length > 0" class="space-y-3">
      <div
        v-for="log in auditLogs"
        :key="log.id"
        class="rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 transition-colors"
      >
        <div class="flex items-start justify-between gap-4">
          <!-- Left: Action & Entity -->
          <div class="flex items-start gap-3 flex-1">
            <!-- Action Badge -->
            <div
              class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
              :class="getActionBgColor(log.action)"
            >
              <span class="text-lg" v-html="getActionIcon(log.action)"></span>
            </div>

            <div class="flex-1">
              <!-- Action & Entity Type -->
              <div class="flex items-center gap-2 mb-1">
                <span class="font-semibold text-white">{{ getActionLabel(log.action) }}</span>
                <span class="text-white/40">•</span>
                <span class="text-white/60">{{ log.entity_type }}</span>
              </div>

              <!-- Entity ID -->
              <p class="text-sm text-white/40 font-mono">{{ log.entity_id }}</p>

              <!-- Changed Fields (for updates) -->
              <div v-if="log.action === 'update' && log.old_values && log.new_values" class="mt-2">
                <div class="text-sm text-white/60">
                  Geänderte Felder:
                  <span class="text-blue-400 ml-2">
                    {{ getChangedFields(log.old_values, log.new_values).join(', ') }}
                  </span>
                </div>
              </div>

              <!-- Status Change Details -->
              <div v-if="log.action === 'status_change' && log.old_values && log.new_values" class="mt-2">
                <div class="flex items-center gap-2 text-sm">
                  <span class="text-white/60">Status:</span>
                  <span class="text-red-400">{{ log.old_values.status }}</span>
                  <span class="text-white/40">→</span>
                  <span class="text-green-400">{{ log.new_values.status }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Right: Timestamp & User -->
          <div class="text-right flex-shrink-0">
            <p class="text-sm text-white/60">{{ formatTimestamp(log.timestamp) }}</p>
            <p v-if="log.user_id" class="text-xs text-white/40 mt-1">
              User: {{ log.user_id }}
            </p>
            <p v-if="log.ip_address" class="text-xs text-white/40 font-mono">
              {{ log.ip_address }}
            </p>
          </div>
        </div>

        <!-- Details Toggle (expandable for full old/new values) -->
        <button
          v-if="log.old_values || log.new_values"
          @click="toggleDetails(log.id)"
          class="mt-3 text-sm text-blue-400 hover:text-blue-300 transition-colors"
        >
          {{ expandedLogs.has(log.id) ? '▼ Details ausblenden' : '▶ Details anzeigen' }}
        </button>

        <!-- Expanded Details -->
        <div v-if="expandedLogs.has(log.id)" class="mt-3 space-y-2">
          <div v-if="log.old_values" class="rounded bg-white/5 p-3">
            <p class="text-xs text-white/60 mb-2">Alte Werte:</p>
            <pre class="text-xs text-white/80 overflow-x-auto">{{ JSON.stringify(log.old_values, null, 2) }}</pre>
          </div>
          <div v-if="log.new_values" class="rounded bg-white/5 p-3">
            <p class="text-xs text-white/60 mb-2">Neue Werte:</p>
            <pre class="text-xs text-white/80 overflow-x-auto">{{ JSON.stringify(log.new_values, null, 2) }}</pre>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="flex items-center justify-between pt-4">
        <p class="text-sm text-white/60">
          Zeige {{ auditLogs.length }} von {{ total }} Einträgen
        </p>
        <div class="flex gap-2">
          <button
            @click="previousPage"
            :disabled="currentPage === 0"
            class="px-4 py-2 rounded-lg bg-white/5 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/10 transition-colors"
          >
            Zurück
          </button>
          <button
            @click="nextPage"
            :disabled="(currentPage + 1) * pageSize >= total"
            class="px-4 py-2 rounded-lg bg-white/5 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-white/10 transition-colors"
          >
            Weiter
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="rounded-lg border border-white/10 bg-white/5 p-12 text-center">
      <p class="text-white/60">Keine Audit-Log-Einträge gefunden</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuditLogs } from '../composables/useAuditLogs'

const {
  auditLogs,
  total,
  loading,
  error,
  fetchAuditLogs,
  getActionLabel,
  getActionColor,
  formatTimestamp,
  getChangedFields
} = useAuditLogs()

const filters = ref({
  entity_type: '',
  entity_id: '',
  action: ''
})

const currentPage = ref(0)
const pageSize = ref(50)
const expandedLogs = ref(new Set<string>())

let debounceTimeout: ReturnType<typeof setTimeout> | null = null

const applyFilters = () => {
  currentPage.value = 0
  loadAuditLogs()
}

const applyFiltersDebounced = () => {
  if (debounceTimeout) clearTimeout(debounceTimeout)
  debounceTimeout = setTimeout(() => {
    applyFilters()
  }, 500)
}

const loadAuditLogs = () => {
  fetchAuditLogs({
    entity_type: filters.value.entity_type || undefined,
    entity_id: filters.value.entity_id || undefined,
    action: filters.value.action || undefined,
    skip: currentPage.value * pageSize.value,
    limit: pageSize.value
  })
}

const previousPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--
    loadAuditLogs()
  }
}

const nextPage = () => {
  if ((currentPage.value + 1) * pageSize.value < total.value) {
    currentPage.value++
    loadAuditLogs()
  }
}

const toggleDetails = (logId: string) => {
  if (expandedLogs.value.has(logId)) {
    expandedLogs.value.delete(logId)
  } else {
    expandedLogs.value.add(logId)
  }
}

const getActionIcon = (action: string): string => {
  const icons: Record<string, string> = {
    create: '➕',
    update: '✏️',
    delete: '🗑️',
    status_change: '🔄'
  }
  return icons[action] || '📝'
}

const getActionBgColor = (action: string): string => {
  const colors: Record<string, string> = {
    create: 'bg-green-500/20',
    update: 'bg-blue-500/20',
    delete: 'bg-red-500/20',
    status_change: 'bg-yellow-500/20'
  }
  return colors[action] || 'bg-gray-500/20'
}

onMounted(() => {
  loadAuditLogs()
})
</script>
