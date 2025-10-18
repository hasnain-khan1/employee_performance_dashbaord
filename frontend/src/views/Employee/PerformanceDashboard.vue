<template>
  <v-container fluid>
    <!-- Header with Employee Info -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card elevation="2" color="primary" variant="tonal">
          <v-card-text class="d-flex align-center">
            <v-avatar size="64" class="mr-4">
              <v-img
                :src="user?.avatar || '/default-avatar.png'"
                :alt="user?.full_name"
              />
            </v-avatar>
            <div class="flex-grow-1">
              <h2 class="text-h4 font-weight-bold mb-2">
                Welcome back, {{ user?.first_name || 'Employee' }}!
              </h2>
              <p class="text-subtitle-1 mb-0">
                Track your performance review progress and stay on top of deadlines
              </p>
            </div>
            <div class="text-right">
              <v-chip
                :color="getOverallStatusColor()"
                size="large"
                variant="elevated"
                class="mb-2"
              >
                {{ getOverallStatusText() }}
              </v-chip>
              <div class="text-caption">
                Last updated: {{ formatTime(lastUpdated) }}
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Progress Overview Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="success" variant="tonal" class="h-100">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-2">mdi-target</v-icon>
            <div class="text-h4 font-weight-bold">{{ progressData.goals_completion }}%</div>
            <div class="text-subtitle-2">Goals Progress</div>
            <v-progress-linear
              :model-value="progressData.goals_completion"
              color="success"
              height="8"
              rounded
              class="mt-2"
            />
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="info" variant="tonal" class="h-100">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-2">mdi-clipboard-text</v-icon>
            <div class="text-h4 font-weight-bold">{{ progressData.self_review_completion }}%</div>
            <div class="text-subtitle-2">Self Review</div>
            <v-progress-linear
              :model-value="progressData.self_review_completion"
              color="info"
              height="8"
              rounded
              class="mt-2"
            />
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="warning" variant="tonal" class="h-100">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-2">mdi-account-group</v-icon>
            <div class="text-h4 font-weight-bold">{{ progressData.peer_feedback_completion }}%</div>
            <div class="text-subtitle-2">Peer Feedback</div>
            <v-progress-linear
              :model-value="progressData.peer_feedback_completion"
              color="warning"
              height="8"
              rounded
              class="mt-2"
            />
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="primary" variant="tonal" class="h-100">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-2">mdi-chart-line</v-icon>
            <div class="text-h4 font-weight-bold">{{ progressData.overall_completion }}%</div>
            <div class="text-subtitle-2">Overall Progress</div>
            <v-progress-linear
              :model-value="progressData.overall_completion"
              color="primary"
              height="8"
              rounded
              class="mt-2"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Deadline Alerts -->
    <v-row class="mb-6" v-if="urgentDeadlines.length > 0">
      <v-col cols="12">
        <v-alert
          type="error"
          variant="tonal"
          prominent
          border="start"
        >
          <template #title>
            <div class="d-flex align-center">
              <v-icon class="mr-2">mdi-alert-circle</v-icon>
              Urgent Deadlines
            </div>
          </template>
          <div class="mt-2">
            <v-list density="compact">
              <v-list-item
                v-for="deadline in urgentDeadlines"
                :key="deadline.id"
                class="mb-2"
              >
                <template #prepend>
                  <v-icon color="error">mdi-clock-alert</v-icon>
                </template>
                <v-list-item-title>{{ deadline.title }}</v-list-item-title>
                <v-list-item-subtitle>
                  Due: {{ formatDate(deadline.due_date) }} 
                  ({{ getDaysUntilDeadline(deadline.due_date) }} days)
                </v-list-item-subtitle>
                <template #append>
                  <v-btn
                    color="error"
                    variant="outlined"
                    size="small"
                    @click="handleUrgentAction(deadline)"
                  >
                    {{ deadline.action_text }}
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>
          </div>
        </v-alert>
      </v-col>
    </v-row>

    <!-- Action Items -->
    <v-row class="mb-6">
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-format-list-checks</v-icon>
            Action Items
            <v-spacer />
            <v-chip
              :color="getActionItemsStatusColor()"
              size="small"
              variant="tonal"
            >
              {{ actionItems.length }} items
            </v-chip>
          </v-card-title>
          
          <v-card-text>
            <v-list v-if="actionItems.length > 0" density="comfortable">
              <v-list-item
                v-for="item in actionItems"
                :key="item.id"
                class="mb-2"
                :class="{ 'bg-warning-lighten-5': item.priority === 'high' }"
              >
                <template #prepend>
                  <v-icon
                    :color="getPriorityColor(item.priority)"
                    :icon="getPriorityIcon(item.priority)"
                  />
                </template>
                
                <v-list-item-title>{{ item.title }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ item.description }} | 
                  Due: {{ formatDate(item.due_date) }}
                  <span v-if="item.estimated_time" class="ml-2">
                    ({{ item.estimated_time }} min)
                  </span>
                </v-list-item-subtitle>
                
                <template #append>
                  <div class="d-flex align-center">
                    <v-chip
                      :color="getStatusColor(item.status)"
                      size="small"
                      variant="tonal"
                      class="mr-2"
                    >
                      {{ item.status }}
                    </v-chip>
                    <v-btn
                      :color="getActionButtonColor(item.status)"
                      variant="outlined"
                      size="small"
                      @click="handleActionItem(item)"
                    >
                      {{ getActionButtonText(item.status) }}
                    </v-btn>
                  </div>
                </template>
              </v-list-item>
            </v-list>
            
            <v-empty-state
              v-else
              title="All caught up!"
              subtitle="No pending action items"
              icon="mdi-check-circle"
            />
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Quick Stats -->
      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-chart-donut</v-icon>
            Quick Stats
          </v-card-title>
          
          <v-card-text>
            <v-list density="compact">
              <v-list-item>
                <template #prepend>
                  <v-icon color="success">mdi-check-circle</v-icon>
                </template>
                <v-list-item-title>Completed</v-list-item-title>
                <v-list-item-subtitle>{{ completedItems }} items</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template #prepend>
                  <v-icon color="warning">mdi-clock</v-icon>
                </template>
                <v-list-item-title>In Progress</v-list-item-title>
                <v-list-item-subtitle>{{ inProgressItems }} items</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template #prepend>
                  <v-icon color="error">mdi-alert</v-icon>
                </template>
                <v-list-item-title>Overdue</v-list-item-title>
                <v-list-item-subtitle>{{ overdueItems }} items</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template #prepend>
                  <v-icon color="info">mdi-calendar</v-icon>
                </template>
                <v-list-item-title>Upcoming</v-list-item-title>
                <v-list-item-subtitle>{{ upcomingItems }} items</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Activity -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-history</v-icon>
            Recent Activity
            <v-spacer />
            <v-btn
              icon="mdi-refresh"
              variant="text"
              @click="refreshActivity"
              :loading="refreshingActivity"
            />
          </v-card-title>
          
          <v-card-text>
            <v-timeline v-if="recentActivity.length > 0" density="compact">
              <v-timeline-item
                v-for="activity in recentActivity"
                :key="activity.id"
                :dot-color="getActivityColor(activity.type)"
                size="small"
              >
                <template #icon>
                  <v-icon :color="getActivityColor(activity.type)">
                    {{ getActivityIcon(activity.type) }}
                  </v-icon>
                </template>
                
                <div class="d-flex align-center justify-space-between">
                  <div>
                    <div class="font-weight-medium">{{ activity.title }}</div>
                    <div class="text-caption text-medium-emphasis">
                      {{ activity.description }}
                    </div>
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ formatTime(activity.timestamp) }}
                  </div>
                </div>
              </v-timeline-item>
            </v-timeline>
            
            <v-empty-state
              v-else
              title="No recent activity"
              subtitle="Your activity will appear here"
              icon="mdi-clock-outline"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Offline Indicator -->
    <v-snackbar
      v-model="showOfflineIndicator"
      color="warning"
      timeout="0"
    >
      <template #prepend>
        <v-icon>mdi-wifi-off</v-icon>
      </template>
      <div>
        <strong>Offline Mode</strong><br>
        <span class="text-caption">Data may be outdated. Will sync when connected.</span>
      </div>
      <template #actions>
        <v-btn
          color="white"
          variant="text"
          @click="showOfflineIndicator = false"
        >
          Dismiss
        </v-btn>
      </template>
    </v-snackbar>

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
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useToast } from 'vue-toastification'
import { goalsAPI } from '@/api/goals'
import { feedbackAPI } from '@/api/feedback'
import { reviewsAPI } from '@/api/reviews'

