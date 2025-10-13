import api from './axios'

export const workflowsAPI = {
  // Workflow Steps
  getWorkflowSteps: (params = {}) => api.get('/workflows/steps/', { params }),
  getWorkflowStep: (id) => api.get(`/workflows/steps/${id}/`),
  createWorkflowStep: (data) => api.post('/workflows/steps/', data),
  updateWorkflowStep: (id, data) => api.patch(`/workflows/steps/${id}/`, data),
  deleteWorkflowStep: (id) => api.delete(`/workflows/steps/${id}/`),
  updateWorkflowStatus: (id, status) => api.post(`/workflows/steps/${id}/update-status/`, { status }),
  
  // Notifications
  getNotifications: (params = {}) => api.get('/workflows/notifications/', { params }),
  getNotification: (id) => api.get(`/workflows/notifications/${id}/`),
  markNotificationRead: (id) => api.post(`/workflows/notifications/${id}/mark-read/`),
  markAllNotificationsRead: () => api.post('/workflows/notifications/mark-all-read/'),
  
  // Audit Logs
  getAuditLogs: (params = {}) => api.get('/workflows/audit-logs/', { params }),
  getAuditLog: (id) => api.get(`/workflows/audit-logs/${id}/`),
}

export default workflowsAPI

