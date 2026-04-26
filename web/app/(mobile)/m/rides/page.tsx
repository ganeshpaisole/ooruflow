'use client'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { Ride } from '@/lib/types'
import RideCard from '@/components/RideCard'
import { useState } from 'react'
import clsx from 'clsx'

export default function MobileRides() {
  const [tab, setTab] = useState<'upcoming'|'past'>('upcoming')
  const { data: rides = [], isLoading } = useQuery<Ride[]>({
    queryKey: ['rides'],
    queryFn: async () => (await api.get('/rides/')).data,
  })
  const upcoming = rides.filter((r) => ['pending','confirmed','in_progress'].includes(r.status))
  const past = rides.filter((r) => ['completed','cancelled'].includes(r.status))
  const list = tab === 'upcoming' ? upcoming : past

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-gray-900 mb-4">My Rides</h1>
      <div className="flex bg-gray-100 rounded-xl p-1 mb-5">
        {(['upcoming','past'] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={clsx('flex-1 py-2 rounded-lg text-sm font-medium capitalize transition',
              tab === t ? 'bg-white text-brand-600 shadow-sm' : 'text-gray-500')}>
            {t}
          </button>
        ))}
      </div>
      {isLoading ? <div className="text-center py-10 text-gray-400">Loading…</div>
        : list.length === 0 ? <div className="text-center py-10 text-gray-400">No rides</div>
        : list.map((r) => <RideCard key={r.id} ride={r} />)}
    </div>
  )
}
