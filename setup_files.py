"""
OoruFlow — Full-stack scaffolding script.
Creates the Next.js web app and Flutter mobile app from scratch.

Run from D:\\OoruFlow:
    python setup_files.py
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

def write(path, content):
    full = os.path.join(BASE, path.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content.lstrip("\n"))
    print(f"  ✓ {path}")


# ═══════════════════════════════════════════════════════════════════════════
#  NEXT.JS WEB APP
# ═══════════════════════════════════════════════════════════════════════════

write("web/package.json", """
{
  "name": "ooruflow-web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18",
    "react-dom": "^18",
    "next-pwa": "^5.6.0",
    "axios": "^1.6.7",
    "@tanstack/react-query": "^5.18.1",
    "js-cookie": "^3.0.5",
    "react-hot-toast": "^2.4.1",
    "lucide-react": "^0.344.0",
    "date-fns": "^3.3.1",
    "clsx": "^2.1.0"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "@types/js-cookie": "^3.0.6",
    "autoprefixer": "^10.0.1",
    "postcss": "^8",
    "tailwindcss": "^3.3.0",
    "eslint": "^8",
    "eslint-config-next": "14.1.0"
  }
}
""")

write("web/next.config.js", """
/** @type {import('next').NextConfig} */
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
})
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_RAZORPAY_KEY_ID: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID || '',
    NEXT_PUBLIC_GMAPS_KEY: process.env.NEXT_PUBLIC_GMAPS_KEY || '',
  },
}
module.exports = withPWA(nextConfig)
""")

write("web/tailwind.config.js", """
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: { 500: '#f97316', 600: '#ea580c', 700: '#c2410c' },
      },
    },
  },
  plugins: [],
}
""")

write("web/postcss.config.js", """
module.exports = { plugins: { tailwindcss: {}, autoprefixer: {} } }
""")

write("web/tsconfig.json", """{
  "compilerOptions": {
    "target": "es5", "lib": ["dom","dom.iterable","esnext"],
    "allowJs": true, "skipLibCheck": true, "strict": true, "noEmit": true,
    "esModuleInterop": true, "module": "esnext", "moduleResolution": "bundler",
    "resolveJsonModule": true, "isolatedModules": true, "jsx": "preserve",
    "incremental": true, "plugins": [{"name":"next"}], "paths": {"@/*":["./*"]}
  },
  "include": ["next-env.d.ts","**/*.ts","**/*.tsx",".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
""")

write("web/.env.local.example", """
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_key_id
NEXT_PUBLIC_GMAPS_KEY=your_google_maps_key
""")

# ── lib/types.ts ────────────────────────────────────────────────────────────

write("web/lib/types.ts", """
export type UserRole = 'rider' | 'driver' | 'admin'
export type RideStatus = 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled'
export type RideType = 'solo' | 'pool'
export type PaymentStatus = 'pending' | 'paid' | 'failed' | 'refunded'
export type DriverStatus = 'pending_approval' | 'approved' | 'suspended' | 'offline' | 'online'

export interface User {
  id: number
  full_name: string
  email: string
  phone?: string
  role: UserRole
  is_active: boolean
}

export interface Ride {
  id: number
  user_id: number
  driver_id?: number
  ride_type: RideType
  pickup_location: string
  dropoff_location: string
  pickup_lat?: number
  pickup_lng?: number
  dropoff_lat?: number
  dropoff_lng?: number
  slot_start: string
  slot_end: string
  confirmation_deadline: string
  status: RideStatus
  fare?: number
  payment_status: PaymentStatus
  created_at: string
}

export interface Driver {
  id: number
  user_id: number
  vehicle_number: string
  vehicle_model: string
  vehicle_type: string
  license_number: string
  status: DriverStatus
  avg_rating: number
  total_rides: number
}

export interface FareEstimate {
  distance_km: number
  solo_fare_inr: number
  pool_fare_per_person_inr: number
  surge_active: boolean
  surge_multiplier: number
}

export interface AdminStats {
  users: { total: number }
  drivers: { total: number; online: number; pending_approval: number }
  rides: { total: number; completed: number }
  revenue: { total_inr: number }
}
""")

# ── lib/api.ts ──────────────────────────────────────────────────────────────

write("web/lib/api.ts", """
import axios from 'axios'
import Cookies from 'js-cookie'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = Cookies.get('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401 && typeof window !== 'undefined') {
      Cookies.remove('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
""")

# ── lib/auth.ts ─────────────────────────────────────────────────────────────

write("web/lib/auth.ts", """
import Cookies from 'js-cookie'
import api from './api'

export async function login(email: string, password: string) {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const { data } = await api.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  Cookies.set('access_token', data.access_token, { expires: 1, sameSite: 'strict' })
  return data
}

export async function signup(payload: {
  full_name: string; email: string; phone?: string; password: string
}) {
  const { data } = await api.post('/auth/signup', payload)
  return data
}

export function logout() {
  Cookies.remove('access_token')
  window.location.href = '/login'
}

export function getToken() {
  return Cookies.get('access_token')
}
""")

# ── middleware.ts ────────────────────────────────────────────────────────────

write("web/middleware.ts", """
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const PUBLIC = ['/', '/login', '/signup']

export function middleware(req: NextRequest) {
  const token = req.cookies.get('access_token')?.value
  const { pathname } = req.nextUrl

  const isPublic = PUBLIC.some((p) => pathname === p)

  if (!token && !isPublic) {
    return NextResponse.redirect(new URL('/login', req.url))
  }
  if (token && (pathname === '/login' || pathname === '/signup')) {
    return NextResponse.redirect(new URL('/dashboard', req.url))
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
""")

# ── app/globals.css ──────────────────────────────────────────────────────────

write("web/app/globals.css", """
@tailwind base;
@tailwind components;
@tailwind utilities;
""")

# ── app/layout.tsx ───────────────────────────────────────────────────────────

write("web/app/layout.tsx", """
import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Providers from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'OoruFlow — Bengaluru Office Commute',
  description: 'Plan your office ride the night before.',
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'OoruFlow',
  },
}

export const viewport: Viewport = {
  themeColor: '#f97316',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="apple-touch-icon" href="/icon-192.svg" />
      </head>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
""")

# ── app/providers.tsx ────────────────────────────────────────────────────────

write("web/app/providers.tsx", """
'use client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { useState } from 'react'

export default function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => new QueryClient())
  return (
    <QueryClientProvider client={client}>
      {children}
      <Toaster position="top-right" />
    </QueryClientProvider>
  )
}
""")

# ── app/page.tsx (root → redirect) ──────────────────────────────────────────

write("web/app/page.tsx", """
import { redirect } from 'next/navigation'
import { headers } from 'next/headers'

export default function Root() {
  const ua = headers().get('user-agent') || ''
  const isMobile = /android|iphone|ipad|ipod|mobile/i.test(ua)
  redirect(isMobile ? '/m/home' : '/dashboard')
}
""")

# ── app/(auth)/login/page.tsx ────────────────────────────────────────────────

write("web/app/(auth)/login/page.tsx", """
'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { login } from '@/lib/auth'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email, password)
      toast.success('Welcome back!')
      router.push('/dashboard')
    } catch {
      toast.error('Invalid email or password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-orange-50">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-brand-700 mb-2">OoruFlow</h1>
        <p className="text-gray-500 mb-8">Sign in to your account</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit" disabled={loading}
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-semibold py-2.5 rounded-lg transition disabled:opacity-50"
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-6">
          No account?{' '}
          <Link href="/signup" className="text-brand-600 font-medium hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  )
}
""")

# ── app/(auth)/signup/page.tsx ───────────────────────────────────────────────

write("web/app/(auth)/signup/page.tsx", """
'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { signup } from '@/lib/auth'

export default function SignupPage() {
  const router = useRouter()
  const [form, setForm] = useState({ full_name: '', email: '', phone: '', password: '' })
  const [loading, setLoading] = useState(false)

  function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      await signup(form)
      toast.success('Account created! Please sign in.')
      router.push('/login')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Signup failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-orange-50">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-brand-700 mb-2">Create Account</h1>
        <p className="text-gray-500 mb-8">Join OoruFlow today</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          {[
            { label: 'Full Name', name: 'full_name', type: 'text', placeholder: 'Priya Sharma' },
            { label: 'Email', name: 'email', type: 'email', placeholder: 'you@example.com' },
            { label: 'Phone', name: 'phone', type: 'tel', placeholder: '+91 98765 43210' },
            { label: 'Password', name: 'password', type: 'password', placeholder: '••••••••' },
          ].map(({ label, name, type, placeholder }) => (
            <div key={name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              <input
                type={type} name={name} value={form[name as keyof typeof form]}
                onChange={onChange} placeholder={placeholder}
                required={name !== 'phone'}
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
          ))}
          <button
            type="submit" disabled={loading}
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-semibold py-2.5 rounded-lg transition disabled:opacity-50"
          >
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link href="/login" className="text-brand-600 font-medium hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
""")

# ── components/Navbar.tsx ────────────────────────────────────────────────────

write("web/components/Navbar.tsx", """
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
""")

# ── components/RideCard.tsx ──────────────────────────────────────────────────

write("web/components/RideCard.tsx", """
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
""")

# ── app/(dashboard)/layout.tsx ───────────────────────────────────────────────

write("web/app/(dashboard)/layout.tsx", """
import Navbar from '@/components/Navbar'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Navbar />
      <main className="flex-1 p-8 overflow-y-auto">{children}</main>
    </div>
  )
}
""")

# ── app/(dashboard)/dashboard/page.tsx ──────────────────────────────────────

write("web/app/(dashboard)/dashboard/page.tsx", """
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
""")

# ── app/(dashboard)/book/page.tsx ────────────────────────────────────────────

write("web/app/(dashboard)/book/page.tsx", """
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
""")

# ── app/(dashboard)/admin/page.tsx ───────────────────────────────────────────

write("web/app/(dashboard)/admin/page.tsx", """
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
""")

print("\n✅ Next.js web app files written.\n")

# ═══════════════════════════════════════════════════════════════════════════
#  FLUTTER MOBILE APP
# ═══════════════════════════════════════════════════════════════════════════

write("mobile/pubspec.yaml", """
name: ooruflow
description: OoruFlow — Bengaluru Office Commute App

publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0
  shared_preferences: ^2.2.2
  provider: ^6.1.2
  google_maps_flutter: ^2.5.3
  geolocator: ^11.0.0
  web_socket_channel: ^2.4.4
  intl: ^0.19.0
  razorpay_flutter: ^1.3.6
  firebase_core: ^2.25.4
  firebase_messaging: ^14.7.15
  flutter_local_notifications: ^16.3.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
""")

write("mobile/lib/config/api_config.dart", """
class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://10.0.2.2:8000', // Android emulator → localhost
  );
}
""")

write("mobile/lib/config/theme.dart", """
import 'package:flutter/material.dart';

class AppTheme {
  static const Color primary = Color(0xFFF97316);   // orange-500
  static const Color primaryDark = Color(0xFFEA580C); // orange-600

  static ThemeData get light => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: primary,
      brightness: Brightness.light,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.white,
      foregroundColor: Color(0xFF1F2937),
      elevation: 0,
      centerTitle: false,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primary,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
    ),
  );
}
""")

write("mobile/lib/models/user.dart", """
class User {
  final int id;
  final String fullName;
  final String email;
  final String? phone;
  final String role;
  final bool isActive;

