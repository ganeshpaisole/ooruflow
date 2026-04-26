'use client'
import { usePathname, useRouter } from 'next/navigation'
import { Home, PlusCircle, History, User } from 'lucide-react'
import clsx from 'clsx'

const tabs = [
  { href: '/m/home',   label: 'Home',    icon: Home },
  { href: '/m/book',   label: 'Book',    icon: PlusCircle },
  { href: '/m/rides',  label: 'Rides',   icon: History },
  { href: '/m/profile',label: 'Profile', icon: User },
]

export default function MobileLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 max-w-md mx-auto">
      {/* Status bar spacer for standalone PWA */}
      <div className="h-safe-top bg-white" />

      <main className="flex-1 overflow-y-auto pb-20">
        {children}
      </main>

      {/* Bottom tab bar */}
      <nav className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white border-t border-gray-200 flex z-50">
        {tabs.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href)
          return (
            <button key={href} onClick={() => router.push(href)}
              className={clsx('flex-1 flex flex-col items-center py-2.5 gap-0.5 text-xs font-medium transition',
                active ? 'text-brand-600' : 'text-gray-400 hover:text-gray-600')}>
              <Icon size={22} strokeWidth={active ? 2.5 : 1.8} />
              {label}
            </button>
          )
        })}
      </nav>
    </div>
  )
}
