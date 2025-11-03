'use client'

import React, { useState, useEffect, useMemo } from 'react'
import {
  Search,
  Filter,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Plus,
  Minus,
  Eye,
  Package,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react'
import type { Inventory, Badge } from '@/lib/types'
import { getInventory, adjustInventory } from '@/lib/api'

interface InventoryDashboardProps {
  onAdjust?: (badgeId: string, newQuantity: number) => void
  onViewDetails?: (badgeId: string) => void
}

type SortField = 'name' | 'quantity' | 'status' | 'category' | 'last_updated'
type SortDirection = 'asc' | 'desc'

const InventoryDashboard: React.FC<InventoryDashboardProps> = ({
  onAdjust,
  onViewDetails,
}) => {
  const [inventory, setInventory] = useState<Inventory[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  // Sorting
  const [sortField, setSortField] = useState<SortField>('name')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  // Adjustment modal
  const [adjustingItem, setAdjustingItem] = useState<Inventory | null>(null)
  const [adjustmentValue, setAdjustmentValue] = useState<number>(0)

  // Load inventory on mount
  useEffect(() => {
    loadInventory()
  }, [])

  const loadInventory = async () => {
    setLoading(true)
    setError(null)
    const response = await getInventory()
    if (response.success && response.data) {
      setInventory(response.data)
    } else {
      setError(response.error || 'Failed to load inventory')
    }
    setLoading(false)
  }

  // Get unique categories
  const categories = useMemo(() => {
    const cats = new Set(inventory.map((item) => item.badge?.category).filter(Boolean))
    return Array.from(cats).sort()
  }, [inventory])

  // Filter and sort inventory
  const filteredInventory = useMemo(() => {
    let filtered = [...inventory]

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter((item) =>
        item.badge?.name.toLowerCase().includes(query)
      )
    }

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter((item) => item.badge?.category === selectedCategory)
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((item) => item.status === statusFilter)
    }

    // Sort
    filtered.sort((a, b) => {
      let comparison = 0

      switch (sortField) {
        case 'name':
          comparison = (a.badge?.name || '').localeCompare(b.badge?.name || '')
          break
        case 'quantity':
          comparison = a.quantity - b.quantity
          break
        case 'status':
          const statusOrder = { low: 0, ok: 1, good: 2 }
          comparison = statusOrder[a.status] - statusOrder[b.status]
          break
        case 'category':
          comparison = (a.badge?.category || '').localeCompare(b.badge?.category || '')
          break
        case 'last_updated':
          comparison =
            new Date(a.last_updated || 0).getTime() -
            new Date(b.last_updated || 0).getTime()
          break
      }

      return sortDirection === 'asc' ? comparison : -comparison
    })

    return filtered
  }, [inventory, searchQuery, selectedCategory, statusFilter, sortField, sortDirection])

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return <ArrowUpDown className="w-4 h-4 text-gray-400" />
    return sortDirection === 'asc' ? (
      <ArrowUp className="w-4 h-4 text-scout-purple" />
    ) : (
      <ArrowDown className="w-4 h-4 text-scout-purple" />
    )
  }

  const getStatusBadge = (item: Inventory) => {
    if (item.status === 'low') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-300">
          <AlertTriangle className="w-3 h-3" />
          Low Stock
        </span>
      )
    } else if (item.status === 'ok') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 border border-yellow-300">
          <Package className="w-3 h-3" />
          Adequate
        </span>
      )
    } else {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-300">
          <CheckCircle className="w-3 h-3" />
          Well Stocked
        </span>
      )
    }
  }

  const handleAdjustClick = (item: Inventory) => {
    setAdjustingItem(item)
    setAdjustmentValue(0)
  }

  const handleAdjustSubmit = async () => {
    if (!adjustingItem || adjustmentValue === 0) return

    const response = await adjustInventory(
      adjustingItem.badge_id,
      adjustmentValue,
      'Manual adjustment from dashboard'
    )

    if (response.success) {
      // Reload inventory
      await loadInventory()
      setAdjustingItem(null)
      setAdjustmentValue(0)
      if (onAdjust) {
        onAdjust(adjustingItem.badge_id, adjustingItem.quantity + adjustmentValue)
      }
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
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

  return (
    <div className="space-y-6">
      {/* Header & Filters */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search badges..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-scout-purple focus:border-transparent"
            />
          </div>

          {/* Category Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-scout-purple focus:border-transparent appearance-none bg-white min-w-[160px]"
            >
              <option value="all">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-scout-purple focus:border-transparent appearance-none bg-white min-w-[140px]"
          >
            <option value="all">All Status</option>
            <option value="low">Low Stock</option>
            <option value="ok">Adequate</option>
            <option value="good">Well Stocked</option>
          </select>
        </div>

        {/* Results count */}
        <p className="text-sm text-gray-600">
          Showing {filteredInventory.length} of {inventory.length} items
        </p>
      </div>

      {/* Desktop Table */}
      <div className="hidden md:block bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left">
                  <button
                    onClick={() => handleSort('name')}
                    className="flex items-center gap-2 font-semibold text-gray-700 hover:text-scout-purple"
                  >
                    Badge
                    {getSortIcon('name')}
                  </button>
                </th>
                <th className="px-4 py-3 text-left">
                  <button
                    onClick={() => handleSort('category')}
                    className="flex items-center gap-2 font-semibold text-gray-700 hover:text-scout-purple"
                  >
                    Category
                    {getSortIcon('category')}
                  </button>
                </th>
                <th className="px-4 py-3 text-left">
                  <button
                    onClick={() => handleSort('quantity')}
                    className="flex items-center gap-2 font-semibold text-gray-700 hover:text-scout-purple"
                  >
                    Quantity
                    {getSortIcon('quantity')}
                  </button>
                </th>
                <th className="px-4 py-3 text-left">
                  <button
                    onClick={() => handleSort('status')}
                    className="flex items-center gap-2 font-semibold text-gray-700 hover:text-scout-purple"
                  >
                    Status
                    {getSortIcon('status')}
                  </button>
                </th>
                <th className="px-4 py-3 text-left">
                  <button
                    onClick={() => handleSort('last_updated')}
                    className="flex items-center gap-2 font-semibold text-gray-700 hover:text-scout-purple"
                  >
                    Last Updated
                    {getSortIcon('last_updated')}
                  </button>
                </th>
                <th className="px-4 py-3 text-right font-semibold text-gray-700">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredInventory.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center">
                    <Package className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-600">No inventory items found</p>
                  </td>
                </tr>
              ) : (
                filteredInventory.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        {item.badge?.image_path && (
                          <div className="w-12 h-12 bg-gray-100 rounded overflow-hidden flex-shrink-0 border border-gray-200">
                            <img
                              src={item.badge.image_path}
                              alt={item.badge.name}
                              className="w-full h-full object-cover"
                            />
                          </div>
                        )}
                        <span className="font-medium text-gray-900">
                          {item.badge?.name || 'Unknown Badge'}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {item.badge?.category || '-'}
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-semibold text-gray-900">{item.quantity}</span>
                      <span className="text-gray-500 text-sm ml-1">
                        / {item.low_stock_threshold}
                      </span>
                    </td>
                    <td className="px-4 py-3">{getStatusBadge(item)}</td>
                    <td className="px-4 py-3 text-gray-700 text-sm">
                      {formatDate(item.last_updated)}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleAdjustClick(item)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Adjust quantity"
                        >
                          <Plus className="w-4 h-4" />
                        </button>
                        {onViewDetails && (
                          <button
                            onClick={() => onViewDetails(item.badge_id)}
                            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                            title="View details"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden space-y-4">
        {filteredInventory.length === 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
            <Package className="w-12 h-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600">No inventory items found</p>
          </div>
        ) : (
          filteredInventory.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-lg border border-gray-200 shadow-sm p-4"
            >
              <div className="flex items-start gap-3 mb-3">
                {item.badge?.image_path && (
                  <div className="w-16 h-16 bg-gray-100 rounded overflow-hidden flex-shrink-0 border border-gray-200">
                    <img
                      src={item.badge.image_path}
                      alt={item.badge.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-gray-900 mb-1">
                    {item.badge?.name || 'Unknown Badge'}
                  </h4>
                  <p className="text-sm text-gray-600 mb-2">
                    {item.badge?.category || '-'}
                  </p>
                  {getStatusBadge(item)}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 mb-3">
                <div>
                  <p className="text-xs text-gray-600 mb-1">Quantity</p>
                  <p className="font-semibold text-gray-900">
                    {item.quantity}{' '}
                    <span className="text-gray-500 text-sm">
                      / {item.low_stock_threshold}
                    </span>
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-600 mb-1">Last Updated</p>
                  <p className="text-sm text-gray-700">{formatDate(item.last_updated)}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleAdjustClick(item)}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                >
                  Adjust
                </button>
                {onViewDetails && (
                  <button
                    onClick={() => onViewDetails(item.badge_id)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
                  >
                    Details
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Adjustment Modal */}
      {adjustingItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Adjust Inventory
            </h3>
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-1">Badge</p>
              <p className="font-medium text-gray-900">{adjustingItem.badge?.name}</p>
              <p className="text-sm text-gray-600 mt-2">
                Current quantity: <span className="font-semibold">{adjustingItem.quantity}</span>
              </p>
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Adjustment
              </label>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setAdjustmentValue(adjustmentValue - 1)}
                  className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                >
                  <Minus className="w-5 h-5" />
                </button>
                <input
                  type="number"
                  value={adjustmentValue}
                  onChange={(e) => setAdjustmentValue(parseInt(e.target.value) || 0)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-center text-lg font-semibold focus:ring-2 focus:ring-scout-purple focus:border-transparent"
                />
                <button
                  onClick={() => setAdjustmentValue(adjustmentValue + 1)}
                  className="p-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>
              <p className="text-sm text-gray-600 mt-2 text-center">
                New quantity: {adjustingItem.quantity + adjustmentValue}
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setAdjustingItem(null)}
                className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleAdjustSubmit}
                disabled={adjustmentValue === 0}
                className="flex-1 px-4 py-2 bg-scout-purple text-white rounded-lg hover:bg-purple-900 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InventoryDashboard
