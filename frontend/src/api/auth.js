import api from './axios'

export const authAPI = {
  // Authentication
  login: (credentials) => api.post('/auth/login/', credentials),
  register: (userData) => api.post('/auth/register/', userData),
  logout: (data) => api.post('/auth/logout/', data),
  refreshToken: (data) => api.post('/auth/token/refresh/', data),
  
  // Profile management
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
  updateProfileExtended: (data) => api.patch('/auth/profile/extended/', data),
  
  // Password management
  changePassword: (data) => api.post('/auth/change-password/', data),
  resetPassword: (data) => api.post('/auth/reset-password/', data),
  
  // User management
  getUsers: (params = {}) => api.get('/auth/users/', { params }),
  getUser: (id) => api.get(`/auth/users/${id}/`),
  updateUser: (id, data) => api.patch(`/auth/users/${id}/`, data),
}