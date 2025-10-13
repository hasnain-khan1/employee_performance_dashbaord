<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">Import Employee Roster</h1>
      </v-col>
    </v-row>

    <!-- Instructions Card -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-6">
          <v-card-title>
            <v-icon left>mdi-information</v-icon>
            CSV Import Instructions
          </v-card-title>
          <v-card-text>
            <v-alert type="info" variant="tonal" class="mb-4">
              <strong>Business Rules:</strong>
              <ul class="mt-2">
                <li><strong>BR-008:</strong> Email addresses must be unique within the system</li>
                <li><strong>BR-009:</strong> Manager ID must reference existing employee in the CSV or database</li>
                <li><strong>BR-010:</strong> Maximum organizational hierarchy depth of 10 reporting levels</li>
                <li><strong>BR-011:</strong> Import is atomic - either all records succeed or all fail</li>
              </ul>
            </v-alert>

            <h3 class="text-h6 mb-2">Required Columns</h3>
            <ul class="mb-4">
              <li><strong>employee_id:</strong> Unique identifier (letters, numbers, hyphens, underscores)</li>
              <li><strong>name:</strong> Full name (2-100 characters)</li>
              <li><strong>email:</strong> Valid email address (must be unique)</li>
              <li><strong>department:</strong> Department name</li>
              <li><strong>level:</strong> Employee level/grade</li>
            </ul>

            <h3 class="text-h6 mb-2">Optional Columns</h3>
            <ul class="mb-4">
              <li><strong>manager_id:</strong> Employee ID of the direct manager</li>
              <li><strong>start_date:</strong> Employment start date (YYYY-MM-DD)</li>
              <li><strong>region:</strong> Geographic location</li>
              <li><strong>job_title:</strong> Job title</li>
              <li><strong>phone:</strong> Contact phone number</li>
            </ul>

            <v-btn
              color="primary"
              prepend-icon="mdi-download"
              @click="downloadTemplate"
              variant="tonal"
            >
              Download CSV Template
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Upload Section -->
    <v-row v-if="!validationResults">
      <v-col cols="12">
        <v-card>
          <v-card-title>Step 1: Upload CSV File</v-card-title>
          <v-card-text>
            <v-file-input
              v-model="selectedFile"
              label="Select CSV File"
              accept=".csv"
              prepend-icon="mdi-file-delimited"
              show-size
              :loading="uploading"
              @change="onFileSelected"
            />

            <v-btn
              color="primary"
              :disabled="!selectedFile || uploading"
              :loading="uploading"
              @click="uploadAndValidate"
              size="large"
              block
              class="mt-4"
            >
              <v-icon left>mdi-upload</v-icon>
              Upload and Validate
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Validation Results -->
    <v-row v-if="validationResults">
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Step 2: Validation Results</span>
            <v-btn
              variant="outlined"
              prepend-icon="mdi-close"
              @click="resetUpload"
            >
              Upload Different File
            </v-btn>
          </v-card-title>
          <v-card-text>
            <!-- Summary -->
            <v-row class="mb-4">
              <v-col cols="12" md="3">
                <v-card variant="tonal" color="primary">
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ validationResults.summary.total_rows }}</div>
                    <div class="text-caption">Total Rows</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="3">
                <v-card variant="tonal" color="success">
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ validationResults.summary.valid_rows }}</div>
                    <div class="text-caption">Valid Rows</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="3">
                <v-card variant="tonal" color="error">
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ validationResults.summary.error_count }}</div>
                    <div class="text-caption">Errors</div>
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="3">
                <v-card variant="tonal" color="warning">
                  <v-card-text class="text-center">
                    <div class="text-h4">{{ validationResults.summary.warning_count }}</div>
                    <div class="text-caption">Warnings</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <!-- Import Status -->
            <v-alert
              :type="validationResults.summary.can_import ? 'success' : 'error'"
              variant="tonal"
              class="mb-4"
            >
              <template v-if="validationResults.summary.can_import">
                <v-icon>mdi-check-circle</v-icon>
                <strong>Ready to Import!</strong> All validation checks passed. You can proceed with the import.
              </template>
              <template v-else>
                <v-icon>mdi-alert-circle</v-icon>
                <strong>Cannot Import.</strong> Please fix the errors below before importing.
              </template>
            </v-alert>

            <!-- Errors List -->
            <v-expansion-panels v-if="validationResults.errors.length > 0" class="mb-4">
              <v-expansion-panel>
                <v-expansion-panel-title>
                  <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
                  <strong>{{ validationResults.errors.length }} Validation Errors</strong>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-list density="compact">
                    <v-list-item
                      v-for="(error, index) in validationResults.errors"
                      :key="index"
                      :title="`Row ${error.row_number}: ${error.field}`"
                      :subtitle="error.message"
                    >
                      <template v-slot:prepend>
                        <v-icon color="error">mdi-alert</v-icon>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <!-- Warnings List -->
            <v-expansion-panels v-if="validationResults.warnings.length > 0" class="mb-4">
              <v-expansion-panel>
                <v-expansion-panel-title>
                  <v-icon color="warning" class="mr-2">mdi-alert</v-icon>
                  <strong>{{ validationResults.warnings.length }} Warnings</strong>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-list density="compact">
                    <v-list-item
                      v-for="(warning, index) in validationResults.warnings"
                      :key="index"
                      :title="`Row ${warning.row_number}: ${warning.field}`"
                      :subtitle="warning.message"
                    >
                      <template v-slot:prepend>
                        <v-icon color="warning">mdi-alert-outline</v-icon>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <!-- Data Preview -->
            <h3 class="text-h6 mb-3">Data Preview</h3>
            <v-data-table
              :headers="previewHeaders"
              :items="previewData"
              :items-per-page="10"
              class="elevation-1"
            >
              <template v-slot:item.row_number="{ item }">
                <v-chip
                  :color="item.has_errors ? 'error' : 'success'"
                  size="small"
                >
                  {{ item.row_number }}
                </v-chip>
              </template>
              
              <template v-slot:item.full_name="{ item }">
                {{ item.full_name || `${item.first_name} ${item.last_name}` }}
              </template>
            </v-data-table>

            <!-- Import Button -->
            <v-btn
              v-if="validationResults.summary.can_import"
              color="success"
              size="large"
              block
              class="mt-4"
              :loading="importing"
              @click="confirmImport"
            >
              <v-icon left>mdi-database-import</v-icon>
              Import {{ validationResults.summary.valid_rows }} Employees
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Import Success Dialog -->
    <v-dialog v-model="importSuccessDialog" max-width="600">
      <v-card>
        <v-card-title class="bg-success">
          <v-icon left>mdi-check-circle</v-icon>
          Import Successful
        </v-card-title>
        <v-card-text class="pt-4">
          <p class="mb-2"><strong>{{ importResult.message }}</strong></p>
          <ul>
            <li>Created: {{ importResult.created_count }} new employees</li>
            <li>Updated: {{ importResult.updated_count }} existing employees</li>
            <li>Total: {{ importResult.total_processed }} employees processed</li>
          </ul>
          
          <v-alert type="success" variant="tonal" class="mt-4">
            <div class="d-flex align-center">
              <v-icon class="mr-2">mdi-information</v-icon>
              <div>
                <strong>Next Steps:</strong>
                <ul class="mt-2">
                  <li>View imported employees in the <strong>All Employees</strong> page</li>
                  <li>Verify manager relationships and organizational hierarchy</li>
                  <li>Review employee details and make any necessary adjustments</li>
                </ul>
              </div>
            </div>
          </v-alert>
          
          <v-alert type="info" variant="tonal" class="mt-2">
            All new employees have been assigned the default password: <strong>ChangeMe123!</strong>
            <br />
            They will need to change this password on first login.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="outlined"
            @click="closeSuccessDialog"
          >
            Import More
          </v-btn>
          <v-btn
            color="primary"
            @click="viewEmployees"
          >
            <v-icon left>mdi-account-group</v-icon>
            View Employees
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/api/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const toast = useToast()

