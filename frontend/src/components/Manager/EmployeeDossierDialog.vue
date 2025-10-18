<template>
  <v-dialog
    v-model="dialog"
    max-width="1400px"
    persistent
    :scrim="true"
  >
    <v-card elevation="8">
      <v-card-title class="d-flex align-center justify-space-between bg-primary pa-4">
        <div class="d-flex align-center">
          <v-icon class="mr-3" color="white">mdi-file-document-multiple</v-icon>
          <div>
            <h3 class="text-h5 font-weight-bold text-white">
              Employee Performance Dossier
            </h3>
            <p class="text-subtitle-2 text-white mb-0" v-if="employee">
              {{ employee.name }} - {{ employee.position }}
            </p>
          </div>
        </div>
        <v-btn
          icon="mdi-close"
          variant="text"
          color="white"
          @click="closeDialog"
        />
      </v-card-title>

      <v-card-text class="pa-6">
        <v-container fluid>
          <!-- Employee Information -->
          <v-row class="mb-6">
            <v-col cols="12">
              <v-card variant="outlined">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2" color="primary">mdi-account</v-icon>
                  Employee Information
                </v-card-title>
                <v-card-text>
                  <v-row v-if="employee">
                    <v-col cols="12" md="6">
                      <div class="d-flex align-center mb-3">
                        <v-avatar size="64" class="mr-4">
                          <v-img
                            :src="employee.avatar || '/default-avatar.png'"
                            :alt="employee.name"
                          />
                        </v-avatar>
                        <div>
                          <h4 class="text-h6 font-weight-bold">{{ employee.name }}</h4>
                          <p class="text-subtitle-2 text-medium-emphasis mb-1">{{ employee.position }}</p>
                          <p class="text-caption text-medium-emphasis">{{ employee.department }}</p>
                        </div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-list density="compact">
                        <v-list-item>
                          <template #prepend>
                            <v-icon>mdi-email</v-icon>
                          </template>
                          <v-list-item-title>{{ employee.email }}</v-list-item-title>
                        </v-list-item>
                        <v-list-item>
                          <template #prepend>
                            <v-icon>mdi-calendar</v-icon>
                          </template>
                          <v-list-item-title>Hire Date: {{ formatDate(employee.hire_date) }}</v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Performance Overview -->
          <v-row class="mb-6">
            <v-col cols="12" md="4">
              <v-card variant="outlined" color="success" class="h-100">
                <v-card-text class="text-center">
                  <v-icon size="48" color="success" class="mb-2">mdi-target</v-icon>
                  <div class="text-h4 font-weight-bold">{{ dossier.goals?.length || 0 }}</div>
                  <div class="text-subtitle-2">Goals</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-card variant="outlined" color="info" class="h-100">
                <v-card-text class="text-center">
                  <v-icon size="48" color="info" class="mb-2">mdi-account-group</v-icon>
                  <div class="text-h4 font-weight-bold">{{ dossier.peer_feedback?.length || 0 }}</div>
                  <div class="text-subtitle-2">Peer Feedback</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-card variant="outlined" color="primary" class="h-100">
                <v-card-text class="text-center">
                  <v-icon size="48" color="primary" class="mb-2">mdi-clipboard-check</v-icon>
                  <div class="text-h4 font-weight-bold">
                    {{ dossier.self_review?.completion_percentage || 0 }}%
                  </div>
                  <div class="text-subtitle-2">Self-Review Complete</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Goals & Achievements -->
          <v-row class="mb-6">
            <v-col cols="12">
              <v-card variant="outlined">
                <v-card-title class="d-flex align-center justify-space-between">
                  <div class="d-flex align-center">
                    <v-icon class="mr-2" color="primary">mdi-target</v-icon>
                    Goals & Achievements
                  </div>
                  <v-chip
                    :color="getGoalsStatusColor()"
                    size="small"
                    variant="tonal"
                  >
                    {{ getGoalsStatusText() }}
                  </v-chip>
                </v-card-title>
                <v-card-text>
                  <v-list v-if="dossier.goals?.length > 0" density="compact">
                    <v-list-item
                      v-for="goal in dossier.goals"
                      :key="goal.id"
                      class="mb-2"
                    >
                      <template #prepend>
                        <v-icon :color="getGoalStatusColor(goal.status)">
                          {{ getGoalStatusIcon(goal.status) }}
                        </v-icon>
                      </template>
                      <v-list-item-title>{{ goal.title }}</v-list-item-title>
                      <v-list-item-subtitle>
                        Progress: {{ goal.progress_percentage }}% | 
                        Priority: {{ goal.priority }} | 
                        Target: {{ formatDate(goal.target_date) }}
                      </v-list-item-subtitle>
                      <template #append>
                        <v-progress-circular
                          :model-value="goal.progress_percentage"
                          size="24"
                          width="3"
                          :color="getProgressColor(goal.progress_percentage)"
                        />
                      </template>
                    </v-list-item>
                  </v-list>
                  <v-alert
                    v-else
                    type="info"
                    variant="tonal"
                    class="mt-4"
                  >
                    No goals found for this employee in the current cycle.
                  </v-alert>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Self-Review Status -->
          <v-row class="mb-6">
            <v-col cols="12">
              <v-card variant="outlined">
                <v-card-title class="d-flex align-center justify-space-between">
                  <div class="d-flex align-center">
                    <v-icon class="mr-2" color="primary">mdi-clipboard-text</v-icon>
                    Self-Review Status
                  </div>
                  <v-chip
                    :color="getSelfReviewStatusColor()"
                    size="small"
                    variant="tonal"
                  >
                    {{ getSelfReviewStatusText() }}
                  </v-chip>
                </v-card-title>
                <v-card-text>
                  <v-row v-if="dossier.self_review">
                    <v-col cols="12" md="6">
                      <v-list density="compact">
                        <v-list-item>
                          <v-list-item-title>Status</v-list-item-title>
                          <v-list-item-subtitle>{{ dossier.self_review.status }}</v-list-item-subtitle>
                        </v-list-item>
                        <v-list-item>
                          <v-list-item-title>Completion</v-list-item-title>
                          <v-list-item-subtitle>{{ dossier.self_review.completion_percentage }}%</v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-progress-linear
                        :model-value="dossier.self_review.completion_percentage"
                        color="primary"
                        height="8"
                        rounded
                      />
                      <p class="text-caption text-center mt-2">
                        Self-Review Progress
                      </p>
                    </v-col>
                  </v-row>
                  <v-alert
                    v-else
                    type="warning"
                    variant="tonal"
                    class="mt-4"
                  >
                    No self-review found for this employee in the current cycle.
                  </v-alert>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Peer Feedback -->
          <v-row class="mb-6">
            <v-col cols="12">
              <v-card variant="outlined">
                <v-card-title class="d-flex align-center justify-space-between">
                  <div class="d-flex align-center">
                    <v-icon class="mr-2" color="primary">mdi-account-group</v-icon>
                    Peer Feedback
                  </div>
                  <v-chip
                    :color="getPeerFeedbackStatusColor()"
                    size="small"
                    variant="tonal"
                  >
                    {{ getPeerFeedbackStatusText() }}
                  </v-chip>
                </v-card-title>
                <v-card-text>
                  <v-list v-if="dossier.peer_feedback?.length > 0" density="compact">
                    <v-list-item
                      v-for="feedback in dossier.peer_feedback"
                      :key="feedback.id"
                      class="mb-2"
                    >
                      <template #prepend>
                        <v-icon :color="getFeedbackStatusColor(feedback.status)">
                          {{ getFeedbackStatusIcon(feedback.status) }}
                        </v-icon>
                      </template>
                      <v-list-item-title>{{ feedback.title }}</v-list-item-title>
                      <v-list-item-subtitle>
                        Status: {{ feedback.status }} | 
                        Completion: {{ feedback.completion_percentage }}%
                      </v-list-item-subtitle>
                      <template #append>
                        <v-progress-circular
                          :model-value="feedback.completion_percentage"
                          size="24"
                          width="3"
                          :color="getProgressColor(feedback.completion_percentage)"
                        />
                      </template>
                    </v-list-item>
                  </v-list>
                  <v-alert
                    v-else
                    type="info"
                    variant="tonal"
                    class="mt-4"
                  >
                    No peer feedback requests found for this employee in the current cycle.
                  </v-alert>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Performance Metrics -->
          <v-row class="mb-6" v-if="dossier.performance_metrics">
            <v-col cols="12">
              <v-card variant="outlined">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2" color="primary">mdi-chart-line</v-icon>
                  Performance Metrics
                </v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="4" v-for="(metric, key) in dossier.performance_metrics" :key="key">
                      <v-card variant="tonal" :color="getMetricColor(metric.value)">
                        <v-card-text class="text-center">
                          <div class="text-h5 font-weight-bold">{{ metric.value }}</div>
                          <div class="text-subtitle-2">{{ metric.label }}</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Existing Manager Review -->
          <v-row v-if="dossier.manager_review">
            <v-col cols="12">
              <v-card variant="outlined" color="info">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2" color="info">mdi-clipboard-check</v-icon>
                  Existing Manager Review
                </v-card-title>
                <v-card-text>
                  <v-list density="compact">
                    <v-list-item>
                      <v-list-item-title>Status</v-list-item-title>
                      <v-list-item-subtitle>{{ dossier.manager_review.status }}</v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Overall Rating</v-list-item-title>
                      <v-list-item-subtitle>
                        <v-rating
                          :model-value="dossier.manager_review.overall_rating"
                          readonly
                          size="small"
                          color="amber"
                        />
                        {{ dossier.manager_review.overall_rating }}/5
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-list-item>
                      <v-list-item-title>Locked</v-list-item-title>
                      <v-list-item-subtitle>
                        <v-icon :color="dossier.manager_review.is_locked ? 'error' : 'success'">
                          {{ dossier.manager_review.is_locked ? 'mdi-lock' : 'mdi-lock-open' }}
                        </v-icon>
                        {{ dossier.manager_review.is_locked ? 'Yes' : 'No' }}
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          color="grey-darken-1"
          variant="outlined"
          @click="closeDialog"
        >
          Close
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          @click="createReview"
          :disabled="!canCreateReview"
        >
          {{ dossier.manager_review ? 'Edit Review' : 'Create Review' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { reviewsAPI } from '@/api/reviews'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  employee: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'review-created'])

