<template>
  <v-dialog
    v-model="dialog"
    max-width="1200px"
    persistent
    :scrim="true"
    scrollable
  >
    <v-card elevation="8" v-if="request">
      <v-card-title class="text-h5 bg-primary pa-4 d-flex align-center">
        <v-icon class="mr-2">mdi-comment-text</v-icon>
        Provide Feedback
        <v-spacer />
        <v-chip
          :color="getStatusColor(request.status)"
          variant="flat"
          size="small"
        >
          {{ getStatusText(request.status) }}
        </v-chip>
      </v-card-title>

      <v-card-text class="pa-0">
        <v-container fluid>
          <!-- Request Info -->
          <v-row class="mb-4">
            <v-col cols="12">
              <v-card variant="outlined" class="pa-4">
                <div class="d-flex align-center mb-3">
                  <v-avatar size="48" class="mr-3">
                    <v-img
                      v-if="request.requester.avatar"
                      :src="request.requester.avatar"
                      :alt="request.requester.first_name"
                    />
                    <v-icon v-else size="24">mdi-account</v-icon>
                  </v-avatar>
                  <div>
                    <h3 class="text-h6 font-weight-bold">
                      {{ request.requester.first_name }} {{ request.requester.last_name }}
                    </h3>
                    <p class="text-subtitle-2 text-grey mb-0">
                      {{ request.requester.email }} • {{ request.requester.department }}
                    </p>
                  </div>
                </div>
                <div class="mb-3">
                  <h4 class="text-subtitle-1 font-weight-bold">{{ request.title }}</h4>
                  <p class="text-body-2">{{ request.description }}</p>
                </div>
                <div class="d-flex align-center">
                  <v-icon class="mr-2">mdi-clock-outline</v-icon>
                  <span class="text-body-2">Deadline: {{ formatDate(request.deadline) }}</span>
                </div>
              </v-card>
            </v-col>
          </v-row>

          <v-row>
            <!-- Left Column: Feedback Form -->
            <v-col cols="12" md="8">
              <v-form ref="formRef" v-model="formValid">
                <!-- Behavioral Competencies -->
                <v-card variant="outlined" class="mb-4">
                  <v-card-title class="d-flex align-center">
                    <v-icon class="mr-2">mdi-star</v-icon>
                    Behavioral Competencies
                  </v-card-title>
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" md="6">
                        <div class="mb-4">
                          <label class="text-subtitle-2 font-weight-medium mb-2 d-block">
                            Communication Skills
                          </label>
                          <v-rating
                            v-model="feedbackForm.communication_rating"
                            color="primary"
                            size="large"
                            :rules="ratingRules"
                          />
                          <div class="text-caption text-grey mt-1">
                            Rate their communication effectiveness
                          </div>
                        </div>
                      </v-col>
                      <v-col cols="12" md="6">
                        <div class="mb-4">
                          <label class="text-subtitle-2 font-weight-medium mb-2 d-block">
                            Collaboration
                          </label>
                          <v-rating
                            v-model="feedbackForm.collaboration_rating"
                            color="primary"
                            size="large"
                            :rules="ratingRules"
                          />
                          <div class="text-caption text-grey mt-1">
                            Rate their teamwork and collaboration
                          </div>
                        </div>
                      </v-col>
                      <v-col cols="12" md="6">
                        <div class="mb-4">
                          <label class="text-subtitle-2 font-weight-medium mb-2 d-block">
                            Leadership
                          </label>
                          <v-rating
                            v-model="feedbackForm.leadership_rating"
                            color="primary"
                            size="large"
                            :rules="ratingRules"
                          />
                          <div class="text-caption text-grey mt-1">
                            Rate their leadership qualities
                          </div>
                        </div>
                      </v-col>
                      <v-col cols="12" md="6">
                        <div class="mb-4">
                          <label class="text-subtitle-2 font-weight-medium mb-2 d-block">
                            Problem Solving
                          </label>
                          <v-rating
                            v-model="feedbackForm.problem_solving_rating"
                            color="primary"
                            size="large"
                            :rules="ratingRules"
                          />
                          <div class="text-caption text-grey mt-1">
                            Rate their problem-solving abilities
                          </div>
                        </div>
                      </v-col>
                      <v-col cols="12">
                        <div class="mb-4">
                          <label class="text-subtitle-2 font-weight-medium mb-2 d-block">
                            Adaptability
                          </label>
                          <v-rating
                            v-model="feedbackForm.adaptability_rating"
                            color="primary"
                            size="large"
                            :rules="ratingRules"
                          />
                          <div class="text-caption text-grey mt-1">
                            Rate their adaptability and flexibility
                          </div>
                        </div>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>

                <!-- Text Feedback -->
                <v-card variant="outlined" class="mb-4">
                  <v-card-title class="d-flex align-center">
                    <v-icon class="mr-2">mdi-text</v-icon>
                    Written Feedback
                  </v-card-title>
                  <v-card-text>
                    <v-row>
                      <v-col cols="12">
                        <v-textarea
                          v-model="feedbackForm.strengths"
                          label="Strengths and Positive Contributions"
                          placeholder="What are their key strengths and positive contributions?"
                          variant="outlined"
                          rows="4"
                          :rules="textRules"
                          counter
                          maxlength="1000"
                        />
                      </v-col>
                      <v-col cols="12">
                        <v-textarea
                          v-model="feedbackForm.development_areas"
                          label="Areas for Development"
                          placeholder="What areas could they improve or develop further?"
                          variant="outlined"
                          rows="4"
                          :rules="textRules"
                          counter
                          maxlength="1000"
                        />
                      </v-col>
                      <v-col cols="12">
                        <v-textarea
                          v-model="feedbackForm.collaboration_examples"
                          label="Specific Examples"
                          placeholder="Provide specific examples of working together..."
                          variant="outlined"
                          rows="3"
                          :rules="textRules"
                          counter
                          maxlength="800"
                        />
                      </v-col>
                      <v-col cols="12">
                        <v-textarea
                          v-model="feedbackForm.additional_comments"
                          label="Additional Comments"
                          placeholder="Any other observations or comments..."
                          variant="outlined"
                          rows="3"
                          counter
                          maxlength="500"
                        />
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>

                <!-- Overall Rating -->
                <v-card variant="outlined" class="mb-4">
                  <v-card-title class="d-flex align-center">
                    <v-icon class="mr-2">mdi-trophy</v-icon>
                    Overall Rating
                  </v-card-title>
                  <v-card-text>
                    <div class="text-center">
                      <v-rating
                        v-model="feedbackForm.overall_rating"
                        color="primary"
                        size="x-large"
                        :rules="ratingRules"
                      />
                      <div class="text-subtitle-1 font-weight-medium mt-2">
                        Overall Performance Rating
                      </div>
                    </div>
                  </v-card-text>
                </v-card>

                <!-- Content Policy Warnings -->
                <v-card
                  v-if="contentViolations.length > 0"
                  variant="outlined"
                  color="warning"
                  class="mb-4"
                >
                  <v-card-title class="d-flex align-center text-warning">
                    <v-icon class="mr-2">mdi-alert</v-icon>
                    Content Policy Violations
                  </v-card-title>
                  <v-card-text>
                    <div v-for="violation in contentViolations" :key="violation.rule_name" class="mb-2">
                      <div class="font-weight-medium">{{ violation.rule_name }}</div>
                      <div class="text-caption">{{ violation.warning_message }}</div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-form>
            </v-col>

            <!-- Right Column: Guidelines and Options -->
            <v-col cols="12" md="4">
              <!-- Feedback Guidelines -->
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2">mdi-lightbulb</v-icon>
                  Feedback Guidelines
                </v-card-title>
                <v-card-text>
                  <ul class="text-body-2">
                    <li>Be specific and constructive</li>
                    <li>Focus on behaviors, not personality</li>
                    <li>Provide concrete examples</li>
                    <li>Balance strengths and development areas</li>
                    <li>Use professional language</li>
                  </ul>
                </v-card-text>
              </v-card>

              <!-- Anonymity Options -->
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2">mdi-incognito</v-icon>
                  Feedback Options
                </v-card-title>
                <v-card-text>
                  <v-checkbox
                    v-model="feedbackForm.is_anonymous"
                    label="Submit anonymously"
                    color="primary"
                  />
                  <div class="text-caption text-grey">
                    Your identity will not be shared with the requester
                  </div>
                </v-card-text>
              </v-card>

              <!-- Save Progress -->
              <v-card variant="outlined">
                <v-card-title class="d-flex align-center">
                  <v-icon class="mr-2">mdi-content-save</v-icon>
                  Save Progress
                </v-card-title>
                <v-card-text>
                  <v-btn
                    color="primary"
                    variant="outlined"
                    block
                    @click="saveDraft"
                    :loading="savingDraft"
                  >
                    Save Draft
                  </v-btn>
                  <div class="text-caption text-grey mt-2">
                    Your progress will be saved automatically
                  </div>
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
          :disabled="!isFormValid || contentViolations.length > 0"
          @click="submitFeedback"
        >
          Submit Feedback
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { feedbackAPI } from '@/api/feedback'

