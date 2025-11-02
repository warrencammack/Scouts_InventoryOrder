# Scouts Inventory Order System - Requirements Specification

## 0. initial requirements scratch

I am a cub scout leader and have to regularly check the inventory of badges to ensure that we have enough to give out to the cubs when required.

What would be helpful is a way to upload images of the badges in the boxes and for an approximate inventory to be created. 

A full list of all cub scout badges in Australia will be needed along with the images of the actual badges will be required.

The system should be able to recognize the badges from the images and match them to the list, providing a count of each badge type based on the images uploaded.

The inventory system should have the following features:
1. Image Upload: Ability to upload multiple images of badge boxes.
2. Badge Recognition: Use image recognition to identify and count each type of badge.
3. Badge Database: A comprehensive database of all cub scout badges in Australia, including images and descriptions.


4. Inventory Report: Generate a report summarizing the inventory counts for each badge type.
5. User Interface: A simple and user-friendly interface for uploading images and viewing reports.

6. Export Functionality: Ability to export the inventory report in various formats (e.g., PDF, Excel).

will also need to make it easy to buy the badges via scoutshop.com.au



## 1. Project Overview

### 1.1 Purpose
An AI-powered badge inventory system for Cub Scout leaders in Australia that uses image recognition to automatically count and track badge inventory from uploaded photos, with integrated purchasing through scoutshop.com.au.

### 1.2 Scope
**In Scope:**
- Image upload and processing of badge boxes/collections
- AI/Computer Vision badge recognition and counting
- Australian Cub Scout badge database with reference images
- Inventory tracking and reporting
- Direct link/integration to scoutshop.com.au for purchasing
- Export functionality (PDF, Excel)

**Out of Scope (Phase 1):**
- Manual inventory entry
- Order approval workflows
- Multi-user/multi-troop management
- Financial transaction processing
- Other scout equipment inventory

## 2. Stakeholders

### 2.1 Primary Users
- **Cub Scout Leaders**: Upload badge photos, view inventory counts, identify badges to reorder

### 2.2 Future Users (Phase 2+)
- Other scout leaders (Scouts, Venturers, Rovers)
- Group/District quartermasters
- Multiple leaders within same group

## 3. Functional Requirements

### 3.1 Badge Database
- **BADGE-001**: System shall include a comprehensive database of all Australian Cub Scout badges
  - Badge name
  - Badge category (Achievement, Special Interest, Milestone, etc.)
  - Official reference image(s) of the badge
  - Badge description/requirements reference
  - Link to scoutshop.com.au product page
  - Badge dimensions/specifications

- **BADGE-002**: Badge database shall be searchable and browsable
  - Filter by category
  - Search by name
  - Visual gallery view

- **BADGE-003**: Badge reference images shall be high quality for accurate AI matching
  - Minimum 300x300px resolution
  - Multiple angles/variations if needed
  - Clear, well-lit images

### 3.2 Image Upload and Processing
- **IMG-001**: System shall support uploading multiple images
  - Formats: JPG, PNG, HEIC (iPhone photos)
  - Maximum file size: 10MB per image
  - Batch upload of multiple images at once
  - Drag-and-drop interface

- **IMG-002**: System shall support images from various sources
  - Photos taken with smartphone
  - Photos from digital camera
  - Scanned images
  - Various lighting conditions and angles

- **IMG-003**: System shall provide upload progress indication
  - Progress bar during upload
  - Preview of uploaded images
  - Ability to remove images before processing

- **IMG-004**: System shall validate uploaded images
  - Check file format
  - Check file size
  - Verify image is readable
  - Provide clear error messages for invalid uploads

### 3.3 AI Badge Recognition
- **AI-001**: System shall automatically detect badges in uploaded images
  - Identify individual badges even when multiple are visible
  - Handle badges at various angles and orientations
  - Work with badges in boxes, on tables, or other backgrounds

