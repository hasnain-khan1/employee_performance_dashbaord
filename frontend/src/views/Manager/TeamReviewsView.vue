<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">
          <v-icon left class="mr-2">mdi-clipboard-text</v-icon>
          Team Reviews
        </h1>
      </v-col>
    </v-row>

    <!-- Review Statistics -->
    <v-row>
      <v-col cols="12" md="3" v-for="stat in reviewStats" :key="stat.title">
        <v-card :color="stat.color" dark>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon size="48" class="mr-4">{{ stat.icon }}</v-icon>
              <div>
                <div class="text-h4">{{ stat.value }}</div>
                <div class="text-body-2">{{ stat.title }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filter and Actions Bar -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filterStatus"
                  :items="statusOptions"
                  label="Filter by Status"
                  variant="outlined"
                  clearable
                  @update:model-value="loadReviews"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filterCycle"
                  :items="cycles"
                  item-title="name"
                  item-value="id"
                  label="Filter by Cycle"
                  variant="outlined"
                  clearable
                  @update:model-value="loadReviews"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="searchQuery"
                  label="Search Employee"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  clearable
                  @input="debouncedSearch"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-btn
                  color="primary"
                  block
                  @click="refreshReviews"
                >
                  <v-icon left>mdi-refresh</v-icon>
                  Refresh
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Pending Reviews -->
    <v-row v-if="pendingReviews.length > 0">
      <v-col cols="12">
        <v-card>
          <v-card-title class="bg-orange">
            <v-icon left class="mr-2">mdi-clock-alert</v-icon>
            <span class="text-white">Pending Reviews ({{ pendingReviews.length }})</span>
          </v-card-title>
          <v-card-text class="pa-0">
            <v-list>
              <v-list-item
                v-for="review in pendingReviews"
                :key="review.id"
                @click="openReviewDialog(review)"
                class="border-b"
              >
                <template v-slot:prepend>
                  <v-avatar size="48">
                    <v-img
                      v-if="review.employee?.userprofile?.avatar"
                      :src="review.employee.userprofile.avatar"
                    />
                    <v-icon v-else>mdi-account</v-icon>
                  </v-avatar>
                </template>
                
                <v-list-item-title>{{ review.employee?.full_name }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ review.cycle?.name }} - {{ formatReviewType(review.review_type) }}
                </v-list-item-subtitle>

                <template v-slot:append>
                  <v-chip size="small" color="orange">
                    {{ formatStatus(review.status) }}
                  </v-chip>
                  <v-btn
                    color="primary"
                    size="small"
                    class="ml-3"
                    @click.stop="startReview(review)"
                  >
                    Start Review
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- All Reviews Table -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left class="mr-2">mdi-clipboard-list</v-icon>
            All Team Reviews
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="reviews"
              :loading="loading"
              :items-per-page="15"
              class="elevation-1"
            >
              <template v-slot:item.employee="{ item }">
                <div class="d-flex align-center py-2">
                  <v-avatar size="40" class="mr-3">
                    <v-img
                      v-if="item.employee?.userprofile?.avatar"
                      :src="item.employee.userprofile.avatar"
                    />
                    <v-icon v-else>mdi-account-circle</v-icon>
                  </v-avatar>
                  <div>
                    <div class="font-weight-medium">{{ item.employee?.full_name }}</div>
                    <div class="text-caption text-grey">{{ item.employee?.email }}</div>
                  </div>
                </div>
              </template>

              <template v-slot:item.cycle="{ item }">
                {{ item.cycle?.name }}
              </template>

              <template v-slot:item.review_type="{ item }">
                <v-chip
                  :color="getReviewTypeColor(item.review_type)"
                  size="small"
                >
                  {{ formatReviewType(item.review_type) }}
                </v-chip>
              </template>

              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  size="small"
                >
                  {{ formatStatus(item.status) }}
                </v-chip>
              </template>

              <template v-slot:item.overall_rating="{ item }">
                <div v-if="item.overall_rating" class="d-flex align-center">
                  <v-rating
                    :model-value="item.overall_rating"
                    readonly
                    density="compact"
                    size="small"
                    color="yellow-darken-2"
                  />
                  <span class="ml-2 text-caption">({{ item.overall_rating }}/5)</span>
                </div>
                <span v-else class="text-grey">Not Rated</span>
              </template>

              <template v-slot:item.submitted_at="{ item }">
                {{ formatDate(item.submitted_at) }}
              </template>

              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="primary"
                  @click="openReviewDialog(item)"
                  title="View Details"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
                <v-btn
                  v-if="item.status === 'pending' || item.status === 'in_progress'"
                  icon
                  size="small"
                  variant="text"
                  color="success"
                  @click="startReview(item)"
                  title="Continue Review"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Review Detail/Edit Dialog -->
    <v-dialog v-model="reviewDialog" max-width="900" persistent>
      <v-card v-if="selectedReview" class="review-detail-card">
        <v-card-title class="bg-primary">
          <span class="text-white">{{ isEditing ? 'Conduct' : 'View' }} Review</span>
          <v-spacer></v-spacer>
          <v-btn
            icon
            variant="text"
            @click="closeReviewDialog"
          >
            <v-icon color="white">mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="mt-4">
          <!-- Employee Info -->
          <v-row>
            <v-col cols="12" class="text-center">
              <v-avatar size="80">
                <v-img
                  v-if="selectedReview.employee?.userprofile?.avatar"
                  :src="selectedReview.employee.userprofile.avatar"
                />
                <v-icon v-else size="80">mdi-account-circle</v-icon>
              </v-avatar>
              <h3 class="mt-3">{{ selectedReview.employee?.full_name }}</h3>
              <p class="text-grey">{{ selectedReview.employee?.position?.title }}</p>
            </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>

          <!-- Review Form -->
          <v-form v-if="isEditing" ref="reviewForm">
            <v-row>
              <v-col cols="12">
                <h4>Performance Rating</h4>
                <v-rating
                  v-model="reviewData.overall_rating"
                  color="yellow-darken-2"
                  hover
                  size="large"
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="reviewData.strengths"
                  label="Strengths"
                  rows="3"
                  variant="outlined"
                  :rules="[v => !!v || 'Strengths are required']"
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="reviewData.areas_for_improvement"
                  label="Areas for Improvement"
                  rows="3"
                  variant="outlined"
                  :rules="[v => !!v || 'Areas for improvement are required']"
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="reviewData.goals_for_next_period"
                  label="Goals for Next Period"
                  rows="3"
                  variant="outlined"
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="reviewData.manager_comments"
                  label="Manager Comments"
                  rows="4"
                  variant="outlined"
                  :rules="[v => !!v || 'Manager comments are required']"
                />
              </v-col>
            </v-row>
          </v-form>

          <!-- View Mode -->
          <v-row v-else>
            <v-col cols="6">
              <div class="text-caption text-grey">Review Type</div>
              <div class="font-weight-medium">{{ formatReviewType(selectedReview.review_type) }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Status</div>
              <div class="font-weight-medium">{{ formatStatus(selectedReview.status) }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Overall Rating</div>
              <v-rating
                v-if="selectedReview.overall_rating"
                :model-value="selectedReview.overall_rating"
                readonly
                density="compact"
                color="yellow-darken-2"
              />
              <div v-else class="font-weight-medium">Not Rated</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Submitted</div>
              <div class="font-weight-medium">{{ formatDate(selectedReview.submitted_at) }}</div>
            </v-col>
            <v-col cols="12" v-if="selectedReview.strengths">
              <div class="text-caption text-grey">Strengths</div>
              <div class="font-weight-medium">{{ selectedReview.strengths }}</div>
            </v-col>
            <v-col cols="12" v-if="selectedReview.areas_for_improvement">
              <div class="text-caption text-grey">Areas for Improvement</div>
              <div class="font-weight-medium">{{ selectedReview.areas_for_improvement }}</div>
            </v-col>
            <v-col cols="12" v-if="selectedReview.goals_for_next_period">
              <div class="text-caption text-grey">Goals for Next Period</div>
              <div class="font-weight-medium">{{ selectedReview.goals_for_next_period }}</div>
            </v-col>
            <v-col cols="12" v-if="selectedReview.manager_comments">
              <div class="text-caption text-grey">Manager Comments</div>
              <div class="font-weight-medium">{{ selectedReview.manager_comments }}</div>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            v-if="isEditing"
            color="success"
            :loading="submitting"
            @click="submitReview"
          >
            <v-icon left>mdi-check</v-icon>
            Submit Review
          </v-btn>
          <v-btn
            v-if="isEditing && selectedReview.status !== 'pending'"
            color="primary"
            :loading="submitting"
            @click="saveDraft"
          >
            <v-icon left>mdi-content-save</v-icon>
            Save Draft
          </v-btn>
          <v-btn variant="text" @click="closeReviewDialog">
            {{ isEditing ? 'Cancel' : 'Close' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/api/axios'

const toast = useToast()

// Reactive data
const reviews = ref([])
const cycles = ref([])
const loading = ref(false)
const submitting = ref(false)
const searchQuery = ref('')
const filterStatus = ref(null)
const filterCycle = ref(null)
const reviewDialog = ref(false)
const selectedReview = ref(null)
const isEditing = ref(false)

const reviewData = ref({
  overall_rating: 0,
  strengths: '',
  areas_for_improvement: '',
  goals_for_next_period: '',
  manager_comments: ''
})

// Options
const statusOptions = [
  { title: 'Pending', value: 'pending' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Completed', value: 'completed' },
  { title: 'Overdue', value: 'overdue' }
]

// Table headers
const headers = [
  { title: 'Employee', key: 'employee', sortable: false },
  { title: 'Cycle', key: 'cycle', sortable: false },
  { title: 'Type', key: 'review_type', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Rating', key: 'overall_rating', sortable: true },
  { title: 'Submitted', key: 'submitted_at', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' }
]

// Computed properties
const pendingReviews = computed(() => {
  return reviews.value.filter(r => r.status === 'pending' || r.status === 'in_progress')
})

const reviewStats = computed(() => {
  const total = reviews.value.length
  const pending = reviews.value.filter(r => r.status === 'pending').length
  const completed = reviews.value.filter(r => r.status === 'completed').length
  const avgRating = reviews.value
    .filter(r => r.overall_rating)
    .reduce((sum, r) => sum + r.overall_rating, 0) / reviews.value.filter(r => r.overall_rating).length || 0

  return [
    { title: 'Total Reviews', value: total, icon: 'mdi-clipboard-text', color: 'primary' },
    { title: 'Pending', value: pending, icon: 'mdi-clock-outline', color: 'orange' },
    { title: 'Completed', value: completed, icon: 'mdi-check-circle', color: 'success' },
    { title: 'Avg Rating', value: avgRating.toFixed(1), icon: 'mdi-star', color: 'blue' }
  ]
})

// Methods
const loadReviews = async () => {
  try {
    loading.value = true
    const params = {}
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    if (filterCycle.value) {
      params.cycle = filterCycle.value
    }

    // Add view parameter to get reviews where user is the reviewer
    params.view = 'reviewer'
    
    const response = await api.get('/reviews/', { params })
    // Handle different response formats (array, paginated results, etc.)
    reviews.value = Array.isArray(response.data)
      ? response.data
      : (response.data?.results || [])
  } catch (error) {
    console.error('Error loading reviews:', error)
    toast.error('Failed to load reviews')
  } finally {
    loading.value = false
  }
}

const loadCycles = async () => {
  try {
    const response = await api.get('/cycles/')
    // Handle different response formats (array, paginated results, etc.)
    cycles.value = Array.isArray(response.data)
      ? response.data
      : (response.data?.results || [])
  } catch (error) {
    console.error('Error loading cycles:', error)
  }
}

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadReviews()
  }, 500)
}

const refreshReviews = () => {
  loadReviews()
  toast.info('Reviews refreshed')
}

const openReviewDialog = (review) => {
  selectedReview.value = review
  isEditing.value = false
  reviewDialog.value = true
}

const startReview = (review) => {
  selectedReview.value = review
  isEditing.value = true
  reviewDialog.value = true
  
  // Populate existing data if available
  reviewData.value = {
    overall_rating: review.overall_rating || 0,
    strengths: review.strengths || '',
    areas_for_improvement: review.areas_for_improvement || '',
    goals_for_next_period: review.goals_for_next_period || '',
    manager_comments: review.manager_comments || ''
  }
}

const closeReviewDialog = () => {
  reviewDialog.value = false
  selectedReview.value = null
  isEditing.value = false
  reviewData.value = {
    overall_rating: 0,
    strengths: '',
    areas_for_improvement: '',
    goals_for_next_period: '',
    manager_comments: ''
  }
}

const submitReview = async () => {
  try {
    submitting.value = true
    
    await api.patch(`/reviews/${selectedReview.value.id}/`, {
      ...reviewData.value,
      status: 'completed',
      submitted_at: new Date().toISOString()
    })
    
    toast.success('Review submitted successfully')
    closeReviewDialog()
    await loadReviews()
  } catch (error) {
    console.error('Error submitting review:', error)
    toast.error('Failed to submit review')
  } finally {
    submitting.value = false
  }
}

const saveDraft = async () => {
  try {
    submitting.value = true
    
    await api.patch(`/reviews/${selectedReview.value.id}/`, {
      ...reviewData.value,
      status: 'in_progress'
    })
    
    toast.success('Draft saved successfully')
    closeReviewDialog()
    await loadReviews()
  } catch (error) {
    console.error('Error saving draft:', error)
    toast.error('Failed to save draft')
  } finally {
    submitting.value = false
  }
}

const getReviewTypeColor = (type) => {
  const colors = {
    self_review: 'blue',
    manager_review: 'green',
    peer_review: 'purple',
    upward_review: 'orange'
  }
  return colors[type] || 'grey'
}

const getStatusColor = (status) => {
  const colors = {
    pending: 'orange',
    in_progress: 'blue',
    completed: 'success',
    overdue: 'error'
  }
  return colors[status] || 'grey'
}

const formatReviewType = (type) => {
  return type.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatStatus = (status) => {
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatDate = (dateString) => {
  if (!dateString) return 'Not Submitted'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Lifecycle
onMounted(() => {
  loadReviews()
  loadCycles()
})
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}
.border-b {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.review-detail-card {
  background-color: white !important;
  opacity: 1 !important;
}

.review-detail-card .v-card-text {
  background-color: white;
}
</style>
