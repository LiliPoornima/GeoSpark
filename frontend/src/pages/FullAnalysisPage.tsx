import React, { useState, useEffect } from "react";
import {
  MapPin,
  Zap,
  Sun,
  Wind,
  DollarSign,
  FileText,
  AlertTriangle, 
  Search,
  Map as MapIcon,
} from "lucide-react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import toast from "react-hot-toast";
import { apiEndpoints } from "../services/api";
import { Reports } from './Reports'

// Leaflet default marker fix
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'

//import { AlertTriangle } from "lucide-react";
import { checkProtectedArea } from "../services/protectedAreas"; // new service
import { ProtectedAreaCheckResult } from '../services/protectedAreas'
import { ProtectedAreaModal } from '../components/ProtectedAreaModal'  // Adjust path as needed

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl,
  iconUrl,
  shadowUrl,
})

type ProjectType = "solar" | "wind" | "hybrid";

interface CitySuggestion {
  name: string;
  country: string;
  lat: number;
  lon: number;
  state?: string;
}

export default function FullAnalysisPage() {
  // Site form states
  const [citySearch, setCitySearch] = useState("");
  const [citySuggestions, setCitySuggestions] = useState<CitySuggestion[]>([]);
  const [selectedCity, setSelectedCity] = useState<CitySuggestion | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const [latitude, setLatitude] = useState<number>(0);
  const [longitude, setLongitude] = useState<number>(0);
  const [areaKm2, setAreaKm2] = useState<number>(0);
  const [projectType, setProjectType] = useState<ProjectType>("solar");

  const [isLoading, setIsLoading] = useState(false);
  const [workflow, setWorkflow] = useState<any | null>(null);
  const [mapType, setMapType] = useState<'street' | 'satellite'>('street');

  const [showProtectedModal, setShowProtectedModal] = useState(false)
  const [protectedResult, setProtectedResult] = useState<ProtectedAreaCheckResult | null>(null)

  // --- Helper Functions ---
  // Removed hardcoded calculations: gwhToWh, gwhToAverageWatts, formatLarge, estimateResources
  // These are now provided by the backend API in the workflow response
  
  const formatLarge = (n: number) => {
    if (!isFinite(n)) return "N/A";
    if (Math.abs(n) >= 1e12) return `${(n / 1e12).toFixed(2)}T`;
    if (Math.abs(n) >= 1e9) return `${(n / 1e9).toFixed(2)}B`;
    if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
    if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(2)}k`;
    return n.toFixed(0);
  };

  const buildSeasonalData = (est: any) => {
    if (!est) return [];
    const { seasonal_variation = {}, annual_generation_gwh = 0 } = est;
    return [
      {
        name: "Spring",
        factor: seasonal_variation.spring ?? 1,
        generation_gwh: (annual_generation_gwh * (seasonal_variation.spring ?? 1)) / 4,
      },
      {
        name: "Summer",
        factor: seasonal_variation.summer ?? 1,
        generation_gwh: (annual_generation_gwh * (seasonal_variation.summer ?? 1)) / 4,
      },
      {
        name: "Fall",
        factor: seasonal_variation.fall ?? 1,
        generation_gwh: (annual_generation_gwh * (seasonal_variation.fall ?? 1)) / 4,
      },
      {
        name: "Winter",
        factor: seasonal_variation.winter ?? 1,
        generation_gwh: (annual_generation_gwh * (seasonal_variation.winter ?? 1)) / 4,
      },
    ];
  };

  // --- City Search ---
  const searchCities = async (query: string) => {
    if (query.length < 3) {
      setCitySuggestions([]);
      return;
    }
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=1`
      );
      const data = await response.json();
      const suggestions: CitySuggestion[] = data.map((item: any) => ({
        name: item.display_name.split(",")[0],
        country: item.address?.country || "",
        state: item.address?.state || "",
        lat: parseFloat(item.lat),
        lon: parseFloat(item.lon),
      }));
      setCitySuggestions(suggestions);
    } catch (err) {
      console.error(err);
      toast.error("Failed to search cities");
    }
  };

  const handleCitySelect = (city: CitySuggestion) => {
    setSelectedCity(city);
    setCitySearch(`${city.name}, ${city.state || city.country}`);
    setLatitude(city.lat);
    setLongitude(city.lon);
    setShowSuggestions(false);
    setCitySuggestions([]);
  };

  useEffect(() => {
    const handleClickOutside = () => setShowSuggestions(false);
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);

  // --- Extracted Analysis Logic ---
  const performAnalysis = async () => {
    const r = await apiEndpoints.fullAnalysis({
      location: { latitude, longitude, area_km2: areaKm2 },
      project_type: projectType,
      analysis_depth: "comprehensive",
      city_name: selectedCity?.name || "",
    });
    const respData: any = r.data;
    const workflowData = respData?.workflow ?? respData;
    if (!workflowData) {
      toast.error("Invalid response from server");
      return;
    }
    setWorkflow(workflowData);
    toast.success("Full analysis completed");
  }

  // --- Full Analysis ---
  const runFullAnalysis = async () => {
    setIsLoading(true)
    setWorkflow(null)
    setShowProtectedModal(false)

    try {
      // Protected check
      if (isFinite(latitude) && isFinite(longitude)) {
        const result = await checkProtectedArea(latitude, longitude)
        if (result.isProtected) {
          setProtectedResult(result)
          setShowProtectedModal(true)
          setIsLoading(false)  // Stop loading until decision
          return
        }
      }

      // If no modal, proceed to analysis
      await performAnalysis()
    } catch (err: any) {
      console.error("Full analysis error:", err)
      toast.error("Full analysis failed. Check console / backend.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleProceedFromModal = async () => {
    setShowProtectedModal(false)
    setIsLoading(true)
    // Re-run the analysis part
    await performAnalysis()
  }

  const handleCancelFromModal = () => {
    setShowProtectedModal(false)
    setIsLoading(false)
  }

  const renderRecommendations = (siteAnalysis: any) => {
    if (!siteAnalysis) return null;
    const recs: string[] = siteAnalysis.recommendations || [];
    if (!recs.length) return <div className="text-sm text-gray-600">No recommendations available.</div>;
    return (
      <ul className="space-y-1">
        {recs.map((r, i) => (
          <li key={i} className="text-sm text-gray-700 flex items-start">
            <span className="text-green-500 mr-2">•</span>
            <div>{r}</div>
          </li>
        ))}
      </ul>
    );
  };

  const renderRisks = (siteAnalysis: any) => {
    if (!siteAnalysis) return null;
    const risks: string[] = siteAnalysis.risks || [];
    if (!risks.length) return <div className="text-sm text-gray-600">No risks flagged.</div>;
    return (
      <ul className="space-y-1">
        {risks.map((r, i) => (
          <li key={i} className="text-sm text-gray-700 flex items-start">
            <span className="text-red-500 mr-2">•</span>
            <div>{r}</div>
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Full Renewable Project Analysis</h1>

      {/* Form with City Search */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4 relative">
        <div className="md:col-span-2 relative">
          <label className="block text-sm font-medium text-gray-700">Search City</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={citySearch}
              onChange={(e) => {
                setCitySearch(e.target.value);
                searchCities(e.target.value);
                setShowSuggestions(true);
              }}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Search for a city..."
            />
          </div>

          {showSuggestions && citySuggestions.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
              {citySuggestions.map((city, idx) => (
                <div
                  key={idx}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0"
                  onClick={() => handleCitySelect(city)}
                >
                  <div className="font-medium">{city.name}</div>
                  <div className="text-sm text-gray-500">{city.state && `${city.state}, `}{city.country}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Latitude</label>
          <input 
            type="number" 
            value={latitude || ''} 
            onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)} 
            placeholder="e.g., 7.29"
            className="w-full border rounded p-2" 
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Longitude</label>
          <input 
            type="number" 
            value={longitude || ''} 
            onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)} 
            placeholder="e.g., 80.63"
            className="w-full border rounded p-2" 
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Area (km²)</label>
          <input 
            type="number" 
            value={areaKm2 || ''} 
            onChange={(e) => setAreaKm2(parseFloat(e.target.value) || 0)} 
            placeholder="e.g., 100"
            className="w-full border rounded p-2" 
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Project Type</label>
          <select value={projectType} onChange={(e) => setProjectType(e.target.value as ProjectType)} className="w-full border rounded p-2">
            <option value="solar">Solar</option>
            <option value="wind">Wind</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </div>
      </div>

      {/* Run & Reset Buttons */}
      <div className="flex gap-3 mb-6">
        <button onClick={runFullAnalysis} disabled={isLoading} className="bg-green-600 text-white px-4 py-2 rounded disabled:opacity-50">
          {isLoading ? "Running full analysis..." : "Run Full Analysis"}
        </button>
        <button onClick={() => setWorkflow(null)} className="bg-gray-200 px-4 py-2 rounded">Reset</button>
      </div>

      {/* Results */}
      {workflow ? (
        <div className="space-y-6">
          {/* Map + Site */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow p-4 lg:col-span-1">
              <div className="flex items-center justify-between mb-2">
                <h2 className="font-semibold flex items-center"><MapIcon className="mr-2" /> Selected Site</h2>
                <div className="flex gap-1 text-xs">
                  <button
                    onClick={() => setMapType('street')}
                    className={`px-2 py-1 rounded ${mapType === 'street' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'}`}
                  >
                    Street
                  </button>
                  <button
                    onClick={() => setMapType('satellite')}
                    className={`px-2 py-1 rounded ${mapType === 'satellite' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'}`}
                  >
                    Satellite
                  </button>
                </div>
              </div>
              <div className="h-56 rounded overflow-hidden">
                <MapContainer center={[latitude, longitude]} zoom={10} style={{ height: "100%", width: "100%" }}>
                  <TileLayer 
                    url={mapType === 'satellite' 
                      ? "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                      : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    }
                    attribution={mapType === 'satellite'
                      ? '&copy; <a href="https://www.esri.com/">Esri</a>'
                      : '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    }
                  />
                  <Marker position={[latitude, longitude]}>
                    <Popup>
                      <div className="text-sm">
                        <div className="font-semibold">Selected site</div>
                        <div>{latitude.toFixed(4)}, {longitude.toFixed(4)}</div>
                        <div className="mt-1 text-xs text-gray-600">Resource: {projectType.toUpperCase()}</div>
                      </div>
                    </Popup>
                  </Marker>
                </MapContainer>
              </div>
            </div>

            {/* Site Analysis */}
            <div className="bg-white rounded-lg shadow p-4 lg:col-span-2">
              <h2 className="font-semibold mb-2 flex items-center"><MapPin className="mr-2" /> Site Analysis</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="p-3 bg-gray-50 rounded">
                  <div className="text-sm text-gray-500">Overall Score</div>
                  <div className="text-2xl font-bold text-green-600">{workflow.site_analysis ? ((workflow.site_analysis.overall_score ?? 0) * 100).toFixed(1) : "N/A"}%</div>
                </div>
                <div className="p-3 bg-blue-50 rounded">
                  <div className="text-sm text-blue-700">Estimated Capacity</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {workflow.site_analysis 
                      ? formatLarge((workflow.site_analysis.estimated_capacity_mw ?? 0) * 1e6) 
                      : "N/A"} W
                  </div>
                </div>

                <div className="p-3 bg-gray-50 rounded">
                  <div className="text-sm text-gray-500">Accessibility / Environmental</div>
                  <div className="text-lg font-semibold text-gray-700">{workflow.site_analysis ? `${Math.round((workflow.site_analysis.accessibility_score ?? 0) * 100)}% / ${Math.round((workflow.site_analysis.environmental_score ?? 0) * 100)}%` : "N/A"}</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-3 border rounded">
                  <h3 className="font-medium mb-2">Recommendations</h3>
                  {renderRecommendations(workflow.site_analysis)}
                </div>
                <div className="p-3 border rounded">
                  <h3 className="font-medium mb-2">Risks</h3>
                  {renderRisks(workflow.site_analysis)}
                </div>
              </div>
            </div>
          </div>

          {/* Resource Estimation */}
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="font-semibold mb-3 flex items-center"><Zap className="mr-2" /> Resource Estimation</h2>
            {(() => {
              const est = workflow.resource_estimation;
              if (!est) return <div className="text-sm text-gray-600">No resource estimation returned.</div>;

              const seasonalData = buildSeasonalData(est);
              const annualGwh = Number(est.annual_generation_gwh ?? 0);
              const peakPowerMw = Number(est.peak_power_mw ?? 0);

              return (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="p-3 bg-green-50 rounded">
                      <div className="text-sm text-green-700">Annual Generation</div>
                      <div className="text-2xl font-bold">{annualGwh.toFixed(1)} GWh</div>
                      <div className="text-xs text-gray-600 mt-1">≈ {formatLarge(annualGwh * 1e9)} Wh/year</div>
                      <div className="text-xs text-gray-600">Avg power ≈ {formatLarge(Math.round((annualGwh * 1e9) / 8760))} W</div>
                    </div>
                    <div className="p-3 bg-blue-50 rounded">
                      <div className="text-sm text-blue-700">Peak Power</div>
                      <div className="text-2xl font-bold">{Number(est.peak_power_mw ?? 0).toFixed(1)} MW</div>
                    </div>
                    <div className="p-3 bg-purple-50 rounded">
                      <div className="text-sm text-purple-700">Capacity Factor</div>
                      <div className="text-2xl font-bold">{((est.capacity_factor ?? 0) * 100).toFixed(1)}%</div>
                    </div>
                    <div className="p-3 bg-yellow-50 rounded">
                      <div className="text-sm text-yellow-700">Confidence / Data Quality</div>
                      <div className="text-lg font-semibold">{((est.confidence_level ?? 0) * 100).toFixed(0)}% / {((est.data_quality_score ?? 0) * 100).toFixed(0)}%</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    <div className="col-span-2 p-3 border rounded min-h-[220px]">
                      <h4 className="font-medium mb-2">Seasonal Generation Variation</h4>
                      <div className="h-44">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={seasonalData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip formatter={(value: any) => [`${Number(value).toFixed(2)} GWh`, "Generation"]} />
                            <Bar dataKey="generation_gwh" fill="#10B981" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                    <div className="p-3 border rounded">
                      <h4 className="font-medium mb-2">Uncertainty Range</h4>
                      <div className="text-sm text-gray-600">Low: {(est.uncertainty_range?.[0] ?? 0).toFixed(1)} GWh</div>
                      <div className="text-sm text-gray-600">High: {(est.uncertainty_range?.[1] ?? 0).toFixed(1)} GWh</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {(projectType === "solar" || projectType === "hybrid") && (
                      <div className="p-4 border rounded">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium flex items-center"><Sun className="mr-2" /> Solar Resource</h4>
                        </div>
                        <div className="space-y-2">
                          <div className="text-sm">Peak Power: {peakPowerMw.toFixed(1)} MW</div>
                          <div className="text-sm">Annual Generation: {annualGwh.toFixed(1)} GWh</div>
                          <div className="text-sm">Capacity Factor: {((est.capacity_factor ?? 0) * 100).toFixed(1)}%</div>
                          <div className="text-xs text-gray-500 mt-2">Equipment details available from backend API</div>
                        </div>
                      </div>
                    )}
                    {(projectType === "wind" || projectType === "hybrid") && (
                      <div className="p-4 border rounded">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium flex items-center"><Wind className="mr-2" /> Wind Resource</h4>
                        </div>
                        <div className="space-y-2">
                          <div className="text-sm">Peak Power: {peakPowerMw.toFixed(1)} MW</div>
                          <div className="text-sm">Annual Generation: {annualGwh.toFixed(1)} GWh</div>
                          <div className="text-sm">Capacity Factor: {((est.capacity_factor ?? 0) * 100).toFixed(1)}%</div>
                          <div className="text-xs text-gray-500 mt-2">Equipment details available from backend API</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })()}
          </div>

          {/* Cost Evaluation */}
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="font-semibold mb-3 flex items-center"><DollarSign className="mr-2" /> Cost Evaluation</h2>
            {workflow.cost_evaluation ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-3 border rounded">
                  <div className="text-sm text-gray-500">Total CAPEX</div>
                  <div className="text-lg font-bold">${Number(workflow.cost_evaluation.total_capex_usd ?? 0).toLocaleString()}</div>
                </div>
                <div className="p-3 border rounded">
                  <div className="text-sm text-gray-500">Annual OPEX</div>
                  <div className="text-lg font-bold">${Number(workflow.cost_evaluation.annual_opex_usd ?? 0).toLocaleString()}</div>
                </div>
                <div className="p-3 border rounded">
                  <div className="text-sm text-gray-500">Annual Revenue</div>
                  <div className="text-lg font-bold">${Number(workflow.cost_evaluation.annual_revenue_usd ?? 0).toLocaleString()}</div>
                </div>
                <div className="p-3 border rounded md:col-span-3">
                  <div className="text-sm text-gray-500">NPV</div>
                  <div className="text-lg font-semibold">${Number(workflow.cost_evaluation.financial_metrics?.net_present_value_usd ?? 0).toLocaleString()}</div>
                </div>
              </div>
            ) : <div className="text-sm text-gray-600">No cost evaluation returned.</div>}
          </div>

          {/* Report Section */}
          <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
            <div className="border-b border-gray-200 pb-3">
              <h2 className="font-bold text-xl text-gray-800 flex items-center">
                <FileText className="mr-2 text-green-600" size={24} />
                Project Report Generation
              </h2>
              <p className="text-sm text-gray-600 mt-1">Fill in project details to generate comprehensive reports</p>
            </div>
            <Reports
              prefill={workflow ? {
                name: '',
                location: { latitude, longitude },
                capacity_mw: workflow?.site_analysis?.estimated_capacity_mw ?? 0,
                resource_type: projectType,
                developer: '',
                country: selectedCity?.country || '',
                estimated_cost: workflow?.cost_evaluation?.total_capex_usd ?? 0,
                timeline_months: 24,
              } : undefined}
            />
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
          <MapPin className="mx-auto mb-4" />
          <p>Fill the form above and click "Run Full Analysis" to generate site, resource, cost and report outputs in one workflow.</p>
        </div>
      )}

      {/* Protected Area Modal */}
      <ProtectedAreaModal
        result={protectedResult || { isProtected: false, names: [] }}
        onProceed={handleProceedFromModal}
        onCancel={handleCancelFromModal}
      />
    </div>
  );
}


//original
// import React, { useState, useEffect } from "react";
// import {
//   MapPin,
//   Zap,
//   Sun,
//   Wind,
//   DollarSign,
//   FileText,
//   AlertTriangle, 
//   Search,
//   Map as MapIcon,
// } from "lucide-react";
// import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
// import L from "leaflet";
// import "leaflet/dist/leaflet.css";
// import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
// import toast from "react-hot-toast";
// import { apiEndpoints } from "../services/api";
// import { Reports } from './Reports'

// // Leaflet default marker fix
// import iconUrl from 'leaflet/dist/images/marker-icon.png'
// import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
// import shadowUrl from 'leaflet/dist/images/marker-shadow.png'

// //import { AlertTriangle } from "lucide-react";
// import { checkProtectedArea } from "../services/protectedAreas"; // new service

// delete (L.Icon.Default.prototype as any)._getIconUrl
// L.Icon.Default.mergeOptions({
//   iconRetinaUrl,
//   iconUrl,
//   shadowUrl,
// })

// type ProjectType = "solar" | "wind" | "hybrid";

// interface CitySuggestion {
//   name: string;
//   country: string;
//   lat: number;
//   lon: number;
//   state?: string;
// }

// export default function FullAnalysisPage() {
//   // Site form states
//   const [citySearch, setCitySearch] = useState("");
//   const [citySuggestions, setCitySuggestions] = useState<CitySuggestion[]>([]);
//   const [selectedCity, setSelectedCity] = useState<CitySuggestion | null>(null);
//   const [showSuggestions, setShowSuggestions] = useState(false);

//   const [latitude, setLatitude] = useState<number>(0);
//   const [longitude, setLongitude] = useState<number>(0);
//   const [areaKm2, setAreaKm2] = useState<number>(0);
//   const [projectType, setProjectType] = useState<ProjectType>("solar");

//   const [isLoading, setIsLoading] = useState(false);
//   const [workflow, setWorkflow] = useState<any | null>(null);
//   const [mapType, setMapType] = useState<'street' | 'satellite'>('street');

  
//   // --- Helper Functions ---
//   // Removed hardcoded calculations: gwhToWh, gwhToAverageWatts, formatLarge, estimateResources
//   // These are now provided by the backend API in the workflow response
  
//   const formatLarge = (n: number) => {
//     if (!isFinite(n)) return "N/A";
//     if (Math.abs(n) >= 1e12) return `${(n / 1e12).toFixed(2)}T`;
//     if (Math.abs(n) >= 1e9) return `${(n / 1e9).toFixed(2)}B`;
//     if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
//     if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(2)}k`;
//     return n.toFixed(0);
//   };

//   const buildSeasonalData = (est: any) => {
//     if (!est) return [];
//     const { seasonal_variation = {}, annual_generation_gwh = 0 } = est;
//     return [
//       {
//         name: "Spring",
//         factor: seasonal_variation.spring ?? 1,
//         generation_gwh: (annual_generation_gwh * (seasonal_variation.spring ?? 1)) / 4,
//       },
//       {
//         name: "Summer",
//         factor: seasonal_variation.summer ?? 1,
//         generation_gwh: (annual_generation_gwh * (seasonal_variation.summer ?? 1)) / 4,
//       },
//       {
//         name: "Fall",
//         factor: seasonal_variation.fall ?? 1,
//         generation_gwh: (annual_generation_gwh * (seasonal_variation.fall ?? 1)) / 4,
//       },
//       {
//         name: "Winter",
//         factor: seasonal_variation.winter ?? 1,
//         generation_gwh: (annual_generation_gwh * (seasonal_variation.winter ?? 1)) / 4,
//       },
//     ];
//   };

//   // --- City Search ---
//   const searchCities = async (query: string) => {
//     if (query.length < 3) {
//       setCitySuggestions([]);
//       return;
//     }
//     try {
//       const response = await fetch(
//         `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=1`
//       );
//       const data = await response.json();
//       const suggestions: CitySuggestion[] = data.map((item: any) => ({
//         name: item.display_name.split(",")[0],
//         country: item.address?.country || "",
//         state: item.address?.state || "",
//         lat: parseFloat(item.lat),
//         lon: parseFloat(item.lon),
//       }));
//       setCitySuggestions(suggestions);
//     } catch (err) {
//       console.error(err);
//       toast.error("Failed to search cities");
//     }
//   };

//   const handleCitySelect = (city: CitySuggestion) => {
//     setSelectedCity(city);
//     setCitySearch(`${city.name}, ${city.state || city.country}`);
//     setLatitude(city.lat);
//     setLongitude(city.lon);
//     setShowSuggestions(false);
//     setCitySuggestions([]);
//   };

//   useEffect(() => {
//     const handleClickOutside = () => setShowSuggestions(false);
//     document.addEventListener("click", handleClickOutside);
//     return () => document.removeEventListener("click", handleClickOutside);
//   }, []);

//   // --- Full Analysis ---

// // Define performAnalysis as the existing try block without the check
//   const runFullAnalysis = async () => {
//   setIsLoading(true);
//   setWorkflow(null);

//   try {
//     // --- Protected Area Check ---
//     if (isFinite(latitude) && isFinite(longitude)) {
//       const { isProtected, names } = await checkProtectedArea(latitude, longitude);
//       if (isProtected) {
//         toast.error(`Location overlaps protected area: ${names.join(", ")}`, { duration: 6000 });
//         setIsLoading(false);
//         return; // stop analysis
//       }
//     }

//     // --- Existing backend call ---
//     const r = await apiEndpoints.fullAnalysis({
//       location: { latitude, longitude, area_km2: areaKm2 },
//       project_type: projectType,
//       analysis_depth: "comprehensive",
//       city_name: selectedCity?.name || "",
//     });
//     const respData: any = r.data;
//     const workflowData = respData?.workflow ?? respData;
//     if (!workflowData) {
//       toast.error("Invalid response from server");
//       setIsLoading(false);
//       return;
//     }
//     setWorkflow(workflowData);
//     toast.success("Full analysis completed");
//   } catch (err: any) {
//     console.error("Full analysis error:", err);
//     toast.error("Full analysis failed. Check console / backend.");
//   } finally {
//     setIsLoading(false);
//   }
// };

//   const renderRecommendations = (siteAnalysis: any) => {
//     if (!siteAnalysis) return null;
//     const recs: string[] = siteAnalysis.recommendations || [];
//     if (!recs.length) return <div className="text-sm text-gray-600">No recommendations available.</div>;
//     return (
//       <ul className="space-y-1">
//         {recs.map((r, i) => (
//           <li key={i} className="text-sm text-gray-700 flex items-start">
//             <span className="text-green-500 mr-2">•</span>
//             <div>{r}</div>
//           </li>
//         ))}
//       </ul>
//     );
//   };

//   const renderRisks = (siteAnalysis: any) => {
//     if (!siteAnalysis) return null;
//     const risks: string[] = siteAnalysis.risks || [];
//     if (!risks.length) return <div className="text-sm text-gray-600">No risks flagged.</div>;
//     return (
//       <ul className="space-y-1">
//         {risks.map((r, i) => (
//           <li key={i} className="text-sm text-gray-700 flex items-start">
//             <span className="text-red-500 mr-2">•</span>
//             <div>{r}</div>
//           </li>
//         ))}
//       </ul>
//     );
//   };

//   return (
//     <div className="p-6">
//       <h1 className="text-xl font-bold mb-4">Full Renewable Project Analysis</h1>

//       {/* Form with City Search */}
//       <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4 relative">
//         <div className="md:col-span-2 relative">
//           <label className="block text-sm font-medium text-gray-700">Search City</label>
//           <div className="relative">
//             <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
//             <input
//               type="text"
//               value={citySearch}
//               onChange={(e) => {
//                 setCitySearch(e.target.value);
//                 searchCities(e.target.value);
//                 setShowSuggestions(true);
//               }}
//               className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
//               placeholder="Search for a city..."
//             />
//           </div>

//           {showSuggestions && citySuggestions.length > 0 && (
//             <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
//               {citySuggestions.map((city, idx) => (
//                 <div
//                   key={idx}
//                   className="px-4 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0"
//                   onClick={() => handleCitySelect(city)}
//                 >
//                   <div className="font-medium">{city.name}</div>
//                   <div className="text-sm text-gray-500">{city.state && `${city.state}, `}{city.country}</div>
//                 </div>
//               ))}
//             </div>
//           )}
//         </div>

//         <div>
//           <label className="block text-sm font-medium text-gray-700">Latitude</label>
//           <input 
//             type="number" 
//             value={latitude || ''} 
//             onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)} 
//             placeholder="e.g., 7.29"
//             className="w-full border rounded p-2" 
//           />
//         </div>
//         <div>
//           <label className="block text-sm font-medium text-gray-700">Longitude</label>
//           <input 
//             type="number" 
//             value={longitude || ''} 
//             onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)} 
//             placeholder="e.g., 80.63"
//             className="w-full border rounded p-2" 
//           />
//         </div>
//         <div>
//           <label className="block text-sm font-medium text-gray-700">Area (km²)</label>
//           <input 
//             type="number" 
//             value={areaKm2 || ''} 
//             onChange={(e) => setAreaKm2(parseFloat(e.target.value) || 0)} 
//             placeholder="e.g., 100"
//             className="w-full border rounded p-2" 
//           />
//         </div>
//         <div>
//           <label className="block text-sm font-medium text-gray-700">Project Type</label>
//           <select value={projectType} onChange={(e) => setProjectType(e.target.value as ProjectType)} className="w-full border rounded p-2">
//             <option value="solar">Solar</option>
//             <option value="wind">Wind</option>
//             <option value="hybrid">Hybrid</option>
//           </select>
//         </div>
//       </div>

//       {/* Run & Reset Buttons */}
//       <div className="flex gap-3 mb-6">
//         <button onClick={runFullAnalysis} disabled={isLoading} className="bg-green-600 text-white px-4 py-2 rounded disabled:opacity-50">
//           {isLoading ? "Running full analysis..." : "Run Full Analysis"}
//         </button>
//         <button onClick={() => setWorkflow(null)} className="bg-gray-200 px-4 py-2 rounded">Reset</button>
//       </div>

//       {/* Results */}
//       {workflow ? (
//         <div className="space-y-6">
//           {/* Map + Site */}
//           <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//             <div className="bg-white rounded-lg shadow p-4 lg:col-span-1">
//               <div className="flex items-center justify-between mb-2">
//                 <h2 className="font-semibold flex items-center"><MapIcon className="mr-2" /> Selected Site</h2>
//                 <div className="flex gap-1 text-xs">
//                   <button
//                     onClick={() => setMapType('street')}
//                     className={`px-2 py-1 rounded ${mapType === 'street' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'}`}
//                   >
//                     Street
//                   </button>
//                   <button
//                     onClick={() => setMapType('satellite')}
//                     className={`px-2 py-1 rounded ${mapType === 'satellite' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700'}`}
//                   >
//                     Satellite
//                   </button>
//                 </div>
//               </div>
//               <div className="h-56 rounded overflow-hidden">
//                 <MapContainer center={[latitude, longitude]} zoom={10} style={{ height: "100%", width: "100%" }}>
//                   <TileLayer 
//                     url={mapType === 'satellite' 
//                       ? "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
//                       : "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
//                     }
//                     attribution={mapType === 'satellite'
//                       ? '&copy; <a href="https://www.esri.com/">Esri</a>'
//                       : '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
//                     }
//                   />
//                   <Marker position={[latitude, longitude]}>
//                     <Popup>
//                       <div className="text-sm">
//                         <div className="font-semibold">Selected site</div>
//                         <div>{latitude.toFixed(4)}, {longitude.toFixed(4)}</div>
//                         <div className="mt-1 text-xs text-gray-600">Resource: {projectType.toUpperCase()}</div>
//                       </div>
//                     </Popup>
//                   </Marker>
//                 </MapContainer>
//               </div>
//             </div>

//             {/* Site Analysis */}
//             <div className="bg-white rounded-lg shadow p-4 lg:col-span-2">
//               <h2 className="font-semibold mb-2 flex items-center"><MapPin className="mr-2" /> Site Analysis</h2>
//               <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
//                 <div className="p-3 bg-gray-50 rounded">
//                   <div className="text-sm text-gray-500">Overall Score</div>
//                   <div className="text-2xl font-bold text-green-600">{workflow.site_analysis ? ((workflow.site_analysis.overall_score ?? 0) * 100).toFixed(1) : "N/A"}%</div>
//                 </div>
//                 <div className="p-3 bg-blue-50 rounded">
//   <div className="text-sm text-blue-700">Estimated Capacity</div>
//   <div className="text-2xl font-bold text-blue-600">
//     {workflow.site_analysis 
//       ? formatLarge((workflow.site_analysis.estimated_capacity_mw ?? 0) * 1e6) 
//       : "N/A"} W
//   </div>
// </div>

//                 <div className="p-3 bg-gray-50 rounded">
//                   <div className="text-sm text-gray-500">Accessibility / Environmental</div>
//                   <div className="text-lg font-semibold text-gray-700">{workflow.site_analysis ? `${Math.round((workflow.site_analysis.accessibility_score ?? 0) * 100)}% / ${Math.round((workflow.site_analysis.environmental_score ?? 0) * 100)}%` : "N/A"}</div>
//                 </div>
//               </div>

//               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//                 <div className="p-3 border rounded">
//                   <h3 className="font-medium mb-2">Recommendations</h3>
//                   {renderRecommendations(workflow.site_analysis)}
//                 </div>
//                 <div className="p-3 border rounded">
//                   <h3 className="font-medium mb-2">Risks</h3>
//                   {renderRisks(workflow.site_analysis)}
//                 </div>
//               </div>
//             </div>
//           </div>

//           {/* Resource Estimation */}
//           <div className="bg-white rounded-lg shadow p-4">
//             <h2 className="font-semibold mb-3 flex items-center"><Zap className="mr-2" /> Resource Estimation</h2>
//             {(() => {
//               const est = workflow.resource_estimation;
//               if (!est) return <div className="text-sm text-gray-600">No resource estimation returned.</div>;

//               const seasonalData = buildSeasonalData(est);
//               const annualGwh = Number(est.annual_generation_gwh ?? 0);
//               const peakPowerMw = Number(est.peak_power_mw ?? 0);

//               return (
//                 <div className="space-y-4">
//                   <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
//                     <div className="p-3 bg-green-50 rounded">
//                       <div className="text-sm text-green-700">Annual Generation</div>
//                       <div className="text-2xl font-bold">{annualGwh.toFixed(1)} GWh</div>
//                       <div className="text-xs text-gray-600 mt-1">≈ {formatLarge(annualGwh * 1e9)} Wh/year</div>
//                       <div className="text-xs text-gray-600">Avg power ≈ {formatLarge(Math.round((annualGwh * 1e9) / 8760))} W</div>
//                     </div>
//                     <div className="p-3 bg-blue-50 rounded">
//                       <div className="text-sm text-blue-700">Peak Power</div>
//                       <div className="text-2xl font-bold">{Number(est.peak_power_mw ?? 0).toFixed(1)} MW</div>
//                     </div>
//                     <div className="p-3 bg-purple-50 rounded">
//                       <div className="text-sm text-purple-700">Capacity Factor</div>
//                       <div className="text-2xl font-bold">{((est.capacity_factor ?? 0) * 100).toFixed(1)}%</div>
//                     </div>
//                     <div className="p-3 bg-yellow-50 rounded">
//                       <div className="text-sm text-yellow-700">Confidence / Data Quality</div>
//                       <div className="text-lg font-semibold">{((est.confidence_level ?? 0) * 100).toFixed(0)}% / {((est.data_quality_score ?? 0) * 100).toFixed(0)}%</div>
//                     </div>
//                   </div>

//                   <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
//                     <div className="col-span-2 p-3 border rounded min-h-[220px]">
//                       <h4 className="font-medium mb-2">Seasonal Generation Variation</h4>
//                       <div className="h-44">
//                         <ResponsiveContainer width="100%" height="100%">
//                           <BarChart data={seasonalData}>
//                             <CartesianGrid strokeDasharray="3 3" />
//                             <XAxis dataKey="name" />
//                             <YAxis />
//                             <Tooltip formatter={(value: any) => [`${Number(value).toFixed(2)} GWh`, "Generation"]} />
//                             <Bar dataKey="generation_gwh" fill="#10B981" />
//                           </BarChart>
//                         </ResponsiveContainer>
//                       </div>
//                     </div>
//                     <div className="p-3 border rounded">
//                       <h4 className="font-medium mb-2">Uncertainty Range</h4>
//                       <div className="text-sm text-gray-600">Low: {(est.uncertainty_range?.[0] ?? 0).toFixed(1)} GWh</div>
//                       <div className="text-sm text-gray-600">High: {(est.uncertainty_range?.[1] ?? 0).toFixed(1)} GWh</div>
//                     </div>
//                   </div>

//                   <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//                     {(projectType === "solar" || projectType === "hybrid") && (
//                       <div className="p-4 border rounded">
//                         <div className="flex items-center justify-between mb-2">
//                           <h4 className="font-medium flex items-center"><Sun className="mr-2" /> Solar Resource</h4>
//                         </div>
//                         <div className="space-y-2">
//                           <div className="text-sm">Peak Power: {peakPowerMw.toFixed(1)} MW</div>
//                           <div className="text-sm">Annual Generation: {annualGwh.toFixed(1)} GWh</div>
//                           <div className="text-sm">Capacity Factor: {((est.capacity_factor ?? 0) * 100).toFixed(1)}%</div>
//                           <div className="text-xs text-gray-500 mt-2">Equipment details available from backend API</div>
//                         </div>
//                       </div>
//                     )}
//                     {(projectType === "wind" || projectType === "hybrid") && (
//                       <div className="p-4 border rounded">
//                         <div className="flex items-center justify-between mb-2">
//                           <h4 className="font-medium flex items-center"><Wind className="mr-2" /> Wind Resource</h4>
//                         </div>
//                         <div className="space-y-2">
//                           <div className="text-sm">Peak Power: {peakPowerMw.toFixed(1)} MW</div>
//                           <div className="text-sm">Annual Generation: {annualGwh.toFixed(1)} GWh</div>
//                           <div className="text-sm">Capacity Factor: {((est.capacity_factor ?? 0) * 100).toFixed(1)}%</div>
//                           <div className="text-xs text-gray-500 mt-2">Equipment details available from backend API</div>
//                         </div>
//                       </div>
//                     )}
//                   </div>
//                 </div>
//               );
//             })()}
//           </div>

//           {/* Cost Evaluation */}
//           <div className="bg-white rounded-lg shadow p-4">
//             <h2 className="font-semibold mb-3 flex items-center"><DollarSign className="mr-2" /> Cost Evaluation</h2>
//             {workflow.cost_evaluation ? (
//               <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
//                 <div className="p-3 border rounded">
//                   <div className="text-sm text-gray-500">Total CAPEX</div>
//                   <div className="text-lg font-bold">${Number(workflow.cost_evaluation.total_capex_usd ?? 0).toLocaleString()}</div>
//                 </div>
//                 <div className="p-3 border rounded">
//                   <div className="text-sm text-gray-500">Annual OPEX</div>
//                   <div className="text-lg font-bold">${Number(workflow.cost_evaluation.annual_opex_usd ?? 0).toLocaleString()}</div>
//                 </div>
//                 <div className="p-3 border rounded">
//                   <div className="text-sm text-gray-500">Annual Revenue</div>
//                   <div className="text-lg font-bold">${Number(workflow.cost_evaluation.annual_revenue_usd ?? 0).toLocaleString()}</div>
//                 </div>
//                 <div className="p-3 border rounded md:col-span-3">
//                   <div className="text-sm text-gray-500">NPV</div>
//                   <div className="text-lg font-semibold">${Number(workflow.cost_evaluation.financial_metrics?.net_present_value_usd ?? 0).toLocaleString()}</div>
//                 </div>
//               </div>
//             ) : <div className="text-sm text-gray-600">No cost evaluation returned.</div>}
//           </div>

         
         
//            {/* Report Section */}
//       <div className="bg-white p-6 rounded-lg shadow-md space-y-4">
//         <div className="border-b border-gray-200 pb-3">
//           <h2 className="font-bold text-xl text-gray-800 flex items-center">
//             <FileText className="mr-2 text-green-600" size={24} />
//             Project Report Generation
//           </h2>
//           <p className="text-sm text-gray-600 mt-1">Fill in project details to generate comprehensive reports</p>
//         </div>
//         <Reports
//           prefill={workflow ? {
//             name: '',
//             location: { latitude, longitude },
//             capacity_mw: workflow?.site_analysis?.estimated_capacity_mw ?? 0,
//             resource_type: projectType,
//             developer: '',
//             country: selectedCity?.country || '',
//             estimated_cost: workflow?.cost_evaluation?.capex_total_usd ?? 0,
//             timeline_months: 24,
//           } : undefined}
//         />
//         <ProtectedAreaModal
//           result={protectedResult || { isProtected: false, names: [] }}
//           onProceed={handleProceedFromModal}
//           onCancel={handleCancelFromModal}
// />
//       </div>
//     </div>      ) : (
//         <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
//           <MapPin className="mx-auto mb-4" />
//           <p>Fill the form above and click "Run Full Analysis" to generate site, resource, cost and report outputs in one workflow.</p>
//         </div>
//       )}
//     </div>
//   );
// }