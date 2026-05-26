import React, { useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Upload, FileText, ShieldCheck } from 'lucide-react'
import './style.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function ScoreCard({ title, value }) {
  return <div className="card"><div className="muted">{title}</div><div className="score">{value}</div></div>
}

function App() {
  const [logFile, setLogFile] = useState(null)
  const [ruleFile, setRuleFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function submit() {
    if (!logFile) return setError('로그 파일을 선택하세요.')
    setError('')
    setLoading(true)
    const form = new FormData()
    form.append('log_file', logFile)
    if (ruleFile) form.append('rule_file', ruleFile)
    try {
      const res = await fetch(`${API_BASE}/api/analyze`, { method: 'POST', body: form })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || '분석 실패')
      setResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return <main>
    <section className="hero">
      <div><h1>LogSight AI</h1><p>보안 로그 품질 진단 및 관측성 사각지대 탐지 MVP</p></div>
      <ShieldCheck size={42}/>
    </section>
    <section className="panel">
      <label><Upload size={18}/> 로그 파일 CSV/JSON/JSONL<input type="file" onChange={e => setLogFile(e.target.files[0])}/></label>
      <label><FileText size={18}/> 룰 파일 YAML 선택<input type="file" onChange={e => setRuleFile(e.target.files[0])}/></label>
      <button onClick={submit} disabled={loading}>{loading ? '분석 중' : '분석 실행'}</button>
      {error && <div className="error">{error}</div>}
    </section>
    {result && <section className="results">
      <h2>{result.filename}</h2>
      <p className="muted">탐지 로그 유형: {result.detected_log_type} · 이벤트 {result.total_events}건</p>
      <div className="grid">
        <ScoreCard title="Log Quality" value={result.scores.log_quality}/>
        <ScoreCard title="Detection Readiness" value={result.scores.detection_readiness}/>
        <ScoreCard title="Investigation Readiness" value={result.scores.investigation_readiness}/>
        <ScoreCard title="MITRE Observability" value={result.scores.mitre_observability}/>
        <ScoreCard title="Remediation Priority" value={result.scores.remediation_priority}/>
      </div>
      <div className="columns">
        <div className="box"><h3>품질 진단</h3>{result.findings.length ? result.findings.map((f,i)=><p key={i}><b>{f.severity}</b> {f.message} ({f.count})</p>) : <p>주요 결함 없음</p>}</div>
        <div className="box"><h3>AI 개선 리포트</h3><p>{result.report.executive_summary}</p><p>{result.report.technical_guide}</p><p>{result.report.audit_summary}</p></div>
      </div>
      <div className="box"><h3>룰 실행 가능성</h3><table><thead><tr><th>룰</th><th>상태</th><th>누락 필드</th><th>MITRE</th></tr></thead><tbody>{result.rule_results.map(r=><tr key={r.id}><td>{r.title}</td><td>{r.status}</td><td>{r.missing_fields.join(', ') || '-'}</td><td>{r.mitre_tactic}</td></tr>)}</tbody></table></div>
    </section>}
  </main>
}

createRoot(document.getElementById('root')).render(<App />)
