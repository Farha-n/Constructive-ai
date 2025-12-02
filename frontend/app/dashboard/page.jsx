'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import ChatInterface from '@/components/ChatInterface'
import { authAPI, chatAPI } from '@/lib/api'
import styles from './Dashboard.module.css'

export default function DashboardPage() {
  const router = useRouter()
  const [token, setToken] = useState(null)
  const [user, setUser] = useState(null)
  const [greeting, setGreeting] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedToken = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
    if (!storedToken) {
      router.replace('/login')
      return
    }
    setToken(storedToken)
  }, [router])

  useEffect(() => {
    if (!token) return

    const fetchData = async () => {
      try {
        const [userData, greetingData] = await Promise.all([
          authAPI.getMe(token),
          chatAPI.getGreeting(token),
        ])
        setUser(userData)
        setGreeting(greetingData.greeting)
      } catch (error) {
        console.error(error)
        localStorage.removeItem('auth_token')
        router.replace('/login')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [token, router])

  const handleLogout = async () => {
    try {
      if (token) {
        await authAPI.logout(token)
      }
    } catch (error) {
      console.error(error)
    } finally {
      localStorage.removeItem('auth_token')
      router.replace('/login')
    }
  }

  if (loading) {
    return (
      <div className={styles.page}>
        <Header user={user} onLogout={handleLogout} />
        <div className={styles.content} style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          Loading dashboard…
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <Header user={user} onLogout={handleLogout} />
      <main className={styles.content}>
        <ChatInterface token={token} initialGreeting={greeting} />
      </main>
    </div>
  )
}

