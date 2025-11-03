'use client'

import React, { useEffect, useState } from 'react'
import {
  PieChart,
  Pie,
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { TrendingUp, Package, AlertTriangle, Clock } from 'lucide-react'
import type { InventoryStats } from '@/lib/types'
import { getInventoryStats } from '@/lib/api'

interface InventoryChartsProps {
  refreshTrigger?: number
}

const COLORS = {
  scout: {
    purple: '#4b0082',
    gold: '#ffd700',
    green: '#006400',
  },
  status: {
    low: '#ef4444',
    ok: '#f59e0b',
    good: '#22c55e',
  },
  chart: [
    '#4b0082', // Purple
    '#0ea5e9', // Blue
    '#22c55e', // Green
    '#f59e0b', // Orange
    '#ec4899', // Pink
    '#8b5cf6', // Violet
    '#14b8a6', // Teal
    '#f97316', // Orange-red
  ],
}

const InventoryCharts: React.FC<InventoryChartsProps> = ({ refreshTrigger = 0 }) => {
  const [stats, setStats] = useState<InventoryStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadStats()
  }, [refreshTrigger])

  const loadStats = async () => {
    setLoading(true)
    setError(null)
    const response = await getInventoryStats()
    if (response.success && response.data) {
      setStats(response.data)
    } else {
      setError(response.error || 'Failed to load statistics')
    }
    setLoading(false)
  }

  // Prepare data for category pie chart
  const categoryData = stats
    ? Object.entries(stats.categories).map(([name, data]) => ({
        name,
        value: data.quantity,
        count: data.count,
      }))
    : []

  // Prepare data for top badges bar chart
  const topBadgesData = stats?.recent_updates
    ? stats.recent_updates
        .slice(0, 10)
        .map((update) => ({
          name: update.badge?.name || 'Unknown',
          quantity: update.new_quantity,
          badge_id: update.badge_id,
        }))
    : []

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-AU', {
      month: 'short',
      day: 'numeric',
    })
  }

  // Custom tooltip for pie chart
  const CategoryTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900">{payload[0].name}</p>
          <p className="text-sm text-gray-600">
            Total Quantity: <span className="font-semibold">{payload[0].value}</span>
          </p>
          <p className="text-sm text-gray-600">
            Badge Types: <span className="font-semibold">{payload[0].payload.count}</span>
          </p>
        </div>
      )
    }
    return null
  }

  // Custom tooltip for bar chart
  const QuantityTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900">{payload[0].payload.name}</p>
          <p className="text-sm text-gray-600">
            Quantity: <span className="font-semibold">{payload[0].value}</span>
          </p>
        </div>
      )
    }
    return null
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-scout-purple" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
      </div>
    )
  }

  if (!stats) {
    return null
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Badges */}
        <div className="bg-gradient-to-br from-scout-purple to-purple-900 text-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <Package className="w-8 h-8 opacity-80" />
            <TrendingUp className="w-5 h-5 opacity-60" />
          </div>
          <p className="text-sm opacity-90 mb-1">Total Badge Types</p>
          <p className="text-4xl font-bold">{stats.total_badges}</p>
        </div>

        {/* Total Quantity */}
        <div className="bg-gradient-to-br from-primary-500 to-primary-700 text-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <Package className="w-8 h-8 opacity-80" />
            <TrendingUp className="w-5 h-5 opacity-60" />
          </div>
          <p className="text-sm opacity-90 mb-1">Total Quantity</p>
          <p className="text-4xl font-bold">{stats.total_quantity}</p>
        </div>

        {/* Low Stock Count */}
        <div className="bg-gradient-to-br from-orange-500 to-red-600 text-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <AlertTriangle className="w-8 h-8 opacity-80" />
            <span className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded-full">
              Alert
            </span>
          </div>
          <p className="text-sm opacity-90 mb-1">Low Stock Items</p>
          <p className="text-4xl font-bold">{stats.low_stock_count}</p>
        </div>

        {/* Last Updated */}
        <div className="bg-gradient-to-br from-green-500 to-emerald-700 text-white rounded-lg p-6 shadow-lg">
          <div className="flex items-center justify-between mb-2">
            <Clock className="w-8 h-8 opacity-80" />
          </div>
          <p className="text-sm opacity-90 mb-1">Last Updated</p>
          <p className="text-lg font-semibold">
            {stats.recent_updates && stats.recent_updates.length > 0
              ? formatDate(stats.recent_updates[0].created_at)
              : 'Never'}
          </p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Pie Chart */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Inventory by Category
          </h3>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS.chart[index % COLORS.chart.length]}
                    />
                  ))}
                </Pie>
                <Tooltip content={<CategoryTooltip />} />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  formatter={(value) => (
                    <span className="text-sm text-gray-700">{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-500">
              <p>No category data available</p>
            </div>
          )}
        </div>

        {/* Stock Levels Bar Chart */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Recent Updates (Top 10)
          </h3>
          {topBadgesData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={topBadgesData}
                margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip content={<QuantityTooltip />} />
                <Bar dataKey="quantity" radius={[8, 8, 0, 0]}>
                  {topBadgesData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS.chart[index % COLORS.chart.length]}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-500">
              <p>No stock data available</p>
            </div>
          )}
        </div>
      </div>

      {/* Category Breakdown Table */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Category Breakdown</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Badge Types
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg per Badge
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {categoryData.length > 0 ? (
                categoryData.map((category, index) => (
                  <tr key={category.name} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{
                            backgroundColor: COLORS.chart[index % COLORS.chart.length],
                          }}
                        />
                        <span className="font-medium text-gray-900">
                          {category.name}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                      {category.count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="font-semibold text-gray-900">
                        {category.value}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                      {(category.value / category.count).toFixed(1)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                    No category data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Activity */}
      {stats.recent_updates && stats.recent_updates.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
          </div>
          <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
            {stats.recent_updates.slice(0, 10).map((update) => (
              <div key={update.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      {update.badge?.name || 'Unknown Badge'}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {update.adjustment_type === 'scan' && 'Updated from scan'}
                      {update.adjustment_type === 'manual' && 'Manual adjustment'}
                      {update.adjustment_type === 'correction' && 'Corrected'}
                      {update.quantity_change > 0 ? (
                        <span className="text-green-600 font-semibold ml-2">
                          +{update.quantity_change}
                        </span>
                      ) : (
                        <span className="text-red-600 font-semibold ml-2">
                          {update.quantity_change}
                        </span>
                      )}
                    </p>
                    {update.notes && (
                      <p className="text-xs text-gray-500 mt-1">{update.notes}</p>
                    )}
                  </div>
                  <div className="text-right ml-4">
                    <p className="text-sm text-gray-900 font-semibold">
                      {update.new_quantity}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatDate(update.created_at)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default InventoryCharts
