import React, { useState, useEffect } from 'react'
import { MapPin, Zap, Sun, Wind, Battery, Search, Map, BarChart3, TrendingUp, Calendar, Gauge, DollarSign, FileText, Download } from 'lucide-react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import { apiEndpoints } from '../services/api'
import toast from 'react-hot-toast'
import 'leaflet/dist/leaflet.css'

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

interface ResourceEstimationResult {
  resource_type: string
  annual_generation_gwh: number
  capacity_factor: number
  peak_power_mw: number
  seasonal_variation: {
    summer: number
    winter: number
    spring: number
    fall: number
  }
  uncertainty_range: [number, number]
  confidence_level: number
  data_quality_score: number
}

interface CitySuggestion {
  name: string
  country: string
  lat: number
  lon: number
  state?: string
}

interface SystemConfig {
  panel_efficiency: number
  wind_turbine_rating: number
  system_losses: number
  availability_factor: number
  tilt_angle?: number
  inverter_efficiency?: number
  turbine_hub_height?: number
}

export function ResourceEstimation() {
  const [formData, setFormData] = useState({
    latitude: '',
    longitude: '',
    area_km2: '100',
    resource_type: 'solar'
  })
  const [systemConfig, setSystemConfig] = useState<SystemConfig>({
    panel_efficiency: 20,
    wind_turbine_rating: 3.0,
    system_losses: 15,
    availability_factor: 95,
    tilt_angle: 25,
    inverter_efficiency: 96,
    turbine_hub_height: 100
  })
  const [citySearch, setCitySearch] = useState('')
  const [citySuggestions, setCitySuggestions] = useState<CitySuggestion[]>([])
  const [selectedCity, setSelectedCity] = useState<CitySuggestion | null>(null)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [result, setResult] = useState<ResourceEstimationResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSearchingCity, setIsSearchingCity] = useState(false)
  const [costResult, setCostResult] = useState<any>(null)
  const [reportText, setReportText] = useState<string>("")

  // Geocoding function using OpenStreetMap Nominatim API
  const searchCities = async (query: string) => {
    if (query.length < 3) {
      setCitySuggestions([])
      return
    }

    setIsSearchingCity(true)
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=1`
      )
      const data = await response.json()
      
      const suggestions: CitySuggestion[] = data.map((item: any) => ({
        name: item.display_name.split(',')[0],
        country: item.address?.country || '',
        state: item.address?.state || '',
        lat: parseFloat(item.lat),
        lon: parseFloat(item.lon)
      }))
      
      setCitySuggestions(suggestions)
    } catch (error) {
      console.error('Error searching cities:', error)
      toast.error('Failed to search cities')
    } finally {
      setIsSearchingCity(false)
    }
  }

  // Handle city search input
  const handleCitySearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setCitySearch(value)
    searchCities(value)
    setShowSuggestions(true)
  }

  // Handle city selection
  const selectCity = async (city: CitySuggestion) => {
    setSelectedCity(city)
    setCitySearch(`${city.name}, ${city.state || city.country}`)
    setFormData({
      ...formData,
      latitude: city.lat.toString(),
      longitude: city.lon.toString()
    })
    setShowSuggestions(false)
    setCitySuggestions([])
    toast.success(`Selected ${city.name}`)

    // Auto-run: resource estimation -> cost evaluation -> report generation
    try {
      setIsLoading(true)
      // 1) Resource estimation using current resource_type and defaults
      const estimationResp = await apiEndpoints.estimateResources({
        location: { latitude: city.lat, longitude: city.lon, area_km2: parseFloat(formData.area_km2) || 100 },
        resource_type: formData.resource_type,
        system_config: systemConfig
      })
      const estimation = estimationResp.data.estimation
      setResult(estimation)

      // 2) Cost evaluation using estimation outputs
      const project_type = formData.resource_type
      const capacity_mw = estimation.peak_power_mw || 100
      const annual_generation_gwh = estimation.annual_generation_gwh || 200
      const costResp = await apiEndpoints.evaluateCosts({
        project_data: { project_type, capacity_mw, annual_generation_gwh },
        financial_params: { electricity_price_usd_mwh: 50, project_lifetime: 25, discount_rate: 0.08 }
      })
      setCostResult(costResp.data.evaluation)

      // 3) Report generation
      const reportResp = await apiEndpoints.generateReport({
        project_data: { project_type, capacity_mw, location: { latitude: city.lat, longitude: city.lon } }
      })
      setReportText(reportResp.data.report)
    } catch (err) {
      toast.error('Auto-generation failed. Try manual estimate.')
    } finally {
      setIsLoading(false)
    }
  }

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await apiEndpoints.estimateResources({
        location: {
          latitude: parseFloat(formData.latitude),
          longitude: parseFloat(formData.longitude),
          area_km2: parseFloat(formData.area_km2)
        },
        resource_type: formData.resource_type,
        system_config: systemConfig
      })

      setResult(response.data.estimation)
      toast.success('Resource estimation completed!')
    } catch (error) {
      toast.error('Estimation failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSystemConfigChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSystemConfig({
      ...systemConfig,
      [e.target.name]: parseFloat(e.target.value)
    })
  }

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setShowSuggestions(false)
    }
    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [])

  // Prepare chart data
  const seasonalData = result ? [
    { name: 'Spring', value: result.seasonal_variation.spring, generation: result.annual_generation_gwh * result.seasonal_variation.spring / 4 },
    { name: 'Summer', value: result.seasonal_variation.summer, generation: result.annual_generation_gwh * result.seasonal_variation.summer / 4 },
    { name: 'Fall', value: result.seasonal_variation.fall, generation: result.annual_generation_gwh * result.seasonal_variation.fall / 4 },
    { name: 'Winter', value: result.seasonal_variation.winter, generation: result.annual_generation_gwh * result.seasonal_variation.winter / 4 }
  ] : []

  const pieData = result ? [
    { name: 'Generation', value: result.annual_generation_gwh, color: '#10B981' },
    { name: 'Uncertainty', value: (result.uncertainty_range[1] - result.uncertainty_range[0]) / 2, color: '#F59E0B' }
  ] : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Resource Estimation</h1>
        <p className="text-gray-600">Estimate renewable energy resources for specific locations</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <div className="space-y-6">
          {/* Location Form */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Location Parameters</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* City Search */}
              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Search City
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="Search for a city..."
                    value={citySearch}
                    onChange={handleCitySearch}
                  />
                  {isSearchingCity && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-600"></div>
                    </div>
                  )}
                </div>
                
                {/* City Suggestions Dropdown */}
                {showSuggestions && citySuggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                    {citySuggestions.map((city, index) => (
                      <div
                        key={index}
                        className="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0"
                        onClick={() => selectCity(city)}
                      >
                        <div className="font-medium text-gray-900">{city.name}</div>
                        <div className="text-sm text-gray-500">
                          {city.state && `${city.state}, `}{city.country}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Latitude
                  </label>
                  <input
                    type="number"
                    name="latitude"
                    step="any"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="40.7128"
                    value={formData.latitude}
                    onChange={handleInputChange}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Longitude
                  </label>
                  <input
                    type="number"
                    name="longitude"
                    step="any"
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="-74.0060"
                    value={formData.longitude}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Area (km²)
                </label>
                <input
                  type="number"
                  name="area_km2"
                  step="any"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={formData.area_km2}
                  onChange={handleInputChange}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Resource Type
                </label>
                <select
                  name="resource_type"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={formData.resource_type}
                  onChange={handleInputChange}
                >
                  <option value="solar">Solar</option>
                  <option value="wind">Wind</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
              >
                {isLoading ? 'Estimating...' : 'Estimate Resources'}
              </button>
            </form>
          </div>

          {/* System Configuration */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">System Configuration</h2>
            <div className="space-y-4">
              {formData.resource_type === 'solar' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Panel Efficiency (%)
                  </label>
                  <input
                    type="number"
                    name="panel_efficiency"
                    min="0"
                    max="100"
                    step="0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    value={systemConfig.panel_efficiency}
                    onChange={handleSystemConfigChange}
                  />
                  <div className="mt-4 grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Tilt Angle (deg)</label>
                      <input type="number" name="tilt_angle" step="1" value={systemConfig.tilt_angle || 0} onChange={handleSystemConfigChange} className="w-full px-3 py-2 border border-gray-300 rounded-md" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Inverter Efficiency (%)</label>
                      <input type="number" name="inverter_efficiency" step="0.1" value={systemConfig.inverter_efficiency || 0} onChange={handleSystemConfigChange} className="w-full px-3 py-2 border border-gray-300 rounded-md" />
                    </div>
                  </div>
                </div>
              )}
              
              {formData.resource_type === 'wind' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Wind Turbine Rating (MW)
                  </label>
                  <input
                    type="number"
                    name="wind_turbine_rating"
                    min="0"
                    step="0.1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    value={systemConfig.wind_turbine_rating}
                    onChange={handleSystemConfigChange}
                  />
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Hub Height (m)</label>
                    <input type="number" name="turbine_hub_height" step="1" value={systemConfig.turbine_hub_height || 0} onChange={handleSystemConfigChange} className="w-full px-3 py-2 border border-gray-300 rounded-md" />
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  System Losses (%)
                </label>
                <input
                  type="number"
                  name="system_losses"
                  min="0"
                  max="100"
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={systemConfig.system_losses}
                  onChange={handleSystemConfigChange}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Availability Factor (%)
                </label>
                <input
                  type="number"
                  name="availability_factor"
                  min="0"
                  max="100"
                  step="0.1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={systemConfig.availability_factor}
                  onChange={handleSystemConfigChange}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Map and Results */}
        <div className="space-y-6">
          {/* Map */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <Map className="h-5 w-5 mr-2" />
              Location Map
            </h2>
            {formData.latitude && formData.longitude ? (
              <div className="h-64 rounded-lg overflow-hidden">
                <MapContainer
                  center={[parseFloat(formData.latitude), parseFloat(formData.longitude)]}
                  zoom={10}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />
                  <Marker position={[parseFloat(formData.latitude), parseFloat(formData.longitude)]}>
                    <Popup>
                      <div className="text-center">
                        <div className="font-semibold">Resource Estimation Site</div>
                        <div className="text-sm text-gray-600">
                          {selectedCity ? `${selectedCity.name}` : 'Custom Location'}
                        </div>
                        <div className="text-xs text-gray-500">
                          {formData.latitude}, {formData.longitude}
                        </div>
                        <div className="text-xs text-green-600 font-medium">
                          {formData.resource_type.toUpperCase()} RESOURCE
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                </MapContainer>
              </div>
            ) : (
              <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <MapPin className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>Enter coordinates or search for a city to view the map</p>
                </div>
              </div>
            )}
          </div>

          {/* Results */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Estimation Results</h2>
            
            {result ? (
              <div className="space-y-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-green-50 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-green-800">Annual Generation</h3>
                        <p className="text-sm text-green-600">GWh per year</p>
                      </div>
                      <div className="text-2xl font-bold text-green-600">
                        {result.annual_generation_gwh.toFixed(1)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-blue-800">Peak Power</h3>
                        <p className="text-sm text-blue-600">MW capacity</p>
                      </div>
                      <div className="text-2xl font-bold text-blue-600">
                        {result.peak_power_mw.toFixed(1)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Performance Metrics */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <Gauge className="h-6 w-6 text-purple-600 mx-auto mb-1" />
                    <div className="text-sm text-gray-600">Capacity Factor</div>
                    <div className="font-semibold text-purple-600">
                      {(result.capacity_factor * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="text-center p-3 bg-yellow-50 rounded-lg">
                    <BarChart3 className="h-6 w-6 text-yellow-600 mx-auto mb-1" />
                    <div className="text-sm text-gray-600">Confidence</div>
                    <div className="font-semibold text-yellow-600">
                      {(result.confidence_level * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="text-center p-3 bg-indigo-50 rounded-lg">
                    <TrendingUp className="h-6 w-6 text-indigo-600 mx-auto mb-1" />
                    <div className="text-sm text-gray-600">Data Quality</div>
                    <div className="font-semibold text-indigo-600">
                      {(result.data_quality_score * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                {/* Seasonal Variation Chart */}
                <div>
                  <h3 className="font-medium mb-3 flex items-center">
                    <Calendar className="h-4 w-4 mr-2" />
                    Seasonal Generation Variation
                  </h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={seasonalData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip formatter={(value) => [`${value.toFixed(1)} GWh`, 'Generation']} />
                        <Bar dataKey="generation" fill="#10B981" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Uncertainty Range */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium mb-2">Uncertainty Range</h3>
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      Low: {result.uncertainty_range[0].toFixed(1)} GWh
                    </div>
                    <div className="text-sm text-gray-600">
                      High: {result.uncertainty_range[1].toFixed(1)} GWh
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{ 
                        width: `${((result.annual_generation_gwh - result.uncertainty_range[0]) / (result.uncertainty_range[1] - result.uncertainty_range[0])) * 100}%`,
                        marginLeft: `${((result.uncertainty_range[0] - result.uncertainty_range[0]) / (result.uncertainty_range[1] - result.uncertainty_range[0])) * 100}%`
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <Zap className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Enter location details to estimate renewable energy resources</p>
              </div>
            )}
          </div>

          {/* Cost Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center"><DollarSign className="h-5 w-5 mr-2"/>Cost Summary</h2>
            {costResult ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-green-50 rounded">
                  <div className="text-sm text-gray-600">Total CAPEX</div>
                  <div className="text-xl font-semibold">{costResult.total_capex_usd.toLocaleString()}</div>
                </div>
                <div className="p-4 bg-blue-50 rounded">
                  <div className="text-sm text-gray-600">Annual OPEX</div>
                  <div className="text-xl font-semibold">{costResult.annual_opex_usd.toLocaleString()}</div>
                </div>
                <div className="p-4 bg-purple-50 rounded">
                  <div className="text-sm text-gray-600">NPV</div>
                  <div className="text-xl font-semibold">{costResult.financial_metrics.net_present_value_usd.toFixed(0)}</div>
                </div>
                <div className="p-4 bg-yellow-50 rounded">
                  <div className="text-sm text-gray-600">ROI</div>
                  <div className="text-xl font-semibold">{(costResult.financial_metrics.return_on_investment * 100).toFixed(1)}%</div>
                </div>
                <div className="p-4 bg-indigo-50 rounded">
                  <div className="text-sm text-gray-600">LCOE</div>
                  <div className="text-xl font-semibold">${'{'}(costResult.financial_metrics.levelized_cost_of_energy_usd_mwh || 0).toFixed(2){'}'}/MWh</div>
                </div>
                <div className="p-4 bg-rose-50 rounded">
                  <div className="text-sm text-gray-600">Payback</div>
                  <div className="text-xl font-semibold">{costResult.financial_metrics.payback_period_years ? costResult.financial_metrics.payback_period_years.toFixed(1) : 'N/A'} yrs</div>
                </div>
              </div>
            ) : (
              <div className="text-gray-500">Select a city to auto-generate costs.</div>
            )}
          </div>

          {/* Report Preview */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center"><FileText className="h-5 w-5 mr-2"/>Report</h2>
            <div className="flex items-center justify-between mb-3">
              <div className="text-sm text-gray-600">Auto-generated project report</div>
              <button
                onClick={() => {
                  if (!reportText) return
                  const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = 'geospark_report.txt'
                  a.click()
                  URL.revokeObjectURL(url)
                }}
                disabled={!reportText}
                className="flex items-center bg-gray-800 text-white px-3 py-2 rounded-md disabled:opacity-50"
              >
                <Download className="h-4 w-4 mr-1"/>Download
              </button>
            </div>
            <pre className="whitespace-pre-wrap text-sm text-gray-800 bg-gray-50 p-4 rounded min-h-[120px]">{reportText || 'Select a city to generate a report.'}</pre>
          </div>
        </div>
      </div>
    </div>
  )
}

export function CostEvaluation() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Cost Evaluation</h1>
        <p className="text-gray-600">Evaluate project costs and financial viability</p>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="h-16 w-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Cost Evaluation</h3>
          <p className="text-gray-600 mb-4">This feature will be available in the next update</p>
          <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
            Coming Soon
          </button>
        </div>
      </div>
    </div>
  )
}

export function Reports() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600">View and download analysis reports</p>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="h-16 w-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Reports</h3>
          <p className="text-gray-600 mb-4">This feature will be available in the next update</p>
          <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
            Coming Soon
          </button>
        </div>
      </div>
    </div>
  )
}