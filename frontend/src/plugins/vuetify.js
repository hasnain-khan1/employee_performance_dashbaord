import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          // Primary brand colors - Professional blue gradient
          primary: '#2563EB', // Modern blue
          'primary-darken-1': '#1D4ED8',
          'primary-darken-2': '#1E40AF',
          'primary-lighten-1': '#3B82F6',
          'primary-lighten-2': '#60A5FA',
          'primary-lighten-3': '#93C5FD',
          'primary-lighten-4': '#DBEAFE',
          'primary-lighten-5': '#EFF6FF',
          
          // Secondary colors - Sophisticated slate
          secondary: '#475569', // Slate-600
          'secondary-darken-1': '#334155',
          'secondary-darken-2': '#1E293B',
          'secondary-lighten-1': '#64748B',
          'secondary-lighten-2': '#94A3B8',
          'secondary-lighten-3': '#CBD5E1',
          'secondary-lighten-4': '#E2E8F0',
          'secondary-lighten-5': '#F1F5F9',
          
          // Accent colors - Vibrant but professional
          accent: '#7C3AED', // Purple accent
          'accent-darken-1': '#6D28D9',
          'accent-lighten-1': '#8B5CF6',
          'accent-lighten-2': '#A78BFA',
          'accent-lighten-3': '#C4B5FD',
          'accent-lighten-4': '#EDE9FE',
          
          // Status colors - Modern and accessible
          success: '#10B981', // Emerald-500
          'success-darken-1': '#059669',
          'success-lighten-1': '#34D399',
          'success-lighten-2': '#6EE7B7',
          'success-lighten-3': '#A7F3D0',
          'success-lighten-4': '#D1FAE5',
          
          warning: '#F59E0B', // Amber-500
          'warning-darken-1': '#D97706',
          'warning-lighten-1': '#FBBF24',
          'warning-lighten-2': '#FCD34D',
          'warning-lighten-3': '#FDE68A',
          'warning-lighten-4': '#FEF3C7',
          
          error: '#EF4444', // Red-500
          'error-darken-1': '#DC2626',
          'error-lighten-1': '#F87171',
          'error-lighten-2': '#FCA5A5',
          'error-lighten-3': '#FECACA',
          'error-lighten-4': '#FEE2E2',
          
          info: '#06B6D4', // Cyan-500
          'info-darken-1': '#0891B2',
          'info-lighten-1': '#22D3EE',
          'info-lighten-2': '#67E8F9',
          'info-lighten-3': '#A5F3FC',
          'info-lighten-4': '#CFFAFE',
          
          // Neutral colors
          surface: '#FFFFFF',
          'surface-bright': '#FFFFFF',
          'surface-light': '#F8FAFC',
          'surface-variant': '#F1F5F9',
          'surface-container': '#F8FAFC',
          'surface-container-high': '#F1F5F9',
          'surface-container-highest': '#E2E8F0',
          
          // Text colors
          'on-surface': '#0F172A',
          'on-surface-variant': '#475569',
          'on-primary': '#FFFFFF',
          'on-secondary': '#FFFFFF',
          'on-success': '#FFFFFF',
          'on-warning': '#FFFFFF',
          'on-error': '#FFFFFF',
          'on-info': '#FFFFFF',
          
          // Background colors
          background: '#F8FAFC',
          'background-darken-1': '#F1F5F9',
          'background-darken-2': '#E2E8F0',
        },
      },
      dark: {
        dark: true,
        colors: {
          // Dark theme with professional colors
          primary: '#3B82F6',
          'primary-darken-1': '#2563EB',
          'primary-darken-2': '#1D4ED8',
          'primary-lighten-1': '#60A5FA',
          'primary-lighten-2': '#93C5FD',
          'primary-lighten-3': '#DBEAFE',
          
          secondary: '#64748B',
          'secondary-darken-1': '#475569',
          'secondary-darken-2': '#334155',
          'secondary-lighten-1': '#94A3B8',
          'secondary-lighten-2': '#CBD5E1',
          'secondary-lighten-3': '#E2E8F0',
          
          accent: '#8B5CF6',
          'accent-darken-1': '#7C3AED',
          'accent-lighten-1': '#A78BFA',
          'accent-lighten-2': '#C4B5FD',
          'accent-lighten-3': '#EDE9FE',
          
          success: '#34D399',
          warning: '#FBBF24',
          error: '#F87171',
          info: '#22D3EE',
          
          surface: '#0F172A',
          'surface-bright': '#1E293B',
          'surface-light': '#334155',
          'surface-variant': '#475569',
          'surface-container': '#1E293B',
          'surface-container-high': '#334155',
          'surface-container-highest': '#475569',
          
          'on-surface': '#F8FAFC',
          'on-surface-variant': '#CBD5E1',
          'on-primary': '#FFFFFF',
          'on-secondary': '#FFFFFF',
          'on-success': '#FFFFFF',
          'on-warning': '#FFFFFF',
          'on-error': '#FFFFFF',
          'on-info': '#FFFFFF',
          
          background: '#0F172A',
          'background-darken-1': '#1E293B',
          'background-darken-2': '#334155',
        },
      },
    },
  },
  defaults: {
    VBtn: {
      color: 'primary',
      variant: 'flat',
      rounded: 'lg',
      elevation: 0,
    },
    VCard: {
      variant: 'elevated',
      elevation: 2,
      rounded: 'xl',
    },
    VTextField: {
      variant: 'outlined',
      rounded: 'lg',
      density: 'comfortable',
    },
    VTextarea: {
      variant: 'outlined',
      rounded: 'lg',
      density: 'comfortable',
    },
    VSelect: {
      variant: 'outlined',
      rounded: 'lg',
      density: 'comfortable',
    },
    VDataTable: {
      density: 'comfortable',
      rounded: 'lg',
    },
    VChip: {
      rounded: 'lg',
      size: 'small',
    },
    VProgressLinear: {
      rounded: 'lg',
      height: 8,
    },
    VAppBar: {
      elevation: 0,
      color: 'primary',
    },
    VNavigationDrawer: {
      elevation: 0,
    },
  },
})