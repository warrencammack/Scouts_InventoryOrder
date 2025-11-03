'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function Home() {
  const [dragActive, setDragActive] = useState(false)

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

      <div className="bg-gradient-to-r from-scout-purple to-purple-700 rounded-lg shadow-xl p-8 text-white text-center">
        <h2 className="text-2xl font-bold mb-4">Ready to get started?</h2>
        <p className="mb-6">Upload your first batch of badge images</p>

        <div
          className={`border-4 border-dashed rounded-lg p-12 mb-6 transition-all cursor-pointer ${
            dragActive
              ? 'border-scout-gold bg-white/20'
              : 'border-white/50 hover:border-white hover:bg-white/10'
          }`}
          onDragOver={(e) => {
            e.preventDefault()
            setDragActive(true)
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragActive(false)
            // File upload logic will be implemented in ACTION-301
            alert('Upload functionality coming soon! (ACTION-301)')
          }}
          onClick={() => alert('Upload functionality coming soon! (ACTION-301)')}
        >
          <div className="text-6xl mb-4">📤</div>
          <p className="text-xl font-semibold mb-2">
            Drop images here or click to upload
          </p>
          <p className="text-sm text-white/80">
            Supports JPG, PNG, and HEIC formats
          </p>
        </div>

        <div className="flex justify-center space-x-4">
          <button className="bg-white text-scout-purple px-6 py-3 rounded-lg font-semibold hover:bg-scout-gold hover:text-white transition-colors shadow-lg">
            Choose Files
          </button>
          <button className="bg-transparent border-2 border-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-scout-purple transition-colors">
            Use Camera
          </button>
        </div>
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
