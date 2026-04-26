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
