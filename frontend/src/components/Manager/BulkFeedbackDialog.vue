<template>
  <v-dialog
    v-model="dialog"
    max-width="800px"
    persistent
    :scrim="true"
  >
    <v-card elevation="8">
      <v-card-title class="text-h5 bg-primary pa-4 d-flex align-center">
        <v-icon class="mr-2">mdi-comment-multiple</v-icon>
        Bulk Feedback
        <v-spacer />
        <v-chip color="white" variant="flat" size="small">
          {{ goals.length }} goal(s)
        </v-chip>
      </v-card-title>

      <v-card-text class="pa-6">
        <!-- Action Selection -->
        <div class="mb-6">
          <h3 class="text-h6 font-weight-bold mb-3">Select Action</h3>
          <v-radio-group v-model="selectedAction" inline>
            <v-radio
              label="Approve Goals"
              value="approve"
              color="success"
            />
            <v-radio
              label="Request Changes"
              value="request_changes"
              color="warning"
            />
            <v-radio
              label="Suggest Modifications"
              value="suggest_modifications"
              color="info"
            />
          </v-radio-group>
        </div>

        <!-- Goals List -->
        <div class="mb-6">
          <h3 class="text-h6 font-weight-bold mb-3">Selected Goals</h3>
          <v-card variant="outlined" class="pa-4" style="max-height: 200px; overflow-y: auto;">
            <div
              v-for="goal in goals"
              :key="goal.id"
              class="d-flex align-center mb-2 pa-2 border rounded"
            >
              <v-avatar size="32" class="mr-3">
                <v-img
                  v-if="goal.employee.avatar"
                  :src="goal.employee.avatar"
                  :alt="goal.employee.first_name"
                />
                <v-icon v-else>mdi-account</v-icon>
              </v-avatar>
              <div class="flex-grow-1">
                <div class="font-weight-medium">{{ goal.title }}</div>
                <div class="text-caption text-grey">
                  {{ goal.employee.first_name }} {{ goal.employee.last_name }}
                </div>
              </div>
              <v-chip
                :color="getStatusColor(goal.status)"
                variant="flat"
                size="small"
              >
                {{ getStatusText(goal.status) }}
              </v-chip>
            </div>
          </v-card>
        </div>

        <!-- Feedback Template -->
        <div class="mb-4">
          <h3 class="text-h6 font-weight-bold mb-3">Feedback Template</h3>
          <v-select
            v-model="selectedTemplate"
            label="Choose a template (optional)"
            :items="feedbackTemplates"
            variant="outlined"
            clearable
            @update:model-value="applyTemplate"
          />
        </div>

        <!-- General Feedback -->
        <div class="mb-4">
          <h3 class="text-h6 font-weight-bold mb-3">General Feedback</h3>
          <v-textarea
            v-model="generalFeedback"
            label="Feedback for all selected goals"
            placeholder="Enter general feedback that applies to all selected goals..."
            variant="outlined"
            rows="4"
            :rules="feedbackRules"
          />
        </div>

        <!-- Individual Goal Feedback -->
        <div v-if="selectedAction === 'request_changes' || selectedAction === 'suggest_modifications'">
          <h3 class="text-h6 font-weight-bold mb-3">Individual Goal Feedback</h3>
          <div
            v-for="goal in goals"
            :key="goal.id"
            class="mb-4 pa-4 border rounded"
          >
            <div class="d-flex align-center mb-3">
              <v-avatar size="32" class="mr-3">
                <v-img
                  v-if="goal.employee.avatar"
                  :src="goal.employee.avatar"
                  :alt="goal.employee.first_name"
                />
                <v-icon v-else>mdi-account</v-icon>
              </v-avatar>
              <div>
                <div class="font-weight-medium">{{ goal.title }}</div>
                <div class="text-caption text-grey">
                  {{ goal.employee.first_name }} {{ goal.employee.last_name }}
                </div>
              </div>
            </div>
            
            <v-textarea
              v-model="individualFeedback[goal.id]"
              :label="`Specific feedback for ${goal.employee.first_name}`"
              placeholder="Enter specific feedback for this goal..."
              variant="outlined"
              rows="3"
            />
          </div>
        </div>

        <!-- SMART Criteria Assessment -->
        <div class="mb-4">
          <h3 class="text-h6 font-weight-bold mb-3">SMART Criteria Assessment</h3>
          <v-row>
            <v-col cols="12" md="6">
              <div class="d-flex align-center mb-2">
                <v-checkbox
                  v-model="smartAssessment.specific"
                  color="success"
                  hide-details
                  class="mr-2"
                />
                <span>Specific</span>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="d-flex align-center mb-2">
                <v-checkbox
                  v-model="smartAssessment.measurable"
                  color="success"
                  hide-details
                  class="mr-2"
                />
                <span>Measurable</span>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="d-flex align-center mb-2">
                <v-checkbox
                  v-model="smartAssessment.achievable"
                  color="success"
                  hide-details
                  class="mr-2"
                />
                <span>Achievable</span>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="d-flex align-center mb-2">
                <v-checkbox
                  v-model="smartAssessment.relevant"
                  color="success"
                  hide-details
                  class="mr-2"
                />
                <span>Relevant</span>
              </div>
            </v-col>
            <v-col cols="12">
              <div class="d-flex align-center mb-2">
                <v-checkbox
                  v-model="smartAssessment.timeBound"
                  color="success"
                  hide-details
                  class="mr-2"
                />
                <span>Time-bound</span>
              </div>
            </v-col>
          </v-row>
        </div>

        <!-- Additional Comments -->
        <div class="mb-4">
          <h3 class="text-h6 font-weight-bold mb-3">Additional Comments</h3>
          <v-textarea
            v-model="additionalComments"
            label="Additional comments or suggestions"
            placeholder="Any additional comments or suggestions..."
            variant="outlined"
            rows="3"
          />
        </div>

        <!-- Notification Settings -->
        <div class="mb-4">
          <h3 class="text-h6 font-weight-bold mb-3">Notification Settings</h3>
          <v-checkbox
            v-model="sendEmailNotification"
            label="Send email notification to employees"
            color="primary"
          />
          <v-checkbox
            v-model="sendSystemNotification"
            label="Send system notification"
            color="primary"
          />
        </div>
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
          @click="submitBulkFeedback"
        >
          Submit Feedback
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
  goals: {
    type: Array,
    default: () => []
  },
  action: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'feedback-submitted'])