  const User({
    required this.id, required this.fullName, required this.email,
    this.phone, required this.role, required this.isActive,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
    id: json['id'], fullName: json['full_name'], email: json['email'],
    phone: json['phone'], role: json['role'], isActive: json['is_active'],
  );
}
""")

write("mobile/lib/models/ride.dart", """
class Ride {
  final int id;
  final int userId;
  final int? driverId;
  final String rideType;
  final String pickupLocation;
  final String dropoffLocation;
  final double? pickupLat;
  final double? pickupLng;
  final double? dropoffLat;
  final double? dropoffLng;
  final DateTime slotStart;
  final DateTime slotEnd;
  final String status;
  final double? fare;
  final String paymentStatus;
  final DateTime createdAt;

  const Ride({
    required this.id, required this.userId, this.driverId,
    required this.rideType, required this.pickupLocation, required this.dropoffLocation,
    this.pickupLat, this.pickupLng, this.dropoffLat, this.dropoffLng,
    required this.slotStart, required this.slotEnd, required this.status,
    this.fare, required this.paymentStatus, required this.createdAt,
  });

  factory Ride.fromJson(Map<String, dynamic> json) => Ride(
    id: json['id'], userId: json['user_id'], driverId: json['driver_id'],
    rideType: json['ride_type'],
    pickupLocation: json['pickup_location'], dropoffLocation: json['dropoff_location'],
    pickupLat: json['pickup_lat']?.toDouble(), pickupLng: json['pickup_lng']?.toDouble(),
    dropoffLat: json['dropoff_lat']?.toDouble(), dropoffLng: json['dropoff_lng']?.toDouble(),
    slotStart: DateTime.parse(json['slot_start']),
    slotEnd: DateTime.parse(json['slot_end']),
    status: json['status'], fare: json['fare']?.toDouble(),
    paymentStatus: json['payment_status'],
    createdAt: DateTime.parse(json['created_at']),
  );

