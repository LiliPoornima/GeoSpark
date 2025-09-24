import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { Layout } from './components/Layout'
import { Home } from './pages/Home'
import { SiteAnalysis } from './pages/SiteAnalysis'
import { ResourceEstimation } from './pages/ResourceEstimation'
import { CostEvaluation } from './pages/CostEvaluation'
import { Reports } from './pages/Reports'
import { AllInOne } from './pages/AllInOne'
import { Login } from './pages/Login'
import { Dashboard } from './pages/Dashboard'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="site-analysis" element={<SiteAnalysis />} />
          <Route path="resource-estimation" element={<ResourceEstimation />} />
          <Route path="cost-evaluation" element={<CostEvaluation />} />
          <Route path="reports" element={<Reports />} />
          <Route path="all" element={<AllInOne />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}

export default App