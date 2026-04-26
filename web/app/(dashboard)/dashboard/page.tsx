'use client'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import RideCard from '@/components/RideCard'
import { Ride } from '@/lib/types'
import Link from 'next/link'

export default function DashboardPage() {
  const { data: rides = [], isLoading } = useQuery<Ride[]>({
    queryKey: ['rides'],
    queryFn: async () => {
      const { data } = await api.get('/rides/')
      return data
    },
  })

  const upcoming = rides.filter((r) => ['pending', 'confirmed'].includes(r.status))
  const past = rides.filter((r) => ['completed', 'cancelled'].includes(r.status))

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Rides</h1>
          <p className="text-gray-500 mt-1">Book by 8 PM IST for next-day pickup</p>
        </div>
        <Link
          href="/book"
          className="bg-brand-600 hover:bg-brand-700 text-white font-semibold px-5 py-2.5 rounded-lg transition"
        >
          + Book Ride
        </Link>
      </div>

      {isLoading ? (
        <div className="text-center py-20 text-gray-400">Loading rides…</div>
      ) : (
        <>
          {upcoming.length > 0 && (
            <section className="mb-8">
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
                Upcoming
              </h2>
              <div className="space-y-3">
                {upcoming.map((ride) => <RideCard key={ride.id} ride={ride} />)}
              </div>
            </section>
          )}

          {past.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
                History
              </h2>
              <div className="space-y-3">
                {past.map((ride) => <RideCard key={ride.id} ride={ride} />)}
              </div>
            </section>
          )}

          {rides.length === 0 && (
            <div className="text-center py-20">
              <p className="text-5xl mb-4">🚗</p>
              <p className="text-gray-600 font-medium">No rides yet</p>
              <p className="text-gray-400 text-sm mt-1">Book your first ride for tomorrow</p>
              <Link href="/book" className="inline-block mt-4 bg-brand-600 text-white px-5 py-2 rounded-lg text-sm">
                Book Now
              </Link>
            </div>
          )}
        </>
      )}
    </div>
  )
}
