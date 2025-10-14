import React, { useState, useEffect } from 'react'
import { apiEndpoints } from '../services/api'
import toast from 'react-hot-toast'
import { 
  Download, FileText, BarChart3, Zap, MapPin, DollarSign, 
  TrendingUp, Users, Globe, Shield, Calendar, ChevronDown
} from 'lucide-react'
import jsPDF from 'jspdf'

// Import Chart.js components
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar, Line, Pie } from 'react-chartjs-2'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

type ReportsPrefill = {
  name?: string
  location?: { latitude: number; longitude: number }
  capacity_mw?: number
  resource_type?: string
  developer?: string
  country?: string
  estimated_cost?: number
  timeline_months?: number
}

export function Reports({ prefill }: { prefill?: ReportsPrefill }) {
  // Initialize with minimal placeholders; will be replaced by prefill when provided
  const [projectData, setProjectData] = useState({
    name: prefill?.name || '',
    location: prefill?.location || { latitude: 0, longitude: 0 },
    capacity_mw: prefill?.capacity_mw ?? 0,
    resource_type: prefill?.resource_type || 'solar',
    developer: prefill?.developer || '',
    country: prefill?.country || '',
    estimated_cost: prefill?.estimated_cost ?? 0,
    timeline_months: prefill?.timeline_months ?? 0,
  })

  // Apply prefill when it changes (e.g., after Full Analysis completes)
  useEffect(() => {
    if (!prefill) return
    setProjectData(prev => ({
      ...prev,
      ...prefill,
      location: prefill.location || prev.location,
      capacity_mw: prefill.capacity_mw ?? prev.capacity_mw,
      estimated_cost: prefill.estimated_cost ?? prev.estimated_cost,
      timeline_months: prefill.timeline_months ?? prev.timeline_months,
    }))
  }, [prefill])
  
  const [report, setReport] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [reportType, setReportType] = useState('executive')
  const [activeTab, setActiveTab] = useState('summary')
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  // Add click outside handler for dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (isDropdownOpen && !target.closest('.resource-dropdown')) {
        setIsDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isDropdownOpen])

  const onChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    if (name.startsWith('location.')) {
      const field = name.split('.')[1]
      setProjectData({
        ...projectData,
        location: { 
          ...projectData.location, 
          [field]: parseFloat(value) || 0 
        }
      })
    } else {
      setProjectData({ 
        ...projectData, 
        [name]: name.includes('capacity') || name.includes('cost') || name.includes('timeline') 
          ? parseFloat(value) || 0 
          : value 
      })
    }
  }

  const onGenerate = async () => {
    if (!projectData.name || !projectData.country || !projectData.capacity_mw) {
      toast.error('Please fill in required fields: Project Name, Country, and Capacity')
      return
    }

    setIsLoading(true)
    try {
      const resp = await apiEndpoints.comprehensiveReport({
        project_name: projectData.name,
        location: projectData.location,
        resource_type: projectData.resource_type,
        capacity_mw: projectData.capacity_mw,
        developer: projectData.developer,
        country: projectData.country,
        report_type: reportType,
        estimated_cost: projectData.estimated_cost,
        timeline_months: projectData.timeline_months
      })
      
      const reportData = resp.data.report
      
      setReport({
        content: reportData.content,
        type: reportData.type,
        generatedAt: new Date().toLocaleString(),
        project: reportData.project,
        sentiment: reportData.sentiment,
        keywords: reportData.keywords,
        charts: reportData.charts,
        metrics: reportData.metrics
      })
      
      toast.success(`${reportType.charAt(0).toUpperCase() + reportType.slice(1)} report generated successfully`)
    } catch (e: any) {
      console.error('Report generation error:', e)
      toast.error('Failed to generate report: ' + (e.response?.data?.detail || e.message))
    } finally {
      setIsLoading(false)
    }
  }

  // Professional PDF Download Function
  const downloadProfessionalPDF = () => {
    if (!report) return;
    
    setIsLoading(true);
    
    try {
      // Create PDF document
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      
      // Add GeoSpark branding header
      pdf.setFillColor(34, 197, 94); // Green color
      pdf.rect(0, 0, pageWidth, 30, 'F');
      
      // Add logo text (you can replace this with your actual logo image)
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(20);
      pdf.setFont('helvetica', 'bold');
      pdf.text('GEO SPARK AI', pageWidth / 2, 15, { align: 'center' });
      
      pdf.setFontSize(12);
      pdf.text('Renewable Energy Analytics Platform', pageWidth / 2, 22, { align: 'center' });
      
      // Add report title
      pdf.setFillColor(255, 255, 255);
      pdf.setTextColor(0, 0, 0);
      pdf.setFontSize(16);
      pdf.setFont('helvetica', 'bold');
      pdf.text(`${report.type.charAt(0).toUpperCase() + report.type.slice(1)} REPORT`, pageWidth / 2, 45, { align: 'center' });
      
      // Add project details
      let yPosition = 60;
      
      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Project Details:', 20, yPosition);
      yPosition += 8;
      
      pdf.setFont('helvetica', 'normal');
      pdf.text(`Project: ${report.project.name}`, 20, yPosition);
      yPosition += 6;
      pdf.text(`Generated: ${new Date().toLocaleString()}`, 20, yPosition);
      yPosition += 10;
      
      // Executive Overview
      pdf.setFont('helvetica', 'bold');
      pdf.text('EXECUTIVE OVERVIEW', 20, yPosition);
      yPosition += 8;
      
      pdf.setFont('helvetica', 'normal');
      const overviewText = `${report.project.name} is a ${report.project.capacity_mw} MW ${report.project.resource_type} energy project located in ${report.project.country}. Developed by ${report.project.developer}, this project represents a significant investment in renewable energy infrastructure.`;
      const overviewLines = pdf.splitTextToSize(overviewText, pageWidth - 40);
      pdf.text(overviewLines, 20, yPosition);
      yPosition += overviewLines.length * 6 + 10;
      
      // Key Financial Metrics
      pdf.setFont('helvetica', 'bold');
      pdf.text('KEY FINANCIAL METRICS', 20, yPosition);
      yPosition += 8;
      
      pdf.setFont('helvetica', 'normal');
      pdf.text(`• Net Present Value: $${report.metrics?.npv?.toFixed(1)} Million`, 25, yPosition);
      yPosition += 6;
      pdf.text(`• Internal Rate of Return: ${(report.metrics?.irr * 100).toFixed(1)}%`, 25, yPosition);
      yPosition += 6;
      pdf.text(`• Payback Period: ${report.metrics?.payback?.toFixed(1)} Years`, 25, yPosition);
      yPosition += 6;
      pdf.text(`• Levelized Cost of Energy: $${report.metrics?.lcoe?.toFixed(1)}/MWh`, 25, yPosition);
      yPosition += 10;
      
      // Technical Performance
      pdf.setFont('helvetica', 'bold');
      pdf.text('TECHNICAL PERFORMANCE', 20, yPosition);
      yPosition += 8;
      
      pdf.setFont('helvetica', 'normal');
      pdf.text(`• Annual Generation: ${report.metrics?.annual_generation?.toFixed(0)} GWh`, 25, yPosition);
      yPosition += 6;
      pdf.text(`• Capacity Factor: ${(report.metrics?.capacity_factor * 100).toFixed(1)}%`, 25, yPosition);
      yPosition += 6;
      pdf.text(`• Carbon Reduction: ${report.metrics?.carbon_reduction?.toLocaleString()} tons CO2/year`, 25, yPosition);
      yPosition += 10;
      
      // Strategic Recommendations
      pdf.setFont('helvetica', 'bold');
      pdf.text('STRATEGIC RECOMMENDATIONS', 20, yPosition);
      yPosition += 8;
      
      pdf.setFont('helvetica', 'normal');
      pdf.text('1. Proceed with project development given strong financial returns', 25, yPosition);
      yPosition += 6;
      pdf.text(`2. Implement phased construction over ${report.project.timeline_months || 24} months`, 25, yPosition);
      yPosition += 6;
      pdf.text('3. Secure power purchase agreements at competitive rates', 25, yPosition);
      yPosition += 6;
      pdf.text(`4. Monitor regulatory developments in ${report.project.country}`, 25, yPosition);
      yPosition += 10;
      
      // Conclusion
      const conclusionText = 'This project demonstrates excellent viability with robust financial metrics and significant environmental benefits.';
      const conclusionLines = pdf.splitTextToSize(conclusionText, pageWidth - 40);
      pdf.text(conclusionLines, 20, yPosition);
      yPosition += conclusionLines.length * 6 + 15;
      
      // Footer
      pdf.setDrawColor(200, 200, 200);
      pdf.line(20, yPosition, pageWidth - 20, yPosition);
      yPosition += 8;
      
      pdf.setFontSize(10);
      pdf.setTextColor(100, 100, 100);
      pdf.text('GeoSpark AI Analytics • Confidential Business Report', pageWidth / 2, yPosition, { align: 'center' });
      
      // Save the PDF
      pdf.save(`GeoSpark_${report.project.name.replace(/\s+/g, '_')}_${report.type}_report.pdf`);
      
      toast.success('Professional PDF report downloaded');
    } catch (error) {
      console.error('PDF generation error:', error);
      toast.error('Failed to generate PDF');
    } finally {
      setIsLoading(false);
    }
  };

  const downloadCSV = () => {
    if (!report) return
    
    const csvContent = [
      ['GeoSpark AI Project Report', ''],
      ['Project Name', report.project.name],
      ['Report Type', report.type],
      ['Generated', report.generatedAt],
      ['Resource Type', report.project.resource_type],
      ['Capacity (MW)', report.project.capacity_mw],
      ['Location', `${report.project.location.latitude}, ${report.project.location.longitude}`],
      ['Country', report.project.country],
      ['Developer', report.project.developer],
      ['Estimated Cost', `$${report.project.estimated_cost?.toLocaleString() || 'N/A'}`],
      ['Timeline (months)', report.project.timeline_months || 'N/A'],
      ['',''],
      ['FINANCIAL METRICS', ''],
      ['Net Present Value', `$${report.metrics?.npv?.toFixed(1)} Million`],
      ['Internal Rate of Return', `${(report.metrics?.irr * 100).toFixed(1)}%`],
      ['Payback Period', `${report.metrics?.payback?.toFixed(1)} Years`],
      ['LCOE', `$${report.metrics?.lcoe?.toFixed(1)}/MWh`],
      ['',''],
      ['TECHNICAL METRICS', ''],
      ['Annual Generation', `${report.metrics?.annual_generation?.toFixed(0)} GWh`],
      ['Capacity Factor', `${(report.metrics?.capacity_factor * 100).toFixed(1)}%`],
      ['Carbon Reduction', `${report.metrics?.carbon_reduction?.toLocaleString()} tons/year`],
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `geospark_${report.project.name.replace(/\s+/g, '_')}_${report.type}_report.csv`
    a.click()
    window.URL.revokeObjectURL(url)
    toast.success('CSV report downloaded')
  }

  // Chart configuration options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
  }

  const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  }

  // Function to render charts
  const renderChart = (chartData: any, type: 'bar' | 'line' | 'pie', label?: string) => {
    if (!chartData || !chartData.labels || !chartData.data) {
      return (
        <div className="h-48 bg-gray-50 rounded-lg flex items-center justify-center">
          <div className="text-center text-gray-500">
            <p className="text-sm">Chart data not available</p>
          </div>
        </div>
      )
    }

    const data = {
      labels: chartData.labels,
      datasets: [
        {
          label: label || chartData.label || 'Data',
          data: chartData.data,
          backgroundColor: chartData.colors || [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
          ],
          borderColor: chartData.colors || [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
            'rgb(255, 206, 86)',
            'rgb(75, 192, 192)',
            'rgb(153, 102, 255)',
          ],
          borderWidth: 1,
        },
      ],
    }

    switch (type) {
      case 'bar':
        return <Bar data={data} options={chartOptions} />
      case 'line':
        return <Line data={data} options={chartOptions} />
      case 'pie':
        return <Pie data={data} options={pieChartOptions} />
      default:
        return <Bar data={data} options={chartOptions} />
    }
  }

  const MetricCard = ({ title, value, unit, icon: Icon }: any) => (
    <div className="bg-white rounded-lg p-4 shadow border hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">
            {value} {unit && <span className="text-sm font-normal text-gray-600">{unit}</span>}
          </p>
        </div>
        <Icon className="h-8 w-8 text-green-600" />
      </div>
    </div>
  )

  const ChartContainer = ({ title, children }: any) => (
    <div className="bg-white rounded-lg p-4 shadow border">
      <h4 className="font-semibold mb-4 text-gray-800">{title}</h4>
      <div className="h-64">
        {children}
      </div>
    </div>
  )

  // Safe calculation functions
  const safeCalculation = (value: number, defaultValue: number = 0) => {
    return isNaN(value) || !isFinite(value) ? defaultValue : value
  }

  const formatNumber = (value: number, decimals: number = 1) => {
    return safeCalculation(value).toFixed(decimals)
  }

  const reportTypes = [
    { 
      id: 'executive', 
      label: 'Executive Summary', 
      icon: FileText, 
      description: 'C-level overview with key metrics' 
    },
    { 
      id: 'investor', 
      label: 'Investor Report', 
      icon: DollarSign, 
      description: 'Investment thesis and financials' 
    },
    { 
      id: 'technical', 
      label: 'Technical Report', 
      icon: Zap, 
      description: 'Engineering specifications' 
    },
    { 
      id: 'environmental', 
      label: 'Environmental Report', 
      icon: Globe, 
      description: 'Sustainability impact' 
    }
  ]

  const resourceTypes = [
    { value: 'solar', label: 'Solar' },
    { value: 'wind', label: 'Wind' },
    { value: 'hybrid', label: 'Hybrid' },
    { value: 'hydro', label: 'Hydro' }
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">GeoSpark AI Project Reports</h1>
          <p className="text-gray-600">Generate comprehensive renewable energy project analysis reports</p>
        </div>
        {report && (
          <div className="flex gap-2">
            <button 
              onClick={downloadCSV}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="h-4 w-4 mr-2" />
              CSV
            </button>
            <button 
              onClick={downloadProfessionalPDF}
              disabled={isLoading}
              className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating PDF...
                </>
              ) : (
                <>
                  <FileText className="h-4 w-4 mr-2" />
                  PDF
                </>
              )}
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Form */}
        <div className="space-y-6 lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-lg font-semibold flex items-center">
              <FileText className="h-5 w-5 mr-2 text-green-600" />
              Project Details
            </h2>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Project Name *</label>
              <input 
                name="name" 
                value={projectData.name} 
                onChange={onChange} 
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                placeholder="Enter project name"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Latitude</label>
                <input 
                  type="number" 
                  step="any"
                  name="location.latitude"
                  value={projectData.location.latitude} 
                  onChange={onChange} 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Longitude</label>
                <input 
                  type="number" 
                  step="any"
                  name="location.longitude"
                  value={projectData.location.longitude} 
                  onChange={onChange} 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Capacity (MW) *</label>
              <input 
                type="number"
                name="capacity_mw"
                value={projectData.capacity_mw} 
                onChange={onChange} 
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                min="1"
              />
            </div>
            
            {/* Fixed Resource Type Dropdown */}
            <div className="relative resource-dropdown">
              <label className="block text-sm font-medium text-gray-700 mb-1">Resource Type</label>
              <button
                type="button"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors bg-white text-gray-900 text-left flex justify-between items-center hover:border-green-300"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              >
                <span className="capitalize">{projectData.resource_type}</span>
                <ChevronDown className={`h-4 w-4 text-gray-500 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
              </button>
              
              {isDropdownOpen && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                  {resourceTypes.map((type) => (
                    <button
                      key={type.value}
                      type="button"
                      className={`w-full px-3 py-3 text-left transition-colors first:rounded-t-md last:rounded-b-md border-b border-gray-100 last:border-b-0 ${
                        projectData.resource_type === type.value 
                          ? 'bg-green-50 text-green-700 font-medium border-green-200' 
                          : 'bg-white text-gray-900 hover:bg-green-50 hover:text-green-700'
                      }`}
                      onClick={() => {
                        setProjectData({ ...projectData, resource_type: type.value })
                        setIsDropdownOpen(false)
                      }}
                    >
                      <div className="flex items-center">
                        <div className={`w-2 h-2 rounded-full mr-3 ${
                          projectData.resource_type === type.value ? 'bg-green-500' : 'bg-gray-300'
                        }`} />
                        <span className="capitalize">{type.label}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Developer</label>
              <input 
                name="developer" 
                value={projectData.developer} 
                onChange={onChange} 
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                placeholder="Enter developer name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Country *</label>
              <input 
                name="country" 
                value={projectData.country} 
                onChange={onChange} 
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                placeholder="Enter country"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Est. Cost ($)</label>
                <input 
                  type="number"
                  name="estimated_cost"
                  value={projectData.estimated_cost} 
                  onChange={onChange} 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Timeline (months)</label>
                <input 
                  type="number"
                  name="timeline_months"
                  value={projectData.timeline_months} 
                  onChange={onChange} 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                />
              </div>
            </div>
          </div>

          {/* Report Type Selection */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center">
              <BarChart3 className="h-5 w-5 mr-2 text-green-600" />
              Report Type
            </h2>
            <div className="grid grid-cols-2 gap-3">
              {reportTypes.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setReportType(type.id)}
                  className={`p-3 border-2 rounded-lg text-left transition-all duration-200 flex items-start space-x-3 min-h-[80px] ${
                    reportType === type.id 
                      ? 'border-green-500 bg-green-50 text-green-700 shadow-md' 
                      : 'border-gray-200 hover:border-green-300 hover:bg-gray-50 hover:shadow-sm'
                  }`}
                >
                  <div className={`p-2 rounded-lg ${
                    reportType === type.id ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-600'
                  }`}>
                    <type.icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-sm mb-1">{type.label}</div>
                    <div className="text-xs text-gray-500 leading-tight">{type.description}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <button 
            onClick={onGenerate} 
            disabled={isLoading}
            className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 flex items-center justify-center transition-colors shadow-md hover:shadow-lg"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generating Report...
              </>
            ) : (
              <>
                <FileText className="h-5 w-5 mr-2" />
                Generate {reportType.charAt(0).toUpperCase() + reportType.slice(1)} Report
              </>
            )}
          </button>
        </div>

        {/* Report Output */}
        <div className="lg:col-span-2">
          {!report ? (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <FileText className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Report Generated</h3>
              <p className="text-gray-600 mb-6">
                {projectData.name
                  ? `Ready to generate a ${projectData.resource_type} report for ${projectData.name} (${projectData.capacity_mw} MW)`
                  : 'Configure your project details and generate a comprehensive report'}
              </p>
              <div className="grid grid-cols-2 gap-4 max-w-md mx-auto">
                <div className="text-center p-4 border-2 border-dashed border-gray-200 rounded-lg bg-gray-50">
                  <BarChart3 className="h-8 w-8 mx-auto mb-2 text-green-600" />
                  <p className="text-sm font-medium">Professional Reports</p>
                  <p className="text-xs text-gray-500 mt-1">Executive, Investor, Technical, Environmental</p>
                </div>
                <div className="text-center p-4 border-2 border-dashed border-gray-200 rounded-lg bg-gray-50">
                  <Download className="h-8 w-8 mx-auto mb-2 text-green-600" />
                  <p className="text-sm font-medium">Export Options</p>
                  <p className="text-xs text-gray-500 mt-1">PDF, CSV Formats</p>
                </div>
              </div>
            </div>
          ) : (
            <div id="report-content" className="bg-white rounded-lg shadow overflow-hidden">
              {/* Report Header */}
              <div className="border-b p-6 bg-gradient-to-r from-green-50 to-blue-50">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{report.project.name}</h2>
                    <p className="text-gray-600">
                      {report.type.charAt(0).toUpperCase() + report.type.slice(1)} Report • 
                      Generated {report.generatedAt} • GeoSpark AI
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-gray-900">{report.project.capacity_mw} MW {report.project.resource_type}</div>
                    <div className="text-gray-600 flex items-center justify-end">
                      <MapPin className="h-4 w-4 mr-1" />
                      {report.project.country}
                    </div>
                  </div>
                </div>
              </div>

              {/* Report Tabs */}
              <div className="border-b bg-white">
                <div className="flex space-x-8 px-6">
                  {['summary', 'metrics', 'financial', 'technical', 'environmental'].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                        activeTab === tab
                          ? 'border-green-500 text-green-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tab Content */}
              <div className="p-6 bg-gray-50">
                {activeTab === 'summary' && (
                  <div className="space-y-6">
                    <div className="prose max-w-none">
                      <div className="bg-white rounded-lg border p-6">
                        <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans leading-relaxed">
                          {report.content}
                        </pre>
                      </div>
                    </div>
                    
                    {/* Key Metrics Grid */}
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                      <MetricCard 
                        title="Net Present Value" 
                        value={formatNumber(report.metrics?.npv)} 
                        unit="M USD" 
                        icon={DollarSign}
                      />
                      <MetricCard 
                        title="Internal Rate of Return" 
                        value={formatNumber(safeCalculation(report.metrics?.irr) * 100)} 
                        unit="%" 
                        icon={TrendingUp}
                      />
                      <MetricCard 
                        title="Payback Period" 
                        value={formatNumber(report.metrics?.payback)} 
                        unit="years" 
                        icon={Calendar}
                      />
                      <MetricCard 
                        title="LCOE" 
                        value={formatNumber(report.metrics?.lcoe)} 
                        unit="USD/MWh" 
                        icon={Zap}
                      />
                    </div>
                  </div>
                )}

                {activeTab === 'metrics' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <ChartContainer title="CAPEX Breakdown">
                        {renderChart(report.charts?.financial?.capex_breakdown, 'pie', 'Cost Distribution')}
                      </ChartContainer>
                      <ChartContainer title="Revenue Forecast (5 Years)">
                        {renderChart(report.charts?.financial?.revenue_forecast, 'line', 'Revenue (Million USD)')}
                      </ChartContainer>
                    </div>
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                      <MetricCard 
                        title="Annual Generation" 
                        value={formatNumber(report.metrics?.annual_generation, 0)} 
                        unit="GWh" 
                        icon={Zap} 
                      />
                      <MetricCard 
                        title="Carbon Reduction" 
                        value={formatNumber(safeCalculation(report.metrics?.carbon_reduction) / 1000, 0)} 
                        unit="K tons/year" 
                        icon={Globe} 
                      />
                      <MetricCard 
                        title="Capacity Factor" 
                        value={formatNumber(safeCalculation(report.metrics?.capacity_factor) * 100)} 
                        unit="%" 
                        icon={Users} 
                      />
                    </div>
                  </div>
                )}

                {activeTab === 'financial' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      <ChartContainer title="CAPEX Breakdown">
                        {renderChart(report.charts?.financial?.capex_breakdown, 'pie', 'Cost Distribution')}
                      </ChartContainer>
                      <ChartContainer title="Revenue Forecast">
                        {renderChart(report.charts?.financial?.revenue_forecast, 'line', 'Revenue (Million USD)')}
                      </ChartContainer>
                    </div>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                      <MetricCard 
                        title="NPV" 
                        value={formatNumber(report.metrics?.npv)} 
                        unit="M USD" 
                        icon={DollarSign}
                      />
                      <MetricCard 
                        title="IRR" 
                        value={formatNumber(safeCalculation(report.metrics?.irr) * 100)} 
                        unit="%" 
                        icon={TrendingUp}
                      />
                      <MetricCard 
                        title="Payback" 
                        value={formatNumber(report.metrics?.payback)} 
                        unit="years" 
                        icon={Calendar}
                      />
                      <MetricCard 
                        title="LCOE" 
                        value={formatNumber(report.metrics?.lcoe)} 
                        unit="USD/MWh" 
                        icon={Zap}
                      />
                    </div>
                  </div>
                )}

                {activeTab === 'technical' && (
                  <div className="space-y-6">
                    <ChartContainer title="Monthly Generation Profile">
                      {renderChart(report.charts?.technical?.monthly_generation, 'line', 'Generation (GWh)')}
                    </ChartContainer>
                    <div className="grid grid-cols-2 gap-4">
                      <MetricCard 
                        title="Capacity Factor" 
                        value={formatNumber(safeCalculation(report.metrics?.capacity_factor) * 100)} 
                        unit="%" 
                        icon={Zap} 
                      />
                      <MetricCard 
                        title="Annual Generation" 
                        value={formatNumber(report.metrics?.annual_generation, 0)} 
                        unit="GWh" 
                        icon={TrendingUp} 
                      />
                    </div>
                  </div>
                )}

                {activeTab === 'environmental' && (
                  <div className="space-y-6">
                    <ChartContainer title="Environmental Impact Analysis">
                      {renderChart({
                        labels: ['CO2 Reduction', 'Equivalent Trees', 'Homes Powered'],
                        data: [
                          safeCalculation(report.metrics?.carbon_reduction) / 1000,
                          (safeCalculation(report.metrics?.carbon_reduction) * 22.4) / 1000000,
                          safeCalculation(report.metrics?.annual_generation) * 0.1
                        ],
                        label: 'Environmental Impact'
                      }, 'bar')}
                    </ChartContainer>
                    <div className="grid grid-cols-2 gap-4">
                      <MetricCard 
                        title="CO2 Reduction" 
                        value={formatNumber(safeCalculation(report.metrics?.carbon_reduction) / 1000, 0)} 
                        unit="K tons/year" 
                        icon={Globe} 
                      />
                      <MetricCard 
                        title="Equivalent Trees" 
                        value={formatNumber((safeCalculation(report.metrics?.carbon_reduction) * 22.4) / 1000000, 1)} 
                        unit="M trees" 
                        icon={Shield} 
                      />
                    </div>
                    
                    {/* Fixed Environmental Report Text Content */}
                    <div className="bg-white rounded-lg border p-6">
                      <h3 className="text-lg font-semibold mb-4 text-green-700">Environmental Impact Summary</h3>
                      <div className="text-sm text-gray-700 space-y-4 leading-relaxed">
                        <p>
                          The <strong>{report.project.capacity_mw} MW {report.project.resource_type}</strong> project in <strong>{report.project.country}</strong> demonstrates significant environmental benefits through clean energy generation and substantial carbon emission reductions.
                        </p>
                        
                        <div>
                          <strong className="text-green-700">Key Environmental Achievements:</strong>
                          <ul className="list-disc list-inside space-y-2 mt-2 ml-4">
                            <li>Annual carbon reduction of approximately <strong>{formatNumber(safeCalculation(report.metrics?.carbon_reduction) / 1000, 0)} thousand tons</strong> of CO₂ emissions</li>
                            <li>Equivalent to planting <strong>{formatNumber((safeCalculation(report.metrics?.carbon_reduction) * 22.4) / 1000000, 1)} million trees</strong></li>
                            <li>Powering approximately <strong>{formatNumber(safeCalculation(report.metrics?.annual_generation) * 0.1, 0)} homes</strong> with clean, renewable energy</li>
                            <li>Supporting <strong>{report.project.country}'s</strong> renewable energy targets and climate commitments</li>
                            <li>Reducing water consumption by <strong>{formatNumber(report.metrics?.annual_generation * 1000, 0)} gallons</strong> annually compared to thermal generation</li>
                          </ul>
                        </div>
                        
                        <p>
                          This project contributes to sustainable development by reducing dependence on fossil fuels, improving local air quality, and supporting the transition to a low-carbon economy. The environmental benefits align with global sustainability goals and create long-term value for both investors and local communities.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Report Footer */}
              <div className="border-t bg-white px-6 py-4">
                <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center">
                    <span className="font-medium mr-2">Sentiment:</span> 
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      report.sentiment === 'positive' ? 'bg-green-100 text-green-800' :
                      report.sentiment === 'negative' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {report.sentiment}
                    </span>
                  </div>
                  <div className="flex-1 lg:text-center">
                    <span className="font-medium">Keywords:</span> {report.keywords?.slice(0, 5).join(', ')}
                  </div>
                  <div className="text-green-600 font-medium">GeoSpark AI Analytics • Confidential</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}