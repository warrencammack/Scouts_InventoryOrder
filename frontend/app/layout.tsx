'use client'

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { Upload, Package, FileText, Menu, X } from 'lucide-react'
import { useState } from 'react'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navItems = [
    { href: '/', label: 'Upload', icon: Upload },
    { href: '/inventory', label: 'Inventory', icon: Package },
    { href: '/reports', label: 'Reports', icon: FileText },
  ]

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/'
    }
    return pathname?.startsWith(href)
  }

  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="bg-scout-purple text-white shadow-lg sticky top-0 z-50">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between py-4">
              {/* Logo */}
              <Link href="/" className="flex items-center gap-2 hover:opacity-90 transition-opacity">
                <div className="w-10 h-10 bg-scout-gold rounded-full flex items-center justify-center">
                  <Package className="w-6 h-6 text-scout-purple" />
                </div>
                <div>
                  <h1 className="text-xl font-bold leading-tight">Scout Badge</h1>
                  <p className="text-xs text-white/80 leading-tight">Inventory Manager</p>
                </div>
              </Link>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center space-x-1">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const active = isActive(item.href)
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                        active
                          ? 'bg-white/20 text-white font-semibold'
                          : 'text-white/80 hover:bg-white/10 hover:text-white'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      {item.label}
                    </Link>
                  )
                })}
              </div>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 hover:bg-white/10 rounded-lg transition-colors"
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? (
                  <X className="w-6 h-6" />
                ) : (
                  <Menu className="w-6 h-6" />
                )}
              </button>
            </div>

            {/* Mobile Navigation */}
            {mobileMenuOpen && (
              <div className="md:hidden py-4 border-t border-white/20">
                <div className="flex flex-col space-y-2">
                  {navItems.map((item) => {
                    const Icon = item.icon
                    const active = isActive(item.href)
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={() => setMobileMenuOpen(false)}
                        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                          active
                            ? 'bg-white/20 text-white font-semibold'
                            : 'text-white/80 hover:bg-white/10 hover:text-white'
                        }`}
                      >
                        <Icon className="w-5 h-5" />
                        {item.label}
                      </Link>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </nav>

        <main className="container mx-auto px-4 py-8 min-h-screen">
          {children}
        </main>

        <footer className="bg-gray-100 mt-12 py-8 border-t border-gray-200">
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="text-center md:text-left">
                <p className="text-gray-900 font-semibold">Scout Badge Inventory Manager</p>
                <p className="text-sm text-gray-600 mt-1">AI-powered inventory tracking for Australian Cub Scout badges</p>
              </div>
              <div className="text-center md:text-right">
                <p className="text-sm text-gray-600">
                  Built with Next.js, FastAPI & Ollama
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  &copy; {new Date().getFullYear()} Scout Badge Inventory Manager
                </p>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
