'use client'

import styles from './ConfirmDialog.module.css'

export default function ConfirmDialog({ title, message, onConfirm, onCancel }) {
  return (
    <div className={styles.backdrop}>
      <div className={styles.dialog}>
        <h3 className={styles.title}>{title}</h3>
        <p className={styles.message}>{message}</p>
        <div className={styles.actions}>
          <button className={`${styles.button} ${styles.cancel}`} onClick={onCancel}>
            Cancel
          </button>
          <button className={`${styles.button} ${styles.confirm}`} onClick={onConfirm}>
            Confirm
          </button>
        </div>
      </div>
    </div>
  )
}

