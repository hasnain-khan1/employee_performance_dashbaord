<template>
  <v-container fluid>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold text-primary">Team Goals Dashboard</h1>
            <p class="text-subtitle-1 text-grey-darken-1 mt-2">
              Review and approve goals for your direct reports
            </p>
          </div>
          <v-btn
            color="primary"
            variant="elevated"
            prepend-icon="mdi-refresh"
            @click="loadData"
            :loading="loading"
          >
            Refresh
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Summary Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4">
          <div class="d-flex align-center">
            <v-icon color="primary" size="40" class="mr-4">mdi-account-group</v-icon>
            <div>
              <div class="text-h6 font-weight-bold">{{ teamStats.totalEmployees }}</div>
              <div class="text-caption text-grey">Direct Reports</div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4">
          <div class="d-flex align-center">
            <v-icon color="warning" size="40" class="mr-4">mdi-clock-outline</v-icon>
            <div>
              <div class="text-h6 font-weight-bold">{{ teamStats.pendingApprovals }}</div>
              <div class="text-caption text-grey">Pending Review</div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4">
          <div class="d-flex align-center">
            <v-icon color="success" size="40" class="mr-4">mdi-check-circle</v-icon>
            <div>
              <div class="text-h6 font-weight-bold">{{ teamStats.approvedGoals }}</div>
              <div class="text-caption text-grey">Approved Goals</div>
            </div>
          </div>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" class="pa-4">
          <div class="d-flex align-center">
            <v-icon color="error" size="40" class="mr-4">mdi-alert-circle</v-icon>
            <div>
              <div class="text-h6 font-weight-bold">{{ teamStats.needsChanges }}</div>
              <div class="text-caption text-grey">Needs Changes</div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filters and Actions -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-text-field
          v-model="searchQuery"
          label="Search employees or goals"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          clearable
          @input="filterGoals"
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="statusFilter"
          label="Filter by status"
          :items="statusOptions"
          variant="outlined"
          clearable
          @update:model-value="filterGoals"
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="sortBy"
          label="Sort by"
          :items="sortOptions"
          variant="outlined"
          @update:model-value="sortGoals"
        />
      </v-col>
    </v-row>

    <!-- Bulk Actions -->
    <v-row v-if="selectedGoals.length > 0" class="mb-4">
      <v-col cols="12">
        <v-card elevation="1" class="pa-4">
          <div class="d-flex align-center">
            <v-icon color="primary" class="mr-2">mdi-checkbox-multiple-marked</v-icon>
            <span class="text-subtitle-1 mr-4">
              {{ selectedGoals.length }} goal(s) selected
            </span>
            <v-btn
              color="success"
              variant="outlined"
              size="small"
              class="mr-2"
              @click="bulkApprove"
              :disabled="bulkActionLoading"
            >
              <v-icon left>mdi-check</v-icon>
              Approve Selected
            </v-btn>
            <v-btn
              color="warning"
              variant="outlined"
              size="small"
              class="mr-2"
              @click="bulkRequestChanges"
              :disabled="bulkActionLoading"
            >
              <v-icon left>mdi-pencil</v-icon>
              Request Changes
            </v-btn>
            <v-btn
              color="grey"
              variant="outlined"
              size="small"
              @click="clearSelection"
            >
              Clear Selection
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Team Goals Table -->
    <v-card elevation="2">
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-account-group</v-icon>
        Team Goals Overview
        <v-spacer />
        <v-chip
          :color="getStatusColor(overallStatus)"
          variant="flat"
          size="small"
        >
          {{ overallStatus }}
        </v-chip>
      </v-card-title>
      
      <v-data-table
        v-model="selectedGoals"
        :headers="headers"
        :items="filteredGoals"
        :loading="loading"
        item-key="id"
        show-select
        class="elevation-0"
        :items-per-page="25"
      >
        <!-- Employee Column -->
        <template #item.employee="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="32" class="mr-3">
              <v-img
                v-if="item.employee.avatar"
                :src="item.employee.avatar"
                :alt="item.employee.first_name"
              />
              <v-icon v-else>mdi-account</v-icon>
            </v-avatar>
            <div>
              <div class="font-weight-medium">
                {{ item.employee.first_name }} {{ item.employee.last_name }}
              </div>
              <div class="text-caption text-grey">
                {{ item.employee.email }}
              </div>
            </div>
          </div>
        </template>

        <!-- Goal Title Column -->
        <template #item.title="{ item }">
          <div>
            <div class="font-weight-medium">{{ item.title }}</div>
            <div class="text-caption text-grey">
              {{ item.goal_type }} • {{ item.priority }}
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

        <!-- Progress Column -->
        <template #item.progress="{ item }">
          <div class="d-flex align-center">
            <v-progress-linear
              :model-value="item.progress_percentage || 0"
              :color="getProgressColor(item.progress_percentage || 0)"
              height="8"
              rounded
              class="mr-2"
              style="min-width: 60px"
            />
            <span class="text-caption">{{ item.progress_percentage || 0 }}%</span>
          </div>
        </template>

        <!-- Submission Date Column -->
        <template #item.submitted_at="{ item }">
          <div class="text-caption">
            {{ formatDate(item.created_at) }}
          </div>
        </template>

        <!-- Actions Column -->
        <template #item.actions="{ item }">
          <div class="d-flex align-center">
            <v-btn
              icon="mdi-eye"
              size="small"
              variant="text"
              @click="reviewGoal(item)"
              color="primary"
            />
            <v-btn
              v-if="item.status === 'draft' || item.status === 'pending'"
              icon="mdi-check"
              size="small"
              variant="text"
              @click="approveGoal(item)"
              color="success"
            />
            <v-btn
              v-if="item.status === 'draft' || item.status === 'pending'"
              icon="mdi-pencil"
              size="small"
              variant="text"
              @click="requestChanges(item)"
              color="warning"
            />
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Goal Review Dialog -->
    <GoalReviewDialog
      v-model="reviewDialog"
      :goal="selectedGoal"
      @goal-updated="handleGoalUpdated"
    />

    <!-- Bulk Feedback Dialog -->
    <BulkFeedbackDialog
      v-model="bulkFeedbackDialog"
      :goals="selectedGoals"
      :action="bulkAction"
      @feedback-submitted="handleBulkFeedback"
    />
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { goalsAPI } from '@/api/goals'
import GoalReviewDialog from '@/components/Manager/GoalReviewDialog.vue'
import BulkFeedbackDialog from '@/components/Manager/BulkFeedbackDialog.vue'

