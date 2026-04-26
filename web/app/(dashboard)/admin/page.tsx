'use client'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { AdminStats, Driver } from '@/lib/types'
import toast from 'react-hot-toast'

export default function AdminPage() {
  const qc = useQueryClient()

  const { data: stats } = useQuery<AdminStats>({
    queryKey: ['admin-stats'],
    queryFn: async () => (await api.get('/admin/stats')).data,
  })

  const { data: pendingDrivers = [] } = useQuery<Driver[]>({
    queryKey: ['pending-drivers'],
    queryFn: async () => (await api.get('/admin/drivers?status=pending_approval')).data,
  })

  const approve = useMutation({
    mutationFn: (id: number) => api.patch(`/admin/drivers/${id}/approve`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['pending-drivers'] }); qc.invalidateQueries({ queryKey: ['admin-stats'] }); toast.success('Driver approved!') },
  })

  const suspend = useMutation({
    mutationFn: (id: number) => api.patch(`/admin/drivers/${id}/suspend`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['pending-drivers'] }); toast.success('Driver suspended.') },
  })

  const statCards = [
    { label: 'Total Users', value: stats?.users.total ?? '—', color: 'text-blue-600' },
    { label: 'Total Drivers', value: stats?.drivers.total ?? '—', color: 'text-green-600' },
    { label: 'Online Drivers', value: stats?.drivers.online ?? '—', color: 'text-emerald-600' },
    { label: 'Total Rides', value: stats?.rides.total ?? '—', color: 'text-purple-600' },
    { label: 'Completed Rides', value: stats?.rides.completed ?? '—', color: 'text-gray-600' },
    { label: 'Revenue (INR)', value: stats ? `₹${stats.revenue.total_inr.toLocaleString()}` : '—', color: 'text-orange-600' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>

      <div className="grid grid-cols-3 gap-4 mb-10">
        {statCards.map(({ label, value, color }) => (
          <div key={label} className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-sm text-gray-500">{label}</p>
            <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      <h2 className="text-lg font-semibold text-gray-800 mb-4">
        Pending Driver Approvals
        {stats?.drivers.pending_approval ? (
          <span className="ml-2 text-sm bg-orange-100 text-orange-700 px-2.5 py-0.5 rounded-full">
            {stats.drivers.pending_approval}
          </span>
        ) : null}
      </h2>

      {pendingDrivers.length === 0 ? (
        <p className="text-gray-400 text-sm">No pending approvals.</p>
      ) : (
        <div className="space-y-3">
          {pendingDrivers.map((d) => (
            <div key={d.id} className="bg-white rounded-xl border border-gray-200 p-5 flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-800">{d.vehicle_model} — {d.vehicle_number}</p>
                <p className="text-sm text-gray-500 mt-0.5 capitalize">{d.vehicle_type} · License: {d.license_number}</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => approve.mutate(d.id)}
                  className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-4 py-1.5 rounded-lg transition">
                  Approve
                </button>
                <button onClick={() => suspend.mutate(d.id)}
                  className="bg-red-50 hover:bg-red-100 text-red-600 text-sm font-medium px-4 py-1.5 rounded-lg transition">
                  Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
