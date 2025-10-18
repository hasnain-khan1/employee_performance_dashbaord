<template>
  <v-dialog
    v-model="dialog"
    max-width="1200px"
    persistent
    :scrim="true"
  >
    <v-card elevation="8">
      <v-card-title class="d-flex align-center justify-space-between bg-primary pa-4">
        <div class="d-flex align-center">
          <v-icon class="mr-3" color="white">mdi-clipboard-check</v-icon>
          <div>
            <h3 class="text-h5 font-weight-bold text-white">
              {{ isEditing ? 'Edit Review' : 'Create New Review' }}
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
        <v-form ref="reviewFormRef" v-model="formValid">
          <!-- Review Period -->
          <v-row class="mb-4">
            <v-col cols="12" md="6">
              <v-text-field
                v-model="reviewData.review_period_start"
                label="Review Period Start Date"
                type="date"
                variant="outlined"
                :rules="[rules.required]"
                required
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="reviewData.review_period_end"
                label="Review Period End Date"
                type="date"
                variant="outlined"
                :rules="[rules.required, rules.endDateAfterStart]"
                required
              />
            </v-col>
          </v-row>

          <!-- Goals & Achievements -->
          <v-card variant="outlined" class="mb-6">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-target</v-icon>
              Goals & Achievements
            </v-card-title>
            <v-card-text>
              <v-textarea
                v-model="reviewData.goals_achievements"
                label="Goals & Achievements Assessment"
                placeholder="Describe the employee's goal achievements and performance..."
                variant="outlined"
                rows="4"
                counter
                :maxlength="2000"
              />
            </v-card-text>
          </v-card>

          <!-- Competency Ratings -->
          <v-card variant="outlined" class="mb-6">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-star</v-icon>
              Competency Ratings
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <div class="mb-4">
                    <label class="text-subtitle-2 mb-2 d-block">Communication Skills</label>
                    <v-rating
                      v-model="reviewData.communication_rating"
                      color="amber"
                      size="large"
                      :rules="[rules.ratingRequired]"
                    />
                    <span class="text-caption text-medium-emphasis ml-2">
                      {{ reviewData.communication_rating || 0 }}/5
                    </span>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="mb-4">
                    <label class="text-subtitle-2 mb-2 d-block">Collaboration</label>
                    <v-rating
                      v-model="reviewData.collaboration_rating"
                      color="amber"
                      size="large"
                      :rules="[rules.ratingRequired]"
                    />
                    <span class="text-caption text-medium-emphasis ml-2">
                      {{ reviewData.collaboration_rating || 0 }}/5
                    </span>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="mb-4">
                    <label class="text-subtitle-2 mb-2 d-block">Leadership</label>
                    <v-rating
                      v-model="reviewData.leadership_rating"
                      color="amber"
                      size="large"
                      :rules="[rules.ratingRequired]"
                    />
                    <span class="text-caption text-medium-emphasis ml-2">
                      {{ reviewData.leadership_rating || 0 }}/5
                    </span>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="mb-4">
                    <label class="text-subtitle-2 mb-2 d-block">Problem Solving</label>
                    <v-rating
                      v-model="reviewData.problem_solving_rating"
                      color="amber"
                      size="large"
                      :rules="[rules.ratingRequired]"
                    />
                    <span class="text-caption text-medium-emphasis ml-2">
                      {{ reviewData.problem_solving_rating || 0 }}/5
                    </span>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="mb-4">
                    <label class="text-subtitle-2 mb-2 d-block">Adaptability</label>
                    <v-rating
                      v-model="reviewData.adaptability_rating"
                      color="amber"
                      size="large"
                      :rules="[rules.ratingRequired]"
                    />
                    <span class="text-caption text-medium-emphasis ml-2">
                      {{ reviewData.adaptability_rating || 0 }}/5
                    </span>
                  </div>
                </v-col>
                
                <v-col cols="12" md="6">
                  <div class="mb-4">
                    <label class="text-subtitle-2 mb-2 d-block">Overall Rating</label>
                    <v-rating
                      v-model="reviewData.overall_rating"
                      color="amber"
                      size="large"
                      :rules="[rules.ratingRequired]"
                    />
                    <span class="text-caption text-medium-emphasis ml-2">
                      {{ reviewData.overall_rating || 0 }}/5
                    </span>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Narrative Sections -->
          <v-card variant="outlined" class="mb-6">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-text</v-icon>
              Manager Narrative
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="reviewData.performance_summary"
                    label="Performance Summary"
                    placeholder="Provide a comprehensive summary of the employee's performance..."
                    variant="outlined"
                    rows="4"
                    counter
                    :maxlength="2000"
                    :rules="[rules.required, rules.minWords(200)]"
                    required
                  />
                </v-col>
                
                <v-col cols="12">
                  <v-textarea
                    v-model="reviewData.strengths"
                    label="Key Strengths"
                    placeholder="Identify and describe the employee's key strengths..."
                    variant="outlined"
                    rows="3"
                    counter
                    :maxlength="1500"
                    :rules="[rules.required, rules.minWords(200)]"
                    required
                  />
                </v-col>
                
                <v-col cols="12">
                  <v-textarea
                    v-model="reviewData.development_areas"
                    label="Development Areas"
                    placeholder="Identify areas for improvement and development..."
                    variant="outlined"
                    rows="3"
                    counter
                    :maxlength="1500"
                    :rules="[rules.required, rules.minWords(200)]"
                    required
                  />
                </v-col>
                
                <v-col cols="12">
                  <v-textarea
                    v-model="reviewData.career_recommendations"
                    label="Career Recommendations"
                    placeholder="Provide career development recommendations..."
                    variant="outlined"
                    rows="3"
                    counter
                    :maxlength="1500"
                    :rules="[rules.required, rules.minWords(200)]"
                    required
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Additional Information -->
          <v-card variant="outlined" class="mb-6">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-information</v-icon>
              Additional Information
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="reviewData.comments"
                    label="Additional Comments"
                    placeholder="Any additional comments or observations..."
                    variant="outlined"
                    rows="3"
                    counter
                    :maxlength="5000"
                  />
                </v-col>
                
                <v-col cols="12">
                  <v-textarea
                    v-model="reviewData.private_notes"
                    label="Private Notes (Not visible to employee)"
                    placeholder="Private notes for your reference..."
                    variant="outlined"
                    rows="3"
                    counter
                    :maxlength="2000"
                  />
                </v-col>
                
                <v-col cols="12">
                  <v-textarea
                    v-model="reviewData.development_notes"
                    label="Development Notes"
                    placeholder="Development planning and next steps..."
                    variant="outlined"
                    rows="3"
                    counter
                    :maxlength="2000"
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Attachments -->
          <v-card variant="outlined" class="mb-6">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-attachment</v-icon>
              Attachments
            </v-card-title>
            <v-card-text>
              <v-file-input
                v-model="newAttachment"
                label="Upload Attachment"
                variant="outlined"
                prepend-icon="mdi-paperclip"
                accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                :rules="[rules.fileSize]"
                @change="handleFileUpload"
              />
              
              <v-list v-if="attachments.length > 0" class="mt-4">
                <v-list-item
                  v-for="attachment in attachments"
                  :key="attachment.id"
                  class="mb-2"
                >
                  <template #prepend>
                    <v-icon>mdi-file</v-icon>
                  </template>
                  <v-list-item-title>{{ attachment.file_name }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ formatFileSize(attachment.file_size) }} - {{ attachment.file_type }}
                  </v-list-item-subtitle>
                  <template #append>
                    <v-btn
                      icon="mdi-delete"
                      size="small"
                      variant="text"
                      color="error"
                      @click="removeAttachment(attachment.id)"
                    />
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          color="grey-darken-1"
          variant="outlined"
          @click="closeDialog"
          :disabled="saving"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          variant="outlined"
          @click="saveReview"
          :disabled="!formValid || saving"
          :loading="saving"
        >
          Save Draft
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          @click="submitReview"
          :disabled="!formValid || saving"
          :loading="saving"
        >
          Submit Review
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
  review: {
    type: Object,
    default: null
  },
  employee: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'saved', 'submitted'])