- **AI-002**: System shall match detected badges to the badge database
  - Provide confidence score for each match (e.g., 95% confident)
  - Flag low-confidence matches for user verification
  - Handle partial or obscured badges

- **AI-003**: System shall count quantity of each badge type
  - Provide total count per badge type
  - Show breakdown by image if multiple images uploaded
  - Detect and warn about potential duplicates across images

- **AI-004**: System shall provide visual feedback on recognition
  - Highlight/outline detected badges on images
  - Label each badge with identified type
  - Show confidence score for each detection
  - Allow user to correct misidentifications

- **AI-005**: System shall handle recognition errors gracefully
  - Allow manual badge identification for failed detections
  - Learn from corrections (future enhancement)
  - Provide option to skip unclear badges

### 3.4 Inventory Management
- **INV-001**: System shall maintain current inventory counts
  - Store latest count for each badge type
  - Track date of last count/update
  - Show historical inventory snapshots

- **INV-002**: System shall support manual inventory adjustments
  - Add badges (new purchases, donations)
  - Remove badges (awarded to cubs, damaged)
  - Manual count corrections
  - Add notes to adjustments

- **INV-003**: System shall track inventory over time
  - Maintain history of inventory counts
  - Show trend graphs (increasing/decreasing)
  - Compare current vs. previous counts

- **INV-004**: System shall highlight low stock situations
  - User-configurable minimum thresholds per badge
  - Visual indicators for low stock (red/yellow/green)
  - Show badges that need reordering

### 3.5 Reporting and Export
- **REP-001**: System shall generate inventory reports
  - Current stock levels for all badges
  - Badges grouped by category
  - Low stock alerts
  - Date of last inventory check

- **REP-002**: Reports shall be exportable in multiple formats
  - PDF: Formatted, printable report
  - Excel/CSV: Spreadsheet for further analysis
  - Include badge images in exports

- **REP-003**: System shall provide visual reports
  - Inventory by category (pie chart)
  - Stock level visualization (bar chart)
  - Trend over time (line graph)

### 3.6 ScoutShop Integration
- **SHOP-001**: System shall link to scoutshop.com.au for purchasing
  - Direct links from each badge to product page
  - "Buy Now" button for each badge type
  - Open scoutshop.com.au in new tab/window

- **SHOP-002**: System shall generate shopping lists
  - Select badges to reorder
  - Export list of badges needed with quantities
  - Include scoutshop.com.au links for each item

- **SHOP-003**: System shall suggest reorder quantities
  - Based on minimum stock thresholds
  - Consider historical usage patterns (future)
  - Suggest quantity to bring stock to target level

## 4. Non-Functional Requirements

### 4.1 Performance
- **PERF-001**: Image upload shall complete within 30 seconds per image (on typical internet)
- **PERF-002**: AI processing shall complete within 60 seconds for batch of 5 images
- **PERF-003**: Page loads shall complete within 2 seconds
- **PERF-004**: System shall handle images up to 10MB without performance degradation

### 4.2 Accuracy
- **ACC-001**: Badge recognition shall achieve 85%+ accuracy on clear, well-lit photos
- **ACC-002**: System shall provide confidence scores to help user verify results
- **ACC-003**: Counting accuracy shall be within ±2 badges for counts under 50

### 4.3 Usability
- **USE-001**: System shall work on mobile devices (iOS/Android)
  - Responsive design
  - Touch-friendly interface
  - Support camera upload from mobile

- **USE-002**: System shall have simple, intuitive workflow
  - Maximum 3 clicks from upload to inventory report
  - Clear visual feedback at each step
  - Minimal technical knowledge required

- **USE-003**: System shall provide helpful guidance
  - Tips for taking good badge photos
  - Clear error messages with solutions
  - Help/FAQ section

- **USE-004**: System shall support offline viewing of last inventory (future)

### 4.4 Security and Privacy
- **SEC-001**: Images shall be stored securely
- **SEC-002**: System shall use HTTPS for all communications
- **SEC-003**: User data shall be backed up regularly
- **SEC-004**: System shall comply with Australian privacy requirements

