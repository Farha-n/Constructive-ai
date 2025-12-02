'use client'

import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const authAPI = {
  login: async () => {
    const response = await api.get('/auth/login')
    return response.data
  },
  getMe: async (token) => {
    const response = await api.get('/auth/me', {
      params: { token },
    })
    return response.data
  },
  logout: async (token) => {
    const response = await api.post('/auth/logout', null, {
      params: { token },
    })
    return response.data
  },
}

export const emailAPI = {
  getRecent: async (token, maxResults = 5) => {
    const response = await api.get('/email/recent', {
      params: { token, max_results: maxResults },
    })
    return response.data
  },
  sendEmail: async (token, payload) => {
    const response = await api.post('/email/send', payload, {
      params: { token },
    })
    return response.data
  },
  deleteEmail: async (token, messageId) => {
    const response = await api.post('/email/delete', { message_id: messageId }, {
      params: { token },
    })
    return response.data
  },
  generateReply: async (token, emailId, userContext = null) => {
    const response = await api.post('/email/generate-reply', null, {
      params: { token, email_id: emailId, user_context: userContext },
    })
    return response.data
  },
}

export const chatAPI = {
  getGreeting: async (token) => {
    const response = await api.get('/chat/greeting', {
      params: { token },
    })
    return response.data
  },
  sendMessage: async (token, message, emailContext = null) => {
    const response = await api.post('/chat/message', {
      message,
      email_context: emailContext,
    }, {
      params: { token },
    })
    return response.data
  },
}

