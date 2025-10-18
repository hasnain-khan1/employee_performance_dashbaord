<template>
  <div class="login-container">
    <!-- Left Hero Section -->
    <div class="hero-section">
      <div class="hero-content">
        <!-- Hero Image -->
        <div class="hero-image-container">
          <img 
            src="https://images.unsplash.com/photo-1552664730-d307ca884978?w=384&h=384&fit=crop&crop=center" 
            alt="Team Collaboration and Performance Analysis" 
            class="hero-image"
          />
        </div>
        
        <!-- Hero Text -->
        <div class="hero-text">
          <h1 class="hero-title">Elevate Performance Together</h1>
          <p class="hero-description">
            Streamline your performance review process with intelligent
            feedback, goal tracking, and meaningful conversations that
            drive growth.
          </p>
        </div>
        
        <!-- Feature Icons -->
        <div class="feature-icons">
          <div class="feature-item">
            <div class="feature-icon goal-setting">
              <v-icon color="#2563EB" size="16">mdi-target</v-icon>
            </div>
            <span class="feature-label">Goal Setting</span>
          </div>
          <div class="feature-item">
            <div class="feature-icon peer-feedback">
              <v-icon color="#16A34A" size="20">mdi-account-group</v-icon>
            </div>
            <span class="feature-label">Peer Feedback</span>
          </div>
          <div class="feature-item">
            <div class="feature-icon analytics">
              <v-icon color="#9333EA" size="16">mdi-chart-line</v-icon>
            </div>
            <span class="feature-label">Analytics</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Right Login Section -->
    <div class="login-section">
      <div class="login-content">
        <!-- Header -->
        <div class="login-header">
          <div class="logo-container">
            <v-icon color="white" size="24">mdi-chart-box</v-icon>
          </div>
          <h2 class="login-title">Performance Hub</h2>
          <p class="login-subtitle">Welcome back! Please sign in to continue.</p>
        </div>
        
        <!-- Login Form -->
        <div class="login-form-container">
          <v-form @submit.prevent="handleLogin" class="login-form">
            <!-- Username/Email Field -->
            <div class="form-group">
              <label class="form-label">Username or Email</label>
              <v-text-field
                v-model="form.username"
                type="text"
                placeholder="Enter your username or email"
                variant="outlined"
                density="comfortable"
                :error-messages="errors.username"
                required
                class="form-field"
                hide-details="auto"
              >
                <template v-slot:prepend-inner>
                  <v-icon color="#667085" size="20">mdi-account</v-icon>
                </template>
              </v-text-field>
            </div>
            
            <!-- Password Field -->
            <div class="form-group">
              <label class="form-label">Password</label>
              <v-text-field
                v-model="form.password"
                type="password"
                placeholder="Enter your password"
                variant="outlined"
                density="comfortable"
                :error-messages="errors.password"
                required
                class="form-field"
                hide-details="auto"
              >
                <template v-slot:prepend-inner>
                  <v-icon color="#667085" size="20">mdi-lock</v-icon>
                </template>
              </v-text-field>
            </div>
            
            <!-- Remember Me Checkbox -->
            <div class="form-group checkbox-group">
              <v-checkbox
                v-model="form.remember"
                label="Remember me"
                color="primary"
                hide-details
                class="remember-checkbox"
              />
            </div>
            
            <!-- Login Button -->
            <v-btn
              type="submit"
              color="primary"
              size="large"
              :loading="loading"
              :disabled="!isFormValid"
              class="login-btn"
              block
            >
              <template v-slot:prepend v-if="!loading">
                <v-icon>mdi-login</v-icon>
              </template>
              {{ loading ? 'Signing In...' : 'Sign In' }}
            </v-btn>
          </v-form>
          
          <!-- Register Link -->
          <div class="register-link">
            <p class="register-text">
              Don't have an account? 
              <router-link to="/register" class="register-link-text">
                Register here
              </router-link>
            </p>
          </div>
        </div>
        
        <!-- Footer Links -->
        <div class="login-footer">
          <div class="footer-links">
            <a href="#" class="footer-link">Privacy Policy</a>
            <span class="footer-separator">|</span>
            <a href="#" class="footer-link">Terms of Service</a>
            <span class="footer-separator">|</span>
            <a href="#" class="footer-link">Support</a>
          </div>
          <p class="copyright">© 2024 Performance Hub. All rights reserved.</p>
        </div>
      </div>
    </div>
  </div>
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
/* Main Container */
.login-container {
  display: flex;
  min-height: 100vh;
  background: #F9FAFB;
}

