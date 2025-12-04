'use client'

import { useEffect, useRef, useState } from 'react'
import { chatAPI, emailAPI } from '@/lib/api'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import EmailList from './EmailList'
import ReplyView from './ReplyView'
import ConfirmDialog from './ConfirmDialog'
import styles from './ChatInterface.module.css'

export default function ChatInterface({ token, initialGreeting }) {
  const [messages, setMessages] = useState([])
  const [emailContext, setEmailContext] = useState([])
  const [replyData, setReplyData] = useState(null)
  const [deleteConfirm, setDeleteConfirm] = useState(null)
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (initialGreeting) {
      setMessages([{
        role: 'assistant',
        content: initialGreeting,
        timestamp: new Date().toISOString(),
      }])
    }
  }, [initialGreeting])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, replyData, emailContext])

  const appendMessage = (message) => {
    setMessages((prev) => [...prev, message])
  }

  const handleSendMessage = async (message) => {
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    }
    appendMessage(userMessage)
    setLoading(true)

    try {
      const response = await chatAPI.sendMessage(token, message, emailContext)
      appendMessage({
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        intent: response.intent,
        action: response.action,
        data: response.data,
      })

      switch (response.action) {
        case 'display_emails':
          setEmailContext(response.data?.emails || [])
          setReplyData(null)
          break
        case 'display_reply':
          setReplyData(response.data)
          setEmailContext([])
          break
        case 'confirm_delete':
          setDeleteConfirm(response.data?.email || null)
          setReplyData(null)
          break
        default:
          if (response.action !== 'display_digest') {
            setReplyData(null)
          }
          break
      }
    } catch (error) {
      console.error(error)
      appendMessage({
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        timestamp: new Date().toISOString(),
        error: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSendReply = async (replyText, toEmail, subject, threadId) => {
    setLoading(true)
    try {
      await emailAPI.sendEmail(token, {
        to: toEmail,
        subject: `Re: ${subject}`,
        body: replyText,
        thread_id: threadId || undefined,
      })
      appendMessage({
        role: 'assistant',
        content: `✅ Email sent to ${toEmail}`,
        timestamp: new Date().toISOString(),
      })
      setReplyData(null)

      if (emailContext.length > 0) {
        const refreshed = await emailAPI.getRecent(token, emailContext.length)
        setEmailContext(refreshed.emails || [])
      }
    } catch (error) {
      appendMessage({
        role: 'assistant',
        content: `❌ Failed to send email: ${error?.response?.data?.detail || 'Unknown error'}`,
        timestamp: new Date().toISOString(),
        error: true,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteEmail = async (messageId, senderName) => {
    setLoading(true)
    try {
      await emailAPI.deleteEmail(token, messageId)
      appendMessage({
        role: 'assistant',
        content: `✅ Deleted email from ${senderName}`,
        timestamp: new Date().toISOString(),
      })
      setEmailContext((prev) => prev.filter((email) => email.id !== messageId))
    } catch (error) {
      appendMessage({
        role: 'assistant',
        content: `❌ Failed to delete email: ${error?.response?.data?.detail || 'Unknown error'}`,
        timestamp: new Date().toISOString(),
        error: true,
      })
    } finally {
      setDeleteConfirm(null)
      setLoading(false)
    }
  }

  return (
    <>
      <div className={styles.wrapper}>
        <div className={styles.container}>
          <div className={styles.messagesArea}>
            <MessageList messages={messages} />
            {replyData && (
              <ReplyView
                replyData={replyData}
                onSend={handleSendReply}
                onCancel={() => setReplyData(null)}
              />
            )}
            {emailContext.length > 0 && !replyData && (
              <EmailList
                emails={emailContext}
                onReply={(email) => handleSendMessage(`Reply to ${email.sender_email}`)}
                onDelete={(email) => setDeleteConfirm({
                  id: email.id,
                  sender_name: email.sender_name,
                  sender_email: email.sender_email,
                  subject: email.subject,
                })}
              />
            )}
            <div ref={messagesEndRef} className={styles.scrollSentinel} />
          </div>
          <MessageInput onSend={handleSendMessage} loading={loading} />
        </div>
      </div>

      {deleteConfirm && (
        <ConfirmDialog
          title="Delete email?"
          message={`Delete the email from ${deleteConfirm.sender_name || deleteConfirm.sender_email} with subject "${deleteConfirm.subject}"?`}
          onConfirm={() => handleDeleteEmail(deleteConfirm.id, deleteConfirm.sender_name || deleteConfirm.sender_email)}
          onCancel={() => setDeleteConfirm(null)}
        />
      )}
    </>
  )
}

