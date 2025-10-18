<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-6">
          <h1 class="text-h4">Analytics Dashboard</h1>
          <v-btn 
            color="primary" 
            @click="refreshData"
            :loading="loading"
            prepend-icon="mdi-refresh"
          >
            Refresh
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Key Metrics -->
    <v-row>
      <v-col cols="12" md="3" v-for="metric in keyMetrics" :key="metric.title">
        <v-card :color="metric.color" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">{{ metric.icon }}</v-icon>
              <div>
                <div class="text-h4">{{ metric.value }}</div>
                <div class="text-body-2">{{ metric.title }}</div>
                <div class="text-caption">{{ metric.change }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts Row -->
    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-chart-line</v-icon>
            Performance Trends
          </v-card-title>
          <v-card-text>
            <div class="text-center pa-8">
              <v-icon size="64" color="grey">mdi-chart-line</v-icon>
              <p class="text-body-2 mt-2">Performance trends chart will be displayed here</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-chart-pie</v-icon>
            Goal Distribution
          </v-card-title>
          <v-card-text>
            <div class="text-center pa-8">
              <v-icon size="64" color="grey">mdi-chart-pie</v-icon>
              <p class="text-body-2 mt-2">Goal distribution chart will be displayed here</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Department Performance -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-office-building</v-icon>
            Department Performance
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="departmentHeaders"
              :items="Array.isArray(departmentData) ? departmentData : []"
              :loading="loading"
              :items-per-page="10"
              class="elevation-1"
            >
              <template v-slot:item.performance_score="{ item }">
                <div class="d-flex align-center">
                  <v-progress-circular
                    :model-value="item.performance_score"
                    size="40"
                    width="4"
                    color="primary"
                    class="mr-3"
                  >
                    {{ item.performance_score }}
                  </v-progress-circular>
                  <span>{{ item.performance_score }}/100</span>
                </div>
              </template>

              <template v-slot:item.goal_completion="{ item }">
                <div class="d-flex align-center">
                  <v-progress-linear
                    :model-value="item.goal_completion"
                    color="primary"
                    height="6"
                    class="mr-2"
                    style="width: 60px"
                  />
                  <span class="text-caption">{{ item.goal_completion }}%</span>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Activity -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-clock-outline</v-icon>
            Recent Activity
          </v-card-title>
          <v-card-text>
            <v-timeline>
              <v-timeline-item
                v-for="activity in recentActivity"
                :key="activity.id"
                :dot-color="activity.color"
                size="small"
              >
                <div class="text-body-2">{{ activity.description }}</div>
                <div class="text-caption text-grey">{{ activity.timestamp }}</div>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-alert</v-icon>
            Alerts & Notifications
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="alert in alerts"
                :key="alert.id"
              >
                <template v-slot:prepend>
                  <v-icon :color="alert.color">{{ alert.icon }}</v-icon>
                </template>
                <v-list-item-title>{{ alert.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ alert.message }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { analyticsAPI } from '@/api/analytics'

const toast = useToast()

// Reactive data
const loading = ref(false)
const keyMetrics = ref([])
const departmentData = ref([])
const recentActivity = ref([])
const alerts = ref([])

const departmentHeaders = [
  { title: 'Department', key: 'name', sortable: true },
  { title: 'Employees', key: 'employee_count', sortable: true },
  { title: 'Performance Score', key: 'performance_score', sortable: true },
  { title: 'Goal Completion', key: 'goal_completion', sortable: true },
  { title: 'Avg Rating', key: 'avg_rating', sortable: true }
]

// Methods
const loadAnalyticsData = async () => {
  try {
    loading.value = true
    
    // Load HR dashboard statistics
    const response = await analyticsAPI.getHRStats()
    const data = response.data
    
    // Update key metrics
    keyMetrics.value = [
      { 
        title: 'Total Employees', 
        value: data.stats?.total_employees || 0, 
        change: 'Active employees', 
        icon: 'mdi-account-group', 
        color: 'primary' 
      },
      { 
        title: 'Active Cycles', 
        value: data.stats?.active_cycles || 0, 
        change: 'Review cycles', 
        icon: 'mdi-calendar-clock', 
        color: 'blue' 
      },
      { 
        title: 'Completed Reviews', 
        value: data.stats?.completed_reviews || 0, 
        change: 'Manager reviews', 
        icon: 'mdi-clipboard-check', 
        color: 'green' 
      },
      { 
        title: 'Pending Feedback', 
        value: data.stats?.pending_feedback || 0, 
        change: 'Awaiting response', 
        icon: 'mdi-comment-text', 
        color: 'orange' 
      }
    ]
    
    // Update department data
    departmentData.value = data.department_performance || []
    
    // Update recent activity
    recentActivity.value = data.recent_activity || []
    
    // Update alerts
    alerts.value = data.alerts || []
    
  } catch (error) {
    console.error('Error loading analytics data:', error)
    toast.error('Failed to load analytics data')
    
    // Fallback to empty data
    keyMetrics.value = [
      { title: 'Total Employees', value: 0, change: 'No data', icon: 'mdi-account-group', color: 'primary' },
      { title: 'Active Cycles', value: 0, change: 'No data', icon: 'mdi-calendar-clock', color: 'blue' },
      { title: 'Completed Reviews', value: 0, change: 'No data', icon: 'mdi-clipboard-check', color: 'green' },
      { title: 'Pending Feedback', value: 0, change: 'No data', icon: 'mdi-comment-text', color: 'orange' }
    ]
    departmentData.value = []
    recentActivity.value = []
    alerts.value = []
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  toast.info('Refreshing analytics data...')
  await loadAnalyticsData()
  toast.success('Analytics data refreshed')
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

// Lifecycle
onMounted(() => {
  loadAnalyticsData()
})
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}
</style>