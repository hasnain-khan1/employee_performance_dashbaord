<template>
  <v-container fluid>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold text-primary">Peer Feedback</h1>
            <p class="text-subtitle-1 text-grey-darken-1 mt-2">
              Request 360-degree feedback from your colleagues
            </p>
          </div>
          <v-btn
            color="primary"
            variant="elevated"
            prepend-icon="mdi-plus"
            @click="openRequestDialog"
          >
            Request Feedback
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4">
          <div class="d-flex align-center">
            <v-icon color="primary" size="40" class="mr-4">mdi-send</v-icon>
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.sent_requests.total }}</div>
              <div class="text-caption text-grey">Requests Sent</div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4">
          <div class="d-flex align-center">
            <v-icon color="success" size="40" class="mr-4">mdi-check-circle</v-icon>
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.sent_requests.completed }}</div>
              <div class="text-caption text-grey">Completed</div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4">
          <div class="d-flex align-center">
            <v-icon color="warning" size="40" class="mr-4">mdi-clock-outline</v-icon>
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.received_requests.pending }}</div>
              <div class="text-caption text-grey">Pending Review</div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4">
          <div class="d-flex align-center">
            <v-icon color="error" size="40" class="mr-4">mdi-alert-circle</v-icon>
            <div>
              <div class="text-h6 font-weight-bold">{{ stats.received_requests.overdue }}</div>
              <div class="text-caption text-grey">Overdue</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabs -->
    <v-card elevation="2">
      <v-tabs v-model="activeTab" color="primary">
        <v-tab value="sent">My Requests</v-tab>
        <v-tab value="received">Feedback to Provide</v-tab>
      </v-tabs>

      <v-tab-window v-model="activeTab">
        <!-- Sent Requests Tab -->
        <v-tab-window-item value="sent">
          <v-card-text class="pa-0">
            <v-data-table
              :headers="sentHeaders"
              :items="Array.isArray(sentRequests) ? sentRequests : []"
              :loading="loading"
              class="elevation-0"
              :items-per-page="10"
            >
              <!-- Status Column -->
              <template #item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  variant="flat"
                  size="small"
                >
                  {{ getStatusText(item.status) }}
                </v-chip>
              </template>

              <!-- Progress Column -->
              <template #item.progress="{ item }">
                <div class="d-flex align-center">
                  <v-progress-linear
                    :model-value="item.completion_percentage"
                    :color="getProgressColor(item.completion_percentage)"
                    height="8"
                    rounded
                    class="mr-2"
                    style="min-width: 60px"
                  />
                  <span class="text-caption">{{ item.completion_percentage }}%</span>
                </div>
              </template>

              <!-- Deadline Column -->
              <template #item.deadline="{ item }">
                <div class="text-caption">
                  {{ formatDate(item.deadline) }}
                  <v-chip
                    v-if="item.is_expired"
                    color="error"
                    variant="flat"
                    size="x-small"
                    class="ml-2"
                  >
                    Expired
                  </v-chip>
                </div>
              </template>

              <!-- Actions Column -->
              <template #item.actions="{ item }">
                <div class="d-flex align-center">
                  <v-btn
                    icon="mdi-eye"
                    size="small"
                    variant="text"
                    @click="viewRequest(item)"
                    color="primary"
                  />
                  <v-btn
                    v-if="item.status === 'draft'"
                    icon="mdi-pencil"
                    size="small"
                    variant="text"
                    @click="editRequest(item)"
                    color="warning"
                  />
                  <v-btn
                    v-if="item.status === 'sent'"
                    icon="mdi-close"
                    size="small"
                    variant="text"
                    @click="cancelRequest(item)"
                    color="error"
                  />
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-tab-window-item>

        <!-- Received Requests Tab -->
        <v-tab-window-item value="received">
          <v-card-text class="pa-0">
            <v-data-table
              :headers="receivedHeaders"
              :items="Array.isArray(receivedRequests) ? receivedRequests : []"
              :loading="loading"
              class="elevation-0"
              :items-per-page="10"
            >
              <!-- Requester Column -->
              <template #item.requester="{ item }">
                <div class="d-flex align-center">
                  <v-avatar size="32" class="mr-3">
                    <v-img
                      v-if="item.requester.avatar"
                      :src="item.requester.avatar"
                      :alt="item.requester.first_name"
                    />
                    <v-icon v-else>mdi-account</v-icon>
                  </v-avatar>
                  <div>
                    <div class="font-weight-medium">
                      {{ item.requester.first_name }} {{ item.requester.last_name }}
                    </div>
                    <div class="text-caption text-grey">
                      {{ item.requester.department }}
                    </div>
                  </div>
                </div>
              </template>

              <!-- Status Column -->
              <template #item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  variant="flat"
                  size="small"
                >
                  {{ getStatusText(item.status) }}
                </v-chip>
              </template>

              <!-- Deadline Column -->
              <template #item.deadline="{ item }">
                <div class="text-caption">
                  {{ formatDate(item.deadline) }}
                  <v-chip
                    v-if="item.is_expired"
                    color="error"
                    variant="flat"
                    size="x-small"
                    class="ml-2"
                  >
                    Overdue
                  </v-chip>
                </div>
              </template>

              <!-- Actions Column -->
              <template #item.actions="{ item }">
                <div class="d-flex align-center">
                  <v-btn
                    icon="mdi-eye"
                    size="small"
                    variant="text"
                    @click="viewRequest(item)"
                    color="primary"
                  />
                  <v-btn
                    v-if="item.status === 'sent'"
                    color="primary"
                    variant="elevated"
                    size="small"
                    @click="provideFeedback(item)"
                  >
                    Provide Feedback
                  </v-btn>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-tab-window-item>
      </v-tab-window>
    </v-card>

    <!-- Request Feedback Dialog -->
    <RequestFeedbackDialog
      v-model="requestDialog"
      @feedback-requested="handleFeedbackRequested"
    />

    <!-- Provide Feedback Dialog -->
    <ProvideFeedbackDialog
      v-model="feedbackDialog"
      :request="selectedRequest"
      @feedback-provided="handleFeedbackProvided"
    />
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { feedbackAPI } from '@/api/feedback'
import RequestFeedbackDialog from '@/components/Employee/RequestFeedbackDialog.vue'
import ProvideFeedbackDialog from '@/components/Employee/ProvideFeedbackDialog.vue'