  bool get isUpcoming => status == 'pending' || status == 'confirmed';
  bool get isPool => rideType == 'pool';
}
""")

write("mobile/lib/models/driver.dart", """
class Driver {
  final int id;
  final int userId;
  final String vehicleNumber;
  final String vehicleModel;
  final String vehicleType;
  final String licenseNumber;
  final String status;
  final double? currentLat;
  final double? currentLng;
  final double avgRating;
  final int totalRides;

  const Driver({
    required this.id, required this.userId, required this.vehicleNumber,
    required this.vehicleModel, required this.vehicleType, required this.licenseNumber,
    required this.status, this.currentLat, this.currentLng,
    required this.avgRating, required this.totalRides,
  });

  factory Driver.fromJson(Map<String, dynamic> json) => Driver(
    id: json['id'], userId: json['user_id'],
    vehicleNumber: json['vehicle_number'], vehicleModel: json['vehicle_model'],
    vehicleType: json['vehicle_type'], licenseNumber: json['license_number'],
    status: json['status'],
    currentLat: json['current_lat']?.toDouble(),
    currentLng: json['current_lng']?.toDouble(),
    avgRating: (json['avg_rating'] ?? 5.0).toDouble(),
    totalRides: json['total_rides'] ?? 0,
  );

  bool get isOnline => status == 'online';
}
""")

write("mobile/lib/services/api_service.dart", """
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../config/api_config.dart';

class ApiService {
  static final ApiService _instance = ApiService._();
  factory ApiService() => _instance;
  ApiService._();

  Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  Future<Map<String, String>> _headers({bool form = false}) async {
    final token = await _getToken();
    return {
      'Content-Type': form ? 'application/x-www-form-urlencoded' : 'application/json',
      if (token != null) 'Authorization': 'Bearer \$token',
    };
  }

  Future<dynamic> get(String path) async {
    final resp = await http.get(
      Uri.parse('\${ApiConfig.baseUrl}\$path'),
      headers: await _headers(),
    );
    return _parse(resp);
  }

  Future<dynamic> post(String path, Map<String, dynamic> body, {bool form = false}) async {
    final resp = await http.post(
      Uri.parse('\${ApiConfig.baseUrl}\$path'),
      headers: await _headers(form: form),
      body: form ? body.map((k, v) => MapEntry(k, v.toString())) : jsonEncode(body),
    );
    return _parse(resp);
  }

  Future<dynamic> patch(String path, Map<String, dynamic> body) async {
    final resp = await http.patch(
      Uri.parse('\${ApiConfig.baseUrl}\$path'),
      headers: await _headers(),
      body: jsonEncode(body),
    );
    return _parse(resp);
  }

  dynamic _parse(http.Response resp) {
    if (resp.statusCode >= 200 && resp.statusCode < 300) {
      if (resp.body.isEmpty) return null;
      return jsonDecode(resp.body);
    }
    final detail = jsonDecode(resp.body)['detail'] ?? 'Request failed';
    throw Exception(detail);
  }
}
""")

write("mobile/lib/services/auth_service.dart", """
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';
import '../models/user.dart';

class AuthService {
  final _api = ApiService();

  Future<String> login(String email, String password) async {
    final data = await _api.post('/auth/login',
      {'username': email, 'password': password}, form: true);
    final token = data['access_token'] as String;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', token);
    return token;
  }

  Future<User> signup(String fullName, String email, String password, String? phone) async {
    final data = await _api.post('/auth/signup', {
      'full_name': fullName, 'email': email, 'password': password,
      if (phone != null && phone.isNotEmpty) 'phone': phone,
    });
    return User.fromJson(data);
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
  }

  Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.containsKey('access_token');
  }
}
""")

write("mobile/lib/providers/auth_provider.dart", """
import 'package:flutter/material.dart';
import '../models/user.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  final _authService = AuthService();
  final _api = ApiService();

  User? _user;
  bool _loading = false;
  String? _error;

  User? get user => _user;
  bool get loading => _loading;
  String? get error => _error;
  bool get isLoggedIn => _user != null;
  bool get isDriver => _user?.role == 'driver';
  bool get isAdmin => _user?.role == 'admin';

  Future<void> checkAuth() async {
    if (!await _authService.isLoggedIn()) return;
    try {
      // Decode user from existing token (lightweight check)
      _loading = true; notifyListeners();
      final rides = await _api.get('/rides/');
      // If token is valid, we're logged in — fetch user from token claims
      _loading = false; notifyListeners();
    } catch (_) {
      await _authService.logout();
      _loading = false; notifyListeners();
    }
  }

  Future<bool> login(String email, String password) async {
    _loading = true; _error = null; notifyListeners();
    try {
      await _authService.login(email, password);
      _loading = false; notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _loading = false; notifyListeners();
      return false;
    }
  }

  Future<bool> signup(String fullName, String email, String password, String? phone) async {
    _loading = true; _error = null; notifyListeners();
    try {
      _user = await _authService.signup(fullName, email, password, phone);
      _loading = false; notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _loading = false; notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await _authService.logout();
    _user = null; notifyListeners();
  }
}
""")

write("mobile/lib/providers/ride_provider.dart", """
import 'package:flutter/material.dart';
import '../models/ride.dart';
import '../services/api_service.dart';

