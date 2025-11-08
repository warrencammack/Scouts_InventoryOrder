'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import type {
  Scan,
  BadgeDetection,
  ScanImage,
  Inventory,
  ApiResponse,
} from '@/lib/types'
import {
  uploadImages as apiUploadImages,
  processScan as apiProcessScan,
  getScan,
  getScanDetections,
  getInventory as apiGetInventory,
  updateInventory as apiUpdateInventory,
} from '@/lib/api'

// ============================================================================
// Types
// ============================================================================

interface AppState {
  // Current scan data
  currentScan: Scan | null
  currentDetections: BadgeDetection[]
  currentImages: ScanImage[]

  // Inventory data
  inventory: Inventory[]

  // User corrections
  corrections: { [detectionId: string]: string } // detectionId -> corrected badgeId

  // Loading states
  uploading: boolean
  processing: boolean
  loadingInventory: boolean

  // Error states
  error: string | null
}

interface AppContextValue extends AppState {
  // Actions
  uploadImages: (files: File[]) => Promise<ApiResponse<{ scan_id: string }>>
  startProcessing: (scanId: string) => Promise<ApiResponse<any>>
  loadScan: (scanId: string) => Promise<void>
  getInventory: () => Promise<void>
  updateInventory: (badgeId: string, quantity: number, notes?: string) => Promise<ApiResponse<Inventory>>
  applyCorrection: (detectionId: string, badgeId: string) => void
  clearCorrections: () => void
  setError: (error: string | null) => void
  clearCurrentScan: () => void
}

// ============================================================================
// Context
// ============================================================================

const AppContext = createContext<AppContextValue | undefined>(undefined)

// ============================================================================
// Provider
// ============================================================================

interface AppProviderProps {
  children: ReactNode
}