const toast = useToast()

// Reactive data
const saving = ref(false)
const selectedAction = ref(props.action || 'approve')
const generalFeedback = ref('')
const individualFeedback = ref({})
const additionalComments = ref('')
const selectedTemplate = ref('')
const smartAssessment = ref({
  specific: false,
  measurable: false,
  achievable: false,
  relevant: false,
  timeBound: false
})
const sendEmailNotification = ref(true)
const sendSystemNotification = ref(true)

// Form validation
const feedbackRules = [
  v => !!v || 'General feedback is required',
  v => v.length >= 10 || 'Feedback must be at least 10 characters'
]

// Feedback templates
const feedbackTemplates = [
  {
    title: 'Approval Template',
    value: 'approval',
    content: 'Great work on setting clear and achievable goals! These objectives align well with our team priorities and will contribute to our overall success.'
  },
  {
    title: 'Request Changes - Specificity',
    value: 'specificity',
    content: 'Please make your goals more specific. Instead of general statements, include concrete details about what exactly will be accomplished.'
  },
  {
    title: 'Request Changes - Measurability',
    value: 'measurability',
    content: 'Please add measurable criteria to your goals. Include specific numbers, percentages, or other quantifiable metrics to track progress.'
  },
  {
    title: 'Request Changes - Timeline',
    value: 'timeline',
    content: 'Please add clear timelines and deadlines to your goals. This will help ensure accountability and proper planning.'
  },
  {
    title: 'Suggest Modifications - Workload',
    value: 'workload',
    content: 'Consider adjusting the scope of this goal to better balance your workload. The current target may be too ambitious given your other responsibilities.'
  }
]

// Computed properties
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isFormValid = computed(() => {
  return generalFeedback.value.length >= 10 && selectedAction.value
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

const applyTemplate = (templateValue) => {
  if (!templateValue) return
  
  const template = feedbackTemplates.find(t => t.value === templateValue)
  if (template) {
    generalFeedback.value = template.content
  }
}

const submitBulkFeedback = async () => {
  if (!isFormValid.value) {
    toast.error('Please fill in all required fields')
    return
  }

  try {
    saving.value = true
    
    const feedbackData = {
      action: selectedAction.value,
      general_feedback: generalFeedback.value,
      individual_feedback: individualFeedback.value,
      additional_comments: additionalComments.value,
      smart_assessment: smartAssessment.value,
      send_email: sendEmailNotification.value,
      send_system: sendSystemNotification.value,
      goal_ids: props.goals.map(g => g.id)
    }

    await goalsAPI.submitBulkFeedback(feedbackData)
    
    toast.success(`Bulk feedback submitted for ${props.goals.length} goal(s)`)
    emit('feedback-submitted')
    closeDialog()
  } catch (error) {
    console.error('Error submitting bulk feedback:', error)
    toast.error('Failed to submit bulk feedback')
  } finally {
    saving.value = false
  }
}

const closeDialog = () => {
  dialog.value = false
  resetForm()
}

const resetForm = () => {
  selectedAction.value = props.action || 'approve'
  generalFeedback.value = ''
  individualFeedback.value = {}
  additionalComments.value = ''
  selectedTemplate.value = ''
  smartAssessment.value = {
    specific: false,
    measurable: false,
    achievable: false,
    relevant: false,
    timeBound: false
  }
  sendEmailNotification.value = true
  sendSystemNotification.value = true
}

// Watchers
watch(() => props.action, (newAction) => {
  if (newAction) {
    selectedAction.value = newAction
  }
}, { immediate: true })

watch(() => props.goals, (newGoals) => {
  // Initialize individual feedback for each goal
  const feedback = {}
  newGoals.forEach(goal => {
    feedback[goal.id] = ''
  })
  individualFeedback.value = feedback
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
