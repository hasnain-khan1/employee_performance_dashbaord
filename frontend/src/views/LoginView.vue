<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12 login-card">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Login to EPMS</v-toolbar-title>
          </v-toolbar>
          
          <v-card-text>
            <v-form @submit.prevent="handleLogin" class="login-form">
              <v-text-field
                v-model="form.username"
                label="Username or Email"
                name="username"
                prepend-icon="mdi-account"
                type="text"
                :error-messages="errors.username"
                required
                class="form-field"
              />
              
              <v-text-field
                v-model="form.password"
                label="Password"
                name="password"
                prepend-icon="mdi-lock"
                type="password"
                :error-messages="errors.password"
                required
                class="form-field"
              />
              
              <v-checkbox
                v-model="form.remember"
                label="Remember me"
                color="primary"
                class="form-field"
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
              :class="['login-btn', { 'success': loginSuccess }]"
              size="large"
              rounded="lg"
              elevation="4"
              :ripple="true"
            >
              <template v-slot:prepend>
                <v-icon v-if="!loading" class="login-icon">mdi-login</v-icon>
              </template>
              <span class="login-text">{{ loading ? 'Signing In...' : 'Login' }}</span>
              <template v-slot:append v-if="!loading">
                <v-icon class="arrow-icon">mdi-arrow-right</v-icon>
              </template>
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
const loginSuccess = ref(false)

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
    
    // Show success animation
    loginSuccess.value = true
    toast.success('Login successful!')
    
    // Wait for animation to complete before redirecting
    setTimeout(() => {
      router.push('/dashboard')
    }, 600)
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

/* Login Button Animations */
.login-btn {
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  box-shadow: 0 4px 15px rgba(25, 118, 210, 0.3);
  min-width: 140px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: white !important;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 25px rgba(25, 118, 210, 0.4);
  background: linear-gradient(135deg, #1e88e5 0%, #1976d2 100%);
  color: white !important;
}

.login-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
  transition: all 0.1s ease;
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Icon Animations */
.login-icon {
  transition: all 0.3s ease;
  animation: pulse 2s infinite;
  color: white !important;
}

.arrow-icon {
  transition: all 0.3s ease;
  transform: translateX(0);
  color: white !important;
}

.login-btn:hover:not(:disabled) .arrow-icon {
  transform: translateX(4px);
  animation: bounce 0.6s ease-in-out;
}

.login-btn:hover:not(:disabled) .login-icon {
  animation: shake 0.5s ease-in-out;
}

/* Text Animation */
.login-text {
  transition: all 0.3s ease;
  position: relative;
  color: white !important;
}

.login-btn:hover:not(:disabled) .login-text {
  letter-spacing: 1px;
  color: white !important;
}

/* Loading State Animations */
.login-btn:deep(.v-btn__loader) {
  animation: spin 1s linear infinite;
}

/* Ensure all button content is white */
.login-btn :deep(.v-btn__content) {
  color: white !important;
}

.login-btn :deep(.v-icon) {
  color: white !important;
}

.login-btn :deep(.v-btn__prepend .v-icon) {
  color: white !important;
}

.login-btn :deep(.v-btn__append .v-icon) {
  color: white !important;
}

/* Keyframe Animations */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateX(0);
  }
  40% {
    transform: translateX(6px);
  }
  60% {
    transform: translateX(3px);
  }
}

@keyframes shake {
  0%, 100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(-5deg);
  }
  75% {
    transform: rotate(5deg);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Ripple Effect Enhancement */
.login-btn:deep(.v-ripple__container) {
  background: rgba(255, 255, 255, 0.3);
}

/* Success Animation (for after login) */
.login-btn.success {
  background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
  animation: successPulse 0.6s ease-in-out;
}

@keyframes successPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

/* Card Enhancement */
.login-card {
  transition: all 0.3s ease;
  border-radius: 16px;
  overflow: hidden;
  animation: slideInUp 0.6s ease-out;
}

.login-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

@keyframes slideInUp {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Form Field Animations */
.login-form {
  animation: fadeInUp 0.8s ease-out 0.2s both;
}

.form-field {
  animation: fadeInUp 0.6s ease-out;
  margin-bottom: 16px;
}

.form-field:nth-child(1) {
  animation-delay: 0.1s;
}

.form-field:nth-child(2) {
  animation-delay: 0.2s;
}

.form-field:nth-child(3) {
  animation-delay: 0.3s;
}

.v-text-field :deep(.v-field) {
  transition: all 0.3s ease;
}

.v-text-field:focus-within :deep(.v-field) {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.2);
}

/* Checkbox Animation */
.v-checkbox :deep(.v-selection-control__input) {
  transition: all 0.3s ease;
}

.v-checkbox:hover :deep(.v-selection-control__input) {
  transform: scale(1.1);
}

@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 600px) {
  .login-btn {
    min-width: 120px;
    font-size: 14px;
  }
  
  .login-btn:hover:not(:disabled) {
    transform: translateY(-1px) scale(1.01);
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .login-btn {
    background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%);
    box-shadow: 0 4px 15px rgba(25, 118, 210, 0.4);
  }
  
  .login-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
    box-shadow: 0 8px 25px rgba(25, 118, 210, 0.5);
  }
}
</style>