class RideProvider extends ChangeNotifier {
  final _api = ApiService();

  List<Ride> _rides = [];
  bool _loading = false;
  String? _error;

  List<Ride> get rides => _rides;
  List<Ride> get upcoming => _rides.where((r) => r.isUpcoming).toList();
  List<Ride> get past => _rides.where((r) => !r.isUpcoming).toList();
  bool get loading => _loading;
  String? get error => _error;

  Future<void> fetchRides() async {
    _loading = true; notifyListeners();
    try {
      final data = await _api.get('/rides/') as List;
      _rides = data.map((j) => Ride.fromJson(j)).toList();
      _error = null;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
    }
    _loading = false; notifyListeners();
  }

  Future<Map<String, dynamic>?> estimateFare({
    required double pickupLat, required double pickupLng,
    required double dropoffLat, required double dropoffLng,
    required String rideType, required String slotStart,
  }) async {
    try {
      final params = '?pickup_lat=\$pickupLat&pickup_lng=\$pickupLng'
          '&dropoff_lat=\$dropoffLat&dropoff_lng=\$dropoffLng'
          '&ride_type=\$rideType&slot_start=\$slotStart';
      final data = await _api.get('/rides/estimate\$params');
      return data as Map<String, dynamic>;
    } catch (_) { return null; }
  }

  Future<Ride?> bookRide(Map<String, dynamic> payload) async {
    try {
      final data = await _api.post('/rides/', payload);
      final ride = Ride.fromJson(data);
      _rides.insert(0, ride);
      notifyListeners();
      return ride;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return null;
    }
  }

  Future<bool> cancelRide(int rideId) async {
    try {
      await _api.patch('/rides/\$rideId/cancel', {});
      _rides.removeWhere((r) => r.id == rideId);
      notifyListeners();
      return true;
    } catch (_) { return false; }
  }
}
""")

write("mobile/lib/widgets/app_button.dart", """
import 'package:flutter/material.dart';

class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final bool loading;
  final bool outlined;
  final Color? color;

  const AppButton({
    super.key, required this.label, this.onPressed,
    this.loading = false, this.outlined = false, this.color,
  });

  @override
  Widget build(BuildContext context) {
    final c = color ?? const Color(0xFFF97316);
    if (outlined) {
      return OutlinedButton(
        onPressed: loading ? null : onPressed,
        style: OutlinedButton.styleFrom(
          foregroundColor: c, side: BorderSide(color: c),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        child: _child,
      );
    }
    return ElevatedButton(
      onPressed: loading ? null : onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: c, foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      child: _child,
    );
  }

  Widget get _child => loading
      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
      : Text(label, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15));
}
""")

write("mobile/lib/widgets/ride_card.dart", """
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/ride.dart';

class RideCard extends StatelessWidget {
  final Ride ride;
  final VoidCallback? onTap;

  const RideCard({super.key, required this.ride, this.onTap});

  Color _statusColor(String s) => switch (s) {
    'pending'    => const Color(0xFFFACC15),
    'confirmed'  => const Color(0xFF22C55E),
    'in_progress'=> const Color(0xFF3B82F6),
    'completed'  => const Color(0xFF6B7280),
    _            => const Color(0xFFEF4444),
  };

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 1,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(ride.pickupLocation, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
                  const SizedBox(height: 2),
                  Text('→ \${ride.dropoffLocation}', style: TextStyle(color: Colors.grey[600], fontSize: 13)),
                ]),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: _statusColor(ride.status).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(ride.status.replaceAll('_', ' ').toUpperCase(),
                  style: TextStyle(color: _statusColor(ride.status), fontSize: 11, fontWeight: FontWeight.w700)),
              ),
            ]),
            const SizedBox(height: 10),
            Row(children: [
              Icon(Icons.schedule, size: 15, color: Colors.grey[500]),
              const SizedBox(width: 4),
              Text(DateFormat('dd MMM, h:mm a').format(ride.slotStart.toLocal()),
                style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              const SizedBox(width: 12),
              Icon(ride.isPool ? Icons.people : Icons.person, size: 15, color: Colors.grey[500]),
              const SizedBox(width: 4),
              Text(ride.isPool ? 'Pool' : 'Solo', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              if (ride.fare != null) ...[
                const SizedBox(width: 12),
                Text('₹\${ride.fare!.toStringAsFixed(0)}',
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13)),
              ],
            ]),
          ]),
        ),
      ),
    );
  }
}
""")

write("mobile/lib/screens/auth/login_screen.dart", """
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/app_button.dart';
import 'signup_screen.dart';
import '../rider/home_screen.dart';
import '../driver/driver_home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailCtrl = TextEditingController();
  final _passCtrl  = TextEditingController();

  Future<void> _login() async {
    final auth = context.read<AuthProvider>();
    final ok = await auth.login(_emailCtrl.text.trim(), _passCtrl.text);
    if (!mounted) return;
    if (ok) {
      Navigator.pushReplacement(context, MaterialPageRoute(
        builder: (_) => auth.isDriver ? const DriverHomeScreen() : const RiderHomeScreen(),
      ));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(auth.error ?? 'Login failed')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    return Scaffold(
      backgroundColor: const Color(0xFFFFF7ED),
      body: SafeArea(child: Center(child: SingleChildScrollView(padding: const EdgeInsets.all(24), child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('🚗 OoruFlow', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFFC2410C))),
          const SizedBox(height: 4),
          Text('Bengaluru Office Commute', style: TextStyle(color: Colors.grey[600])),
          const SizedBox(height: 40),
          TextField(controller: _emailCtrl, keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email_outlined))),
          const SizedBox(height: 16),
          TextField(controller: _passCtrl, obscureText: true,
            decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock_outline))),
          const SizedBox(height: 24),
          AppButton(label: 'Sign In', onPressed: _login, loading: auth.loading),
          const SizedBox(height: 16),
          TextButton(
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SignupScreen())),
            child: const Text("Don't have an account? Sign up"),
          ),
        ],
      )))),
    );
  }
}
""")

write("mobile/lib/screens/auth/signup_screen.dart", """
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/app_button.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});
  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _nameCtrl  = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _passCtrl  = TextEditingController();

  Future<void> _signup() async {
    final auth = context.read<AuthProvider>();
    final ok = await auth.signup(_nameCtrl.text.trim(), _emailCtrl.text.trim(),
        _passCtrl.text, _phoneCtrl.text.trim());
    if (!mounted) return;
    if (ok) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Account created! Please sign in.')));
      Navigator.pop(context);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(auth.error ?? 'Signup failed')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    return Scaffold(
      appBar: AppBar(title: const Text('Create Account')),
      body: SingleChildScrollView(padding: const EdgeInsets.all(24), child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(controller: _nameCtrl, decoration: const InputDecoration(labelText: 'Full Name', prefixIcon: Icon(Icons.person_outline))),
          const SizedBox(height: 16),
          TextField(controller: _emailCtrl, keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email_outlined))),
          const SizedBox(height: 16),
          TextField(controller: _phoneCtrl, keyboardType: TextInputType.phone,
            decoration: const InputDecoration(labelText: 'Phone (optional)', prefixIcon: Icon(Icons.phone_outlined))),
          const SizedBox(height: 16),
          TextField(controller: _passCtrl, obscureText: true,
            decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock_outline))),
          const SizedBox(height: 28),
          AppButton(label: 'Create Account', onPressed: _signup, loading: auth.loading),
        ],
      )),
    );
  }
}
""")

write("mobile/lib/screens/rider/home_screen.dart", """
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/ride_provider.dart';
import '../../widgets/ride_card.dart';
import '../../widgets/app_button.dart';
import 'book_ride_screen.dart';
import 'my_rides_screen.dart';

