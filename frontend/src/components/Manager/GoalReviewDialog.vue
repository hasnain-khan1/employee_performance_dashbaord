<template>
  <v-dialog
    v-model="dialog"
    max-width="1200px"
    persistent
    :scrim="true"
    scrollable
  >
    <v-card elevation="8" v-if="goal">
      <v-card-title class="text-h5 bg-primary pa-4 d-flex align-center">
        <v-icon class="mr-2">mdi-clipboard-check</v-icon>
        Goal Review: {{ goal.title }}
        <v-spacer />
        <v-chip
          :color="getStatusColor(goal.status)"
          variant="flat"
          size="small"
        >
          {{ getStatusText(goal.status) }}
        </v-chip>
      </v-card-title>

      <v-card-text class="pa-0">
        <v-container fluid>
          <!-- Employee Info -->
          <v-row class="mb-4">
            <v-col cols="12">
              <v-card variant="outlined" class="pa-4">
                <div class="d-flex align-center mb-3">
                  <v-avatar size="48" class="mr-3">
                    <v-img
                      v-if="goal.employee.avatar"
                      :src="goal.employee.avatar"
                      :alt="goal.employee.first_name"
                    />
                    <v-icon v-else size="24">mdi-account</v-icon>
                  </v-avatar>
                  <div>
                    <h3 class="text-h6 font-weight-bold">
                      {{ goal.employee.first_name }} {{ goal.employee.last_name }}
                    </h3>
                    <p class="text-subtitle-2 text-grey mb-0">
                      {{ goal.employee.email }} • {{ goal.employee.department }}
                    </p>
                  </div>
                </div>
              </v-card>
            </v-col>
          </v-row>

          <v-row>
            <!-- Left Column: Goal Details -->
            <v-col cols="12" md="8">
              <!-- Goal Information -->
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2">mdi-target</v-icon>
                  Goal Details
                </v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="6">
                      <div class="mb-3">
                        <label class="text-caption text-grey">Goal Type</label>
                        <div class="text-body-1 font-weight-medium">{{ goal.goal_type }}</div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="mb-3">
                        <label class="text-caption text-grey">Priority</label>
                        <div class="text-body-1 font-weight-medium">{{ goal.priority }}</div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="mb-3">
                        <label class="text-caption text-grey">Weight</label>
                        <div class="text-body-1 font-weight-medium">{{ goal.weight }}%</div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="mb-3">
                        <label class="text-caption text-grey">Target Date</label>
                        <div class="text-body-1 font-weight-medium">{{ formatDate(goal.target_date) }}</div>
                      </div>
                    </v-col>
                  </v-row>
                  
                  <div class="mb-3">
                    <label class="text-caption text-grey">Description</label>
                    <div class="text-body-1">{{ goal.description }}</div>
                  </div>

                  <div class="mb-3">
                    <label class="text-caption text-grey">Metric & Target</label>
                    <div class="text-body-1">
                      <strong>{{ goal.metric }}</strong>
                      <span v-if="goal.target_value">: {{ goal.target_value }} {{ goal.unit || '' }}</span>
                    </div>
                  </div>
                </v-card-text>
              </v-card>

              <!-- SMART Criteria Evaluation -->
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2">mdi-check-circle-outline</v-icon>
                  SMART Criteria Evaluation
                </v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="6">
                      <div class="d-flex align-center mb-3">
                        <v-checkbox
                          v-model="smartCriteria.specific"
                          color="success"
                          hide-details
                          class="mr-2"
                        />
                        <div>
                          <div class="font-weight-medium">Specific</div>
                          <div class="text-caption text-grey">{{ goal.specific }}</div>
                        </div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="d-flex align-center mb-3">
                        <v-checkbox
                          v-model="smartCriteria.measurable"
                          color="success"
                          hide-details
                          class="mr-2"
                        />
                        <div>
                          <div class="font-weight-medium">Measurable</div>
                          <div class="text-caption text-grey">{{ goal.measurable }}</div>
                        </div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="d-flex align-center mb-3">
                        <v-checkbox
                          v-model="smartCriteria.achievable"
                          color="success"
                          hide-details
                          class="mr-2"
                        />
                        <div>
                          <div class="font-weight-medium">Achievable</div>
                          <div class="text-caption text-grey">{{ goal.achievable }}</div>
                        </div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="d-flex align-center mb-3">
                        <v-checkbox
                          v-model="smartCriteria.relevant"
                          color="success"
                          hide-details
                          class="mr-2"
                        />
                        <div>
                          <div class="font-weight-medium">Relevant</div>
                          <div class="text-caption text-grey">{{ goal.relevant }}</div>
                        </div>
                      </div>
                    </v-col>
                    <v-col cols="12">
                      <div class="d-flex align-center mb-3">
                        <v-checkbox
                          v-model="smartCriteria.timeBound"
                          color="success"
                          hide-details
                          class="mr-2"
                        />
                        <div>
                          <div class="font-weight-medium">Time-bound</div>
                          <div class="text-caption text-grey">{{ goal.time_bound }}</div>
                        </div>
                      </div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>

              <!-- Business Alignment -->
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2">mdi-chart-line</v-icon>
                  Business Alignment
                </v-card-title>
                <v-card-text>
                  <v-textarea
                    v-model="alignmentComments"
                    label="Alignment Comments"
                    placeholder="How does this goal align with business objectives?"
                    variant="outlined"
                    rows="3"
                  />
                </v-card-text>
              </v-card>

              <!-- Manager Feedback -->
              <v-card variant="outlined">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2">mdi-comment-text</v-icon>
                  Manager Feedback
                </v-card-title>
                <v-card-text>
                  <v-textarea
                    v-model="managerFeedback"
                    label="Feedback"
                    placeholder="Provide specific feedback for the employee..."
                    variant="outlined"
                    rows="4"
                    :rules="feedbackRules"
                  />
                  
                  <div class="mt-3">
                    <v-select
                      v-model="selectedAction"
                      label="Review Action"
                      :items="actionOptions"
                      variant="outlined"
                      :rules="actionRules"
                    />
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Right Column: Goal History & Progress -->
            <v-col cols="12" md="4">
              <!-- Progress Tracking -->
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2">mdi-progress-clock</v-icon>
                  Progress
                </v-card-title>
                <v-card-text>
                  <div class="text-center mb-4">
                    <div class="text-h4 font-weight-bold text-primary">
                      {{ goal.progress_percentage || 0 }}%
                    </div>
                    <v-progress-circular
                      :model-value="goal.progress_percentage || 0"
                      :color="getProgressColor(goal.progress_percentage || 0)"
                      size="80"
                      width="8"
                    />
                  </div>
                  
                  <div class="mb-3">
                    <label class="text-caption text-grey">Current Value</label>
                    <div class="text-body-1 font-weight-medium">
                      {{ goal.current_value || 'Not set' }} {{ goal.unit || '' }}
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label class="text-caption text-grey">Target Value</label>
                    <div class="text-body-1 font-weight-medium">
                      {{ goal.target_value || 'Not set' }} {{ goal.unit || '' }}
                    </div>
                  </div>
                </v-card-text>
              </v-card>

              <!-- Goal History -->
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2">mdi-history</v-icon>
                  Version History
                </v-card-title>
                <v-card-text>
                  <div v-if="goalHistory.length === 0" class="text-center text-grey">
                    No version history available
                  </div>
                  <div v-else>
                    <div
                      v-for="(version, index) in goalHistory"
                      :key="index"
                      class="mb-3 pa-3 border rounded"
                    >
                      <div class="d-flex align-center mb-2">
                        <v-chip size="small" color="primary" variant="flat">
                          v{{ version.version }}
                        </v-chip>
                        <span class="ml-2 text-caption text-grey">
                          {{ formatDate(version.created_at) }}
                        </span>
                      </div>
                      <div class="text-body-2">{{ version.changes }}</div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>

              <!-- Workload Assessment -->
              <v-card variant="outlined">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2">mdi-scale-balance</v-icon>
                  Workload Assessment
                </v-card-title>
                <v-card-text>
                  <v-slider
                    v-model="workloadAssessment"
                    label="Workload Level"
                    :min="1"
                    :max="5"
                    :step="1"
                    :ticks="workloadTicks"
                    thumb-label
                    color="primary"
                  />
                  
                  <v-textarea
                    v-model="workloadComments"
                    label="Workload Comments"
                    placeholder="Comments on workload and achievability..."
                    variant="outlined"
                    rows="2"
                    class="mt-3"
                  />
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
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          :loading="saving"
          :disabled="!isFormValid"
          @click="submitReview"
        >
          Submit Review
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { goalsAPI } from '@/api/goals'

