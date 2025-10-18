import api from './axios'

export const goalsAPI = {
  // Goals
  getGoals: (params = {}) => api.get('/goals/', { params }),
  getGoal: (id) => api.get(`/goals/${id}/`),
  createGoal: (data) => api.post('/goals/', data),
  updateGoal: (id, data) => api.patch(`/goals/${id}/`, data),
  deleteGoal: (id) => api.delete(`/goals/${id}/`),
  
  // Goal updates
  getGoalUpdates: (goalId) => api.get(`/goals/${goalId}/updates/`),
  createGoalUpdate: (goalId, data) => api.post(`/goals/${goalId}/updates/`, data),
  
  // Goal categories
  getCategories: () => api.get('/goals/categories/'),
  createCategory: (data) => api.post('/goals/categories/', data),
  updateCategory: (id, data) => api.patch(`/goals/categories/${id}/`, data),
  deleteCategory: (id) => api.delete(`/goals/categories/${id}/`),
  
  // Goal approval
  approveGoal: (id, data) => api.post(`/goals/${id}/approve/`, data),
  rejectGoal: (id, data) => api.post(`/goals/${id}/reject/`, data),
  submitGoalForApproval: (id) => api.post(`/goals/${id}/submit/`),
  
  // Manager-specific endpoints
  getManagerGoals: (params = {}) => api.get('/goals/manager/team/', { params }),
  submitGoalReview: (goalId, data) => api.post(`/goals/${goalId}/review/`, data),
  getGoalHistory: (goalId) => api.get(`/goals/${goalId}/history/`),
  submitBulkFeedback: (data) => api.post('/goals/bulk-feedback/', data),
}