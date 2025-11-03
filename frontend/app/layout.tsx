import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Scout Badge Inventory Manager',
  description: 'AI-powered inventory management for Australian Cub Scout badges',
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-scout-purple text-white shadow-lg">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold">Scout Badge Inventory</h1>
              <div className="flex space-x-4">
                <a href="/" className="hover:text-scout-gold transition-colors">
                  Upload
                </a>
                <a href="/inventory" className="hover:text-scout-gold transition-colors">
                  Inventory
                </a>
                <a href="/reports" className="hover:text-scout-gold transition-colors">
                  Reports
                </a>
              </div>
            </div>
          </div>
        </nav>
        <main className="container mx-auto px-4 py-8">
          {children}
        </main>
        <footer className="bg-gray-100 mt-12 py-6">
          <div className="container mx-auto px-4 text-center text-gray-600">
            <p>Scout Badge Inventory Manager - Powered by AI</p>
            <p className="text-sm mt-2">Australian Cub Scout Badges</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
