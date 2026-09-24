import { useState } from 'react'
import './AnalysisResults.css'

interface SecurityFinding {
  test: string
  issue: string
  component: string
}

interface Analysis {
  test_name: string
  failure_type: string
  root_cause: string
  affected_components: string[]
  confidence: number
  security_implications?: string
}

interface AnalysisResultsProps {
  analyses: Analysis[]
  securityFindings: SecurityFinding[]
  overallRiskLevel: string
}

export default function AnalysisResults({
  analyses,
  securityFindings,
  overallRiskLevel,
}: AnalysisResultsProps) {
  const [expandedTest, setExpandedTest] = useState<string | null>(null)

  const getRiskBadgeClass = (riskLevel: string) => {
    switch (riskLevel) {
      case 'CRITICAL':
        return 'risk-critical'
      case 'HIGH':
        return 'risk-high'
      case 'MEDIUM':
        return 'risk-medium'
      case 'LOW':
        return 'risk-low'
      default:
        return 'risk-unknown'
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return '#10b981'
    if (confidence >= 60) return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className="analysis-results">
      {/* Risk Summary */}
      <div className={`risk-summary ${getRiskBadgeClass(overallRiskLevel)}`}>
        <div className="risk-icon">⚠️</div>
        <div className="risk-info">
          <div className="risk-label">Overall Risk Level</div>
          <div className="risk-value">{overallRiskLevel}</div>
        </div>
        <div className="findings-count">
          {securityFindings.length} Security Finding{securityFindings.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Security Findings */}
      {securityFindings.length > 0 && (
        <section className="security-section">
          <h3>🔒 Security Findings</h3>
          <div className="findings-list">
            {securityFindings.map((finding, idx) => (
              <div key={idx} className="finding-item">
                <div className="finding-severity">
                  {finding.issue.includes('CRITICAL') ? '🔴' : '🟡'}
                </div>
                <div className="finding-details">
                  <div className="finding-issue">{finding.issue}</div>
                  <div className="finding-component">Component: {finding.component}</div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Detailed Analysis */}
      <section className="analyses-section">
        <h3>📊 Detailed Analysis</h3>
        <div className="analyses-list">
          {analyses.map((analysis, idx) => (
            <div key={idx} className="analysis-card">
              <button
                className="analysis-header"
                onClick={() =>
                  setExpandedTest(expandedTest === analysis.test_name ? null : analysis.test_name)
                }
              >
                <div className="header-left">
                  <span className="expand-icon">
                    {expandedTest === analysis.test_name ? '▼' : '▶'}
                  </span>
                  <div className="test-info">
                    <div className="test-name">{analysis.test_name}</div>
                    <div className="failure-type">{analysis.failure_type}</div>
                  </div>
                </div>
                <div className="header-right">
                  <div
                    className="confidence-bar"
                    style={{
                      background: getConfidenceColor(analysis.confidence),
                      width: `${analysis.confidence}%`,
                    }}
                  />
                  <span className="confidence-value">{analysis.confidence}%</span>
                </div>
              </button>

              {expandedTest === analysis.test_name && (
                <div className="analysis-details">
                  <div className="detail-section">
                    <h4>Root Cause</h4>
                    <p>{analysis.root_cause}</p>
                  </div>

                  <div className="detail-section">
                    <h4>Affected Components</h4>
                    <div className="component-list">
                      {analysis.affected_components.map((comp, i) => (
                        <span key={i} className="component-tag">
                          {comp}
                        </span>
                      ))}
                    </div>
                  </div>

                  {analysis.security_implications && (
                    <div className="detail-section security-alert">
                      <h4>⚠️ Security Implications</h4>
                      <p>{analysis.security_implications}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Recommendations */}
      <section className="recommendations-section">
        <h3>✓ Recommendations</h3>
        <ul className="recommendations-list">
          {securityFindings.length > 0 && (
            <li>🔒 Address security findings before other improvements</li>
          )}
          {analyses.filter(a => a.confidence >= 80).length > 0 && (
            <li>
              ⚡ Implement fixes for{' '}
              {analyses.filter(a => a.confidence >= 80).length} high-confidence analysis/analyses
            </li>
          )}
          <li>🧪 Run comprehensive regression tests after fixes</li>
          <li>📋 Document all changes in commit messages</li>
        </ul>
      </section>
    </div>
  )
}
