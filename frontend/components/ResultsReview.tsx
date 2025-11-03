'use client'

import React, { useState, useEffect } from 'react'
import { Check, X, Edit2, Search, AlertCircle, CheckCircle2, AlertTriangle } from 'lucide-react'
import type { BadgeDetection, Badge, ScanImage } from '@/lib/types'
import { getBadges, searchBadges } from '@/lib/api'

interface ResultsReviewProps {
  scanId: string
  detections: BadgeDetection[]
  images: ScanImage[]
  onCorrection?: (detectionId: string, badgeId: string) => void
  onVerify?: (detectionId: string, verified: boolean) => void
}

interface GroupedDetection {
  image: ScanImage
  detections: BadgeDetection[]
}

const ResultsReview: React.FC<ResultsReviewProps> = ({
  scanId,
  detections,
  images,
  onCorrection,
  onVerify,
}) => {
  const [groupedData, setGroupedData] = useState<GroupedDetection[]>([])
  const [editingDetection, setEditingDetection] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<Badge[]>([])
  const [allBadges, setAllBadges] = useState<Badge[]>([])
  const [loading, setLoading] = useState(false)

  // Group detections by image
  useEffect(() => {
    const grouped = images.map((image) => ({
      image,
      detections: detections.filter((d) => d.scan_image_id === image.id),
    }))
    setGroupedData(grouped)
  }, [images, detections])

  // Load all badges on mount
  useEffect(() => {
    const loadBadges = async () => {
      setLoading(true)
      const response = await getBadges()
      if (response.success && response.data) {
        setAllBadges(response.data)
      }
      setLoading(false)
    }
    loadBadges()
  }, [])

  // Search badges when query changes
  useEffect(() => {
    const performSearch = async () => {
      if (searchQuery.length < 2) {
        setSearchResults([])
        return
      }

      const response = await searchBadges(searchQuery)
      if (response.success && response.data) {
        setSearchResults(response.data)
      }
    }

    const debounce = setTimeout(performSearch, 300)
    return () => clearTimeout(debounce)
  }, [searchQuery])

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 90) return 'bg-green-100 text-green-800 border-green-300'
    if (confidence >= 70) return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    return 'bg-red-100 text-red-800 border-red-300'
  }

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 90) return <CheckCircle2 className="w-4 h-4" />
    if (confidence >= 70) return <AlertTriangle className="w-4 h-4" />
    return <AlertCircle className="w-4 h-4" />
  }

  const handleEdit = (detectionId: string) => {
    setEditingDetection(detectionId)
    setSearchQuery('')
  }

  const handleSelectBadge = (detectionId: string, badge: Badge) => {
    if (onCorrection) {
      onCorrection(detectionId, badge.id)
    }
    setEditingDetection(null)
    setSearchQuery('')
  }

  const handleVerify = (detectionId: string, verified: boolean) => {
    if (onVerify) {
      onVerify(detectionId, verified)
    }
  }

  const getTotalBadges = (): number => {
    return detections.reduce((sum, d) => sum + d.quantity, 0)
  }

  const getUniqueBadges = (): number => {
    const unique = new Set(detections.map((d) => d.badge_id).filter(Boolean))
    return unique.size
  }

  const getLowConfidenceCount = (): number => {
    return detections.filter((d) => d.confidence < 70).length
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <p className="text-sm text-gray-600 mb-1">Total Badges Detected</p>
          <p className="text-3xl font-bold text-scout-purple">{getTotalBadges()}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <p className="text-sm text-gray-600 mb-1">Unique Badge Types</p>
          <p className="text-3xl font-bold text-primary-600">{getUniqueBadges()}</p>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
          <p className="text-sm text-gray-600 mb-1">Needs Review</p>
          <p className="text-3xl font-bold text-orange-600">{getLowConfidenceCount()}</p>
        </div>
      </div>

      {/* Detection Results */}
      <div className="space-y-6">
        <h3 className="text-xl font-semibold text-gray-900">
          Detection Results ({images.length} images)
        </h3>

        {groupedData.map((group) => (
          <div
            key={group.image.id}
            className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden"
          >
            {/* Image Header */}
            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gray-200 rounded overflow-hidden flex-shrink-0">
                    <img
                      src={group.image.file_path}
                      alt={group.image.file_name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">
                      {group.image.file_name}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {group.detections.length} badge{group.detections.length !== 1 ? 's' : ''} detected
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">
                    {new Date(group.image.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Detections List */}
            <div className="divide-y divide-gray-200">
              {group.detections.length === 0 ? (
                <div className="px-4 py-8 text-center">
                  <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600">No badges detected in this image</p>
                </div>
              ) : (
                group.detections.map((detection) => (
                  <div key={detection.id} className="px-4 py-4">
                    {editingDetection === detection.id ? (
                      // Edit Mode
                      <div className="space-y-3">
                        <div className="flex items-center gap-2">
                          <Search className="w-5 h-5 text-gray-400" />
                          <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search for correct badge..."
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-scout-purple focus:border-transparent"
                            autoFocus
                          />
                          <button
                            onClick={() => setEditingDetection(null)}
                            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
                          >
                            <X className="w-5 h-5" />
                          </button>
                        </div>
                        {searchResults.length > 0 && (
                          <div className="bg-gray-50 rounded-lg border border-gray-200 max-h-60 overflow-y-auto">
                            {searchResults.map((badge) => (
                              <button
                                key={badge.id}
                                onClick={() => handleSelectBadge(detection.id, badge)}
                                className="w-full px-4 py-3 text-left hover:bg-white transition-colors flex items-center gap-3 border-b border-gray-200 last:border-b-0"
                              >
                                {badge.image_path && (
                                  <div className="w-10 h-10 bg-gray-200 rounded overflow-hidden flex-shrink-0">
                                    <img
                                      src={badge.image_path}
                                      alt={badge.name}
                                      className="w-full h-full object-cover"
                                    />
                                  </div>
                                )}
                                <div>
                                  <p className="font-medium text-gray-900">{badge.name}</p>
                                  <p className="text-xs text-gray-600">{badge.category}</p>
                                </div>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    ) : (
                      // View Mode
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-center gap-3 flex-1">
                          {detection.badge?.image_path && (
                            <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0 border-2 border-gray-200">
                              <img
                                src={detection.badge.image_path}
                                alt={detection.badge.name}
                                className="w-full h-full object-cover"
                              />
                            </div>
                          )}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h5 className="font-semibold text-gray-900">
                                {detection.badge?.name || detection.detected_name}
                              </h5>
                              {detection.verified && (
                                <CheckCircle2 className="w-5 h-5 text-green-600" />
                              )}
                            </div>
                            <div className="flex items-center gap-3 flex-wrap">
                              <span
                                className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${getConfidenceColor(
                                  detection.confidence
                                )}`}
                              >
                                {getConfidenceIcon(detection.confidence)}
                                {detection.confidence.toFixed(1)}% confidence
                              </span>
                              <span className="text-sm text-gray-600">
                                Quantity: <span className="font-semibold">{detection.quantity}</span>
                              </span>
                              {detection.badge?.category && (
                                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                  {detection.badge.category}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {!detection.verified && (
                            <button
                              onClick={() => handleVerify(detection.id, true)}
                              className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title="Mark as correct"
                            >
                              <Check className="w-5 h-5" />
                            </button>
                          )}
                          <button
                            onClick={() => handleEdit(detection.id)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Edit detection"
                          >
                            <Edit2 className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleVerify(detection.id, false)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Mark as incorrect"
                          >
                            <X className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {groupedData.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
          <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No Results Yet
          </h3>
          <p className="text-gray-600">
            Upload and process images to see badge detections here.
          </p>
        </div>
      )}

      {/* Help Text */}
      {detections.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">
            Review Tips
          </h4>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>Green badges have high confidence (90%+) and are likely correct</li>
            <li>Yellow badges (70-90%) should be reviewed for accuracy</li>
            <li>Red badges (&lt;70%) need verification or correction</li>
            <li>Click the edit icon to search for the correct badge if needed</li>
            <li>Mark verified badges with the check icon to confirm accuracy</li>
          </ul>
        </div>
      )}
    </div>
  )
}

export default ResultsReview
