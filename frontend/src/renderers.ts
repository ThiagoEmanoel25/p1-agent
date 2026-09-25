import type { Block, StreamEvent } from './types'

/**
 * Renderer da familia on_chat_model_*.
 *
 * AC-07: os tokens de on_chat_model_stream concatenam num rascunho, e o
 * on_chat_model_end daquela passada substitui o rascunho pelo texto final.
 */
function renderChatModel(blocks: Block[], ev: StreamEvent): Block[] {
  switch (ev.event) {
    case 'on_chat_model_start':
      return [...blocks, { kind: 'text', id: ev.run_id, content: '', done: false }]

    case 'on_chat_model_stream': {
      const token = ev.data.chunk?.content ?? ''
      if (!token) return blocks
      return blocks.map((b) =>
        b.kind === 'text' && b.id === ev.run_id
          ? { ...b, content: b.content + token }
          : b,
      )
    }

    case 'on_chat_model_end': {
      // O end substitui o rascunho -- nao concatena.
      const final = ev.data.output?.content ?? ''
      const substituido = blocks.map((b) =>
        b.kind === 'text' && b.id === ev.run_id
          ? { ...b, content: final, done: true }
          : b,
      )

      // Quando o modelo decide chamar tool, o content vem vazio e a decisao
      // vive em tool_calls. Vira um bloco proprio (AC-07).
      const toolCalls = ev.data.output?.tool_calls ?? []
      const chamadas: Block[] = toolCalls.map((tc, i) => ({
        kind: 'tool_call',
        id: `${ev.run_id}-tc-${i}`,
        name: tc.name,
        args: tc.args,
      }))

      return [...substituido, ...chamadas]
    }

    default:
      return blocks
  }
}

/** Renderer da familia on_tool_*. */
function renderTool(blocks: Block[], ev: StreamEvent): Block[] {
  switch (ev.event) {
    case 'on_tool_start':
      return [
        ...blocks,
        { kind: 'tool_result', id: ev.run_id, name: ev.name, output: null },
      ]

    case 'on_tool_end':
      return blocks.map((b) =>
        b.kind === 'tool_result' && b.id === ev.run_id
          ? { ...b, output: ev.data.output?.content ?? '' }
          : b,
      )

    default:
      return blocks
  }
}

/** Renderer do evento final emitido pelo formatador estruturado. */
function renderStructuredOutput(blocks: Block[], ev: StreamEvent): Block[] {
  const data = ev.data.structured
  if (!data) return blocks

  // O backend emite uma resposta estruturada por execução. Usamos o run_id
  // para evitar duplicação caso o evento seja reenviado pelo stream.
  const semRespostaAnterior = blocks.filter(
    (block) => block.kind !== 'structured' || block.id !== ev.run_id,
  )

  return [...semRespostaAnterior, { kind: 'structured', id: ev.run_id, data }]
}

/**
 * AC-06: evento chega, checa o tipo, escolhe o renderer.
 * Tipo fora de on_chat_model_* / on_tool_* lanca erro.
 */
export function applyEvent(blocks: Block[], ev: StreamEvent): Block[] {
  if (ev.event.startsWith('on_chat_model_')) return renderChatModel(blocks, ev)
  if (ev.event.startsWith('on_tool_')) return renderTool(blocks, ev)
  if (ev.event === 'on_structured_output') return renderStructuredOutput(blocks, ev)

  throw new Error(`Tipo de evento nao suportado: ${ev.event}`)
}
