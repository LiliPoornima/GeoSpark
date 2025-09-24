import React, { useState } from 'react'
import { apiEndpoints } from '../services/api'
import toast from 'react-hot-toast'
import { Search, MapPin, Map, Gauge, BarChart3, TrendingUp, DollarSign, FileText, Download } from 'lucide-react'

export function AllInOne() {
  const [form, setForm] = useState({
    latitude: '',
    longitude: '',
    area_km2: '100',
    project_type: 'solar',
    resource_type: 'solar',
  })
  const [isLoading, setIsLoading] = useState(false)
  const [analysis, setAnalysis] = useState<any>(null)
  const [estimation, setEstimation] = useState<any>(null)
  const [cost, setCost] = useState<any>(null)
  const [report, setReport] = useState<string>('')
  const [finParams, setFinParams] = useState({ electricity_price_usd_mwh: 50, project_lifetime: 25, discount_rate: 0.08, capex_per_mw_override: '', opex_per_mw_override: '' })

  const onChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: value }))
  }

  const runAll = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.latitude || !form.longitude) {
      toast.error('Please enter latitude and longitude')
      return
    }
    setIsLoading(true)
    setAnalysis(null); setEstimation(null); setCost(null); setReport('')
    try {
      // 1) Site analysis
      const siteResp = await apiEndpoints.analyzeSite({
        location: {
          latitude: parseFloat(form.latitude),
          longitude: parseFloat(form.longitude),
          area_km2: parseFloat(form.area_km2) || 100
        },
        project_type: form.project_type,
        analysis_depth: 'comprehensive'
      })
      setAnalysis(siteResp.data.analysis)

      // 2) Resource estimation
      const estResp = await apiEndpoints.estimateResources({
        location: {
          latitude: parseFloat(form.latitude),
          longitude: parseFloat(form.longitude),
          area_km2: parseFloat(form.area_km2) || 100
        },
        resource_type: form.resource_type,
        system_config: {}
      })
      setEstimation(estResp.data.estimation)

      // 3) Cost evaluation
      const peakPower = estResp.data.estimation?.peak_power_mw ?? 100
      const annualGen = estResp.data.estimation?.annual_generation_gwh ?? 200
      const costResp = await apiEndpoints.evaluateCosts({
        project_data: { project_type: form.project_type, capacity_mw: peakPower, annual_generation_gwh: annualGen },
        financial_params: {
          electricity_price_usd_mwh: finParams.electricity_price_usd_mwh,
          project_lifetime: finParams.project_lifetime,
          discount_rate: finParams.discount_rate,
          capex_per_mw_override: finParams.capex_per_mw_override ? parseFloat(String(finParams.capex_per_mw_override)) : undefined,
          opex_per_mw_override: finParams.opex_per_mw_override ? parseFloat(String(finParams.opex_per_mw_override)) : undefined,
        }
      })
      setCost(costResp.data.evaluation)

      // 4) Report
      const reportResp = await apiEndpoints.generateReport({
        project_data: {
          project_type: form.project_type,
          capacity_mw: peakPower,
          location: { latitude: parseFloat(form.latitude), longitude: parseFloat(form.longitude) },
          financials: {
            annual_revenue: costResp.data.evaluation.annual_revenue_usd,
            npv: costResp.data.evaluation.financial_metrics.net_present_value_usd,
            irr: costResp.data.evaluation.financial_metrics.internal_rate_of_return,
            lcoe: costResp.data.evaluation.financial_metrics.levelized_cost_of_energy_usd_mwh,
            payback: costResp.data.evaluation.financial_metrics.payback_period_years,
          }
        }
      })
      setReport(reportResp.data.report)

      toast.success('All analyses completed')
    } catch (err) {
      toast.error('Failed to complete analyses')
    } finally {
      setIsLoading(false)
    }
  }

  const download = () => {
    if (!report) return
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
        <h1 className="text-2xl font-bold text-gray-900">All-in-One Analysis</h1>
        <p className="text-gray-600">Run site analysis, resource estimation, cost evaluation, and report generation in one place</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center"><Search className="h-5 w-5 mr-2"/>Inputs</h2>
          <form className="space-y-4" onSubmit={runAll}>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Latitude</label>
                <input type="number" step="any" name="latitude" value={form.latitude} onChange={onChange} className="w-full px-3 py-2 border rounded-md" placeholder="40.7128" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Longitude</label>
                <input type="number" step="any" name="longitude" value={form.longitude} onChange={onChange} className="w-full px-3 py-2 border rounded-md" placeholder="-74.0060" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Area (km²)</label>
              <input type="number" step="any" name="area_km2" value={form.area_km2} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Project Type</label>
                <select name="project_type" value={form.project_type} onChange={onChange} className="w-full px-3 py-2 border rounded-md">
                  <option value="solar">Solar</option>
                  <option value="wind">Wind</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Resource Type</label>
                <select name="resource_type" value={form.resource_type} onChange={onChange} className="w-full px-3 py-2 border rounded-md">
                  <option value="solar">Solar</option>
                  <option value="wind">Wind</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>
            </div>
            <button type="submit" disabled={isLoading} className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 disabled:opacity-50">{isLoading ? 'Running...' : 'Run All'}</button>
          </form>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center"><Map className="h-5 w-5 mr-2"/>Location</h2>
          {form.latitude && form.longitude ? (
            <div className="text-sm text-gray-700">
              <div className="flex items-center"><MapPin className="h-4 w-4 mr-2"/>Lat: {form.latitude}, Lon: {form.longitude}</div>
            </div>
          ) : (
            <div className="text-gray-500">Enter coordinates to view details.</div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Site Analysis</h2>
          {analysis ? (
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-green-50 rounded">
                <div className="text-sm text-gray-600">Overall Score</div>
                <div className="text-xl font-semibold">{(analysis.overall_score * 100).toFixed(0)}%</div>
              </div>
              <div className="p-3 bg-blue-50 rounded">
                <div className="text-sm text-gray-600">Capacity (MW)</div>
                <div className="text-xl font-semibold">{analysis.estimated_capacity_mw}</div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500">Run to see analysis.</div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Resource Estimation</h2>
          {estimation ? (
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 bg-purple-50 rounded"><Gauge className="h-5 w-5 mx-auto mb-1"/><div className="text-sm text-gray-600">Capacity Factor</div><div className="font-semibold">{(estimation.capacity_factor * 100).toFixed(1)}%</div></div>
              <div className="text-center p-3 bg-yellow-50 rounded"><BarChart3 className="h-5 w-5 mx-auto mb-1"/><div className="text-sm text-gray-600">Annual Gen</div><div className="font-semibold">{estimation.annual_generation_gwh.toFixed(1)} GWh</div></div>
              <div className="text-center p-3 bg-indigo-50 rounded"><TrendingUp className="h-5 w-5 mx-auto mb-1"/><div className="text-sm text-gray-600">Peak Power</div><div className="font-semibold">{estimation.peak_power_mw.toFixed(1)} MW</div></div>
            </div>
          ) : (
            <div className="text-gray-500">Run to see estimation.</div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center"><DollarSign className="h-5 w-5 mr-2"/>Cost Evaluation</h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Electricity Price (USD/MWh)</label>
              <input type="number" value={finParams.electricity_price_usd_mwh} onChange={(e)=>setFinParams({...finParams, electricity_price_usd_mwh: parseFloat(e.target.value)})} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Discount Rate</label>
              <input type="number" step="0.01" value={finParams.discount_rate} onChange={(e)=>setFinParams({...finParams, discount_rate: parseFloat(e.target.value)})} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Lifetime (years)</label>
              <input type="number" value={finParams.project_lifetime} onChange={(e)=>setFinParams({...finParams, project_lifetime: parseInt(e.target.value)})} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">CAPEX override ($/MW)</label>
              <input type="number" value={finParams.capex_per_mw_override} onChange={(e)=>setFinParams({...finParams, capex_per_mw_override: e.target.value})} className="w-full px-3 py-2 border rounded-md" placeholder="optional" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">OPEX override ($/MW/yr)</label>
              <input type="number" value={finParams.opex_per_mw_override} onChange={(e)=>setFinParams({...finParams, opex_per_mw_override: e.target.value})} className="w-full px-3 py-2 border rounded-md" placeholder="optional" />
            </div>
          </div>
          {cost ? (
            <div className="grid grid-cols-3 gap-4">
              <div className="p-3 bg-green-50 rounded"><div className="text-sm text-gray-600">CAPEX</div><div className="text-lg font-semibold">{cost.total_capex_usd.toLocaleString()}</div></div>
              <div className="p-3 bg-blue-50 rounded"><div className="text-sm text-gray-600">OPEX</div><div className="text-lg font-semibold">{cost.annual_opex_usd.toLocaleString()}</div></div>
              <div className="p-3 bg-purple-50 rounded"><div className="text-sm text-gray-600">NPV</div><div className="text-lg font-semibold">{cost.financial_metrics.net_present_value_usd.toFixed(0)}</div></div>
              <div className="p-3 bg-yellow-50 rounded"><div className="text-sm text-gray-600">ROI</div><div className="text-lg font-semibold">{(cost.financial_metrics.return_on_investment * 100).toFixed(1)}%</div></div>
              <div className="p-3 bg-indigo-50 rounded"><div className="text-sm text-gray-600">LCOE</div><div className="text-lg font-semibold">${'{'}(cost.financial_metrics.levelized_cost_of_energy_usd_mwh || 0).toFixed(2){'}'}/MWh</div></div>
              <div className="p-3 bg-rose-50 rounded"><div className="text-sm text-gray-600">Payback</div><div className="text-lg font-semibold">{cost.financial_metrics.payback_period_years ? cost.financial_metrics.payback_period_years.toFixed(1) : 'N/A'} yrs</div></div>
            </div>
          ) : (
            <div className="text-gray-500">Run to see costs.</div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center"><FileText className="h-5 w-5 mr-2"/>Report</h2>
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm text-gray-600">Auto-generated project report</div>
            <button onClick={download} disabled={!report} className="flex items-center bg-gray-800 text-white px-3 py-2 rounded-md disabled:opacity-50"><Download className="h-4 w-4 mr-1"/>Download</button>
          </div>
          <pre className="whitespace-pre-wrap text-sm text-gray-800 bg-gray-50 p-4 rounded min-h-[120px]">{report || 'Run to generate report.'}</pre>
        </div>
      </div>
    </div>
  )
}


