<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">
          <v-icon left class="mr-2">mdi-file-chart</v-icon>
          Reports Management
        </h1>
      </v-col>
    </v-row>

    <!-- Report Generation Card -->
    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title class="bg-primary white--text">
            <v-icon left color="white">mdi-file-plus</v-icon>
            Generate New Report
          </v-card-title>
          <v-card-text class="mt-4">
            <v-select
              v-model="newReport.type"
              :items="reportTypes"
              label="Report Type"
              variant="outlined"
            />
            
            <v-select
              v-model="newReport.format"
              :items="formatOptions"
              label="Export Format"
              variant="outlined"
            />

            <v-select
              v-model="newReport.period"
              :items="periodOptions"
              label="Time Period"
              variant="outlined"
            />

            <v-row v-if="newReport.period === 'custom'">
              <v-col cols="6">
                <v-text-field
                  v-model="newReport.startDate"
                  label="Start Date"
                  type="date"
                  variant="outlined"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="newReport.endDate"
                  label="End Date"
                  type="date"
                  variant="outlined"
                />
              </v-col>
            </v-row>

            <v-select
              v-if="['performance', 'goals', 'reviews'].includes(newReport.type)"
              v-model="newReport.departmentId"
              :items="departments"
              item-title="name"
              item-value="id"
              label="Select Department (Optional)"
              variant="outlined"
              clearable
            />

            <v-btn
              color="primary"
              block
              :loading="generating"
              @click="generateReport"
            >
              <v-icon left>mdi-file-document</v-icon>
              Generate Report
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Quick Stats -->
      <v-col cols="12" md="8">
        <v-row>
          <v-col cols="12" md="6" v-for="stat in reportStats" :key="stat.title">
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

        <v-card class="mt-4">
          <v-card-title>
            <v-icon left>mdi-information</v-icon>
            Available Report Types
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item v-for="type in reportTypes" :key="type.value">
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-file-document</v-icon>
                </template>
                <v-list-item-title>{{ type.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ getReportDescription(type.value) }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Reports List -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-file-multiple</v-icon>
            Generated Reports
            <v-spacer></v-spacer>
            <v-text-field
              v-model="searchQuery"
              label="Search Reports"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              hide-details
              clearable
              class="mr-4"
              style="max-width: 300px"
            />
            <v-select
              v-model="filterType"
              :items="[{ title: 'All Types', value: null }, ...reportTypes]"
              label="Filter by Type"
              variant="outlined"
              density="compact"
              hide-details
              style="max-width: 200px"
              @update:model-value="loadReports"
            />
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="reportHeaders"
              :items="filteredReports"
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

              <template v-slot:item.report_type="{ item }">
                <v-chip
                  :color="getTypeColor(item.report_type)"
                  size="small"
                >
                  {{ formatReportType(item.report_type) }}
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

              <template v-slot:item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
              </template>

              <template v-slot:item.actions="{ item }">
                <v-btn
                  v-if="item.status === 'completed'"
                  icon
                  size="small"
                  variant="text"
                  color="primary"
                  @click="downloadReport(item)"
                  title="Download"
                >
                  <v-icon>mdi-download</v-icon>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="info"
                  @click="viewReport(item)"
                  title="View Details"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="error"
                  @click="deleteReport(item)"
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

    <!-- Report Detail Dialog -->
    <v-dialog v-model="detailDialog" max-width="700">
      <v-card v-if="selectedReport" class="report-detail-card">
        <v-card-title class="bg-primary">
          <span class="text-white">Report Details</span>
          <v-spacer></v-spacer>
          <v-btn
            icon
            variant="text"
            @click="detailDialog = false"
          >
            <v-icon color="white">mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="mt-4">
          <v-row>
            <v-col cols="12">
              <h3>{{ selectedReport.name }}</h3>
              <p class="text-grey">{{ selectedReport.description }}</p>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Report Type</div>
              <div class="font-weight-medium">{{ formatReportType(selectedReport.report_type) }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Status</div>
              <div class="font-weight-medium">{{ formatStatus(selectedReport.status) }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Created By</div>
              <div class="font-weight-medium">{{ selectedReport.created_by?.full_name || 'System' }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Created At</div>
              <div class="font-weight-medium">{{ formatDate(selectedReport.created_at) }}</div>
            </v-col>
            <v-col cols="12" v-if="selectedReport.parameters">
              <div class="text-caption text-grey">Parameters</div>
              <pre class="text-caption">{{ JSON.stringify(selectedReport.parameters, null, 2) }}</pre>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            v-if="selectedReport.status === 'completed'"
            color="primary"
            @click="downloadReport(selectedReport)"
          >
            <v-icon left>mdi-download</v-icon>
            Download
          </v-btn>
          <v-btn variant="text" @click="detailDialog = false">
            Close
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
const reports = ref([])
const departments = ref([])
const loading = ref(false)
const generating = ref(false)
const searchQuery = ref('')
const filterType = ref(null)
const detailDialog = ref(false)
const selectedReport = ref(null)

// New report form
const newReport = ref({
  type: 'performance',
  format: 'pdf',
  period: 'current_month',
  startDate: '',
  endDate: '',
  departmentId: null
})

// Options
const reportTypes = [
  { title: 'Performance Report', value: 'performance' },
  { title: 'Goals Report', value: 'goals' },
  { title: 'Feedback Report', value: 'feedback' },
  { title: 'Reviews Report', value: 'reviews' },
  { title: 'Analytics Report', value: 'analytics' },
  { title: 'Custom Report', value: 'custom' }
]

const formatOptions = [
  { title: 'PDF', value: 'pdf' },
  { title: 'Excel (XLSX)', value: 'xlsx' },
  { title: 'CSV', value: 'csv' },
  { title: 'JSON', value: 'json' }
]

const periodOptions = [
  { title: 'Current Month', value: 'current_month' },
  { title: 'Last Month', value: 'last_month' },
  { title: 'Current Quarter', value: 'current_quarter' },
  { title: 'Last Quarter', value: 'last_quarter' },
  { title: 'Current Year', value: 'current_year' },
  { title: 'Last Year', value: 'last_year' },
  { title: 'Custom Range', value: 'custom' }
]

// Table headers
const reportHeaders = [
  { title: 'Report Name', key: 'name', sortable: true },
  { title: 'Type', key: 'report_type', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Created', key: 'created_at', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' }
]

// Computed properties
const filteredReports = computed(() => {
  let filtered = reports.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(report =>
      report.name.toLowerCase().includes(query) ||
      report.description?.toLowerCase().includes(query)
    )
  }

  if (filterType.value) {
    filtered = filtered.filter(report => report.report_type === filterType.value)
  }

  return filtered
})

const reportStats = computed(() => {
  const total = reports.value.length
  const completed = reports.value.filter(r => r.status === 'completed').length
  const pending = reports.value.filter(r => r.status === 'pending').length
  const thisMonth = reports.value.filter(r => {
    const created = new Date(r.created_at)
    const now = new Date()
    return created.getMonth() === now.getMonth() && created.getFullYear() === now.getFullYear()
  }).length

  return [
    { title: 'Total Reports', value: total, icon: 'mdi-file-multiple', color: 'primary' },
    { title: 'Completed', value: completed, icon: 'mdi-check-circle', color: 'success' },
    { title: 'Pending', value: pending, icon: 'mdi-clock-outline', color: 'orange' },
    { title: 'This Month', value: thisMonth, icon: 'mdi-calendar-month', color: 'blue' }
  ]
})

// Methods
const loadReports = async () => {
  try {
    loading.value = true
    const params = {}
    if (filterType.value) {
      params.type = filterType.value
    }
    
    const response = await api.get('/analytics/reports/', { params })
    // Handle different response formats (array, paginated results, etc.)
    reports.value = Array.isArray(response.data)
      ? response.data
      : (response.data?.results || [])
  } catch (error) {
    console.error('Error loading reports:', error)
    toast.error('Failed to load reports')
  } finally {
    loading.value = false
  }
}

const loadDepartments = async () => {
  try {
    const response = await api.get('/org/departments/')
    // Handle different response formats (array, paginated results, etc.)
    departments.value = Array.isArray(response.data)
      ? response.data
      : (response.data?.results || [])
  } catch (error) {
    console.error('Error loading departments:', error)
  }
}

const generateReport = async () => {
  try {
    generating.value = true
    
    const payload = {
      report_type: newReport.value.type,
      name: `${formatReportType(newReport.value.type)} - ${new Date().toLocaleDateString()}`,
      description: `Generated ${formatReportType(newReport.value.type)} report`,
      parameters: {
        format: newReport.value.format,
        period: newReport.value.period,
        ...(newReport.value.period === 'custom' && {
          start_date: newReport.value.startDate,
          end_date: newReport.value.endDate
        }),
        ...(newReport.value.departmentId && {
          department_id: newReport.value.departmentId
        })
      }
    }

    await api.post('/analytics/reports/', payload)
    toast.success('Report generation started successfully')
    await loadReports()
    
    // Reset form
    newReport.value = {
      type: 'performance',
      format: 'pdf',
      period: 'current_month',
      startDate: '',
      endDate: '',
      departmentId: null
    }
  } catch (error) {
    console.error('Error generating report:', error)
    toast.error('Failed to generate report')
  } finally {
    generating.value = false
  }
}

const viewReport = (report) => {
  selectedReport.value = report
  detailDialog.value = true
}

const downloadReport = async (report) => {
  try {
    toast.info('Download functionality will be implemented')
    // Implementation would involve:
    // const response = await api.get(`/analytics/reports/${report.id}/download/`, { responseType: 'blob' })
    // Create download link and trigger download
  } catch (error) {
    console.error('Error downloading report:', error)
    toast.error('Failed to download report')
  }
}

const deleteReport = async (report) => {
  if (!confirm('Are you sure you want to delete this report?')) {
    return
  }

  try {
    await api.delete(`/analytics/reports/${report.id}/`)
    toast.success('Report deleted successfully')
    await loadReports()
  } catch (error) {
    console.error('Error deleting report:', error)
    toast.error('Failed to delete report')
  }
}

const getReportDescription = (type) => {
  const descriptions = {
    performance: 'Individual employee performance metrics and ratings',
    goals: 'Overview of goal progress and completion rates',
    feedback: 'Peer feedback statistics and trends',
    reviews: 'Summary of review cycle completion and ratings',
    analytics: 'Comprehensive analytics and insights',
    custom: 'Custom report with selected parameters'
  }
  return descriptions[type] || 'No description available'
}

const getTypeColor = (type) => {
  const colors = {
    performance: 'primary',
    goals: 'green',
    feedback: 'orange',
    reviews: 'purple',
    analytics: 'blue',
    custom: 'grey'
  }
  return colors[type] || 'grey'
}

const getStatusColor = (status) => {
  const colors = {
    pending: 'orange',
    processing: 'blue',
    completed: 'success',
    failed: 'error'
  }
  return colors[status] || 'grey'
}

const formatReportType = (type) => {
  return type.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  loadReports()
  loadDepartments()
})
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}

.report-detail-card {
  background-color: white !important;
  opacity: 1 !important;
}

.report-detail-card .v-card-text {
  background-color: white;
}
</style>
