import { BrowserRouter, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom'
import { useState, useEffect, type FormEvent } from 'react'
import Dashboard from './pages/Dashboard'
import ProjectList from './pages/ProjectList'
import ExecutionDetail from './pages/ExecutionDetail'
import './App.css'

type User = { id: string; email: string; full_name: string }

function DemoProject() {
  const { id } = useParams()
  const navigate = useNavigate()
  const name = id === 'demo-api' ? 'payments-api' : 'identity-service'
  return <div className="demo-project"><span className="eyebrow">Demo project</span><h1>{name}</h1><p>Review the repository signal, launch the five-agent analysis, and inspect the generated engineering report.</p><div className="demo-project-grid"><div><strong>12</strong><span>test cases</span></div><div><strong>3</strong><span>known risks</span></div><div><strong>5</strong><span>analysis agents</span></div></div><button className="btn btn-primary" onClick={() => navigate('/executions/demo-execution')}>Run demo analysis</button></div>
}

function AuthScreen({ onAuthenticated }: { onAuthenticated: (token: string, user: User) => void }) {
  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [form, setForm] = useState({ email: '', password: '', full_name: '' })
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const response = await fetch(`/api/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mode === 'login' ? { email: form.email, password: form.password } : form),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail || payload.error?.message || 'Authentication failed')
      onAuthenticated(payload.access_token, payload.user)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <div className="auth-brand">AI Debugging Agent</div>
        <p className="auth-kicker">Engineering intelligence workspace</p>
        <h1>{mode === 'login' ? 'Welcome back' : 'Create your workspace'}</h1>
        <p className="auth-copy">Trace failures, coordinate agents, and turn noisy test output into an actionable plan.</p>
        <div className="auth-tabs">
          <button className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')}>Sign in</button>
          <button className={mode === 'signup' ? 'active' : ''} onClick={() => setMode('signup')}>Create account</button>
        </div>
        <form onSubmit={submit} className="auth-form">
          {mode === 'signup' && <label>Full name<input className="input" required minLength={2} value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} /></label>}
          <label>Email address<input className="input" type="email" required value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} /></label>
          <label>Password<input className="input" type="password" required minLength={8} value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} /></label>
          {error && <div className="alert alert-error">{error}</div>}
          <button className="btn btn-primary auth-submit" disabled={submitting}>{submitting ? 'Working...' : mode === 'login' ? 'Sign in' : 'Create account'}</button>
          <button type="button" className="demo-link" onClick={() => onAuthenticated('demo-token', { id: 'demo-user', email: 'demo@debugger.local', full_name: 'Demo Reviewer' })}>Explore demo workspace</button>
        </form>
      </section>
      <aside className="auth-aside"><span>01 / ORCHESTRATE</span><strong>From failing test<br />to confident fix.</strong><p>A focused command center for the entire debugging lifecycle.</p></aside>
    </main>
  )
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'))
  const [user, setUser] = useState<User | null>(() => localStorage.getItem('auth_token') === 'demo-token' ? { id: 'demo-user', email: 'demo@debugger.local', full_name: 'Demo Reviewer' } : null)
  const [apiHealth, setApiHealth] = useState(false)

  useEffect(() => {
    // Check API health
    fetch('/api/health')
      .then(res => setApiHealth(res.ok))
      .catch(() => setApiHealth(false))
  }, [])

  useEffect(() => {
    if (!token || token === 'demo-token') return
    fetch('/api/auth/me', { headers: { Authorization: `Bearer ${token}` } })
      .then(response => response.ok ? response.json() : Promise.reject())
      .then(setUser)
      .catch(() => { localStorage.removeItem('auth_token'); setToken(null) })
  }, [token])

  if (!token || !user) return <AuthScreen onAuthenticated={(nextToken, nextUser) => { localStorage.setItem('auth_token', nextToken); setToken(nextToken); setUser(nextUser) }} />

  return (
    <BrowserRouter>
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <Link to="/" className="logo">
              <h1>🤖 AI Debugging Agent</h1>
            </Link>
            <div className="status-indicator">
              <span className={`status ${apiHealth ? 'online' : 'offline'}`}>
                {apiHealth ? '● Online' : '● Offline'}
              </span>
              <span className="user-name">{user.full_name}</span>
              <button className="btn btn-sm btn-secondary" onClick={() => { localStorage.removeItem('auth_token'); setToken(null); setUser(null) }}>Log out</button>
            </div>
          </div>
          <nav className="nav-menu">
            <Link to="/" className="nav-link">Dashboard</Link>
            <Link to="/projects" className="nav-link">Projects</Link>
          </nav>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/projects" element={<ProjectList />} />
            <Route path="/projects/:id" element={<DemoProject />} />
            <Route path="/executions/:id" element={<ExecutionDetail />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>AI-Driven Multi-Agent Software Debugging System • v0.1.0</p>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App
