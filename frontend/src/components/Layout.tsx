import React from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { 
  Home, 
  BarChart3, 
  MapPin, 
  Zap, 
  DollarSign, 
  FileText,
  LogOut,
  User
} from 'lucide-react'

export function Layout() {
  const { user, logout: authLogout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate() // <-- for redirecting after logout

  const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
    { name: 'Site Analysis', href: '/site-analysis', icon: MapPin },
    { name: 'Resource Estimation', href: '/resource-estimation', icon: Zap },
    { name: 'Cost Evaluation', href: '/cost-evaluation', icon: DollarSign },
    { name: 'Reports', href: '/reports', icon: FileText },
    // { name: 'AI Agent', href: '/agent', icon: Zap },
    // { name: 'AI Agent', href: '/chatbot', icon: Zap },
    { name: 'Full Analysis', href: '/full-analysis', icon: FileText },
    { name: 'AI Agent', href: '/sparks', icon: Zap },
  ]

  // Handle logout + redirect
  const handleLogout = () => {
    authLogout()        // clear user state
    navigate('/login')  // redirect to login page
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-center border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-lg bg-green-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">G</span>
              </div>
              <span className="text-xl font-bold text-gray-900">GeoSpark</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-4 py-4">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-green-100 text-green-700'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* User info or auth actions */}
          <div className="border-t border-gray-200 p-4">
            {user ? (
              <div className="flex items-center space-x-3">
                <div className="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
                  <User className="h-4 w-4 text-gray-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <Link to="/profile" className="text-sm font-medium text-gray-900 truncate hover:underline">
                    {user.username}
                  </Link>
                  <p className="text-xs text-gray-500 truncate">
                    {user.role}
                  </p>
                </div>
                <button
                  onClick={handleLogout} // <-- updated
                  className="p-1 text-gray-400 hover:text-gray-600"
                  title="Logout"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center justify-between space-x-2">
                <Link
                  to="/login"
                  className="w-1/2 text-center px-3 py-2 text-sm font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200"
                >
                  Sign in
                </Link>
                <Link
                  to="/signup"
                  className="w-1/2 text-center px-3 py-2 text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                >
                  Sign up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
