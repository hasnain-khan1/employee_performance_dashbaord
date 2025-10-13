<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center justify-space-between mb-6">
          <div>
            <h1 class="text-h4 font-weight-bold">
              <v-icon left class="mr-2">mdi-calendar-clock</v-icon>
              Review Cycles
            </h1>
            <p class="text-subtitle-1 text-grey mt-2">
              Manage performance review cycles and timelines
            </p>
          </div>
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="openCreateDialog"
          >
            Create Cycle
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- Cycle Statistics -->
    <v-row>
      <v-col cols="12" md="3" v-for="stat in cycleStats" :key="stat.title">
        <v-card :color="stat.color" dark elevation="2">
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

    <!-- Active Cycles -->
    <v-row v-if="activeCycles.length > 0">
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title class="bg-success">
            <v-icon left color="white">mdi-play-circle</v-icon>
            <span class="text-white">Active Cycles ({{ activeCycles.length }})</span>
          </v-card-title>
          <v-card-text class="pa-0">
            <v-expansion-panels>
              <v-expansion-panel
                v-for="cycle in activeCycles"
                :key="cycle.id"
              >
                <v-expansion-panel-title>
                  <div class="d-flex align-center justify-space-between w-100 pr-4">
                    <div>
                      <div class="font-weight-bold">{{ cycle.name }}</div>
                      <div class="text-caption text-grey">{{ formatDateRange(cycle.start_date, cycle.end_date) }}</div>
                    </div>
                    <v-chip color="success" size="small">Active</v-chip>
                  </div>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-row>
                    <v-col cols="12" md="6">
                      <div class="text-caption text-grey">Description</div>
                      <p>{{ cycle.description }}</p>
                    </v-col>
                    <v-col cols="6" md="3">
                      <div class="text-caption text-grey">Start Date</div>
                      <div class="font-weight-medium">{{ formatDate(cycle.start_date) }}</div>
                    </v-col>
                    <v-col cols="6" md="3">
                      <div class="text-caption text-grey">End Date</div>
                      <div class="font-weight-medium">{{ formatDate(cycle.end_date) }}</div>
                    </v-col>
                  </v-row>
                  <v-divider class="my-3"></v-divider>
                  <v-btn
                    color="primary"
                    size="small"
                    class="mr-2"
                    @click="editCycle(cycle)"
                  >
                    <v-icon left size="small">mdi-pencil</v-icon>
                    Edit
                  </v-btn>
                  <v-btn
                    color="warning"
                    size="small"
                    @click="completeCycle(cycle)"
                  >
                    <v-icon left size="small">mdi-check</v-icon>
                    Complete
                  </v-btn>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- All Cycles Table -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon left class="mr-2">mdi-calendar-multiple</v-icon>
            All Review Cycles
            <v-spacer></v-spacer>
            <v-select
              v-model="filterStatus"
              :items="statusOptions"
              label="Filter by Status"
              variant="outlined"
              density="compact"
              hide-details
              style="max-width: 200px"
              @update:model-value="loadCycles"
            />
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="cycles"
              :loading="loading"
              :items-per-page="10"
              class="elevation-1"
            >
              <template v-slot:item.name="{ item }">
                <div>
                  <div class="font-weight-medium">{{ item.name }}</div>
                  <div class="text-caption text-grey">{{ item.description }}</div>
                </div>
              </template>

              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  size="small"
                >
                  {{ formatStatus(item.status) }}
                </v-chip>
              </template>

              <template v-slot:item.date_range="{ item }">
                {{ formatDateRange(item.start_date, item.end_date) }}
              </template>

              <template v-slot:item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
              </template>

              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="primary"
                  @click="viewCycle(item)"
                  title="View Details"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="success"
                  @click="editCycle(item)"
                  title="Edit"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn
                  v-if="item.status !== 'completed'"
                  icon
                  size="small"
                  variant="text"
                  color="error"
                  @click="deleteCycle(item)"
                  title="Delete"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Create/Edit Dialog -->
    <v-dialog v-model="dialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="bg-primary">
          <span class="text-white">{{ isEditing ? 'Edit' : 'Create' }} Review Cycle</span>
          <v-spacer></v-spacer>
          <v-btn
            icon
            variant="text"
            @click="closeDialog"
          >
            <v-icon color="white">mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="mt-4">
          <v-form ref="form">
            <v-text-field
              v-model="formData.name"
              label="Cycle Name"
              variant="outlined"
              :rules="[v => !!v || 'Name is required']"
            />

            <v-textarea
              v-model="formData.description"
              label="Description"
              variant="outlined"
              rows="3"
              :rules="[v => !!v || 'Description is required']"
            />

            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="formData.start_date"
                  label="Start Date"
                  type="date"
                  variant="outlined"
                  :rules="[v => !!v || 'Start date is required']"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="formData.end_date"
                  label="End Date"
                  type="date"
                  variant="outlined"
                  :rules="[v => !!v || 'End date is required']"
                />
              </v-col>
            </v-row>

            <v-select
              v-model="formData.status"
              :items="statusOptions"
              label="Status"
              variant="outlined"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            :loading="saving"
            @click="saveCycle"
          >
            {{ isEditing ? 'Update' : 'Create' }}
          </v-btn>
          <v-btn variant="text" @click="closeDialog">
            Cancel
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
const cycles = ref([])
const loading = ref(false)
const saving = ref(false)
const dialog = ref(false)
const isEditing = ref(false)
const filterStatus = ref(null)

