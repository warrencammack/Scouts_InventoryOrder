'use client'

import { useState } from 'react'
import ShoppingList from '@/components/ShoppingList'
import InventoryCharts from '@/components/InventoryCharts'
import { ShoppingCart, BarChart3, Download, FileText } from 'lucide-react'
import { exportCSV, exportPDF, downloadBlob } from '@/lib/api'

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState<'shopping' | 'charts'>('shopping')
  const [exporting, setExporting] = useState(false)

  const handleExportCSV = async () => {
    setExporting(true)
    try {
      const response = await exportCSV()
      if (response.success && response.data) {
        const date = new Date().toISOString().split('T')[0]
        downloadBlob(response.data, `inventory-${date}.csv`)
      }
    } catch (err) {
      console.error('Failed to export CSV:', err)
    } finally {
      setExporting(false)
    }
  }

  const handleExportPDF = async () => {
    setExporting(true)
    try {
      const response = await exportPDF()
      if (response.success && response.data) {
        const date = new Date().toISOString().split('T')[0]
        downloadBlob(response.data, `inventory-report-${date}.pdf`)
      }
    } catch (err) {
      console.error('Failed to export PDF:', err)
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Reports & Exports</h1>
            <p className="text-gray-600">
              Generate reports and shopping lists for your badge inventory
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleExportCSV}
              disabled={exporting}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FileText className="w-4 h-4" />
              Export CSV
            </button>
            <button
              onClick={handleExportPDF}
              disabled={exporting}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="w-4 h-4" />
              Export PDF
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('shopping')}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 font-medium transition-colors ${
              activeTab === 'shopping'
                ? 'border-scout-purple text-scout-purple'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
            }`}
          >
            <ShoppingCart className="w-5 h-5" />
            Shopping List
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
      {activeTab === 'shopping' ? (
        <ShoppingList />
      ) : (
        <InventoryCharts />
      )}

      {/* Info Box */}
      <div className="mt-8 bg-gradient-to-r from-scout-purple to-purple-700 text-white rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-3 flex items-center gap-2">
          <BarChart3 className="w-6 h-6" />
          Advanced Analytics (Coming Soon)
        </h3>
        <p className="mb-3">
          Future updates will include historical tracking and predictive analytics:
        </p>
        <ul className="list-disc list-inside space-y-1 text-white/90">
          <li>Track inventory changes over time</li>
          <li>Identify usage patterns and trends</li>
          <li>Predictive ordering based on historical data</li>
          <li>Seasonal analysis and forecasting</li>
          <li>Automated reorder alerts</li>
        </ul>
        <p className="text-sm text-white/70 mt-3">
          This feature will be available in ACTION-601
        </p>
      </div>
    </div>
  )
}
