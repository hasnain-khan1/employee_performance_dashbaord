<template>
  <v-container fluid>
    <!-- Header -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between mb-6">
          <div>
            <h1 class="text-h4 font-weight-bold">
              <v-icon size="large" color="primary" class="mr-2">mdi-view-dashboard</v-icon>
              Dashboard
            </h1>
            <p class="text-subtitle-1 text-grey mt-2">
              Welcome back, {{ user?.full_name || 'User' }}!
            </p>
          </div>
          <v-btn
            color="primary"
            prepend-icon="mdi-refresh"
            @click="refreshDashboard"
            :loading="loading"
          >
            Refresh
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Quick Stats -->
    <v-row v-if="quickStats.length > 0">
      <v-col cols="12" sm="6" md="3" v-for="(stat, index) in quickStats" :key="'stat-' + index">
        <v-card class="stat-card" :class="stat.color" elevation="2">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <div class="text-h3 font-weight-bold white--text">{{ stat.value }}</div>
                <div class="text-subtitle-2 white--text mt-1">{{ stat.title }}</div>
              </div>
              <v-avatar :color="stat.iconBg || 'white'" size="60">
                <v-icon :color="stat.color" size="30">{{ stat.icon }}</v-icon>
              </v-avatar>
            </div>
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
                :items="hrData.department_performance || []"
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
              <v-timeline density="compact" v-if="hrData.recent_activity && hrData.recent_activity.length > 0">
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
              <v-list v-if="hrData.alerts && hrData.alerts.length > 0">
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

// Reactive data
const loading = ref(false)
const quickStats = ref([])
const employeeData = ref(null)
const managerData = ref(null)
const hrData = ref(null)

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
        icon: 'mdi-target',
        color: 'bg-primary',
        iconBg: 'rgba(255,255,255,0.3)'
      },
      { 
        title: 'Pending Reviews', 
        value: statsResponse.data.pending_reviews || 0,
        icon: 'mdi-clipboard-text',
        color: 'bg-orange',
        iconBg: 'rgba(255,255,255,0.3)'
      },
      { 
        title: 'Feedback Received', 
        value: statsResponse.data.feedback_received || 0,
        icon: 'mdi-comment-text',
        color: 'bg-green',
        iconBg: 'rgba(255,255,255,0.3)'
      },
      { 
        title: 'Completion Rate', 
        value: `${statsResponse.data.completion_rate || 0}%`,
        icon: 'mdi-chart-line',
        color: 'bg-blue',
        iconBg: 'rgba(255,255,255,0.3)'
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
    toast.error('Failed to load dashboard data')
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
.stat-card {
  border-radius: 12px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.border-b {
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.bg-primary {
  background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
}

.bg-orange {
  background: linear-gradient(135deg, #FF6F00 0%, #F57C00 100%);
}

.bg-green {
  background: linear-gradient(135deg, #388E3C 0%, #2E7D32 100%);
}

.bg-blue {
  background: linear-gradient(135deg, #0288D1 0%, #0277BD 100%);
}

.bg-error {
  background: linear-gradient(135deg, #D32F2F 0%, #C62828 100%);
}
</style>
