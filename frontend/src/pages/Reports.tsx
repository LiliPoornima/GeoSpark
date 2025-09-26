import React, { useState } from 'react'
import { apiEndpoints } from '../services/api'
import toast from 'react-hot-toast'

export function Reports() {
  const [projectData, setProjectData] = useState<any>({
    name: 'Demo Project',
    location: { latitude: 7.2931, longitude: 80.6350 },
    capacity_mw: 100,
    resource_type: 'solar',
  })
  const [report, setReport] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const onChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setProjectData({ ...projectData, [name]: name === 'capacity_mw' ? parseFloat(value) : value })
  }

  const onGenerate = async () => {
    setIsLoading(true)
    try {
      const resp = await apiEndpoints.analyzeText({
        text: `Generate a concise project report for ${projectData.name} at (${projectData.location.latitude}, ${projectData.location.longitude}). Resource: ${projectData.resource_type}. Capacity: ${projectData.capacity_mw} MW.`,
        analysis_type: 'report'
      })
      const analysis = resp.data.analysis
      const content = `Project: ${projectData.name}\nResource: ${projectData.resource_type}\nCapacity: ${projectData.capacity_mw} MW\n\nSummary:\nSentiment: ${analysis.sentiment}\nWord Count: ${analysis.word_count}\nProcessed: ${analysis.processed_at}`
      setReport(content)
      toast.success('Report generated')
    } catch (e) {
      toast.error('Failed to generate report')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600">Generate a simple project report</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Project Name</label>
            <input name="name" value={projectData.name} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Resource Type</label>
            <select name="resource_type" value={projectData.resource_type} onChange={onChange} className="w-full px-3 py-2 border rounded-md">
              <option value="solar">Solar</option>
              <option value="wind">Wind</option>
              <option value="hybrid">Hybrid</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Capacity (MW)</label>
            <input name="capacity_mw" type="number" value={projectData.capacity_mw} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
          </div>
          <button onClick={onGenerate} disabled={isLoading} className="w-full bg-green-600 text-white py-2 px-4 rounded-md disabled:opacity-50">{isLoading ? 'Generating...' : 'Generate Report'}</button>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-2">Report</h2>
          {!report ? (
            <div className="text-gray-500">Fill details and click Generate to view a report.</div>
          ) : (
            <pre className="whitespace-pre-wrap text-sm text-gray-800">{report}</pre>
          )}
        </div>
      </div>
    </div>
  )
}