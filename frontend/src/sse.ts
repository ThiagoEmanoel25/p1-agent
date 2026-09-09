import type { StreamEvent } from './types'

/**
 * Consome o SSE de POST /agent/execute.
 *
 * O EventSource nativo do browser so faz GET, e o AC-01 exige POST com body
 * JSON -- entao lemos o corpo com fetch + ReadableStream e parseamos o
 * protocolo SSE na mao.
 */
export async function* streamAgent(
  message: string,
  signal?: AbortSignal,
): AsyncGenerator<StreamEvent> {
  const response = await fetch('/agent/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
    signal,
  })

  if (!response.ok || !response.body) {
    throw new Error(`HTTP ${response.status} ao chamar /agent/execute`)
  }

  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += value

    // Frames SSE sao separados por linha em branco.
    let sep: number
    while ((sep = buffer.indexOf('\n\n')) !== -1) {
      const frame = buffer.slice(0, sep)
      buffer = buffer.slice(sep + 2)

      const dataLine = frame
        .split('\n')
        .find((line) => line.startsWith('data:'))

      if (dataLine) {
        yield JSON.parse(dataLine.slice(5)) as StreamEvent
      }
    }
  }
}
