import api from './axios'

export const analyticsAPI = {
  // Dashboard statistics
  getDashboardStats: () => api.get('/analytics/dashboard-stats/'),
  getEmployeeStats: () => api.get('/analytics/employee-stats/'),
  getManagerStats: () => api.get('/analytics/manager-stats/'),
  getHRStats: () => api.get('/analytics/hr-stats/'),
  
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
  getMetrics: (params = {}) => api.get('/analytics/metrics/', { params }),
  getMetric: (id) => api.get(`/analytics/metrics/${id}/`),
  createMetric: (data) => api.post('/analytics/metrics/', data),
  updateMetric: (id, data) => api.patch(`/analytics/metrics/${id}/`, data),
  deleteMetric: (id) => api.delete(`/analytics/metrics/${id}/`)
}

export default analyticsAPI
