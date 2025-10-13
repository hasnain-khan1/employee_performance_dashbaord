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
    
    // Load team members with their goals
    const response = await api.get('/auth/users/', { 
      params: { manager: 'me' }  // Get users managed by current user
    })
    
    // Process team members and their goals
    const members = response.data
    
    for (let member of members) {
      try {
        const goalsResponse = await api.get('/goals/', {
          params: { employee: member.id }
        })
        
        const goals = goalsResponse.data
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
      name: m.full_name,
      employee_id: m.employee_id,
      role: m.position?.title || 'No Position',
      goals_count: m.goals_count || 0,
      completion_rate: m.completion_rate || 0,
      last_update: m.last_update,
      avatar: m.userprofile?.avatar
    }))
    
    // Load pending goal approvals
    const approvalsResponse = await api.get('/goals/', {
      params: { status: 'submitted', manager: 'me' }
    })
    
    pendingApprovals.value = approvalsResponse.data.map(goal => ({
      id: goal.id,
      goal_title: goal.title,
      employee_name: goal.employee?.full_name || 'Unknown',
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