<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-6">
          <h1 class="text-h4">My Goals</h1>
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
          >
            Create Goal
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-row>
      <v-col cols="12" md="4">
        <v-select
          v-model="filters.status"
          :items="statusOptions"
          label="Filter by Status"
          clearable
          @update:model-value="loadGoals"
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          v-model="filters.priority"
          :items="priorityOptions"
          label="Filter by Priority"
          clearable
          @update:model-value="loadGoals"
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-text-field
          v-model="filters.search"
          label="Search Goals"
          prepend-inner-icon="mdi-magnify"
          clearable
          @input="loadGoals"
        />
      </v-col>
    </v-row>

    <!-- Goals List -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-data-table
            :headers="headers"
            :items="goals"
            :loading="loading"
            :items-per-page="10"
            class="elevation-1"
          >
            <template v-slot:item.title="{ item }">
              <div>
                <div class="font-weight-medium">{{ item.title }}</div>
                <div class="text-caption text-grey">{{ item.description }}</div>
              </div>
            </template>

            <template v-slot:item.progress_percentage="{ item }">
              <div class="d-flex align-center">
                <v-progress-linear
                  :model-value="item.progress_percentage"
                  color="primary"
                  height="6"
                  class="mr-2"
                  style="width: 60px"
                />
                <span class="text-caption">{{ item.progress_percentage }}%</span>
              </div>
            </template>

            <template v-slot:item.status="{ item }">
              <v-chip
                :color="getStatusColor(item.status)"
                size="small"
              >
                {{ item.status }}
              </v-chip>
            </template>

            <template v-slot:item.priority="{ item }">
              <v-chip
                :color="getPriorityColor(item.priority)"
                size="small"
                variant="outlined"
              >
                {{ item.priority }}
              </v-chip>
            </template>

            <template v-slot:item.target_date="{ item }">
              {{ formatDate(item.target_date) }}
            </template>

            <template v-slot:item.actions="{ item }">
              <v-btn
                icon="mdi-eye"
                size="small"
                variant="text"
                @click="viewGoal(item)"
              />
              <v-btn
                v-if="item.status === 'draft'"
                icon="mdi-send"
                size="small"
                variant="text"
                color="primary"
                @click="submitGoalForApproval(item)"
                title="Submit for Approval"
              />
              <v-btn
                v-if="item.status === 'draft'"
                icon="mdi-pencil"
                size="small"
                variant="text"
                @click="editGoal(item)"
              />
              <v-btn
                v-if="item.status === 'draft'"
                icon="mdi-delete"
                size="small"
                variant="text"
                color="error"
                @click="deleteGoal(item)"
              />
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Create/Edit Goal Dialog -->
    <v-dialog 
      v-model="goalDialog" 
      max-width="800px"
      persistent
      :scrim="true"
    >
      <v-card elevation="8" class="goal-dialog-card">
        <v-card-title class="text-h5 bg-primary pa-4">
          {{ editingGoal ? 'Edit Goal' : 'Create New Goal' }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="goalFormRef" v-model="formValid">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="goalForm.title"
                  label="Goal Title"
                  :rules="[v => !!v || 'Title is required']"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="goalForm.description"
                  label="Description"
                  :rules="[v => !!v || 'Description is required']"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="goalForm.goal_type"
                  :items="goalTypeOptions"
                  label="Goal Type"
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="goalForm.priority"
                  :items="priorityOptions"
                  label="Priority"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="goalForm.metric"
                  label="Metric"
                  :rules="[v => !!v || 'Metric is required']"
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="goalForm.target_value"
                  label="Target Value"
                  type="number"
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="goalForm.start_date"
                  label="Start Date"
                  type="date"
                  :rules="[v => !!v || 'Start date is required']"
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="goalForm.target_date"
                  label="Target Date"
                  type="date"
                  :rules="[v => !!v || 'Target date is required']"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="goalForm.weight"
                  label="Weight (%)"
                  type="number"
                  min="1"
                  max="100"
                  :rules="[v => !!v || 'Weight is required', v => v >= 1 && v <= 100 || 'Weight must be between 1 and 100']"
                  required
                />
              </v-col>
            </v-row>

            <!-- SMART Criteria -->
            <v-divider class="my-4" />
            <h3 class="text-h6 mb-4">SMART Criteria</h3>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="goalForm.specific"
                  label="Specific - What exactly will be accomplished?"
                  :rules="[v => !!v || 'Specific criteria is required']"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="goalForm.measurable"
                  label="Measurable - How will success be measured?"
                  :rules="[v => !!v || 'Measurable criteria is required']"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="goalForm.achievable"
                  label="Achievable - Is this goal realistic and attainable?"
                  :rules="[v => !!v || 'Achievable criteria is required']"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="goalForm.relevant"
                  label="Relevant - How does this align with broader objectives?"
                  :rules="[v => !!v || 'Relevant criteria is required']"
                  required
                />
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="goalForm.time_bound"
                  label="Time-bound - What is the deadline and timeline?"
                  :rules="[v => !!v || 'Time-bound criteria is required']"
                  required
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            color="grey-darken-1"
            variant="outlined"
            @click="closeGoalDialog"
          >
            Cancel
          </v-btn>
          <v-btn
            v-if="!editingGoal"
            color="secondary"
            variant="outlined"
            :disabled="!formValid"
            :loading="saving"
            @click="saveGoalAsDraft"
          >
            Save as Draft
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            :disabled="!formValid"
            :loading="saving"
            @click="editingGoal ? saveGoal : submitGoal"
          >
            {{ editingGoal ? 'Update Goal' : 'Submit for Approval' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { goalsAPI } from '@/api/goals'
import { useToast } from 'vue-toastification'
import { format } from 'date-fns'

const toast = useToast()

// Reactive data
const goals = ref([])
const loading = ref(false)
const saving = ref(false)
const goalDialog = ref(false)
const editingGoal = ref(null)
const formValid = ref(false)
const goalFormRef = ref(null) // Template ref for v-form

const filters = ref({
  status: null,
  priority: null,
  search: ''
})

const goalForm = ref({
  title: '',
  description: '',
  goal_type: 'performance',
  priority: 'medium',
  metric: '',
  target_value: null,
  start_date: '',
  target_date: '',
  weight: 10,
  specific: '',
  measurable: '',
  achievable: '',
  relevant: '',
  time_bound: ''
})

// Options
const statusOptions = [
  { title: 'Draft', value: 'draft' },
  { title: 'Submitted', value: 'submitted' },
  { title: 'Approved', value: 'approved' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Completed', value: 'completed' },
  { title: 'Cancelled', value: 'cancelled' },
  { title: 'Overdue', value: 'overdue' }
]

const priorityOptions = [
  { title: 'Low', value: 'low' },
  { title: 'Medium', value: 'medium' },
  { title: 'High', value: 'high' },
  { title: 'Critical', value: 'critical' }
]

const goalTypeOptions = [
  { title: 'Performance', value: 'performance' },
  { title: 'Development', value: 'development' },
  { title: 'Behavioral', value: 'behavioral' },
  { title: 'Project', value: 'project' },
  { title: 'Stretch', value: 'stretch' }
]

const headers = [
  { title: 'Title', key: 'title', sortable: false },
  { title: 'Progress', key: 'progress_percentage', sortable: false },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Priority', key: 'priority', sortable: true },
  { title: 'Target Date', key: 'target_date', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

// Methods
const loadGoals = async () => {
  try {
    loading.value = true
    const params = {}
    
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.priority) params.priority = filters.value.priority
    if (filters.value.search) params.search = filters.value.search
    
    const response = await goalsAPI.getGoals(params)
    goals.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading goals:', error)
    toast.error('Failed to load goals')
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  editingGoal.value = null
  goalForm.value = {
    title: '',
    description: '',
    goal_type: 'performance',
    priority: 'medium',
    metric: '',
    target_value: null,
    start_date: '',
    target_date: '',
    weight: 10,
    specific: '',
    measurable: '',
    achievable: '',
    relevant: '',
    time_bound: ''
  }
  goalDialog.value = true
}

const editGoal = (goal) => {
  editingGoal.value = goal
  goalForm.value = { ...goal }
  goalDialog.value = true
}

const closeGoalDialog = () => {
  goalDialog.value = false
  editingGoal.value = null
}

const saveGoalAsDraft = async () => {
  await saveGoalWithStatus('draft', 'Goal saved as draft')
}

const submitGoal = async () => {
  await saveGoalWithStatus('submitted', 'Goal submitted for approval')
}

const saveGoalWithStatus = async (status, successMessage) => {
  // Validate the form
  if (goalFormRef.value) {
    const { valid } = await goalFormRef.value.validate()
    if (!valid) {
      toast.error('Please fill in all required fields')
      return
    }
  } else if (!formValid.value) {
    toast.error('Please fill in all required fields')
    return
  }

  try {
    saving.value = true
    
    // Create a clean copy of the form data (avoid circular references)
    const goalData = {
      title: goalForm.value.title,
      description: goalForm.value.description,
      goal_type: goalForm.value.goal_type,
      priority: goalForm.value.priority,
      metric: goalForm.value.metric,
      target_value: goalForm.value.target_value ? parseFloat(goalForm.value.target_value) : null,
      start_date: goalForm.value.start_date,
      target_date: goalForm.value.target_date,
      weight: goalForm.value.weight ? parseInt(goalForm.value.weight) : 10,
      specific: goalForm.value.specific,
      measurable: goalForm.value.measurable,
      achievable: goalForm.value.achievable,
      relevant: goalForm.value.relevant,
      time_bound: goalForm.value.time_bound,
      status: status
    }
    
    console.log('Saving goal with data:', goalData)
    
    const response = await goalsAPI.createGoal(goalData)
    console.log('Goal created:', response.data)
    toast.success(successMessage)
    
    closeGoalDialog()
    await loadGoals()
  } catch (error) {
    console.error('Error saving goal:', error)
    const errorMsg = error.response?.data?.message || error.message || 'Failed to save goal'
    toast.error(errorMsg)
  } finally {
    saving.value = false
  }
}

const saveGoal = async () => {
  // Validate the form
  if (goalFormRef.value) {
    const { valid } = await goalFormRef.value.validate()
    if (!valid) {
      toast.error('Please fill in all required fields')
      return
    }
  } else if (!formValid.value) {
    toast.error('Please fill in all required fields')
    return
  }

  try {
    saving.value = true
    
    // Create a clean copy of the form data (avoid circular references)
    const goalData = {
      title: goalForm.value.title,
      description: goalForm.value.description,
      goal_type: goalForm.value.goal_type,
      priority: goalForm.value.priority,
      metric: goalForm.value.metric,
      target_value: goalForm.value.target_value ? parseFloat(goalForm.value.target_value) : null,
      start_date: goalForm.value.start_date,
      target_date: goalForm.value.target_date,
      weight: goalForm.value.weight ? parseInt(goalForm.value.weight) : 10,
      specific: goalForm.value.specific,
      measurable: goalForm.value.measurable,
      achievable: goalForm.value.achievable,
      relevant: goalForm.value.relevant,
      time_bound: goalForm.value.time_bound
    }
    
    console.log('Updating goal with data:', goalData)
    
    await goalsAPI.updateGoal(editingGoal.value.id, goalData)
    toast.success('Goal updated successfully')
    
    closeGoalDialog()
    await loadGoals()
  } catch (error) {
    console.error('Error saving goal:', error)
    const errorMsg = error.response?.data?.message || error.message || 'Failed to save goal'
    toast.error(errorMsg)
    
    // Log detailed error for debugging
    if (error.response) {
      console.error('Error response:', error.response.data)
    }
  } finally {
    saving.value = false
  }
}

const viewGoal = (goal) => {
  // Navigate to goal detail view
  console.log('View goal:', goal)
}

const deleteGoal = async (goal) => {
  if (confirm('Are you sure you want to delete this goal?')) {
    try {
      await goalsAPI.deleteGoal(goal.id)
      toast.success('Goal deleted successfully')
      loadGoals()
    } catch (error) {
      console.error('Error deleting goal:', error)
      toast.error('Failed to delete goal')
    }
  }
}

const submitGoalForApproval = async (goal) => {
  if (confirm(`Submit "${goal.title}" for approval?`)) {
    try {
      await goalsAPI.updateGoal(goal.id, { status: 'submitted' })
      toast.success('Goal submitted for approval')
      loadGoals()
    } catch (error) {
      console.error('Error submitting goal:', error)
      toast.error('Failed to submit goal')
    }
  }
}

const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    submitted: 'orange',
    approved: 'blue',
    in_progress: 'primary',
    completed: 'green',
    cancelled: 'red',
    overdue: 'red'
  }
  return colors[status] || 'grey'
}

const getPriorityColor = (priority) => {
  const colors = {
    low: 'green',
    medium: 'blue',
    high: 'orange',
    critical: 'red'
  }
  return colors[priority] || 'grey'
}

const formatDate = (date) => {
  return format(new Date(date), 'MMM dd, yyyy')
}

// Lifecycle
onMounted(() => {
  loadGoals()
})
</script>

<style scoped>
.v-data-table {
  border-radius: 4px;
}

/* Ensure dialog has proper backdrop */
:deep(.v-overlay__scrim) {
  background-color: rgba(0, 0, 0, 0.7) !important;
  opacity: 1 !important;
}

/* Make card opaque and visible */
:deep(.v-dialog > .v-overlay__content > .v-card) {
  background-color: rgb(var(--v-theme-surface)) !important;
  opacity: 1 !important;
}

/* Card styling */
.v-card {
  background-color: white !important;
}

.goal-dialog-card {
  background-color: white !important;
  opacity: 1 !important;
}

.goal-dialog-card .v-card-text {
  background-color: white !important;
}

.v-card-title {
  color: white !important;
}

/* Form spacing */
.v-card-text {
  background-color: white;
}
</style>