// Composables
const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

// Reactive data
const loading = ref(false)
const refreshingActivity = ref(false)
const showOfflineIndicator = ref(false)
const lastUpdated = ref(new Date())
const refreshInterval = ref(null)

const user = computed(() => authStore.user)

const progressData = ref({
  goals_completion: 0,
  self_review_completion: 0,
  peer_feedback_completion: 0,
  overall_completion: 0
})

const urgentDeadlines = ref([])
const actionItems = ref([])
const recentActivity = ref([])

// Computed properties
const completedItems = computed(() => 
  actionItems.value.filter(item => item.status === 'completed').length
)

const inProgressItems = computed(() => 
  actionItems.value.filter(item => item.status === 'in_progress').length
)

const overdueItems = computed(() => 
  actionItems.value.filter(item => item.status === 'overdue').length
)

const upcomingItems = computed(() => 
  actionItems.value.filter(item => item.status === 'pending').length
)

// Methods
const loadDashboardData = async () => {
  try {
    loading.value = true
    await Promise.all([
      loadProgressData(),
      loadActionItems(),
      loadRecentActivity(),
      checkDeadlines()
    ])
    lastUpdated.value = new Date()
  } catch (error) {
    console.error('Error loading dashboard data:', error)
    toast.error('Failed to load dashboard data')
  } finally {
    loading.value = false
  }
}

