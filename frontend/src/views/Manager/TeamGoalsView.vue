<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">Team Goals</h1>
      </v-col>
    </v-row>

    <!-- Team Overview -->
    <v-row>
      <v-col cols="12" md="3" v-for="stat in teamStats" :key="stat.title">
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

    <!-- Team Members -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-account-group</v-icon>
            Team Members
          </v-card-title>

          <v-card-text>
            <v-data-table
              :headers="memberHeaders"
              :items="teamMembers"
              :loading="loading"
              :items-per-page="10"
              class="elevation-1"
            >
              <template v-slot:item.name="{ item }">
                <div class="d-flex align-center">
                  <v-avatar size="32" class="mr-3">
                    <v-img
                      v-if="item.avatar"
                      :src="item.avatar"
                      :alt="item.name"
                    />
                    <v-icon v-else>mdi-account</v-icon>
                  </v-avatar>
                  <div>
                    <div class="font-weight-medium">{{ item.name }}</div>
                    <div class="text-caption text-grey">{{ item.employee_id }}</div>
                  </div>
                </div>
              </template>

              <template v-slot:item.goals_count="{ item }">
                <v-chip
                  :color="getGoalsCountColor(item.goals_count)"
                  size="small"
                >
                  {{ item.goals_count }} goals
                </v-chip>
              </template>

              <template v-slot:item.completion_rate="{ item }">
                <div class="d-flex align-center">
                  <v-progress-linear
                    :model-value="item.completion_rate"
                    color="primary"
                    height="6"
                    class="mr-2"
                    style="width: 60px"
                  />
                  <span class="text-caption">{{ item.completion_rate }}%</span>
                </div>
              </template>

              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click="viewMemberGoals(item)"
                />
                <v-btn
                  icon="mdi-message-text"
                  size="small"
                  variant="text"
                  @click="sendFeedback(item)"
                />
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Pending Approvals -->
    <v-row v-if="pendingApprovals.length > 0">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-clock-outline</v-icon>
            Pending Goal Approvals
          </v-card-title>

          <v-card-text>
            <v-list>
              <v-list-item
                v-for="approval in pendingApprovals"
                :key="approval.id"
              >
                <v-list-item-title>{{ approval.goal_title }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ approval.employee_name }} - {{ approval.submitted_at }}
                </v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn
                    color="success"
                    size="small"
                    class="mr-2"
                    @click="approveGoal(approval)"
                  >
                    Approve
                  </v-btn>
                  <v-btn
                    color="error"
                    size="small"
                    @click="rejectGoal(approval)"
                  >
                    Reject
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'

const toast = useToast()

// Reactive data
const teamMembers = ref([])
const pendingApprovals = ref([])
const loading = ref(false)

const teamStats = ref([
  { title: 'Team Members', value: '12', icon: 'mdi-account-group', color: 'primary' },
  { title: 'Active Goals', value: '45', icon: 'mdi-target', color: 'blue' },
  { title: 'Completed Goals', value: '23', icon: 'mdi-check-circle', color: 'green' },
  { title: 'Avg Completion', value: '78%', icon: 'mdi-chart-line', color: 'orange' }
])

const memberHeaders = [
  { title: 'Name', key: 'name', sortable: false },
  { title: 'Role', key: 'role', sortable: true },
  { title: 'Goals', key: 'goals_count', sortable: true },
  { title: 'Completion Rate', key: 'completion_rate', sortable: true },
  { title: 'Last Update', key: 'last_update', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

// Methods
const loadTeamData = async () => {
  try {
    loading.value = true
    
    // Mock data - in real app, this would come from API
    teamMembers.value = [
      {
        id: 1,
        name: 'John Doe',
        employee_id: 'EMP000001',
        role: 'Senior Developer',
        goals_count: 5,
        completion_rate: 85,
        last_update: '2024-01-15',
        avatar: null
      },
      {
        id: 2,
        name: 'Jane Smith',
        employee_id: 'EMP000002',
        role: 'Developer',
        goals_count: 3,
        completion_rate: 92,
        last_update: '2024-01-14',
        avatar: null
      },
      {
        id: 3,
        name: 'Mike Johnson',
        employee_id: 'EMP000003',
        role: 'Developer',
        goals_count: 4,
        completion_rate: 67,
        last_update: '2024-01-13',
        avatar: null
      }
    ]

    pendingApprovals.value = [
      {
        id: 1,
        goal_title: 'Improve Code Quality',
        employee_name: 'Jane Smith',
        submitted_at: '2024-01-15'
      },
      {
        id: 2,
        goal_title: 'Learn New Framework',
        employee_name: 'Mike Johnson',
        submitted_at: '2024-01-14'
      }
    ]
  } catch (error) {
    console.error('Error loading team data:', error)
    toast.error('Failed to load team data')
  } finally {
    loading.value = false
  }
}

const getGoalsCountColor = (count) => {
  if (count >= 5) return 'green'
  if (count >= 3) return 'blue'
  if (count >= 1) return 'orange'
  return 'grey'
}

const viewMemberGoals = (member) => {
  // Navigate to member's goals
  console.log('View goals for:', member.name)
}

const sendFeedback = (member) => {
  // Open feedback dialog
  console.log('Send feedback to:', member.name)
}

const approveGoal = async (approval) => {
  try {
    // API call to approve goal
    console.log('Approving goal:', approval.id)
    toast.success('Goal approved successfully')
    
    // Remove from pending list
    const index = pendingApprovals.value.findIndex(a => a.id === approval.id)
    if (index > -1) {
      pendingApprovals.value.splice(index, 1)
    }
  } catch (error) {
    console.error('Error approving goal:', error)
    toast.error('Failed to approve goal')
  }
}

const rejectGoal = async (approval) => {
  try {
    // API call to reject goal
    console.log('Rejecting goal:', approval.id)
    toast.success('Goal rejected')
    
    // Remove from pending list
    const index = pendingApprovals.value.findIndex(a => a.id === approval.id)
    if (index > -1) {
      pendingApprovals.value.splice(index, 1)
    }
  } catch (error) {
    console.error('Error rejecting goal:', error)
    toast.error('Failed to reject goal')
  }
}

// Lifecycle
onMounted(() => {
  loadTeamData()
})
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}
</style>