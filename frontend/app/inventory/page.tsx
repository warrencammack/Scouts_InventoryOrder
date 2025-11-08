'use client'

import { useState } from 'react'
import InventoryDashboard from '@/components/InventoryDashboard'
import InventoryCharts from '@/components/InventoryCharts'
import { BarChart3, Table } from 'lucide-react'

export default function InventoryPage() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'charts'>('dashboard')
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleAdjust = () => {
    // Trigger refresh when inventory is adjusted
    setRefreshTrigger((prev) => prev + 1)
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Badge Inventory</h1>
        <p className="text-gray-600">
          View and manage your current badge stock levels
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium transition-colors ${
              activeTab === 'dashboard'
                ? 'border-scout-purple text-scout-purple'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
            }`}
          >
            <Table className="w-5 h-5" />
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('charts')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium transition-colors ${
              activeTab === 'charts'
                ? 'border-scout-purple text-scout-purple'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
            }`}
          >
            <BarChart3 className="w-5 h-5" />
            Charts & Analytics
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'dashboard' ? (
        <InventoryDashboard onAdjust={handleAdjust} />
      ) : (
        <InventoryCharts refreshTrigger={refreshTrigger} />
      )}
    </div>
  )
}
