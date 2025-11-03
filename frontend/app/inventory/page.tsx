'use client'

export default function InventoryPage() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Badge Inventory</h1>
        <p className="text-gray-600">
          View and manage your current badge stock levels
        </p>
      </div>

      <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded mb-8">
        <h3 className="font-semibold text-blue-900 mb-2">Coming Soon!</h3>
        <p className="text-blue-800">
          The inventory dashboard will be implemented in ACTION-304. It will display:
        </p>
        <ul className="list-disc list-inside text-blue-800 mt-2 space-y-1">
          <li>All badge inventory with images and current quantities</li>
          <li>Filtering by category (Milestone, Special Interest, etc.)</li>
          <li>Search functionality</li>
          <li>Stock status indicators (Low, Adequate, Well Stocked)</li>
          <li>Manual inventory adjustments</li>
        </ul>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Total Badges</h3>
          <p className="text-4xl font-bold text-scout-purple">0</p>
          <p className="text-sm text-gray-500 mt-1">Different badge types</p>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Total Quantity</h3>
          <p className="text-4xl font-bold text-scout-green">0</p>
          <p className="text-sm text-gray-500 mt-1">Badges in stock</p>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Low Stock Items</h3>
          <p className="text-4xl font-bold text-red-600">0</p>
          <p className="text-sm text-gray-500 mt-1">Need reordering</p>
        </div>
      </div>

      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Inventory List</h2>
          <div className="flex space-x-2">
            <button className="btn-secondary">
              Filter
            </button>
            <button className="btn-secondary">
              Export
            </button>
          </div>
        </div>

        <div className="text-center py-12 text-gray-500">
          <div className="text-6xl mb-4">📦</div>
          <p className="text-lg">No inventory data yet</p>
          <p className="text-sm mt-2">Upload and process badge images to populate inventory</p>
        </div>
      </div>
    </div>
  )
}
