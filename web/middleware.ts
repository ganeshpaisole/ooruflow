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
