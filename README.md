# AI Email Assistant

A full-stack AI-powered email assistant application built with FastAPI (backend) and Next.js (frontend). This application allows users to authenticate with Google, read emails, generate AI-powered summaries and replies, and manage their inbox through a conversational chatbot interface.

## Features

### Core Features
- ✅ **Google OAuth Authentication** - Secure login with Gmail permissions
- ✅ **AI Chatbot Dashboard** - Natural language interface for email management
- ✅ **Email Reading** - Fetch and display the last 5 emails with AI-generated summaries
- ✅ **AI Reply Generation** - Generate context-aware email replies using AI
- ✅ **Email Sending** - Send replies directly through Gmail
- ✅ **Email Deletion** - Delete emails by sender, subject, or reference number with confirmation
- ✅ **Session Management** - Secure session handling with automatic token refresh

### Bonus Features (Partially Implemented)
- ⚡ **Natural Language Command Understanding** - Process commands like "show me emails from John"
- 📊 **Daily Digest** - Generate AI-powered daily email summaries

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Google API Client** - Gmail API integration
- **OpenAI API** - AI-powered email summaries and replies
- **Python-dotenv** - Environment variable management

### Frontend
- **Next.js 14** - React framework deployed on Vercel
- **App Router** - File-based routing
- **Axios** - HTTP client
- **date-fns** - Date formatting

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication routes
│   │   ├── email.py           # Email operation routes
│   │   └── chat.py            # Chatbot routes
│   └── utils/
│       ├── session.py         # Session management
│       ├── gmail.py           # Gmail API wrapper
│       └── ai.py              # AI service integration
├── frontend/
│   ├── app/                   # Next.js routes (login, dashboard)
│   ├── components/            # Reusable UI components
│   ├── lib/                   # API helpers
│   ├── public/                # Static assets
│   ├── package.json
│   └── next.config.js
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+ installed
- Node.js 18+ and npm/yarn installed
- Google Cloud Console account (for OAuth credentials)
- OpenAI API key

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google OAuth:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Web application)
   - Add authorized redirect URI: `http://localhost:8000/auth/callback`
   - **Important:** Add `test@gmail.com` as a test user in OAuth consent screen for testing

5. **Create `.env` file in backend directory:**
   ```env
   GOOGLE_CLIENT_ID=your_google_client_id_here
   GOOGLE_CLIENT_SECRET=your_google_client_secret_here
   REDIRECT_URI=http://localhost:8000/auth/callback
   
   SECRET_KEY=your_secret_key_here_change_in_production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   OPENAI_API_KEY=your_openai_api_key_here
   
   FRONTEND_URL=http://localhost:3000
   BACKEND_URL=http://localhost:8000
   ```

6. **Run the backend server:**
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create `.env.local` file (you can copy `env.example`):**
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Deployment

### Frontend Deployment to Vercel

1. **Build the frontend:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy to Vercel:**
   - Install Vercel CLI: `npm i -g vercel`
   - Run `vercel` in the frontend directory
   - Follow the prompts
   - Add environment variables in Vercel dashboard:
    - `NEXT_PUBLIC_API_URL` - Your backend API URL
    - `NEXT_PUBLIC_BACKEND_URL` - Your backend API URL

3. **Update Google OAuth Settings:**
   - Add your Vercel deployment URL to authorized JavaScript origins
   - Add callback URL: `https://your-backend-url/auth/callback`

### Backend Deployment

The backend needs to be deployed to a service that supports Python/FastAPI. Options include:
- **Railway** - Easy Python deployment
- **Render** - Free tier available
- **Heroku** - Requires credit card
- **DigitalOcean App Platform**
- **AWS/GCP** - More complex setup

**Important:** Update the following in your backend `.env` after deployment:
- `REDIRECT_URI` - Your production callback URL
- `FRONTEND_URL` - Your Vercel deployment URL
- `BACKEND_URL` - Your backend deployment URL

### Environment Variables for Production

**Backend:**
- `GOOGLE_CLIENT_ID` - Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Your Google OAuth client secret
- `REDIRECT_URI` - Production callback URL (e.g., `https://your-backend.railway.app/auth/callback`)
- `OPENAI_API_KEY` - Your OpenAI API key
- `FRONTEND_URL` - Your Vercel frontend URL (e.g., `https://your-app.vercel.app`)
- `BACKEND_URL` - Your backend URL
- `SECRET_KEY` - A secure random string for sessions

**Frontend:**
- `NEXT_PUBLIC_API_URL` - Your backend API URL
- `NEXT_PUBLIC_BACKEND_URL` - Your backend API URL

## Usage

1. **Start the application:**
   - Start backend: `cd backend && python main.py`
   - Start frontend: `cd frontend && npm run dev`

2. **Access the application:**
   - Open `http://localhost:3000` in your browser
   - Click "Sign in with Google"
   - Authorize Gmail permissions

3. **Using the Chatbot:**
   - **Read emails:** "Show me my recent emails" or "Fetch last 5 emails"
   - **Generate reply:** "Reply to the latest email from [sender]" or "Generate a reply"
   - **Delete email:** "Delete the email from [sender]" or "Delete email number 2"
   - **Daily digest:** "Give me today's email digest"

## API Endpoints

### Authentication
- `GET /auth/login` - Initiate Google OAuth login
- `GET /auth/callback` - OAuth callback handler
- `GET /auth/me?token=...` - Get current user info
- `POST /auth/logout?token=...` - Logout user

### Email Operations
- `GET /email/recent?token=...&max_results=5` - Get recent emails with AI summaries
- `POST /email/send?token=...` - Send an email
- `POST /email/delete?token=...` - Delete an email
- `POST /email/generate-reply?token=...&email_id=...` - Generate AI reply
- `GET /email/find-by-sender?token=...&sender_email=...` - Find email by sender
- `GET /email/find-by-subject?token=...&subject_keyword=...` - Find email by subject

### Chat
- `GET /chat/greeting?token=...` - Get greeting message
- `POST /chat/message?token=...` - Process chat message

## Known Limitations

1. **Session Storage:** Currently uses in-memory session storage. In production, use Redis or a database.
2. **Error Handling:** Some edge cases may not be fully handled.
3. **Email Parsing:** HTML emails may not render perfectly; plain text is extracted.
4. **Rate Limiting:** No rate limiting implemented for API calls.
5. **Testing:** Limited automated test coverage.

## Troubleshooting

### Backend Issues

- **Import errors:** Make sure you're in the backend directory and virtual environment is activated
- **OAuth errors:** Verify Google OAuth credentials and redirect URI match exactly
- **Gmail API errors:** Ensure Gmail API is enabled in Google Cloud Console
- **OpenAI errors:** Check your API key is valid and has credits

### Frontend Issues

- **CORS errors:** Verify `FRONTEND_URL` in backend matches your frontend URL
- **API connection errors:** Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- **Build errors:** Remove `node_modules` and reinstall: `rm -rf node_modules && npm install`

## License

This project is created for the Constructure AI technical assignment.

## Contact

For questions or issues, please refer to the submission instructions.