// Composables
const toast = useToast()

// Reactive data
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const reviewFormRef = ref(null)
const formValid = ref(false)
const saving = ref(false)
const newAttachment = ref(null)
const attachments = ref([])

const reviewData = ref({
  review_period_start: '',
  review_period_end: '',
  goals_achievements: '',
  communication_rating: null,
  collaboration_rating: null,
  leadership_rating: null,
  problem_solving_rating: null,
  adaptability_rating: null,
  overall_rating: null,
  performance_summary: '',
  strengths: '',
  development_areas: '',
  career_recommendations: '',
  comments: '',
  private_notes: '',
  development_notes: ''
})

// Computed properties
const isEditing = computed(() => !!props.review)

// Validation rules
const rules = {
  required: (value) => !!value || 'This field is required',
  ratingRequired: (value) => !!value || 'Rating is required',
  endDateAfterStart: (value) => {
    if (!value || !reviewData.value.review_period_start) return true
    return new Date(value) > new Date(reviewData.value.review_period_start) || 'End date must be after start date'
  },
  minWords: (min) => (value) => {
    if (!value) return true
    const wordCount = value.split().length
    return wordCount >= min || `Minimum ${min} words required`
  },
  fileSize: (file) => {
    if (!file) return true
    const maxSize = 10 * 1024 * 1024 // 10MB
    return file.size <= maxSize || 'File size must be less than 10MB'
  }
}

