import { useEffect, useState } from 'react'
import './ExecutionMonitor.css'

interface AgentUpdate {
  type: string
  agent: string
  status: string
  timestamp: string
  data?: any
}

interface ExecutionMonitorProps {
  executionId: string
}

export default function ExecutionMonitor({ executionId }: ExecutionMonitorProps) {
  const [updates, setUpdates] = useState<AgentUpdate[]>([])
  const [connected, setConnected] = useState(false)
  const [overallProgress, setOverallProgress] = useState(0)

  useEffect(() => {
    // Connect to WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/executions/${executionId}`)

    ws.onopen = () => {
      console.log('WebSocket connected')
      setConnected(true)
    }

    ws.onmessage = (event) => {
      const message: AgentUpdate = JSON.parse(event.data)
      setUpdates(prev => {
        const nextUpdates = [...prev, message]
        const agents = ['testing_agent', 'debugging_agent', 'coding_agent', 'architect_agent', 'project_manager_agent']
        const completedAgents = new Set(nextUpdates.filter(u => u.status === 'completed').map(u => u.agent))
        setOverallProgress((completedAgents.size / agents.length) * 100)
        return nextUpdates
      })

    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnected(false)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setConnected(false)
    }

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [executionId])

  const getAgentIcon = (agent: string) => {
    const icons: Record<string, string> = {
      testing_agent: '🧪',
      debugging_agent: '🔍',
      coding_agent: '✏️',
      architect_agent: '🏗️',
      project_manager_agent: '📋',
    }
    return icons[agent] || '⚙️'
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#10b981'
      case 'running':
        return '#f59e0b'
      case 'failed':
        return '#ef4444'
      default:
        return '#9ca3af'
    }
  }

  return (
    <div className="execution-monitor">
      <div className="monitor-header">
        <h2>Real-Time Execution Monitor</h2>
        <div className="connection-status">
          <span className={`status-dot ${connected ? 'connected' : 'disconnected'}`}></span>
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      <div className="progress-section">
        <div className="progress-label">
          Overall Progress: {Math.round(overallProgress)}%
        </div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${overallProgress}%` }}></div>
        </div>
      </div>

      <div className="updates-timeline">
        {updates.map((update, idx) => (
          <div key={idx} className="update-item" style={{ borderLeftColor: getStatusColor(update.status) }}>
            <div className="update-agent">
              <span className="agent-icon">{getAgentIcon(update.agent)}</span>
              <div className="agent-info">
                <div className="agent-name">{update.agent.replace(/_/g, ' ')}</div>
                <div className="agent-time">{new Date(update.timestamp).toLocaleTimeString()}</div>
              </div>
            </div>
            <div className="update-status">
              <span className={`status-badge status-${update.status}`}>
                {update.status}
              </span>
            </div>
            {update.data && (
              <div className="update-data">
                <pre>{JSON.stringify(update.data, null, 2)}</pre>
              </div>
            )}
          </div>
        ))}

        {updates.length === 0 && (
          <div className="no-updates">
            Waiting for execution to start...
          </div>
        )}
      </div>
    </div>
  )
}
