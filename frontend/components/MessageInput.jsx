'use client'

import { useEffect, useRef, useState } from 'react'
import styles from './MessageInput.module.css'

export default function MessageInput({ onSend, loading }) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef(null)

  useEffect(() => {
    if (!textareaRef.current) return
    textareaRef.current.style.height = 'auto'
    textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
  }, [message])

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!message.trim() || loading) return
    onSend(message.trim())
    setMessage('')
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSubmit(event)
    }
  }

  return (
    <div className={styles.wrapper}>
      <form className={styles.form} onSubmit={handleSubmit}>
        <textarea
          ref={textareaRef}
          className={styles.textarea}
          placeholder="Type a message... (Shift+Enter for newline)"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button type="submit" className={styles.button} disabled={!message.trim() || loading}>
          {loading ? '...' : 'Send'}
        </button>
      </form>
    </div>
  )
}

