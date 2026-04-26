import { Ride } from '@/lib/types'
import { format } from 'date-fns'
import clsx from 'clsx'

const STATUS_STYLES: Record<string, string> = {
  pending:     'bg-yellow-100 text-yellow-700',
  confirmed:   'bg-green-100 text-green-700',
  in_progress: 'bg-blue-100 text-blue-700',
  completed:   'bg-gray-100 text-gray-600',
  cancelled:   'bg-red-100 text-red-600',
}

export default function RideCard({ ride }: { ride: Ride }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition">
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-semibold text-gray-800">{ride.pickup_location}</p>
          <p className="text-sm text-gray-500 mt-0.5">→ {ride.dropoff_location}</p>
        </div>
        <span className={clsx('text-xs font-medium px-2.5 py-1 rounded-full capitalize', STATUS_STYLES[ride.status])}>
          {ride.status.replace('_', ' ')}
        </span>
      </div>
      <div className="flex items-center gap-4 text-sm text-gray-500">
        <span>🗓 {format(new Date(ride.slot_start), 'dd MMM, h:mm a')}</span>
        <span className={clsx('capitalize', ride.ride_type === 'pool' ? 'text-blue-600' : 'text-gray-500')}>
          {ride.ride_type === 'pool' ? '🤝 Pool' : '🚗 Solo'}
        </span>
        {ride.fare && <span className="font-medium text-gray-700">₹{ride.fare}</span>}
      </div>
    </div>
  )
}
