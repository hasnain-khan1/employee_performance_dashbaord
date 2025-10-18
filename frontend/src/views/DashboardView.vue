<template>
  <v-container fluid class="dashboard-container">
    <!-- Header -->
    <v-row>
      <v-col cols="12">
        <div class="dashboard-header">
          <div class="header-content">
            <div class="welcome-section">
              <h1 class="dashboard-title">
                <v-icon size="32" color="primary" class="mr-3">mdi-view-dashboard</v-icon>
                Dashboard
              </h1>
              <p class="welcome-text">
                Welcome back, <span class="user-name">{{ user?.full_name || 'User' }}</span>!
              </p>
              <p class="date-text">{{ currentDate }}</p>
            </div>
            <v-btn
              color="primary"
              prepend-icon="mdi-refresh"
              @click="refreshDashboard"
              :loading="loading"
              class="refresh-btn"
              size="large"
              rounded="lg"
            >
              Refresh
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Quick Stats -->
    <v-row v-if="quickStats.length > 0" class="stats-row">
      <v-col cols="12" sm="6" md="3" v-for="(stat, index) in quickStats" :key="'stat-' + index">
        <v-card 
          class="stat-card modern-stat-card" 
          :class="stat.colorClass"
          elevation="0"
          rounded="xl"
        >
          <v-card-text class="stat-content">
            <div class="stat-header">
              <div class="stat-icon-container">
                <v-icon :color="stat.iconColor" size="28">{{ stat.icon }}</v-icon>
              </div>
              <div class="stat-trend" v-if="stat.trend">
                <v-icon 
                  :color="stat.trend > 0 ? 'success' : 'error'" 
                  size="16"
                >
                  {{ stat.trend > 0 ? 'mdi-trending-up' : 'mdi-trending-down' }}
                </v-icon>
                <span class="trend-text">{{ Math.abs(stat.trend) }}%</span>
              </div>
            </div>
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-title">{{ stat.title }}</div>
            <div class="stat-subtitle" v-if="stat.subtitle">{{ stat.subtitle }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Employee Dashboard -->
    <template v-if="isEmployee && employeeData">
      <v-row>
        <v-col cols="12" md="8">
          <v-card elevation="2">
            <v-card-title class="bg-primary">
              <v-icon left color="white">mdi-target</v-icon>
              <span class="text-white">My Goals</span>
            </v-card-title>
            <v-card-text class="pa-0">
              <v-list v-if="employeeData.recent_goals && employeeData.recent_goals.length > 0">
                <v-list-item
                  v-for="goal in employeeData.recent_goals"
                  :key="goal.id"
                  :to="`/employee/goals`"
                  class="border-b"
                >
                  <v-list-item-title class="font-weight-medium">{{ goal.title }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-progress-linear
                      :model-value="goal.progress_percentage"
                      color="primary"
                      height="8"
                      class="mt-2"
                      rounded
                    >
                      <template v-slot:default>
                        <strong class="text-caption">{{ goal.progress_percentage }}%</strong>
                      </template>
                    </v-progress-linear>
                  </v-list-item-subtitle>
                  <template v-slot:append>
                    <v-chip
                      :color="getGoalStatusColor(goal.status)"
                      size="small"
                      label
                    >
                      {{ formatStatus(goal.status) }}
                    </v-chip>
                  </template>
                </v-list-item>
              </v-list>
              <div v-else class="pa-8 text-center text-grey">
                <v-icon size="64" color="grey-lighten-1">mdi-target</v-icon>
                <p class="mt-4">No goals found. Create your first goal to get started!</p>
              </div>
            </v-card-text>
            <v-card-actions>
              <v-btn
                color="primary"
                variant="text"
                to="/employee/goals"
                block
              >
                View All Goals
                <v-icon right>mdi-arrow-right</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card elevation="2" class="mb-4">
            <v-card-title class="bg-blue">
              <v-icon left color="white">mdi-calendar-clock</v-icon>
              <span class="text-white">Current Review Cycle</span>
            </v-card-title>
            <v-card-text>
              <div v-if="employeeData.current_cycle" class="text-center">
                <h3 class="mt-3">{{ employeeData.current_cycle.name }}</h3>
                <p class="text-body-2 text-grey">{{ employeeData.current_cycle.description }}</p>
                
                <v-progress-circular
                  :model-value="employeeData.current_cycle.completion_percentage"
                  :size="120"
                  :width="12"
                  color="primary"
                  class="my-4"
                >
                  <span class="text-h5 font-weight-bold">
                    {{ employeeData.current_cycle.completion_percentage }}%
                  </span>
                </v-progress-circular>
                
                <div class="text-caption text-grey">
                  Ends: {{ formatDate(employeeData.current_cycle.end_date) }}
                </div>
              </div>
              <div v-else class="pa-4 text-center text-grey">
                <v-icon size="48" color="grey-lighten-1">mdi-calendar-remove</v-icon>
                <p class="mt-2">No active review cycle</p>
              </div>
            </v-card-text>
          </v-card>

          <v-card elevation="2">
            <v-card-title class="bg-green">
              <v-icon left color="white">mdi-chart-bar</v-icon>
              <span class="text-white">My Statistics</span>
            </v-card-title>
            <v-card-text v-if="employeeData.stats">
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>Total Goals</v-list-item-title>
                  <template v-slot:append>
                    <v-chip color="primary" size="small">{{ employeeData.stats.total_goals }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Completed</v-list-item-title>
                  <template v-slot:append>
                    <v-chip color="success" size="small">{{ employeeData.stats.completed_goals }}</v-chip>
                  </template>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Feedback Received</v-list-item-title>
                  <template v-slot:append>
                    <v-chip color="blue" size="small">{{ employeeData.stats.feedback_count }}</v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Manager Dashboard -->
    <template v-if="isManager && managerData">
      <v-row>
        <v-col cols="12" md="6">
          <v-card elevation="2" class="mb-4">
            <v-card-title class="bg-primary">
              <v-icon left color="white">mdi-account-group</v-icon>
              <span class="text-white">Team Overview</span>
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="6" class="text-center">
                  <div class="text-h3 font-weight-bold text-primary">{{ managerData.team_stats.total_members }}</div>
                  <div class="text-caption text-grey">Team Members</div>
                </v-col>
                <v-col cols="6" class="text-center">
                  <div class="text-h3 font-weight-bold text-success">{{ managerData.team_stats.goals_completed }}</div>
                  <div class="text-caption text-grey">Goals Completed</div>
                </v-col>
                <v-col cols="6" class="text-center">
                  <div class="text-h3 font-weight-bold text-blue">{{ managerData.team_stats.total_goals }}</div>
                  <div class="text-caption text-grey">Total Goals</div>
                </v-col>
                <v-col cols="6" class="text-center">
                  <div class="text-h3 font-weight-bold text-orange">{{ managerData.team_stats.average_rating }}</div>
                  <div class="text-caption text-grey">Avg Rating</div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <v-card elevation="2">
            <v-card-title class="bg-orange">
              <v-icon left color="white">mdi-clipboard-alert</v-icon>
              <span class="text-white">Pending Reviews ({{ managerData.pending_reviews.length }})</span>
            </v-card-title>
            <v-card-text class="pa-0">
              <v-list v-if="managerData.pending_reviews.length > 0">
                <v-list-item
                  v-for="review in managerData.pending_reviews"
                  :key="review.id"
                  :to="`/manager/team-reviews`"
                  class="border-b"
                >
                  <v-list-item-title>{{ review.employee_name }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ formatReviewType(review.review_type) }} - {{ formatStatus(review.status) }}
                  </v-list-item-subtitle>
                  <template v-slot:append>
                    <v-icon color="primary">mdi-chevron-right</v-icon>
                  </template>
                </v-list-item>
              </v-list>
              <div v-else class="pa-6 text-center text-grey">
                <v-icon size="48" color="grey-lighten-1">mdi-check-circle</v-icon>
                <p class="mt-2">No pending reviews</p>
              </div>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" variant="text" to="/manager/team-reviews" block>
                View All Reviews
                <v-icon right>mdi-arrow-right</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card elevation="2">
            <v-card-title class="bg-green">
              <v-icon left color="white">mdi-account-multiple</v-icon>
              <span class="text-white">Team Members</span>
            </v-card-title>
            <v-card-text class="pa-0">
              <v-list v-if="managerData.team_members && managerData.team_members.length > 0">
                <v-list-item
                  v-for="member in managerData.team_members"
                  :key="member.id"
                  class="border-b"
                >
                  <template v-slot:prepend>
                    <v-avatar color="primary">
                      <span class="white--text">{{ getInitials(member.full_name) }}</span>
                    </v-avatar>
                  </template>
                  <v-list-item-title>{{ member.full_name }}</v-list-item-title>
                  <v-list-item-subtitle>{{ member.position || 'No Position' }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
              <div v-else class="pa-6 text-center text-grey">
                <v-icon size="48" color="grey-lighten-1">mdi-account-off</v-icon>
                <p class="mt-2">No team members assigned</p>
              </div>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" variant="text" to="/manager/team-goals" block>
                View Team Goals
                <v-icon right>mdi-arrow-right</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- HR Dashboard -->
    <template v-if="isHR && hrData">
      <v-row>
        <v-col cols="12" md="8">
          <v-card elevation="2" class="mb-4">
            <v-card-title class="bg-primary">
              <v-icon left color="white">mdi-chart-line</v-icon>
              <span class="text-white">Department Performance</span>
            </v-card-title>
            <v-card-text>
              <v-data-table
                :headers="departmentHeaders"
                :items="Array.isArray(hrData.department_performance) ? hrData.department_performance : []"
                :items-per-page="5"
                density="compact"
                class="elevation-0"
              >
                <template v-slot:item.performance_score="{ item }">
                  <div class="d-flex align-center">
                    <v-progress-circular
                      :model-value="item.performance_score"
                      size="35"
                      width="4"
                      color="primary"
                      class="mr-2"
                    >
                      <span class="text-caption">{{ item.performance_score }}</span>
                    </v-progress-circular>
                  </div>
                </template>

                <template v-slot:item.goal_completion="{ item }">
                  <div class="d-flex align-center">
                    <v-progress-linear
                      :model-value="item.goal_completion"
                      color="success"
                      height="8"
                      rounded
                      class="mr-2"
                      style="min-width: 80px"
                    />
                    <span class="text-caption">{{ item.goal_completion }}%</span>
                  </div>
                </template>

                <template v-slot:item.avg_rating="{ item }">
                  <v-chip color="blue" size="small">
                    <v-icon left size="small">mdi-star</v-icon>
                    {{ item.avg_rating }}/5
                  </v-chip>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>

          <v-card elevation="2">
            <v-card-title class="bg-blue">
              <v-icon left color="white">mdi-clock-outline</v-icon>
              <span class="text-white">Recent Activity</span>
            </v-card-title>
            <v-card-text>
              <v-timeline density="compact" v-if="Array.isArray(hrData.recent_activity) && hrData.recent_activity.length > 0">
                <v-timeline-item
                  v-for="activity in hrData.recent_activity.slice(0, 8)"
                  :key="activity.id + activity.type"
                  :dot-color="activity.color"
                  size="small"
                >
                  <div class="text-body-2">{{ activity.description }}</div>
                  <div class="text-caption text-grey">{{ formatDateTime(activity.timestamp) }}</div>
                </v-timeline-item>
              </v-timeline>
              <div v-else class="pa-4 text-center text-grey">
                <p>No recent activity</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card elevation="2" class="mb-4">
            <v-card-title class="bg-error">
              <v-icon left color="white">mdi-alert</v-icon>
              <span class="text-white">Alerts & Notifications</span>
            </v-card-title>
            <v-card-text class="pa-0">
              <v-list v-if="Array.isArray(hrData.alerts) && hrData.alerts.length > 0">
                <v-list-item
                  v-for="(alert, index) in hrData.alerts"
                  :key="'alert-' + index"
                  class="border-b"
                >
                  <template v-slot:prepend>
                    <v-icon :color="alert.color">{{ alert.icon }}</v-icon>
                  </template>
                  <v-list-item-title class="font-weight-medium">{{ alert.title }}</v-list-item-title>
                  <v-list-item-subtitle>{{ alert.message }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
              <div v-else class="pa-6 text-center text-grey">
                <v-icon size="48" color="grey-lighten-1">mdi-check-circle</v-icon>
                <p class="mt-2">No alerts</p>
              </div>
            </v-card-text>
          </v-card>

          <v-card elevation="2">
            <v-card-title class="bg-green">
              <v-icon left color="white">mdi-speedometer</v-icon>
              <span class="text-white">Quick Actions</span>
            </v-card-title>
            <v-card-text class="pa-2">
              <v-list density="compact">
                <v-list-item to="/hr/employees" prepend-icon="mdi-account-multiple">
                  <v-list-item-title>Manage Employees</v-list-item-title>
                </v-list-item>
                <v-list-item to="/hr/reports" prepend-icon="mdi-file-chart">
                  <v-list-item-title>Generate Report</v-list-item-title>
                </v-list-item>
                <v-list-item to="/hr/cycles" prepend-icon="mdi-calendar-clock">
                  <v-list-item-title>Manage Cycles</v-list-item-title>
                </v-list-item>
                <v-list-item to="/hr/analytics" prepend-icon="mdi-chart-line">
                  <v-list-item-title>View Analytics</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Loading State -->
    <v-row v-if="loading && !quickStats.length">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        />
        <p class="mt-4 text-grey">Loading dashboard...</p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { analyticsAPI } from '@/api/analytics'
import { useToast } from 'vue-toastification'

const authStore = useAuthStore()
const toast = useToast()

// Computed properties
const user = computed(() => authStore.user)
const isEmployee = computed(() => authStore.isEmployee)
const isManager = computed(() => authStore.isManager)
const isHR = computed(() => authStore.isHR)

const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

// Reactive data
const loading = ref(false)
const quickStats = ref([])
const employeeData = ref(null)
const managerData = ref(null)
const hrData = ref({
  department_performance: [],
  recent_activity: [],
  alerts: []
})

// Department table headers
const departmentHeaders = [
  { title: 'Department', key: 'name', sortable: true },
  { title: 'Employees', key: 'employee_count', sortable: true },
  { title: 'Score', key: 'performance_score', sortable: true },
  { title: 'Goal Completion', key: 'goal_completion', sortable: true },
  { title: 'Rating', key: 'avg_rating', sortable: true }
]

// Methods
const loadDashboardData = async () => {
  try {
    loading.value = true
    
    // Load general stats
    const statsResponse = await analyticsAPI.getDashboardStats()
    quickStats.value = [
      { 
        title: 'Active Goals', 
        value: statsResponse.data.active_goals || 0,
        subtitle: 'In Progress',
        icon: 'mdi-target',
        iconColor: 'primary',
        colorClass: 'stat-primary',
        trend: 12
      },
      { 
        title: 'Pending Reviews', 
        value: statsResponse.data.pending_reviews || 0,
        subtitle: 'Awaiting Action',
        icon: 'mdi-clipboard-text',
        iconColor: 'warning',
        colorClass: 'stat-warning',
        trend: -5
      },
      { 
        title: 'Feedback Received', 
        value: statsResponse.data.feedback_received || 0,
        subtitle: 'This Month',
        icon: 'mdi-comment-text',
        iconColor: 'success',
        colorClass: 'stat-success',
        trend: 8
      },
      { 
        title: 'Completion Rate', 
        value: `${statsResponse.data.completion_rate || 0}%`,
        subtitle: 'Overall Performance',
        icon: 'mdi-chart-line',
        iconColor: 'info',
        colorClass: 'stat-info',
        trend: 15
      }
    ]
    
    // Load role-specific data
    if (isEmployee.value) {
      const empResponse = await analyticsAPI.getEmployeeStats()
      employeeData.value = empResponse.data
    }
    
    if (isManager.value) {
      const mgrResponse = await analyticsAPI.getManagerStats()
      managerData.value = mgrResponse.data
    }
    
    if (isHR.value) {
      const hrResponse = await analyticsAPI.getHRStats()
      hrData.value = hrResponse.data
    }
  } catch (error) {
    console.error('Error loading dashboard data:', error)
    
    // Handle specific error cases
    if (error.response?.status === 400) {
      console.warn('Dashboard data not available:', error.response.data)
      // Don't show error popup for 400 - this might be expected
    } else {
      toast.error('Failed to load dashboard data')
    }
  } finally {
    loading.value = false
  }
}

const refreshDashboard = async () => {
  toast.info('Refreshing dashboard...')
  await loadDashboardData()
  toast.success('Dashboard refreshed')
}

const getGoalStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    submitted: 'orange',
    approved: 'blue',
    in_progress: 'primary',
    completed: 'green',
    cancelled: 'red',
    overdue: 'red'
  }
  return colors[status] || 'grey'
}

const formatStatus = (status) => {
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatReviewType = (type) => {
  return type.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hours ago`
  if (diffDays < 7) return `${diffDays} days ago`
  
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const getInitials = (name) => {
  if (!name) return '?'
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
}

// Lifecycle
onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
/* Dashboard Container */
.dashboard-container {
  background: linear-gradient(180deg, #F8FAFC 0%, #FFFFFF 100%);
  min-height: 100vh;
  padding: 24px;
}

/* Header Styling */
.dashboard-header {
  background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 24px;
}

.welcome-section {
  flex: 1;
}

.dashboard-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #0F172A;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.welcome-text {
  font-size: 1.25rem;
  color: #64748B;
  margin-bottom: 4px;
}

.user-name {
  color: #2563EB;
  font-weight: 600;
}

.date-text {
  font-size: 0.875rem;
  color: #94A3B8;
  margin: 0;
}

.refresh-btn {
  background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
}

/* Stats Row */
.stats-row {
  margin-bottom: 32px;
}

/* Modern Stat Cards */
.modern-stat-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border: 1px solid rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: relative;
}

.modern-stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.modern-stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #2563EB, #1D4ED8);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.modern-stat-card:hover::before {
  opacity: 1;
}

.stat-content {
  padding: 24px;
  position: relative;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stat-icon-container {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(37, 99, 235, 0.1);
  transition: all 0.3s ease;
}

.modern-stat-card:hover .stat-icon-container {
  transform: scale(1.1);
  background: rgba(37, 99, 235, 0.15);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.trend-text {
  font-size: 0.75rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #0F172A;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-title {
  font-size: 1rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 4px;
}

.stat-subtitle {
  font-size: 0.875rem;
  color: #94A3B8;
  margin: 0;
}

/* Stat Card Color Variants */
.stat-primary {
  background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
  border-color: rgba(37, 99, 235, 0.2);
}

.stat-primary .stat-icon-container {
  background: rgba(37, 99, 235, 0.1);
}

.stat-warning {
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-color: rgba(245, 158, 11, 0.2);
}

.stat-warning .stat-icon-container {
  background: rgba(245, 158, 11, 0.1);
}

.stat-success {
  background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
  border-color: rgba(16, 185, 129, 0.2);
}

.stat-success .stat-icon-container {
  background: rgba(16, 185, 129, 0.1);
}

.stat-info {
  background: linear-gradient(135deg, #CFFAFE 0%, #A5F3FC 100%);
  border-color: rgba(6, 182, 212, 0.2);
}

.stat-info .stat-icon-container {
  background: rgba(6, 182, 212, 0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }
  
  .dashboard-header {
    padding: 24px;
    margin-bottom: 24px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .dashboard-title {
    font-size: 2rem;
  }
  
  .stat-content {
    padding: 20px;
  }
  
  .stat-value {
    font-size: 2rem;
  }
}

/* Smooth Animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modern-stat-card {
  animation: fadeInUp 0.6s ease-out;
}

.modern-stat-card:nth-child(1) { animation-delay: 0.1s; }
.modern-stat-card:nth-child(2) { animation-delay: 0.2s; }
.modern-stat-card:nth-child(3) { animation-delay: 0.3s; }
.modern-stat-card:nth-child(4) { animation-delay: 0.4s; }
</style>
