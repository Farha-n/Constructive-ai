import './globals.css'

export const metadata = {
  title: 'AI Email Assistant',
  description: 'AI-powered Gmail assistant built with Next.js and FastAPI',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