const props = defineProps({
  modelValue: Boolean,
  request: Object
})

const emit = defineEmits(['update:modelValue', 'feedback-provided'])

const toast = useToast()

// Reactive data
const formRef = ref(null)
const formValid = ref(false)
const saving = ref(false)
const savingDraft = ref(false)
const contentViolations = ref([])

// Form data
const feedbackForm = ref({
  communication_rating: null,
  collaboration_rating: null,
  leadership_rating: null,
  problem_solving_rating: null,
  adaptability_rating: null,
  overall_rating: null,
  strengths: '',
  development_areas: '',
  collaboration_examples: '',
  additional_comments: '',
  is_anonymous: false
})

// Form validation
const ratingRules = [
  v => v !== null || 'Rating is required'
]

const textRules = [
  v => !!v || 'This field is required',
  v => v.length >= 10 || 'Please provide at least 10 characters'
]

// Computed properties
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isFormValid = computed(() => {
  return formValid.value &&
         feedbackForm.value.communication_rating &&
         feedbackForm.value.collaboration_rating &&
         feedbackForm.value.leadership_rating &&
         feedbackForm.value.problem_solving_rating &&
         feedbackForm.value.adaptability_rating &&
         feedbackForm.value.overall_rating &&
         feedbackForm.value.strengths &&
         feedbackForm.value.development_areas &&
         feedbackForm.value.collaboration_examples
})

