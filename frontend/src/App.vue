<template>
  <v-app>
    <v-app-bar
      v-if="!isAuthPage"
      app
      color="primary"
      elevation="0"
      class="app-bar-modern"
    >
      <v-app-bar-nav-icon 
        @click="drawer = !drawer" 
        class="menu-icon-white"
        size="large"
      />
      
      <v-toolbar-title class="d-flex align-center">
        <router-link to="/" class="text-decoration-none text-white d-flex align-center">
          <v-icon size="28" class="mr-2">mdi-chart-line-variant</v-icon>
          <span class="text-h6 font-weight-bold">EPMS</span>
        </router-link>
      </v-toolbar-title>

      <v-spacer />

      <!-- User Menu -->
      <v-menu offset-y>
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
            class="user-menu-btn"
            size="large"
          >
            <v-avatar size="36" class="user-avatar">
              <v-img
                v-if="user?.avatar"
                :src="user.avatar"
                :alt="user.full_name"
              />
              <v-icon v-else size="20">mdi-account-circle</v-icon>
            </v-avatar>
          </v-btn>
        </template>

        <v-list class="user-menu-list" min-width="280">
          <v-list-item class="user-info-item">
            <v-list-item-title class="text-h6 font-weight-bold">
              {{ getUserName(user) }}
            </v-list-item-title>
            <v-list-item-subtitle class="text-caption">
              {{ user?.employee_id || 'Employee' }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-divider class="my-2" />
          <v-list-item @click="goToProfile" class="menu-item">
            <template v-slot:prepend>
              <v-icon color="primary">mdi-account-circle</v-icon>
            </template>
            <v-list-item-title>Profile</v-list-item-title>
          </v-list-item>
          <v-list-item @click="logout" class="menu-item">
            <template v-slot:prepend>
              <v-icon color="error">mdi-logout</v-icon>
            </template>
            <v-list-item-title>Logout</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-if="!isAuthPage"
      v-model="drawer"
      app
      temporary
      class="modern-drawer"
      width="280"
    >
      <div class="drawer-header">
        <div class="d-flex align-center pa-4">
          <v-icon size="32" color="primary" class="mr-3">mdi-chart-line-variant</v-icon>
          <div>
            <div class="text-h6 font-weight-bold">EPMS</div>
            <div class="text-caption text-medium-emphasis">Performance Management</div>
          </div>
        </div>
        <v-divider />
      </div>
      
      <v-list class="navigation-list" density="comfortable">
        <v-list-item
          v-for="item in navigationItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          :disabled="item.disabled"
          class="navigation-item"
          rounded="lg"
        />
      </v-list>
    </v-navigation-drawer>

    <!-- Main Content -->
    <v-main class="main-content">
      <router-view />
    </v-main>

    <!-- Loading Overlay -->
    <v-overlay
      v-model="loading"
      class="loading-overlay"
      persistent
    >
      <div class="loading-content">
        <v-progress-circular
          color="primary"
          indeterminate
          size="64"
          width="6"
        />
        <div class="text-h6 mt-4">Loading...</div>
      </div>
    </v-overlay>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()

// Reactive data
const drawer = ref(false)
const loading = ref(false)

// Computed properties
const user = computed(() => authStore.user)
const isAuthPage = computed(() => {
  return route.path.startsWith('/login') || route.path.startsWith('/register')
})

const navigationItems = computed(() => {
  const items = [
    {
      title: 'Dashboard',
      icon: 'mdi-view-dashboard',
      to: '/dashboard'
    }
  ]

  if (user.value?.role === 'employee') {
    items.push(
      {
        title: 'Performance Dashboard',
        icon: 'mdi-view-dashboard',
        to: '/employee/performance-dashboard'
      },
      {
        title: 'My Goals',
        icon: 'mdi-target',
        to: '/employee/goals'
      },
      {
        title: 'Self Review',
        icon: 'mdi-account-edit',
        to: '/employee/self-review'
      },
      {
        title: 'Feedback',
        icon: 'mdi-comment-text',
        to: '/employee/feedback'
      }
    )
  }

  if (user.value?.role === 'manager') {
    items.push(
      {
        title: 'Team Goals',
        icon: 'mdi-account-group',
        to: '/manager/team-goals'
      },
      {
        title: 'Final Reviews',
        icon: 'mdi-clipboard-check',
        to: '/manager/review-dashboard'
      },
      {
        title: 'Team Reviews',
        icon: 'mdi-clipboard-text',
        to: '/manager/team-reviews'
      },
      {
        title: 'Team Feedback',
        icon: 'mdi-message-text',
        to: '/manager/team-feedback'
      },
      {
        title: 'Feedback Requests',
        icon: 'mdi-comment-plus',
        to: '/manager/feedback-requests'
      }
    )
  }

  if (user.value?.role === 'hr' || user.value?.role === 'admin') {
    items.push(
      {
        title: 'All Employees',
        icon: 'mdi-account-multiple',
        to: '/hr/employees'
      },
      {
        title: 'CSV Import',
        icon: 'mdi-file-upload',
        to: '/hr/csv-import'
      },
      {
        title: 'Review Cycles',
        icon: 'mdi-calendar-clock',
        to: '/hr/cycles'
      },
      {
        title: 'Analytics',
        icon: 'mdi-chart-line',
        to: '/hr/analytics'
      },
      {
        title: 'Reports',
        icon: 'mdi-file-chart',
        to: '/hr/reports'
      }
    )
  }

  return items
})

// Methods
const getUserName = (user) => {
  if (!user) return 'User'
  if (user.full_name) return user.full_name
  const firstName = user.first_name || ''
  const lastName = user.last_name || ''
  const fullName = `${firstName} ${lastName}`.trim()
  return fullName || user.username || user.email || 'User'
}

const goToProfile = () => {
  router.push('/profile')
}

const logout = async () => {
  try {
    loading.value = true
    await authStore.logout()
    toast.success('Logged out successfully')
    router.push('/login')
  } catch (error) {
    toast.error('Error logging out')
    console.error('Logout error:', error)
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(async () => {
  try {
    loading.value = true
    await authStore.checkAuth()
  } catch (error) {
    console.error('Auth check error:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* Modern App Bar Styling */
.app-bar-modern {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.menu-icon-white :deep(.v-icon) {
  color: white !important;
}

.user-menu-btn {
  transition: all 0.3s ease;
}

.user-menu-btn:hover {
  transform: scale(1.05);
}

.user-avatar {
  border: 2px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.user-avatar:hover {
  border-color: rgba(255, 255, 255, 0.4);
  transform: scale(1.05);
}

.user-menu-list {
  border-radius: 16px !important;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.user-info-item {
  background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
  border-radius: 12px;
  margin: 8px;
}

.menu-item {
  transition: all 0.2s ease;
  border-radius: 8px;
  margin: 4px 8px;
}

.menu-item:hover {
  background-color: rgba(37, 99, 235, 0.08);
  transform: translateX(4px);
}

/* Modern Navigation Drawer */
.modern-drawer {
  background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%) !important;
  border-right: 1px solid rgba(0, 0, 0, 0.05);
}

.drawer-header {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
  color: white;
  margin-bottom: 8px;
}

.navigation-list {
  padding: 8px;
}

.navigation-item {
  margin: 4px 0;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.navigation-item:hover {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.08) 0%, rgba(37, 99, 235, 0.04) 100%);
  transform: translateX(8px);
}

.navigation-item.v-list-item--active {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.navigation-item.v-list-item--active :deep(.v-icon) {
  color: white !important;
}

/* Main Content */
.main-content {
  background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
  min-height: 100vh;
}

/* Loading Overlay */
.loading-overlay {
  background: rgba(248, 250, 252, 0.95);
  backdrop-filter: blur(8px);
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

/* Responsive Design */
@media (max-width: 768px) {
  .modern-drawer {
    width: 100% !important;
  }
  
  .user-menu-list {
    min-width: 240px !important;
  }
}

/* Smooth Transitions */
.v-list-item {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.v-btn {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.v-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Custom Scrollbar */
.modern-drawer :deep(.v-navigation-drawer__content) {
  scrollbar-width: thin;
  scrollbar-color: rgba(37, 99, 235, 0.3) transparent;
}

.modern-drawer :deep(.v-navigation-drawer__content)::-webkit-scrollbar {
  width: 6px;
}

.modern-drawer :deep(.v-navigation-drawer__content)::-webkit-scrollbar-track {
  background: transparent;
}

.modern-drawer :deep(.v-navigation-drawer__content)::-webkit-scrollbar-thumb {
  background: rgba(37, 99, 235, 0.3);
  border-radius: 3px;
}

.modern-drawer :deep(.v-navigation-drawer__content)::-webkit-scrollbar-thumb:hover {
  background: rgba(37, 99, 235, 0.5);
}
</style>