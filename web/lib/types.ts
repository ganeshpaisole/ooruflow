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
