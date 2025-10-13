<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Login to EPMS</v-toolbar-title>
          </v-toolbar>
          
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="form.username"
                label="Username or Email"
                name="username"
                prepend-icon="mdi-account"
                type="text"
                :error-messages="errors.username"
                required
              />
              
              <v-text-field
                v-model="form.password"
                label="Password"
                name="password"
                prepend-icon="mdi-lock"
                type="password"
                :error-messages="errors.password"
                required
              />
              
              <v-checkbox
                v-model="form.remember"
                label="Remember me"
                color="primary"
              />
            </v-form>
          </v-card-text>
          
          <v-card-actions>
            <v-spacer />
            <v-btn
              color="primary"
              :loading="loading"
              :disabled="!isFormValid"
              @click="handleLogin"
            >
              Login
            </v-btn>
          </v-card-actions>
          
          <v-card-text class="text-center">
            <router-link to="/register" class="text-decoration-none">
              Don't have an account? Register here
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
  username: '',
  password: '',
  remember: false
})

// Form validation
const errors = ref({})
const loading = ref(false)

const isFormValid = computed(() => {
  return form.value.username && form.value.password
})

// Methods
const handleLogin = async () => {
  if (!isFormValid.value) return

  try {
    loading.value = true
    errors.value = {}
    
    await authStore.login(form.value)
    
    toast.success('Login successful!')
    router.push('/dashboard')
  } catch (error) {
    console.error('Login error:', error)
    
    if (error.response?.data) {
      const data = error.response.data
      
      // Handle field-specific errors
      if (data.username) {
        errors.value.username = Array.isArray(data.username) ? data.username : [data.username]
      }
      if (data.password) {
        errors.value.password = Array.isArray(data.password) ? data.password : [data.password]
      }
      
      // Handle general errors
      if (data.detail) {
        toast.error(data.detail)
      } else if (data.non_field_errors) {
        toast.error(Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors)
      }
    } else {
      toast.error('Login failed. Please try again.')
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