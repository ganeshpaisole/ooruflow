'use client'
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { useRouter } from 'next/navigation'

export default function MobileBook() {
  const router = useRouter()
  const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1)
  const dateStr = tomorrow.toISOString().split('T')[0]

  const [form, setForm] = useState({
    pickup_location: '', dropoff_location: '',
    slot_date: dateStr, slot_start_time: '09:00', slot_end_time: '09:30',
    ride_type: 'solo',
  })

  function onChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
  }

  const book = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/rides/', {
        pickup_location: form.pickup_location,
        dropoff_location: form.dropoff_location,
        slot_start: `${form.slot_date}T${form.slot_start_time}:00+05:30`,
        slot_end:   `${form.slot_date}T${form.slot_end_time}:00+05:30`,
        ride_type: form.ride_type,
      })
      return data
    },
    onSuccess: () => { toast.success('Booked! Confirmed by 8 PM IST.'); router.push('/m/home') },
    onError: (e: any) => toast.error(e.response?.data?.detail || 'Failed'),
  })

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold text-gray-900 mb-1">Book a Ride</h1>
      <p className="text-sm text-gray-500 mb-6">Closes at 8 PM IST the night before</p>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Pickup</label>
          <input name="pickup_location" value={form.pickup_location} onChange={onChange}
            placeholder="e.g. Koramangala 5th Block" required
            className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Dropoff</label>
          <input name="dropoff_location" value={form.dropoff_location} onChange={onChange}
            placeholder="e.g. Whitefield, ITPL" required
            className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input type="date" name="slot_date" value={form.slot_date} onChange={onChange}
              min={dateStr}
              className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div className="col-span-1.5">
            <label className="block text-sm font-medium text-gray-700 mb-1">From</label>
            <input type="time" name="slot_start_time" value={form.slot_start_time} onChange={onChange}
              className="w-full border border-gray-300 rounded-xl px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div className="col-span-1.5">
            <label className="block text-sm font-medium text-gray-700 mb-1">To</label>
            <input type="time" name="slot_end_time" value={form.slot_end_time} onChange={onChange}
              className="w-full border border-gray-300 rounded-xl px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Ride Type</label>
          <div className="grid grid-cols-2 gap-3">
            {['solo','pool'].map((t) => (
              <button key={t} type="button" onClick={() => setForm((f) => ({ ...f, ride_type: t }))}
                className={`py-3.5 rounded-xl border font-semibold text-sm transition
                  ${form.ride_type === t ? 'bg-brand-600 text-white border-brand-600' : 'bg-white text-gray-600 border-gray-200'}`}>
                {t === 'solo' ? '🚗 Solo' : '🤝 Pool'}
              </button>
            ))}
          </div>
        </div>
        <button onClick={() => book.mutate()} disabled={book.isPending || !form.pickup_location || !form.dropoff_location}
          className="w-full bg-brand-600 hover:bg-brand-700 text-white font-bold py-4 rounded-2xl transition disabled:opacity-50 mt-2">
          {book.isPending ? 'Booking…' : 'Confirm Booking'}
        </button>
      </div>
    </div>
  )
}
