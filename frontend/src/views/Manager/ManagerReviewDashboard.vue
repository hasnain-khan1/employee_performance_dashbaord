<template>
  <v-container fluid>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3" color="primary">mdi-clipboard-check</v-icon>
            <div>
              <h2 class="text-h4 font-weight-bold">Manager Final Review & Rating</h2>
              <p class="text-subtitle-1 text-medium-emphasis mb-0">
                Comprehensive Performance Evaluation Dashboard
              </p>
            </div>
          </v-card-title>
        </v-card>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="primary" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-2">mdi-account-group</v-icon>
            <div class="text-h4 font-weight-bold">{{ statistics.direct_reports_count || 0 }}</div>
            <div class="text-subtitle-2">Direct Reports</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="success" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-2">mdi-check-circle</v-icon>
            <div class="text-h4 font-weight-bold">{{ statistics.submitted_reviews || 0 }}</div>
            <div class="text-subtitle-2">Submitted Reviews</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="warning" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-2">mdi-clock-outline</v-icon>
            <div class="text-h4 font-weight-bold">{{ statistics.draft_reviews || 0 }}</div>
            <div class="text-subtitle-2">Draft Reviews</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card elevation="2" color="info" variant="tonal">
          <v-card-text class="text-center">
            <v-icon size="48" class="mb-2">mdi-lock</v-icon>
            <div class="text-h4 font-weight-bold">{{ statistics.locked_reviews || 0 }}</div>
            <div class="text-subtitle-2">Locked Reviews</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filters and Actions -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-text-field
          v-model="searchQuery"
          label="Search employees..."
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          clearable
          @input="filterReviews"
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-select
          v-model="statusFilter"
          label="Filter by Status"
          :items="Array.isArray(statusOptions) ? statusOptions : []"
          variant="outlined"
          clearable
          @update:model-value="filterReviews"
        />
      </v-col>
      
      <v-col cols="12" md="3">
        <v-btn
          color="primary"
          variant="elevated"
          prepend-icon="mdi-plus"
          @click="createNewReview"
          :disabled="loading"
        >
          New Review
        </v-btn>
      </v-col>
    </v-row>

    <!-- Reviews Table -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title class="d-flex align-center justify-space-between">
            <span>Employee Reviews</span>
            <v-btn
              v-if="selectedReviews.length > 0"
              color="primary"
              variant="outlined"
              @click="showBulkActions = true"
            >
              Bulk Actions ({{ selectedReviews.length }})
            </v-btn>
          </v-card-title>
          
          <v-data-table
            v-model="selectedReviews"
            :headers="headers"
            :items="Array.isArray(filteredReviews) ? filteredReviews : []"
            :loading="loading"
            item-key="id"
            show-select
            class="elevation-1"
          >
            <!-- Employee Column -->
            <template #item.employee="{ item }">
              <div class="d-flex align-center">
                <v-avatar size="32" class="mr-3">
                  <v-img
                    :src="item.employee.avatar || '/default-avatar.png'"
                    :alt="item.employee.name"
                  />
                </v-avatar>
                <div>
                  <div class="font-weight-medium">{{ item.employee.name }}</div>
                  <div class="text-caption text-medium-emphasis">{{ item.employee.position }}</div>
                </div>
              </div>
            </template>

            <!-- Status Column -->
            <template #item.status="{ item }">
              <v-chip
                :color="getStatusColor(item.status)"
                size="small"
                variant="tonal"
              >
                {{ getStatusText(item.status) }}
              </v-chip>
            </template>

            <!-- Rating Column -->
            <template #item.overall_rating="{ item }">
              <div v-if="item.overall_rating" class="d-flex align-center">
                <v-rating
                  :model-value="item.overall_rating"
                  readonly
                  size="small"
                  color="amber"
                />
                <span class="ml-2 text-caption">{{ item.overall_rating }}/5</span>
              </div>
              <span v-else class="text-medium-emphasis">Not rated</span>
            </template>

            <!-- Locked Column -->
            <template #item.is_locked="{ item }">
              <v-icon
                :color="item.is_locked ? 'error' : 'success'"
                size="small"
              >
                {{ item.is_locked ? 'mdi-lock' : 'mdi-lock-open' }}
              </v-icon>
            </template>

            <!-- Actions Column -->
            <template #item.actions="{ item }">
              <div class="d-flex align-center">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click="viewReview(item)"
                  :disabled="loading"
                />
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  @click="editReview(item)"
                  :disabled="item.is_locked || loading"
                />
                <v-btn
                  icon="mdi-dots-vertical"
                  size="small"
                  variant="text"
                  @click="showReviewMenu(item)"
                />
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <!-- Review Dialog -->
    <ManagerReviewDialog
      v-model="reviewDialog"
      :review="selectedReview"
      :employee="selectedEmployee"
      @saved="handleReviewSaved"
      @submitted="handleReviewSubmitted"
    />

    <!-- Employee Dossier Dialog -->
    <EmployeeDossierDialog
      v-model="dossierDialog"
      :employee="selectedEmployee"
      @review-created="handleReviewCreated"
    />

    <!-- Bulk Actions Dialog -->
    <BulkReviewActionsDialog
      v-model="showBulkActions"
      :selected-reviews="selectedReviews"
      @action-completed="handleBulkActionCompleted"
    />

    <!-- Review Menu -->
    <v-menu
      v-model="showMenu"
      :activator="menuActivator"
      location="bottom end"
    >
      <v-list>
        <v-list-item @click="viewReview(menuReview)">
          <template #prepend>
            <v-icon>mdi-eye</v-icon>
          </template>
          <v-list-item-title>View Review</v-list-item-title>
        </v-list-item>
        
        <v-list-item @click="editReview(menuReview)">
          <template #prepend>
            <v-icon>mdi-pencil</v-icon>
          </template>
          <v-list-item-title>Edit Review</v-list-item-title>
        </v-list-item>
        
        <v-list-item @click="viewDossier(menuReview)">
          <template #prepend>
            <v-icon>mdi-file-document-multiple</v-icon>
          </template>
          <v-list-item-title>View Dossier</v-list-item-title>
        </v-list-item>
        
        <v-divider />
        
        <v-list-item
          v-if="!menuReview.is_locked"
          @click="lockReview(menuReview)"
        >
          <template #prepend>
            <v-icon>mdi-lock</v-icon>
          </template>
          <v-list-item-title>Lock Review</v-list-item-title>
        </v-list-item>
        
        <v-list-item
          v-if="menuReview.is_locked"
          @click="unlockReview(menuReview)"
        >
          <template #prepend>
            <v-icon>mdi-lock-open</v-icon>
          </template>
          <v-list-item-title>Unlock Review</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { reviewsAPI } from '@/api/reviews'
