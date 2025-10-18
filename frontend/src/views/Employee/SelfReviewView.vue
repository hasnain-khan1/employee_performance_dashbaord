<template>
  <v-container fluid>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold text-primary">Self Review</h1>
            <p class="text-subtitle-1 text-grey-darken-1 mt-2">
              Complete your structured self-assessment for the performance cycle
            </p>
          </div>
          <div class="d-flex align-center gap-3">
            <v-chip
              :color="getStatusColor(selfReview?.status)"
              variant="flat"
              size="large"
            >
              {{ getStatusText(selfReview?.status) }}
            </v-chip>
            <v-btn
              v-if="selfReview?.status === 'draft' || selfReview?.status === 'in_progress'"
              color="primary"
              variant="elevated"
              prepend-icon="mdi-content-save"
              @click="saveDraft"
              :loading="saving"
            >
              Save Draft
            </v-btn>
          </div>
        </div>
      </v-col>
    </v-row>

    <!-- Prerequisites Check -->
    <v-card v-if="!prerequisitesMet" elevation="2" class="mb-6">
      <v-card-title class="d-flex align-center text-warning">
        <v-icon class="mr-2">mdi-alert-circle</v-icon>
        Prerequisites Required
      </v-card-title>
      <v-card-text>
        <p class="text-body-1 mb-4">
          Before you can complete your self-review, please ensure the following prerequisites are met:
        </p>
        <v-list>
          <v-list-item>
            <template #prepend>
              <v-icon :color="goalsApproved ? 'success' : 'warning'">
                {{ goalsApproved ? 'mdi-check-circle' : 'mdi-clock-outline' }}
              </v-icon>
            </template>
            <v-list-item-title>
              {{ goalsApproved ? 'Goals Approved' : 'Goals Pending Approval' }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ goalsApproved ? 'All your goals have been approved by your manager' : 'Please ensure all your goals are approved by your manager' }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-list-item>
            <template #prepend>
              <v-icon :color="peerFeedbackReceived ? 'success' : 'warning'">
                {{ peerFeedbackReceived ? 'mdi-check-circle' : 'mdi-clock-outline' }}
              </v-icon>
            </template>
            <v-list-item-title>
              {{ peerFeedbackReceived ? 'Peer Feedback Received' : 'Peer Feedback Pending' }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ peerFeedbackReceived ? 'You have received sufficient peer feedback' : 'Please request and receive peer feedback from colleagues' }}
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
        <div class="mt-4">
          <v-btn
            color="primary"
            variant="outlined"
            @click="checkPrerequisites"
            :loading="checkingPrerequisites"
          >
            Check Prerequisites Again
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- Progress Overview -->
    <v-card v-if="prerequisitesMet" elevation="2" class="mb-6">
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-progress-clock</v-icon>
        Review Progress
      </v-card-title>
      <v-card-text>
        <div class="d-flex align-center mb-4">
          <v-progress-linear
            :model-value="selfReview?.completion_percentage || 0"
            :color="getProgressColor(selfReview?.completion_percentage || 0)"
            height="12"
            rounded
            class="mr-4"
            style="flex: 1"
          />
          <span class="text-h6 font-weight-bold">
            {{ selfReview?.completion_percentage || 0 }}%
          </span>
        </div>
        <div class="d-flex justify-space-between text-caption text-grey">
          <span>Last saved: {{ formatDate(selfReview?.last_auto_save) }}</span>
          <span>Auto-save: Every 30 seconds</span>
        </div>
      </v-card-text>
    </v-card>

    <!-- Self Review Sections -->
    <div v-if="prerequisitesMet" class="self-review-sections">
      <!-- Goal Achievement Summary -->
      <SelfReviewSection
        v-model="sections.goal_achievement"
        section-type="goal_achievement"
        title="Goal Achievement Summary"
        description="Analyze your progress on each approved goal with specific evidence and metrics"
        :min-words="150"
        :max-words="500"
        :goals="approvedGoals"
        @update="updateSection"
        @save-draft="saveSectionDraft"
      />

      <!-- Key Accomplishments -->
      <SelfReviewSection
        v-model="sections.accomplishments"
        section-type="accomplishments"
        title="Key Accomplishments"
        description="Highlight your most significant contributions and achievements during this period"
        :min-words="200"
        :max-words="800"
        @update="updateSection"
        @save-draft="saveSectionDraft"
      />

      <!-- Behavioral Competencies -->
      <SelfReviewSection
        v-model="sections.competencies"
        section-type="competencies"
        title="Behavioral Competencies"
        description="Self-assess your performance against organizational competency framework"
        :min-words="100"
        :max-words="300"
        :peer-feedback="peerFeedbackThemes"
        @update="updateSection"
        @save-draft="saveSectionDraft"
      />

      <!-- Development Areas -->
      <SelfReviewSection
        v-model="sections.development"
        section-type="development"
        title="Development Areas"
        description="Identify growth opportunities and learning initiatives you've pursued"
        :min-words="200"
        :max-words="600"
        @update="updateSection"
        @save-draft="saveSectionDraft"
      />

      <!-- Career Aspirations -->
      <SelfReviewSection
        v-model="sections.career"
        section-type="career"
        title="Career Aspirations"
        description="Share your professional objectives and desired career progression"
        :min-words="150"
        :max-words="400"
        @update="updateSection"
        @save-draft="saveSectionDraft"
      />
    </div>

    <!-- Submit Review -->
    <v-card v-if="prerequisitesMet && canSubmit" elevation="2" class="mt-6">
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-check-circle</v-icon>
        Ready to Submit
      </v-card-title>
      <v-card-text>
        <p class="text-body-1 mb-4">
          Your self-review is complete and ready for submission. Once submitted, you will not be able to make further changes.
        </p>
        <div class="d-flex gap-3">
          <v-btn
            color="primary"
            variant="elevated"
            prepend-icon="mdi-send"
            @click="submitReview"
            :loading="submitting"
          >
            Submit Self Review
          </v-btn>
          <v-btn
            color="grey"
            variant="outlined"
            prepend-icon="mdi-eye"
            @click="previewReview"
          >
            Preview Review
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <!-- Preview Dialog -->
    <SelfReviewPreviewDialog
      v-model="previewDialog"
      :self-review="selfReview"
      :sections="sections"
    />
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from 'vue-toastification'
import { selfReviewAPI } from '@/api/reviews'
import SelfReviewSection from '@/components/Employee/SelfReviewSection.vue'
import SelfReviewPreviewDialog from '@/components/Employee/SelfReviewPreviewDialog.vue'