// State
const selectedFile = ref(null)
const uploading = ref(false)
const importing = ref(false)
const validationResults = ref(null)
const importSuccessDialog = ref(false)
const importResult = ref({})

// Computed
const previewHeaders = computed(() => [
  { title: 'Row', key: 'row_number', sortable: true },
  { title: 'Employee ID', key: 'employee_id', sortable: false },
  { title: 'Name', key: 'full_name', sortable: false },
  { title: 'Email', key: 'email', sortable: false },
  { title: 'Department', key: 'department', sortable: false },
  { title: 'Level', key: 'level', sortable: false },
  { title: 'Manager ID', key: 'manager_id', sortable: false }
])

const previewData = computed(() => {
  if (!validationResults.value) return []
  return validationResults.value.parsed_data.slice(0, 50) // Show first 50 rows
})

// Methods
const downloadTemplate = async () => {
  try {
    const response = await authAPI.downloadTemplate()
    
    // Create blob link to download
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'employee_import_template.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    toast.success('Template downloaded successfully')
  } catch (error) {
    console.error('Error downloading template:', error)
    toast.error('Failed to download template')
  }
}

const onFileSelected = () => {
  if (selectedFile.value) {
    // Handle both single file and array format
    const file = Array.isArray(selectedFile.value) ? selectedFile.value[0] : selectedFile.value
    
    // Validate file type
    if (file && !file.name.endsWith('.csv')) {
      toast.error('Please select a CSV file')
      selectedFile.value = null
    }
  }
}

const uploadAndValidate = async () => {
  if (!selectedFile.value) {
    toast.error('Please select a file')
    return
  }

  try {
    uploading.value = true
    
    // Handle both single file and array format
    const file = Array.isArray(selectedFile.value) ? selectedFile.value[0] : selectedFile.value
    
    if (!file) {
      toast.error('Please select a file')
      return
    }
    
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await authAPI.uploadCSV(formData)
    validationResults.value = response.data
    
    if (response.data.summary.can_import) {
      toast.success('Validation passed! Ready to import.')
    } else {
      toast.warning(`Validation found ${response.data.summary.error_count} errors`)
    }
  } catch (error) {
    console.error('Error uploading CSV:', error)
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to upload and validate CSV'
    toast.error(errorMsg)
  } finally {
    uploading.value = false
  }
}

const confirmImport = async () => {
  if (!validationResults.value || !validationResults.value.summary.can_import) {
    toast.error('Cannot import data with validation errors')
    return
  }

  try {
    importing.value = true
    
    const response = await authAPI.confirmImport({
      parsed_data: validationResults.value.parsed_data
    })
    
    importResult.value = response.data
    importSuccessDialog.value = true
    
    toast.success(response.data.message)
  } catch (error) {
    console.error('Error importing data:', error)
    const errorMsg = error.response?.data?.message || error.message || 'Failed to import data'
    toast.error(errorMsg)
  } finally {
    importing.value = false
  }
}

const resetUpload = () => {
  selectedFile.value = null
  validationResults.value = null
}

const closeSuccessDialog = () => {
  importSuccessDialog.value = false
  resetUpload()
}

const viewEmployees = () => {
  importSuccessDialog.value = false
  router.push('/hr/employees')
}
</script>

<style scoped>
.v-card {
  border-radius: 8px;
}

.v-data-table {
  border-radius: 4px;
}
</style>

