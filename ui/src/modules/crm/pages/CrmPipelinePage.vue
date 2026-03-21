<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { ChevronLeft, Users, Trophy, Ban } from 'lucide-vue-next';
import { useCustomers } from '../composables/useCustomers';
import type { Customer, PipelineStage } from '../types/customer';

// Props & Emits
const emit = defineEmits<{
  back: [];
  openCustomer: [id: string];
}>();

const { pipeline, loading, error, loadPipeline, updatePipelineStage } = useCustomers();

// ─── PIPELINE STAGES CONFIG ───────────────────────────────
const STAGES: { key: PipelineStage; label: string; color: string; headerColor: string }[] = [
  { key: 'new_lead',    label: 'Neuer Lead',   color: 'border-cyan-400/40 bg-cyan-500/10',    headerColor: 'text-cyan-300' },
  { key: 'qualified',  label: 'Qualifiziert',  color: 'border-blue-400/40 bg-blue-500/10',    headerColor: 'text-blue-300' },
  { key: 'proposal',   label: 'Angebot',       color: 'border-orange-400/40 bg-orange-500/10', headerColor: 'text-orange-300' },
  { key: 'negotiation',label: 'Verhandlung',   color: 'border-yellow-400/40 bg-yellow-500/10', headerColor: 'text-yellow-300' },
  { key: 'won',        label: 'Gewonnen',      color: 'border-emerald-400/40 bg-emerald-500/10', headerColor: 'text-emerald-300' },
  { key: 'lost',       label: 'Verloren',      color: 'border-white/10 bg-white/5',           headerColor: 'text-white/50' },
];

// ─── DRAG & DROP STATE ────────────────────────────────────
const dragCustomerId = ref<string | null>(null);
const dragOverStage = ref<PipelineStage | null>(null);

function onDragStart(event: DragEvent, customer: Customer) {
  dragCustomerId.value = customer.id;
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', customer.id);
  }
}

function onDragOver(event: DragEvent, stage: PipelineStage) {
  event.preventDefault();
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move';
  }
  dragOverStage.value = stage;
}

function onDragLeave() {
  dragOverStage.value = null;
}

async function onDrop(event: DragEvent, targetStage: PipelineStage) {
  event.preventDefault();
  dragOverStage.value = null;

  const customerId = dragCustomerId.value;
  if (!customerId) return;
  dragCustomerId.value = null;

  // Prüfen ob Stage sich geändert hat
  const currentStage = findCustomerStage(customerId);
  if (currentStage === targetStage) return;

  await updatePipelineStage(customerId, targetStage);
}

function onDragEnd() {
  dragCustomerId.value = null;
  dragOverStage.value = null;
}

function findCustomerStage(customerId: string): PipelineStage | null {
  for (const stage of STAGES) {
    const customers = pipeline.value[stage.key] || [];
    if (customers.some(c => c.id === customerId)) return stage.key;
  }
  return null;
}

// ─── COMPUTED ─────────────────────────────────────────────
function getStageCustomers(stage: PipelineStage): Customer[] {
  return pipeline.value[stage] || [];
}

function getStageCount(stage: PipelineStage): number {
  return getStageCustomers(stage).length;
}

// ─── LIFECYCLE ────────────────────────────────────────────
onMounted(() => {
  loadPipeline();
});
</script>

<template>
  <div class="h-full flex flex-col gap-4 p-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="emit('back')" class="kit-btn-ghost">
          <ChevronLeft :size="18" />
        </button>
        <div>
          <h1 class="text-2xl font-bold text-white">Sales Pipeline</h1>
          <p class="text-sm text-white/60 mt-1">Drag & Drop zum Verschieben</p>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p class="mt-4 text-white/60">Lade Pipeline...</p>
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="rounded-lg border border-red-400/30 bg-red-500/20 p-4">
      <p class="text-red-200">{{ error }}</p>
    </div>

    <!-- Kanban Board -->
    <div v-else class="flex-1 overflow-x-auto">
      <div class="flex gap-4 h-full min-h-0" style="min-width: max-content;">
        <div
          v-for="stage in STAGES"
          :key="stage.key"
          class="w-72 flex flex-col rounded-xl border transition-all duration-150"
          :class="[
            stage.color,
            dragOverStage === stage.key ? 'ring-2 ring-white/30 scale-[1.01]' : '',
          ]"
          @dragover="onDragOver($event, stage.key)"
          @dragleave="onDragLeave"
          @drop="onDrop($event, stage.key)"
        >
          <!-- Stage Header -->
          <div class="p-3 border-b border-white/10 flex items-center justify-between">
            <span class="font-semibold text-sm" :class="stage.headerColor">
              {{ stage.label }}
            </span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-white/10 text-white/60 font-mono">
              {{ getStageCount(stage.key) }}
            </span>
          </div>

          <!-- Cards -->
          <div class="flex-1 overflow-y-auto p-2 space-y-2 min-h-[120px]">
            <!-- Empty State -->
            <div
              v-if="getStageCustomers(stage.key).length === 0"
              class="h-full flex items-center justify-center text-white/20 text-sm py-8"
            >
              Keine Kunden
            </div>

            <!-- Customer Cards -->
            <div
              v-for="customer in getStageCustomers(stage.key)"
              :key="customer.id"
              class="rounded-lg border border-white/10 bg-white/5 p-3 cursor-grab hover:bg-white/10 transition select-none"
              :class="dragCustomerId === customer.id ? 'opacity-40' : ''"
              draggable="true"
              @dragstart="onDragStart($event, customer)"
              @dragend="onDragEnd"
            >
              <!-- Name -->
              <div class="flex items-center gap-2 mb-2">
                <div class="p-1.5 bg-blue-500/20 rounded border border-blue-400/30">
                  <Users :size="14" class="text-blue-200" />
                </div>
                <span class="font-medium text-sm text-white truncate">{{ customer.name }}</span>
              </div>

              <!-- Meta -->
              <div class="space-y-1">
                <p v-if="customer.email" class="text-xs text-white/50 truncate">{{ customer.email }}</p>
                <p v-if="customer.city" class="text-xs text-white/40">{{ customer.city }}</p>
                <p v-if="customer.customer_number" class="text-xs text-white/30 font-mono">{{ customer.customer_number }}</p>
              </div>

              <!-- Actions -->
              <div class="mt-2 pt-2 border-t border-white/5 flex gap-1">
                <button
                  @click.stop="emit('openCustomer', customer.id)"
                  class="flex-1 text-xs py-1 px-2 rounded hover:bg-white/10 text-white/60 hover:text-white transition text-center"
                >
                  Details
                </button>
                <button
                  v-if="stage.key !== 'won'"
                  @click.stop="updatePipelineStage(customer.id, 'won')"
                  class="px-2 py-1 rounded hover:bg-emerald-500/20 text-emerald-400/60 hover:text-emerald-300 transition"
                  title="Als gewonnen markieren"
                >
                  <Trophy :size="12" />
                </button>
                <button
                  v-if="stage.key !== 'lost'"
                  @click.stop="updatePipelineStage(customer.id, 'lost')"
                  class="px-2 py-1 rounded hover:bg-white/10 text-white/30 hover:text-white/60 transition"
                  title="Als verloren markieren"
                >
                  <Ban :size="12" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
