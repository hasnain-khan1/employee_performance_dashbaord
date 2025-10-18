<template>
  <v-dialog
    v-model="dialog"
    max-width="1000px"
    persistent
    :scrim="true"
    scrollable
  >
    <v-card elevation="8">
      <v-card-title class="text-h5 bg-primary pa-4 d-flex align-center">
        <v-icon class="mr-2">mdi-account-group</v-icon>
        Request Peer Feedback
        <v-spacer />
        <v-chip color="white" variant="flat" size="small">
          {{ selectedPeers.length }}/5 selected
        </v-chip>
      </v-card-title>

      <v-card-text class="pa-6">
        <v-form ref="formRef" v-model="formValid">
          <!-- Request Details -->
          <v-card variant="outlined" class="mb-6">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-information</v-icon>
              Request Details
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="requestForm.title"
                    label="Feedback Request Title"
                    placeholder="e.g., Q4 Performance Feedback"
                    variant="outlined"
                    :rules="titleRules"
                    required
                  />
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    v-model="requestForm.description"
                    label="Description (Optional)"
                    placeholder="Provide context about what feedback you're looking for..."
                    variant="outlined"
                    rows="3"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="requestForm.deadline"
                    label="Deadline"
                    type="datetime-local"
                    variant="outlined"
                    :rules="deadlineRules"
                    required
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-checkbox
                    v-model="requestForm.allow_anonymous"
                    label="Allow anonymous feedback"
                    color="primary"
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <!-- Peer Selection -->
          <v-card variant="outlined" class="mb-6">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-account-multiple</v-icon>
              Select Peer Reviewers
              <v-spacer />
              <v-chip
                :color="selectedPeers.length >= 1 && selectedPeers.length <= 5 ? 'success' : 'error'"
                variant="flat"
                size="small"
              >
                {{ selectedPeers.length }}/5 selected
              </v-chip>
            </v-card-title>
            <v-card-text>
              <!-- Search and Filters -->
              <v-row class="mb-4">
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="searchQuery"
                    label="Search colleagues"
                    prepend-inner-icon="mdi-magnify"
                    variant="outlined"
                    clearable
                    @input="filterPeers"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="departmentFilter"
                    label="Filter by department"
                    :items="departments"
                    variant="outlined"
                    clearable
                    @update:model-value="filterPeers"
                  />
                </v-col>
              </v-row>

              <!-- Peer List -->
              <div class="peer-list" style="max-height: 400px; overflow-y: auto;">
                <div
                  v-for="peer in filteredPeers"
                  :key="peer.id"
                  class="peer-item pa-3 mb-2 border rounded"
                  :class="{ 'selected': isPeerSelected(peer.id) }"
                  @click="togglePeerSelection(peer)"
                >
                  <div class="d-flex align-center">
                    <v-checkbox
                      :model-value="isPeerSelected(peer.id)"
                      color="primary"
                      hide-details
                      class="mr-3"
                      @click.stop
                    />
                    <v-avatar size="40" class="mr-3">
                      <v-img
                        v-if="peer.avatar"
                        :src="peer.avatar"
                        :alt="peer.first_name"
                      />
                      <v-icon v-else>mdi-account</v-icon>
                    </v-avatar>
                    <div class="flex-grow-1">
                      <div class="font-weight-medium">
                        {{ peer.first_name }} {{ peer.last_name }}
                      </div>
                      <div class="text-caption text-grey">
                        {{ peer.email }} • {{ peer.department }}
                      </div>
                    </div>
                    <v-chip
                      v-if="peer.department"
                      size="small"
                      variant="outlined"
                    >
                      {{ peer.department }}
                    </v-chip>
                  </div>
                </div>
              </div>

              <!-- Selection Summary -->
              <div v-if="selectedPeers.length > 0" class="mt-4">
                <h4 class="text-subtitle-1 mb-2">Selected Reviewers:</h4>
                <div class="d-flex flex-wrap gap-2">
                  <v-chip
                    v-for="peer in selectedPeers"
                    :key="peer.id"
                    closable
                    @click:close="removePeer(peer.id)"
                    color="primary"
                    variant="flat"
                  >
                    {{ peer.first_name }} {{ peer.last_name }}
                  </v-chip>
                </div>
              </div>
            </v-card-text>
          </v-card>

          <!-- Relationship Context -->
          <v-card variant="outlined" class="mb-6">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-handshake</v-icon>
              Working Relationship Context
            </v-card-title>
            <v-card-text>
              <v-textarea
                v-model="requestForm.relationship_context"
                label="Relationship Context (Optional)"
                placeholder="Describe your working relationship with the selected reviewers..."
                variant="outlined"
                rows="3"
              />
            </v-card-text>
          </v-card>

          <!-- Personal Message -->
          <v-card variant="outlined">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-message-text</v-icon>
              Personal Message
            </v-card-title>
            <v-card-text>
              <v-textarea
                v-model="requestForm.personal_message"
                label="Personal Message (Optional)"
                placeholder="Add a personal message to your reviewers..."
                variant="outlined"
                rows="3"
              />
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          color="grey-darken-1"
          variant="outlined"
          @click="closeDialog"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          variant="elevated"
          :loading="saving"
          :disabled="!isFormValid"
          @click="submitRequest"
        >
          Send Request
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { feedbackAPI } from '@/api/feedback'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'feedback-requested'])

