import { redirect } from 'next/navigation'
import { headers } from 'next/headers'

export default function Root() {
  const ua = headers().get('user-agent') || ''
  const isMobile = /android|iphone|ipad|ipod|mobile/i.test(ua)
  redirect(isMobile ? '/m/home' : '/dashboard')
}
