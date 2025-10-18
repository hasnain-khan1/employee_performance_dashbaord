<template>
  <v-card elevation="2" class="self-review-section">
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">{{ getSectionIcon(sectionType) }}</v-icon>
      {{ title }}
      <v-spacer />
      <div class="d-flex align-center gap-2">
        <v-chip
          :color="isCompleted ? 'success' : 'warning'"
          variant="flat"
          size="small"
        >
          {{ isCompleted ? 'Completed' : 'In Progress' }}
        </v-chip>
        <v-chip
          :color="getWordCountColor()"
          variant="outlined"
          size="small"
        >
          {{ wordCount }}/{{ maxWords }} words
        </v-chip>
      </div>
    </v-card-title>

    <v-card-text>
      <p class="text-body-2 text-grey mb-4">{{ description }}</p>
      
      <!-- Rich Text Editor -->
      <div class="rich-text-editor">
        <v-textarea
          v-model="localContent"
          :label="`${title} Content`"
          :placeholder="getPlaceholder()"
          variant="outlined"
          rows="8"
          counter
            :maxlength="maxWords * 6"
          @input="handleContentChange"
          @blur="saveDraft"
        />
      </div>

      <!-- Word Count Progress -->
      <div class="mt-3">
        <v-progress-linear
          :model-value="wordCountProgress"
          :color="getWordCountColor()"
          height="6"
          rounded
        />
        <div class="d-flex justify-space-between text-caption text-grey mt-1">
          <span>Minimum: {{ minWords }} words</span>
          <span>Maximum: {{ maxWords }} words</span>
        </div>
      </div>

      <!-- Evidence Linking -->
      <div v-if="showEvidenceLinking" class="mt-4">
        <v-divider class="mb-4" />
        <h4 class="text-subtitle-1 font-weight-bold mb-3">Evidence & References</h4>
        
        <!-- Goal References -->
        <div v-if="goals && goals.length > 0" class="mb-4">
          <h5 class="text-body-1 font-weight-medium mb-2">Link to Goals</h5>
          <v-select
            v-model="selectedGoal"
            :items="goalOptions"
            label="Select a goal to reference"
            variant="outlined"
            clearable
            @update:model-value="insertGoalReference"
          />
        </div>

        <!-- Peer Feedback Themes -->
        <div v-if="peerFeedback && peerFeedback.length > 0" class="mb-4">
          <h5 class="text-body-1 font-weight-medium mb-2">Peer Feedback Themes</h5>
          <v-chip-group
            v-model="selectedFeedbackThemes"
            multiple
            @update:model-value="insertFeedbackThemes"
          >
            <v-chip
              v-for="theme in peerFeedback"
              :key="theme"
              variant="outlined"
              size="small"
            >
              {{ theme }}
            </v-chip>
          </v-chip-group>
        </div>

        <!-- Evidence Links -->
        <div class="mb-4">
          <h5 class="text-body-1 font-weight-medium mb-2">Add Evidence Links</h5>
          <div class="d-flex gap-2">
            <v-btn
              color="primary"
              variant="outlined"
              size="small"
              prepend-icon="mdi-link"
              @click="addUrlLink"
            >
              URL Link
            </v-btn>
            <v-btn
              color="primary"
              variant="outlined"
              size="small"
              prepend-icon="mdi-file-document"
              @click="addDocument"
            >
              Document
            </v-btn>
            <v-btn
              color="primary"
              variant="outlined"
              size="small"
              prepend-icon="mdi-chart-line"
              @click="addMetric"
            >
              Metric
            </v-btn>
          </div>
        </div>

        <!-- Evidence List -->
        <div v-if="evidenceLinks.length > 0" class="evidence-links">
          <h5 class="text-body-1 font-weight-medium mb-2">Added Evidence</h5>
          <div
            v-for="(link, index) in evidenceLinks"
            :key="index"
            class="evidence-link-item pa-3 mb-2 border rounded"
          >
            <div class="d-flex align-center">
              <v-icon class="mr-2">{{ getLinkIcon(link.type) }}</v-icon>
              <div class="flex-grow-1">
                <div class="font-weight-medium">{{ link.title }}</div>
                <div class="text-caption text-grey">{{ link.description }}</div>
              </div>
              <v-btn
                icon="mdi-close"
                size="small"
                variant="text"
                @click="removeEvidenceLink(index)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Writing Guidelines -->
      <div class="mt-4">
        <v-expansion-panels variant="accordion">
          <v-expansion-panel>
            <v-expansion-panel-title>
              <v-icon class="mr-2">mdi-lightbulb</v-icon>
              Writing Guidelines
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <ul class="text-body-2">
                <li>Use specific examples and concrete details</li>
                <li>Include quantifiable results where possible</li>
                <li>Be honest and balanced in your assessment</li>
                <li>Link achievements to business impact</li>
                <li>Use professional, clear language</li>
              </ul>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </div>
    </v-card-text>

    <!-- Section Actions -->
    <v-card-actions>
      <v-spacer />
      <v-btn
        color="primary"
        variant="outlined"
        @click="saveDraft"
        :loading="saving"
      >
        Save Draft
      </v-btn>
      <v-btn
        color="primary"
        variant="elevated"
        @click="markCompleted"
        :disabled="!isValid"
      >
        Mark Complete
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useToast } from 'vue-toastification'