const router = useRouter()
const toast = useToast()

// Reactive data
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const sortBy = ref('submission_date')
const selectedGoals = ref([])
const goals = ref([])
const reviewDialog = ref(false)
const selectedGoal = ref(null)
const bulkFeedbackDialog = ref(false)
const bulkAction = ref('')
const bulkActionLoading = ref(false)

// Table headers
const headers = [
  { title: 'Employee', key: 'employee', sortable: false },
  { title: 'Goal Title', key: 'title', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Progress', key: 'progress', sortable: true },
  { title: 'Priority', key: 'priority', sortable: true },
  { title: 'Submitted', key: 'submitted_at', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

// Filter options
const statusOptions = [
  { title: 'All Statuses', value: '' },
  { title: 'Draft', value: 'draft' },
  { title: 'Pending Review', value: 'pending' },
  { title: 'Approved', value: 'approved' },
  { title: 'Needs Changes', value: 'needs_changes' },
  { title: 'Rejected', value: 'rejected' }
]

const sortOptions = [
  { title: 'Submission Date (Oldest First)', value: 'submission_date' },
  { title: 'Submission Date (Newest First)', value: '-submission_date' },
  { title: 'Employee Name', value: 'employee' },
  { title: 'Priority', value: 'priority' },
  { title: 'Status', value: 'status' }
]

// Computed properties
const teamStats = computed(() => {
  const total = goals.value.length
  const pending = goals.value.filter(g => g.status === 'pending').length
  const approved = goals.value.filter(g => g.status === 'approved').length
  const needsChanges = goals.value.filter(g => g.status === 'needs_changes').length
  
  return {
    totalEmployees: new Set(goals.value.map(g => g.employee.id)).size,
    pendingApprovals: pending,
    approvedGoals: approved,
    needsChanges: needsChanges
  }
})

const overallStatus = computed(() => {
  const pending = teamStats.value.pendingApprovals
  const total = teamStats.value.totalEmployees
  
  if (pending === 0) return 'All Goals Approved'
  if (pending === total) return 'All Goals Pending'
  return `${total - pending}/${total} Goals Approved`
})

const filteredGoals = computed(() => {
  let filtered = goals.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(goal => 
      goal.title.toLowerCase().includes(query) ||
      goal.employee.first_name.toLowerCase().includes(query) ||
      goal.employee.last_name.toLowerCase().includes(query) ||
      goal.employee.email.toLowerCase().includes(query)
    )
  }

  // Status filter
  if (statusFilter.value) {
    filtered = filtered.filter(goal => goal.status === statusFilter.value)
  }

  return filtered
})

// Methods
const loadData = async () => {
  try {
    loading.value = true
    const response = await goalsAPI.getManagerGoals()
    goals.value = response.data
  } catch (error) {
    console.error('Error loading team goals:', error)
    toast.error('Failed to load team goals')
  } finally {
    loading.value = false
  }
}

const filterGoals = () => {
  // Filtering is handled by computed property
}

const sortGoals = () => {
  // Sorting is handled by v-data-table
}

const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    pending: 'warning',
    approved: 'success',
    needs_changes: 'error',
    rejected: 'error'
  }
  return colors[status] || 'grey'
}

const getStatusText = (status) => {
  const texts = {
    draft: 'Draft',
    pending: 'Pending',
    approved: 'Approved',
    needs_changes: 'Needs Changes',
    rejected: 'Rejected'
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

const reviewGoal = (goal) => {
  selectedGoal.value = goal
  reviewDialog.value = true
}

const approveGoal = async (goal) => {
  try {
    await goalsAPI.approveGoal(goal.id, { feedback: 'Goal approved by manager' })
    toast.success('Goal approved successfully')
    await loadData()
  } catch (error) {
    console.error('Error approving goal:', error)
    toast.error('Failed to approve goal')
  }
}

const requestChanges = (goal) => {
  selectedGoal.value = goal
  reviewDialog.value = true
}

const bulkApprove = () => {
  bulkAction.value = 'approve'
  bulkFeedbackDialog.value = true
}

const bulkRequestChanges = () => {
  bulkAction.value = 'request_changes'
  bulkFeedbackDialog.value = true
}

const clearSelection = () => {
  selectedGoals.value = []
}

const handleGoalUpdated = () => {
  loadData()
}

const handleBulkFeedback = async () => {
  bulkActionLoading.value = true
  try {
    // Handle bulk actions here
    await loadData()
    clearSelection()
    toast.success('Bulk action completed successfully')
  } catch (error) {
    console.error('Error in bulk action:', error)
    toast.error('Failed to complete bulk action')
  } finally {
    bulkActionLoading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.v-data-table {
  border-radius: 8px;
}

.v-card {
  border-radius: 12px;
}

.v-chip {
  font-weight: 500;
}
</style>