const loadProgressData = async () => {
  try {
    // Load goals progress
    const goalsResponse = await goalsAPI.getGoals()
    const goals = goalsResponse.data
    const completedGoals = goals.filter(goal => goal.status === 'completed').length
    progressData.value.goals_completion = goals.length > 0 ? Math.round((completedGoals / goals.length) * 100) : 0

    // Load self-review progress
    const selfReviewResponse = await reviewsAPI.getSelfReviews()
    const selfReviews = selfReviewResponse.data
    if (selfReviews.length > 0) {
      progressData.value.self_review_completion = selfReviews[0].completion_percentage || 0
    }

    // Load peer feedback progress
    const feedbackResponse = await feedbackAPI.getFeedbackStatistics()
    const feedbackStats = feedbackResponse.data
    progressData.value.peer_feedback_completion = feedbackStats.requests_completed || 0

    // Calculate overall completion
    const components = [
      progressData.value.goals_completion,
      progressData.value.self_review_completion,
      progressData.value.peer_feedback_completion
    ]
    progressData.value.overall_completion = Math.round(components.reduce((sum, val) => sum + val, 0) / components.length)
  } catch (error) {
    console.error('Error loading progress data:', error)
  }
}

const loadActionItems = async () => {
  try {
    // This would typically come from a dedicated API endpoint
    // For now, we'll generate mock data based on current state
    const items = []
    
    // Goals action items
    const goalsResponse = await goalsAPI.getGoals()
    const goals = goalsResponse.data
    const incompleteGoals = goals.filter(goal => goal.status !== 'completed')
    
    incompleteGoals.forEach(goal => {
      items.push({
        id: `goal-${goal.id}`,
        title: `Complete Goal: ${goal.title}`,
        description: goal.description,
        due_date: goal.target_date,
        priority: goal.priority === 'high' ? 'high' : 'medium',
        status: goal.status === 'draft' ? 'pending' : 'in_progress',
        type: 'goal',
        action_url: `/employee/goals`
      })
    })

    // Self-review action items
    const selfReviewResponse = await reviewsAPI.getSelfReviews()
    const selfReviews = selfReviewResponse.data
    if (selfReviews.length > 0 && selfReviews[0].completion_percentage < 100) {
      items.push({
        id: 'self-review',
        title: 'Complete Self Review',
        description: 'Finish your self-assessment',
        due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
        priority: 'high',
        status: 'in_progress',
        type: 'self_review',
        action_url: `/employee/self-review`
      })
    }

    // Peer feedback action items
    const feedbackResponse = await feedbackAPI.getFeedbackStatistics()
    const feedbackStats = feedbackResponse.data
    if (feedbackStats.feedback_to_provide > 0) {
      items.push({
        id: 'peer-feedback',
        title: 'Provide Peer Feedback',
        description: `${feedbackStats.feedback_to_provide} feedback requests pending`,
        due_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000), // 3 days from now
        priority: 'medium',
        status: 'pending',
        type: 'peer_feedback',
        action_url: `/employee/peer-feedback`
      })
    }

    actionItems.value = items.sort((a, b) => {
      // Sort by priority and due date
      const priorityOrder = { high: 3, medium: 2, low: 1 }
      if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
        return priorityOrder[b.priority] - priorityOrder[a.priority]
      }
      return new Date(a.due_date) - new Date(b.due_date)
    })
  } catch (error) {
    console.error('Error loading action items:', error)
  }
}

const loadRecentActivity = async () => {
  try {
    // This would typically come from a dedicated API endpoint
    // For now, we'll generate mock data
    const activities = [
      {
        id: 1,
        title: 'Goal Updated',
        description: 'Updated progress on "Increase Sales by 20%"',
        type: 'goal_update',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
      },
      {
        id: 2,
        title: 'Self Review Started',
        description: 'Began working on your self-assessment',
        type: 'self_review_start',
        timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000) // 1 day ago
      },
      {
        id: 3,
        title: 'Peer Feedback Received',
        description: 'Received feedback from John Smith',
        type: 'feedback_received',
        timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000) // 3 days ago
      }
    ]
    
    recentActivity.value = activities
  } catch (error) {
    console.error('Error loading recent activity:', error)
  }
}

