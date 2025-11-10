# Scout Badge Inventory - Mobile Access Guide

Access the Scout Badge Inventory System from your phone or tablet on the same WiFi network.

## Overview

The system can be accessed from any device on your local network (same WiFi), making it easy to scan badges with your mobile phone camera and manage inventory from tablets.

## Prerequisites

- Backend and frontend running on your computer
- Mobile device connected to the **same WiFi network**
- Know your computer's local IP address

## Quick Setup

### Step 1: Find Your Computer's IP Address

**On macOS/Linux:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}'
```

**On Windows:**
```cmd
ipconfig | findstr IPv4
```

Your local IP will look like: `192.168.1.100` or `10.1.1.23`

### Step 2: Start Backend for Network Access

Use the network-enabled startup script:

```bash
./scripts/start-backend-network.sh
```

This starts the backend on `0.0.0.0` (all network interfaces) instead of just `localhost`.

You'll see output like:
```
================================================
Local access:   http://127.0.0.1:8000
Network access: http://10.1.1.23:8000
API docs:       http://10.1.1.23:8000/docs
================================================
```

### Step 3: Configure Frontend for Network Access

**Option A: Quick Test (Temporary)**

Start the frontend with custom host:
```bash
cd frontend
npm run dev -- -H 0.0.0.0
```

**Option B: Permanent Configuration**

1. Create/edit `frontend/.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://10.1.1.23:8000
   ```
   *(Replace `10.1.1.23` with your actual IP)*

2. Start frontend normally:
   ```bash
   ./scripts/start-frontend.sh
   ```

### Step 4: Access from Mobile Device

1. **Connect your mobile device to the same WiFi network**

2. Open browser on mobile and go to:
   ```
   http://10.1.1.23:3000
   ```
   *(Replace with your computer's IP)*

3. You should see the Scout Badge Inventory app!

## Usage Tips

### Taking Photos on Mobile

1. Open the app in your mobile browser
2. Tap the upload area
3. Choose "Take Photo" or "Choose Photo"
4. Take clear, well-lit photos of badges
5. Upload and process as normal

### Best Practices

**For Best Photo Quality:**
- Use good lighting (natural light is best)
- Hold camera steady
- Fill the frame with badges
- Avoid shadows and glare
- Take multiple angles if needed

**Network Performance:**
- Stay on same WiFi network
- Image upload may take longer than on desktop
- Processing time is the same (~40 seconds per image)

## Troubleshooting

### Can't Access from Mobile

**Check 1: Same WiFi Network**
```bash
# On computer, check WiFi name
networksetup -getairportnetwork en0  # macOS
iwgetid -r                             # Linux

# On mobile, verify connected to same WiFi
```

**Check 2: Firewall Settings**

Your computer's firewall may be blocking connections:

**macOS:**
```bash
# Allow Node.js and Python through firewall
System Preferences → Security & Privacy → Firewall → Firewall Options
→ Allow "node" and "Python"
```

**Linux (ufw):**
```bash
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
```

**Windows:**
```
Windows Defender Firewall → Allow an app
→ Add Python and Node.js
```

**Check 3: Backend Running on All Interfaces**

Verify backend is listening on 0.0.0.0:
```bash
lsof -i :8000 | grep LISTEN
# Should show: 0.0.0.0:8000 (not 127.0.0.1:8000)
```

If showing 127.0.0.1, stop backend and restart with:
```bash
./scripts/start-backend-network.sh
```

**Check 4: Test Backend Connection**

From mobile browser, test API directly:
```
http://10.1.1.23:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "upload_dir": "..."
}
```

### Connection Refused Error

**Cause**: Backend not accessible from network

**Solution**:
1. Stop backend (Ctrl+C)
2. Restart with network script:
   ```bash
   ./scripts/start-backend-network.sh
   ```
3. Verify it shows "Network access: http://YOUR-IP:8000"

### API Connection Failed in Frontend

**Cause**: Frontend configured with wrong API URL

**Solution**:
1. Check `frontend/.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://10.1.1.23:8000
   ```
2. Ensure IP matches your computer's actual IP
3. Restart frontend

### Slow Performance

**Causes & Solutions**:

1. **Weak WiFi Signal**
   - Move closer to router
   - Use 5GHz WiFi if available

2. **Large Image Files**
   - Compress images before upload
   - Take photos at lower resolution

3. **Background Downloads**
   - Pause other downloads
   - Close unnecessary apps

## Network Architecture

```
┌─────────────────┐
│  Your Computer  │
│                 │
│  Backend: 8000  │◄──┐
│  Frontend: 3000 │◄──┤
└─────────────────┘   │
         │            │
         │ WiFi       │ WiFi
         │            │
    ┌────▼────┐   ┌───▼──────┐
    │ Phone/  │   │  Tablet  │
    │ Mobile  │   │          │
    └─────────┘   └──────────┘
