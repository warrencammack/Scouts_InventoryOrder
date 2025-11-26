/**
 * Frontend Configuration
 *
 * Centralized configuration for the Scout Badge Inventory frontend.
 * All configurable values should be defined here for easy maintenance.
 */

// API Configuration
export const API_CONFIG = {
  /**
   * Base URL for the backend API
   * Can be overridden with NEXT_PUBLIC_API_URL environment variable
   * Using 127.0.0.1 instead of localhost to avoid IPv6 resolution issues
   */
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',

  /**
   * Default timeout for API requests (milliseconds)
   * 120 seconds to handle slower connections and AI processing (doubled from 60s)
   * Note: Image processing runs in background, so this doesn't need to be longer
   */
  TIMEOUT: 120000,

  /**
   * Timeout specifically for large file uploads (milliseconds)
   * 120 seconds for uploading multiple large image files (doubled from 60s)
   */
  UPLOAD_TIMEOUT: 120000,

  /**
   * Retry configuration for failed requests
   */
  RETRY: {
    MAX_ATTEMPTS: 3,
    DELAY: 1000, // milliseconds between retries
  },
}

// Polling Configuration
export const POLLING_CONFIG = {
  /**
   * Interval for polling scan processing status (milliseconds)
   * 2 seconds provides good UX without overloading the server
   */
  SCAN_STATUS_INTERVAL: 2000,

  /**
   * Maximum polling duration before giving up (milliseconds)
   * 20 minutes should be sufficient for processing even large batches (doubled from 10 minutes)
   */
  MAX_POLLING_DURATION: 1200000,
}

// UI Configuration
export const UI_CONFIG = {
  /**
   * Maximum number of images that can be uploaded at once
   */
  MAX_UPLOAD_FILES: 20,

  /**
   * Maximum file size per image (bytes)
   * 10MB per image
   */
  MAX_FILE_SIZE: 10 * 1024 * 1024,

  /**
   * Accepted image file types
   */
  ACCEPTED_IMAGE_TYPES: ['.jpg', '.jpeg', '.png', '.heic'],

  /**
   * Items per page for paginated lists
   */
  ITEMS_PER_PAGE: 25,

  /**
   * Debounce delay for search inputs (milliseconds)
   */
  SEARCH_DEBOUNCE_DELAY: 300,
}

// Processing Configuration
export const PROCESSING_CONFIG = {
  /**
   * Estimated processing time per image (seconds)
   * Used for ETA calculations in the UI
   */
  ESTIMATED_TIME_PER_IMAGE: 40,

  /**
   * Confidence threshold for badge detection (0-1)
   * Detections below this threshold are flagged for review
   */
  CONFIDENCE_THRESHOLD: 0.7,
}

// Inventory Configuration
export const INVENTORY_CONFIG = {
  /**
   * Default low stock threshold for badges
   */
  DEFAULT_LOW_STOCK_THRESHOLD: 10,

  /**
   * Stock level classifications
   */
  STOCK_LEVELS: {
    LOW: 10,
    OK: 20,
    GOOD: 50,
  },

  /**
   * Priority levels for shopping list
   */
  PRIORITY_THRESHOLDS: {
    HIGH: 5,    // Less than 5 in stock = high priority
    MEDIUM: 15, // Less than 15 in stock = medium priority
    LOW: 30,    // Less than 30 in stock = low priority
  },
}

// Feature Flags
export const FEATURES = {
  /**
   * Enable/disable image thumbnail display on results page
   * Currently disabled as feature is not yet implemented
   */
  SHOW_IMAGE_THUMBNAILS: false,

  /**
   * Enable/disable analytics dashboard
   */
  ENABLE_ANALYTICS: true,

  /**
   * Enable/disable shopping list export
   */
  ENABLE_SHOPPING_LIST_EXPORT: true,

  /**
   * Enable/disable manual badge corrections
   */
  ENABLE_MANUAL_CORRECTIONS: true,
}

// Export all configs
export default {
  API_CONFIG,
  POLLING_CONFIG,
  UI_CONFIG,
  PROCESSING_CONFIG,
  INVENTORY_CONFIG,
  FEATURES,
}
