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
          {{ viewingGoal ? 'View Goal' : (editingGoal ? 'Edit Goal' : 'Create New Goal') }}
        </v-card-title>

        <v-card-text class="pa-6">
          <v-form ref="goalFormRef" v-model="formValid">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="goalForm.title"
                  label="Goal Title"
                  :rules="[v => !!v || 'Title is required']"
                  :readonly="viewingGoal"
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
                  :readonly="viewingGoal"
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
                  :readonly="viewingGoal"
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="goalForm.priority"
                  :items="priorityOptions"
                  label="Priority"
                  :readonly="viewingGoal"
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
                  :readonly="viewingGoal"
                  hint="How will success be measured? Examples: 'Increase revenue by 25%', 'Complete 10 projects', 'Reduce time to 2 hours'"
                  persistent-hint
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="goalForm.target_value"
                  label="Target Value"
                  type="number"
                  :readonly="viewingGoal"
                  hint="Numeric target (optional). Example: 25, 10, 2"
                  persistent-hint
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
                  :readonly="viewingGoal"
                  required
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="goalForm.target_date"
                  label="Target Date"
                  type="date"
                  :rules="[v => !!v || 'Target date is required']"
                  :readonly="viewingGoal"
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
                  :readonly="viewingGoal"
                  hint="Enter the percentage weight for this goal (1-100%)"
                  persistent-hint
                  required
                />
              </v-col>
            </v-row>

            <!-- Weight Total Info -->
            <v-row v-if="!editingGoal">
              <v-col cols="12">
                <v-alert
                  :type="weightTotalStatus.type"
                  variant="tonal"
                  density="compact"
                  class="mb-2"
                >
                  <div class="d-flex justify-space-between align-center">
                    <span>{{ weightTotalStatus.message }}</span>
                    <v-chip :color="weightTotalStatus.chipColor" size="small">
                      {{ weightTotalStatus.total }}%
                    </v-chip>
                  </div>
                </v-alert>
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
                  :readonly="viewingGoal"
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
                  :readonly="viewingGoal"
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
                  :readonly="viewingGoal"
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
                  :readonly="viewingGoal"
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
                  :readonly="viewingGoal"
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
            {{ viewingGoal ? 'Close' : 'Cancel' }}
          </v-btn>
          <v-btn
            v-if="!editingGoal && !viewingGoal"
            color="secondary"
            variant="outlined"
            :disabled="!formValid"
            :loading="saving"
            @click="saveGoalAsDraft"
          >
            Save as Draft
          </v-btn>
          <v-btn
            v-if="!viewingGoal"
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
const viewingGoal = ref(false)
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
  // Properly map all fields from the goal
  goalForm.value = {
    title: goal.title || '',
    description: goal.description || '',
    goal_type: goal.goal_type || 'performance',
    priority: goal.priority || 'medium',
    metric: goal.metric || '',
    target_value: goal.target_value || null,
    start_date: goal.start_date || '',
    target_date: goal.target_date || '',
    weight: goal.weight || 10,
    specific: goal.specific || '',
    measurable: goal.measurable || '',
    achievable: goal.achievable || '',
    relevant: goal.relevant || '',
    time_bound: goal.time_bound || ''
  }
  goalDialog.value = true
}

