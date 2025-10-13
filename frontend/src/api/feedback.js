import api from './axios'

export const feedbackAPI = {
  // Feedback requests
  getFeedbackRequests: (params = {}) => api.get('/feedback/', { params }),
  getFeedbackRequest: (id) => api.get(`/feedback/${id}/`),
  createFeedbackRequest: (data) => api.post('/feedback/', data),
  updateFeedbackRequest: (id, data) => api.patch(`/feedback/${id}/`, data),
  deleteFeedbackRequest: (id) => api.delete(`/feedback/${id}/`),
  
  // Feedback responses
  getFeedbackResponse: (requestId) => api.get(`/feedback/${requestId}/response/`),
  createFeedbackResponse: (requestId, data) => api.post(`/feedback/${requestId}/response/`, data),
  updateFeedbackResponse: (requestId, data) => api.patch(`/feedback/${requestId}/response/`, data),
  
  // Feedback templates
  getTemplates: () => api.get('/feedback/templates/'),
  createTemplate: (data) => api.post('/feedback/templates/', data),
  updateTemplate: (id, data) => api.patch(`/feedback/templates/${id}/`, data),
  deleteTemplate: (id) => api.delete(`/feedback/templates/${id}/`),
  
  // Feedback actions
  acceptFeedbackRequest: (id) => api.post(`/feedback/${id}/accept/`),
  declineFeedbackRequest: (id, data) => api.post(`/feedback/${id}/decline/`, data),
  submitFeedbackResponse: (id, data) => api.post(`/feedback/${id}/submit/`, data),
}