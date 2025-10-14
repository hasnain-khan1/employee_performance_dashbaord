<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title class="d-flex justify-space-between align-center">
            <span class="text-h5">Team Feedback</span>
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="openCreateDialog"
            >
              Add Feedback
            </v-btn>
          </v-card-title>

          <v-card-text>
            <!-- Filters -->
            <v-row>
              <v-col cols="12" md="4">
                <v-select
                  v-model="filters.employee_id"
                  :items="teamMembers"
                  item-title="name"
                  item-value="id"
                  label="Filter by Employee"
                  clearable
                  @update:model-value="loadFeedback"
                />
              </v-col>
              <v-col cols="12" md="4">
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
              <v-col cols="12" md="4">
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
                />
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  @click="editFeedback(item)"
                />
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Create/Edit Feedback Dialog -->
    <v-dialog
      v-model="feedbackDialog"
      max-width="900px"
      persistent
      scrollable
    >
      <v-card elevation="8" class="feedback-dialog-card">
        <v-card-title class="text-h5 bg-primary pa-4">
          {{ editingFeedback ? 'Edit Feedback' : 'Add New Feedback' }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="feedbackFormRef" v-model="formValid">
            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="feedbackForm.employee_id"
                  :items="teamMembers"
                  item-title="name"
                  item-value="id"
                  label="Employee"
                  :rules="[v => !!v || 'Employee is required']"
                  :readonly="!!editingFeedback"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="feedbackForm.feedback_type"
                  :items="feedbackTypes"
                  item-title="title"
                  item-value="value"
                  label="Feedback Type"
                  :rules="[v => !!v || 'Type is required']"
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="feedbackForm.visibility"
                  :items="visibilityOptions"
                  item-title="title"
                  item-value="value"
                  label="Visibility"
                  :rules="[v => !!v || 'Visibility is required']"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="feedbackForm.subject"
                  label="Subject"
                  :rules="[v => !!v || 'Subject is required']"
                  hint="Brief summary of the feedback"
                  persistent-hint
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="feedbackForm.feedback"
                  label="Feedback"
                  :rules="[v => !!v || 'Feedback is required']"
                  hint="Detailed feedback for the employee"
                  persistent-hint
                  rows="4"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="feedbackForm.strengths"
                  label="Strengths (Optional)"
                  hint="Specific strengths observed"
                  persistent-hint
                  rows="3"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="feedbackForm.areas_for_improvement"
                  label="Areas for Improvement (Optional)"
                  hint="Areas for growth and development"
                  persistent-hint
                  rows="3"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="feedbackForm.action_items"
                  label="Action Items (Optional)"
                  hint="Suggested action items or next steps"
                  persistent-hint
                  rows="3"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="closeFeedbackDialog">Cancel</v-btn>
          <v-btn color="primary" @click="saveFeedback" :loading="saving">
            {{ editingFeedback ? 'Update' : 'Create' }} Feedback
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- View Feedback Dialog -->
    <v-dialog
      v-model="viewDialog"
      max-width="900px"
      scrollable
    >
      <v-card elevation="8" class="feedback-detail-card" v-if="selectedFeedback">
        <v-card-title class="text-h5 bg-primary pa-4">
          Feedback Details
        </v-card-title>

        <v-card-text class="pa-6">
          <v-row>
            <v-col cols="12" md="6">
              <div class="text-subtitle-2 text-grey">Employee</div>
              <div class="text-body-1">{{ selectedFeedback.employee_name }}</div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="text-subtitle-2 text-grey">Type</div>
              <v-chip :color="getTypeColor(selectedFeedback.feedback_type)" size="small">
                {{ formatType(selectedFeedback.feedback_type) }}
              </v-chip>
            </v-col>
          </v-row>

          <v-row class="mt-2">
            <v-col cols="12" md="6">
              <div class="text-subtitle-2 text-grey">Status</div>
              <v-chip
                :color="selectedFeedback.is_acknowledged ? 'success' : 'warning'"
                size="small"
              >
                {{ selectedFeedback.is_acknowledged ? 'Acknowledged' : 'Pending' }}
              </v-chip>
            </v-col>
            <v-col cols="12" md="6">
              <div class="text-subtitle-2 text-grey">Date</div>
              <div class="text-body-1">{{ formatDate(selectedFeedback.created_at) }}</div>
            </v-col>
          </v-row>

          <v-divider class="my-4" />

          <v-row>
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey">Subject</div>
              <div class="text-body-1">{{ selectedFeedback.subject }}</div>
            </v-col>
          </v-row>

          <v-row class="mt-2">
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey">Feedback</div>
              <div class="text-body-1">{{ selectedFeedback.feedback }}</div>
            </v-col>
          </v-row>

          <v-row class="mt-2" v-if="selectedFeedback.strengths">
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey">Strengths</div>
              <div class="text-body-1">{{ selectedFeedback.strengths }}</div>
            </v-col>
          </v-row>

          <v-row class="mt-2" v-if="selectedFeedback.areas_for_improvement">
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey">Areas for Improvement</div>
              <div class="text-body-1">{{ selectedFeedback.areas_for_improvement }}</div>
            </v-col>
          </v-row>

          <v-row class="mt-2" v-if="selectedFeedback.action_items">
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey">Action Items</div>
              <div class="text-body-1">{{ selectedFeedback.action_items }}</div>
            </v-col>
          </v-row>

          <v-divider class="my-4" v-if="selectedFeedback.employee_response" />

          <v-row v-if="selectedFeedback.employee_response">
            <v-col cols="12">
              <div class="text-subtitle-2 text-grey">Employee Response</div>
              <v-alert type="info" variant="tonal" class="mt-2">
                {{ selectedFeedback.employee_response }}
              </v-alert>
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="viewDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { feedbackAPI } from '@/api/feedback'
import { authAPI } from '@/api/auth'
import { useToast } from 'vue-toastification'

const toast = useToast()

// Data
const feedback = ref([])
const teamMembers = ref([])
const loading = ref(false)
const saving = ref(false)
const feedbackDialog = ref(false)
const viewDialog = ref(false)
const formValid = ref(false)
const feedbackFormRef = ref(null)
const editingFeedback = ref(null)
const selectedFeedback = ref(null)

// Filters
const filters = ref({
  employee_id: null,
  feedback_type: null,
  is_acknowledged: null
})

// Form
const feedbackForm = ref({
  employee_id: null,
  feedback_type: 'general',
  subject: '',
  feedback: '',
  strengths: '',
  areas_for_improvement: '',
  action_items: '',
  visibility: 'private'
})

// Options
const feedbackTypes = [
  { title: 'Recognition', value: 'recognition' },
  { title: 'Constructive', value: 'constructive' },
  { title: 'Coaching', value: 'coaching' },
  { title: 'Development', value: 'development' },
  { title: 'General', value: 'general' }
]

const visibilityOptions = [
  { title: 'Private (Manager & Employee only)', value: 'private' },
  { title: 'Visible to HR', value: 'hr' },
  { title: 'Public (Visible to all)', value: 'public' }
]

const acknowledgmentOptions = [
  { title: 'Acknowledged', value: true },
  { title: 'Pending', value: false }
]

const headers = [
  { title: 'Employee', key: 'employee_name' },
  { title: 'Type', key: 'feedback_type' },
  { title: 'Subject', key: 'subject' },
  { title: 'Status', key: 'is_acknowledged' },
  { title: 'Date', key: 'created_at' },
  { title: 'Actions', key: 'actions', sortable: false }
]

// Methods
const loadFeedback = async () => {
  try {
    loading.value = true
    const params = { view: 'given' }
    
    if (filters.value.employee_id) params.employee_id = filters.value.employee_id
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

const loadTeamMembers = async () => {
  try {
    // Get current user
    const userResponse = await authAPI.getCurrentUser()
    const currentUserId = userResponse.data.id
    
    // Get all users and filter for direct reports
    const usersResponse = await authAPI.getAllUsers()
    const allUsers = usersResponse.data.results || usersResponse.data
    
    // Filter to get direct reports (users whose manager is current user)
    const directReports = allUsers.filter(user => user.manager === currentUserId)
    
    teamMembers.value = directReports.map(member => ({
      id: member.id,
      name: member.full_name || `${member.first_name} ${member.last_name}` || member.username
    }))
  } catch (error) {
    console.error('Error loading team members:', error)
    toast.error('Failed to load team members')
  }
}

const openCreateDialog = () => {
  editingFeedback.value = null
  feedbackForm.value = {
    employee_id: null,
    feedback_type: 'general',
    subject: '',
    feedback: '',
    strengths: '',
    areas_for_improvement: '',
    action_items: '',
    visibility: 'private'
  }
  feedbackDialog.value = true
}

const editFeedback = async (item) => {
  try {
    const response = await feedbackAPI.getManagerFeedbackDetail(item.id)
    const fb = response.data
    
    editingFeedback.value = fb
    feedbackForm.value = {
      employee_id: fb.employee.id,
      feedback_type: fb.feedback_type,
      subject: fb.subject,
      feedback: fb.feedback,
      strengths: fb.strengths || '',
      areas_for_improvement: fb.areas_for_improvement || '',
      action_items: fb.action_items || '',
      visibility: fb.visibility
    }
    feedbackDialog.value = true
  } catch (error) {
    console.error('Error loading feedback details:', error)
    toast.error('Failed to load feedback details')
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

const saveFeedback = async () => {
  // Validate form
  if (feedbackFormRef.value) {
    const { valid } = await feedbackFormRef.value.validate()
    if (!valid) {
      toast.error('Please fill in all required fields')
      return
    }
  }

  try {
    saving.value = true
    
    if (editingFeedback.value) {
      await feedbackAPI.updateManagerFeedback(editingFeedback.value.id, feedbackForm.value)
      toast.success('Feedback updated successfully')
    } else {
      await feedbackAPI.createManagerFeedback(feedbackForm.value)
      toast.success('Feedback created successfully')
    }
    
    closeFeedbackDialog()
    await loadFeedback()
  } catch (error) {
    console.error('Error saving feedback:', error)
    
    let errorMsg = 'Failed to save feedback'
    if (error.response?.data) {
      const data = error.response.data
      if (data.employee_id) {
        errorMsg = Array.isArray(data.employee_id) ? data.employee_id[0] : data.employee_id
      } else if (data.detail) {
        errorMsg = data.detail
      } else if (data.message) {
        errorMsg = data.message
      }
    }
    
    toast.error(errorMsg)
  } finally {
    saving.value = false
  }
}

const closeFeedbackDialog = () => {
  feedbackDialog.value = false
  editingFeedback.value = null
  feedbackForm.value = {
    employee_id: null,
    feedback_type: 'general',
    subject: '',
    feedback: '',
    strengths: '',
    areas_for_improvement: '',
    action_items: '',
    visibility: 'private'
  }
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
  loadTeamMembers()
  loadFeedback()
})
</script>

<style scoped>
.feedback-dialog-card,
.feedback-detail-card {
  background-color: white !important;
  opacity: 1 !important;
}
</style>

