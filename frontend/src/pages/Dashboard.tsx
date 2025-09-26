import React, { useState } from 'react'
import { apiEndpoints } from '../services/api'
import toast from 'react-hot-toast'

export function Dashboard() {
  const [city, setCity] = useState('')
  const [coords, setCoords] = useState<{lat: number; lon: number} | null>(null)
  const [site, setSite] = useState<any>(null)
  const [resource, setResource] = useState<any>(null)
  const [cost, setCost] = useState<any>(null)
  const [report, setReport] = useState<string>('')
  const [resourceType, setResourceType] = useState('solar')
  const [isLoading, setIsLoading] = useState(false)

  const geocode = async () => {
    if (city.length < 3) return
    const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city)}&limit=1`)
    const data = await res.json()
    if (data?.length) {
      setCoords({ lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon) })
    } else {
      toast.error('City not found')
    }
  }

  const runAll = async () => {
    try {
      setIsLoading(true)
      if (!coords) await geocode()
      const { lat, lon } = coords || { lat: 0, lon: 0 }
      // 1) Site analysis
      const siteResp = await apiEndpoints.analyzeSite({
        location: { latitude: lat, longitude: lon, area_km2: 100 },
        project_type: resourceType,
        analysis_depth: 'comprehensive'
      })
      setSite(siteResp.data.analysis)

      // 2) Resource estimation
      const resResp = await apiEndpoints.estimateResources({
        location: { latitude: lat, longitude: lon, area_km2: 100 },
        resource_type: resourceType,
        system_config: {}
      })
      setResource(resResp.data.estimation)

      // 3) Cost evaluation
      const costResp = await apiEndpoints.evaluateCosts({
        project_data: {
          project_type: resourceType,
          capacity_mw: siteResp.data.analysis.estimated_capacity_mw,
          annual_generation_gwh: resResp.data.estimation.annual_generation_gwh
        },
        financial_params: { electricity_price_usd_mwh: 50, project_lifetime: 25, discount_rate: 0.08 }
      })
      setCost(costResp.data.evaluation)

      // 4) Report (simple)
      const text = `Generate a brief project report for ${city} (${lat}, ${lon}). Resource: ${resourceType}. Capacity: ${siteResp.data.analysis.estimated_capacity_mw} MW. Annual generation: ${resResp.data.estimation.annual_generation_gwh} GWh.`
      const repResp = await apiEndpoints.analyzeText({ text, analysis_type: 'report' })
      setReport(`Project: ${city}\nResource: ${resourceType}\nCapacity: ${siteResp.data.analysis.estimated_capacity_mw} MW\nGeneration: ${resResp.data.estimation.annual_generation_gwh} GWh\n\nSummary: ${repResp.data.analysis.sentiment}`)

      toast.success('All analyses completed')
    } catch (e) {
      toast.error('One of the analyses failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-end gap-3">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
          <input value={city} onChange={(e)=>setCity(e.target.value)} onBlur={geocode} className="w-full px-3 py-2 border rounded-md" placeholder="Enter a city" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Resource</label>
          <select className="px-3 py-2 border rounded-md" value={resourceType} onChange={e=>setResourceType(e.target.value)}>
            <option value="solar">Solar</option>
            <option value="wind">Wind</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </div>
        <button onClick={runAll} disabled={isLoading} className="bg-green-600 text-white px-4 py-2 rounded-md">{isLoading ? 'Running...' : 'Analyze'}</button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-2">Site Analysis</h3>
          <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(site, null, 2) || 'No data yet'}</pre>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-2">Resource Estimation</h3>
          <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(resource, null, 2) || 'No data yet'}</pre>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-2">Cost Evaluation</h3>
          <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(cost, null, 2) || 'No data yet'}</pre>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-2">Report</h3>
          <pre className="text-xs whitespace-pre-wrap">{report || 'No report yet'}</pre>
        </div>
      </div>
      <DashboardOverview />
    </div>
  )
}
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

function DashboardOverview() {
  // Mock data for demonstration
  const projectData = [
    { name: 'Solar', value: 45, count: 120 },
    { name: 'Wind', value: 30, count: 80 },
    { name: 'Hybrid', value: 25, count: 65 }
  ]

  const monthlyData = [
    { month: 'Jan', analyses: 45, capacity: 1200 },
    { month: 'Feb', analyses: 52, capacity: 1350 },
    { month: 'Mar', analyses: 48, capacity: 1280 },
    { month: 'Apr', analyses: 61, capacity: 1580 },
    { month: 'May', analyses: 55, capacity: 1420 },
    { month: 'Jun', analyses: 67, capacity: 1750 }
  ]

  const COLORS = ['#10B981', '#3B82F6', '#8B5CF6']

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of your renewable energy analysis activities</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="bg-green-100 p-3 rounded-lg">
              <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Analyses</p>
              <p className="text-2xl font-semibold text-gray-900">265</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="bg-blue-100 p-3 rounded-lg">
              <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Capacity Analyzed</p>
              <p className="text-2xl font-semibold text-gray-900">8.5 GW</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="bg-purple-100 p-3 rounded-lg">
              <svg className="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg. Score</p>
              <p className="text-2xl font-semibold text-gray-900">87%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="bg-yellow-100 p-3 rounded-lg">
              <svg className="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Time Saved</p>
              <p className="text-2xl font-semibold text-gray-900">340h</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Project Types */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Types</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={projectData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {projectData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Monthly Trends */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="analyses" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {[
            { project: 'Solar Farm - Texas', score: 92, date: '2 hours ago' },
            { project: 'Wind Project - California', score: 88, date: '5 hours ago' },
            { project: 'Hybrid System - Nevada', score: 85, date: '1 day ago' },
            { project: 'Solar Installation - Arizona', score: 91, date: '2 days ago' }
          ].map((activity, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium text-gray-900">{activity.project}</p>
                <p className="text-sm text-gray-600">{activity.date}</p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-green-600">{activity.score}%</p>
                <p className="text-sm text-gray-600">Score</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}