// Methods
const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    sent: 'primary',
    in_progress: 'warning',
    completed: 'success',
    expired: 'error'
  }
  return colors[status] || 'grey'
}

const getStatusText = (status) => {
  const texts = {
    draft: 'Draft',
    sent: 'Sent',
    in_progress: 'In Progress',
    completed: 'Completed',
    expired: 'Expired'
  }
  return texts[status] || status
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const validateContent = async () => {
  try {
    const allText = [
      feedbackForm.value.strengths,
      feedbackForm.value.development_areas,
      feedbackForm.value.collaboration_examples,
      feedbackForm.value.additional_comments
    ].join(' ')

    const response = await feedbackAPI.validateContentPolicy({ content: allText })
    contentViolations.value = response.data.violations
  } catch (error) {
    console.error('Error validating content:', error)
  }
}

const saveDraft = async () => {
  try {
    savingDraft.value = true
    
    // TODO: Implement draft saving
    toast.success('Draft saved successfully')
  } catch (error) {
    console.error('Error saving draft:', error)
    toast.error('Failed to save draft')
  } finally {
    savingDraft.value = false
  }
}

const submitFeedback = async () => {
  if (!isFormValid.value) {
    toast.error('Please fill in all required fields')
    return
  }

  if (contentViolations.value.length > 0) {
    toast.error('Please address content policy violations before submitting')
    return
  }

  try {
    saving.value = true
    
    const responseData = {
      ...feedbackForm.value,
      peer_reviewer_id: props.request.id // This would be the peer reviewer ID
    }

    await feedbackAPI.submitFeedbackResponse(responseData)
    
    toast.success('Feedback submitted successfully')
    emit('feedback-provided')
    closeDialog()
  } catch (error) {
    console.error('Error submitting feedback:', error)
    const errorMsg = error.response?.data?.error || 'Failed to submit feedback'
    toast.error(errorMsg)
  } finally {
    saving.value = false
  }
}

const closeDialog = () => {
  dialog.value = false
  resetForm()
}

const resetForm = () => {
  feedbackForm.value = {
    communication_rating: null,
    collaboration_rating: null,
    leadership_rating: null,
    problem_solving_rating: null,
    adaptability_rating: null,
    overall_rating: null,
    strengths: '',
    development_areas: '',
    collaboration_examples: '',
    additional_comments: '',
    is_anonymous: false
  }
  contentViolations.value = []
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    // Load existing feedback if available
    // TODO: Implement loading existing feedback
  }
})

watch(feedbackForm, () => {
  // Validate content when form changes
  if (feedbackForm.value.strengths || feedbackForm.value.development_areas) {
    validateContent()
  }
}, { deep: true })
</script>

<style scoped>
.v-card {
  border-radius: 8px;
}

.v-rating {
  justify-content: flex-start;
}
</style>