export function AppProvider({ children }: AppProviderProps) {
  // State
  const [state, setState] = useState<AppState>({
    currentScan: null,
    currentDetections: [],
    currentImages: [],
    inventory: [],
    corrections: {},
    uploading: false,
    processing: false,
    loadingInventory: false,
    error: null,
  })

  // ============================================================================
  // LocalStorage Persistence
  // ============================================================================

  useEffect(() => {
    // Load persisted data on mount
    if (typeof window !== 'undefined') {
      const savedScanId = localStorage.getItem('currentScanId')
      const savedCorrections = localStorage.getItem('corrections')

      if (savedScanId) {
        loadScan(savedScanId)
      }

      if (savedCorrections) {
        try {
          const corrections = JSON.parse(savedCorrections)
          setState((prev) => ({ ...prev, corrections }))
        } catch (err) {
          console.error('Failed to parse saved corrections:', err)
        }
      }
    }
  }, [])

  // Save current scan ID to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined' && state.currentScan) {
      localStorage.setItem('currentScanId', state.currentScan.id)
    }
  }, [state.currentScan])

  // Save corrections to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('corrections', JSON.stringify(state.corrections))
    }
  }, [state.corrections])

  // ============================================================================
  // Actions
  // ============================================================================

  const uploadImages = async (files: File[]): Promise<ApiResponse<{ scan_id: string }>> => {
    setState((prev) => ({ ...prev, uploading: true, error: null }))

    try {
      const response = await apiUploadImages(files)

      if (response.success && response.data) {
        // Store scan ID for later retrieval
        if (typeof window !== 'undefined') {
          localStorage.setItem('currentScanId', response.data.scan_id)
        }
      }

      setState((prev) => ({ ...prev, uploading: false }))
      return response
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        uploading: false,
        error: err.message || 'Failed to upload images',
      }))
      return {
        success: false,
        error: err.message || 'Failed to upload images',
      }
    }
  }

  const startProcessing = async (scanId: string): Promise<ApiResponse<any>> => {
    setState((prev) => ({ ...prev, processing: true, error: null }))

    try {
      const response = await apiProcessScan(scanId)
      setState((prev) => ({ ...prev, processing: false }))
      return response
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        processing: false,
        error: err.message || 'Failed to start processing',
      }))
      return {
        success: false,
        error: err.message || 'Failed to start processing',
      }
    }
  }

  const loadScan = async (scanId: string): Promise<void> => {
    setState((prev) => ({ ...prev, error: null }))

    try {
      // Load scan details
      const scanResponse = await getScan(scanId)
      if (!scanResponse.success || !scanResponse.data) {
        throw new Error(scanResponse.error || 'Failed to load scan')
      }

      // Load detections
      const detectionsResponse = await getScanDetections(scanId)
      if (!detectionsResponse.success || !detectionsResponse.data) {
        throw new Error(detectionsResponse.error || 'Failed to load detections')
      }

      setState((prev) => ({
        ...prev,
        currentScan: scanResponse.data!,
        currentDetections: detectionsResponse.data!,
        // TODO: Load scan images
        currentImages: [],
      }))
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        error: err.message || 'Failed to load scan',
      }))
    }
  }

  const getInventory = async (): Promise<void> => {
    setState((prev) => ({ ...prev, loadingInventory: true, error: null }))

    try {
      const response = await apiGetInventory()

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to load inventory')
      }

      setState((prev) => ({
        ...prev,
        inventory: response.data!,
        loadingInventory: false,
      }))
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        loadingInventory: false,
        error: err.message || 'Failed to load inventory',
      }))
    }
  }

  const updateInventory = async (
    badgeId: string,
    quantity: number,
    notes?: string
  ): Promise<ApiResponse<Inventory>> => {
    setState((prev) => ({ ...prev, error: null }))

    try {
      const response = await apiUpdateInventory(badgeId, quantity, notes)

      if (response.success && response.data) {
        // Update local inventory state
        setState((prev) => ({
          ...prev,
          inventory: prev.inventory.map((item) =>
            item.badge_id === badgeId ? response.data! : item
          ),
        }))
      }

      return response
    } catch (err: any) {
      setState((prev) => ({
        ...prev,
        error: err.message || 'Failed to update inventory',
      }))
      return {
        success: false,
        error: err.message || 'Failed to update inventory',
      }
    }
  }

  const applyCorrection = (detectionId: string, badgeId: string): void => {
    setState((prev) => ({
      ...prev,
      corrections: {
        ...prev.corrections,
        [detectionId]: badgeId,
      },
      // Update the detection in current detections
      currentDetections: prev.currentDetections.map((detection) =>
        detection.id === detectionId
          ? { ...detection, badge_id: badgeId, verified: true }
          : detection
      ),
    }))
  }

  const clearCorrections = (): void => {
    setState((prev) => ({ ...prev, corrections: {} }))
    if (typeof window !== 'undefined') {
      localStorage.removeItem('corrections')
    }
  }

  const setError = (error: string | null): void => {
    setState((prev) => ({ ...prev, error }))
  }

  const clearCurrentScan = (): void => {
    setState((prev) => ({
      ...prev,
      currentScan: null,
      currentDetections: [],
      currentImages: [],
    }))
    if (typeof window !== 'undefined') {
      localStorage.removeItem('currentScanId')
    }
  }

  // ============================================================================
  // Context Value
  // ============================================================================

  const value: AppContextValue = {
    ...state,
    uploadImages,
    startProcessing,
    loadScan,
    getInventory,
    updateInventory,
    applyCorrection,
    clearCorrections,
    setError,
    clearCurrentScan,
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

// ============================================================================
// Hooks
// ============================================================================

/**
 * Main app context hook
 */
export function useApp(): AppContextValue {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

/**
 * Hook for scan-related functionality
 */
export function useScan() {
  const context = useApp()
  return {
    currentScan: context.currentScan,
    currentDetections: context.currentDetections,
    currentImages: context.currentImages,
    corrections: context.corrections,
    uploading: context.uploading,
    processing: context.processing,
    uploadImages: context.uploadImages,
    startProcessing: context.startProcessing,
    loadScan: context.loadScan,
    applyCorrection: context.applyCorrection,
    clearCorrections: context.clearCorrections,
    clearCurrentScan: context.clearCurrentScan,
  }
}

/**
 * Hook for inventory-related functionality
 */
export function useInventory() {
  const context = useApp()
  return {
    inventory: context.inventory,
    loadingInventory: context.loadingInventory,
    getInventory: context.getInventory,
    updateInventory: context.updateInventory,
  }
}

/**
 * Hook for error handling
 */
export function useAppError() {
  const context = useApp()
  return {
    error: context.error,
    setError: context.setError,
  }
}
