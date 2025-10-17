import React, { useState, useEffect } from 'react'
import { MapPin, Zap, DollarSign, BarChart3, TrendingUp, AlertTriangle, Search, Map } from 'lucide-react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
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

interface SiteAnalysisResult {
  site_id: string
  location: {
    latitude: number
    longitude: number
    area_km2: number
  }
  overall_score: number
  solar_potential: {
    annual_irradiance_kwh_m2: number
    peak_sun_hours: number
    capacity_factor: number
    solar_score: number
  }
  wind_potential: {
    average_wind_speed_ms: number
    capacity_factor: number
    wind_score: number
  }
  environmental_score: number
  regulatory_score: number
  accessibility_score: number
  recommendations: string[]
  risks: string[]
  estimated_capacity_mw: number
  // Protected area flags
  protected_overlap?: boolean
  protected_nearby_km?: number | null
  protected_features?: Array<{
    id?: number
    type?: string
    name?: string
    distance_km?: number | null
    tags?: Record<string, string>
  }>
  suitability?: 'suitable' | 'caution' | 'unsuitable'
}

interface CitySuggestion {
  name: string
  country: string
  lat: number
  lon: number
  state?: string
}

export function SiteAnalysis() {
  const [formData, setFormData] = useState({
    latitude: '',
    longitude: '',
    area_km2: '100',
    project_type: 'solar'
  })
  const [citySearch, setCitySearch] = useState('')
  const [citySuggestions, setCitySuggestions] = useState<CitySuggestion[]>([])
  const [selectedCity, setSelectedCity] = useState<CitySuggestion | null>(null)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [result, setResult] = useState<SiteAnalysisResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isSearchingCity, setIsSearchingCity] = useState(false)
  const [showProtectedDisclaimer, setShowProtectedDisclaimer] = useState(false)

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
  const selectCity = (city: CitySuggestion) => {
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
  }

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const lat = parseFloat(formData.latitude)
      const lon = parseFloat(formData.longitude)
      const area = parseFloat(formData.area_km2)

      if (
        Number.isNaN(lat) || Number.isNaN(lon) || Number.isNaN(area) ||
        lat < -90 || lat > 90 || lon < -180 || lon > 180 || area <= 0
      ) {
        setIsLoading(false)
        toast.error('Please enter valid latitude, longitude, and area values.')
        return
      }

      const response = await apiEndpoints.analyzeSite({
        location: { latitude: lat, longitude: lon, area_km2: area },
        project_type: formData.project_type,
        analysis_depth: 'comprehensive'
      })

      if (response.data?.success && response.data?.analysis) {
        setResult(response.data.analysis)
        toast.success('Site analysis completed!')
      } else {
        throw new Error(response.data?.message || 'Analysis failed')
      }
    } catch (error: any) {
      const serverMsg = error?.response?.data?.detail || error?.response?.data?.message || error?.message
      toast.error(`Analysis failed: ${serverMsg || 'Please try again.'}`)
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

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setShowSuggestions(false)
    }
    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [])

  // Open eye-catching disclaimer modal when protected land detected
  useEffect(() => {
    if (result?.protected_overlap) {
      setShowProtectedDisclaimer(true)
    }
  }, [result?.protected_overlap])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Site Analysis</h1>
        <p className="text-gray-600">Analyze renewable energy potential for specific locations</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Analysis Parameters</h2>
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
                Project Type
              </label>
              <select
                name="project_type"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                value={formData.project_type}
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
              {isLoading ? 'Analyzing...' : 'Analyze Site'}
            </button>
          </form>
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
                        <div className="font-semibold">Analysis Site</div>
                        <div className="text-sm text-gray-600">
                          {selectedCity ? `${selectedCity.name}` : 'Custom Location'}
                        </div>
                        <div className="text-xs text-gray-500">
                          {formData.latitude}, {formData.longitude}
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
            <h2 className="text-lg font-semibold mb-4">Analysis Results</h2>
          
          {result ? (
            <div className="space-y-4">
              {/* Suitability Badge */}
              {result.suitability && (
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">Site Suitability</div>
                  <span
                    className={
                      result.suitability === 'unsuitable'
                        ? 'px-2 py-1 rounded text-xs font-semibold bg-red-100 text-red-700'
                        : result.suitability === 'caution'
                        ? 'px-2 py-1 rounded text-xs font-semibold bg-yellow-100 text-yellow-700'
                        : 'px-2 py-1 rounded text-xs font-semibold bg-green-100 text-green-700'
                    }
                  >
                    {result.suitability.charAt(0).toUpperCase() + result.suitability.slice(1)}
                  </span>
                </div>
              )}
              {/* Protected Area Warning */}
              {result.protected_overlap && (
                <div className="rounded-md bg-red-50 border border-red-200 p-4">
                  <div className="flex">
                    <AlertTriangle className="h-5 w-5 text-red-600 mr-2 mt-0.5" />
                    <div>
                      <div className="font-semibold text-red-800">Protected Area Detected Nearby</div>
                      <div className="text-sm text-red-700">
                        This location overlaps or is within {result.protected_nearby_km?.toFixed(2) ?? 'N/A'} km of a protected area.
                        Development may be restricted and require special permits.
                      </div>
                      {result.protected_features && result.protected_features.length > 0 && (
                        <div className="mt-2">
                          <div className="text-xs font-medium text-red-800 mb-1">Nearby protected features:</div>
                          <ul className="text-xs text-red-700 list-disc pl-5 space-y-0.5">
                            {result.protected_features.slice(0, 5).map((f, idx) => (
                              <li key={idx}>
                                {f.name || 'Protected Area'}{typeof f.distance_km === 'number' ? ` (${f.distance_km.toFixed(2)} km)` : ''}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Eye-catching Disclaimer Modal */}
              {showProtectedDisclaimer && result.protected_overlap && (
                <div className="fixed inset-0 z-50 flex items-center justify-center">
                  {/* Backdrop */}
                  <div className="absolute inset-0 bg-black bg-opacity-50" onClick={() => setShowProtectedDisclaimer(false)}></div>
                  {/* Modal */}
                  <div className="relative z-10 max-w-xl w-11/12 rounded-lg overflow-hidden shadow-2xl">
                    <div className="bg-gradient-to-r from-red-600 to-red-500 text-white p-4 flex items-center">
                      <AlertTriangle className="h-6 w-6 mr-2" />
                      <div className="text-lg font-semibold">Protected Land Entered</div>
                    </div>
                    <div className="bg-white p-5">
                      <p className="text-sm text-gray-800 mb-3">
                        This location intersects or is within close proximity to a protected or conservation area.
                        Project development here is generally unsuitable and may violate environmental regulations.
                      </p>
                      <ul className="text-sm text-gray-700 list-disc pl-5 space-y-1 mb-3">
                        <li>
                          Nearest protected feature: {result.protected_features && result.protected_features[0]?.name ? result.protected_features[0]?.name : 'Protected Area'}
                          {typeof result.protected_nearby_km === 'number' ? ` (~${result.protected_nearby_km.toFixed(2)} km)` : ''}
                        </li>
                        <li>Permitting is likely restricted or not allowed.</li>
                        <li>Consider alternative sites outside protected boundaries.</li>
                      </ul>
                      <div className="text-xs text-gray-500">
                        Data source: OpenStreetMap/Overpass. Screening only. Verify with official datasets and EIA.
                      </div>
                      <div className="mt-4 flex items-center justify-end space-x-2">
                        <button
                          type="button"
                          className="px-3 py-2 text-sm rounded-md border border-gray-300 text-gray-700 bg-white hover:bg-gray-50"
                          onClick={() => setShowProtectedDisclaimer(false)}
                        >
                          Dismiss
                        </button>
                        <button
                          type="button"
                          className="px-3 py-2 text-sm rounded-md bg-red-600 text-white hover:bg-red-700"
                          onClick={() => setShowProtectedDisclaimer(false)}
                        >
                          Choose Different Location
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Development Restriction Disclaimer */}
              {result.protected_overlap && (
                <div className="rounded-md border border-red-300 bg-white p-4">
                  <div className="text-red-700 font-semibold mb-1">Disclaimer: Location Unsuitable for Development</div>
                  <p className="text-sm text-red-700 mb-2">
                    Based on detected conservation and protected-area boundaries, this site should not be used for project
                    development. Proceeding may violate environmental regulations and result in legal, permitting, or
                    compliance issues.
                  </p>
                  <div className="text-sm text-red-800 font-medium mb-1">Why this site is unsuitable:</div>
                  <ul className="text-sm text-red-700 list-disc pl-5 space-y-1">
                    <li>Overlaps or lies within proximity of a protected area (≈ {result.protected_nearby_km?.toFixed(2) ?? 'N/A'} km).</li>
                    {result.protected_features && result.protected_features.slice(0, 3).map((f, idx) => (
                      <li key={idx}>
                        {f.name || 'Protected Area'}{typeof f.distance_km === 'number' ? ` at ~${f.distance_km.toFixed(2)} km` : ''}
                      </li>
                    ))}
                    <li>Activities are typically restricted; special permits and mitigation would be required.</li>
                  </ul>
                  <div className="text-xs text-gray-600 mt-3">
                    Note: This screening uses public OpenStreetMap data via Overpass and is indicative only. Always verify
                    boundaries with official datasets and conduct a full Environmental Impact Assessment (EIA).
                  </div>
                </div>
              )}
              {/* Overall Score */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium">Overall Score</h3>
                  <span className="text-2xl font-bold text-green-600">
                    {(result.overall_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${result.overall_score * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Scores Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <MapPin className="h-6 w-6 text-blue-600 mx-auto mb-1" />
                  <div className="text-sm text-gray-600">Solar Score</div>
                  <div className="font-semibold text-blue-600">
                    {(result.solar_potential.solar_score * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <Zap className="h-6 w-6 text-purple-600 mx-auto mb-1" />
                  <div className="text-sm text-gray-600">Wind Score</div>
                  <div className="font-semibold text-purple-600">
                    {(result.wind_potential.wind_score * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <BarChart3 className="h-6 w-6 text-green-600 mx-auto mb-1" />
                  <div className="text-sm text-gray-600">Environmental</div>
                  <div className="font-semibold text-green-600">
                    {(result.environmental_score * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="text-center p-3 bg-yellow-50 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-yellow-600 mx-auto mb-1" />
                  <div className="text-sm text-gray-600">Regulatory</div>
                  <div className="font-semibold text-yellow-600">
                    {(result.regulatory_score * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Capacity Estimate */}
              <div className="bg-green-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-green-800">Estimated Capacity</h3>
                    <p className="text-sm text-green-600">Based on site analysis</p>
                  </div>
                  <div className="text-2xl font-bold text-green-600">
                    {result.estimated_capacity_mw.toFixed(1)} MW
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              {result.recommendations.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Recommendations</h3>
                  <ul className="space-y-1">
                    {result.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start">
                        <span className="text-green-500 mr-2">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Risks */}
              {result.risks.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2 flex items-center">
                    <AlertTriangle className="h-4 w-4 text-red-500 mr-1" />
                    Risks
                  </h3>
                  <ul className="space-y-1">
                    {[...result.risks, ...(result.protected_overlap ? [
                      'Proximity to protected land may restrict development and extend permitting timelines.'
                    ] : [])].map((risk, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-start">
                        <span className="text-red-500 mr-2">•</span>
                        {risk}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              <MapPin className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>Enter location details to analyze renewable energy potential</p>
            </div>
          )}
          </div>
        </div>
      </div>
    </div>
  )
}