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

              <template v-slot:item.manager_name="{ item }">
                <div v-if="item.manager_name" class="d-flex align-center">
                  <v-icon size="small" class="mr-1">mdi-account-supervisor</v-icon>
                  {{ item.manager_name }}
                </div>
                <v-chip v-else size="small" variant="outlined" color="grey">
                  <v-icon start>mdi-crown</v-icon>
                  Top Level
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

              <template v-slot:item.department_name="{ item }">
                {{ item.department_name || 'Not Assigned' }}
              </template>

              <template v-slot:item.job_title="{ item }">
                {{ item.job_title || 'Not Assigned' }}
              </template>

              <template v-slot:item.hire_date="{ item }">
                {{ item.hire_date ? formatDate(item.hire_date) : 'N/A' }}
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
              <h2 class="mt-3">{{ getEmployeeFullName(selectedEmployee) }}</h2>
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
              <div class="font-weight-medium">{{ selectedEmployee.phone || 'N/A' }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Department</div>
              <div class="font-weight-medium">{{ selectedEmployee.department_name || 'Not Assigned' }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Position</div>
              <div class="font-weight-medium">{{ selectedEmployee.job_title || 'Not Assigned' }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Manager</div>
              <div class="font-weight-medium">{{ selectedEmployee.manager_name || 'N/A' }}</div>
            </v-col>
            <v-col cols="6">
              <div class="text-caption text-grey">Date Joined</div>
              <div class="font-weight-medium">{{ formatDate(selectedEmployee.hire_date) }}</div>
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

    <!-- Edit Employee Dialog -->
    <v-dialog v-model="editDialog" max-width="600" persistent>
      <v-card class="employee-edit-card">
        <v-card-title class="bg-primary">
          <span class="text-white">Edit Employee</span>
          <v-spacer></v-spacer>
          <v-btn
            icon
            variant="text"
            @click="closeEditDialog"
          >
            <v-icon color="white">mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text class="mt-4">
          <v-form ref="editFormRef">
            <v-text-field
              v-model="editForm.employee_id"
              label="Employee ID"
              variant="outlined"
              :rules="[v => !!v || 'Employee ID is required']"
              prepend-inner-icon="mdi-identifier"
            />

            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="editForm.first_name"
                  label="First Name"
                  variant="outlined"
                  :rules="[v => !!v || 'First name is required']"
                  prepend-inner-icon="mdi-account"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="editForm.last_name"
                  label="Last Name"
                  variant="outlined"
                  :rules="[v => !!v || 'Last name is required']"
                />
              </v-col>
            </v-row>

            <v-text-field
              v-model="editForm.email"
              label="Email"
              type="email"
              variant="outlined"
              :rules="[
                v => !!v || 'Email is required',
                v => /.+@.+\..+/.test(v) || 'Email must be valid'
              ]"
              prepend-inner-icon="mdi-email"
            />

            <v-text-field
              v-model="editForm.job_title"
              label="Job Title"
              variant="outlined"
              prepend-inner-icon="mdi-briefcase"
            />

            <v-select
              v-model="editForm.role"
              :items="roleOptions"
              label="Role"
              variant="outlined"
              :rules="[v => !!v || 'Role is required']"
              prepend-inner-icon="mdi-account-key"
            />

            <v-select
              v-model="editForm.status"
              :items="statusOptions"
              label="Status"
              variant="outlined"
              :rules="[v => !!v || 'Status is required']"
              prepend-inner-icon="mdi-account-check"
            />

            <v-select
              v-model="editForm.department"
              :items="departmentOptions"
              item-title="name"
              item-value="id"
              label="Department"
              variant="outlined"
              clearable
              prepend-inner-icon="mdi-domain"
            />

            <v-select
              v-model="editForm.manager"
              :items="managerOptions"
              item-title="full_name"
              item-value="id"
              label="Manager"
              variant="outlined"
              clearable
              prepend-inner-icon="mdi-account-supervisor"
              hint="Select the direct manager for this employee"
              persistent-hint
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            :loading="saving"
            @click="saveEmployee"
          >
            Save Changes
          </v-btn>
          <v-btn variant="text" @click="closeEditDialog">
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
import { authAPI } from '@/api/auth'

const toast = useToast()

// Reactive data
const employees = ref([])
const departments = ref([])
const managersList = ref([])
const loading = ref(false)
const searchQuery = ref('')
const filterRole = ref(null)
const filterStatus = ref(null)
const detailDialog = ref(false)
const editDialog = ref(false)
const selectedEmployee = ref(null)
const saving = ref(false)

const editForm = ref({
  email: '',
  first_name: '',
  last_name: '',
  role: '',
  status: '',
  job_title: '',
  employee_id: '',
  department: null,
  manager: null
})

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
  { title: 'Department', key: 'department_name', sortable: false },
  { title: 'Manager', key: 'manager_name', sortable: false },
  { title: 'Position', key: 'job_title', sortable: false },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Date Joined', key: 'hire_date', sortable: true },
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

const departmentOptions = computed(() => {
  return departments.value
})

const managerOptions = computed(() => {
  // Filter to show only employees with manager, hr, or admin role
  // and exclude the employee being edited to prevent self-assignment
  let managers = managersList.value.filter(emp => 
    ['manager', 'hr', 'admin'].includes(emp.role)
  )
  
  if (editForm.value.employee_id) {
    managers = managers.filter(emp => emp.employee_id !== editForm.value.employee_id)
  }
  
  return managers
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
  selectedEmployee.value = employee
  editForm.value = {
    email: employee.email || '',
    first_name: employee.first_name || '',
    last_name: employee.last_name || '',
    role: employee.role || 'employee',
    status: employee.status || 'active',
    job_title: employee.job_title || '',
    employee_id: employee.employee_id || '',
    department: employee.department || null,
    manager: employee.manager || null
  }
  detailDialog.value = false
  editDialog.value = true
}

const saveEmployee = async () => {
  try {
    saving.value = true
    await authAPI.updateUser(selectedEmployee.value.id, editForm.value)
    toast.success('Employee updated successfully')
    editDialog.value = false
    await loadEmployees()
  } catch (error) {
    console.error('Error updating employee:', error)
    toast.error('Failed to update employee')
  } finally {
    saving.value = false
  }
}

const closeEditDialog = () => {
  editDialog.value = false
  selectedEmployee.value = null
  editForm.value = {
    email: '',
    first_name: '',
    last_name: '',
    role: '',
    status: '',
    job_title: '',
    employee_id: '',
    department: null,
    manager: null
  }
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

const getEmployeeFullName = (employee) => {
  if (!employee) return 'N/A'
  if (employee.full_name) return employee.full_name
  const firstName = employee.first_name || ''
  const lastName = employee.last_name || ''
  return `${firstName} ${lastName}`.trim() || 'N/A'
}

const loadDepartments = async () => {
  try {
    // For now, we'll extract departments from employees
    // In the future, you could create a dedicated departments API endpoint
    const response = await authAPI.getUsers()
    const allEmployees = Array.isArray(response.data)
      ? response.data
      : (response.data?.results || [])
    
    // Extract unique departments
    const deptMap = new Map()
    allEmployees.forEach(emp => {
      if (emp.department) {
        deptMap.set(emp.department, {
          id: emp.department,
          name: emp.department_name || `Department ${emp.department}`
        })
      }
    })
    departments.value = Array.from(deptMap.values())
    
    // Set managers list with role information for filtering
    managersList.value = allEmployees.map(emp => ({
      id: emp.id,
      employee_id: emp.employee_id,
      role: emp.role,
      full_name: `${emp.first_name} ${emp.last_name} (${emp.employee_id}) - ${emp.role.toUpperCase()}`
    }))
  } catch (error) {
    console.error('Error loading departments:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadEmployees()
  loadDepartments()
})
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}

.bg-primary {
  background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
}

.employee-detail-card {
  background-color: white !important;
  opacity: 1 !important;
}

.employee-detail-card .v-card-text {
  background-color: white;
}

.employee-edit-card {
  background-color: white !important;
  opacity: 1 !important;
}

.employee-edit-card .v-card-text {
  background-color: white;
}
</style>
