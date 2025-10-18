<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Register for EPMS</v-toolbar-title>
          </v-toolbar>
          
          <v-card-text>
            <v-form @submit.prevent="handleRegister">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.first_name"
                    label="First Name"
                    prepend-icon="mdi-account"
                    :error-messages="errors.first_name"
                    required
                  />
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="form.last_name"
                    label="Last Name"
                    prepend-icon="mdi-account"
                    :error-messages="errors.last_name"
                    required
                  />
                </v-col>
              </v-row>
              
              <v-text-field
                v-model="form.username"
                label="Username"
                prepend-icon="mdi-account"
                :error-messages="errors.username"
                required
              />
              
              <v-text-field
                v-model="form.email"
                label="Email"
                prepend-icon="mdi-email"
                type="email"
                :error-messages="errors.email"
                required
              />
              
              <v-text-field
                v-model="form.phone"
                label="Phone"
                prepend-icon="mdi-phone"
                :error-messages="errors.phone"
              />
              
              <v-text-field
                v-model="form.password"
                label="Password"
                prepend-icon="mdi-lock"
                type="password"
                :error-messages="errors.password"
                required
              />
              
              <v-text-field
                v-model="form.password_confirm"
                label="Confirm Password"
                prepend-icon="mdi-lock"
                type="password"
                :error-messages="errors.password_confirm"
                required
              />
              
              <v-select
                v-model="form.role"
                label="Role"
                prepend-icon="mdi-account-tie"
                :items="Array.isArray(roleOptions) ? roleOptions : []"
                :error-messages="errors.role"
                required
              />
            </v-form>
          </v-card-text>
          
          <v-card-actions>
            <v-spacer />
            <v-btn
              color="primary"
              :loading="loading"
              :disabled="!isFormValid"
              @click="handleRegister"
            >
              Register
            </v-btn>
          </v-card-actions>
          
          <v-card-text class="text-center">
            <router-link to="/login" class="text-decoration-none">
              Already have an account? Login here
            </router-link>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

// Form data
const form = ref({
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  phone: '',
  password: '',
  password_confirm: '',
  role: 'employee'
})

// Form validation
const errors = ref({})
const loading = ref(false)

const roleOptions = [
  { title: 'Employee', value: 'employee' },
  { title: 'Manager', value: 'manager' },
  { title: 'HR', value: 'hr' }
]

const isFormValid = computed(() => {
  return form.value.first_name &&
         form.value.last_name &&
         form.value.username &&
         form.value.email &&
         form.value.password &&
         form.value.password_confirm &&
         form.value.password === form.value.password_confirm
})

// Methods
const handleRegister = async () => {
  if (!isFormValid.value) return

  try {
    loading.value = true
    errors.value = {}
    
    await authStore.register(form.value)
    
    toast.success('Registration successful! Please login.')
    router.push('/login')
  } catch (error) {
    console.error('Registration error:', error)
    
    if (error.response?.data) {
      const data = error.response.data
      
      // Handle field-specific errors
      Object.keys(data).forEach(field => {
        if (field !== 'non_field_errors') {
          errors.value[field] = Array.isArray(data[field]) ? data[field] : [data[field]]
        }
      })
      
      // Handle general errors
      if (data.non_field_errors) {
        toast.error(Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors)
      }
    } else {
      toast.error('Registration failed. Please try again.')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}
</style>