const props = defineProps({
  modelValue: Object,
  sectionType: String,
  title: String,
  description: String,
  minWords: Number,
  maxWords: Number,
  goals: Array,
  peerFeedback: Array
})

const emit = defineEmits(['update:modelValue', 'save-draft'])

const toast = useToast()

// Reactive data
const localContent = ref(props.modelValue?.content || '')
const selectedGoal = ref(null)
const selectedFeedbackThemes = ref([])
const evidenceLinks = ref([])
const saving = ref(false)

// Computed properties
const wordCount = computed(() => {
  return localContent.value.trim().split(/\s+/).filter(word => word.length > 0).length
})

const wordCountProgress = computed(() => {
  return Math.min((wordCount.value / props.maxWords) * 100, 100)
})

const isCompleted = computed(() => {
  return props.modelValue?.is_completed || false
})

const isValid = computed(() => {
  return wordCount.value >= props.minWords && wordCount.value <= props.maxWords
})

const showEvidenceLinking = computed(() => {
  return props.sectionType === 'goal_achievement' || props.sectionType === 'competencies'
})

const goalOptions = computed(() => {
  if (!props.goals) return []
  return props.goals.map(goal => ({
    title: goal.title,
    value: goal.id
  }))
})

// Methods
const getSectionIcon = (sectionType) => {
  const icons = {
    goal_achievement: 'mdi-target',
    accomplishments: 'mdi-trophy',
    competencies: 'mdi-star',
    development: 'mdi-trending-up',
    career: 'mdi-account-arrow-up'
  }
  return icons[sectionType] || 'mdi-text'
}

const getWordCountColor = () => {
  if (wordCount.value < props.minWords) return 'error'
  if (wordCount.value > props.maxWords) return 'error'
  if (wordCount.value >= props.minWords) return 'success'
  return 'warning'
}

const getPlaceholder = () => {
  const placeholders = {
    goal_achievement: 'Describe your progress on each goal with specific metrics and outcomes...',
    accomplishments: 'Highlight your most significant contributions and achievements...',
    competencies: 'Self-assess your performance against organizational competencies...',
    development: 'Identify areas for growth and learning initiatives you\'ve pursued...',
    career: 'Share your professional objectives and career aspirations...'
  }
  return placeholders[props.sectionType] || 'Enter your content here...'
}

const getLinkIcon = (type) => {
  const icons = {
    goal: 'mdi-target',
    feedback: 'mdi-comment-text',
    document: 'mdi-file-document',
    url: 'mdi-link',
    metric: 'mdi-chart-line'
  }
  return icons[type] || 'mdi-link'
}

const handleContentChange = () => {
  const updatedValue = {
    ...props.modelValue,
    content: localContent.value,
    word_count: wordCount.value,
    is_completed: isCompleted.value && isValid.value
  }
  emit('update:modelValue', updatedValue)
}

const saveDraft = async () => {
  try {
    saving.value = true
    emit('save-draft', props.sectionType, localContent.value)
  } finally {
    saving.value = false
  }
}

const markCompleted = () => {
  if (!isValid.value) {
    toast.error(`Please ensure content is between ${props.minWords} and ${props.maxWords} words`)
    return
  }
  
  const updatedValue = {
    ...props.modelValue,
    content: localContent.value,
    word_count: wordCount.value,
    is_completed: true
  }
  emit('update:modelValue', updatedValue)
  toast.success('Section marked as complete')
}

const insertGoalReference = (goalId) => {
  if (!goalId) return
  
  const goal = props.goals?.find(g => g.id === goalId)
  if (goal) {
    const reference = `[Goal: ${goal.title}]`
    localContent.value += ` ${reference}`
    selectedGoal.value = null
  }
}

const insertFeedbackThemes = (themes) => {
  if (themes.length === 0) return
  
  const themesText = themes.map(theme => `[Feedback: ${theme}]`).join(' ')
  localContent.value += ` ${themesText}`
  selectedFeedbackThemes.value = []
}

const addUrlLink = () => {
  const url = prompt('Enter URL:')
  if (url) {
    evidenceLinks.value.push({
      type: 'url',
      title: 'URL Link',
      description: url,
      url: url
    })
  }
}

const addDocument = () => {
  // In a real implementation, this would open a file picker
  const document = prompt('Enter document name:')
  if (document) {
    evidenceLinks.value.push({
      type: 'document',
      title: 'Document',
      description: document
    })
  }
}

const addMetric = () => {
  const metric = prompt('Enter metric description:')
  if (metric) {
    evidenceLinks.value.push({
      type: 'metric',
      title: 'Performance Metric',
      description: metric
    })
  }
}

const removeEvidenceLink = (index) => {
  evidenceLinks.value.splice(index, 1)
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    localContent.value = newValue.content || ''
  }
}, { deep: true })
</script>

<style scoped>
.self-review-section {
  border-radius: 8px;
}

.evidence-link-item {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.border {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.v-chip {
  font-weight: 500;
}
</style>