// Methods
const loadReviewData = () => {
  if (props.review) {
    reviewData.value = {
      review_period_start: props.review.review_period_start || '',
      review_period_end: props.review.review_period_end || '',
      goals_achievements: props.review.goals_achievements || '',
      communication_rating: props.review.communication_rating,
      collaboration_rating: props.review.collaboration_rating,
      leadership_rating: props.review.leadership_rating,
      problem_solving_rating: props.review.problem_solving_rating,
      adaptability_rating: props.review.adaptability_rating,
      overall_rating: props.review.overall_rating,
      performance_summary: props.review.performance_summary || '',
      strengths: props.review.strengths || '',
      development_areas: props.review.development_areas || '',
      career_recommendations: props.review.career_recommendations || '',
      comments: props.review.comments || '',
      private_notes: props.review.private_notes || '',
      development_notes: props.review.development_notes || ''
    }
    attachments.value = props.review.attachments || []
  } else {
    // Set default dates for new review
    const today = new Date()
    const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate())
    reviewData.value.review_period_start = oneYearAgo.toISOString().split('T')[0]
    reviewData.value.review_period_end = today.toISOString().split('T')[0]
  }
}

const saveReview = async () => {
  try {
    if (reviewFormRef.value) {
      const { valid } = await reviewFormRef.value.validate()
      if (!valid) {
        toast.error('Please fill in all required fields')
        return
      }
    }

    saving.value = true

    if (isEditing.value) {
      await reviewsAPI.updateManagerReview(props.review.id, reviewData.value)
      toast.success('Review updated successfully')
      emit('saved')
    } else {
      const reviewDataWithEmployee = {
        ...reviewData.value,
        employee: props.employee.id
      }
      await reviewsAPI.createManagerReview(reviewDataWithEmployee)
      toast.success('Review created successfully')
      emit('saved')
    }
  } catch (error) {
    console.error('Error saving review:', error)
    const errorMsg = error.response?.data?.error || error.message || 'Failed to save review'
    toast.error(errorMsg)
  } finally {
    saving.value = false
  }
}

const submitReview = async () => {
  try {
    if (reviewFormRef.value) {
      const { valid } = await reviewFormRef.value.validate()
      if (!valid) {
        toast.error('Please fill in all required fields')
        return
      }
    }

    // Validate narrative sections have minimum word count
    const narrativeSections = [
      reviewData.value.performance_summary,
      reviewData.value.strengths,
      reviewData.value.development_areas,
      reviewData.value.career_recommendations
    ]

    for (const section of narrativeSections) {
      if (!section || section.split().length < 200) {
        toast.error('All narrative sections must have at least 200 words')
        return
      }
    }

    saving.value = true

    if (isEditing.value) {
      await reviewsAPI.submitManagerReview(props.review.id)
      toast.success('Review submitted successfully')
      emit('submitted')
    } else {
      // Create and submit in one step
      const reviewDataWithEmployee = {
        ...reviewData.value,
        employee: props.employee.id
      }
      const response = await reviewsAPI.createManagerReview(reviewDataWithEmployee)
      await reviewsAPI.submitManagerReview(response.data.id)
      toast.success('Review created and submitted successfully')
      emit('submitted')
    }
  } catch (error) {
    console.error('Error submitting review:', error)
    const errorMsg = error.response?.data?.error || error.message || 'Failed to submit review'
    toast.error(errorMsg)
  } finally {
    saving.value = false
  }
}

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (file.size > 10 * 1024 * 1024) {
    toast.error('File size must be less than 10MB')
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', getFileType(file.name))
    formData.append('description', '')

    const response = await reviewsAPI.uploadReviewAttachment(props.review?.id || 'new', formData)
    attachments.value.push(response.data)
    toast.success('Attachment uploaded successfully')
  } catch (error) {
    console.error('Error uploading attachment:', error)
    toast.error('Failed to upload attachment')
  }
}

const removeAttachment = async (attachmentId) => {
  try {
    await reviewsAPI.deleteReviewAttachment(attachmentId)
    attachments.value = attachments.value.filter(a => a.id !== attachmentId)
    toast.success('Attachment removed successfully')
  } catch (error) {
    console.error('Error removing attachment:', error)
    toast.error('Failed to remove attachment')
  }
}

const getFileType = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase()
  const typeMap = {
    'pdf': 'document',
    'doc': 'document',
    'docx': 'document',
    'txt': 'document',
    'jpg': 'image',
    'jpeg': 'image',
    'png': 'image',
    'xls': 'spreadsheet',
    'xlsx': 'spreadsheet',
    'ppt': 'presentation',
    'pptx': 'presentation'
  }
  return typeMap[extension] || 'other'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const closeDialog = () => {
  dialog.value = false
  // Reset form data
  reviewData.value = {
    review_period_start: '',
    review_period_end: '',
    goals_achievements: '',
    communication_rating: null,
    collaboration_rating: null,
    leadership_rating: null,
    problem_solving_rating: null,
    adaptability_rating: null,
    overall_rating: null,
    performance_summary: '',
    strengths: '',
    development_areas: '',
    career_recommendations: '',
    comments: '',
    private_notes: '',
    development_notes: ''
  }
  attachments.value = []
}

// Watchers
watch(() => props.review, loadReviewData, { immediate: true })
watch(() => props.employee, loadReviewData, { immediate: true })

// Lifecycle
onMounted(() => {
  loadReviewData()
})
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.v-rating {
  display: inline-flex;
}

.v-textarea {
  font-family: inherit;
}
</style>
