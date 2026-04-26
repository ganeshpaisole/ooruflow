'use client'
import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import { useRouter } from 'next/navigation'
import { FareEstimate } from '@/lib/types'

export default function BookRidePage() {
  const router = useRouter()
  const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1)
  const dateStr = tomorrow.toISOString().split('T')[0]

  const [form, setForm] = useState({
    pickup_location: '',
    dropoff_location: '',
    pickup_lat: '',  pickup_lng: '',
    dropoff_lat: '', dropoff_lng: '',
    slot_date: dateStr,
    slot_start_time: '09:00',
    slot_end_time: '09:30',
    ride_type: 'solo',
  })

  const fareQuery = useQuery<FareEstimate>({
    queryKey: ['fare', form.pickup_lat, form.pickup_lng, form.dropoff_lat, form.dropoff_lng, form.slot_date, form.slot_start_time],
    queryFn: async () => {
      const { data } = await api.get('/rides/estimate', {
        params: {
          pickup_lat: form.pickup_lat, pickup_lng: form.pickup_lng,
          dropoff_lat: form.dropoff_lat, dropoff_lng: form.dropoff_lng,
          ride_type: form.ride_type,
          slot_start: `${form.slot_date}T${form.slot_start_time}:00+05:30`,
        },
      })
      return data
    },
    enabled: !!(form.pickup_lat && form.dropoff_lat),
  })

  const bookMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        pickup_location: form.pickup_location,
        dropoff_location: form.dropoff_location,
        pickup_lat: Number(form.pickup_lat) || undefined,
        pickup_lng: Number(form.pickup_lng) || undefined,
        dropoff_lat: Number(form.dropoff_lat) || undefined,
        dropoff_lng: Number(form.dropoff_lng) || undefined,
        slot_start: `${form.slot_date}T${form.slot_start_time}:00+05:30`,
        slot_end: `${form.slot_date}T${form.slot_end_time}:00+05:30`,
        ride_type: form.ride_type,
      }
      const { data } = await api.post('/rides/', payload)
      return data
    },
    onSuccess: () => {
      toast.success('Ride booked! You will be confirmed by 8 PM IST.')
      router.push('/dashboard')
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Booking failed.')
    },
  })

  function onChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
  }

  const fare = fareQuery.data

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Book a Ride</h1>
      <p className="text-gray-500 mb-8">Booking closes at <strong>8 PM IST</strong> the day before your ride.</p>

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pickup Location</label>
            <input name="pickup_location" value={form.pickup_location} onChange={onChange} required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="Koramangala, Bengaluru" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Dropoff Location</label>
            <input name="dropoff_location" value={form.dropoff_location} onChange={onChange} required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="Whitefield, Bengaluru" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Pickup Lat, Lng</label>
            <div className="flex gap-2">
              <input name="pickup_lat" value={form.pickup_lat} onChange={onChange} placeholder="12.9352"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              <input name="pickup_lng" value={form.pickup_lng} onChange={onChange} placeholder="77.6245"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Dropoff Lat, Lng</label>
            <div className="flex gap-2">
              <input name="dropoff_lat" value={form.dropoff_lat} onChange={onChange} placeholder="12.9698"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              <input name="dropoff_lng" value={form.dropoff_lng} onChange={onChange} placeholder="77.7499"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input type="date" name="slot_date" value={form.slot_date} onChange={onChange}
              min={dateStr}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
            <input type="time" name="slot_start_time" value={form.slot_start_time} onChange={onChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Time</label>
            <input type="time" name="slot_end_time" value={form.slot_end_time} onChange={onChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Ride Type</label>
          <div className="flex gap-3">
            {['solo', 'pool'].map((t) => (
              <button key={t} type="button"
                onClick={() => setForm((f) => ({ ...f, ride_type: t }))}
                className={`flex-1 py-2.5 rounded-lg border text-sm font-medium capitalize transition
                  ${form.ride_type === t ? 'bg-brand-600 text-white border-brand-600' : 'bg-white text-gray-600 border-gray-300 hover:border-brand-500'}`}>
                {t === 'solo' ? '🚗 Solo' : '🤝 Pool'}
              </button>
            ))}
          </div>
        </div>

        {fare && (
          <div className={`rounded-lg p-4 ${fare.surge_active ? 'bg-orange-50 border border-orange-200' : 'bg-green-50 border border-green-200'}`}>
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-gray-700">Fare Estimate</p>
                <p className="text-xs text-gray-500 mt-0.5">{fare.distance_km} km</p>
              </div>
              {fare.surge_active && (
                <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full font-medium">
                  ⚡ {fare.surge_multiplier}× Surge
                </span>
              )}
            </div>
            <div className="mt-3 flex gap-6">
              <div>
                <p className="text-xs text-gray-500">Solo</p>
                <p className="text-lg font-bold text-gray-800">₹{fare.solo_fare_inr}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Pool (per person)</p>
                <p className="text-lg font-bold text-blue-600">₹{fare.pool_fare_per_person_inr}</p>
              </div>
            </div>
          </div>
        )}

        <button
          onClick={() => bookMutation.mutate()}
          disabled={bookMutation.isPending || !form.pickup_location || !form.dropoff_location}
          className="w-full bg-brand-600 hover:bg-brand-700 text-white font-semibold py-3 rounded-lg transition disabled:opacity-50"
        >
          {bookMutation.isPending ? 'Booking…' : 'Confirm Booking'}
        </button>
      </div>
    </div>
  )
}
