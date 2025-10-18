import api from './axios'

// Self Review API - specific methods for self-review functionality
export const selfReviewAPI = {
  // Get current self-review for the logged-in user
  getCurrentSelfReview: () => api.get('/reviews/self/current/'),
  
  // Check prerequisites for self-review
  checkPrerequisites: () => api.get('/reviews/self/prerequisites/'),
  
  // Save draft of self-review
  saveDraft: (sectionType, data) => api.post(`/reviews/self/draft/${sectionType}/`, data),
  
  // Save complete self-review
  saveSelfReview: (data) => api.post('/reviews/self/save/', data),
  
  // Submit self-review
  submitSelfReview: (data) => api.post('/reviews/self/submit/', data),
  
  // Auto-save functionality
  autoSave: (data) => api.post('/reviews/self/auto-save/', data),
  
  // Self-Review endpoints
  getSelfReviews: (params = {}) => api.get('/reviews/self/', { params }),
  getSelfReview: (id) => api.get(`/reviews/self/${id}/`),
  createSelfReview: (data) => api.post('/reviews/self/', data),
  updateSelfReview: (id, data) => api.patch(`/reviews/self/${id}/`, data),
  deleteSelfReview: (id) => api.delete(`/reviews/self/${id}/`),
  
  // Self-Review sections
  getSelfReviewSections: (selfReviewId) => api.get(`/reviews/self/${selfReviewId}/sections/`),
  updateSelfReviewSection: (selfReviewId, sectionId, data) => api.patch(`/reviews/self/${selfReviewId}/sections/${sectionId}/`, data),
  
  // Evidence links
  getEvidenceLinks: (selfReviewId) => api.get(`/reviews/self/${selfReviewId}/evidence/`),
  createEvidenceLink: (selfReviewId, data) => api.post(`/reviews/self/${selfReviewId}/evidence/`, data),
  updateEvidenceLink: (selfReviewId, linkId, data) => api.patch(`/reviews/self/${selfReviewId}/evidence/${linkId}/`, data),
  deleteEvidenceLink: (selfReviewId, linkId) => api.delete(`/reviews/self/${selfReviewId}/evidence/${linkId}/`),
  
  // Self-Review drafts
  getSelfReviewDrafts: (selfReviewId) => api.get(`/reviews/self/${selfReviewId}/drafts/`),
  saveSelfReviewDraft: (selfReviewId, data) => api.post(`/reviews/self/${selfReviewId}/drafts/`, data),
  
  // Self-Review audit trail
  getSelfReviewAuditTrail: (selfReviewId) => api.get(`/reviews/self/${selfReviewId}/audit-trail/`),
  
  // Templates
  getSelfReviewTemplates: (params = {}) => api.get('/reviews/templates/', { params }),
  getSelfReviewTemplate: (id) => api.get(`/reviews/templates/${id}/`)
}

// Manager Review API
export const managerReviewAPI = {
  // Manager Review endpoints
  getManagerReviews: (params = {}) => api.get('/reviews/manager/', { params }),
  getManagerReview: (id) => api.get(`/reviews/manager/${id}/`),
  createManagerReview: (data) => api.post('/reviews/manager/', data),
  updateManagerReview: (id, data) => api.patch(`/reviews/manager/${id}/`, data),
  deleteManagerReview: (id) => api.delete(`/reviews/manager/${id}/`),
  submitManagerReview: (id) => api.post(`/reviews/manager/${id}/submit/`),
  
  // Manager Review attachments
  uploadReviewAttachment: (reviewId, data) => api.post(`/reviews/manager/${reviewId}/attachments/`, data),
  getReviewAttachments: (reviewId) => api.get(`/reviews/manager/${reviewId}/attachments/`),
  deleteReviewAttachment: (attachmentId) => api.delete(`/reviews/attachments/${attachmentId}/`),
  
  // Bulk actions
  bulkReviewAction: (data) => api.post('/reviews/manager/bulk-action/', data),
  
  // Review statistics
  getReviewStatistics: () => api.get('/reviews/manager/statistics/'),
  
  // Employee dossier
  getEmployeeDossier: (employeeId) => api.get(`/reviews/dossier/${employeeId}/`),
  
  // Review locking/unlocking
  lockReview: (id) => api.post(`/reviews/manager/${id}/lock/`),
  unlockReview: (id) => api.post(`/reviews/manager/${id}/unlock/`),
  
  // Review audit trail
  getReviewAuditTrail: (reviewId) => api.get(`/reviews/manager/${reviewId}/audit-trail/`)
}

// Combined reviews API for backward compatibility
export const reviewsAPI = {
  ...selfReviewAPI,
  ...managerReviewAPI
}