### 4.5 Reliability
- **REL-001**: System shall gracefully handle AI service outages
  - Queue images for later processing
  - Provide clear status messages
  - Allow manual entry as fallback

- **REL-002**: System shall preserve uploaded images until processing completes
- **REL-003**: System shall auto-save progress during multi-image processing

## 5. Technical Specifications

### 5.1 Platform Recommendation
**Primary: Progressive Web App (PWA)**
- ✅ Works on all devices (desktop, mobile, tablet)
- ✅ Installable on mobile home screen
- ✅ Access camera on mobile devices
- ✅ Can work offline (view cached inventory)
- ✅ Single codebase for all platforms
- ✅ No app store approval needed

**Alternative: Native Mobile App**
- Better camera integration
- Better performance
- Requires separate iOS/Android development

### 5.2 Technology Stack (Recommended)

**Frontend:**
- [x] **Framework**: React or Next.js
  - Large ecosystem, good for PWA
  - Excellent image handling libraries
  - Strong community support
- [x] **UI Library**: Tailwind CSS + shadcn/ui or Material-UI
  - Modern, responsive design
  - Pre-built components
  - Mobile-friendly
- [x] **State Management**: React Context or Zustand
- [x] **Image Handling**: React Dropzone for uploads

**Backend:**
- [x] **Language**: Python (best for AI/ML integration)
  - Alternative: Node.js (TypeScript)
- [x] **Framework**: FastAPI (Python) or Express (Node.js)
  - FastAPI: Built-in async support, great for AI integration
  - Express: JavaScript throughout stack
- [x] **Database**: PostgreSQL + S3-compatible storage for images
  - PostgreSQL for structured data (badges, inventory)
  - AWS S3 / Cloudflare R2 / Backblaze B2 for image storage
  - Alternative: SQLite for simpler single-user version

