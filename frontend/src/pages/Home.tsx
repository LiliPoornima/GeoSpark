import React from 'react'
import { MapPin, Zap, DollarSign, BarChart3, Users, Globe } from 'lucide-react'

export function Home() {
  const features = [
    {
      icon: MapPin,
      title: 'Site Selection',
      description: 'AI-powered analysis of geographical locations for renewable energy potential',
      href: '/site-analysis'
    },
    {
      icon: Zap,
      title: 'Resource Estimation',
      description: 'Comprehensive evaluation of solar, wind, and hydro resources',
      href: '/resource-estimation'
    },
    {
      icon: DollarSign,
      title: 'Cost Evaluation',
      description: 'Advanced financial modeling and ROI calculations',
      href: '/cost-evaluation'
    },
    {
      icon: BarChart3,
      title: 'Analytics Dashboard',
      description: 'Real-time insights and performance monitoring',
      href: '/dashboard'
    }
  ]

  const stats = [
    { label: 'Sites Analyzed', value: '1,250+' },
    { label: 'Projects Supported', value: '500+' },
    { label: 'Accuracy Rate', value: '95%+' },
    { label: 'Time Saved', value: '80%' }
  ]

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-green-600 to-green-800 rounded-lg text-white p-8">
        <div className="max-w-3xl">
          <h1 className="text-4xl font-bold mb-4">
            AI-Powered Renewable Energy Analysis
          </h1>
          <p className="text-xl text-green-100 mb-6">
            Accelerate your renewable energy projects with intelligent site selection, 
            resource estimation, and cost evaluation powered by advanced AI.
          </p>
          <div className="flex space-x-4">
            <button className="bg-white text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
              Start Analysis
            </button>
            <button className="border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-green-600 transition-colors">
              View Demo
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6 text-center">
            <div className="text-2xl font-bold text-green-600 mb-1">
              {stat.value}
            </div>
            <div className="text-sm text-gray-600">
              {stat.label}
            </div>
          </div>
        ))}
      </div>

      {/* Features */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => (
            <div key={index} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start space-x-4">
                <div className="bg-green-100 p-3 rounded-lg">
                  <feature.icon className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {feature.description}
                  </p>
                  <a 
                    href={feature.href}
                    className="text-green-600 font-medium hover:text-green-700"
                  >
                    Learn more →
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* How it Works */}
      <div className="bg-gray-50 rounded-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          How GeoSpark Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-green-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold mx-auto mb-4">
              1
            </div>
            <h3 className="text-lg font-semibold mb-2">Input Location</h3>
            <p className="text-gray-600">
              Provide coordinates and project specifications for analysis
            </p>
          </div>
          <div className="text-center">
            <div className="bg-green-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold mx-auto mb-4">
              2
            </div>
            <h3 className="text-lg font-semibold mb-2">AI Analysis</h3>
            <p className="text-gray-600">
              Our multi-agent system analyzes resources, costs, and risks
            </p>
          </div>
          <div className="text-center">
            <div className="bg-green-600 text-white rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold mx-auto mb-4">
              3
            </div>
            <h3 className="text-lg font-semibold mb-2">Get Results</h3>
            <p className="text-gray-600">
              Receive comprehensive reports and recommendations
            </p>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Ready to Accelerate Your Renewable Energy Projects?
        </h2>
        <p className="text-gray-600 mb-6">
          Join hundreds of developers, utilities, and consultants using GeoSpark
        </p>
        <div className="flex justify-center space-x-4">
          <button className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors">
            Start Free Trial
          </button>
          <button className="border-2 border-green-600 text-green-600 px-8 py-3 rounded-lg font-semibold hover:bg-green-600 hover:text-white transition-colors">
            Contact Sales
          </button>
        </div>
      </div>
    </div>
  )
}