<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useCurrentUser } from '@/composables/useCurrentUser';
import {
  User,
  Settings,
  LogOut,
  ChevronDown,
} from 'lucide-vue-next';

// Emits
const emit = defineEmits<{
  openProfile: [];
  openSettings: [];
  logout: [];
}>();

// Composable
const { currentUser, fullName, displayName, getGravatarUrl, loadCurrentUser } = useCurrentUser();

// State
const isOpen = ref(false);
const dropdownRef = ref<HTMLElement | null>(null);

// Load user on mount
onMounted(() => {
  loadCurrentUser();
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

// Actions
function toggleDropdown() {
  isOpen.value = !isOpen.value;
}

function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false;
  }
}

function handleOpenProfile() {
  isOpen.value = false;
  emit('openProfile');
}

function handleOpenSettings() {
  isOpen.value = false;
  emit('openSettings');
}

function handleLogout() {
  isOpen.value = false;
  emit('logout');
}
</script>

<template>
  <div ref="dropdownRef" class="user-dropdown-container">
    <!-- Trigger Button -->
    <button
      class="user-dropdown-trigger"
      aria-label="User menu"
      @click="toggleDropdown"
    >
      <!-- Gravatar Image -->
      <img
        v-if="currentUser"
        :src="getGravatarUrl(80)"
        :alt="fullName"
        class="user-avatar"
      />
      <div v-else class="user-avatar-placeholder">
        <User :size="16" />
      </div>

      <!-- Chevron -->
      <ChevronDown
        :size="14"
        class="user-dropdown-chevron"
        :class="{ 'rotate-180': isOpen }"
      />
    </button>

    <!-- Dropdown Menu -->
    <Transition name="dropdown">
      <div v-if="isOpen" class="user-dropdown-menu">
        <!-- User Info Header -->
        <div class="user-dropdown-header">
          <img
            v-if="currentUser"
            :src="getGravatarUrl(96)"
            :alt="fullName"
            class="user-avatar-large"
          />
          <div v-else class="user-avatar-large-placeholder">
            <User :size="24" />
          </div>

          <div class="user-info">
            <div class="user-name">{{ fullName }}</div>
            <div v-if="currentUser" class="user-code">{{ currentUser.employee_code }}</div>
          </div>
        </div>

        <!-- Divider -->
        <div class="dropdown-divider"></div>

        <!-- Menu Items -->
        <button @click="handleOpenProfile" class="dropdown-item">
          <User :size="16" />
          <span>Mein Profil</span>
        </button>

        <button @click="handleOpenSettings" class="dropdown-item">
          <Settings :size="16" />
          <span>Einstellungen</span>
        </button>

        <!-- Divider -->
        <div class="dropdown-divider"></div>

        <!-- Logout -->
        <button @click="handleLogout" class="dropdown-item dropdown-item-danger">
          <LogOut :size="16" />
          <span>Abmelden</span>
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* Container */
.user-dropdown-container {
  position: relative;
}

/* Trigger Button */
.user-dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem;
  padding-right: 0.5rem;
  border-radius: 0.75rem;
  border: 1px solid var(--color-border-light);
  background: transparent;
  transition: all 0.2s;
  cursor: pointer;
}

.user-dropdown-trigger:hover {
  background: var(--color-panel-glass);
  border-color: var(--color-border-medium);
}

/* Avatar */
.user-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  object-fit: cover;
}

.user-avatar-placeholder {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  background: var(--color-panel-glass-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
}

/* Chevron */
.user-dropdown-chevron {
  color: var(--color-text-tertiary);
  transition: transform 0.2s;
}

/* Dropdown Menu */
.user-dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 16rem;
  background: var(--color-bg-secondary);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-light);
  border-radius: 0.75rem;
  padding: 0.5rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  z-index: 1000;
}

/* Header */
.user-dropdown-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
}

.user-avatar-large {
  width: 3rem;
  height: 3rem;
  border-radius: 0.625rem;
  object-fit: cover;
}

.user-avatar-large-placeholder {
  width: 3rem;
  height: 3rem;
  border-radius: 0.625rem;
  background: var(--color-panel-glass-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-weight: 600;
  color: var(--color-text-primary);
  font-size: 0.875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-code {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  margin-top: 0.125rem;
}

/* Divider */
.dropdown-divider {
  height: 1px;
  background: var(--color-border-light);
  margin: 0.5rem 0;
}

/* Menu Items */
.dropdown-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.5rem;
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.dropdown-item:hover {
  background: var(--color-panel-glass-hover);
  color: var(--color-text-primary);
}

.dropdown-item-danger {
  color: var(--color-error);
}

.dropdown-item-danger:hover {
  background: var(--color-error-bg);
  color: var(--color-error);
}

/* Transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-0.5rem);
}
</style>
