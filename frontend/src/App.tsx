import { useRef, useState } from 'react'
import { streamAgent } from './sse'
import { applyEvent } from './renderers'
import type { Block } from './types'
import './App.css'

export default function App() {
  const [message, setMessage] = useState('Qual o clima em São Paulo?')
  const [blocks, setBlocks] = useState<Block[]>([])
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const abort = useRef<AbortController | null>(null)

  async function enviar(e: React.FormEvent) {
    e.preventDefault()
    if (running || !message.trim()) return

    setBlocks([])
    setError(null)
    setRunning(true)
    abort.current = new AbortController()

    try {
      for await (const ev of streamAgent(message, abort.current.signal)) {
        setBlocks((atuais) => applyEvent(atuais, ev))
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setRunning(false)
    }
  }

  return (
    <main className="app">
      <header>
        <h1>p1-agent</h1>
        <p>Agent com tool de clima, streaming via SSE.</p>
      </header>

      <form onSubmit={enviar}>
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Pergunte sobre o clima de uma cidade"
          disabled={running}
        />
        <button type="submit" disabled={running || !message.trim()}>
          {running ? 'Rodando…' : 'Enviar'}
        </button>
      </form>

      <section className="timeline">
        {blocks.map((b) => {
          if (b.kind === 'text') {
            // O modelo devolve content vazio na passada em que decide chamar
            // a tool -- nao ha rascunho para pintar ali.
            if (!b.content) return null
            return (
              <article key={b.id} className={`bloco texto ${b.done ? 'final' : 'rascunho'}`}>
                <span className="rotulo">{b.done ? 'resposta' : 'digitando'}</span>
                <p>{b.content}</p>
              </article>
            )
          }

          if (b.kind === 'tool_call') {
            return (
              <article key={b.id} className="bloco tool-call">
                <span className="rotulo">tool call</span>
                <code>
                  {b.name}({JSON.stringify(b.args)})
                </code>
              </article>
            )
          }

          if (b.kind === 'structured') {
            const fields = [
              ['Cidade', [b.data.city, b.data.country].filter(Boolean).join(', ')],
              ['Temperatura', b.data.temperature_c === null ? '' : `${b.data.temperature_c} °C`],
              ['Condição', b.data.condition ?? ''],
              ['Observado em', b.data.observed_at ?? ''],
              ['Fonte', b.data.source ?? ''],
            ].filter(([, value]) => value)

            return (
              <article key={b.id} className="bloco structured-output">
                <span className="rotulo">resultado estruturado — {b.data.status}</span>
                <p>{b.data.answer}</p>
                {fields.length > 0 && (
                  <dl>
                    {fields.map(([label, value]) => (
                      <div key={label}>
                        <dt>{label}</dt>
                        <dd>{value}</dd>
                      </div>
                    ))}
                  </dl>
                )}
              </article>
            )
          }

          return (
            <article key={b.id} className="bloco tool-result">
              <span className="rotulo">
                {b.output === null ? `${b.name} — executando…` : `${b.name} — resultado`}
              </span>
              {b.output !== null && <pre>{b.output}</pre>}
            </article>
          )
        })}
      </section>

      {error && <p className="erro">{error}</p>}
    </main>
  )
}