**AI/Computer Vision:**
- [x] **SELECTED: Ollama with Local Vision Models**
  - **Primary Model**: LLaVA 1.6 (llava:13b or llava:7b)
  - **Alternative Models to Test**:
    - BakLLaVA (bakllava)
    - LLaVA-Phi3 (smaller, faster)
    - Moondream2 (lightweight vision model)
  - **Pros**:
    - Zero ongoing costs
    - Complete privacy
    - Works offline
    - Easy setup with Ollama
  - **Cons**:
    - Requires local compute (8GB+ RAM recommended)
    - May need model experimentation
    - Slower than cloud APIs on basic hardware

  - **Fallback Options** (if local doesn't work well):
    - OpenAI GPT-4 Vision API for difficult images
    - Google Cloud Vision API
    - Custom YOLO model (future enhancement)

**Deployment:**
- [x] **Option 1**: Vercel/Netlify + AWS/Google Cloud
  - Vercel for frontend (free tier available)
  - AWS Lambda/Cloud Functions for backend
  - S3 for image storage

- [x] **Option 2**: Single Cloud Provider (AWS/Google Cloud/Azure)
  - All-in-one solution
  - Easier to manage

- [x] **Option 3**: Self-hosted (Docker on VPS)
  - Lower cost for high usage
  - More control
  - Requires maintenance

### 5.3 Database Schema (Preliminary)

**Badges Table:**
```sql
badges (
  badge_id UUID PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  category VARCHAR(100),
  description TEXT,
  scoutshop_url VARCHAR(500),
  reference_image_url VARCHAR(500),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

**Inventory Table:**
```sql
inventory (
  inventory_id UUID PRIMARY KEY,
  badge_id UUID REFERENCES badges(badge_id),
  quantity INTEGER DEFAULT 0,
  min_threshold INTEGER DEFAULT 5,
  last_counted_at TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

**Inventory_Snapshots Table (History):**
```sql
inventory_snapshots (
  snapshot_id UUID PRIMARY KEY,
  scan_id UUID REFERENCES scans(scan_id),
  badge_id UUID REFERENCES badges(badge_id),
  quantity INTEGER,
  snapshot_date TIMESTAMP,
  notes TEXT
)
```

**Scans Table (Image Upload Sessions):**
```sql
scans (
  scan_id UUID PRIMARY KEY,
  scan_date TIMESTAMP,
  status VARCHAR(50), -- 'processing', 'completed', 'failed'
  total_badges_detected INTEGER,
  processing_time_seconds INTEGER,
  notes TEXT
)
```

**Scan_Images Table:**
```sql
scan_images (
  image_id UUID PRIMARY KEY,
  scan_id UUID REFERENCES scans(scan_id),
  image_url VARCHAR(500),
  uploaded_at TIMESTAMP,
  processed_at TIMESTAMP,
  ai_confidence_avg DECIMAL(3,2)
)
```

**Badge_Detections Table (Individual detections):**
```sql
badge_detections (
  detection_id UUID PRIMARY KEY,
  image_id UUID REFERENCES scan_images(image_id),
  badge_id UUID REFERENCES badges(badge_id),
  confidence_score DECIMAL(3,2),
  bounding_box JSON, -- {x, y, width, height}
  verified BOOLEAN DEFAULT FALSE,
  corrected_badge_id UUID REFERENCES badges(badge_id)
)
```

**Adjustments Table (Manual changes):**
```sql
inventory_adjustments (
  adjustment_id UUID PRIMARY KEY,
  badge_id UUID REFERENCES badges(badge_id),
  adjustment_type VARCHAR(50), -- 'add', 'remove', 'correction'
  quantity_change INTEGER,
  reason TEXT,
  adjusted_at TIMESTAMP
)
```

## 6. User Stories

### 6.1 As a Cub Scout Leader

**Core Workflow:**
1. **Taking Photos**: "I want to quickly take photos of my badge boxes with my phone so I can count inventory without handling each badge"

2. **Uploading**: "I want to upload multiple photos at once so I don't have to wait between each one"

3. **AI Processing**: "I want the system to automatically identify and count the badges in my photos so I don't have to count manually"

4. **Verification**: "I want to see which badges were detected on each photo with confidence scores so I can verify the AI got it right"

5. **Corrections**: "I want to easily correct any badges the AI misidentified so my inventory is accurate"

6. **Viewing Results**: "I want to see a summary of all badge types and quantities so I know what I have in stock"

**Inventory Management:**
7. **Historical Tracking**: "I want to see how my inventory has changed over time so I can understand usage patterns"

8. **Low Stock Alerts**: "I want to be notified when badges are running low so I can reorder before running out"

9. **Manual Adjustments**: "I want to manually adjust counts when I award badges to cubs or receive new stock"

**Reporting:**
10. **Export Reports**: "I want to export my inventory to Excel so I can share it with other leaders or use it in budget reports"

11. **Visual Reports**: "I want to see charts showing my inventory by category so I can quickly understand stock levels"

**Ordering:**
12. **Shopping List**: "I want to generate a shopping list of badges I need to reorder with links to scoutshop.com.au"

13. **Quick Purchase**: "I want to click a button next to any badge to buy it on scoutshop.com.au so ordering is fast and easy"

**Convenience:**
14. **Mobile First**: "I want to use this on my phone since that's where my photos are and what I have with me at scout meetings"

15. **Quick Access**: "I want to see my last inventory count immediately when I open the app without uploading new photos"

## 7. Future Enhancements (Phase 2+)

### 7.1 Enhanced AI Features
- **Machine Learning Improvements**: Train custom model on actual badge photos for better accuracy
- **Duplicate Detection**: Automatically detect if same badge appears in multiple photos
- **Partial Badge Recognition**: Identify badges even when partially obscured
- **Background Removal**: Automatically isolate badges from background clutter

### 7.2 Extended Badge Coverage
- **All Sections**: Support Scouts, Venturers, Rovers badges
- **International**: Support badges from other countries
- **Historical Badges**: Database of discontinued/legacy badges
- **Custom Badges**: Support for group-specific or camp badges

### 7.3 Collaboration Features
- **Multi-User**: Multiple leaders can manage same inventory
- **Multi-Location**: Track badges across different storage locations
- **Borrowing/Lending**: Track badges loaned to other groups
- **Permissions**: Different access levels for leaders, assistants, quartermasters

### 7.4 Advanced Inventory
- **Predictive Ordering**: AI suggests what to order based on usage trends
- **Award Tracking**: Record when badges are awarded to which cubs
- **Expiry Tracking**: Track badges with time-sensitive components
- **Batch Tracking**: Track badges by purchase date/batch for quality issues

### 7.5 Integration
- **ScoutShop API**: Direct ordering through API (if available)
- **Email Notifications**: Alerts for low stock, processing complete
- **Calendar Integration**: Schedule regular inventory checks
- **Expense Tracking**: Integration with financial management tools
- **Scouts Australia Systems**: Integration with membership/achievement systems

### 7.6 Reporting & Analytics
- **Cost Analysis**: Track spending on badges over time
- **Usage Patterns**: Which badges are most awarded, seasonal trends
- **Forecasting**: Predict future badge needs
- **Budget Planning**: Generate budget requests based on historical data

### 7.7 User Experience
- **Voice Commands**: "How many Bronze Boomerang badges do I have?"
- **Offline Mode**: Full functionality when internet unavailable
- **Barcode Scanning**: Quick lookup of specific badges
- **AR Preview**: Use AR to see how badges look when worn
- **Native Mobile Apps**: iOS and Android apps with better camera integration

## 8. Constraints and Assumptions

### 8.1 Constraints
- **Budget**: TBD - AI API costs will be ongoing expense
- **Timeline**: TBD - MVP target: 2-3 months?
- **Team Size**: TBD - Solo developer or small team?
- **Data Collection**: Need to compile complete list of Australian Cub Scout badges with reference images
- **ScoutShop Integration**: Limited to URL linking unless API available
- **AI Accuracy**: Dependent on image quality and badge visibility

### 8.2 Assumptions
- **User Device**: Leaders have smartphone with camera (iOS or Android)
- **Internet**: Reliable internet connection for image upload and AI processing
- **Photo Quality**: Users can take reasonably clear, well-lit photos
- **Badge Condition**: Badges are in good condition and recognizable
- **Storage**: Badges stored in relatively organized manner (boxes, trays)
- **Update Frequency**: Inventory checked monthly or quarterly, not daily
- **Single User (MVP)**: Phase 1 focuses on single leader, one group

## 9. Success Criteria

### 9.1 MVP Success Metrics
- **Accuracy**: Badge recognition achieves 85%+ accuracy on test images
- **Time Savings**: Inventory count takes 5 minutes vs. 30+ minutes manual counting
- **User Satisfaction**: Single user (you) finds it valuable and uses it regularly
- **Data Quality**: Badge database includes all current Australian Cub Scout badges

### 9.2 Adoption Success (Post-MVP)
- **Usability**: User can complete full workflow (upload → report) in under 10 minutes
- **Reliability**: System successfully processes 95%+ of uploaded images
- **User Adoption**: 5+ leaders actively using the system
- **Retention**: Users conduct 2+ inventory scans per month

### 9.3 Business Success
- **Cost Efficiency**: Operating costs under $10/month per user
- **Feedback**: Positive feedback from beta testers
- **Expansion**: Viable path to add other scout sections (Scouts, Venturers)

## 10. Open Questions & Decisions Needed

### 10.1 Technical Decisions
1. **AI Provider**: ✅ **DECIDED - Ollama (Local Vision Models)**
   - **Choice**: Run vision models locally using Ollama
   - **Models**: LLaVA, BakLLaVA, or similar vision-capable models
   - **Pros**:
     - Zero per-image costs
     - Complete privacy (no data sent externally)
     - Works offline
     - Full control over model
   - **Cons**:
     - Requires decent hardware (GPU recommended but not required)
     - May have lower accuracy than GPT-4 Vision
     - Need to test different models for best badge recognition

2. **Deployment**: Where to host?
   - Cloud (Vercel + AWS): Easier, auto-scaling, potentially higher cost
   - Self-hosted (VPS): Lower cost, more control, more maintenance
   - What's your preference/experience level?

3. **Database**: Simple or robust?
   - SQLite: Simple, good for single user, easy to backup
   - PostgreSQL: More robust, better for future multi-user expansion

4. **Mobile Strategy**:
   - PWA (web app): Works everywhere, single codebase
   - Native app: Better performance, requires app store deployment
   - Recommendation: Start with PWA

### 10.2 Data & Content
5. **Badge Database**: How to compile?
   - Manual entry from Scouts Australia website?
   - Web scraping (if permitted)?
   - Do you have access to badge list/images already?
   - Can you get official badge images from Scouts Australia?

6. **ScoutShop Integration**:
   - Do they have an API? (Need to check scoutshop.com.au)
   - URL format for badge products?
   - Is there a product catalog we can reference?

### 10.3 User Experience
7. **Photo Guidelines**: How prescriptive should we be?
   - Strict requirements (specific distance, lighting, background)?
   - Flexible "just take a photo" approach?
   - Trade-off between accuracy and ease of use

8. **Verification Workflow**:
   - Should user verify every detection, or only low-confidence ones?
   - Auto-accept high confidence (>90%) detections?

### 10.4 Scope & Features
9. **MVP Feature Set**: What's absolutely essential for first version?
   - Minimum: Upload photos → AI detection → View counts → Export
   - Nice to have: Historical tracking, low stock alerts, shopping list
   - What can wait for v2?

10. **Multi-user**: When to add?
    - MVP: Single user only (simpler)
    - v1.5: Add authentication and multiple users
    - v2: Full multi-troop support

### 10.5 Development
11. **Your Technical Background**:
    - What's your experience level with web development?
    - Familiar with React, Python, or other frameworks?
    - Building this yourself or hiring developers?
    - How much time can you dedicate?

12. **Budget**:
    - Development budget: DIY or outsource?
    - Ongoing costs: AI API ($), hosting ($5-50/month), domain ($)
    - Willing to invest in quality badge reference images?

---

## 11. Recommended Next Steps

### Phase 1: Research & Planning (Week 1-2)
1. ✅ Define requirements (this document)
2. ⬜ Compile list of all Australian Cub Scout badges
3. ⬜ Gather reference images for each badge
4. ⬜ Research scoutshop.com.au product URLs
5. ⬜ Choose AI provider and test with sample badge photos
6. ⬜ Finalize technology stack based on your skills/budget

### Phase 2: MVP Development (Week 3-8)
1. ⬜ Set up development environment
2. ⬜ Build badge database
3. ⬜ Implement image upload interface
4. ⬜ Integrate AI badge recognition
5. ⬜ Build results review/correction UI
6. ⬜ Create inventory display and export
7. ⬜ Add ScoutShop links
8. ⬜ Testing with real badge photos

### Phase 3: Testing & Refinement (Week 9-12)
1. ⬜ Beta testing with actual badge inventory
2. ⬜ Refine AI accuracy
3. ⬜ Improve UI based on real usage
4. ⬜ Add documentation and help guides
5. ⬜ Deploy to production

### Phase 4: Expansion (Post-MVP)
1. ⬜ Gather feedback from other leaders
2. ⬜ Add historical tracking and analytics
3. ⬜ Expand to other scout sections
4. ⬜ Consider multi-user features

---

## Document History
- **Version 0.1** - Initial generic draft created
- **Version 0.2** - Refined based on user requirements for AI-powered badge inventory
- **Last Updated**: 2025-11-02
- **Status**: DRAFT - Ready for technical decision-making and development planning
