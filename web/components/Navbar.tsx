'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Car, CalendarDays, LayoutDashboard, LogOut, MapPin } from 'lucide-react'
import { logout } from '@/lib/auth'
import clsx from 'clsx'

const links = [
  { href: '/dashboard', label: 'My Rides', icon: LayoutDashboard },
  { href: '/book', label: 'Book Ride', icon: Car },
  { href: '/pool', label: 'Pool Rides', icon: MapPin },
  { href: '/recurring', label: 'Recurring', icon: CalendarDays },
]

export default function Navbar() {
  const pathname = usePathname()
  return (
    <aside className="w-56 min-h-screen bg-white border-r border-gray-200 flex flex-col">
      <div className="px-6 py-5 border-b border-gray-100">
        <span className="text-xl font-bold text-brand-600">🚗 OoruFlow</span>
        <p className="text-xs text-gray-400 mt-0.5">Bengaluru Commute</p>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ href, label, icon: Icon }) => (
          <Link
            key={href} href={href}
            className={clsx(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition',
              pathname === href
                ? 'bg-orange-50 text-brand-600'
                : 'text-gray-600 hover:bg-gray-50'
            )}
          >
            <Icon size={18} /> {label}
          </Link>
        ))}
      </nav>
      <div className="p-3 border-t border-gray-100">
        <button
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm text-gray-600 hover:bg-red-50 hover:text-red-600 transition"
        >
          <LogOut size={18} /> Sign Out
        </button>
      </div>
    </aside>
  )
}
