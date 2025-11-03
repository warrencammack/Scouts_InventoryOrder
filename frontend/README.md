# Scout Badge Inventory - Frontend

Modern Next.js 14 frontend application for the Scout Badge Inventory Manager.

## Technology Stack

- **Next.js 14+** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **React Dropzone** - Drag-and-drop file upload
- **Recharts** - Chart library for data visualization

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout with navigation
│   ├── page.tsx           # Home page (upload interface)
│   ├── globals.css        # Global styles with Tailwind
│   ├── inventory/         # Inventory management page
│   │   └── page.tsx
│   └── reports/           # Reports and exports page
│       └── page.tsx
├── components/            # React components (to be added)
│   └── .gitkeep
├── lib/                   # Utilities and API client
│   ├── api.ts            # API client functions
│   └── types.ts          # TypeScript type definitions
├── public/               # Static assets
│   └── .gitkeep
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── next.config.mjs       # Next.js configuration
├── tailwind.config.ts    # Tailwind CSS configuration
└── postcss.config.js     # PostCSS configuration
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend server running on http://localhost:8000

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file (optional):
   ```bash
   cp .env.example .env.local
   ```

   Set the API URL if different from default:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The development server features:
- Hot reload on file changes
- Fast Refresh for React components
- API proxy to backend server
- TypeScript error checking

### Building for Production

Build the application:

```bash
npm run build
```

Start the production server:

```bash
npm start
```

### Linting

Run ESLint to check code quality:

```bash
npm run lint
```

## Configuration

### API Proxy

The Next.js configuration (`next.config.mjs`) includes an API proxy that forwards requests from `/api/*` to the backend server at `http://localhost:8000/api/*`. This avoids CORS issues during development.

### Tailwind CSS

Custom Scout-themed colors are defined in `tailwind.config.ts`:
- `scout-purple`: #4b0082 - Primary Scout color
- `scout-gold`: #ffd700 - Accent color
- `scout-green`: #006400 - Success color

### TypeScript

Strict mode is enabled in `tsconfig.json` for better type safety. Path aliases are configured:
- `@/*` maps to the root directory

## API Client

The API client (`lib/api.ts`) provides typed functions for all backend endpoints:

### Upload Functions
- `uploadImages(files: File[])` - Upload badge images

### Processing Functions
- `processScan(scanId: string)` - Process uploaded images
- `getProcessingProgress(scanId: string)` - Get processing status
- `getScan(scanId: string)` - Get scan details
- `getScanDetections(scanId: string)` - Get badge detections

### Inventory Functions
- `getInventory(filters?)` - Get all inventory items
- `getBadgeInventory(badgeId: string)` - Get specific badge inventory
- `updateInventory(badgeId: string, quantity: number)` - Update quantity
- `adjustInventory(badgeId: string, adjustment: number)` - Adjust quantity
- `getInventoryStats()` - Get inventory statistics

### Badge Functions
- `getBadges(category?)` - Get all badges
- `getBadge(badgeId: string)` - Get specific badge
- `searchBadges(query: string)` - Search badges

### Export Functions
- `exportCSV(options?)` - Export as CSV
- `exportPDF(options?)` - Export as PDF
- `exportShoppingList()` - Generate shopping list

## Type Definitions

All TypeScript types are defined in `lib/types.ts`:

- `Badge` - Badge information
- `Inventory` - Inventory item with stock levels
- `Scan` - Upload scan session
- `ScanImage` - Individual uploaded image
- `BadgeDetection` - AI-detected badge
- `InventoryAdjustment` - Inventory change record
- `ShoppingListItem` - Shopping list entry
- And more...

## Styling Guidelines

### Tailwind Utility Classes

Custom utility classes are defined in `globals.css`:

**Buttons:**
- `.btn-primary` - Purple Scout-themed button
- `.btn-secondary` - Gray secondary button

**Cards:**
- `.card` - White card with shadow and border

**Badge Status:**
- `.badge-status-low` - Red badge for low stock
- `.badge-status-ok` - Yellow badge for adequate stock
- `.badge-status-good` - Green badge for good stock

### Responsive Design

All components should be mobile-first and responsive:
- Use Tailwind's responsive prefixes (`sm:`, `md:`, `lg:`, `xl:`)
- Test on mobile, tablet, and desktop viewports
- Ensure touch-friendly button sizes (min 44x44px)

## Next Steps

The following components need to be implemented:

### ACTION-301: Image Upload Component
Create `components/ImageUpload.tsx` with:
- Drag-and-drop file upload
- Image preview grid
- File validation
- Progress indicators
- Mobile camera support

### ACTION-302: Processing Status Component
Create `components/ProcessingStatus.tsx` with:
- Real-time processing progress
- Current image indicator
- Time remaining estimate
- Error handling

### ACTION-303: Results Review Component
Create `components/ResultsReview.tsx` with:
- Image display with detected badges
- Confidence scores
- Correction interface
- Badge search and selection

### ACTION-304: Inventory Dashboard Component
Create `components/InventoryDashboard.tsx` with:
- Inventory table with filtering
- Search functionality
- Sorting options
- Stock status indicators

### ACTION-305: Charts Component
Create `components/InventoryCharts.tsx` with:
- Recharts integration
- Pie charts, bar charts, line charts
- Interactive visualizations

### ACTION-306: Shopping List Component
Create `components/ShoppingList.tsx` with:
- Low stock item display
- ScoutShop links
- Export functionality

### ACTION-307: Main Pages Enhancement
Update existing pages to use the new components

### ACTION-308: State Management
Implement React Context for global state management

### ACTION-310: PWA Configuration
Add Progressive Web App capabilities for mobile installation

## Development Tips

1. **Fast Refresh**: Save files to see changes instantly
2. **TypeScript**: Use VS Code for the best TypeScript experience
3. **Components**: Keep components small and focused
4. **API Calls**: Always use the API client functions from `lib/api.ts`
5. **Error Handling**: Display user-friendly error messages
6. **Loading States**: Show loading indicators for async operations
7. **Accessibility**: Use semantic HTML and ARIA labels

## Troubleshooting

### Port Already in Use

If port 3000 is already in use:
```bash
npx kill-port 3000
# or
npm run dev -- -p 3001
```

### API Connection Issues

1. Verify backend is running on http://localhost:8000
2. Check Next.js proxy configuration in `next.config.mjs`
3. Check browser console for CORS errors

### TypeScript Errors

Run type checking:
```bash
npx tsc --noEmit
```

### Module Not Found

Clear Next.js cache:
```bash
rm -rf .next
npm run dev
```

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Documentation](https://react.dev)
- [Axios Documentation](https://axios-http.com/docs/intro)

## License

See LICENSE file in the project root.
