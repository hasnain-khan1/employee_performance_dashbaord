<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">Analytics Dashboard</h1>
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
              :items="departmentData"
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

// Reactive data
const loading = ref(false)

const keyMetrics = ref([
  { title: 'Total Employees', value: '150', change: '+5 this month', icon: 'mdi-account-group', color: 'primary' },
  { title: 'Active Goals', value: '420', change: '+12 this week', icon: 'mdi-target', color: 'blue' },
  { title: 'Completed Reviews', value: '95%', change: '+3% vs last cycle', icon: 'mdi-clipboard-check', color: 'green' },
  { title: 'Avg Performance', value: '4.2/5', change: '+0.3 vs last cycle', icon: 'mdi-star', color: 'orange' }
])

const departmentHeaders = [
  { title: 'Department', key: 'name', sortable: true },
  { title: 'Employees', key: 'employee_count', sortable: true },
  { title: 'Performance Score', key: 'performance_score', sortable: true },
  { title: 'Goal Completion', key: 'goal_completion', sortable: true },
  { title: 'Avg Rating', key: 'avg_rating', sortable: true }
]

const departmentData = ref([
  { name: 'Engineering', employee_count: 45, performance_score: 85, goal_completion: 78, avg_rating: 4.2 },
  { name: 'Sales', employee_count: 25, performance_score: 92, goal_completion: 85, avg_rating: 4.5 },
  { name: 'Marketing', employee_count: 15, performance_score: 78, goal_completion: 72, avg_rating: 3.9 },
  { name: 'HR', employee_count: 8, performance_score: 88, goal_completion: 90, avg_rating: 4.3 }
])

const recentActivity = ref([
  { id: 1, description: 'John Doe completed Q4 review', timestamp: '2 hours ago', color: 'green' },
  { id: 2, description: 'Jane Smith submitted new goal', timestamp: '4 hours ago', color: 'blue' },
  { id: 3, description: 'Mike Johnson requested feedback', timestamp: '6 hours ago', color: 'orange' },
  { id: 4, description: 'Sarah Wilson approved team goals', timestamp: '1 day ago', color: 'purple' }
])

const alerts = ref([
  { id: 1, title: 'Review Cycle Ending', message: 'Q4 2024 cycle ends in 5 days', icon: 'mdi-clock-alert', color: 'orange' },
  { id: 2, title: 'Goal Approval Needed', message: '15 goals pending approval', icon: 'mdi-target', color: 'blue' },
  { id: 3, title: 'Performance Alert', message: '3 employees below target', icon: 'mdi-alert', color: 'red' }
])

// Methods
const loadAnalyticsData = async () => {
  try {
    loading.value = true
    // Load analytics data from API
    console.log('Loading analytics data...')
  } catch (error) {
    console.error('Error loading analytics data:', error)
  } finally {
    loading.value = false
  }
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