import ManagerReviewDialog from '@/components/Manager/ManagerReviewDialog.vue'
import EmployeeDossierDialog from '@/components/Manager/EmployeeDossierDialog.vue'
import BulkReviewActionsDialog from '@/components/Manager/BulkReviewActionsDialog.vue'

// Composables
const router = useRouter()
const toast = useToast()

// Reactive data
const loading = ref(false)
const reviews = ref([])
const selectedReviews = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const reviewDialog = ref(false)
const dossierDialog = ref(false)
const showBulkActions = ref(false)
const showMenu = ref(false)
const menuActivator = ref(null)
const menuReview = ref(null)
const selectedReview = ref(null)
const selectedEmployee = ref(null)
const statistics = ref({})

// Table headers
const headers = [
  { title: 'Employee', key: 'employee', sortable: true },
  { title: 'Review Period', key: 'review_period', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Overall Rating', key: 'overall_rating', sortable: true },
  { title: 'Locked', key: 'is_locked', sortable: true },
  { title: 'Created', key: 'created_at', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

// Status options
const statusOptions = [
  { title: 'Draft', value: 'draft' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Submitted', value: 'submitted' },
  { title: 'Approved', value: 'approved' },
  { title: 'Returned', value: 'returned' }
]

// Computed properties
const filteredReviews = computed(() => {
  let filtered = reviews.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(review =>
      review.employee.name.toLowerCase().includes(query) ||
      review.employee.position.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(review => review.status === statusFilter.value)
  }

  return filtered
})

// Methods
const loadReviews = async () => {
  try {
    loading.value = true
    const response = await reviewsAPI.getManagerReviews()
    reviews.value = response.data
  } catch (error) {
    console.error('Error loading reviews:', error)
    toast.error('Failed to load reviews')
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const response = await reviewsAPI.getReviewStatistics()
    statistics.value = response.data
  } catch (error) {
    console.error('Error loading statistics:', error)
  }
}

const filterReviews = () => {
  // Filtering is handled by computed property
}

const createNewReview = () => {
  selectedReview.value = null
  selectedEmployee.value = null
  reviewDialog.value = true
}

const viewReview = (review) => {
  selectedReview.value = review
  selectedEmployee.value = review.employee
  reviewDialog.value = true
}

const editReview = (review) => {
  if (review.is_locked) {
    toast.warning('This review is locked and cannot be edited')
    return
  }
  
  selectedReview.value = review
  selectedEmployee.value = review.employee
  reviewDialog.value = true
}

const viewDossier = (review) => {
  selectedEmployee.value = review.employee
  dossierDialog.value = true
}

const showReviewMenu = (review) => {
  menuReview.value = review
  menuActivator.value = event.target
  showMenu.value = true
}

const lockReview = async (review) => {
  try {
    await reviewsAPI.lockReview(review.id)
    toast.success('Review locked successfully')
    await loadReviews()
  } catch (error) {
    console.error('Error locking review:', error)
    toast.error('Failed to lock review')
  }
}

const unlockReview = async (review) => {
  try {
    await reviewsAPI.unlockReview(review.id)
    toast.success('Review unlocked successfully')
    await loadReviews()
  } catch (error) {
    console.error('Error unlocking review:', error)
    toast.error('Failed to unlock review')
  }
}

const handleReviewSaved = () => {
  toast.success('Review saved successfully')
  loadReviews()
}

const handleReviewSubmitted = () => {
  toast.success('Review submitted successfully')
  loadReviews()
}

const handleReviewCreated = () => {
  toast.success('Review created successfully')
  loadReviews()
}

const handleBulkActionCompleted = () => {
  toast.success('Bulk action completed successfully')
  selectedReviews.value = []
  loadReviews()
}

// Status helpers
const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    in_progress: 'blue',
    submitted: 'orange',
    approved: 'green',
    returned: 'red'
  }
  return colors[status] || 'grey'
}

const getStatusText = (status) => {
  const texts = {
    draft: 'Draft',
    in_progress: 'In Progress',
    submitted: 'Submitted',
    approved: 'Approved',
    returned: 'Returned'
  }
  return texts[status] || status
}

// Lifecycle
onMounted(() => {
  loadReviews()
  loadStatistics()
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
  border-radius: 16px;
}
</style>
