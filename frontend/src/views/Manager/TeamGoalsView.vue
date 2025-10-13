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
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/api/axios'

const toast = useToast()

// Reactive data
const teamMembers = ref([])
const pendingApprovals = ref([])
const loading = ref(false)

// Computed properties
const teamStats = computed(() => {
  const totalMembers = teamMembers.value.length
  const totalGoals = teamMembers.value.reduce((sum, m) => sum + m.goals_count, 0)
  const avgCompletionRate = totalMembers > 0
    ? Math.round(teamMembers.value.reduce((sum, m) => sum + m.completion_rate, 0) / totalMembers)
    : 0
  const pendingCount = pendingApprovals.value.length

  return [
    {
      title: 'Team Members',
      value: totalMembers,
      icon: 'mdi-account-group',
      color: 'primary'
    },
    {
      title: 'Total Goals',
      value: totalGoals,
      icon: 'mdi-target',
      color: 'success'
    },
    {
      title: 'Avg Completion',
      value: `${avgCompletionRate}%`,
      icon: 'mdi-chart-line',
      color: 'info'
    },
    {
      title: 'Pending Approvals',
      value: pendingCount,
      icon: 'mdi-clock-outline',
      color: 'warning'
    }
  ]
})

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
    
    // Get current user's profile to find their ID
    const profileResponse = await api.get('/auth/profile/')
    const currentUserId = profileResponse.data.id
    
    // Load all users and filter for direct reports
    const response = await api.get('/auth/users/')
    
    // Process team members and their goals
    // Handle different response formats (array, paginated results, etc.)
    const allUsers = Array.isArray(response.data) 
      ? response.data 
      : (response.data?.results || [])
    
    // Filter for direct reports (users whose manager is the current user)
    const members = allUsers.filter(user => user.manager === currentUserId)
    
    for (let member of members) {
      try {
        const goalsResponse = await api.get('/goals/', {
          params: { employee: member.id }
        })
        
        // Handle different response formats
        const goals = Array.isArray(goalsResponse.data)
          ? goalsResponse.data
          : (goalsResponse.data?.results || [])
        member.goals_count = goals.length
        
        const completedGoals = goals.filter(g => g.status === 'completed').length
        member.completion_rate = goals.length > 0 
          ? Math.round((completedGoals / goals.length) * 100) 
          : 0
        
        // Get latest goal update
        if (goals.length > 0) {
          const latestGoal = goals.reduce((latest, g) => 
            new Date(g.updated_at || g.created_at) > new Date(latest.updated_at || latest.created_at) 
              ? g : latest
          )
          member.last_update = latestGoal.updated_at || latestGoal.created_at
        }
      } catch (error) {
        console.error(`Error loading goals for ${member.full_name}:`, error)
        member.goals_count = 0
        member.completion_rate = 0
        member.last_update = null
      }
    }
    
    teamMembers.value = members.map(m => ({
      id: m.id,
      name: m.full_name || `${m.first_name} ${m.last_name}`,
      employee_id: m.employee_id,
      role: m.job_title || 'No Position',
      goals_count: m.goals_count || 0,
      completion_rate: m.completion_rate || 0,
      last_update: m.last_update,
      avatar: m.avatar
    }))
    
    // Load pending goal approvals - get all submitted goals and filter for team members
    const approvalsResponse = await api.get('/goals/', {
      params: { status: 'submitted' }
    })
    
    // Handle different response formats
    const allApprovals = Array.isArray(approvalsResponse.data)
      ? approvalsResponse.data
      : (approvalsResponse.data?.results || [])
    
    // Filter for goals from direct reports only
    const teamMemberIds = members.map(m => m.id)
    const teamApprovals = allApprovals.filter(goal => 
      teamMemberIds.includes(goal.employee?.id || goal.employee)
    )
    
    pendingApprovals.value = teamApprovals.map(goal => ({
      id: goal.id,
      goal_title: goal.title,
      employee_name: goal.employee?.full_name || goal.employee?.first_name + ' ' + goal.employee?.last_name || 'Unknown',
      employee_id: goal.employee?.id || goal.employee,
      submitted_at: goal.created_at
    }))
    
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

const viewMemberGoals = async (member) => {
  try {
    // Load member's goals and show them
    const goalsResponse = await api.get('/goals/', {
      params: { employee: member.id }
    })
    
    const goals = Array.isArray(goalsResponse.data)
      ? goalsResponse.data
      : (goalsResponse.data?.results || [])
    
    if (goals.length === 0) {
      toast.info(`${member.name} has no goals yet`)
      return
    }
    
    // Show goals information
    const goalsInfo = goals.map(g => 
      `• ${g.title} (${g.status})`
    ).join('\n')
    
    toast.info(`Goals for ${member.name}:\n${goalsInfo}`, { 
      timeout: 5000 
    })
  } catch (error) {
    console.error('Error loading member goals:', error)
    toast.error('Failed to load member goals')
  }
}

const sendFeedback = (member) => {
  // For now, show info message
  toast.info(`Feedback feature for ${member.name} will be implemented soon`, {
    timeout: 3000
  })
}

const approveGoal = async (approval) => {
  try {
    await api.patch(`/goals/${approval.id}/`, {
      status: 'approved',
      approved_at: new Date().toISOString()
    })
    
    toast.success('Goal approved successfully')
    await loadTeamData()
  } catch (error) {
    console.error('Error approving goal:', error)
    toast.error('Failed to approve goal')
  }
}

const rejectGoal = async (approval) => {
  try {
    await api.patch(`/goals/${approval.id}/`, {
      status: 'rejected'
    })
    
    toast.success('Goal rejected')
    await loadTeamData()
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