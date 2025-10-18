import api from './axios'

export const dashboardAPI = {
  // Employee Dashboard endpoints
  getDashboardData: () => api.get('/auth/dashboard/'),
  getProgressSummary: () => api.get('/auth/dashboard/progress/'),
  getActionItems: () => api.get('/auth/dashboard/action-items/'),
  
  // Real-time updates
  refreshDashboard: () => api.post('/auth/dashboard/refresh/'),
  
  // Offline support
  getCachedData: () => {
    const cached = localStorage.getItem('dashboard_cache')
    return cached ? JSON.parse(cached) : null
  },
  
  setCachedData: (data) => {
    localStorage.setItem('dashboard_cache', JSON.stringify({
      data,
      timestamp: new Date().toISOString()
    }))
  },
  
  clearCachedData: () => {
    localStorage.removeItem('dashboard_cache')
  },
  
  isDataStale: (maxAgeMinutes = 5) => {
    const cached = localStorage.getItem('dashboard_cache')
    if (!cached) return true
    
    const { timestamp } = JSON.parse(cached)
    const age = new Date() - new Date(timestamp)
    return age > (maxAgeMinutes * 60 * 1000)
  }
}