const checkDeadlines = () => {
  const now = new Date()
  const urgent = actionItems.value.filter(item => {
    const dueDate = new Date(item.due_date)
    const daysUntil = Math.ceil((dueDate - now) / (1000 * 60 * 60 * 24))
    return daysUntil <= 2 && item.status !== 'completed'
  })
  
  urgentDeadlines.value = urgent.map(item => ({
    id: item.id,
    title: item.title,
    due_date: item.due_date,
    action_text: getActionButtonText(item.status)
  }))
}

const refreshActivity = async () => {
  try {
    refreshingActivity.value = true
    await loadRecentActivity()
    toast.success('Activity refreshed')
  } catch (error) {
    console.error('Error refreshing activity:', error)
    toast.error('Failed to refresh activity')
  } finally {
    refreshingActivity.value = false
  }
}

const handleUrgentAction = (deadline) => {
  const item = actionItems.value.find(i => i.id === deadline.id)
  if (item) {
    handleActionItem(item)
  }
}

const handleActionItem = (item) => {
  if (item.action_url) {
    router.push(item.action_url)
  } else {
    toast.info(`Action for ${item.title} not yet implemented`)
  }
}

// Status helpers
const getOverallStatusColor = () => {
  const completion = progressData.value.overall_completion
  if (completion >= 90) return 'success'
  if (completion >= 70) return 'info'
  if (completion >= 50) return 'warning'
  return 'error'
}

const getOverallStatusText = () => {
  const completion = progressData.value.overall_completion
  if (completion >= 90) return 'Excellent Progress'
  if (completion >= 70) return 'Good Progress'
  if (completion >= 50) return 'On Track'
  return 'Needs Attention'
}

const getActionItemsStatusColor = () => {
  if (overdueItems.value > 0) return 'error'
  if (inProgressItems.value > 0) return 'warning'
  return 'success'
}

const getPriorityColor = (priority) => {
  const colors = { high: 'error', medium: 'warning', low: 'info' }
  return colors[priority] || 'grey'
}

const getPriorityIcon = (priority) => {
  const icons = { high: 'mdi-alert', medium: 'mdi-clock', low: 'mdi-information' }
  return icons[priority] || 'mdi-help'
}

const getStatusColor = (status) => {
  const colors = {
    completed: 'success',
    in_progress: 'info',
    pending: 'warning',
    overdue: 'error'
  }
  return colors[status] || 'grey'
}

const getActionButtonColor = (status) => {
  const colors = {
    completed: 'success',
    in_progress: 'primary',
    pending: 'warning',
    overdue: 'error'
  }
  return colors[status] || 'primary'
}

const getActionButtonText = (status) => {
  const texts = {
    completed: 'View',
    in_progress: 'Continue',
    pending: 'Start',
    overdue: 'Urgent'
  }
  return texts[status] || 'Action'
}

const getActivityColor = (type) => {
  const colors = {
    goal_update: 'success',
    self_review_start: 'info',
    feedback_received: 'warning',
    deadline_approaching: 'error'
  }
  return colors[type] || 'primary'
}

const getActivityIcon = (type) => {
  const icons = {
    goal_update: 'mdi-target',
    self_review_start: 'mdi-clipboard-text',
    feedback_received: 'mdi-account-group',
    deadline_approaching: 'mdi-clock-alert'
  }
  return icons[type] || 'mdi-information'
}

const getDaysUntilDeadline = (dueDate) => {
  const now = new Date()
  const due = new Date(dueDate)
  const diffTime = due - now
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const formatTime = (date) => {
  return new Date(date).toLocaleTimeString()
}

// Auto-refresh functionality
const startAutoRefresh = () => {
  // Refresh every 5 minutes as per requirements
  refreshInterval.value = setInterval(() => {
    loadDashboardData()
  }, 5 * 60 * 1000)
}

const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// Offline detection
const checkOnlineStatus = () => {
  if (!navigator.onLine) {
    showOfflineIndicator.value = true
  } else {
    showOfflineIndicator.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadDashboardData()
  startAutoRefresh()
  checkOnlineStatus()
  
  // Listen for online/offline events
  window.addEventListener('online', checkOnlineStatus)
  window.addEventListener('offline', checkOnlineStatus)
})

onUnmounted(() => {
  stopAutoRefresh()
  window.removeEventListener('online', checkOnlineStatus)
  window.removeEventListener('offline', checkOnlineStatus)
})
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.v-progress-linear {
  border-radius: 4px;
}

.v-timeline-item {
  padding-bottom: 16px;
}

.bg-warning-lighten-5 {
  background-color: rgba(255, 193, 7, 0.05);
}

.v-empty-state {
  padding: 2rem;
}
</style>
