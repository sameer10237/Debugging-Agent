import { useState, useEffect } from 'react'
import './Dashboard.css'

interface Stats {
  total_projects: number
  active_executions: number
  completed_executions: number
  total_failures_analyzed: number
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    total_projects: 0,
    active_executions: 0,
    completed_executions: 0,
    total_failures_analyzed: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      // In a real implementation, this would call an actual stats endpoint
      setStats({
        total_projects: 5,
        active_executions: 2,
        completed_executions: 23,
        total_failures_analyzed: 156,
      })
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stats')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading dashboard...</div>
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <p className="subtitle">Multi-Agent Debugging System Overview</p>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_projects}</div>
          <div className="stat-label">Projects</div>
          <div className="stat-icon">📁</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats.active_executions}</div>
          <div className="stat-label">Active Executions</div>
          <div className="stat-icon">⚙️</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats.completed_executions}</div>
          <div className="stat-label">Completed</div>
          <div className="stat-icon">✓</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats.total_failures_analyzed}</div>
          <div className="stat-label">Failures Analyzed</div>
          <div className="stat-icon">🔍</div>
        </div>
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <h2>System Architecture</h2>
          <div className="architecture-diagram">
            <div className="agent-box">Testing Agent</div>
            <div className="arrow">↓</div>
            <div className="agent-box">Debugging Agent</div>
            <div className="arrow">↓</div>
            <div className="agent-box">Coding Agent</div>
            <div className="arrow">↓</div>
            <div className="agent-box">Architect Agent</div>
            <div className="arrow">↓</div>
            <div className="agent-box">Project Manager</div>
          </div>
        </section>

        <section className="panel">
          <h2>Recent Executions</h2>
          <div className="execution-list">
            <div className="execution-item">
              <div className="execution-status completed">Completed</div>
              <div className="execution-details">
                <div className="execution-name">project-auth: Login flow</div>
                <div className="execution-time">2 hours ago</div>
              </div>
              <div className="execution-result">✓ 3 fixes</div>
            </div>
            <div className="execution-item">
              <div className="execution-status running">Running</div>
              <div className="execution-details">
                <div className="execution-name">project-api: Database queries</div>
                <div className="execution-time">5 minutes ago</div>
              </div>
              <div className="execution-result">...</div>
            </div>
          </div>
        </section>
      </div>

      <section className="panel">
        <h2>Quick Start</h2>
        <div className="quick-start">
          <ol>
            <li>Create a new project with your repository</li>
            <li>Upload test suite and source code</li>
            <li>System runs testing, debugging, and analysis</li>
            <li>Review proposed fixes and recommendations</li>
            <li>Apply fixes or implement manually</li>
          </ol>
        </div>
      </section>
    </div>
  )
}
