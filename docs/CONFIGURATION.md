# Scout Badge Inventory - Configuration Guide

This document explains all configuration options for the Scout Badge Inventory application.

## Configuration File Location

**Frontend**: `frontend/lib/config.ts`

All frontend configuration values are centralized in this single file for easy maintenance.

## Configuration Sections

### 1. API Configuration (`API_CONFIG`)

Controls how the frontend communicates with the backend API.

```typescript
API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000,              // 30 seconds for standard API calls
  UPLOAD_TIMEOUT: 60000,       // 60 seconds for large file uploads
  RETRY: {
    MAX_ATTEMPTS: 3,           // Retry failed requests up to 3 times
    DELAY: 1000,               // Wait 1 second between retries
  },
}
```

**Environment Variables:**
- `NEXT_PUBLIC_API_URL`: Override the default API URL (useful for production)
  - Example: `NEXT_PUBLIC_API_URL=http://10.1.1.23:8000` for network access
  - Example: `NEXT_PUBLIC_API_URL=https://api.example.com` for production

**When to Change:**
- **BASE_URL**: Change when deploying to production or accessing from network
- **TIMEOUT**: Increase if you have slow network or large responses
- **UPLOAD_TIMEOUT**: Increase if users upload very large image files (>10MB)
- **RETRY**: Adjust for unstable networks

---

### 2. Polling Configuration (`POLLING_CONFIG`)

Controls how often the frontend checks for updates during processing.

```typescript
POLLING_CONFIG = {
  SCAN_STATUS_INTERVAL: 2000,      // Check every 2 seconds
  MAX_POLLING_DURATION: 600000,    // Give up after 10 minutes
}
```

**When to Change:**
- **SCAN_STATUS_INTERVAL**:
  - Decrease (e.g., 1000ms) for more responsive UI
  - Increase (e.g., 5000ms) to reduce server load
- **MAX_POLLING_DURATION**: Increase if processing very large batches (20+ images)

---

### 3. UI Configuration (`UI_CONFIG`)

Controls user interface behavior and limits.

```typescript
UI_CONFIG = {
  MAX_UPLOAD_FILES: 20,                          // Maximum images per upload
  MAX_FILE_SIZE: 10 * 1024 * 1024,              // 10MB per image
  ACCEPTED_IMAGE_TYPES: ['.jpg', '.jpeg', '.png', '.heic'],
  ITEMS_PER_PAGE: 25,                            // Pagination size
  SEARCH_DEBOUNCE_DELAY: 300,                    // Search input delay (ms)
}
```

**When to Change:**
- **MAX_UPLOAD_FILES**: Increase if users need to process large batches
  - Note: Also check backend's MAX_UPLOAD_SIZE setting
- **MAX_FILE_SIZE**: Increase for high-resolution images
  - Note: Ensure backend accepts larger files
- **ACCEPTED_IMAGE_TYPES**: Add formats like `.webp` if needed
- **ITEMS_PER_PAGE**: Adjust based on screen size and performance

---

### 4. Processing Configuration (`PROCESSING_CONFIG`)

Controls AI processing parameters and estimations.

```typescript
PROCESSING_CONFIG = {
  ESTIMATED_TIME_PER_IMAGE: 40,      // Seconds per image for ETA
  CONFIDENCE_THRESHOLD: 0.7,         // 70% confidence minimum
}
```

**When to Change:**
- **ESTIMATED_TIME_PER_IMAGE**:
  - Update based on actual average processing time
  - Varies by hardware (faster with GPU)
- **CONFIDENCE_THRESHOLD**:
  - Lower (0.5-0.6) if AI is too conservative
  - Raise (0.8+) if you want only high-confidence detections

---

### 5. Inventory Configuration (`INVENTORY_CONFIG`)

Controls stock levels and priority thresholds.

```typescript
INVENTORY_CONFIG = {
  DEFAULT_LOW_STOCK_THRESHOLD: 10,
  STOCK_LEVELS: {
    LOW: 10,      // Red indicator
    OK: 20,       // Yellow indicator
    GOOD: 50,     // Green indicator
  },
  PRIORITY_THRESHOLDS: {
    HIGH: 5,      // Less than 5 = urgent
    MEDIUM: 15,   // Less than 15 = medium priority
    LOW: 30,      // Less than 30 = low priority
  },
}
```

