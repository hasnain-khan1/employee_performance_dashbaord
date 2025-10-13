import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// Import views
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardView from '@/views/DashboardView.vue'

// Employee views
import EmployeeGoalsView from '@/views/Employee/GoalsView.vue'
import EmployeeSelfReviewView from '@/views/Employee/SelfReviewView.vue'
import EmployeeFeedbackView from '@/views/Employee/FeedbackView.vue'

// Manager views
import ManagerTeamGoalsView from '@/views/Manager/TeamGoalsView.vue'
import ManagerTeamReviewsView from '@/views/Manager/TeamReviewsView.vue'
import ManagerFeedbackRequestsView from '@/views/Manager/FeedbackRequestsView.vue'

// HR views
import HREmployeesView from '@/views/HR/EmployeesView.vue'
import HRCyclesView from '@/views/HR/CyclesView.vue'
import HRAnalyticsView from '@/views/HR/AnalyticsView.vue'
import HRReportsView from '@/views/HR/ReportsView.vue'
import HRCSVImportView from '@/views/HR/CSVImportView.vue'

// Profile view
import ProfileView from '@/views/ProfileView.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false, layout: 'auth' }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresAuth: false, layout: 'auth' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  // Employee routes
  {
    path: '/employee/goals',
    name: 'EmployeeGoals',
    component: EmployeeGoalsView,
    meta: { requiresAuth: true, role: 'employee' }
  },
  {
    path: '/employee/self-review',
    name: 'EmployeeSelfReview',
    component: EmployeeSelfReviewView,
    meta: { requiresAuth: true, role: 'employee' }
  },
  {
    path: '/employee/feedback',
    name: 'EmployeeFeedback',
    component: EmployeeFeedbackView,
    meta: { requiresAuth: true, role: 'employee' }
  },
  // Manager routes
  {
    path: '/manager/team-goals',
    name: 'ManagerTeamGoals',
    component: ManagerTeamGoalsView,
    meta: { requiresAuth: true, role: 'manager' }
  },
  {
    path: '/manager/team-reviews',
    name: 'ManagerTeamReviews',
    component: ManagerTeamReviewsView,
    meta: { requiresAuth: true, role: 'manager' }
  },
  {
    path: '/manager/feedback-requests',
    name: 'ManagerFeedbackRequests',
    component: ManagerFeedbackRequestsView,
    meta: { requiresAuth: true, role: 'manager' }
  },
  // HR routes
  {
    path: '/hr/employees',
    name: 'HREmployees',
    component: HREmployeesView,
    meta: { requiresAuth: true, role: 'hr' }
  },
  {
    path: '/hr/cycles',
    name: 'HRCycles',
    component: HRCyclesView,
    meta: { requiresAuth: true, role: 'hr' }
  },
  {
    path: '/hr/analytics',
    name: 'HRAnalytics',
    component: HRAnalyticsView,
    meta: { requiresAuth: true, role: 'hr' }
  },
  {
    path: '/hr/reports',
    name: 'HRReports',
    component: HRReportsView,
    meta: { requiresAuth: true, role: 'hr' }
  },
  {
    path: '/hr/csv-import',
    name: 'HRCSVImport',
    component: HRCSVImportView,
    meta: { requiresAuth: true, role: 'hr' }
  },
  // Catch all route
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }
    
    // Check role-based access
    if (to.meta.role && authStore.user?.role !== to.meta.role) {
      // Check if user has higher privilege
      const roleHierarchy = {
        'employee': 1,
        'manager': 2,
        'hr': 3,
        'admin': 4
      }
      
      const userRoleLevel = roleHierarchy[authStore.user?.role] || 0
      const requiredRoleLevel = roleHierarchy[to.meta.role] || 0
      
      if (userRoleLevel < requiredRoleLevel) {
        next('/dashboard')
        return
      }
    }
  }
  
  // Redirect authenticated users away from auth pages
  if (to.meta.requiresAuth === false && authStore.isAuthenticated) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router