class RiderHomeScreen extends StatefulWidget {
  const RiderHomeScreen({super.key});
  @override
  State<RiderHomeScreen> createState() => _RiderHomeScreenState();
}

class _RiderHomeScreenState extends State<RiderHomeScreen> {
  int _tab = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<RideProvider>().fetchRides();
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth  = context.watch<AuthProvider>();
    final rides = context.watch<RideProvider>();

    return Scaffold(
      appBar: AppBar(
        title: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('OoruFlow', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
          Text('Hi, \${auth.user?.fullName.split(' ').first ?? 'there'} 👋',
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.normal)),
        ]),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_outlined),
            onPressed: () => auth.logout(),
          ),
        ],
      ),
      body: IndexedStack(index: _tab, children: [
        // Tab 0: Upcoming rides
        rides.loading
          ? const Center(child: CircularProgressIndicator())
          : rides.upcoming.isEmpty
            ? Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                const Text('🚗', style: TextStyle(fontSize: 48)),
                const SizedBox(height: 12),
                const Text('No upcoming rides', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                const SizedBox(height: 8),
                Text('Book by 8 PM IST for tomorrow', style: TextStyle(color: Colors.grey[600])),
                const SizedBox(height: 24),
                AppButton(label: 'Book a Ride', onPressed: () => setState(() => _tab = 1)),
              ]))
            : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: rides.upcoming.length,
                itemBuilder: (_, i) => RideCard(ride: rides.upcoming[i]),
              ),

        // Tab 1: Book Ride
        const BookRideScreen(),

        // Tab 2: All Rides
        const MyRidesScreen(),
      ]),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (i) => setState(() => _tab = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.add_circle_outline), selectedIcon: Icon(Icons.add_circle), label: 'Book'),
          NavigationDestination(icon: Icon(Icons.history_outlined), selectedIcon: Icon(Icons.history), label: 'Rides'),
        ],
      ),
    );
  }
}
""")

write("mobile/lib/screens/rider/book_ride_screen.dart", """
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/ride_provider.dart';
import '../../widgets/app_button.dart';

class BookRideScreen extends StatefulWidget {
  const BookRideScreen({super.key});
  @override
  State<BookRideScreen> createState() => _BookRideScreenState();
}

class _BookRideScreenState extends State<BookRideScreen> {
  final _pickupCtrl  = TextEditingController();
  final _dropoffCtrl = TextEditingController();
  DateTime _slotDate = DateTime.now().add(const Duration(days: 1));
  TimeOfDay _startTime = const TimeOfDay(hour: 9, minute: 0);
  TimeOfDay _endTime   = const TimeOfDay(hour: 9, minute: 30);
  String _rideType = 'solo';
  Map<String, dynamic>? _estimate;
  bool _booking = false;

  String _fmt(DateTime d) => DateFormat('yyyy-MM-dd').format(d);
  String _fmtTime(TimeOfDay t) => '\${t.hour.toString().padLeft(2,'0')}:\${t.minute.toString().padLeft(2,'0')}';

