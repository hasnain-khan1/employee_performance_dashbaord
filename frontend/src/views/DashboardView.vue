<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">Dashboard</h1>
      </v-col>
    </v-row>

    <!-- Welcome Section -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-account</v-icon>
            Welcome, {{ user?.full_name || 'User' }}!
          </v-card-title>
          <v-card-text>
            <p class="text-body-1">
              Welcome to the Employee Performance Management System. 
              Here's an overview of your current status and upcoming tasks.
            </p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Stats -->
    <v-row>
      <v-col cols="12" md="3" v-for="stat in quickStats" :key="stat.title">
        <v-card :color="stat.color" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">{{ stat.icon }}</v-icon>
              <div>
                <div class="text-h4">{{ stat.value }}</div>
                <div class="text-body-2">{{ stat.title }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Employee Dashboard -->
    <template v-if="isEmployee">
      <v-row>
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>
              <v-icon left>mdi-target</v-icon>
              My Goals
            </v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item
                  v-for="goal in recentGoals"
                  :key="goal.id"
                  :to="`/employee/goals/${goal.id}`"
                >
                  <v-list-item-title>{{ goal.title }}</v-list-item-title>
                  <v-list-item-subtitle>
                    Progress: {{ goal.progress_percentage }}%
                  </v-list-item-subtitle>
                  <template v-slot:append>
                    <v-chip
                      :color="getGoalStatusColor(goal.status)"
                      size="small"
                    >
                      {{ goal.status }}
                    </v-chip>
                  </template>
                </v-list-item>
              </v-list>
              <v-btn
                color="primary"
                variant="outlined"
                block
                class="mt-4"
                to="/employee/goals"
              >
                View All Goals
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>
              <v-icon left>mdi-calendar-clock</v-icon>
              Current Review Cycle
            </v-card-title>
            <v-card-text>
              <div v-if="currentCycle">
                <h3>{{ currentCycle.name }}</h3>
                <p class="text-body-2">{{ currentCycle.description }}</p>
                <v-progress-linear
                  :model-value="currentCycle.completion_percentage"
                  color="primary"
                  height="8"
                  class="mt-2"
                />
                <div class="text-caption mt-1">
                  {{ currentCycle.completion_percentage }}% Complete
                </div>
              </div>
              <div v-else>
                <p class="text-body-2">No active review cycle</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Manager Dashboard -->
    <template v-if="isManager">
      <v-row>
        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>
              <v-icon left>mdi-account-group</v-icon>
              Team Overview
            </v-card-title>
            <v-card-text>
              <div class="text-h4">{{ teamStats.totalMembers }}</div>
              <div class="text-body-2">Team Members</div>
              <v-divider class="my-4" />
              <div class="text-h4">{{ teamStats.goalsCompleted }}</div>
              <div class="text-body-2">Goals Completed</div>
            </v-card-text>
          </v-card>

          <v-card class="mt-4">
            <v-card-title>
              <v-icon left>mdi-clipboard-text</v-icon>
              Pending Reviews
            </v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item
                  v-for="review in pendingReviews"
                  :key="review.id"
                  :to="`/manager/team-reviews/${review.id}`"
                >
                  <v-list-item-title>{{ review.employee_name }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ review.review_type }} - {{ review.status }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card>
            <v-card-title>
              <v-icon left>mdi-chart-line</v-icon>
              Team Performance
            </v-card-title>
            <v-card-text>
              <div class="text-center">
                <v-progress-circular
                  :model-value="teamStats.averageRating * 20"
                  size="100"
                  width="8"
                  color="primary"
                >
                  {{ teamStats.averageRating }}/5
                </v-progress-circular>
                <div class="text-body-2 mt-2">Average Rating</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- HR Dashboard -->
    <template v-if="isHR">
      <v-row>
        <v-col cols="12" md="3" v-for="stat in hrStats" :key="stat.title">
          <v-card>
            <v-card-text>
              <div class="text-h4">{{ stat.value }}</div>
              <div class="text-body-2">{{ stat.title }}</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

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
              <v-icon left>mdi-alert</v-icon>
              Alerts
            </v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item
                  v-for="alert in alerts"
                  :key="alert.id"
                >
                  <v-list-item-title>{{ alert.title }}</v-list-item-title>
                  <v-list-item-subtitle>{{ alert.message }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()

// Computed properties
const user = computed(() => authStore.user)
const isEmployee = computed(() => authStore.isEmployee)
const isManager = computed(() => authStore.isManager)
const isHR = computed(() => authStore.isHR)

// Mock data - in real app, this would come from API
const quickStats = ref([
  { title: 'Active Goals', value: '5', icon: 'mdi-target', color: 'primary' },
  { title: 'Pending Reviews', value: '2', icon: 'mdi-clipboard-text', color: 'orange' },
  { title: 'Feedback Received', value: '8', icon: 'mdi-comment-text', color: 'green' },
  { title: 'Completion Rate', value: '85%', icon: 'mdi-chart-line', color: 'blue' }
])

const recentGoals = ref([
  { id: 1, title: 'Improve Sales Performance', progress_percentage: 75, status: 'in_progress' },
  { id: 2, title: 'Complete Training Course', progress_percentage: 100, status: 'completed' },
  { id: 3, title: 'Lead Team Project', progress_percentage: 45, status: 'in_progress' }
])

const currentCycle = ref({
  name: 'Q4 2024 Review Cycle',
  description: 'End of year performance review',
  completion_percentage: 65
})

const teamStats = ref({
  totalMembers: 12,
  goalsCompleted: 8,
  averageRating: 4.2
})

const pendingReviews = ref([
  { id: 1, employee_name: 'John Doe', review_type: 'Self Review', status: 'pending' },
  { id: 2, employee_name: 'Jane Smith', review_type: 'Manager Review', status: 'in_progress' }
])

const hrStats = ref([
  { title: 'Total Employees', value: '150' },
  { title: 'Active Cycles', value: '3' },
  { title: 'Completed Reviews', value: '120' },
  { title: 'Pending Feedback', value: '25' }
])

const alerts = ref([
  { id: 1, title: 'Review Cycle Ending', message: 'Q4 2024 cycle ends in 5 days' },
  { id: 2, title: 'Goal Approval Needed', message: '5 goals pending approval' }
])

// Methods
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

// Lifecycle
onMounted(() => {
  // Load dashboard data
  console.log('Dashboard loaded for user:', user.value)
})
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}
</style>