const toast = useToast()

// Reactive data
const formRef = ref(null)
const formValid = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const departmentFilter = ref('')
const availablePeers = ref([])
const selectedPeers = ref([])

// Form data
const requestForm = ref({
  title: '',
  description: '',
  deadline: '',
  allow_anonymous: true,
  relationship_context: '',
  personal_message: ''
})

// Form validation
const titleRules = [
  v => !!v || 'Title is required',
  v => v.length >= 3 || 'Title must be at least 3 characters'
]

const deadlineRules = [
  v => !!v || 'Deadline is required',
  v => {
    if (!v) return true
    const deadline = new Date(v)
    const now = new Date()
    return deadline > now || 'Deadline must be in the future'
  }
]

// Computed properties
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const departments = computed(() => {
  const depts = [...new Set(availablePeers.value.map(peer => peer.department).filter(Boolean))]
  return depts.map(dept => ({ title: dept, value: dept }))
})

const filteredPeers = computed(() => {
  let filtered = availablePeers.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(peer =>
      peer.first_name.toLowerCase().includes(query) ||
      peer.last_name.toLowerCase().includes(query) ||
      peer.email.toLowerCase().includes(query)
    )
  }

  // Department filter
  if (departmentFilter.value) {
    filtered = filtered.filter(peer => peer.department === departmentFilter.value)
  }

  return filtered
})

const isFormValid = computed(() => {
  return formValid.value &&
         requestForm.value.title &&
         requestForm.value.deadline &&
         selectedPeers.value.length >= 1 &&
         selectedPeers.value.length <= 5
})

// Methods
const loadAvailablePeers = async () => {
  try {
    const response = await feedbackAPI.getAvailablePeers()
    availablePeers.value = response.data
  } catch (error) {
    console.error('Error loading available peers:', error)
    toast.error('Failed to load available peers')
  }
}

const filterPeers = () => {
  // Filtering is handled by computed property
}

const isPeerSelected = (peerId) => {
  return selectedPeers.value.some(peer => peer.id === peerId)
}

const togglePeerSelection = (peer) => {
  if (isPeerSelected(peer.id)) {
    removePeer(peer.id)
  } else {
    addPeer(peer)
  }
}

const addPeer = (peer) => {
  if (selectedPeers.value.length >= 5) {
    toast.warning('Maximum 5 peer reviewers allowed')
    return
  }
  selectedPeers.value.push(peer)
}

const removePeer = (peerId) => {
  selectedPeers.value = selectedPeers.value.filter(peer => peer.id !== peerId)
}

const submitRequest = async () => {
  if (!isFormValid.value) {
    toast.error('Please fill in all required fields and select 1-5 peer reviewers')
    return
  }

  try {
    saving.value = true
    
    const requestData = {
      title: requestForm.value.title,
      description: requestForm.value.description,
      deadline: requestForm.value.deadline,
      allow_anonymous: requestForm.value.allow_anonymous,
      relationship_context: requestForm.value.relationship_context,
      personal_message: requestForm.value.personal_message,
      peer_reviewer_ids: selectedPeers.value.map(peer => peer.id)
    }

    await feedbackAPI.createPeerFeedbackRequest(requestData)
    
    toast.success('Feedback request sent successfully')
    emit('feedback-requested')
    closeDialog()
  } catch (error) {
    console.error('Error creating feedback request:', error)
    const errorMsg = error.response?.data?.error || 'Failed to create feedback request'
    toast.error(errorMsg)
  } finally {
    saving.value = false
  }
}

const closeDialog = () => {
  dialog.value = false
  resetForm()
}

const resetForm = () => {
  requestForm.value = {
    title: '',
    description: '',
    deadline: '',
    allow_anonymous: true,
    relationship_context: '',
    personal_message: ''
  }
  selectedPeers.value = []
  searchQuery.value = ''
  departmentFilter.value = ''
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    loadAvailablePeers()
  }
})

// Lifecycle
onMounted(() => {
  // Set default deadline to 2 weeks from now
  const defaultDeadline = new Date()
  defaultDeadline.setDate(defaultDeadline.getDate() + 14)
  requestForm.value.deadline = defaultDeadline.toISOString().slice(0, 16)
})
</script>

<style scoped>
.v-card {
  border-radius: 8px;
}

.peer-item {
  cursor: pointer;
  transition: all 0.2s ease;
}

.peer-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.04);
}

.peer-item.selected {
  background-color: rgba(var(--v-theme-primary), 0.08);
  border-color: rgb(var(--v-theme-primary));
}

.border {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
</style>
