'use client'

export default function ReportsPage() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Reports & Exports</h1>
        <p className="text-gray-600">
          Generate reports and shopping lists for your badge inventory
        </p>
      </div>

      <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded mb-8">
        <h3 className="font-semibold text-blue-900 mb-2">Coming Soon!</h3>
        <p className="text-blue-800">
          This page will be implemented with:
        </p>
        <ul className="list-disc list-inside text-blue-800 mt-2 space-y-1">
          <li>ACTION-305: Charts and visualizations</li>
          <li>ACTION-306: Shopping list generation</li>
          <li>ACTION-208: Export functionality (CSV, PDF)</li>
        </ul>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="card hover:shadow-lg transition-shadow cursor-pointer">
          <div className="text-4xl mb-4">📊</div>
          <h3 className="text-xl font-semibold mb-2">Inventory Charts</h3>
          <p className="text-gray-600 mb-4">
            Visualize your inventory with interactive charts and graphs
          </p>
          <ul className="text-sm text-gray-500 space-y-1">
            <li>• Stock levels by category</li>
            <li>• Inventory trends over time</li>
            <li>• Low stock alerts</li>
          </ul>
        </div>

        <div className="card hover:shadow-lg transition-shadow cursor-pointer">
          <div className="text-4xl mb-4">🛒</div>
          <h3 className="text-xl font-semibold mb-2">Shopping List</h3>
          <p className="text-gray-600 mb-4">
            Generate a shopping list for low stock badges
          </p>
          <ul className="text-sm text-gray-500 space-y-1">
            <li>• Automatic recommendations</li>
            <li>• Direct links to ScoutShop</li>
            <li>• Customizable quantities</li>
          </ul>
        </div>

        <div className="card hover:shadow-lg transition-shadow cursor-pointer">
          <div className="text-4xl mb-4">📄</div>
          <h3 className="text-xl font-semibold mb-2">Export CSV</h3>
          <p className="text-gray-600 mb-4">
            Download your inventory data as a spreadsheet
          </p>
          <button className="btn-primary w-full" disabled>
            Export CSV
          </button>
        </div>

        <div className="card hover:shadow-lg transition-shadow cursor-pointer">
          <div className="text-4xl mb-4">📑</div>
          <h3 className="text-xl font-semibold mb-2">Export PDF Report</h3>
          <p className="text-gray-600 mb-4">
            Generate a formatted PDF report with images
          </p>
          <button className="btn-primary w-full" disabled>
            Export PDF
          </button>
        </div>
      </div>

      <div className="mt-8 card bg-gradient-to-r from-scout-purple to-purple-700 text-white">
        <h3 className="text-xl font-semibold mb-4">Historical Analysis</h3>
        <p className="mb-4">
          Track inventory changes over time and identify usage patterns
        </p>
        <p className="text-sm text-white/80">
          This feature will be available in a future update (ACTION-601)
        </p>
      </div>
    </div>
  )
}
