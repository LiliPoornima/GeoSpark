import React, { useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import toast from "react-hot-toast";
import "leaflet/dist/leaflet.css";

// Fix default leaflet icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

function FullAnalysisPage() {
  const [latitude, setLatitude] = useState(7.29);
  const [longitude, setLongitude] = useState(80.63);
  const [projectType, setProjectType] = useState("solar");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const runFullAnalysis = async () => {
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/api/v1/full-analysis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          location: { latitude, longitude, area_km2: 100 },
          project_type: projectType,
          analysis_depth: "comprehensive",
        }),
      });

      const data = await res.json();

      if (!data.workflow) {
        toast.error("Full analysis failed. Check server logs.");
        setResult(null);
        return;
      }

      setResult(data.workflow);
      toast.success("Full analysis completed!");
    } catch (err) {
      console.error(err);
      toast.error("Failed to run full analysis.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Full Renewable Project Analysis</h1>

      {/* Input Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <input
          type="number"
          value={latitude}
          onChange={(e) => setLatitude(parseFloat(e.target.value))}
          placeholder="Latitude"
          className="border rounded p-2"
        />
        <input
          type="number"
          value={longitude}
          onChange={(e) => setLongitude(parseFloat(e.target.value))}
          placeholder="Longitude"
          className="border rounded p-2"
        />
        <select
          value={projectType}
          onChange={(e) => setProjectType(e.target.value)}
          className="border rounded p-2"
        >
          <option value="solar">Solar</option>
          <option value="wind">Wind</option>
          <option value="hybrid">Hybrid</option>
        </select>
      </div>

      <button
        onClick={runFullAnalysis}
        disabled={loading}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        {loading ? "Analyzing..." : "Run Full Analysis"}
      </button>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Map */}
          <div className="h-64 rounded-lg overflow-hidden border">
            <MapContainer
              center={[latitude, longitude]}
              zoom={10}
              style={{ height: "100%", width: "100%" }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution="&copy; OpenStreetMap contributors"
              />
              <Marker position={[latitude, longitude]}>
                <Popup>
                  {projectType} project site <br /> ({latitude}, {longitude})
                </Popup>
              </Marker>
            </MapContainer>
          </div>

          {/* 1️⃣ Site Analysis */}
          {result.site_analysis && (
            <div className="p-4 border rounded space-y-3">
              <h2 className="font-bold text-lg">1️⃣ Site Analysis</h2>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <ScoreCard
                  label="Solar Score"
                  value={result.site_analysis.solar_potential?.solar_score}
                  color="yellow"
                />
                <ScoreCard
                  label="Wind Score"
                  value={result.site_analysis.wind_potential?.wind_score}
                  color="blue"
                />
                <ScoreCard
                  label="Environmental"
                  value={result.site_analysis.environmental_score}
                  color="green"
                />
                <ScoreCard
                  label="Regulatory"
                  value={result.site_analysis.regulatory_score}
                  color="purple"
                />
              </div>
              <div className="mt-2">
                <strong>Estimated Capacity:</strong>{" "}
                {result.site_analysis.estimated_capacity_mw} MW
              </div>
            </div>
          )}

          {/* 2️⃣ Resource Estimation */}
          {result.resource_estimation && (
            <div className="p-4 border rounded space-y-2">
              <h2 className="font-bold text-lg">2️⃣ Resource Estimation</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <strong>Annual Generation:</strong>{" "}
                  {result.resource_estimation.annual_generation_gwh} GWh
                </div>
                <div>
                  <strong>Capacity Factor:</strong>{" "}
                  {result.resource_estimation.capacity_factor}
                </div>
                <div>
                  <strong>Peak Power:</strong>{" "}
                  {result.resource_estimation.peak_power_mw} MW
                </div>
                <div>
                  <strong>Confidence Level:</strong>{" "}
                  {result.resource_estimation.confidence_level}
                </div>
              </div>
            </div>
          )}

          {/* 3️⃣ Cost Evaluation */}
          {result.cost_evaluation && (
            <div className="p-4 border rounded space-y-2">
              <h2 className="font-bold text-lg">3️⃣ Cost Evaluation</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <strong>NPV:</strong>{" "}
                  {result.cost_evaluation.financial_metrics.net_present_value_usd.toFixed(2)} USD
                </div>
                <div>
                  <strong>IRR:</strong>{" "}
                  {result.cost_evaluation.financial_metrics.internal_rate_of_return.toFixed(2)}
                </div>
                <div>
                  <strong>Payback Period:</strong>{" "}
                  {result.cost_evaluation.financial_metrics.payback_period_years?.toFixed(1)} yrs
                </div>
                <div>
                  <strong>LCOE:</strong>{" "}
                  {result.cost_evaluation.financial_metrics.levelized_cost_of_energy_usd_mwh?.toFixed(2)} USD/MWh
                </div>
              </div>
            </div>
          )}

          {/* 4️⃣ Report Summary */}
          {result.report_summary && (
            <div className="p-4 border rounded">
              <h2 className="font-bold text-lg">4️⃣ Report Summary</h2>
              <p>{result.report_summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ScoreCard component
const ScoreCard = ({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) => {
  const percentage = (value ?? 0) * 100;
  const colorMap: Record<string, string> = {
    yellow: "bg-yellow-400",
    blue: "bg-blue-400",
    green: "bg-green-400",
    purple: "bg-purple-400",
  };
  return (
    <div className="p-3 bg-gray-50 rounded-lg">
      <div className="text-sm">{label}</div>
      <div className="text-xl font-bold">{percentage.toFixed(1)}%</div>
      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
        <div className={`${colorMap[color]} h-2 rounded-full`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
};

export default FullAnalysisPage;