  Future<void> _book() async {
    if (_pickupCtrl.text.isEmpty || _dropoffCtrl.text.isEmpty) return;
    setState(() => _booking = true);
    final iso = '\${_fmt(_slotDate)}T\${_fmtTime(_startTime)}:00+05:30';
    final isoEnd = '\${_fmt(_slotDate)}T\${_fmtTime(_endTime)}:00+05:30';
    final ride = await context.read<RideProvider>().bookRide({
      'pickup_location': _pickupCtrl.text,
      'dropoff_location': _dropoffCtrl.text,
      'slot_start': iso, 'slot_end': isoEnd,
      'ride_type': _rideType,
    });
    setState(() => _booking = false);
    if (!mounted) return;
    if (ride != null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Ride booked! Confirmation by 8 PM IST.')));
      _pickupCtrl.clear(); _dropoffCtrl.clear();
    } else {
      final err = context.read<RideProvider>().error;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(err ?? 'Booking failed')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(padding: const EdgeInsets.all(20), child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text('Book a Ride', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text('Closes at 8 PM IST', style: TextStyle(color: Colors.grey[600], fontSize: 13)),
        const SizedBox(height: 24),
        TextField(controller: _pickupCtrl, decoration: const InputDecoration(labelText: 'Pickup Location', prefixIcon: Icon(Icons.my_location))),
        const SizedBox(height: 14),
        TextField(controller: _dropoffCtrl, decoration: const InputDecoration(labelText: 'Dropoff Location', prefixIcon: Icon(Icons.location_on_outlined))),
        const SizedBox(height: 20),
        ListTile(
          contentPadding: EdgeInsets.zero,
          leading: const Icon(Icons.calendar_today_outlined),
          title: Text(DateFormat('EEE, dd MMM yyyy').format(_slotDate)),
          trailing: const Icon(Icons.chevron_right),
          onTap: () async {
            final picked = await showDatePicker(context: context,
              initialDate: _slotDate,
              firstDate: DateTime.now().add(const Duration(days: 1)),
              lastDate: DateTime.now().add(const Duration(days: 30)));
            if (picked != null) setState(() => _slotDate = picked);
          },
        ),
        Row(children: [
          Expanded(child: ListTile(contentPadding: EdgeInsets.zero,
            leading: const Icon(Icons.schedule),
            title: Text('From \${_fmtTime(_startTime)}'),
            onTap: () async {
              final t = await showTimePicker(context: context, initialTime: _startTime);
              if (t != null) setState(() => _startTime = t);
            })),
          Expanded(child: ListTile(contentPadding: EdgeInsets.zero,
            title: Text('To \${_fmtTime(_endTime)}'),
            onTap: () async {
              final t = await showTimePicker(context: context, initialTime: _endTime);
              if (t != null) setState(() => _endTime = t);
            })),
        ]),
        const SizedBox(height: 16),
        Row(children: [
          Expanded(child: _TypeButton(label: '🚗 Solo', value: 'solo', selected: _rideType, onTap: () => setState(() => _rideType = 'solo'))),
          const SizedBox(width: 12),
          Expanded(child: _TypeButton(label: '🤝 Pool', value: 'pool', selected: _rideType, onTap: () => setState(() => _rideType = 'pool'))),
        ]),
        const SizedBox(height: 28),
        AppButton(label: 'Confirm Booking', onPressed: _book, loading: _booking),
      ],
    ));
  }
}

class _TypeButton extends StatelessWidget {
  final String label, value, selected;
  final VoidCallback onTap;
  const _TypeButton({required this.label, required this.value, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final isSelected = value == selected;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFFF97316) : Colors.white,
          border: Border.all(color: isSelected ? const Color(0xFFF97316) : Colors.grey[300]!),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Text(label, textAlign: TextAlign.center,
          style: TextStyle(fontWeight: FontWeight.w600, color: isSelected ? Colors.white : Colors.grey[700])),
      ),
    );
  }
}
""")

write("mobile/lib/screens/rider/my_rides_screen.dart", """
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/ride_provider.dart';
import '../../widgets/ride_card.dart';

class MyRidesScreen extends StatefulWidget {
  const MyRidesScreen({super.key});
  @override
  State<MyRidesScreen> createState() => _MyRidesScreenState();
}

class _MyRidesScreenState extends State<MyRidesScreen> with SingleTickerProviderStateMixin {
  late TabController _tabs;

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 2, vsync: this);
  }

  @override
  Widget build(BuildContext context) {
    final rides = context.watch<RideProvider>();
    return Column(children: [
      TabBar(controller: _tabs,
        labelColor: const Color(0xFFF97316),
        indicatorColor: const Color(0xFFF97316),
        tabs: const [Tab(text: 'Upcoming'), Tab(text: 'History')]),
      Expanded(child: TabBarView(controller: _tabs, children: [
        rides.loading
          ? const Center(child: CircularProgressIndicator())
          : rides.upcoming.isEmpty
            ? const Center(child: Text('No upcoming rides'))
            : ListView.builder(padding: const EdgeInsets.all(12),
                itemCount: rides.upcoming.length,
                itemBuilder: (_, i) => RideCard(ride: rides.upcoming[i])),
        rides.past.isEmpty
          ? const Center(child: Text('No ride history'))
          : ListView.builder(padding: const EdgeInsets.all(12),
              itemCount: rides.past.length,
              itemBuilder: (_, i) => RideCard(ride: rides.past[i])),
      ])),
    ]);
  }
}
""")

write("mobile/lib/screens/rider/tracking_screen.dart", """
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import '../../models/ride.dart';
import '../../config/api_config.dart';

class TrackingScreen extends StatefulWidget {
  final Ride ride;
  final String token;
  const TrackingScreen({super.key, required this.ride, required this.token});
  @override
  State<TrackingScreen> createState() => _TrackingScreenState();
}

class _TrackingScreenState extends State<TrackingScreen> {
  late WebSocketChannel _channel;
  LatLng? _driverLocation;
  GoogleMapController? _mapController;

  @override
  void initState() {
    super.initState();
    final wsUrl = ApiConfig.baseUrl.replaceFirst('http', 'ws');
    _channel = WebSocketChannel.connect(
      Uri.parse('\$wsUrl/ws/rides/\${widget.ride.id}/track?token=\${widget.token}'),
    );
    _channel.stream.listen((msg) {
      final data = jsonDecode(msg);
      if (data['type'] == 'location') {
        setState(() => _driverLocation = LatLng(data['lat'], data['lng']));
        _mapController?.animateCamera(CameraUpdate.newLatLng(_driverLocation!));
      }
    });
  }