/* Hero Section (Left) */
.hero-section {
  flex: 1;
  background: linear-gradient(90deg, #EFF6FF 0%, #E0E7FF 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.hero-content {
  max-width: 512px;
  text-align: center;
}

.hero-image-container {
  margin-bottom: 32px;
}

.hero-image {
  width: 384px;
  height: 384px;
  border-radius: 16px;
  box-shadow: 0px 10px 15px rgba(0, 0, 0, 0.10);
  object-fit: cover;
}

.hero-text {
  margin-bottom: 40px;
}

.hero-title {
  font-size: 30px;
  font-weight: 600;
  line-height: 38px;
  color: #111827;
  margin-bottom: 16px;
}

.hero-description {
  font-size: 18px;
  font-weight: 400;
  line-height: 28px;
  color: #4B5563;
  margin: 0;
}

.feature-icons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 32px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-icon.goal-setting {
  background: #DBEAFE;
}

.feature-icon.peer-feedback {
  background: #DCFCE7;
}

.feature-icon.analytics {
  background: #F3E8FF;
}

.feature-label {
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  color: #374151;
  text-align: center;
}

/* Login Section (Right) */
.login-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background: white;
}

.login-content {
  max-width: 448px;
  width: 100%;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-container {
  width: 64px;
  height: 64px;
  background: #2563EB;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  line-height: 32px;
  color: #111827;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 16px;
  font-weight: 400;
  line-height: 24px;
  color: #4B5563;
  margin: 0;
}

.login-form-container {
  background: white;
  box-shadow: 0px 20px 25px rgba(0, 0, 0, 0.10);
  border-radius: 16px;
  border: 1px solid #F3F4F6;
  padding: 32px;
  margin-bottom: 32px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  color: #344054;
  margin-bottom: 6px;
}

/* Form Fields */
.form-field {
  width: 100%;
}

.form-field :deep(.v-field) {
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  background: white;
}

.form-field :deep(.v-field--focused) {
  border-color: #2563EB;
  box-shadow: 0px 0px 0px 4px #EFF6FF;
}

.form-field :deep(.v-field--error) {
  border-color: #DC2626;
  box-shadow: 0px 0px 0px 4px #FEF2F2;
}

.form-field :deep(.v-field__input) {
  padding: 12px 16px;
  font-size: 16px;
  color: #111827;
}

.form-field :deep(.v-field__input::placeholder) {
  color: #9CA3AF;
}

/* Checkbox Group */
.checkbox-group {
  margin-bottom: 24px;
}

.remember-checkbox {
  margin: 0;
}

.remember-checkbox :deep(.v-selection-control__input) {
  color: #2563EB;
}

.remember-checkbox :deep(.v-label) {
  color: #374151;
  font-size: 14px;
  font-weight: 400;
}

/* Login Button */
.login-btn {
  width: 100%;
  height: 48px;
  background: #2563EB;
  color: white;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  text-transform: none;
  letter-spacing: 0;
  margin-bottom: 24px;
}

.login-btn:hover:not(:disabled) {
  background: #1D4ED8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.login-btn:disabled {
  background: #9CA3AF;
  cursor: not-allowed;
}

/* Register Link */
.register-link {
  text-align: center;
}

.register-text {
  font-size: 14px;
  font-weight: 400;
  line-height: 20px;
  color: #6B7280;
  margin: 0;
}

.register-link-text {
  color: #2563EB;
  text-decoration: none;
  font-weight: 500;
}

.register-link-text:hover {
  text-decoration: underline;
}

.login-footer {
  text-align: center;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  margin-bottom: 16px;
}

.footer-link {
  font-size: 14px;
  font-weight: 400;
  line-height: 20px;
  color: #6B7280;
  text-decoration: none;
}

.footer-link:hover {
  color: #374151;
  text-decoration: underline;
}

.footer-separator {
  font-size: 14px;
  font-weight: 400;
  color: #D1D5DB;
}

.copyright {
  font-size: 12px;
  font-weight: 400;
  line-height: 18px;
  color: #9CA3AF;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .login-container {
    flex-direction: column;
  }
  
  .hero-section {
    padding: 32px 24px;
  }
  
  .hero-image {
    width: 300px;
    height: 300px;
  }
  
  .hero-title {
    font-size: 24px;
    line-height: 32px;
  }
  
  .hero-description {
    font-size: 16px;
    line-height: 24px;
  }
  
  .feature-icons {
    gap: 24px;
  }
  
  .feature-icon {
    width: 40px;
    height: 40px;
  }
  
  .feature-label {
    font-size: 12px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 24px 16px;
  }
  
  .login-section {
    padding: 24px 16px;
  }
  
  .hero-image {
    width: 250px;
    height: 250px;
  }
  
  .hero-title {
    font-size: 20px;
    line-height: 28px;
  }
  
  .hero-description {
    font-size: 14px;
    line-height: 20px;
  }
  
  .feature-icons {
    flex-direction: column;
    gap: 16px;
  }
  
  .login-form-container {
    padding: 24px;
  }
  
  .footer-links {
    flex-direction: column;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .hero-image {
    width: 200px;
    height: 200px;
  }
  
  .hero-title {
    font-size: 18px;
    line-height: 24px;
  }
  
  .login-title {
    font-size: 20px;
    line-height: 28px;
  }
  
  .login-form-container {
    padding: 20px;
  }
}
</style>