'use client'

import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { X, Upload, Camera, AlertCircle } from 'lucide-react'

interface ImageUploadProps {
  onImagesSelected: (files: File[]) => void
  maxFiles?: number
  maxSizeMB?: number
}

interface PreviewImage {
  file: File
  preview: string
  id: string
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  onImagesSelected,
  maxFiles = 20,
  maxSizeMB = 10,
}) => {
  const [images, setImages] = useState<PreviewImage[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const [uploadProgress, setUploadProgress] = useState<number>(0)
  const [isUploading, setIsUploading] = useState(false)

  const validateFile = useCallback(
    (file: File): string | null => {
      // Check file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/heic']
      if (!validTypes.includes(file.type.toLowerCase())) {
        return `${file.name}: Invalid file type. Only JPG, PNG, and HEIC images are allowed.`
      }

      // Check file size
      const maxSizeBytes = maxSizeMB * 1024 * 1024
      if (file.size > maxSizeBytes) {
        return `${file.name}: File size exceeds ${maxSizeMB}MB limit.`
      }

      return null
    },
    [maxSizeMB]
  )

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      const newErrors: string[] = []

      // Handle rejected files
      rejectedFiles.forEach((rejected) => {
        rejected.errors.forEach((error: any) => {
          if (error.code === 'file-too-large') {
            newErrors.push(`${rejected.file.name}: File is too large`)
          } else if (error.code === 'file-invalid-type') {
            newErrors.push(`${rejected.file.name}: Invalid file type`)
          } else {
            newErrors.push(`${rejected.file.name}: ${error.message}`)
          }
        })
      })

      // Check max files
      if (images.length + acceptedFiles.length > maxFiles) {
        newErrors.push(`Maximum ${maxFiles} images allowed`)
        setErrors(newErrors)
        return
      }

      // Validate and process accepted files
      const validFiles: File[] = []
      acceptedFiles.forEach((file) => {
        const error = validateFile(file)
        if (error) {
          newErrors.push(error)
        } else {
          validFiles.push(file)
        }
      })

      if (newErrors.length > 0) {
        setErrors(newErrors)
      } else {
        setErrors([])
      }

      // Create preview images
      const newImages: PreviewImage[] = validFiles.map((file) => ({
        file,
        preview: URL.createObjectURL(file),
        id: `${file.name}-${Date.now()}-${Math.random()}`,
      }))

      setImages((prev) => [...prev, ...newImages])

      // Notify parent component
      if (validFiles.length > 0) {
        const allFiles = [...images.map((img) => img.file), ...validFiles]
        onImagesSelected(allFiles)
      }
    },
    [images, maxFiles, validateFile, onImagesSelected]
  )

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/heic': ['.heic'],
    },
    maxSize: maxSizeMB * 1024 * 1024,
    noClick: false,
    noKeyboard: false,
  })

  const removeImage = (id: string) => {
    setImages((prev) => {
      const updated = prev.filter((img) => img.id !== id)
      const removedImage = prev.find((img) => img.id === id)
      if (removedImage) {
        URL.revokeObjectURL(removedImage.preview)
      }
      onImagesSelected(updated.map((img) => img.file))
      return updated
    })
  }

  const handleCameraClick = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.capture = 'environment'
    input.multiple = true
    input.onchange = (e: any) => {
      const files = Array.from(e.target.files || []) as File[]
      if (files.length > 0) {
        onDrop(files, [])
      }
    }
    input.click()
  }

  const clearAll = () => {
    images.forEach((img) => URL.revokeObjectURL(img.preview))
    setImages([])
    setErrors([])
    onImagesSelected([])
  }

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      images.forEach((img) => URL.revokeObjectURL(img.preview))
    }
  }, [images])

  return (
    <div className="w-full space-y-4">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${
            isDragActive
              ? 'border-scout-purple bg-purple-50 scale-105'
              : 'border-gray-300 hover:border-scout-purple hover:bg-gray-50'
          }
          ${images.length > 0 ? 'min-h-[150px]' : 'min-h-[250px]'}
        `}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center space-y-4">
          <Upload
            className={`w-12 h-12 ${
              isDragActive ? 'text-scout-purple' : 'text-gray-400'
            }`}
          />
          {isDragActive ? (
            <p className="text-lg font-medium text-scout-purple">
              Drop the images here...
            </p>
          ) : (
            <div className="space-y-2">
              <p className="text-lg font-medium text-gray-700">
                Drag and drop badge images here
              </p>
              <p className="text-sm text-gray-500">
                or click to browse (max {maxFiles} images, {maxSizeMB}MB each)
              </p>
            </div>
          )}
          <div className="flex gap-4 mt-4">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                open()
              }}
              className="px-4 py-2 bg-scout-purple text-white rounded-lg hover:bg-purple-900 transition-colors"
            >
              Browse Files
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                handleCameraClick()
              }}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2"
            >
              <Camera className="w-4 h-4" />
              Take Photo
            </button>
          </div>
        </div>
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-red-800 mb-1">
                Upload Errors
              </h4>
              <ul className="text-sm text-red-700 space-y-1">
                {errors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Upload Progress */}
      {isUploading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-900">
              Uploading images...
            </span>
            <span className="text-sm text-blue-700">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div
              className="bg-scout-purple h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Image Preview Grid */}
      {images.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-800">
              Selected Images ({images.length}/{maxFiles})
            </h3>
            <button
              onClick={clearAll}
              className="text-sm text-red-600 hover:text-red-800 font-medium"
            >
              Clear All
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {images.map((image) => (
              <div
                key={image.id}
                className="relative group aspect-square rounded-lg overflow-hidden bg-gray-100 border-2 border-gray-200 hover:border-scout-purple transition-colors"
              >
                <img
                  src={image.preview}
                  alt={image.file.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-200" />
                <button
                  onClick={() => removeImage(image.id)}
                  className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-red-600"
                  aria-label={`Remove ${image.file.name}`}
                >
                  <X className="w-4 h-4" />
                </button>
                <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <p className="text-xs text-white truncate" title={image.file.name}>
                    {image.file.name}
                  </p>
                  <p className="text-xs text-gray-300">
                    {(image.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Info Message */}
      {images.length === 0 && (
        <div className="text-center text-sm text-gray-500 py-4">
          <p>Supported formats: JPG, PNG, HEIC</p>
          <p className="mt-1">
            For best results, take clear photos with good lighting
          </p>
        </div>
      )}
    </div>
  )
}

export default ImageUpload