  @override
  void dispose() {
    _channel.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Live Tracking')),
      body: Stack(children: [
        GoogleMap(
          initialCameraPosition: CameraPosition(
            target: LatLng(
              widget.ride.pickupLat ?? 12.9716,
              widget.ride.pickupLng ?? 77.5946,
            ),
            zoom: 14,
          ),
          onMapCreated: (c) => _mapController = c,
          markers: {
            if (_driverLocation != null)
              Marker(markerId: const MarkerId('driver'), position: _driverLocation!,
                icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueOrange),
                infoWindow: const InfoWindow(title: 'Your Driver')),
            if (widget.ride.pickupLat != null)
              Marker(markerId: const MarkerId('pickup'),
                position: LatLng(widget.ride.pickupLat!, widget.ride.pickupLng!),
                icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen),
                infoWindow: const InfoWindow(title: 'Your Pickup')),
          },
        ),
        Positioned(bottom: 0, left: 0, right: 0,
          child: Container(
            margin: const EdgeInsets.all(16),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16),
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 10)]),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
              Text(widget.ride.status == 'confirmed' ? '🚗 Driver on the way' : '📍 Ride in progress',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              const SizedBox(height: 6),
              Text('\${widget.ride.pickupLocation} → \${widget.ride.dropoffLocation}',
                style: TextStyle(color: Colors.grey[600], fontSize: 13)),
              if (_driverLocation == null)
                const Padding(padding: EdgeInsets.only(top: 8),
                  child: Text('Waiting for driver location…', style: TextStyle(color: Colors.orange))),
            ]),
          )),
      ]),
    );
  }
}
""")

write("mobile/lib/screens/driver/driver_home_screen.dart", """
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:geolocator/geolocator.dart';
import '../../providers/auth_provider.dart';
import '../../services/api_service.dart';
import 'earnings_screen.dart';

class DriverHomeScreen extends StatefulWidget {
  const DriverHomeScreen({super.key});
  @override
  State<DriverHomeScreen> createState() => _DriverHomeScreenState();
}

class _DriverHomeScreenState extends State<DriverHomeScreen> {
  final _api = ApiService();
  bool _online = false;
  bool _toggling = false;
  List _assignedRides = [];

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      final driver = await _api.get('/drivers/me');
      setState(() => _online = driver['status'] == 'online');
      final rides = await _api.get('/rides/');
      setState(() => _assignedRides = (rides as List).where((r) =>
        r['status'] == 'confirmed' || r['status'] == 'in_progress').toList());
    } catch (_) {}
  }

  Future<void> _toggleOnline() async {
    setState(() => _toggling = true);
    try {
      final newStatus = _online ? 'offline' : 'online';
      await _api.patch('/drivers/me/status', {'status': newStatus});
      setState(() => _online = !_online);
      if (_online) _startLocationUpdates();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    }
    setState(() => _toggling = false);
  }

  void _startLocationUpdates() async {
    final permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) return;
    Geolocator.getPositionStream(
      locationSettings: const LocationSettings(accuracy: LocationAccuracy.high, distanceFilter: 20),
    ).listen((pos) async {
      try {
        await _api.patch('/drivers/me/location', {'lat': pos.latitude, 'lng': pos.longitude});
      } catch (_) {}
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    return Scaffold(
      appBar: AppBar(
        title: const Text('Driver Dashboard'),
        actions: [
          IconButton(icon: const Icon(Icons.bar_chart_outlined),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const EarningsScreen()))),
          IconButton(icon: const Icon(Icons.logout_outlined), onPressed: () => auth.logout()),
        ],
      ),
      body: Padding(padding: const EdgeInsets.all(20), child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Online/Offline toggle
          Container(padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: _online ? const Color(0xFFDCFCE7) : const Color(0xFFF3F4F6),
              borderRadius: BorderRadius.circular(16)),
            child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(_online ? 'You are ONLINE' : 'You are OFFLINE',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18,
                    color: _online ? const Color(0xFF16A34A) : Colors.grey[700])),
                const SizedBox(height: 4),
                Text(_online ? 'Ready to receive rides' : 'Go online to accept rides',
                  style: TextStyle(color: Colors.grey[600], fontSize: 13)),
              ]),
              _toggling
                ? const CircularProgressIndicator()
                : Switch(value: _online, onChanged: (_) => _toggleOnline(),
                    activeColor: const Color(0xFF16A34A)),
            ])),
          const SizedBox(height: 24),
          const Text('Assigned Rides', style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Expanded(child: _assignedRides.isEmpty
            ? Center(child: Text('No rides assigned yet', style: TextStyle(color: Colors.grey[500])))
            : ListView.builder(
                itemCount: _assignedRides.length,
                itemBuilder: (_, i) {
                  final r = _assignedRides[i];
                  return Card(margin: const EdgeInsets.symmetric(vertical: 6),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    child: ListTile(
                      title: Text('\${r['pickup_location']} → \${r['dropoff_location']}'),
                      subtitle: Text('Status: \${r['status']} · ₹\${r['fare'] ?? 'TBD'}'),
                      leading: const Icon(Icons.directions_car, color: Color(0xFFF97316)),
                    ));
                })),
        ],
      )),
    );
  }
}
""")

write("mobile/lib/screens/driver/earnings_screen.dart", """
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../services/api_service.dart';

class EarningsScreen extends StatefulWidget {
  const EarningsScreen({super.key});
  @override
  State<EarningsScreen> createState() => _EarningsScreenState();
}