// Composables
const toast = useToast()

// Reactive data
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)
const dossier = ref({})

// Computed properties
const canCreateReview = computed(() => {
  return props.employee && (
    !dossier.value.manager_review || 
    !dossier.value.manager_review.is_locked
  )
})

// Methods
const loadDossier = async () => {
  if (!props.employee) return

  try {
    loading.value = true
    const response = await reviewsAPI.getEmployeeDossier(props.employee.id)
    dossier.value = response.data
  } catch (error) {
    console.error('Error loading dossier:', error)
    toast.error('Failed to load employee dossier')
  } finally {
    loading.value = false
  }
}

const createReview = () => {
  emit('review-created', props.employee)
  closeDialog()
}

const closeDialog = () => {
  dialog.value = false
  dossier.value = {}
}

// Status helpers
const getGoalsStatusColor = () => {
  const goals = dossier.value.goals || []
  if (goals.length === 0) return 'grey'
  
  const completed = goals.filter(g => g.status === 'completed').length
  const total = goals.length
  
  if (completed === total) return 'success'
  if (completed > 0) return 'warning'
  return 'error'
}

const getGoalsStatusText = () => {
  const goals = dossier.value.goals || []
  if (goals.length === 0) return 'No Goals'
  
  const completed = goals.filter(g => g.status === 'completed').length
  const total = goals.length
  
  return `${completed}/${total} Completed`
}

