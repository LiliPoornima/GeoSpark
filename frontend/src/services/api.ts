import axios from 'axios'

export const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const apiEndpoints = {
  // Authentication
  authenticate: (credentials: { username: string; password: string }) =>
    api.post('/authenticate', credentials),
  
  // Site Analysis
  analyzeSite: (data: any) =>
    api.post('/site-analysis', data),
  
  // Resource Estimation
  estimateResources: (data: any) =>
    api.post('/resource-estimation', data),
  
  // Cost Evaluation
  evaluateCosts: (data: any) =>
    api.post('/cost-evaluation', data),
  
  // Report Generation
  generateReport: (data: any) =>
    api.post('/generate-report', data),
  
  // Text Analysis
  analyzeText: (data: { text: string; analysis_type?: string }) =>
    api.post('/text-analysis', data),
  
  // Data Search
  searchData: (data: any) =>
    api.post('/data-search', data),
  
  // System Status
  getSystemStatus: () =>
    api.get('/system-status'),
  
  // Data Statistics
  getDataStatistics: () =>
    api.get('/data-statistics'),
}