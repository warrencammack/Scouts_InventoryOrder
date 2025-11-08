'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import ImageUpload from '@/components/ImageUpload'
import { uploadImages, processScan } from '@/lib/api'

export default function Home() {
  const router = useRouter()
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleImagesSelected = (files: File[]) => {
    setSelectedFiles(files)
    setError(null)
  }

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one image to upload')
      return
    }

    setUploading(true)
    setError(null)

    try {
      // Upload images
      const uploadResponse = await uploadImages(selectedFiles)

      if (!uploadResponse.success || !uploadResponse.data) {
        throw new Error(uploadResponse.error || 'Failed to upload images')
      }

      const scanId = uploadResponse.data.scan_id

      // Start processing
      const processResponse = await processScan(scanId)

      if (!processResponse.success) {
        throw new Error(processResponse.error || 'Failed to start processing')
      }

      // Navigate to processing page
      router.push(`/scan/${scanId}`)
    } catch (err: any) {
      setError(err.message || 'An error occurred during upload')
      setUploading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to Scout Badge Inventory Manager
        </h1>
        <p className="text-xl text-gray-600 mb-2">
          AI-powered badge counting and inventory management
        </p>
        <p className="text-gray-500">
          Upload photos of your badge collection and let AI do the counting
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-12">
        <div className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200 hover:border-scout-purple transition-colors">
          <div className="text-4xl mb-4">📸</div>
          <h3 className="text-xl font-semibold mb-2">1. Upload Images</h3>
          <p className="text-gray-600">
            Take photos of your badge boxes or collections using your phone or camera
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200 hover:border-scout-purple transition-colors">
          <div className="text-4xl mb-4">🤖</div>
          <h3 className="text-xl font-semibold mb-2">2. AI Processing</h3>
          <p className="text-gray-600">
            Our AI identifies and counts badges automatically with high accuracy
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200 hover:border-scout-purple transition-colors">
          <div className="text-4xl mb-4">✏️</div>
          <h3 className="text-xl font-semibold mb-2">3. Review & Correct</h3>
          <p className="text-gray-600">
            Verify results and make corrections if needed before updating inventory
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border-2 border-gray-200 hover:border-scout-purple transition-colors">
          <div className="text-4xl mb-4">📊</div>
          <h3 className="text-xl font-semibold mb-2">4. Track Inventory</h3>
          <p className="text-gray-600">
            View current stock levels and generate shopping lists for low inventory items
          </p>
        </div>
      </div>

      <div className="bg-gradient-to-r from-scout-purple to-purple-700 rounded-lg shadow-xl p-8 text-white">
        <h2 className="text-2xl font-bold mb-4 text-center">Ready to get started?</h2>
        <p className="mb-6 text-center">Upload your first batch of badge images</p>

        <ImageUpload onImagesSelected={handleImagesSelected} />

        {error && (
          <div className="mt-4 bg-red-100 border border-red-300 text-red-800 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {selectedFiles.length > 0 && (
          <div className="mt-6 flex justify-center">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="bg-scout-gold text-gray-900 px-8 py-3 rounded-lg font-semibold hover:bg-yellow-500 transition-colors shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : `Upload ${selectedFiles.length} Image${selectedFiles.length > 1 ? 's' : ''} & Start Processing`}
            </button>
          </div>
        )}
      </div>

      <div className="mt-12 bg-blue-50 border-l-4 border-blue-500 p-6 rounded">
        <h3 className="font-semibold text-blue-900 mb-2">Tips for best results:</h3>
        <ul className="list-disc list-inside text-blue-800 space-y-1">
          <li>Use good lighting when taking photos</li>
          <li>Ensure badges are clearly visible and in focus</li>
          <li>Take photos from directly above the badges when possible</li>
          <li>Multiple angles can help improve accuracy</li>
          <li>Group similar badges together in the same photo</li>
        </ul>
      </div>

      <div className="mt-8 text-center">
        <Link
          href="/inventory"
          className="text-scout-purple hover:text-scout-gold font-semibold underline"
        >
          View Current Inventory →
        </Link>
      </div>
    </div>
  )
}
