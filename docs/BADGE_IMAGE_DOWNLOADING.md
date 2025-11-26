# Badge Image Downloading Guide

This guide explains how to download badge images for the Scouts Inventory System, including handling login-protected content from scoutshop.com.au.

## Overview

The system provides multiple approaches to download badge images:

1. **Public Image Downloading** - Downloads publicly available images without authentication
2. **Authenticated Downloading** - Downloads login-protected images using Scout Member credentials
3. **Alternative Sources** - Downloads from alternative sources when scoutshop.com.au is not available
4. **PDF Extraction** - Extracts images from the official badge chart PDF (future feature)

## Setup

### 1. Install Additional Dependencies

```bash
# Install additional packages for web scraping
pip install -r scripts/requirements.txt

# Or install individually:
pip install beautifulsoup4 lxml requests
```

### 2. Optional Dependencies

For enhanced functionality, you can install:

```bash
# For image processing and validation
pip install Pillow

# For PDF processing (badge chart extraction)
pip install PyMuPDF

# For progress bars during downloads
pip install tqdm
```

## Usage

### Public Image Downloading

Download publicly available badge images without authentication:

```bash
# Download all public images
python scripts/download-badge-images.py

# Dry run to see what would be downloaded
python scripts/download-badge-images.py --dry-run

# Force re-download existing images
python scripts/download-badge-images.py --force-redownload

# Only validate existing images
python scripts/download-badge-images.py --validate-only
```

### Authenticated Downloading

Download login-protected images using Scout Member credentials:

```bash
# Interactive login (recommended - secure password input)
python scripts/authenticated-badge-downloader.py --username your.email@example.com --prompt-password

# Command line login (less secure)
python scripts/authenticated-badge-downloader.py --username your.email@example.com --password yourpassword

# Dry run to see what would be downloaded
python scripts/authenticated-badge-downloader.py --username your.email@example.com --prompt-password --dry-run

# Use saved session (login once, reuse session)
python scripts/authenticated-badge-downloader.py --session-file scout_session.pkl
```

### Combined Workflow

For maximum coverage, use both scripts:

```bash
# Step 1: Download public images
python scripts/download-badge-images.py

# Step 2: Download protected images (requires Scout Member account)
python scripts/authenticated-badge-downloader.py --username your.email@example.com --prompt-password

# Step 3: Validate all images
python scripts/download-badge-images.py --validate-only
```

## Authentication Requirements

### Scout Member Account

To download login-protected images, you need:

- Valid Scout Member account on scoutshop.com.au
- Permission to access badge inventory
- Compliance with scoutshop.com.au terms of service

### Security Considerations

- **Use `--prompt-password`** for secure password input
- **Session files** store login cookies - keep them secure
- **Rate limiting** is built-in to respect server resources
- **Logout** is automatic to clean up sessions

## File Structure

### Downloaded Images

Images are saved to:
```
data/badges/
├── grey-wolf-award.png
├── milestone-1.png
├── achievement-art-design.png
└── ...
```

### Metadata Tracking

Download information is tracked in:
- `data/badge_images_metadata.json` - Updated with download status
- `badge_download.log` - Public download log
- `authenticated_badge_download.log` - Authenticated download log

### Session Management

- `scout_session.pkl` - Saved login session (optional)

## Troubleshooting

### Common Issues

#### 1. Login Failures

```
ERROR - Login failed - invalid credentials or login process changed
```

**Solutions:**
- Verify Scout Member credentials
- Check if scoutshop.com.au login process has changed
- Try logging in manually through web browser first

#### 2. Missing Images

```
INFO - Missing images for badges: badge-1, badge-2, badge-3
```

**Solutions:**
- Run authenticated downloader for login-protected badges
- Check if badges are discontinued or out of stock
- Verify URLs in `data/scoutshop_urls.json`

#### 3. Network Errors

```
ERROR - Request failed: Connection timeout
```

**Solutions:**
- Check internet connection
- Retry with longer timeout
- Check if scoutshop.com.au is accessible

#### 4. Import Errors

```
ImportError: No module named 'beautifulsoup4'
```

**Solutions:**
- Install required dependencies: `pip install -r scripts/requirements.txt`
- Ensure you're using the correct Python environment

### Debug Mode

Enable detailed logging:

```bash
# Set log level to DEBUG
export PYTHONPATH=/workspace
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
exec(open('scripts/download-badge-images.py').read())
"
```

## Badge Coverage Status

Current status (as of metadata):
- **Total badges**: 70
- **Documented URLs**: 15
- **Estimated URLs**: 32
- **Login-protected**: 23

### Priority Levels