**When to Change:**
- Adjust based on your typical usage patterns
- Higher values for frequently used badges
- Lower values for rare badges

---

### 6. Feature Flags (`FEATURES`)

Enable or disable specific features without code changes.

```typescript
FEATURES = {
  SHOW_IMAGE_THUMBNAILS: false,          // Not yet implemented
  ENABLE_ANALYTICS: true,
  ENABLE_SHOPPING_LIST_EXPORT: true,
  ENABLE_MANUAL_CORRECTIONS: true,
}
```

**When to Change:**
- Set flags to `false` to hide incomplete features
- Use for A/B testing or gradual rollouts
- Disable features that cause issues

---

## Environment-Specific Configuration

### Local Development

Default values in `config.ts` are optimized for local development:
- `BASE_URL`: `http://localhost:8000`
- Fast polling for responsive development

### Network Access (Same WiFi)

Create `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://10.1.1.23:8000
```

### Production Deployment

1. Set environment variables:
   ```bash
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   ```

2. Consider adjusting:
   - Increase timeouts for remote API calls
   - Reduce polling frequency to save bandwidth
   - Enable/disable features based on production readiness

---

## Quick Reference

### Most Common Changes

**1. Enable Network Access:**
```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://YOUR_IP:8000
```

**2. Adjust Processing Speed Estimate:**
```typescript
// frontend/lib/config.ts
ESTIMATED_TIME_PER_IMAGE: 30  // If your hardware is faster
```

**3. Change Stock Thresholds:**
```typescript
// frontend/lib/config.ts
STOCK_LEVELS: {
  LOW: 5,
  OK: 15,
  GOOD: 30,
}
```

**4. Increase Upload Limits:**
```typescript
// frontend/lib/config.ts
MAX_UPLOAD_FILES: 50,
MAX_FILE_SIZE: 20 * 1024 * 1024,  // 20MB
```

---

## Troubleshooting

### Issue: Timeout Errors During Upload
**Solution**: Increase `UPLOAD_TIMEOUT` or `TIMEOUT` values

### Issue: Processing Status Not Updating
**Solution**: Check `SCAN_STATUS_INTERVAL` - may be too slow or too fast

### Issue: Stock Indicators Wrong Colors
**Solution**: Adjust `STOCK_LEVELS` thresholds to match your inventory

### Issue: Can't Upload Certain Image Types
**Solution**: Add file extensions to `ACCEPTED_IMAGE_TYPES`

---

## Backend Configuration

Backend configuration is in `backend/.env`:

```bash
DATABASE_URL=sqlite:///./database/inventory.db
UPLOAD_DIR=./uploads
OLLAMA_MODEL=llava:7b
OLLAMA_HOST=http://localhost:11434
API_PORT=8000
LOG_LEVEL=INFO
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for backend configuration details.

---

## Testing Configuration Changes

After changing configuration:

1. **Restart Frontend**:
   ```bash
   # Stop current frontend (Ctrl+C)
   # Then restart
   ./scripts/start-frontend.sh
   ```

2. **Test the Change**:
   - Verify the new behavior
   - Check browser console for errors
   - Monitor network requests

3. **Revert if Issues**:
   - Config is just TypeScript/JavaScript
   - Changes take effect immediately on reload
   - Easy to revert if something breaks

---

## Best Practices

1. **Document Changes**: Add comments when changing values
2. **Test Locally First**: Always test config changes locally
3. **Use Environment Variables**: For environment-specific values (URLs, keys)
4. **Keep Sensible Defaults**: Default values should work for most users
5. **Version Control**: Commit config changes with descriptive messages

---

## Related Documentation

- [Deployment Guide](DEPLOYMENT.md) - Backend configuration and deployment
- [Mobile Access Guide](MOBILE_ACCESS.md) - Network configuration
- [Action Plan](../ACTION_PLAN.md) - Future configuration enhancements

---

**Last Updated**: 2025-11-10
