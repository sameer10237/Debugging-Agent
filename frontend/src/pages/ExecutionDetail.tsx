import { useParams } from 'react-router-dom'
import { useState, useEffect } from 'react'

export default function ExecutionDetail() {
  const { id } = useParams()
  const [execution, setExecution] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [fixesApplied, setFixesApplied] = useState(false)

  useEffect(() => {
    if (id === 'demo-execution') {
      setExecution({ id, status: 'completed', metadata: { project_id: 'identity-service', workflow_results: { final_state: { test_results: { failed: 2 }, proposed_fixes: [{}, {}], root_causes: ['Missing null-check in auth service', 'Incorrect error status code'], confidence: 95 }, results: { testing_agent: { status: 'completed' }, debugging_agent: { status: 'completed' }, coding_agent: { status: 'completed' }, architect_agent: { status: 'completed' }, project_manager_agent: { status: 'completed' } } } } })
      setLoading(false)
      return
    }
    fetch(`/api/executions/${id}/results`)
      .then(async response => {
        if (!response.ok) throw new Error('Execution not found')
        return response.json()
      })
      .then(setExecution)
      .catch(err => setError(err instanceof Error ? err.message : 'Unable to load execution'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="loading">Loading execution details...</div>
  if (error) return <div className="alert alert-error">{error}</div>

  const workflowResults = execution.metadata?.workflow_results?.results || {}
  const completedAgents = Object.values(workflowResults).filter((agent: any) => agent.status === 'completed').length
  const finalState = execution.metadata?.workflow_results?.final_state || {}

  const downloadResults = () => {
    const report = JSON.stringify({ execution_id: id, status: execution.status, findings: finalState }, null, 2)
    const link = document.createElement('a')
    link.href = URL.createObjectURL(new Blob([report], { type: 'application/json' }))
    link.download = `debugging-report-${id}.json`
    link.click()
    URL.revokeObjectURL(link.href)
  }

  return (
    <div className="execution-detail">
      <h1>Execution #{id?.slice(0, 8)}</h1>

      <div className="execution-header">
        <div className="info-card">
          <div className="info-label">Project</div>
          <div className="info-value">{execution.metadata?.project_id || 'Project'}</div>
        </div>
        <div className="info-card">
          <div className="info-label">Status</div>
          <div className="info-value">
            <span className={`badge badge-${execution.status}`}>{execution.status}</span>
          </div>
        </div>
        <div className="info-card">
          <div className="info-label">Confidence</div>
          <div className="info-value">{execution.metadata?.workflow_results?.final_state?.confidence || 0}%</div>
        </div>
      </div>

      <section className="agent-timeline">
        <h2>Agent Execution Timeline</h2>
        <div className="timeline">
          {Object.entries(execution.metadata?.workflow_results?.results || {}).map(([name, agent]: [string, any]) => (
            <div key={name} className="timeline-item">
              <div className={`timeline-marker ${agent.status === 'completed' ? 'completed' : 'pending'}`}>{agent.status === 'completed' ? '✓' : '!'}</div>
              <div className="timeline-content">
                <div className="timeline-title">{name.replace(/_/g, ' ')}</div>
                <div className="timeline-duration">Status: {agent.status}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="findings" id="findings">
        <h2>Analysis Findings</h2>
        <div className="findings-grid">
          <div className="finding-card">
            <div className="finding-icon">🔍</div>
            <div className="finding-title">Total Failures</div>
            <div className="finding-value">{execution.metadata?.workflow_results?.final_state?.test_results?.failed || 0}</div>
          </div>
          <div className="finding-card">
            <div className="finding-icon">🎯</div>
            <div className="finding-title">Root Causes Found</div>
            <div className="finding-value">{completedAgents}</div>
          </div>
          <div className="finding-card">
            <div className="finding-icon">✓</div>
            <div className="finding-title">Fixes Proposed</div>
            <div className="finding-value">{execution.metadata?.workflow_results?.final_state?.proposed_fixes?.length || 0}</div>
          </div>
        </div>

        <div className="root-causes">
          <h3>Root Causes</h3>
          <ul>
            {(execution.metadata?.workflow_results?.final_state?.root_causes || [execution.error || 'Detailed findings will appear after the workflow completes.']).map((cause: string) => <li key={cause}>{cause}</li>)}
          </ul>
        </div>
      </section>

      <div className="actions">
        <button className="btn btn-primary" onClick={() => document.getElementById('findings')?.scrollIntoView({ behavior: 'smooth' })}>View Detailed Report</button>
        <button className="btn btn-secondary" onClick={downloadResults}>Download Results</button>
        <button className="btn btn-success" onClick={() => setFixesApplied(true)} disabled={fixesApplied}>{fixesApplied ? 'Fixes Applied' : 'Apply Fixes'}</button>
      </div>
      {fixesApplied && <div className="alert alert-success">Demo fixes applied. In production, this action would open a reviewed pull request.</div>}
    </div>
  )
}
