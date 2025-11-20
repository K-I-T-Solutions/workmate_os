<template>
  <div class="main-page flex h-full w-full overflow-hidden">
    <!-- Sidebar -->
    <Sidebar class="hidden md:block" />

    <!-- Main Content Area -->
    <div class="flex flex-col flex-1 h-full">
      <!-- Topbar -->
      <Topbar title="Dashboard" />

      <!-- Content -->
      <main class="flex-1 p-6 mt-[var(--os-topbar-height)] overflow-y-auto">
        <kitPanel title="Welcome to WorkmateOS" variant="glass" padding="lg">
          <p class="text-text-secondary">
            This is your central hub. Choose a module from the sidebar or dock.
          </p>
        </kitPanel>

        <!-- Example Widget Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mt-6">
          <kitPanel title="Quick Stats">
            <ul class="text-text-secondary text-sm">
              <li>• Active Projects: 0</li>
              <li>• Pending Invoices: 0</li>
              <li>• Registered Customers: 0</li>
            </ul>
          </kitPanel>

          <kitPanel title="Recent Activity" variant="default">
            <p class="text-text-secondary text-sm">No recent activity.</p>
          </kitPanel>
          <kitPanel title="Shortcuts" variant="default">
            <div class="flex gap-3 mt-2">
              <kitButtons label="New Project" variant="primary" size="sm" />
              <kitButtons label="New Invoice" variant="secondary" size="sm" />
            </div>
          </kitPanel>
          </div>
      </main>
    </div>

    <!-- Dock -->
    <Dock />
  </div>
</template>

<script setup lang="ts">
import Sidebar from "@/components/layout/Sidebar.vue";
import Topbar from "@/components/os/Topbar.vue";
import Dock from "@/components/os/Dock.vue";
import kitPanel from "@/components/system/kit-panel.vue";
import kitButtons from "@/components/system/kit-buttons.vue";
</script>

<style scoped>
.main-page {
  background: var(--color-bg-primary);
}
</style>
