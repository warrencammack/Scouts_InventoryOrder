// TypeScript types for the Scout Badge Inventory application

export interface Badge {
  id: string
  name: string
  category: string
  description?: string
  requirements_url?: string
  estimated_size_mm?: number
  image_path?: string
  scoutshop_url?: string
  created_at?: string
  updated_at?: string
}

export interface Inventory {
  id: string
  badge_id: string
  badge?: Badge
  quantity: number
  low_stock_threshold: number
  status: 'low' | 'ok' | 'good'
  last_counted?: string
  last_updated?: string
  created_at?: string
}

export interface Scan {
  id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  total_images: number
  processed_images: number
  total_badges_detected: number
  created_at: string
  updated_at?: string
  completed_at?: string
  error_message?: string
}

export interface ScanImage {
  id: string
  scan_id: string
  file_path: string
  file_name: string
  file_size: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  badges_detected: number
  processed_at?: string
  error_message?: string
  created_at: string
}

export interface BadgeDetection {
  id: string
  scan_image_id: string
  badge_id?: string
  badge?: Badge
  detected_name: string
  confidence: number
  quantity: number
  verified: boolean
  bounding_box?: {
    x: number
    y: number
    width: number
    height: number
  }
  created_at: string
}

export interface InventoryAdjustment {
  id: string
  badge_id: string
  badge?: Badge
  adjustment_type: 'scan' | 'manual' | 'correction'
  quantity_change: number
  previous_quantity: number
  new_quantity: number
  scan_id?: string
  notes?: string
  created_by?: string
  created_at: string
}

export interface ShoppingListItem {
  badge_id: string
  badge_name: string
  category: string
  current_quantity: number
  recommended_quantity: number
  scoutshop_url?: string
  priority: 'high' | 'medium' | 'low'
}

export interface ProcessingProgress {
  scan_id: string
  current_image: number
  total_images: number
  percentage: number
  current_image_name?: string
  estimated_time_remaining?: number
  status: string
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface UploadResponse {
  scan_id: string
  total_images: number
  message: string
}

export interface ProcessingResult {
  scan_id: string
  total_badges_detected: number
  unique_badges: number
  detections: BadgeDetection[]
  images: ScanImage[]
  status: string
}

export interface InventoryStats {
  total_badges: number
  total_quantity: number
  low_stock_count: number
  categories: {
    [category: string]: {
      count: number
      quantity: number
    }
  }
  recent_updates: InventoryAdjustment[]
}

export interface ExportOptions {
  format: 'csv' | 'pdf' | 'json'
  include_categories?: string[]
  include_low_stock_only?: boolean
  include_images?: boolean
}
