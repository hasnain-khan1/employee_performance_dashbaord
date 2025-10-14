<template>
  <v-app>
    <v-app-bar
      v-if="!isAuthPage"
      app
      color="primary"
      dark
      elevation="2"
    >
      <v-app-bar-nav-icon @click="drawer = !drawer" class="menu-icon-black"></v-app-bar-nav-icon>
      
      <v-toolbar-title>
        <router-link to="/" class="text-decoration-none text-white">
          EPMS
        </router-link>
      </v-toolbar-title>

      <v-spacer />

      <!-- User Menu -->
      <v-menu offset-y>
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
          >
            <v-avatar size="32">
              <v-img
                v-if="user?.avatar"
                :src="user.avatar"
                :alt="user.full_name"
              />
              <v-icon v-else>mdi-account</v-icon>
            </v-avatar>
          </v-btn>
        </template>

        <v-list>
          <v-list-item>
            <v-list-item-title>{{ getUserName(user) }}</v-list-item-title>
            <v-list-item-subtitle>{{ user?.employee_id || 'Employee' }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item @click="goToProfile">
            <v-list-item-icon>
              <v-icon>mdi-account</v-icon>
            </v-list-item-icon>
            <v-list-item-title>Profile</v-list-item-title>
          </v-list-item>
          <v-list-item @click="logout">
            <v-list-item-icon>
              <v-icon>mdi-logout</v-icon>
            </v-list-item-icon>
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
    >
      <v-list>
        <v-list-item
          v-for="item in navigationItems"
          :key="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          :disabled="item.disabled"
        />
      </v-list>
    </v-navigation-drawer>

    <!-- Main Content -->
    <v-main>
      <router-view />
    </v-main>

    <!-- Loading Overlay -->
    <v-overlay
      v-model="loading"
      class="align-center justify-center"
    >
      <v-progress-circular
        color="primary"
        indeterminate
        size="64"
      />
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
.v-navigation-drawer {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.v-list-item--active {
  background-color: rgba(25, 118, 210, 0.08);
}

.menu-icon-black :deep(.v-icon) {
  color: black !important;
}
</style>