const getSelfReviewStatusColor = () => {
  if (!dossier.value.self_review) return 'grey'
  
  const status = dossier.value.self_review.status
  const colors = {
    draft: 'grey',
    in_progress: 'blue',
    submitted: 'orange',
    completed: 'success'
  }
  return colors[status] || 'grey'
}

const getSelfReviewStatusText = () => {
  if (!dossier.value.self_review) return 'Not Started'
  return dossier.value.self_review.status
}

const getPeerFeedbackStatusColor = () => {
  const feedback = dossier.value.peer_feedback || []
  if (feedback.length === 0) return 'grey'
  
  const completed = feedback.filter(f => f.status === 'completed').length
  const total = feedback.length
  
  if (completed === total) return 'success'
  if (completed > 0) return 'warning'
  return 'error'
}

const getPeerFeedbackStatusText = () => {
  const feedback = dossier.value.peer_feedback || []
  if (feedback.length === 0) return 'No Feedback'
  
  const completed = feedback.filter(f => f.status === 'completed').length
  const total = feedback.length
  
  return `${completed}/${total} Completed`
}

const getGoalStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    in_progress: 'blue',
    completed: 'success',
    overdue: 'error'
  }
  return colors[status] || 'grey'
}

const getGoalStatusIcon = (status) => {
  const icons = {
    draft: 'mdi-pencil',
    in_progress: 'mdi-clock',
    completed: 'mdi-check',
    overdue: 'mdi-alert'
  }
  return icons[status] || 'mdi-help'
}

const getFeedbackStatusColor = (status) => {
  const colors = {
    pending: 'grey',
    in_progress: 'blue',
    completed: 'success',
    overdue: 'error'
  }
  return colors[status] || 'grey'
}

const getFeedbackStatusIcon = (status) => {
  const icons = {
    pending: 'mdi-clock',
    in_progress: 'mdi-pencil',
    completed: 'mdi-check',
    overdue: 'mdi-alert'
  }
  return icons[status] || 'mdi-help'
}

const getProgressColor = (percentage) => {
  if (percentage >= 100) return 'success'
  if (percentage >= 75) return 'info'
  if (percentage >= 50) return 'warning'
  return 'error'
}

const getMetricColor = (value) => {
  if (value >= 4) return 'success'
  if (value >= 3) return 'info'
  if (value >= 2) return 'warning'
  return 'error'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

// Watchers
watch(() => props.employee, loadDossier, { immediate: true })
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    loadDossier()
  }
})

// Lifecycle
onMounted(() => {
  if (props.modelValue && props.employee) {
    loadDossier()
  }
})
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.v-progress-circular {
  margin-left: auto;
}

.v-progress-linear {
  border-radius: 4px;
}
</style>
