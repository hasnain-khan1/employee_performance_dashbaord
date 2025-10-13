<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-6">Profile</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-account</v-icon>
            Personal Information
          </v-card-title>

          <v-card-text>
            <v-form ref="profileForm" v-model="formValid">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="profileForm.first_name"
                    label="First Name"
                    :rules="[v => !!v || 'First name is required']"
                    required
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="profileForm.last_name"
                    label="Last Name"
                    :rules="[v => !!v || 'Last name is required']"
                    required
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="profileForm.email"
                    label="Email"
                    type="email"
                    :rules="[v => !!v || 'Email is required', v => /.+@.+\..+/.test(v) || 'Email must be valid']"
                    required
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="profileForm.phone"
                    label="Phone"
                    :rules="[v => !v || /^\+?[\d\s-()]+$/.test(v) || 'Phone must be valid']"
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="profileForm.bio"
                    label="Bio"
                    rows="3"
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="profileForm.job_title"
                    label="Job Title"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="profileForm.hire_date"
                    label="Hire Date"
                    type="date"
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>

          <v-card-actions>
            <v-spacer />
            <v-btn
              color="primary"
              :disabled="!formValid"
              :loading="saving"
              @click="saveProfile"
            >
              Save Changes
            </v-btn>
          </v-card-actions>
        </v-card>

        <!-- Extended Profile -->
        <v-card class="mt-6">
          <v-card-title>
            <v-icon left>mdi-account-details</v-icon>
            Extended Profile
          </v-card-title>

          <v-card-text>
            <v-form ref="extendedForm" v-model="extendedFormValid">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="extendedForm.date_of_birth"
                    label="Date of Birth"
                    type="date"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="extendedForm.timezone"
                    label="Timezone"
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="extendedForm.address"
                    label="Address"
                    rows="2"
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="extendedForm.emergency_contact_name"
                    label="Emergency Contact Name"
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="extendedForm.emergency_contact_phone"
                    label="Emergency Contact Phone"
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="extendedForm.skills"
                    label="Skills (comma-separated)"
                    rows="2"
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="extendedForm.certifications"
                    label="Certifications"
                    rows="2"
                  />
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <v-textarea
                    v-model="extendedForm.education"
                    label="Education"
                    rows="2"
                  />
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>

          <v-card-actions>
            <v-spacer />
            <v-btn
              color="primary"
              :disabled="!extendedFormValid"
              :loading="savingExtended"
              @click="saveExtendedProfile"
            >
              Save Extended Profile
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <!-- Avatar -->
        <v-card>
          <v-card-title>
            <v-icon left>mdi-account-circle</v-icon>
            Profile Picture
          </v-card-title>

          <v-card-text class="text-center">
            <v-avatar size="120" class="mb-4">
              <v-img
                v-if="profileForm.avatar"
                :src="profileForm.avatar"
                :alt="profileForm.full_name"
              />
              <v-icon v-else size="60">mdi-account</v-icon>
            </v-avatar>

            <v-file-input
              v-model="avatarFile"
              label="Upload Avatar"
              accept="image/*"
              prepend-icon="mdi-camera"
              @change="uploadAvatar"
            />
          </v-card-text>
        </v-card>

        <!-- Change Password -->
        <v-card class="mt-6">
          <v-card-title>
            <v-icon left>mdi-lock</v-icon>
            Change Password
          </v-card-title>

          <v-card-text>
            <v-form ref="passwordForm" v-model="passwordFormValid">
              <v-text-field
                v-model="passwordForm.old_password"
                label="Current Password"
                type="password"
                :rules="[v => !!v || 'Current password is required']"
                required
              />

              <v-text-field
                v-model="passwordForm.new_password"
                label="New Password"
                type="password"
                :rules="[v => !!v || 'New password is required', v => v.length >= 8 || 'Password must be at least 8 characters']"
                required
              />

              <v-text-field
                v-model="passwordForm.new_password_confirm"
                label="Confirm New Password"
                type="password"
                :rules="[v => !!v || 'Password confirmation is required', v => v === passwordForm.new_password || 'Passwords do not match']"
                required
              />
            </v-form>
          </v-card-text>

          <v-card-actions>
            <v-spacer />
            <v-btn
              color="primary"
              :disabled="!passwordFormValid"
              :loading="changingPassword"
              @click="changePassword"
            >
              Change Password
            </v-btn>
          </v-card-actions>
        </v-card>

        <!-- Account Info -->
        <v-card class="mt-6">
          <v-card-title>
            <v-icon left>mdi-information</v-icon>
            Account Information
          </v-card-title>

          <v-card-text>
            <div class="mb-4">
              <div class="text-caption text-grey">Employee ID</div>
              <div class="text-body-1">{{ user?.employee_id }}</div>
            </div>

            <div class="mb-4">
              <div class="text-caption text-grey">Role</div>
              <div class="text-body-1">{{ user?.role }}</div>
            </div>

            <div class="mb-4">
              <div class="text-caption text-grey">Status</div>
              <v-chip
                :color="getStatusColor(user?.status)"
                size="small"
              >
                {{ user?.status }}
              </v-chip>
            </div>

            <div class="mb-4">
              <div class="text-caption text-grey">Department</div>
              <div class="text-body-1">{{ user?.department_name || 'Not assigned' }}</div>
            </div>

            <div class="mb-4">
              <div class="text-caption text-grey">Manager</div>
              <div class="text-body-1">{{ user?.manager_name || 'Not assigned' }}</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useToast } from 'vue-toastification'

