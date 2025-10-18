<template>
  <v-dialog
    v-model="dialog"
    max-width="1000px"
    persistent
    :scrim="true"
    scrollable
  >
    <v-card elevation="8">
      <v-card-title class="text-h5 bg-primary pa-4 d-flex align-center">
        <v-icon class="mr-2">mdi-eye</v-icon>
        Self Review Preview
        <v-spacer />
        <v-chip color="white" variant="flat" size="small">
          {{ getCompletionPercentage() }}% Complete
        </v-chip>
      </v-card-title>

      <v-card-text class="pa-6">
        <!-- Review Summary -->
        <v-card variant="outlined" class="mb-6">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-information</v-icon>
            Review Summary
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <div class="mb-3">
                  <label class="text-caption text-grey">Employee</label>
                  <div class="text-body-1 font-weight-medium">
                    {{ selfReview?.employee?.first_name }} {{ selfReview?.employee?.last_name }}
                  </div>
                </div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="mb-3">
                  <label class="text-caption text-grey">Review Cycle</label>
                  <div class="text-body-1 font-weight-medium">
                    {{ selfReview?.cycle?.name }}
                  </div>
                </div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="mb-3">
                  <label class="text-caption text-grey">Status</label>
                  <v-chip
                    :color="getStatusColor(selfReview?.status)"
                    variant="flat"
                    size="small"
                  >
                    {{ getStatusText(selfReview?.status) }}
                  </v-chip>
                </div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="mb-3">
                  <label class="text-caption text-grey">Completion</label>
                  <div class="d-flex align-center">
                    <v-progress-linear
                      :model-value="selfReview?.completion_percentage || 0"
                      :color="getProgressColor(selfReview?.completion_percentage || 0)"
                      height="8"
                      rounded
                      class="mr-2"
                      style="width: 100px"
                    />
                    <span class="text-body-2">{{ selfReview?.completion_percentage || 0 }}%</span>
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- Section Previews -->
        <div class="preview-sections">
          <!-- Goal Achievement Summary -->
          <PreviewSection
            v-if="sections.goal_achievement?.content"
            title="Goal Achievement Summary"
            :content="sections.goal_achievement.content"
            :word-count="getWordCount(sections.goal_achievement.content)"
            :is-completed="sections.goal_achievement.is_completed"
            icon="mdi-target"
          />

          <!-- Key Accomplishments -->
          <PreviewSection
            v-if="sections.accomplishments?.content"
            title="Key Accomplishments"
            :content="sections.accomplishments.content"
            :word-count="getWordCount(sections.accomplishments.content)"
            :is-completed="sections.accomplishments.is_completed"
            icon="mdi-trophy"
          />

          <!-- Behavioral Competencies -->
          <PreviewSection
            v-if="sections.competencies?.content"
            title="Behavioral Competencies"
            :content="sections.competencies.content"
            :word-count="getWordCount(sections.competencies.content)"
            :is-completed="sections.competencies.is_completed"
            icon="mdi-star"
          />

          <!-- Development Areas -->
          <PreviewSection
            v-if="sections.development?.content"
            title="Development Areas"
            :content="sections.development.content"
            :word-count="getWordCount(sections.development.content)"
            :is-completed="sections.development.is_completed"
            icon="mdi-trending-up"
          />

          <!-- Career Aspirations -->
          <PreviewSection
            v-if="sections.career?.content"
            title="Career Aspirations"
            :content="sections.career.content"
            :word-count="getWordCount(sections.career.content)"
            :is-completed="sections.career.is_completed"
            icon="mdi-account-arrow-up"
          />
        </div>

        <!-- Completion Status -->
        <v-card variant="outlined" class="mt-6">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-check-circle</v-icon>
            Completion Status
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="(section, key) in sections"
                :key="key"
                :title="getSectionTitle(key)"
                :subtitle="section.content ? `${getWordCount(section.content)} words` : 'Not started'"
              >
                <template #prepend>
                  <v-icon :color="section.is_completed ? 'success' : 'warning'">
                    {{ section.is_completed ? 'mdi-check-circle' : 'mdi-clock-outline' }}
                  </v-icon>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
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
          v-if="canSubmit"
          color="primary"
          variant="elevated"
          @click="submitReview"
        >
          Submit Review
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'
import PreviewSection from './PreviewSection.vue'

const props = defineProps({
  modelValue: Boolean,
  selfReview: Object,
  sections: Object
})

const emit = defineEmits(['update:modelValue', 'submit-review'])

// Computed properties
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const canSubmit = computed(() => {
  return Object.values(props.sections).every(section => section.is_completed)
})

// Methods
const getCompletionPercentage = () => {
  const completedSections = Object.values(props.sections).filter(section => section.is_completed).length
  return Math.round((completedSections / Object.keys(props.sections).length) * 100)
}

const getWordCount = (content) => {
  if (!content) return 0
  return content.trim().split(/\s+/).filter(word => word.length > 0).length
}

const getSectionTitle = (key) => {
  const titles = {
    goal_achievement: 'Goal Achievement Summary',
    accomplishments: 'Key Accomplishments',
    competencies: 'Behavioral Competencies',
    development: 'Development Areas',
    career: 'Career Aspirations'
  }
  return titles[key] || key
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

const closeDialog = () => {
  dialog.value = false
}

const submitReview = () => {
  emit('submit-review')
  closeDialog()
}
</script>

<style scoped>
.preview-sections {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.v-card {
  border-radius: 8px;
}

.v-chip {
  font-weight: 500;
}
</style>
