import React, { useState } from 'react'
import { apiEndpoints } from '../services/api'
import toast from 'react-hot-toast'
import { FileText, Download } from 'lucide-react'

export function Reports() {
  const [form, setForm] = useState({
    project_type: 'solar',
    capacity_mw: 100,
    location: { latitude: 0, longitude: 0 },
  })
  const [report, setReport] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)

  const onChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    if (name === 'latitude' || name === 'longitude') {
      setForm(prev => ({ ...prev, location: { ...prev.location, [name]: parseFloat(value) } }))
    } else if (name === 'capacity_mw') {
      setForm(prev => ({ ...prev, [name]: parseFloat(value) }))
    } else {
      setForm(prev => ({ ...prev, [name]: value }))
    }
  }

  const generate = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      const resp = await apiEndpoints.generateReport({ project_data: form })
      setReport(resp.data.report)
      toast.success('Report generated')
    } catch (err) {
      toast.error('Failed to generate report')
    } finally {
      setIsLoading(false)
    }
  }

  const download = () => {
    const blob = new Blob([report], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'geospark_report.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600">Generate and download project reports</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center"><FileText className="h-5 w-5 mr-2"/>Report Inputs</h2>
          <form className="space-y-4" onSubmit={generate}>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Project Type</label>
              <select name="project_type" value={form.project_type} onChange={onChange} className="w-full px-3 py-2 border rounded-md">
                <option value="solar">Solar</option>
                <option value="wind">Wind</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Capacity (MW)</label>
                <input type="number" name="capacity_mw" value={form.capacity_mw} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Latitude</label>
                <input type="number" name="latitude" value={form.location.latitude} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Longitude</label>
                <input type="number" name="longitude" value={form.location.longitude} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
              </div>
            </div>
            <button type="submit" disabled={isLoading} className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 disabled:opacity-50">{isLoading ? 'Generating...' : 'Generate Report'}</button>
          </form>
        </div>

        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Report Preview</h2>
            <button onClick={download} disabled={!report} className="flex items-center bg-gray-800 text-white px-3 py-2 rounded-md disabled:opacity-50"><Download className="h-4 w-4 mr-1"/>Download</button>
          </div>
          <pre className="whitespace-pre-wrap text-sm text-gray-800 bg-gray-50 p-4 rounded min-h-[200px]">{report || 'Generate a report to preview here.'}</pre>
        </div>
      </div>
    </div>
  )
}