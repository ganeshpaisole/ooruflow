'use client'
import { logout } from '@/lib/auth'
import { LogOut, Bell, HelpCircle, Star, ChevronRight } from 'lucide-react'

const items = [
  { icon: Bell, label: 'Notifications' },
  { icon: Star, label: 'Rate & Review' },
  { icon: HelpCircle, label: 'Help & Support' },
]

export default function MobileProfile() {
  return (
    <div className="p-4">
      <div className="bg-brand-600 rounded-2xl p-5 text-white mb-6">
        <div className="w-14 h-14 bg-white/20 rounded-full flex items-center justify-center text-2xl mb-3">👤</div>
        <p className="font-bold text-lg">My Profile</p>
        <p className="text-orange-100 text-sm">OoruFlow Rider</p>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 divide-y divide-gray-50 mb-4">
        {items.map(({ icon: Icon, label }) => (
          <button key={label} className="flex items-center justify-between w-full px-4 py-3.5 hover:bg-gray-50 transition">
            <div className="flex items-center gap-3">
              <Icon size={18} className="text-gray-400" />
              <span className="text-sm font-medium text-gray-700">{label}</span>
            </div>
            <ChevronRight size={16} className="text-gray-300" />
          </button>
        ))}
      </div>

      <button onClick={logout}
        className="flex items-center gap-3 w-full bg-red-50 text-red-600 font-medium px-4 py-3.5 rounded-2xl">
        <LogOut size={18} /> Sign Out
      </button>
    </div>
  )
}
