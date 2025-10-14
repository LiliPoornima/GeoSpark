import React, { Suspense } from 'react'
import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { Layout } from './components/Layout'
import { Home } from './pages/Home'
// Dynamic lazy element to avoid stale bindings during HMR
const LazySiteAnalysisElement = (
  <React.Suspense fallback={<div style={{ padding: 24 }}>Loading Site Analysis...</div>}>
    {React.createElement(React.lazy(() => import('./pages/SiteAnalysis')))}
  </React.Suspense>
)
import { ResourceEstimation } from './pages/ResourceEstimation'
import { CostEvaluation } from './pages/CostEvaluation'
import {Reports}from './pages/Reports'
//import { Agent } from './pages/Agent'
import { Login } from './pages/Login'
import { Signup } from './pages/Signup'
import { Profile } from './pages/Profile'
import { Dashboard } from './pages/Dashboard'
import SparksChat from './pages/SparksChat'
import FullAnalysisPage from "./pages/FullAnalysisPage";


function App() {
  // Expose a small debug flag to verify this build is loaded in the browser
  ;(globalThis as any).__APP_DEBUG__ = {
    buildTime: new Date().toISOString(),
    siteAnalysisBindingType: 'lazy-element',
  }
  return (
    <AuthProvider>
      <Suspense fallback={<div style={{ padding: 24 }}>Loading...</div>}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="site-analysis" element={LazySiteAnalysisElement} />
          <Route path="resource-estimation" element={<ResourceEstimation />} />
          <Route path="cost-evaluation" element={<CostEvaluation />} />
          <Route path="reports" element={<Reports />} />
          
          {/* <Route path="agent" element={<Agent />} /> */}
          {/* <Route path='chatbot' element={<Chatbot/>}/> */}
          <Route path='sparks' element={<SparksChat/>}/>
          <Route path="profile" element={<Profile />} />
          <Route path="/full-analysis" element={<FullAnalysisPage />} />

        </Route>
      </Routes>
      </Suspense>
    </AuthProvider>
  )
}

export default App