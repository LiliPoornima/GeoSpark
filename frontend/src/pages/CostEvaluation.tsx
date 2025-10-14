import React, { useState } from 'react'
import { apiEndpoints } from '../services/api'
import toast from 'react-hot-toast'

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
    if (name in form) setForm({ ...form, [name]: name === 'project_type' ? value : parseFloat(value) })
    else setFinancial({ ...financial, [name]: parseFloat(value) })
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      const resp = await apiEndpoints.evaluateCosts({
        project_data: form,
        financial_params: financial,
      })
      setResult(resp.data.evaluation)
      toast.success('Cost evaluation completed')
    } catch (err) {
      toast.error('Cost evaluation failed')
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
        {/* Input Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Inputs</h2>
          <form className="space-y-4" onSubmit={onSubmit}>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Project Type</label>
              <select name="project_type" value={form.project_type} onChange={onChange} className="w-full px-3 py-2 border rounded-md">
                <option value="solar">Solar</option>
                <option value="wind">Wind</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Capacity (MW)</label>
              <input name="capacity_mw" type="number" value={form.capacity_mw} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Annual Generation (GWh)</label>
              <input name="annual_generation_gwh" type="number" value={form.annual_generation_gwh} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Price ($/MWh)</label>
                <input name="electricity_price_usd_mwh" type="number" value={financial.electricity_price_usd_mwh} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Lifetime (years)</label>
                <input name="project_lifetime" type="number" value={financial.project_lifetime} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Discount Rate</label>
                <input name="discount_rate" type="number" step="0.01" value={financial.discount_rate} onChange={onChange} className="w-full px-3 py-2 border rounded-md" />
              </div>
            </div>
            <button type="submit" disabled={isLoading} className="w-full bg-green-600 text-white py-2 px-4 rounded-md disabled:opacity-50">
              {isLoading ? 'Evaluating...' : 'Evaluate Costs'}
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Results</h2>
          {!result ? (
            <div className="text-gray-500">Fill the form and evaluate to see results.</div>
          ) : (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-600">Total CAPEX (Capital Expenditure)</div>
                  <div className="font-semibold">${result.total_capex_usd.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Annual OPEX (Operational Expenditure)</div>
                  <div className="font-semibold">${result.annual_opex_usd.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Annual Revenue</div>
                  <div className="font-semibold">${result.annual_revenue_usd.toLocaleString()}</div>
                </div>
                
                <div className="mt-2">
                <div className="text-sm text-gray-600">NPV <br></br>(Net Present Value)</div>
                <div className="font-semibold">${result.financial_metrics.net_present_value_usd.toLocaleString()}</div>
              </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-gray-600">IRR <br></br>(Internal Rate of Return)</div>
                  <div className="font-semibold">{(result.financial_metrics.internal_rate_of_return * 100).toFixed(2)}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">Payback (yrs)</div>
                  <div className="font-semibold">{result.financial_metrics.payback_period_years?.toFixed(1)}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">LCOE <br></br>(Levelized Cost Of Energy) ($/MWh)</div>
                  <div className="font-semibold">{result.financial_metrics.levelized_cost_of_energy_usd_mwh?.toFixed(2)}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
