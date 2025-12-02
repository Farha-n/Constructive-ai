'use client'

import { useState } from 'react'
import styles from './ReplyView.module.css'

export default function ReplyView({ replyData, onSend, onCancel }) {
  const [replyText, setReplyText] = useState(replyData.reply || '')
  const [sending, setSending] = useState(false)

  const handleSend = async () => {
    if (!replyText.trim()) return
    setSending(true)
    await onSend(
      replyText,
      replyData.original_email.sender_email,
      replyData.original_email.subject,
      replyData.original_email.thread_id,
    )
    setSending(false)
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <h3>Suggested Reply</h3>
        <button className={styles.dismiss} onClick={onCancel}>
          ×
        </button>
      </div>

      <div className={styles.details}>
        <span className={styles.label}>To:</span>
        <span>{replyData.original_email.sender_name || replyData.original_email.sender_email}</span>
        <span className={styles.label}>Subject:</span>
        <span>Re: {replyData.original_email.subject}</span>
      </div>

      <textarea
        className={styles.textarea}
        value={replyText}
        onChange={(e) => setReplyText(e.target.value)}
      />

      <div className={styles.actions}>
        <button className={`${styles.button} ${styles.cancel}`} onClick={onCancel}>
          Cancel
        </button>
        <button
          className={`${styles.button} ${styles.send}`}
          onClick={handleSend}
          disabled={!replyText.trim() || sending}
        >
          {sending ? 'Sending…' : 'Send'}
        </button>
      </div>
    </div>
  )
}