const toast = useToast()

// Reactive data
const loading = ref(false)
const saving = ref(false)
const submitting = ref(false)
const checkingPrerequisites = ref(false)
const previewDialog = ref(false)
const selfReview = ref(null)
const prerequisitesMet = ref(false)
const goalsApproved = ref(false)
const peerFeedbackReceived = ref(false)
const approvedGoals = ref([])
const peerFeedbackThemes = ref([])

// Section data
const sections = ref({
  goal_achievement: {
    content: '',
    word_count: 0,
    is_completed: false
  },
  accomplishments: {
    content: '',
    word_count: 0,
    is_completed: false
  },
  competencies: {
    content: '',
    word_count: 0,
    is_completed: false
  },
  development: {
    content: '',
    word_count: 0,
    is_completed: false
  },
  career: {
    content: '',
    word_count: 0,
    is_completed: false
  }
})

// Auto-save interval
let autoSaveInterval = null

// Computed properties
const canSubmit = computed(() => {
  return Object.values(sections.value).every(section => section.is_completed)
})

// Methods
const loadSelfReview = async () => {
  try {
    loading.value = true
    const response = await selfReviewAPI.getCurrentSelfReview()
    selfReview.value = response.data
    
    if (selfReview.value) {
      // Load section data
      sections.value = {
        goal_achievement: {
          content: selfReview.value.goal_achievement_summary || '',
          word_count: 0,
          is_completed: !!selfReview.value.goal_achievement_summary
        },
        accomplishments: {
          content: selfReview.value.key_accomplishments || '',
          word_count: 0,
          is_completed: !!selfReview.value.key_accomplishments
        },
        competencies: {
          content: selfReview.value.behavioral_competencies || '',
          word_count: 0,
          is_completed: !!selfReview.value.behavioral_competencies
        },
        development: {
          content: selfReview.value.development_areas || '',
          word_count: 0,
          is_completed: !!selfReview.value.development_areas
        },
        career: {
          content: selfReview.value.career_aspirations || '',
          word_count: 0,
          is_completed: !!selfReview.value.career_aspirations
        }
      }
      
      prerequisitesMet.value = selfReview.value.prerequisites_met
      goalsApproved.value = selfReview.value.goals_approved
      peerFeedbackReceived.value = selfReview.value.peer_feedback_received
    }
  } catch (error) {
    console.error('Error loading self-review:', error)
    toast.error('Failed to load self-review')
  } finally {
    loading.value = false
  }
}