const props = defineProps({
  modelValue: Boolean,
  goal: Object
})

const emit = defineEmits(['update:modelValue', 'goal-updated'])

const toast = useToast()

// Reactive data
const saving = ref(false)
const smartCriteria = ref({
  specific: false,
  measurable: false,
  achievable: false,
  relevant: false,
  timeBound: false
})
const alignmentComments = ref('')
const managerFeedback = ref('')
const selectedAction = ref('')
const workloadAssessment = ref(3)
const workloadComments = ref('')
const goalHistory = ref([])

// Form validation
const feedbackRules = [
  v => !!v || 'Feedback is required',
  v => v.length >= 10 || 'Feedback must be at least 10 characters'
]

const actionRules = [
  v => !!v || 'Review action is required'
]

// Action options
const actionOptions = [
  { title: 'Approve Goal', value: 'approve' },
  { title: 'Request Changes', value: 'request_changes' },
  { title: 'Suggest Modifications', value: 'suggest_modifications' }
]

// Workload assessment ticks
const workloadTicks = {
  1: 'Very Light',
  2: 'Light',
  3: 'Moderate',
  4: 'Heavy',
  5: 'Very Heavy'
}

// Computed properties
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isFormValid = computed(() => {
  return managerFeedback.value.length >= 10 && selectedAction.value
})

