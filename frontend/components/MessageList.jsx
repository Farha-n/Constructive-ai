'use client'

import { format } from 'date-fns'
import styles from './MessageList.module.css'

export default function MessageList({ messages }) {
  return (
    <div className={styles.list}>
      {messages.map((message, index) => (
        <div
          key={`${message.timestamp}-${index}`}
          className={`${styles.message} ${message.role === 'user' ? styles.user : styles.assistant} ${message.error ? styles.error : ''}`}
        >
          <div className={styles.content}>
            {message.content.split('\n').map((line, idx) => (
              <p key={idx}>{line || '\u00A0'}</p>
            ))}
          </div>
          {message.timestamp && (
            <div className={styles.timestamp}>
              {format(new Date(message.timestamp), 'HH:mm')}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

