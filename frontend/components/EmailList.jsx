'use client'

import { format } from 'date-fns'
import styles from './EmailList.module.css'

export default function EmailList({ emails, onReply, onDelete }) {
  return (
    <div className={styles.wrapper}>
      <h3 className={styles.title}>📧 Recent Emails</h3>
      {emails.map((email) => (
        <div key={email.id} className={styles.card}>
          <div className={styles.header}>
            <div>
              <div className={styles.sender}>
                {email.sender_name || email.sender_email}
                <span className={styles.address}>{email.sender_email}</span>
              </div>
              <div className={styles.subject}>{email.subject || '(No subject)'}</div>
            </div>
            <div className={styles.actions}>
              <button className={`${styles.action} ${styles.reply}`} onClick={() => onReply(email)}>
                Reply
              </button>
              <button className={`${styles.action} ${styles.delete}`} onClick={() => onDelete(email)}>
                Delete
              </button>
            </div>
          </div>
          {email.date && <div className={styles.date}>{format(new Date(email.date), 'PPp')}</div>}
          {email.ai_summary && (
            <div className={styles.summary}>
              <strong>AI Summary:</strong> {email.ai_summary}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