// Methods
const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    pending: 'warning',
    approved: 'success',
    needs_changes: 'error',
    rejected: 'error'
  }
  return colors[status] || 'grey'
}

const getStatusText = (status) => {
  const texts = {
    draft: 'Draft',
    pending: 'Pending',
    approved: 'Approved',
    needs_changes: 'Needs Changes',
    rejected: 'Rejected'
  }
  return texts[status] || status
}

const getProgressColor = (progress) => {
  if (progress >= 80) return 'success'
  if (progress >= 50) return 'warning'
  return 'error'
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const loadGoalHistory = async () => {
  if (!props.goal?.id) return
  
  try {
    const response = await goalsAPI.getGoalHistory(props.goal.id)
    goalHistory.value = response.data
  } catch (error) {
    console.error('Error loading goal history:', error)
  }
}

const submitReview = async () => {
  if (!isFormValid.value) {
    toast.error('Please fill in all required fields')
    return
  }

  try {
    saving.value = true
    
    const reviewData = {
      action: selectedAction.value,
      feedback: managerFeedback.value,
      alignment_comments: alignmentComments.value,
      workload_assessment: workloadAssessment.value,
      workload_comments: workloadComments.value,
      smart_criteria: smartCriteria.value
    }

    await goalsAPI.submitGoalReview(props.goal.id, reviewData)
    
    toast.success('Review submitted successfully')
    emit('goal-updated')
    closeDialog()
  } catch (error) {
    console.error('Error submitting review:', error)
    toast.error('Failed to submit review')
  } finally {
    saving.value = false
  }
}

const closeDialog = () => {
  dialog.value = false
  resetForm()
}

const resetForm = () => {
  smartCriteria.value = {
    specific: false,
    measurable: false,
    achievable: false,
    relevant: false,
    timeBound: false
  }
  alignmentComments.value = ''
  managerFeedback.value = ''
  selectedAction.value = ''
  workloadAssessment.value = 3
  workloadComments.value = ''
}

// Watchers
watch(() => props.goal, (newGoal) => {
  if (newGoal) {
    loadGoalHistory()
  }
}, { immediate: true })
</script>

<style scoped>
.v-card {
  border-radius: 8px;
}

.v-chip {
  font-weight: 500;
}

.border {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
</style>
