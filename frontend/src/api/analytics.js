import api from './axios'

export const analyticsAPI = {
  // Reports
  getReports: (params = {}) => api.get('/analytics/reports/', { params }),
  getReport: (id) => api.get(`/analytics/reports/${id}/`),
  createReport: (data) => api.post('/analytics/reports/', data),
  updateReport: (id, data) => api.patch(`/analytics/reports/${id}/`, data),
  deleteReport: (id) => api.delete(`/analytics/reports/${id}/`),
  downloadReport: (id) => api.get(`/analytics/reports/${id}/download/`, { responseType: 'blob' }),
  
  // Dashboards
  getDashboards: (params = {}) => api.get('/analytics/dashboards/', { params }),
  getDashboard: (id) => api.get(`/analytics/dashboards/${id}/`),
  createDashboard: (data) => api.post('/analytics/dashboards/', data),
  updateDashboard: (id, data) => api.patch(`/analytics/dashboards/${id}/`, data),
  deleteDashboard: (id) => api.delete(`/analytics/dashboards/${id}/`),
  
  // Metrics
  getMetrics: () => api.get('/analytics/metrics/'),
  getMetric: (id) => api.get(`/analytics/metrics/${id}/`),
  createMetric: (data) => api.post('/analytics/metrics/', data),
  updateMetric: (id, data) => api.patch(`/analytics/metrics/${id}/`, data),
  deleteMetric: (id) => api.delete(`/analytics/metrics/${id}/`),
  
  // Analytics data
  getPerformanceData: (params = {}) => api.get('/analytics/performance/', { params }),
  getGoalsData: (params = {}) => api.get('/analytics/goals/', { params }),
  getFeedbackData: (params = {}) => api.get('/analytics/feedback/', { params }),
  getReviewsData: (params = {}) => api.get('/analytics/reviews/', { params }),
}