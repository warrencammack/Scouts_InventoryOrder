import axios, { AxiosError } from 'axios'
import type {
  ApiResponse,
  Badge,
  BadgeDetection,
  Inventory,
  InventoryStats,
  ProcessingProgress,
  ProcessingResult,
  Scan,
  ScanImage,
  UploadResponse,
  InventoryAdjustment,
  ShoppingListItem,
  ExportOptions,
} from './types'
import { API_CONFIG } from './config'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Error handler
const handleApiError = (error: AxiosError): ApiResponse<never> => {
  if (error.response) {
    // Server responded with error
    return {
      success: false,
      error: error.response.data?.detail || error.message || 'Server error',
    }
  } else if (error.request) {
    // Request made but no response
    return {
      success: false,
      error: 'No response from server. Please check your connection.',
    }
  } else {
    // Error setting up request
    return {
      success: false,
      error: error.message || 'An unexpected error occurred',
    }
  }
}

// ============================================================================
// Upload API
// ============================================================================

/**
 * Upload badge images for processing
 * @param files - Array of image files to upload
 * @returns Upload response with scan ID
 */
export async function uploadImages(files: File[]): Promise<ApiResponse<UploadResponse>> {
  try {
    const formData = new FormData()
    files.forEach((file) => {
      formData.append('files', file)
    })

    const response = await apiClient.post<UploadResponse>('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

// ============================================================================
// Processing API
// ============================================================================

/**
 * Process uploaded scan images with AI
 * @param scanId - The scan ID to process
 * @returns Processing result with detected badges
 */
export async function processScan(scanId: number | string): Promise<ApiResponse<ProcessingResult>> {
  try {
    const response = await apiClient.post<ProcessingResult>(`/api/process/${scanId}`)

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Get processing status for a scan
 * @param scanId - The scan ID to check
 * @returns Current processing status
 */
export async function getProcessingStatus(
  scanId: number | string
): Promise<ApiResponse<ProcessingProgress>> {
  try {
    const response = await apiClient.get<ProcessingProgress>(`/api/process/${scanId}/status`)

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Get processing results for a completed scan
 * @param scanId - The scan ID to get results for
 * @returns Processing results with detections
 */
export async function getProcessingResults(
  scanId: number | string
): Promise<ApiResponse<ProcessingResult>> {
  try {
    const response = await apiClient.get<ProcessingResult>(`/api/process/${scanId}/results`)

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Get scan details
 * @param scanId - The scan ID to retrieve
 * @returns Scan details with images
 */
export async function getScan(scanId: string): Promise<ApiResponse<Scan>> {
  try {
    const response = await apiClient.get<Scan>(`/api/scans/${scanId}`)

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Get detections for a scan
 * @param scanId - The scan ID
 * @returns List of badge detections
 */
export async function getScanDetections(
  scanId: string
): Promise<ApiResponse<BadgeDetection[]>> {
  try {
    const response = await apiClient.get<BadgeDetection[]>(`/api/scans/${scanId}/detections`)

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

// ============================================================================
// Inventory API
// ============================================================================

/**
 * Get all inventory items
 * @param filters - Optional filters (category, low_stock_only, etc.)
 * @returns List of inventory items
 */
export async function getInventory(filters?: {
  category?: string
  low_stock_only?: boolean
  search?: string
}): Promise<ApiResponse<Inventory[]>> {
  try {
    const params = new URLSearchParams()
    if (filters?.category) params.append('category', filters.category)
    if (filters?.low_stock_only) params.append('low_stock_only', 'true')
    if (filters?.search) params.append('search', filters.search)

    const response = await apiClient.get<{ items: Inventory[], total_items: number, low_stock_count: number }>(`/api/inventory?${params.toString()}`)

    // Backend returns {items: [...], total_items: N, low_stock_count: N}, extract items array
    return {
      success: true,
      data: response.data.items || [],
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Get specific badge inventory
 * @param badgeId - The badge ID
 * @returns Inventory details for the badge
 */
export async function getBadgeInventory(badgeId: string): Promise<ApiResponse<Inventory>> {
  try {
    const response = await apiClient.get<Inventory>(`/api/inventory/${badgeId}`)

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Update badge inventory quantity
 * @param badgeId - The badge ID
 * @param quantity - New quantity
 * @param notes - Optional notes for the adjustment
 * @returns Updated inventory
 */
export async function updateInventory(
  badgeId: string,
  quantity: number,
  notes?: string
): Promise<ApiResponse<Inventory>> {
  try {
    const response = await apiClient.put<Inventory>(`/api/inventory/${badgeId}`, {
      quantity,
      notes,
    })

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Adjust inventory (add or subtract)
 * @param badgeId - The badge ID
 * @param adjustment - Quantity to add (positive) or subtract (negative)
 * @param notes - Optional notes
 * @returns Updated inventory
 */
export async function adjustInventory(
  badgeId: string,
  adjustment: number,
  notes?: string
): Promise<ApiResponse<InventoryAdjustment>> {
  try {
    const response = await apiClient.post<InventoryAdjustment>('/api/inventory/adjust', {
      badge_id: badgeId,
      quantity_change: adjustment,
      adjustment_type: 'manual',
      notes,
    })

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Get inventory statistics
 * @returns Overall inventory stats
 */
export async function getInventoryStats(): Promise<ApiResponse<InventoryStats>> {
  try {
    const response = await apiClient.get<InventoryStats>('/api/inventory/stats')

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

// ============================================================================
// Badge API
// ============================================================================

/**
 * Get all badges
 * @param category - Optional category filter
 * @returns List of badges
 */
export async function getBadges(category?: string): Promise<ApiResponse<Badge[]>> {
  try {
    const params = category ? `?category=${encodeURIComponent(category)}` : ''
    const response = await apiClient.get<Badge[]>(`/api/badges${params}`)

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Get specific badge details
 * @param badgeId - The badge ID
 * @returns Badge details
 */
export async function getBadge(badgeId: string): Promise<ApiResponse<Badge>> {
  try {
    const response = await apiClient.get<Badge>(`/api/badges/${badgeId}`)

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Search badges by name
 * @param query - Search query
 * @returns Matching badges
 */
export async function searchBadges(query: string): Promise<ApiResponse<Badge[]>> {
  try {
    const response = await apiClient.get<Badge[]>(`/api/badges/search?q=${encodeURIComponent(query)}`)

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

// ============================================================================
// Shopping List API
// ============================================================================

/**
 * Get shopping list (low stock items)
 * @returns List of items to purchase
 */
export async function getShoppingList(): Promise<ApiResponse<ShoppingListItem[]>> {
  try {
    const response = await apiClient.get<ShoppingListItem[]>('/api/shopping-list')

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

// ============================================================================
// Export API
// ============================================================================

/**
 * Export inventory as CSV
 * @param options - Export options
 * @returns CSV file blob
 */
export async function exportCSV(options?: ExportOptions): Promise<ApiResponse<Blob>> {
  try {
    const response = await apiClient.post(
      '/api/export/csv',
      options || {},
      {
        responseType: 'blob',
      }
    )

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Export inventory as PDF
 * @param options - Export options
 * @returns PDF file blob
 */
export async function exportPDF(options?: ExportOptions): Promise<ApiResponse<Blob>> {
  try {
    const response = await apiClient.post(
      '/api/export/pdf',
      options || {},
      {
        responseType: 'blob',
      }
    )

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

/**
 * Generate shopping list as formatted text
 * @returns Shopping list text
 */
export async function exportShoppingList(): Promise<ApiResponse<string>> {
  try {
    const response = await apiClient.get<string>('/api/export/shopping-list')

    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    return handleApiError(error as AxiosError)
  }
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Download a blob as a file
 * @param blob - The blob to download
 * @param filename - Desired filename
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

/**
 * Format date to readable string
 * @param dateString - ISO date string
 * @returns Formatted date string
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-AU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Get status color for inventory levels
 * @param inventory - Inventory item
 * @returns Tailwind color class
 */
export function getInventoryStatusColor(inventory: Inventory): string {
  if (inventory.quantity <= inventory.low_stock_threshold) {
    return 'badge-status-low'
  } else if (inventory.quantity <= inventory.low_stock_threshold * 2) {
    return 'badge-status-ok'
  }
  return 'badge-status-good'
}

/**
 * Get status label for inventory
 * @param inventory - Inventory item
 * @returns Status label
 */
export function getInventoryStatusLabel(inventory: Inventory): string {
  if (inventory.quantity <= inventory.low_stock_threshold) {
    return 'Low Stock'
  } else if (inventory.quantity <= inventory.low_stock_threshold * 2) {
    return 'Adequate'
  }
  return 'Well Stocked'
}
