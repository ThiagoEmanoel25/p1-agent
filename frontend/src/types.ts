/** O StreamEvent do LangGraph, como chega no `data:` do SSE (AC-04/AC-05). */
export interface StreamEvent {
  event: string
  name: string
  run_id: string
  data: {
    chunk?: { content?: string }
    input?: Record<string, unknown>
    output?: {
      content?: string
      tool_calls?: { name: string; args: Record<string, unknown> }[]
    }
  }
}

/** Cada bloco pintado na timeline. Tool call, resultado e texto final
 *  sao estados separados (AC-07). */
export type Block =
  | { kind: 'text'; id: string; content: string; done: boolean }
  | { kind: 'tool_call'; id: string; name: string; args: Record<string, unknown> }
  | { kind: 'tool_result'; id: string; name: string; output: string | null }
