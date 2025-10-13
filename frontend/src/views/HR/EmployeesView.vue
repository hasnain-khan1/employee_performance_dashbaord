<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">
          <v-icon left class="mr-2">mdi-account-multiple</v-icon>
          All Employees
        </h1>
      </v-col>
    </v-row>

    <!-- Search and Filter Bar -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="searchQuery"
                  label="Search Employees"
                  prepend-inner-icon="mdi-magnify"
                  clearable
                  @input="debouncedSearch"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filterRole"
                  :items="roleOptions"
                  label="Filter by Role"
                  clearable
                  @update:model-value="loadEmployees"
                />
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filterStatus"
                  :items="statusOptions"
                  label="Filter by Status"
                  clearable
                  @update:model-value="loadEmployees"
                />
              </v-col>
              <v-col cols="12" md="2">
                <v-btn
                  color="primary"
                  block
                  @click="openAddEmployeeDialog"
                >
                  <v-icon left>mdi-plus</v-icon>
                  Add Employee
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Employee Statistics -->
    <v-row>
      <v-col cols="12" md="3" v-for="stat in employeeStats" :key="stat.title">
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

    <!-- Employees Table -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left class="mr-2">mdi-account-group</v-icon>
            Employee List ({{ employees.length }} total)
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="employees"
              :loading="loading"
              :items-per-page="15"
              class="elevation-1"
            >
              <template v-slot:item.full_name="{ item }">
                <div class="d-flex align-center py-2">
                  <v-avatar size="40" class="mr-3">
                    <v-img
                      v-if="item.userprofile?.avatar"
                      :src="item.userprofile.avatar"
                      :alt="item.full_name"
                    />
                    <v-icon v-else>mdi-account-circle</v-icon>
                  </v-avatar>
                  <div>
                    <div class="font-weight-medium">{{ item.full_name }}</div>
                    <div class="text-caption text-grey">{{ item.email }}</div>
                  </div>
                </div>
              </template>

              <template v-slot:item.employee_id="{ item }">
                <v-chip size="small" color="primary" variant="outlined">
                  {{ item.employee_id }}
                </v-chip>
              </template>

              <template v-slot:item.role="{ item }">
                <v-chip
                  :color="getRoleColor(item.role)"
                  size="small"
                >
                  {{ formatRole(item.role) }}
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

              <template v-slot:item.department="{ item }">
                {{ item.department?.name || 'Not Assigned' }}
              </template>

              <template v-slot:item.position="{ item }">
                {{ item.position?.title || 'Not Assigned' }}
              </template>

              <template v-slot:item.date_joined="{ item }">
                {{ formatDate(item.date_joined) }}
              </template>

              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="primary"
                  @click="viewEmployee(item)"
                  title="View Details"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="success"
                  @click="editEmployee(item)"
                  title="Edit"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  :color="item.status === 'active' ? 'error' : 'warning'"
                  @click="toggleEmployeeStatus(item)"
                  :title="item.status === 'active' ? 'Deactivate' : 'Activate'"
                >
                  <v-icon>{{ item.status === 'active' ? 'mdi-account-off' : 'mdi-account-check' }}</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Employee Detail Dialog -->
    <v-dialog v-model="detailDialog" max-width="800">
      <v-card v-if="selectedEmployee" class="employee-detail-card">
        <v-card-title class="bg-primary">
          <span class="text-white">Employee Details</span>
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
            <v-col cols="12" class="text-center">
              <v-avatar size="100">
                <v-img
                  v-if="selectedEmployee.userprofile?.avatar"
                  :src="selectedEmployee.userprofile.avatar"
                />
                <v-icon v-else size="100">mdi-account-circle</v-icon>
              </v-avatar>
              <h2 class="mt-3">{{ selectedEmployee.full_name }}</h2>
              <p class="text-grey">{{ selectedEmployee.email }}</p>
            </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>

          <v-row>
            <v-col cols="6">
              <div class="text-caption text-grey">Employee ID</div>
              <div class="font-weight-medium">{{ selectedEmployee.employee_id }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Role</div>
              <div class="font-weight-medium">{{ formatRole(selectedEmployee.role) }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Status</div>
              <div class="font-weight-medium">{{ formatStatus(selectedEmployee.status) }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Phone</div>
              <div class="font-weight-medium">{{ selectedEmployee.userprofile?.phone_number || 'N/A' }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Department</div>
              <div class="font-weight-medium">{{ selectedEmployee.department?.name || 'Not Assigned' }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Position</div>
              <div class="font-weight-medium">{{ selectedEmployee.position?.title || 'Not Assigned' }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Manager</div>
              <div class="font-weight-medium">{{ selectedEmployee.manager?.full_name || 'N/A' }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Date Joined</div>
              <div class="font-weight-medium">{{ formatDate(selectedEmployee.date_joined) }}</div>
            </v-col>
            <v-col cols="12" v-if="selectedEmployee.userprofile?.bio">
              <div class="text-caption text-grey">Bio</div>
              <div class="font-weight-medium">{{ selectedEmployee.userprofile.bio }}</div>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="editEmployee(selectedEmployee)">
            Edit Employee
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
import { authAPI } from '@/api/auth'

const toast = useToast()

// Reactive data
const employees = ref([])
const loading = ref(false)
const searchQuery = ref('')
const filterRole = ref(null)
const filterStatus = ref(null)
const detailDialog = ref(false)
const selectedEmployee = ref(null)

// Options
const roleOptions = [
  { title: 'Employee', value: 'employee' },
  { title: 'Manager', value: 'manager' },
  { title: 'HR', value: 'hr' },
  { title: 'Admin', value: 'admin' }
]

const statusOptions = [
  { title: 'Active', value: 'active' },
  { title: 'Inactive', value: 'inactive' },
  { title: 'On Leave', value: 'on_leave' },
  { title: 'Terminated', value: 'terminated' }
]

// Table headers
const headers = [
  { title: 'Employee', key: 'full_name', sortable: true },
  { title: 'Employee ID', key: 'employee_id', sortable: true },
  { title: 'Role', key: 'role', sortable: true },
  { title: 'Department', key: 'department', sortable: false },
  { title: 'Position', key: 'position', sortable: false },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Date Joined', key: 'date_joined', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' }
]

// Computed properties
const employeeStats = computed(() => {
  const total = employees.value.length
  const active = employees.value.filter(e => e.status === 'active').length
  const managers = employees.value.filter(e => e.role === 'manager').length
  const onLeave = employees.value.filter(e => e.status === 'on_leave').length

  return [
    { title: 'Total Employees', value: total, icon: 'mdi-account-group', color: 'primary' },
    { title: 'Active', value: active, icon: 'mdi-account-check', color: 'success' },
    { title: 'Managers', value: managers, icon: 'mdi-account-tie', color: 'blue' },
    { title: 'On Leave', value: onLeave, icon: 'mdi-calendar-clock', color: 'orange' }
  ]
})

// Methods
const loadEmployees = async () => {
  try {
    loading.value = true
    const params = {}
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (filterRole.value) {
      params.role = filterRole.value
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }

    const response = await authAPI.getUsers(params)
    // Handle different response formats (array, paginated results, etc.)
    employees.value = Array.isArray(response.data)
      ? response.data
      : (response.data?.results || [])
  } catch (error) {
    console.error('Error loading employees:', error)
    toast.error('Failed to load employees')
  } finally {
    loading.value = false
  }
}

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadEmployees()
  }, 500)
}

const viewEmployee = (employee) => {
  selectedEmployee.value = employee
  detailDialog.value = true
}

const editEmployee = (employee) => {
  // Navigate to edit page or open edit dialog
  toast.info('Edit functionality will be implemented')
}

const toggleEmployeeStatus = async (employee) => {
  const newStatus = employee.status === 'active' ? 'inactive' : 'active'
  try {
    // This would need to be implemented in the backend
    toast.info(`Status change to ${newStatus} will be implemented`)
    // After implementation:
    // await authAPI.updateUser(employee.id, { status: newStatus })
    // await loadEmployees()
  } catch (error) {
    console.error('Error updating employee status:', error)
    toast.error('Failed to update employee status')
  }
}

const openAddEmployeeDialog = () => {
  toast.info('Add employee functionality will be implemented')
}

const getRoleColor = (role) => {
  const colors = {
    admin: 'purple',
    hr: 'pink',
    manager: 'blue',
    employee: 'green'
  }
  return colors[role] || 'grey'
}

const getStatusColor = (status) => {
  const colors = {
    active: 'success',
    inactive: 'grey',
    on_leave: 'orange',
    terminated: 'error'
  }
  return colors[status] || 'grey'
}

const formatRole = (role) => {
  return role.charAt(0).toUpperCase() + role.slice(1)
}

const formatStatus = (status) => {
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
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

// Lifecycle
onMounted(() => {
  loadEmployees()
})
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}

.employee-detail-card {
  background-color: white !important;
  opacity: 1 !important;
}

.employee-detail-card .v-card-text {
  background-color: white;
}
</style>
