'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import ResultsReview from '@/components/ResultsReview'
import { getScan, getScanDetections, updateInventory } from '@/lib/api'
import type { Scan, BadgeDetection, ScanImage } from '@/lib/types'
import { CheckCircle, Package, AlertCircle } from 'lucide-react'

export default function ResultsPage() {
  const router = useRouter()
  const params = useParams()
  const scanId = params.id as string

  const [scan, setScan] = useState<Scan | null>(null)
  const [detections, setDetections] = useState<BadgeDetection[]>([])
  const [images, setImages] = useState<ScanImage[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    if (scanId) {
      loadResults()
    }
  }, [scanId])

  const loadResults = async () => {
    setLoading(true)
    setError(null)

    try {
      // Load scan details
      const scanResponse = await getScan(scanId)
      if (!scanResponse.success || !scanResponse.data) {
        throw new Error(scanResponse.error || 'Failed to load scan')
      }

      setScan(scanResponse.data)

      // Load detections
      const detectionsResponse = await getScanDetections(scanId)
      if (!detectionsResponse.success || !detectionsResponse.data) {
        throw new Error(detectionsResponse.error || 'Failed to load detections')
      }

      setDetections(detectionsResponse.data)

      // TODO: Load scan images from API
      // For now, using mock data
      setImages([])
    } catch (err: any) {
      setError(err.message || 'Failed to load results')
    } finally {
      setLoading(false)
    }
  }

  const handleCorrection = async (detectionId: string, badgeId: string) => {
    // Update the detection with the corrected badge
    setDetections((prev) =>
      prev.map((d) =>
        d.id === detectionId
          ? { ...d, badge_id: badgeId, verified: true }
          : d
      )
    )
  }

  const handleVerify = async (detectionId: string, verified: boolean) => {
    // Update the detection verification status
    setDetections((prev) =>
      prev.map((d) =>
        d.id === detectionId ? { ...d, verified } : d
      )
    )
  }

  const handleUpdateInventory = async () => {
    setUpdating(true)
    setError(null)

    try {
      // Group detections by badge
      const badgeTotals: { [badgeId: string]: number } = {}
      detections.forEach((detection) => {
        if (detection.badge_id && detection.verified) {
          badgeTotals[detection.badge_id] =
            (badgeTotals[detection.badge_id] || 0) + detection.quantity
        }
      })

      // Update inventory for each badge
      const updatePromises = Object.entries(badgeTotals).map(([badgeId, quantity]) =>
        updateInventory(badgeId, quantity, `Updated from scan ${scanId}`)
      )

      await Promise.all(updatePromises)

      // Navigate to inventory page
      router.push('/inventory')
    } catch (err: any) {
      setError(err.message || 'Failed to update inventory')
    } finally {
      setUpdating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-scout-purple" />
      </div>
    )
  }

  if (error && !scan) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-red-900 mb-4">Error Loading Results</h2>
          <p className="text-red-800 mb-6">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-3 bg-scout-purple text-white rounded-lg hover:bg-purple-900 transition-colors font-semibold"
          >
            Return to Home
          </button>
        </div>
      </div>
    )
  }

  const verifiedCount = detections.filter((d) => d.verified).length
  const needsReviewCount = detections.filter((d) => !d.verified).length

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Scan Results - Review & Correct
            </h1>
            <p className="text-gray-600">
              Review the detected badges and make any necessary corrections before updating
              inventory
            </p>
          </div>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            New Scan
          </button>
        </div>

        {/* Summary Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <Package className="w-5 h-5" />
              <span className="text-sm font-medium">Total Detections</span>
            </div>
            <p className="text-3xl font-bold text-scout-purple">{detections.length}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm font-medium">Verified</span>
            </div>
            <p className="text-3xl font-bold text-green-600">{verifiedCount}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm font-medium">Needs Review</span>
            </div>
            <p className="text-3xl font-bold text-orange-600">{needsReviewCount}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <Package className="w-5 h-5" />
              <span className="text-sm font-medium">Total Badges</span>
            </div>
            <p className="text-3xl font-bold text-primary-600">
              {detections.reduce((sum, d) => sum + d.quantity, 0)}
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      <ResultsReview
        scanId={scanId}
        detections={detections}
        images={images}
        onCorrection={handleCorrection}
        onVerify={handleVerify}
      />

      {/* Action Buttons */}
      <div className="mt-8 bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">Ready to update inventory?</h3>
            <p className="text-sm text-gray-600">
              {verifiedCount} of {detections.length} detections are verified and ready to be added
              to inventory
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => router.push('/inventory')}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-semibold"
            >
              Cancel
            </button>
            <button
              onClick={handleUpdateInventory}
              disabled={updating || verifiedCount === 0}
              className="px-6 py-3 bg-scout-purple text-white rounded-lg hover:bg-purple-900 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <CheckCircle className="w-5 h-5" />
              {updating ? 'Updating...' : `Update Inventory (${verifiedCount} items)`}
            </button>
          </div>
        </div>
      </div>

      {scan && (
        <div className="mt-6 bg-gray-50 rounded-lg border border-gray-200 p-4 text-sm text-gray-600">
          <p>
            Scan ID: <span className="font-mono">{scan.id}</span> | Completed:{' '}
            {scan.completed_at ? new Date(scan.completed_at).toLocaleString('en-AU') : 'N/A'}
          </p>
        </div>
      )}
    </div>
  )
}
