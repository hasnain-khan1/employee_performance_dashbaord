<template>
  <v-dialog
    v-model="dialog"
    max-width="600px"
    persistent
    :scrim="true"
  >
    <v-card elevation="8">
      <v-card-title class="d-flex align-center justify-space-between bg-primary pa-4">
        <div class="d-flex align-center">
          <v-icon class="mr-3" color="white">mdi-format-list-bulleted</v-icon>
          <div>
            <h3 class="text-h5 font-weight-bold text-white">
              Bulk Review Actions
            </h3>
            <p class="text-subtitle-2 text-white mb-0">
              {{ selectedReviews.length }} review(s) selected
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
        <!-- Action Selection -->
        <v-card variant="outlined" class="mb-6">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-cog</v-icon>
            Select Action
          </v-card-title>
          <v-card-text>
            <v-radio-group v-model="selectedAction" inline>
              <v-radio
                value="submit"
                label="Submit Reviews"
                color="primary"
              />
              <v-radio
                value="approve"
                label="Approve Reviews"
                color="success"
              />
              <v-radio
                value="return"
                label="Return for Revision"
                color="warning"
              />
              <v-radio
                value="lock"
                label="Lock Reviews"
                color="error"
              />
              <v-radio
                value="unlock"
                label="Unlock Reviews"
                color="info"
              />
            </v-radio-group>
          </v-card-text>
        </v-card>

        <!-- Reason/Notes -->
        <v-card variant="outlined" class="mb-6">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-note-text</v-icon>
            Action Details
          </v-card-title>
          <v-card-text>
            <v-textarea
              v-model="actionReason"
              :label="getReasonLabel()"
              :placeholder="getReasonPlaceholder()"
              variant="outlined"
              rows="3"
              counter
              :maxlength="500"
            />
          </v-card-text>
        </v-card>

        <!-- Selected Reviews Preview -->
        <v-card variant="outlined">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-account-group</v-icon>
            Selected Reviews
          </v-card-title>
          <v-card-text>
            <v-list density="compact" class="max-height-300 overflow-y-auto">
              <v-list-item
                v-for="review in selectedReviews"
                :key="review.id"
                class="mb-2"
              >
                <template #prepend>
                  <v-icon :color="getStatusColor(review.status)">
                    {{ getStatusIcon(review.status) }}
                  </v-icon>
                </template>
                <v-list-item-title>{{ review.employee.name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ review.employee.position }} | {{ review.status }} | 
                  {{ review.overall_rating ? `${review.overall_rating}/5` : 'Not rated' }}
                </v-list-item-subtitle>
                <template #append>
                  <v-chip
                    :color="review.is_locked ? 'error' : 'success'"
                    size="small"
                    variant="tonal"
                  >
                    {{ review.is_locked ? 'Locked' : 'Unlocked' }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <!-- Action Summary -->
        <v-alert
          v-if="selectedAction"
          :type="getActionAlertType()"
          variant="tonal"
          class="mt-4"
        >
          <div class="d-flex align-center">
            <v-icon class="mr-2">{{ getActionIcon() }}</v-icon>
            <div>
              <strong>{{ getActionTitle() }}</strong>
              <p class="mb-0 text-caption">
                {{ getActionDescription() }}
              </p>
            </div>
          </div>
        </v-alert>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          color="grey-darken-1"
          variant="outlined"
          @click="closeDialog"
          :disabled="processing"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          @click="executeBulkAction"
          :disabled="!selectedAction || processing"
          :loading="processing"
        >
          {{ getActionButtonText() }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { reviewsAPI } from '@/api/reviews'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  selectedReviews: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'action-completed'])

// Composables
const toast = useToast()

// Reactive data
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const selectedAction = ref('')
const actionReason = ref('')
const processing = ref(false)

// Computed properties
const getReasonLabel = () => {
  const labels = {
    submit: 'Submission Notes',
    approve: 'Approval Notes',
    return: 'Revision Feedback',
    lock: 'Lock Reason',
    unlock: 'Unlock Reason'
  }
  return labels[selectedAction.value] || 'Reason'
}

const getReasonPlaceholder = () => {
  const placeholders = {
    submit: 'Add any notes about the submission...',
    approve: 'Add any notes about the approval...',
    return: 'Provide specific feedback for revision...',
    lock: 'Explain why these reviews are being locked...',
    unlock: 'Explain why these reviews are being unlocked...'
  }
  return placeholders[selectedAction.value] || 'Enter reason...'
}

const getActionAlertType = () => {
  const types = {
    submit: 'info',
    approve: 'success',
    return: 'warning',
    lock: 'error',
    unlock: 'info'
  }
  return types[selectedAction.value] || 'info'
}

const getActionIcon = () => {
  const icons = {
    submit: 'mdi-send',
    approve: 'mdi-check-circle',
    return: 'mdi-arrow-left',
    lock: 'mdi-lock',
    unlock: 'mdi-lock-open'
  }
  return icons[selectedAction.value] || 'mdi-help'
}

const getActionTitle = () => {
  const titles = {
    submit: 'Submit Reviews',
    approve: 'Approve Reviews',
    return: 'Return for Revision',
    lock: 'Lock Reviews',
    unlock: 'Unlock Reviews'
  }
  return titles[selectedAction.value] || 'Bulk Action'
}

const getActionDescription = () => {
  const descriptions = {
    submit: 'This will submit all selected reviews for final approval.',
    approve: 'This will approve all selected reviews and mark them as completed.',
    return: 'This will return all selected reviews to employees for revision.',
    lock: 'This will lock all selected reviews to prevent further editing.',
    unlock: 'This will unlock all selected reviews to allow editing.'
  }
  return descriptions[selectedAction.value] || ''
}

const getActionButtonText = () => {
  const texts = {
    submit: 'Submit Reviews',
    approve: 'Approve Reviews',
    return: 'Return Reviews',
    lock: 'Lock Reviews',
    unlock: 'Unlock Reviews'
  }
  return texts[selectedAction.value] || 'Execute Action'
}

// Methods
const executeBulkAction = async () => {
  if (!selectedAction.value) {
    toast.error('Please select an action')
    return
  }

  try {
    processing.value = true

    const reviewIds = props.selectedReviews.map(review => review.id)
    const payload = {
      review_ids: reviewIds,
      action: selectedAction.value,
      reason: actionReason.value
    }

    const response = await reviewsAPI.bulkReviewAction(payload)
    
    toast.success(response.data.message || 'Bulk action completed successfully')
    emit('action-completed')
    closeDialog()
  } catch (error) {
    console.error('Error executing bulk action:', error)
    const errorMsg = error.response?.data?.error || error.message || 'Failed to execute bulk action'
    toast.error(errorMsg)
  } finally {
    processing.value = false
  }
}

const closeDialog = () => {
  dialog.value = false
  selectedAction.value = ''
  actionReason.value = ''
}

// Status helpers
const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    in_progress: 'blue',
    submitted: 'orange',
    approved: 'success',
    returned: 'warning'
  }
  return colors[status] || 'grey'
}

const getStatusIcon = (status) => {
  const icons = {
    draft: 'mdi-pencil',
    in_progress: 'mdi-clock',
    submitted: 'mdi-send',
    approved: 'mdi-check',
    returned: 'mdi-arrow-left'
  }
  return icons[status] || 'mdi-help'
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    selectedAction.value = ''
    actionReason.value = ''
  }
})
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.max-height-300 {
  max-height: 300px;
}

.v-list-item {
  border-radius: 8px;
}

.v-alert {
  border-radius: 8px;
}
</style>