class _EarningsScreenState extends State<EarningsScreen> {
  final _api = ApiService();
  String _period = 'week';
  Map<String, dynamic>? _data;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await _api.get('/drivers/me/earnings?period=\$_period');
      setState(() { _data = data; _loading = false; });
    } catch (_) { setState(() => _loading = false); }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Earnings')),
      body: Padding(padding: const EdgeInsets.all(16), child: Column(children: [
        Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          for (final p in ['week', 'month', 'all'])
            Padding(padding: const EdgeInsets.symmetric(horizontal: 4),
              child: ChoiceChip(label: Text(p.capitalize()), selected: _period == p,
                selectedColor: const Color(0xFFF97316), onSelected: (_) {
                  setState(() => _period = p); _load();
                })),
        ]),
        const SizedBox(height: 20),
        if (_loading) const Center(child: CircularProgressIndicator())
        else if (_data != null) ...[
          Container(width: double.infinity, padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(gradient: const LinearGradient(
              colors: [Color(0xFFF97316), Color(0xFFEA580C)]),
              borderRadius: BorderRadius.circular(16)),
            child: Column(children: [
              const Text('Total Earnings', style: TextStyle(color: Colors.white70, fontSize: 14)),
              const SizedBox(height: 8),
              Text('₹\${(_data!['total_earnings'] as num).toStringAsFixed(2)}',
                style: const TextStyle(color: Colors.white, fontSize: 36, fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              Text('\${_data!['total_rides']} rides completed',
                style: const TextStyle(color: Colors.white70, fontSize: 13)),
            ])),
          const SizedBox(height: 20),
          Expanded(child: ListView.builder(
            itemCount: (_data!['earnings'] as List).length,
            itemBuilder: (_, i) {
              final e = (_data!['earnings'] as List)[i];
              return ListTile(
                title: Text('Ride #\${e['ride_id']}'),
                subtitle: Text(DateFormat('dd MMM, h:mm a').format(DateTime.parse(e['date']).toLocal())),
                trailing: Text('₹\${(e['amount'] as num).toStringAsFixed(2)}',
                  style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF16A34A))),
              );
            })),
        ],
      ])),
    );
  }
}

extension StringExt on String {
  String capitalize() => isEmpty ? this : '\${this[0].toUpperCase()}\${substring(1)}';
}
""")

write("mobile/lib/main.dart", """
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/theme.dart';
import 'providers/auth_provider.dart';
import 'providers/ride_provider.dart';
import 'screens/auth/login_screen.dart';
import 'screens/rider/home_screen.dart';
import 'screens/driver/driver_home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => RideProvider()),
      ],
      child: const OoruFlowApp(),
    ),
  );
}

class OoruFlowApp extends StatelessWidget {
  const OoruFlowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OoruFlow',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: const _Splash(),
    );
  }
}

class _Splash extends StatefulWidget {
  const _Splash();
  @override
  State<_Splash> createState() => _SplashState();
}

class _SplashState extends State<_Splash> {
  @override
  void initState() {
    super.initState();
    _navigate();
  }

  Future<void> _navigate() async {
    await Future.delayed(const Duration(milliseconds: 800));
    if (!mounted) return;
    final auth = context.read<AuthProvider>();
    await auth.checkAuth();
    if (!mounted) return;
    if (auth.isLoggedIn) {
      Navigator.pushReplacement(context, MaterialPageRoute(
        builder: (_) => auth.isDriver ? const DriverHomeScreen() : const RiderHomeScreen(),
      ));
    } else {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const LoginScreen()));
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        Text('🚗', style: TextStyle(fontSize: 64)),
        SizedBox(height: 16),
        Text('OoruFlow', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Color(0xFFC2410C))),
        SizedBox(height: 8),
        Text('Bengaluru Office Commute', style: TextStyle(color: Colors.grey)),
        SizedBox(height: 40),
        CircularProgressIndicator(color: Color(0xFFF97316)),
      ])),
    );
  }
}
""")

print("✅ Flutter mobile app files written.\n")

# ═══════════════════════════════════════════════════════════════════════════
#  NGINX CONFIG
# ═══════════════════════════════════════════════════════════════════════════

write("nginx/nginx.conf", """
events { worker_connections 1024; }

http {
  upstream api {
    server app:8000;
  }

  server {
    listen 80;
    server_name _;

    location /api/ {
      proxy_pass http://api/;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /ws/ {
      proxy_pass http://api;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_set_header Host $host;
    }

    location / {
      proxy_pass http://web:3000;
      proxy_set_header Host $host;
    }
  }
}
""")

print("✅ Nginx config written.\n")

# ═══════════════════════════════════════════════════════════════════════════
#  PWA ASSETS  (manifest + service-worker hint + mobile meta)
# ═══════════════════════════════════════════════════════════════════════════

write("web/public/manifest.json", """
{
  "name": "OoruFlow",
  "short_name": "OoruFlow",
  "description": "Bengaluru office commute — plan your ride the night before",
  "start_url": "/dashboard",
  "display": "standalone",
  "background_color": "#fff7ed",
  "theme_color": "#f97316",
  "orientation": "portrait",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ],
  "screenshots": [
    { "src": "/screenshot-mobile.png", "sizes": "390x844", "type": "image/png", "form_factor": "narrow" }
  ]
}
""")

# Minimal SVG placeholder icons (replace with real PNGs in production)
write("web/public/icon-192.svg", """
<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192">
  <rect width="192" height="192" rx="40" fill="#f97316"/>
  <text x="96" y="120" font-size="80" text-anchor="middle" fill="white">🚗</text>
</svg>
""")

# Mobile-specific layout for the PWA rider experience
write("web/app/(mobile)/layout.tsx", """
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
""")

write("web/app/(mobile)/m/home/page.tsx", """
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
""")

write("web/app/(mobile)/m/book/page.tsx", """
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
""")

write("web/app/(mobile)/m/rides/page.tsx", """
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
""")

write("web/app/(mobile)/m/profile/page.tsx", """
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
""")

# Update root layout to include PWA meta tags
print("✅ PWA files written.\n")

write("web/Dockerfile", """
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json ./
RUN npm install

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
""")

print("=" * 60)
print("All files created! Next steps:")
print()
print("1. Start backend services:")
print("   docker-compose up -d db redis")
print()
print("2. Start FastAPI (from D:\\OoruFlow):")
print("   venv\\Scripts\\pip.exe install -r requirements.txt")
print("   venv\\Scripts\\uvicorn.exe app.main:app --reload")
print()
print("3. Start web frontend:")
print("   cd web && npm install && npm run dev")
print("   Open: http://localhost:3000")
print()
print("4. Run Flutter mobile app:")
print("   cd mobile && flutter pub get && flutter run")
print()
print("5. Full Docker stack (after backend works):")
print("   docker-compose up --build")
print("=" * 60)
