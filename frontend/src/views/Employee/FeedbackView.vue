<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title class="d-flex justify-space-between align-center">
            <span class="text-h5">Feedback from Manager</span>
            <v-chip :color="unacknowledgedCount > 0 ? 'warning' : 'success'" size="large">
              {{ unacknowledgedCount }} Pending
            </v-chip>
          </v-card-title>

          <v-card-text>
            <!-- Filters -->
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="filters.feedback_type"
                  :items="feedbackTypes"
                  item-title="title"
                  item-value="value"
                  label="Filter by Type"
                  clearable
                  @update:model-value="loadFeedback"
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="filters.is_acknowledged"
                  :items="acknowledgmentOptions"
                  item-title="title"
                  item-value="value"
                  label="Filter by Status"
                  clearable
                  @update:model-value="loadFeedback"
                />
              </v-col>
            </v-row>

            <!-- Feedback List -->
            <v-data-table
              :headers="headers"
              :items="feedback"
              :loading="loading"
              class="elevation-1"
            >
              <template v-slot:item.feedback_type="{ item }">
                <v-chip :color="getTypeColor(item.feedback_type)" size="small">
                  {{ formatType(item.feedback_type) }}
                </v-chip>
              </template>

              <template v-slot:item.is_acknowledged="{ item }">
                <v-chip
                  :color="item.is_acknowledged ? 'success' : 'warning'"
                  size="small"
                >
                  {{ item.is_acknowledged ? 'Acknowledged' : 'Pending' }}
                </v-chip>
              </template>

              <template v-slot:item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
              </template>

              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click="viewFeedback(item)"
                  title="View Feedback"
                />
                <v-btn
                  v-if="!item.is_acknowledged"
                  icon="mdi-check-circle"
                  size="small"
                  variant="text"
                  color="success"
                  @click="openAcknowledgeDialog(item)"
                  title="Acknowledge Feedback"
                />
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- View Feedback Dialog -->
    <v-dialog
      v-model="viewDialog"
      max-width="900px"
      scrollable
    >
      <v-card elevation="8" class="feedback-detail-card" v-if="selectedFeedback">
        <v-card-title class="text-h5 bg-primary pa-4">
          Feedback from {{ selectedFeedback.manager_name }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-row>
            <v-col cols="12" md="6">
              <div class="text-subtitle-2 text-grey">Type</div>
              <v-chip :color="getTypeColor(selectedFeedback.feedback_type)" size="small">
                {{ formatType(selectedFeedback.feedback_type) }}
              </v-chip>
            </v-col>
            <v-col cols="12" md="6">
              <div class="text-subtitle-2 text-grey">Date</div>
              <div class="text-body-1">{{ formatDate(selectedFeedback.created_at) }}</div>
            </v-col>
          </v-row>

          <v-row class="mt-2">
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey">Status</div>
              <v-chip
                :color="selectedFeedback.is_acknowledged ? 'success' : 'warning'"
                size="small"
              >
                {{ selectedFeedback.is_acknowledged ? 'Acknowledged' : 'Pending' }}
              </v-chip>
            </v-col>
          </v-row>

          <v-divider class="my-4" />

          <v-row>
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey">Subject</div>
              <div class="text-h6">{{ selectedFeedback.subject }}</div>
            </v-col>
          </v-row>

          <v-row class="mt-4">
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey mb-2">Feedback</div>
              <v-alert type="info" variant="tonal">
                {{ selectedFeedback.feedback }}
              </v-alert>
            </v-col>
          </v-row>

          <v-row class="mt-2" v-if="selectedFeedback.strengths">
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey mb-2">Strengths Observed</div>
              <v-alert type="success" variant="tonal">
                {{ selectedFeedback.strengths }}
              </v-alert>
            </v-col>
          </v-row>

          <v-row class="mt-2" v-if="selectedFeedback.areas_for_improvement">
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey mb-2">Areas for Improvement</div>
              <v-alert type="warning" variant="tonal">
                {{ selectedFeedback.areas_for_improvement }}
              </v-alert>
            </v-col>
          </v-row>

          <v-row class="mt-2" v-if="selectedFeedback.action_items">
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey mb-2">Action Items</div>
              <v-alert type="primary" variant="tonal">
                {{ selectedFeedback.action_items }}
              </v-alert>
            </v-col>
          </v-row>

          <v-divider class="my-4" v-if="selectedFeedback.employee_response" />

          <v-row v-if="selectedFeedback.employee_response">
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey">Your Response</div>
              <v-alert type="info" variant="outlined" class="mt-2">
                {{ selectedFeedback.employee_response }}
              </v-alert>
              <div class="text-caption text-grey mt-1">
                Acknowledged on {{ formatDate(selectedFeedback.acknowledged_at) }}
              </div>
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            v-if="!selectedFeedback.is_acknowledged"
            color="success"
            prepend-icon="mdi-check-circle"
            @click="openAcknowledgeDialogFromView"
          >
            Acknowledge
          </v-btn>
          <v-btn variant="text" @click="viewDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Acknowledge Dialog -->
    <v-dialog
      v-model="acknowledgeDialog"
      max-width="600px"
      persistent
    >
      <v-card elevation="8" class="acknowledge-dialog-card">
        <v-card-title class="text-h5 bg-success pa-4 text-white">
          Acknowledge Feedback
        </v-card-title>

        <v-card-text class="pa-6">
          <p class="text-body-1 mb-4">
            You are about to acknowledge that you have read and understood this feedback.
          </p>

          <v-textarea
            v-model="acknowledgeResponse"
            label="Your Response (Optional)"
            hint="You can add a response to this feedback"
            persistent-hint
            rows="4"
          />
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="closeAcknowledgeDialog">Cancel</v-btn>
          <v-btn
            color="success"
            @click="acknowledgeFeedback"
            :loading="acknowledging"
          >
            Acknowledge
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { feedbackAPI } from '@/api/feedback'
import { useToast } from 'vue-toastification'

const toast = useToast()

// Data
const feedback = ref([])
const loading = ref(false)
const acknowledging = ref(false)
const viewDialog = ref(false)
const acknowledgeDialog = ref(false)
const selectedFeedback = ref(null)
const feedbackToAcknowledge = ref(null)
const acknowledgeResponse = ref('')

// Filters
const filters = ref({
  feedback_type: null,
  is_acknowledged: null
})

// Options
const feedbackTypes = [
  { title: 'Recognition', value: 'recognition' },
  { title: 'Constructive', value: 'constructive' },
  { title: 'Coaching', value: 'coaching' },
  { title: 'Development', value: 'development' },
  { title: 'General', value: 'general' }
]

const acknowledgmentOptions = [
  { title: 'Acknowledged', value: true },
  { title: 'Pending', value: false }
]

const headers = [
  { title: 'Manager', key: 'manager_name' },
  { title: 'Type', key: 'feedback_type' },
  { title: 'Subject', key: 'subject' },
  { title: 'Status', key: 'is_acknowledged' },
  { title: 'Date', key: 'created_at' },
  { title: 'Actions', key: 'actions', sortable: false }
]

// Computed
const unacknowledgedCount = computed(() => {
  return feedback.value.filter(f => !f.is_acknowledged).length
})

// Methods
const loadFeedback = async () => {
  try {
    loading.value = true
    const params = { view: 'received' }
    
    if (filters.value.feedback_type) params.feedback_type = filters.value.feedback_type
    if (filters.value.is_acknowledged !== null) params.is_acknowledged = filters.value.is_acknowledged
    
    const response = await feedbackAPI.getManagerFeedback(params)
    feedback.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading feedback:', error)
    toast.error('Failed to load feedback')
  } finally {
    loading.value = false
  }
}

const viewFeedback = async (item) => {
  try {
    const response = await feedbackAPI.getManagerFeedbackDetail(item.id)
    selectedFeedback.value = response.data
    viewDialog.value = true
  } catch (error) {
    console.error('Error loading feedback details:', error)
    toast.error('Failed to load feedback details')
  }
}

const openAcknowledgeDialog = (item) => {
  feedbackToAcknowledge.value = item
  acknowledgeResponse.value = ''
  acknowledgeDialog.value = true
}

const openAcknowledgeDialogFromView = () => {
  feedbackToAcknowledge.value = selectedFeedback.value
  viewDialog.value = false
  acknowledgeResponse.value = ''
  acknowledgeDialog.value = true
}

const acknowledgeFeedback = async () => {
  try {
    acknowledging.value = true
    
    await feedbackAPI.acknowledgeFeedback(
      feedbackToAcknowledge.value.id,
      { employee_response: acknowledgeResponse.value }
    )
    
    toast.success('Feedback acknowledged successfully')
    closeAcknowledgeDialog()
    await loadFeedback()
  } catch (error) {
    console.error('Error acknowledging feedback:', error)
    toast.error('Failed to acknowledge feedback')
  } finally {
    acknowledging.value = false
  }
}

const closeAcknowledgeDialog = () => {
  acknowledgeDialog.value = false
  feedbackToAcknowledge.value = null
  acknowledgeResponse.value = ''
}

const getTypeColor = (type) => {
  const colors = {
    recognition: 'success',
    constructive: 'warning',
    coaching: 'info',
    development: 'primary',
    general: 'grey'
  }
  return colors[type] || 'grey'
}

const formatType = (type) => {
  return type.charAt(0).toUpperCase() + type.slice(1)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

// Lifecycle
onMounted(() => {
  loadFeedback()
})
</script>

<style scoped>
.feedback-detail-card,
.acknowledge-dialog-card {
  background-color: white !important;
  opacity: 1 !important;
}
</style>
