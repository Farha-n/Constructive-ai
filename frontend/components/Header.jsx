'use client'

import Image from 'next/image'
import styles from './Header.module.css'

export default function Header({ user, onLogout }) {
  return (
    <header className={styles.header}>
      <div className={styles.content}>
        <h1 className={styles.title}>AI Email Assistant</h1>
        <div className={styles.user}>
          {user?.picture && (
            <Image
              src={user.picture}
              alt={user?.name || 'User avatar'}
              width={40}
              height={40}
              className={styles.avatar}
            />
          )}
          <span className={styles.name}>{user?.name || user?.email}</span>
          <button className={styles.logout} onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}

