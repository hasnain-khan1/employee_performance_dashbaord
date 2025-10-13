import api from './axios'

export const reviewsAPI = {
  // Reviews
  getReviews: (params = {}) => api.get('/reviews/', { params }),
  getReview: (id) => api.get(`/reviews/${id}/`),
  createReview: (data) => api.post('/reviews/', data),
  updateReview: (id, data) => api.patch(`/reviews/${id}/`, data),
  deleteReview: (id) => api.delete(`/reviews/${id}/`),
  
  // Review sections
  getReviewSections: (reviewId) => api.get(`/reviews/${reviewId}/sections/`),
  createReviewSection: (reviewId, data) => api.post(`/reviews/${reviewId}/sections/`, data),
  updateReviewSection: (reviewId, sectionId, data) => 
    api.patch(`/reviews/${reviewId}/sections/${sectionId}/`, data),
  deleteReviewSection: (reviewId, sectionId) => 
    api.delete(`/reviews/${reviewId}/sections/${sectionId}/`),
  
  // Review templates
  getTemplates: () => api.get('/reviews/templates/'),
  createTemplate: (data) => api.post('/reviews/templates/', data),
  updateTemplate: (id, data) => api.patch(`/reviews/templates/${id}/`, data),
  deleteTemplate: (id) => api.delete(`/reviews/templates/${id}/`),
  
  // Review actions
  submitReview: (id) => api.post(`/reviews/${id}/submit/`),
  approveReview: (id, data) => api.post(`/reviews/${id}/approve/`, data),
  rejectReview: (id, data) => api.post(`/reviews/${id}/reject/`, data),
}