const formData = ref({
  name: '',
  description: '',
  start_date: '',
  end_date: '',
  status: 'draft'
})

const selectedCycle = ref(null)

// Options
const statusOptions = [
  { title: 'All', value: null },
  { title: 'Draft', value: 'draft' },
  { title: 'Active', value: 'active' },
  { title: 'Completed', value: 'completed' },
  { title: 'Cancelled', value: 'cancelled' }
]

// Table headers
const headers = [
  { title: 'Cycle Name', key: 'name', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Date Range', key: 'date_range', sortable: false },
  { title: 'Created', key: 'created_at', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' }
]

// Computed properties
const activeCycles = computed(() => {
  return cycles.value.filter(c => c.status === 'active')
})

const cycleStats = computed(() => {
  const total = cycles.value.length
  const active = cycles.value.filter(c => c.status === 'active').length
  const completed = cycles.value.filter(c => c.status === 'completed').length
  const draft = cycles.value.filter(c => c.status === 'draft').length

  return [
    { title: 'Total Cycles', value: total, icon: 'mdi-calendar-multiple', color: 'primary' },
    { title: 'Active', value: active, icon: 'mdi-play-circle', color: 'success' },
    { title: 'Completed', value: completed, icon: 'mdi-check-circle', color: 'blue' },
    { title: 'Draft', value: draft, icon: 'mdi-file-document-edit', color: 'orange' }
  ]
})

// Methods
const loadCycles = async () => {
  try {
    loading.value = true
    const params = {}
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    
    const response = await api.get('/cycles/', { params })
    // Handle different response formats (array, paginated results, etc.)
    cycles.value = Array.isArray(response.data)
      ? response.data
      : (response.data?.results || [])
  } catch (error) {
    console.error('Error loading cycles:', error)
    toast.error('Failed to load review cycles')
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEditing.value = false
  formData.value = {
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    status: 'draft'
  }
  dialog.value = true
}

const editCycle = (cycle) => {
  isEditing.value = true
  selectedCycle.value = cycle
  formData.value = {
    name: cycle.name,
    description: cycle.description,
    start_date: cycle.start_date,
    end_date: cycle.end_date,
    status: cycle.status
  }
  dialog.value = true
}

const viewCycle = (cycle) => {
  // Could open a detailed view dialog
  toast.info('View cycle details')
}

const saveCycle = async () => {
  try {
    saving.value = true
    
    if (isEditing.value && selectedCycle.value) {
      await api.patch(`/cycles/${selectedCycle.value.id}/`, formData.value)
      toast.success('Cycle updated successfully')
    } else {
      await api.post('/cycles/', formData.value)
      toast.success('Cycle created successfully')
    }
    
    closeDialog()
    await loadCycles()
  } catch (error) {
    console.error('Error saving cycle:', error)
    toast.error('Failed to save cycle')
  } finally {
    saving.value = false
  }
}

const completeCycle = async (cycle) => {
  if (!confirm(`Are you sure you want to complete "${cycle.name}"?`)) {
    return
  }

  try {
    await api.patch(`/cycles/${cycle.id}/`, { status: 'completed' })
    toast.success('Cycle marked as completed')
    await loadCycles()
  } catch (error) {
    console.error('Error completing cycle:', error)
    toast.error('Failed to complete cycle')
  }
}

const deleteCycle = async (cycle) => {
  if (!confirm(`Are you sure you want to delete "${cycle.name}"?`)) {
    return
  }

  try {
    await api.delete(`/cycles/${cycle.id}/`)
    toast.success('Cycle deleted successfully')
    await loadCycles()
  } catch (error) {
    console.error('Error deleting cycle:', error)
    toast.error('Failed to delete cycle')
  }
}

const closeDialog = () => {
  dialog.value = false
  isEditing.value = false
  selectedCycle.value = null
}

const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    active: 'success',
    completed: 'blue',
    cancelled: 'error'
  }
  return colors[status] || 'grey'
}

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDateRange = (startDate, endDate) => {
  return `${formatDate(startDate)} - ${formatDate(endDate)}`
}

// Lifecycle
onMounted(() => {
  loadCycles()
})
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}

.bg-primary {
  background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
}

.bg-success {
  background: linear-gradient(135deg, #388E3C 0%, #2E7D32 100%);
}
</style>
