'use client'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { Ride } from '@/lib/types'
import RideCard from '@/components/RideCard'
import { useRouter } from 'next/navigation'

export default function MobileHome() {
  const router = useRouter()
  const { data: rides = [], isLoading } = useQuery<Ride[]>({
    queryKey: ['rides'],
    queryFn: async () => (await api.get('/rides/')).data,
  })
  const upcoming = rides.filter((r) => ['pending','confirmed'].includes(r.status))

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Good morning 👋</h1>
          <p className="text-sm text-gray-500">Book by 8 PM for tomorrow</p>
        </div>
        <span className="text-3xl">🚗</span>
      </div>

      <button onClick={() => router.push('/m/book')}
        className="w-full bg-brand-600 text-white font-semibold py-4 rounded-2xl text-base shadow-md shadow-orange-200 mb-6">
        + Book a Ride
      </button>

      <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Upcoming</h2>
      {isLoading ? (
        <div className="text-center py-10 text-gray-400">Loading…</div>
      ) : upcoming.length === 0 ? (
        <div className="text-center py-10 text-gray-400">
          <p className="text-4xl mb-2">📅</p>
          <p>No rides scheduled</p>
        </div>
      ) : (
        upcoming.map((r) => <RideCard key={r.id} ride={r} />)
      )}
    </div>
  )
}