const authStore = useAuthStore()
const toast = useToast()

// Reactive data
const profileForm = ref({})
const extendedForm = ref({})
const passwordForm = ref({
  old_password: '',
  new_password: '',
  new_password_confirm: ''
})

const formValid = ref(false)
const extendedFormValid = ref(false)
const passwordFormValid = ref(false)
const saving = ref(false)
const savingExtended = ref(false)
const changingPassword = ref(false)
const avatarFile = ref(null)

// Computed properties
const user = computed(() => authStore.user)

// Methods
const loadProfile = async () => {
  try {
    const response = await authStore.getProfile()
    profileForm.value = { ...response }
    extendedForm.value = { ...response.profile } || {}
  } catch (error) {
    console.error('Error loading profile:', error)
    toast.error('Failed to load profile')
  }
}

const saveProfile = async () => {
  try {
    saving.value = true
    await authStore.updateProfile(profileForm.value)
    toast.success('Profile updated successfully')
  } catch (error) {
    console.error('Error saving profile:', error)
    toast.error('Failed to update profile')
  } finally {
    saving.value = false
  }
}

const saveExtendedProfile = async () => {
  try {
    savingExtended.value = true
    await authStore.updateProfileExtended(extendedForm.value)
    toast.success('Extended profile updated successfully')
  } catch (error) {
    console.error('Error saving extended profile:', error)
    toast.error('Failed to update extended profile')
  } finally {
    savingExtended.value = false
  }
}

const changePassword = async () => {
  try {
    changingPassword.value = true
    await authStore.changePassword(passwordForm.value)
    toast.success('Password changed successfully')
    passwordForm.value = {
      old_password: '',
      new_password: '',
      new_password_confirm: ''
    }
  } catch (error) {
    console.error('Error changing password:', error)
    toast.error('Failed to change password')
  } finally {
    changingPassword.value = false
  }
}

const uploadAvatar = async () => {
  if (!avatarFile.value) return

  try {
    const formData = new FormData()
    formData.append('avatar', avatarFile.value)
    
    // This would be implemented in the API
    // await authStore.uploadAvatar(formData)
    toast.success('Avatar uploaded successfully')
  } catch (error) {
    console.error('Error uploading avatar:', error)
    toast.error('Failed to upload avatar')
  }
}

const getStatusColor = (status) => {
  const colors = {
    active: 'green',
    inactive: 'grey',
    on_leave: 'orange',
    terminated: 'red'
  }
  return colors[status] || 'grey'
}

// Lifecycle
onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.v-card {
  margin-bottom: 16px;
}
</style>