- **High Priority**: Peak awards, milestones, SIA badges
- **Medium Priority**: Achievement badges
- **Low Priority**: Participation badges, event badges

## Alternative Sources

When scoutshop.com.au is not available, images can be sourced from:

### Official Sources
- **Badge Chart PDF**: https://scoutshop.com.au/assets/badge_chart-dd3261395447ed6d32dc9a4489ec4535d608072a16d90c5495df0cb2a0ef671f.pdf
- **Program Resources**: https://pr.scouts.com.au/
- **Scouts Australia**: Official documentation and resources

### State Organizations
- **Scouts Victoria**: https://scoutsvictoria.com.au/
- **Scouts NSW**: https://nsw.scouts.com.au/
- **Scouts Queensland**: https://scoutsqld.com.au/

## Legal and Ethical Considerations

### Copyright

- All badge designs are property of Scouts Australia
- Images should only be used for legitimate Scouting purposes
- Not for commercial use without permission
- Credit Scouts Australia as the source

### Terms of Service

- Respect scoutshop.com.au terms of service
- Use reasonable rate limiting (built into scripts)
- Only use Scout Member credentials you own or have permission to use
- Don't circumvent access controls

### Best Practices

- **Rate Limiting**: Scripts include delays between requests
- **User Agent**: Identifies as a standard web browser
- **Session Management**: Proper login/logout procedures
- **Error Handling**: Graceful failure without overwhelming servers

## Integration with Inventory System

### Backend Integration

The backend automatically serves images from `data/badges/`:

```python
# In backend/services/badge_service.py
def get_badge_image_path(badge_id: str) -> Optional[Path]:
    image_path = Path(f"data/badges/{badge_id}.png")
    return image_path if image_path.exists() else None
```

### Frontend Integration

The frontend displays badge images with fallbacks:

```typescript
// In frontend components
const badgeImageUrl = `/api/badges/${badgeId}/image`;
// Fallback to placeholder if image not available
```

### Database Updates

Consider adding image availability flags:

```sql
ALTER TABLE badges ADD COLUMN image_available BOOLEAN DEFAULT FALSE;
```

## Maintenance

### Regular Updates

1. **Weekly**: Run public downloader to catch new badges
2. **Monthly**: Run authenticated downloader for protected content
3. **Quarterly**: Validate all images and update metadata

### Monitoring

Check logs for:
- Failed downloads
- Changed URLs
- New badges added to metadata
- Authentication issues

### URL Updates

When scoutshop.com.au changes:
1. Update URLs in `data/scoutshop_urls.json`
2. Test with dry-run mode
3. Update authentication flow if needed

## Future Enhancements

### Planned Features

1. **PDF Processing**: Extract images from badge chart PDF
2. **Alternative Source Scraping**: Automated downloading from state Scout sites
3. **Image Quality Enhancement**: Automatic upscaling and cleanup
4. **Batch Processing**: Parallel downloads for faster processing
5. **Web Interface**: GUI for managing downloads

### Contributing

To contribute improvements:

1. Test changes with `--dry-run` first
2. Respect rate limiting and ToS
3. Update documentation
4. Add appropriate error handling
5. Include logging for debugging

## Support

For issues with badge downloading:

1. Check this documentation
2. Review log files for error details
3. Verify network connectivity and credentials
4. Test with dry-run mode first
5. Report bugs with full error logs

## Examples

### Complete Setup and Download

```bash
# 1. Install dependencies
pip install -r scripts/requirements.txt

# 2. Download public images
python scripts/download-badge-images.py --dry-run
python scripts/download-badge-images.py

# 3. Download protected images (if you have Scout Member account)
python scripts/authenticated-badge-downloader.py \
  --username your.email@example.com \
  --prompt-password \
  --dry-run

python scripts/authenticated-badge-downloader.py \
  --username your.email@example.com \
  --prompt-password

# 4. Validate results
python scripts/download-badge-images.py --validate-only

# 5. Check coverage
ls -la data/badges/
```

### Automated Workflow

```bash
#!/bin/bash
# automated-badge-download.sh

echo "Starting badge image download..."

# Download public images
echo "Downloading public images..."
python scripts/download-badge-images.py

# Check if we have Scout Member credentials
if [ -f "scout_credentials.txt" ]; then
    echo "Downloading protected images..."
    python scripts/authenticated-badge-downloader.py \
      --session-file scout_session.pkl
fi

# Validate all images
echo "Validating images..."
python scripts/download-badge-images.py --validate-only

echo "Badge download complete!"
```

This comprehensive system provides multiple approaches to downloading badge images while respecting authentication requirements and terms of service.