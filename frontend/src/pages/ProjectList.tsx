import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

interface Project {
  id: string
  name: string
  description?: string
  repository_url?: string
}

export default function ProjectList() {
  const demoProjects: Project[] = [
    { id: 'demo-auth', name: 'identity-service', description: 'Authentication and session management', repository_url: 'Demo workspace' },
    { id: 'demo-api', name: 'payments-api', description: 'REST API with validation coverage', repository_url: 'Demo workspace' },
  ]
  const isDemo = localStorage.getItem('auth_token') === 'demo-token'
  const [projects, setProjects] = useState<Project[]>(isDemo ? demoProjects : [])
  const [newProject, setNewProject] = useState({ name: '', description: '' })
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadProjects = async () => {
    if (isDemo) {
      setLoading(false)
      return
    }
    try {
      const response = await fetch('/api/projects')
      if (!response.ok) throw new Error('Unable to load projects')
      setProjects(await response.json())
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load projects')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProjects()
  }, [])

  const handleCreateProject = async () => {
    if (!newProject.name.trim()) {
      setError('Project name is required')
      return
    }

    setSubmitting(true)
    if (isDemo) {
      setProjects(current => [...current, { id: `demo-${Date.now()}`, name: newProject.name.trim(), description: newProject.description.trim() || 'New demo project', repository_url: 'Demo workspace' }])
      setNewProject({ name: '', description: '' })
      setSubmitting(false)
      return
    }
    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newProject.name.trim(),
          description: newProject.description.trim() || null,
        }),
      })
      if (!response.ok) {
        const payload = await response.json().catch(() => null)
        throw new Error(payload?.detail || 'Unable to create project')
      }
      setNewProject({ name: '', description: '' })
      await loadProjects()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create project')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="projects-page">
      <h1>Projects</h1>

      {error && <div className="alert alert-error">{error}</div>}

      <section className="create-project-panel">
        <h2>New Project</h2>
        <div className="form-group">
          <input
            type="text"
            className="input"
            placeholder="Project name"
            value={newProject.name}
            onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
          />
        </div>
        <div className="form-group">
          <textarea
            className="textarea"
            placeholder="Project description (optional)"
            value={newProject.description}
            onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
          />
        </div>
        <button className="btn btn-primary" onClick={handleCreateProject} disabled={submitting}>
          {submitting ? 'Creating...' : 'Create Project'}
        </button>
      </section>

      <section className="projects-list">
        <h2>Existing Projects</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Repository</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={4}>Loading projects...</td></tr>}
            {!loading && projects.length === 0 && <tr><td colSpan={4}>No projects yet. Create your first project above.</td></tr>}
            {projects.map(project => (
              <tr key={project.id}>
                <td><strong>{project.name}</strong></td>
                <td>{project.description || 'No description'}</td>
                <td>{project.repository_url || 'Local project'}</td>
                <td>
                  <Link className="btn btn-sm btn-primary" to={`/projects/${project.id}`}>View</Link>
                  <Link className="btn btn-sm btn-secondary" to={`/projects/${project.id}`}>Run Analysis</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}
