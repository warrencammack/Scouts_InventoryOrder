# Project Context: Scouts Badge Inventory System

## Project Owner
- **Name**: Warren Cammack
- **Role**: Cub Scout Leader (Australia)
- **Primary Use Case**: Managing inventory of Cub Scout badges

## Project Overview
This is an AI-powered badge inventory management system that uses computer vision to automatically count and track badge inventory from uploaded photos.

### Core Problem
- Warren regularly needs to check inventory of badges to ensure enough are available for cubs
- Manual counting is time-consuming and tedious
- Need to know what badges to reorder from scoutshop.com.au

### Core Solution
- Upload photos of badge boxes/storage
- AI recognizes and counts badges automatically
- Generates inventory reports
- Easy purchasing links to scoutshop.com.au

## Key Requirements

### Must Have (MVP)
1. Upload multiple images of badge boxes
2. AI badge recognition and counting
3. Database of all Australian Cub Scout badges with reference images
4. Inventory reports showing counts by badge type
5. Export to PDF/Excel
6. Links to scoutshop.com.au for purchasing

### Nice to Have (Future)
- Historical inventory tracking
- Low stock alerts
- Multi-user support
- Support for other scout sections (Scouts, Venturers, Rovers)
- Custom ML model for better accuracy

## Technical Preferences

### Platform
- **Primary Choice**: Progressive Web App (PWA)
  - Works on all devices
  - Mobile-first design
  - Camera access for photo upload
  - Single codebase

### Technology Stack (Recommended)
- **Frontend**: React/Next.js + Tailwind CSS
- **Backend**: Python (FastAPI) or Node.js (Express)
- **Database**: PostgreSQL + S3 for images (or SQLite for simpler MVP)
- **AI**: OpenAI GPT-4 Vision for MVP (quick to implement)
- **Deployment**: Vercel + AWS/Google Cloud or self-hosted VPS

### AI Approach
- **MVP**: OpenAI GPT-4 Vision API (~$0.01-0.03 per image)
- **Long-term**: Consider custom YOLO model to reduce per-image costs
- **Hybrid**: Object detection + image similarity matching

## Success Criteria
- 85%+ badge recognition accuracy
- Reduce inventory time from 30+ minutes to ~5 minutes
- Cost under $10/month per user
- Simple enough for non-technical leaders to use

## Open Questions (To Be Answered)
1. Warren's technical experience level - building himself or hiring?
2. Budget for development and ongoing costs?
3. Access to official Cub Scout badge database/images?
4. ScoutShop.com.au API availability?
5. Timeline expectations?

## Project Status
- **Phase**: Requirements gathering complete
- **Next Steps**:
  1. Compile Australian Cub Scout badge database
  2. Gather reference images
  3. Test AI feasibility with sample photos
  4. Finalize technology stack
  5. Begin MVP development

## Important Notes
- Focus on Australian Cub Scout badges first
- Mobile-friendly is critical (leaders use phones)
- Image quality will impact AI accuracy
- Need to balance ease-of-use vs. accuracy requirements
- Single user MVP, multi-user in future phases

## Files
- **Requirements**: `/Requirements.md` - Comprehensive requirements document
- **README**: `/README.md` - Basic project info
- **Action Plan**: `/ACTION_PLAN.md` - Detailed action plan with task tracking

## Task Tracking Protocol

### Automatic ACTION_PLAN.md Status Updates
Whenever you complete any work on this project, you MUST update the ACTION_PLAN.md file with the current status:

1. **Before Starting Work**: Review ACTION_PLAN.md to identify which action items you're working on
2. **While Working**: Update status from ⬜ to 🔄 (In progress)
3. **After Completing**: Update status from 🔄 to ✅ (Completed) and add **Completed** field with date
4. **Status Updates**: Keep ACTION_PLAN.md synchronized with actual project progress

### Status Update Format
When marking an action as completed:
```markdown
**Status**: ✅
**Completed**: YYYY-MM-DD
```

When marking an action as in progress:
```markdown
**Status**: 🔄
```

### Example
```markdown
### ACTION-200: Setup Python Backend Environment
**Status**: ✅
**Parallel**: 🟢
**Estimated Time**: 30 minutes
**Dependencies**: ACTION-001
**Completed**: 2025-11-02
```

### Required Actions
- After creating any files or completing any tasks, immediately update the corresponding ACTION in ACTION_PLAN.md
- Use the TodoWrite tool to track your work within each session
- Ensure the ACTION_PLAN.md reflects the current state of the project at all times
- When starting a new session, first review ACTION_PLAN.md to understand what's been completed
