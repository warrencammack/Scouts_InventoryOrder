'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import ProcessingStatus from '@/components/ProcessingStatus'
import { getScan } from '@/lib/api'
import type { Scan } from '@/lib/types'

export default function ScanPage() {
  const router = useRouter()
  const params = useParams()
  const scanId = params.id as string

  const [scan, setScan] = useState<Scan | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (scanId) {
      loadScan()
    }
  }, [scanId])

  const loadScan = async () => {
    console.log(`[ScanPage] Loading scan with ID: ${scanId}`)
    const response = await getScan(scanId)
    console.log('[ScanPage] Scan response:', { success: response.success, hasData: !!response.data, error: response.error })

    if (response.success && response.data) {
      console.log(`[ScanPage] Scan loaded successfully - Status: ${response.data.status}, Images: ${response.data.processed_images}/${response.data.total_images}`)
      setScan(response.data)

      // If already completed, redirect to results
      if (response.data.status === 'completed') {
        console.log(`[ScanPage] Scan ${scanId} already completed, redirecting to results`)
        router.push(`/results/${scanId}`)
      } else if (response.data.status === 'failed') {
        console.error(`[ScanPage] Scan ${scanId} failed:`, response.data.error_message)
        setError(response.data.error_message || 'Processing failed')
      }
    } else {
      console.error(`[ScanPage] Failed to load scan ${scanId}:`, response.error)
      setError(response.error || 'Failed to load scan')
    }
  }

  const handleComplete = (completedScanId: string) => {
    console.log(`[ScanPage] handleComplete called for scan ${completedScanId}`)
    // Navigate to results page
    router.push(`/results/${completedScanId}`)
  }

  const handleError = (errorMessage: string) => {
    console.error(`[ScanPage] handleError called:`, errorMessage)
    setError(errorMessage)
  }

  const handleCancel = () => {
    // Navigate back to home
    router.push('/')
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
          <div className="text-6xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-red-900 mb-4">Processing Failed</h2>
          <p className="text-red-800 mb-6">{error}</p>
          <div className="flex justify-center gap-4">
            <button
              onClick={() => router.push('/')}
              className="px-6 py-3 bg-scout-purple text-white rounded-lg hover:bg-purple-900 transition-colors font-semibold"
            >
              Upload New Images
            </button>
            <button
              onClick={() => router.push('/inventory')}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-semibold"
            >
              View Inventory
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Processing Badge Images</h1>
        <p className="text-gray-600">
          Please wait while our AI analyzes your images and identifies badges...
        </p>
      </div>

      <ProcessingStatus
        scanId={scanId}
        onComplete={handleComplete}
        onError={handleError}
        onCancel={handleCancel}
      />

      <div className="mt-8 bg-blue-50 border-l-4 border-blue-500 p-6 rounded">
        <h3 className="font-semibold text-blue-900 mb-2">What's happening?</h3>
        <ul className="list-disc list-inside text-blue-800 space-y-1">
          <li>AI is analyzing each uploaded image</li>
          <li>Detecting and identifying individual badges</li>
          <li>Counting quantities of each badge type</li>
          <li>Matching detected badges to the database</li>
          <li>Calculating confidence scores for each detection</li>
        </ul>
        <p className="text-sm text-blue-700 mt-4">
          Processing time depends on the number of images and badges detected. Typically takes
          5-10 seconds per image.
        </p>
      </div>

      {scan && (
        <div className="mt-6 bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Scan Details</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600 mb-1">Scan ID</p>
              <p className="font-mono text-gray-900">{scan.id}</p>
            </div>
            <div>
              <p className="text-gray-600 mb-1">Total Images</p>
              <p className="font-semibold text-gray-900">{scan.total_images}</p>
            </div>
            <div>
              <p className="text-gray-600 mb-1">Started</p>
              <p className="text-gray-900">
                {new Date(scan.created_at).toLocaleString('en-AU')}
              </p>
            </div>
            <div>
              <p className="text-gray-600 mb-1">Status</p>
              <p className="font-semibold text-scout-purple capitalize">{scan.status}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
