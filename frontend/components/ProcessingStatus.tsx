'use client'

import React, { useEffect, useState } from 'react'
import { CheckCircle, XCircle, Loader2, X, AlertTriangle, Clock } from 'lucide-react'
import type { ProcessingProgress, ScanImage } from '@/lib/types'

interface ProcessingStatusProps {
  scanId: string
  onComplete?: (scanId: string) => void
  onError?: (error: string) => void
  onCancel?: () => void
  pollInterval?: number
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  scanId,
  onComplete,
  onError,
  onCancel,
  pollInterval = 1000, // Poll every second
}) => {
  const [progress, setProgress] = useState<ProcessingProgress | null>(null)
  const [currentImage, setCurrentImage] = useState<ScanImage | null>(null)
  const [status, setStatus] = useState<'processing' | 'completed' | 'failed' | 'cancelled'>(
    'processing'
  )
  const [error, setError] = useState<string | null>(null)
  const [startTime] = useState(Date.now())
  const [elapsedTime, setElapsedTime] = useState(0)

  useEffect(() => {
    let isMounted = true
    let intervalId: NodeJS.Timeout

    const fetchProgress = async () => {
      try {
        // This would call the actual API - for now using placeholder
        // const response = await getProcessingProgress(scanId)

        // Simulated progress for demonstration
        setProgress((prev) => {
          const current = prev?.current_image || 0
          const total = prev?.total_images || 10

          if (current >= total) {
            if (isMounted) {
              setStatus('completed')
              if (onComplete) onComplete(scanId)
            }
            return prev
          }

          return {
            scan_id: scanId,
            current_image: current + 1,
            total_images: total,
            percentage: Math.round(((current + 1) / total) * 100),
            current_image_name: `badge_image_${current + 1}.jpg`,
            estimated_time_remaining: Math.max(0, (total - current - 1) * 3),
            status: 'processing',
          }
        })
      } catch (err: any) {
        if (isMounted) {
          setStatus('failed')
          setError(err.message || 'Failed to fetch processing status')
          if (onError) onError(err.message)
        }
      }
    }

    if (status === 'processing') {
      // Initial fetch
      fetchProgress()

      // Set up polling
      intervalId = setInterval(fetchProgress, pollInterval)
    }

    return () => {
      isMounted = false
      if (intervalId) clearInterval(intervalId)
    }
  }, [scanId, status, pollInterval, onComplete, onError])

  // Update elapsed time
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000))
    }, 1000)

    return () => clearInterval(timer)
  }, [startTime])

  const handleCancel = () => {
    setStatus('cancelled')
    if (onCancel) onCancel()
  }

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return <Loader2 className="w-8 h-8 text-scout-purple animate-spin" />
      case 'completed':
        return <CheckCircle className="w-8 h-8 text-green-500" />
      case 'failed':
        return <XCircle className="w-8 h-8 text-red-500" />
      case 'cancelled':
        return <AlertTriangle className="w-8 h-8 text-orange-500" />
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'processing':
        return 'bg-blue-50 border-blue-200'
      case 'completed':
        return 'bg-green-50 border-green-200'
      case 'failed':
        return 'bg-red-50 border-red-200'
      case 'cancelled':
        return 'bg-orange-50 border-orange-200'
    }
  }

  const getStatusMessage = () => {
    switch (status) {
      case 'processing':
        return 'Processing badge images...'
      case 'completed':
        return 'Processing complete!'
      case 'failed':
        return 'Processing failed'
      case 'cancelled':
        return 'Processing cancelled'
    }
  }

  if (!progress && status === 'processing') {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-8 h-8 text-scout-purple animate-spin" />
        <span className="ml-3 text-gray-600">Initializing...</span>
      </div>
    )
  }

  return (
    <div className={`border rounded-lg p-6 ${getStatusColor()} transition-all duration-300`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {getStatusMessage()}
            </h3>
            {status === 'processing' && progress && (
              <p className="text-sm text-gray-600 mt-1">
                Processing image {progress.current_image} of {progress.total_images}
              </p>
            )}
          </div>
        </div>
        {status === 'processing' && onCancel && (
          <button
            onClick={handleCancel}
            className="p-2 hover:bg-red-100 rounded-full transition-colors"
            aria-label="Cancel processing"
          >
            <X className="w-5 h-5 text-red-600" />
          </button>
        )}
      </div>

      {/* Progress Bar */}
      {progress && status === 'processing' && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Progress: {progress.percentage}%
            </span>
            <span className="text-sm text-gray-600">
              {progress.current_image}/{progress.total_images} images
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-scout-purple to-purple-600 h-3 rounded-full transition-all duration-500 ease-out relative overflow-hidden"
              style={{ width: `${progress.percentage}%` }}
            >
              <div className="absolute inset-0 bg-white opacity-20 animate-pulse" />
            </div>
          </div>
        </div>
      )}

      {/* Current Image Info */}
      {progress && status === 'processing' && progress.current_image_name && (
        <div className="bg-white bg-opacity-60 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center overflow-hidden">
              {currentImage?.file_path ? (
                <img
                  src={currentImage.file_path}
                  alt="Current image"
                  className="w-full h-full object-cover"
                />
              ) : (
                <Loader2 className="w-6 h-6 text-gray-400 animate-spin" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {progress.current_image_name}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Detecting badges with AI...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Time Information */}
      {progress && status === 'processing' && (
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-white bg-opacity-60 rounded-lg p-3">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <Clock className="w-4 h-4" />
              <span className="text-xs font-medium">Elapsed Time</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">
              {formatTime(elapsedTime)}
            </p>
          </div>
          <div className="bg-white bg-opacity-60 rounded-lg p-3">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <Clock className="w-4 h-4" />
              <span className="text-xs font-medium">Est. Remaining</span>
            </div>
            <p className="text-lg font-semibold text-gray-900">
              {progress.estimated_time_remaining
                ? formatTime(progress.estimated_time_remaining)
                : 'Calculating...'}
            </p>
          </div>
        </div>
      )}

      {/* Error Display */}
      {status === 'failed' && error && (
        <div className="bg-white bg-opacity-80 rounded-lg p-4 border border-red-300">
          <p className="text-sm text-red-800">{error}</p>
          <p className="text-xs text-red-600 mt-2">
            Please try again or contact support if the problem persists.
          </p>
        </div>
      )}

      {/* Completed Message */}
      {status === 'completed' && progress && (
        <div className="bg-white bg-opacity-80 rounded-lg p-4 border border-green-300">
          <p className="text-sm text-green-800 font-medium">
            Successfully processed {progress.total_images} images!
          </p>
          <p className="text-xs text-green-700 mt-1">
            Total time: {formatTime(elapsedTime)}
          </p>
        </div>
      )}

      {/* Cancelled Message */}
      {status === 'cancelled' && (
        <div className="bg-white bg-opacity-80 rounded-lg p-4 border border-orange-300">
          <p className="text-sm text-orange-800">
            Processing was cancelled. You can start a new scan anytime.
          </p>
        </div>
      )}

      {/* Status Messages */}
      {status === 'processing' && (
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Please keep this window open while processing...
          </p>
        </div>
      )}
    </div>
  )
}

export default ProcessingStatus