const toast = useToast()

// Reactive data
const loading = ref(false)
const activeTab = ref('sent')
const requestDialog = ref(false)
const feedbackDialog = ref(false)
const selectedRequest = ref(null)
const sentRequests = ref([])
const receivedRequests = ref([])
const stats = ref({
  sent_requests: { total: 0, completed: 0, in_progress: 0, expired: 0 },
  received_requests: { total: 0, completed: 0, pending: 0, overdue: 0 }
})

// Table headers
const sentHeaders = [
  { title: 'Title', key: 'title', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Progress', key: 'progress', sortable: true },
  { title: 'Deadline', key: 'deadline', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

const receivedHeaders = [
  { title: 'Requester', key: 'requester', sortable: false },
  { title: 'Title', key: 'title', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Deadline', key: 'deadline', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

// Methods
const loadData = async () => {
  try {
    loading.value = true
    
    // Load sent requests
    const sentResponse = await feedbackAPI.getFeedbackRequests({ view: 'sent' })
    sentRequests.value = sentResponse.data
    
    // Load received requests
    const receivedResponse = await feedbackAPI.getFeedbackRequests({ view: 'received' })
    receivedRequests.value = receivedResponse.data
    
    // Load statistics
    const statsResponse = await feedbackAPI.getFeedbackStatistics()
    stats.value = statsResponse.data
    
  } catch (error) {
    console.error('Error loading peer feedback data:', error)
    toast.error('Failed to load peer feedback data')
  } finally {
    loading.value = false
  }
}

const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    sent: 'primary',
    in_progress: 'warning',
    completed: 'success',
    expired: 'error',
    cancelled: 'grey'
  }
  return colors[status] || 'grey'
}

const getStatusText = (status) => {
  const texts = {
    draft: 'Draft',
    sent: 'Sent',
    in_progress: 'In Progress',
    completed: 'Completed',
    expired: 'Expired',
    cancelled: 'Cancelled'
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

const openRequestDialog = () => {
  requestDialog.value = true
}

const viewRequest = (request) => {
  selectedRequest.value = request
  // TODO: Implement view request details
}

const editRequest = (request) => {
  selectedRequest.value = request
  requestDialog.value = true
}

const cancelRequest = async (request) => {
  try {
    await feedbackAPI.cancelFeedbackRequest(request.id)
    toast.success('Feedback request cancelled')
    await loadData()
  } catch (error) {
    console.error('Error cancelling request:', error)
    toast.error('Failed to cancel request')
  }
}

const provideFeedback = (request) => {
  selectedRequest.value = request
  feedbackDialog.value = true
}

const handleFeedbackRequested = () => {
  requestDialog.value = false
  loadData()
  toast.success('Feedback request sent successfully')
}

const handleFeedbackProvided = () => {
  feedbackDialog.value = false
  loadData()
  toast.success('Feedback provided successfully')
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.v-card {
  border-radius: 8px;
}

.v-chip {
  font-weight: 500;
}
</style>
