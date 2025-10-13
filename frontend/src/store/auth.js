import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api/auth'
import { useToast } from 'vue-toastification'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))
  const loading = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role)
  const isEmployee = computed(() => user.value?.role === 'employee')
  const isManager = computed(() => user.value?.role === 'manager')
  const isHR = computed(() => user.value?.role === 'hr' || user.value?.role === 'admin')

  // Actions
  const login = async (credentials) => {
    try {
      loading.value = true
      const response = await authAPI.login(credentials)
      
      // Store tokens
      token.value = response.data.access
      refreshToken.value = response.data.refresh
      user.value = response.data.user
      
      // Save to localStorage
      localStorage.setItem('access_token', token.value)
      localStorage.setItem('refresh_token', refreshToken.value)
      
      return response.data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const register = async (userData) => {
    try {
      loading.value = true
      const response = await authAPI.register(userData)
      return response.data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      if (refreshToken.value) {
        await authAPI.logout({ refresh: refreshToken.value })
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear state
      user.value = null
      token.value = null
      refreshToken.value = null
      
      // Clear localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  const checkAuth = async () => {
    if (!token.value) {
      return false
    }

    try {
      const response = await authAPI.getProfile()
      user.value = response.data
      return true
    } catch (error) {
      // Token might be expired, try to refresh
      if (refreshToken.value) {
        try {
          await refreshAccessToken()
          return true
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError)
          await logout()
          return false
        }
      } else {
        await logout()
        return false
      }
    }
  }

  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await authAPI.refreshToken({ refresh: refreshToken.value })
      token.value = response.data.access
      localStorage.setItem('access_token', token.value)
      return response.data
    } catch (error) {
      throw error
    }
  }

  const updateProfile = async (profileData) => {
    try {
      loading.value = true
      const response = await authAPI.updateProfile(profileData)
      user.value = response.data
      return response.data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const changePassword = async (passwordData) => {
    try {
      loading.value = true
      const response = await authAPI.changePassword(passwordData)
      return response.data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    user,
    token,
    refreshToken,
    loading,
    
    // Getters
    isAuthenticated,
    userRole,
    isEmployee,
    isManager,
    isHR,
    
    // Actions
    login,
    register,
    logout,
    checkAuth,
    refreshAccessToken,
    updateProfile,
    changePassword
  }
})