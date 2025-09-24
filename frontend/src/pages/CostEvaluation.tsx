import React, { useState } from 'react'
import { apiEndpoints } from '../services/api'
import toast from 'react-hot-toast'
import { DollarSign, TrendingUp } from 'lucide-react'

export function CostEvaluation() {
  const [form, setForm] = useState({
    project_type: 'solar',
    capacity_mw: 100,
    annual_generation_gwh: 200,
  })
  const [financial, setFinancial] = useState({
    electricity_price_usd_mwh: 50,
    project_lifetime: 25,
    discount_rate: 0.08,
  })
  const [result, setResult] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)

  const onChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: name.includes('capacity') || name.includes('annual') ? parseFloat(value) : value }))
  }
  const onChangeFin = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFinancial(prev => ({ ...prev, [name]: name === 'project_lifetime' ? parseInt(value) : parseFloat(value) }))
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      const resp = await apiEndpoints.evaluateCosts({
        project_data: form,
        financial_params: financial,
      })
      setResult(resp.data.evaluation)
      toast.success('Cost evaluation complete')
    } catch (err) {
      toast.error('Failed to evaluate costs')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Cost Evaluation</h1>
        <p className="text-gray-600">Evaluate project costs and financial viability</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center"><DollarSign className="h-5 w-5 mr-2"/>Inputs</h2>
          <form className="space-y-4" onSubmit={submit}>
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
                <label className="block text-sm font-medium text-gray-700 mb-1">Annual Generation (GWh)</label>
                <input type="number" name="annual_generation_gwh" value={form.annual_generation_gwh} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Price (USD/MWh)</label>
                <input type="number" name="electricity_price_usd_mwh" value={financial.electricity_price_usd_mwh} onChange={onChangeFin} className="w-full px-3 py-2 border rounded-md" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Lifetime (years)</label>
                <input type="number" name="project_lifetime" value={financial.project_lifetime} onChange={onChangeFin} className="w-full px-3 py-2 border rounded-md" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Discount rate</label>
                <input type="number" step="0.01" name="discount_rate" value={financial.discount_rate} onChange={onChangeFin} className="w-full px-3 py-2 border rounded-md" />
              </div>
            </div>
            <button type="submit" disabled={isLoading} className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-700 disabled:opacity-50">{isLoading ? 'Evaluating...' : 'Evaluate Costs'}</button>
          </form>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center"><TrendingUp className="h-5 w-5 mr-2"/>Results</h2>
          {result ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-green-50 rounded">
                  <div className="text-sm text-gray-600">Total CAPEX</div>
                  <div className="text-lg font-semibold">{result.total_capex_usd.toLocaleString()}</div>
                </div>
                <div className="p-3 bg-blue-50 rounded">
                  <div className="text-sm text-gray-600">Annual OPEX</div>
                  <div className="text-lg font-semibold">{result.annual_opex_usd.toLocaleString()}</div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-3 bg-purple-50 rounded">
                  <div className="text-sm text-gray-600">NPV</div>
                  <div className="text-lg font-semibold">{result.financial_metrics.net_present_value_usd.toFixed(0)}</div>
                </div>
                <div className="p-3 bg-yellow-50 rounded">
                  <div className="text-sm text-gray-600">IRR</div>
                  <div className="text-lg font-semibold">{(result.financial_metrics.internal_rate_of_return * 100).toFixed(1)}%</div>
                </div>
                <div className="p-3 bg-indigo-50 rounded">
                  <div className="text-sm text-gray-600">Payback</div>
                  <div className="text-lg font-semibold">{result.financial_metrics.payback_period_years ? result.financial_metrics.payback_period_years.toFixed(1) + ' yrs' : 'N/A'}</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500">Fill inputs and evaluate to see results.</div>
          )}
        </div>
      </div>
    </div>
  )
}