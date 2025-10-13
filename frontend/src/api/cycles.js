import api from './axios'

export const cyclesAPI = {
  // Review cycles
  getCycles: (params = {}) => api.get('/cycles/', { params }),
  getCycle: (id) => api.get(`/cycles/${id}/`),
  createCycle: (data) => api.post('/cycles/', data),
  updateCycle: (id, data) => api.patch(`/cycles/${id}/`, data),
  deleteCycle: (id) => api.delete(`/cycles/${id}/`),
  
  // Cycle participants
  getCycleParticipants: (cycleId) => api.get(`/cycles/${cycleId}/participants/`),
  addCycleParticipant: (cycleId, data) => api.post(`/cycles/${cycleId}/participants/`, data),
  updateCycleParticipant: (cycleId, participantId, data) => 
    api.patch(`/cycles/${cycleId}/participants/${participantId}/`, data),
  removeCycleParticipant: (cycleId, participantId) => 
    api.delete(`/cycles/${cycleId}/participants/${participantId}/`),
  
  // Cycle templates
  getTemplates: () => api.get('/cycles/templates/'),
  createTemplate: (data) => api.post('/cycles/templates/', data),
  updateTemplate: (id, data) => api.patch(`/cycles/templates/${id}/`, data),
  deleteTemplate: (id) => api.delete(`/cycles/templates/${id}/`),
  
  // Cycle actions
  startCycle: (id) => api.post(`/cycles/${id}/start/`),
  completeCycle: (id) => api.post(`/cycles/${id}/complete/`),
  cancelCycle: (id) => api.post(`/cycles/${id}/cancel/`),
}