const checkPrerequisites = async () => {
  try {
    checkingPrerequisites.value = true
    const response = await selfReviewAPI.checkPrerequisites()
    prerequisitesMet.value = response.data.prerequisites_met
    goalsApproved.value = response.data.goals_approved
    peerFeedbackReceived.value = response.data.peer_feedback_received
  } catch (error) {
    console.error('Error checking prerequisites:', error)
    toast.error('Failed to check prerequisites')
  } finally {
    checkingPrerequisites.value = false
  }
}

const updateSection = (sectionType, data) => {
  sections.value[sectionType] = { ...sections.value[sectionType], ...data }
  autoSave()
}

const saveSectionDraft = async (sectionType, content) => {
  try {
    await selfReviewAPI.saveDraft(sectionType, { content })
    toast.success('Draft saved successfully')
  } catch (error) {
    console.error('Error saving draft:', error)
    toast.error('Failed to save draft')
  }
}

const saveDraft = async () => {
  try {
    saving.value = true
    await selfReviewAPI.saveSelfReview(sections.value)
    toast.success('Self-review saved successfully')
    await loadSelfReview()
  } catch (error) {
    console.error('Error saving self-review:', error)
    toast.error('Failed to save self-review')
  } finally {
    saving.value = false
  }
}

const submitReview = async () => {
  try {
    submitting.value = true
    await selfReviewAPI.submitSelfReview(sections.value)
    toast.success('Self-review submitted successfully')
    await loadSelfReview()
  } catch (error) {
    console.error('Error submitting self-review:', error)
    toast.error('Failed to submit self-review')
  } finally {
    submitting.value = false
  }
}

const previewReview = () => {
  previewDialog.value = true
}

const autoSave = async () => {
  try {
    await selfReviewAPI.autoSave(sections.value)
  } catch (error) {
    console.error('Auto-save failed:', error)
  }
}

const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    in_progress: 'warning',
    submitted: 'success',
    under_review: 'info',
    completed: 'success',
    returned: 'error'
  }
  return colors[status] || 'grey'
}

const getStatusText = (status) => {
  const texts = {
    draft: 'Draft',
    in_progress: 'In Progress',
    submitted: 'Submitted',
    under_review: 'Under Review',
    completed: 'Completed',
    returned: 'Returned for Revision'
  }
  return texts[status] || status
}

const getProgressColor = (progress) => {
  if (progress >= 80) return 'success'
  if (progress >= 50) return 'warning'
  return 'error'
}

const formatDate = (date) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleString()
}

// Lifecycle
onMounted(() => {
  loadSelfReview()
  checkPrerequisites()
  
  // Start auto-save interval
  autoSaveInterval = setInterval(autoSave, 30000) // 30 seconds
})

onUnmounted(() => {
  if (autoSaveInterval) {
    clearInterval(autoSaveInterval)
  }
})
</script>

<style scoped>
.self-review-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.v-card {
  border-radius: 8px;
}

.v-chip {
  font-weight: 500;
}
</style>