```

All devices connect to your computer via local WiFi network.

## Security Considerations

### On Private Network (Home/Office)

✅ Safe to use with default settings
✅ Only accessible on your local network
✅ No internet exposure

### On Public WiFi

⚠️ **Not Recommended** - Others on network can access

If you must use public WiFi:
1. Use VPN for extra security
2. Change backend `SECRET_KEY` in `.env`
3. Consider using HTTPS (requires SSL certificate)

### Authentication (Future Enhancement)

The current version has **no user authentication**. Anyone on your network can access the system.

For production deployment, consider:
- Adding user login
- Implementing API keys
- Using HTTPS/SSL
- Setting up reverse proxy (nginx)

## Advanced Configuration

### Custom Port Numbers

If ports 3000 or 8000 are already in use:

**Backend (change to 8080):**
```bash
# Edit scripts/start-backend-network.sh
# Change: --port 8000
# To:     --port 8080
```

**Frontend (change to 3001):**
```bash
# Edit package.json
"dev": "next dev -p 3001 -H 0.0.0.0"
```

Update `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://10.1.1.23:8080
```

### Static IP Address

To avoid changing IP every time:

**macOS:**
```
System Preferences → Network → Advanced → TCP/IP
→ Configure IPv4: Using DHCP with manual address
→ IPv4 Address: 10.1.1.23
```

**Windows:**
```
Network Connections → Properties → IPv4 Properties
→ Use the following IP address: 10.1.1.23
```

**Linux:**
```bash
# Edit /etc/network/interfaces or use NetworkManager
```

### QR Code for Easy Access

Generate a QR code for quick mobile access:

```bash
# Install qrencode
brew install qrencode  # macOS

# Generate QR code
qrencode -t UTF8 "http://10.1.1.23:3000"
```

Scan the QR code with your phone camera to instantly open the app!

## Example Workflow

### Typical Usage Scenario

1. **Setup (once)**
   - Start backend with `./scripts/start-backend-network.sh`
   - Start frontend with `./scripts/start-frontend.sh`
   - Note the IP address shown

2. **Daily Use**
   - Open browser on phone
   - Go to `http://YOUR-IP:3000`
   - Bookmark it for quick access

3. **Badge Scanning**
   - Take photos with phone camera
   - Upload directly from photos
   - Process and review on phone or tablet
   - View inventory dashboard

4. **Multi-Device**
   - Take photos on phone
   - Review/edit on tablet
   - Generate reports on computer
   - All devices stay in sync (same database)

## Support

If you encounter issues:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
2. Verify network connectivity
3. Check firewall settings
4. Review backend logs: `logs/backend.log`
5. Test with `curl` from another computer on network

---

**Quick Reference:**
- Backend Network: `./scripts/start-backend-network.sh`
- Your IP: Run `ifconfig | grep "inet " | grep -v 127.0.0.1`
- Mobile URL: `http://YOUR-IP:3000`
- Test API: `http://YOUR-IP:8000/health`
