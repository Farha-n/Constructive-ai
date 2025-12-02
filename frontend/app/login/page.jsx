'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { authAPI } from '@/lib/api'
import styles from './Login.module.css'

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    const token = searchParams.get('token')
    if (token) {
      localStorage.setItem('auth_token', token)
      router.replace('/dashboard')
    }

    if (searchParams.get('error') === 'auth_failed') {
      setError('Authentication failed. Please try again.')
    }
  }, [router, searchParams])

  const handleLogin = async () => {
    try {
      setLoading(true)
      setError(null)
      const { authorization_url } = await authAPI.login()
      window.location.href = authorization_url
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to initiate login. Please try again.')
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.navbar}>
        <div className={styles.brand}>AI Email Assistant</div>
        <nav className={styles.navLinks}>
          <a href="#" aria-disabled>Home</a>
          <a href="#" aria-disabled>Login</a>
          <a href="#" aria-disabled>Register</a>
        </nav>
      </header>

      <main className={styles.main}>
        <div className={styles.card}>
          <h1 className={styles.cardTitle}>Login</h1>
          <p className={styles.cardSubtitle}>Welcome back! Use Google to continue.</p>

          {error && <div className={styles.error}>{error}</div>}

          <button className={styles.button} onClick={handleLogin} disabled={loading}>
            {loading ? 'Connecting…' : 'Sign in with Google'}
          </button>

          <p className={styles.hint}>
            Need access? Ensure your Google account is on the tester list.
          </p>
        </div>
      </main>
    </div>
  )
}