const closeGoalDialog = () => {
  goalDialog.value = false
  editingGoal.value = null
  viewingGoal.value = false
  // Reset form to default values
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
    
    // Extract detailed validation errors
    let errorMsg = 'Failed to save goal'
    if (error.response?.data) {
      const data = error.response.data
      
      // Handle field-specific errors
      if (data.weight) {
        errorMsg = Array.isArray(data.weight) ? data.weight[0] : data.weight
      } else if (data.non_field_errors) {
        errorMsg = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors
      } else if (data.message) {
        errorMsg = data.message
      } else if (data.detail) {
        errorMsg = data.detail
      } else {
        // Combine all field errors
        const errors = Object.entries(data).map(([field, msgs]) => {
          const message = Array.isArray(msgs) ? msgs[0] : msgs
          return `${field}: ${message}`
        }).join('; ')
        if (errors) errorMsg = errors
      }
    } else if (error.message) {
      errorMsg = error.message
    }
    
    toast.error(errorMsg, { timeout: 8000 })
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
    
    // Extract detailed validation errors
    let errorMsg = 'Failed to save goal'
    if (error.response?.data) {
      const data = error.response.data
      
      // Handle field-specific errors
      if (data.weight) {
        errorMsg = Array.isArray(data.weight) ? data.weight[0] : data.weight
      } else if (data.non_field_errors) {
        errorMsg = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors
      } else if (data.message) {
        errorMsg = data.message
      } else if (data.detail) {
        errorMsg = data.detail
      } else {
        // Combine all field errors
        const errors = Object.entries(data).map(([field, msgs]) => {
          const message = Array.isArray(msgs) ? msgs[0] : msgs
          return `${field}: ${message}`
        }).join('; ')
        if (errors) errorMsg = errors
      }
    } else if (error.message) {
      errorMsg = error.message
    }
    
    toast.error(errorMsg, { timeout: 8000 })
  } finally {
    saving.value = false
  }
}

const viewGoal = (goal) => {
  viewingGoal.value = true
  editingGoal.value = goal
  // Populate form with goal data for viewing
  goalForm.value = {
    title: goal.title || '',
    description: goal.description || '',
    goal_type: goal.goal_type || 'performance',
    priority: goal.priority || 'medium',
    metric: goal.metric || '',
    target_value: goal.target_value || null,
    start_date: goal.start_date || '',
    target_date: goal.target_date || '',
    weight: goal.weight || 10,
    specific: goal.specific || '',
    measurable: goal.measurable || '',
    achievable: goal.achievable || '',
    relevant: goal.relevant || '',
    time_bound: goal.time_bound || ''
  }
  goalDialog.value = true
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
      await loadGoals()
    } catch (error) {
      console.error('Error submitting goal:', error)
      
      // Extract detailed validation errors
      let errorMsg = 'Failed to submit goal'
      if (error.response?.data) {
        const data = error.response.data
        
        // Handle field-specific errors
        if (data.weight) {
          errorMsg = Array.isArray(data.weight) ? data.weight[0] : data.weight
        } else if (data.non_field_errors) {
          errorMsg = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors
        } else if (data.status) {
          errorMsg = Array.isArray(data.status) ? data.status[0] : data.status
        } else if (data.message) {
          errorMsg = data.message
        } else if (data.detail) {
          errorMsg = data.detail
        } else {
          // Combine all field errors
          const errors = Object.entries(data).map(([field, msgs]) => {
            const message = Array.isArray(msgs) ? msgs[0] : msgs
            return `${field}: ${message}`
          }).join('; ')
          if (errors) errorMsg = errors
        }
      } else if (error.message) {
        errorMsg = error.message
      }
      
      toast.error(errorMsg, { timeout: 8000 })
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

// Computed properties
const weightTotalStatus = computed(() => {
  // Calculate total weight of existing goals (excluding the one being edited if any)
  const existingTotal = goals.value
    .filter(g => g.status !== 'cancelled' && (!editingGoal.value || g.id !== editingGoal.value.id))
    .reduce((sum, g) => sum + (g.weight || 0), 0)
  
  const currentWeight = parseInt(goalForm.value.weight) || 0
  const total = existingTotal + currentWeight
  
  let type = 'info'
  let message = `Total weight across all goals: ${existingTotal}% (existing) + ${currentWeight}% (this goal) = ${total}%`
  let chipColor = 'primary'
  
  if (total === 100) {
    type = 'success'
    message = '✓ Perfect! Total weight equals 100%. You can submit for approval.'
    chipColor = 'success'
  } else if (total < 100) {
    type = 'warning'
    message = `You need ${100 - total}% more to reach 100%. You can save as draft, but need 100% total to submit.`
    chipColor = 'warning'
  } else if (total > 100) {
    type = 'error'
    message = `Total weight exceeds 100% by ${total - 100}%. Please reduce the weight.`
    chipColor = 'error'
  }
  
  return { type, message, total, chipColor }
})

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