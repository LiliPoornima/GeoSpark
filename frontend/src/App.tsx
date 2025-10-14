import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { Layout } from './components/Layout'
import { Home } from './pages/Home'
import { Login } from './pages/Login'
import { Signup } from './pages/Signup'
import { Profile } from './pages/Profile'
import { Dashboard } from './pages/Dashboard'
import SparksChat from './pages/SparksChat'
import FullAnalysisPage from "./pages/FullAnalysisPage";


function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="site-analysis" element={<SiteAnalysis />} />
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
    </AuthProvider>
  )
}

export default App