'use client'

import React, { useState, useEffect, useMemo } from 'react'
import {
  ShoppingCart,
  ExternalLink,
  Download,
  Copy,
  Check,
  AlertCircle,
  Package,
  DollarSign,
  CheckSquare,
  Square,
} from 'lucide-react'
import type { ShoppingListItem } from '@/lib/types'
import { getShoppingList, exportShoppingList } from '@/lib/api'

interface ShoppingListProps {
  onExport?: (items: ShoppingListItem[]) => void
}

const ShoppingList: React.FC<ShoppingListProps> = ({ onExport }) => {
  const [items, setItems] = useState<ShoppingListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [copied, setCopied] = useState(false)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    loadShoppingList()
  }, [])

  const loadShoppingList = async () => {
    setLoading(true)
    setError(null)
    const response = await getShoppingList()
    if (response.success && response.data) {
      setItems(response.data)
      // Select all items by default
      const allIds = new Set(response.data.map((item) => item.badge_id))
      setSelectedItems(allIds)
    } else {
      setError(response.error || 'Failed to load shopping list')
    }
    setLoading(false)
  }

  const toggleItem = (badgeId: string) => {
    setSelectedItems((prev) => {
      const updated = new Set(prev)
      if (updated.has(badgeId)) {
        updated.delete(badgeId)
      } else {
        updated.add(badgeId)
      }
      return updated
    })
  }

  const toggleAll = () => {
    if (selectedItems.size === items.length) {
      setSelectedItems(new Set())
    } else {
      setSelectedItems(new Set(items.map((item) => item.badge_id)))
    }
  }

  const selectedCount = selectedItems.size
  const totalItems = items.length

  const totalQuantity = useMemo(() => {
    return items
      .filter((item) => selectedItems.has(item.badge_id))
      .reduce((sum, item) => sum + item.recommended_quantity, 0)
  }, [items, selectedItems])

  const getPriorityColor = (priority: 'high' | 'medium' | 'low') => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'low':
        return 'bg-green-100 text-green-800 border-green-300'
    }
  }

  const getPriorityLabel = (priority: 'high' | 'medium' | 'low') => {
    return priority.charAt(0).toUpperCase() + priority.slice(1) + ' Priority'
  }

  const handleCopyToClipboard = async () => {
    const selectedItemsList = items.filter((item) => selectedItems.has(item.badge_id))

    const text = [
      'Scout Badge Shopping List',
      '========================',
      '',
      ...selectedItemsList.map(
        (item) =>
          `• ${item.badge_name} (${item.category})
  Current: ${item.current_quantity} | Recommended: ${item.recommended_quantity}
  Priority: ${item.priority.toUpperCase()}
  ${item.scoutshop_url ? `Link: ${item.scoutshop_url}` : 'No link available'}`
      ),
      '',
      `Total Items: ${selectedCount}`,
      `Total Quantity: ${totalQuantity}`,
      '',
      `Generated: ${new Date().toLocaleString('en-AU')}`,
    ].join('\n')

    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleExport = async () => {
    setExporting(true)
    try {
      const response = await exportShoppingList()
      if (response.success && response.data) {
        // Create a downloadable file
        const blob = new Blob([response.data], { type: 'text/plain' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `shopping-list-${new Date().toISOString().split('T')[0]}.txt`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      }

      if (onExport) {
        const selectedItemsList = items.filter((item) => selectedItems.has(item.badge_id))
        onExport(selectedItemsList)
      }
    } catch (err) {
      console.error('Export failed:', err)
    } finally {
      setExporting(false)
    }
  }

  const handleBuyAll = () => {
    const selectedItemsList = items.filter((item) => selectedItems.has(item.badge_id))
    // Open all ScoutShop links in new tabs (be careful with popup blockers)
    selectedItemsList.forEach((item) => {
      if (item.scoutshop_url) {
        window.open(item.scoutshop_url, '_blank')
      }
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
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <ShoppingCart className="w-7 h-7 text-scout-purple" />
            Shopping List
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Low stock badges that need to be ordered
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCopyToClipboard}
            disabled={selectedCount === 0}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy List
              </>
            )}
          </button>
          <button
            onClick={handleExport}
            disabled={selectedCount === 0 || exporting}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4" />
            {exporting ? 'Exporting...' : 'Export'}
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <Package className="w-5 h-5" />
            <span className="text-sm font-medium">Selected Items</span>
          </div>
          <p className="text-3xl font-bold text-scout-purple">
            {selectedCount}{' '}
            <span className="text-lg text-gray-500">/ {totalItems}</span>
          </p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <ShoppingCart className="w-5 h-5" />
            <span className="text-sm font-medium">Total Quantity</span>
          </div>
          <p className="text-3xl font-bold text-primary-600">{totalQuantity}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <div className="flex items-center gap-2 text-gray-600 mb-1">
            <AlertTriangle className="w-5 h-5" />
            <span className="text-sm font-medium">High Priority</span>
          </div>
          <p className="text-3xl font-bold text-red-600">
            {items.filter((item) => item.priority === 'high').length}
          </p>
        </div>
      </div>

      {/* Actions Bar */}
      {items.length > 0 && (
        <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <button
              onClick={toggleAll}
              className="flex items-center gap-2 text-scout-purple hover:text-purple-900 font-medium"
            >
              {selectedItems.size === items.length ? (
                <>
                  <CheckSquare className="w-5 h-5" />
                  Deselect All
                </>
              ) : (
                <>
                  <Square className="w-5 h-5" />
                  Select All
                </>
              )}
            </button>
            <button
              onClick={handleBuyAll}
              disabled={selectedCount === 0}
              className="px-6 py-2 bg-scout-purple text-white rounded-lg hover:bg-purple-900 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
            >
              <ExternalLink className="w-4 h-4" />
              Open Selected in ScoutShop ({selectedCount})
            </button>
          </div>
        </div>
      )}

      {/* Shopping List Items */}
      <div className="space-y-3">
        {items.length === 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
            <CheckSquare className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              All Stocked Up!
            </h3>
            <p className="text-gray-600">
              No badges are currently low on stock. Great job keeping your inventory full!
            </p>
          </div>
        ) : (
          items.map((item) => (
            <div
              key={item.badge_id}
              className={`bg-white rounded-lg border-2 transition-all duration-200 ${
                selectedItems.has(item.badge_id)
                  ? 'border-scout-purple shadow-md'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="p-4">
                <div className="flex items-start gap-4">
                  {/* Checkbox */}
                  <button
                    onClick={() => toggleItem(item.badge_id)}
                    className="flex-shrink-0 mt-1"
                  >
                    {selectedItems.has(item.badge_id) ? (
                      <CheckSquare className="w-6 h-6 text-scout-purple" />
                    ) : (
                      <Square className="w-6 h-6 text-gray-400 hover:text-scout-purple" />
                    )}
                  </button>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {item.badge_name}
                        </h3>
                        <p className="text-sm text-gray-600">{item.category}</p>
                      </div>
                      <span
                        className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(
                          item.priority
                        )}`}
                      >
                        {getPriorityLabel(item.priority)}
                      </span>
                    </div>

                    {/* Stock Info */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-xs text-gray-600 mb-1">Current Stock</p>
                        <p className="text-lg font-bold text-red-600">
                          {item.current_quantity}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600 mb-1">Recommended Order</p>
                        <p className="text-lg font-bold text-green-600">
                          {item.recommended_quantity}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600 mb-1">After Order</p>
                        <p className="text-lg font-bold text-gray-900">
                          {item.current_quantity + item.recommended_quantity}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-600 mb-1">Priority</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {item.priority.toUpperCase()}
                        </p>
                      </div>
                    </div>

                    {/* Buy Button */}
                    {item.scoutshop_url ? (
                      <a
                        href={item.scoutshop_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-4 py-2 bg-scout-gold text-gray-900 rounded-lg hover:bg-yellow-500 transition-colors font-medium text-sm"
                      >
                        <ShoppingCart className="w-4 h-4" />
                        Buy Now at ScoutShop
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : (
                      <div className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-500 rounded-lg text-sm">
                        <AlertCircle className="w-4 h-4" />
                        ScoutShop link not available
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Info Box */}
      {items.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-blue-900 mb-2 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            Shopping Tips
          </h4>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>High priority items should be ordered immediately</li>
            <li>Recommended quantities are based on your current stock levels</li>
            <li>
              Use the "Copy List" button to share with other leaders or paste into
              emails
            </li>
            <li>Opening multiple ScoutShop tabs may trigger popup blockers</li>
            <li>Check ScoutShop for current pricing and availability</li>
          </ul>
        </div>
      )}
    </div>
  )
}

export default ShoppingList
