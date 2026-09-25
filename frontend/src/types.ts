
export interface WeatherOutput {
  answer: string
  city: string | null
  country: string | null
  temperature_c: number | null
  condition: string | null
  observed_at: string | null
  source: string | null
  status: 'success' | 'error' | 'not_weather'
}

export interface StreamEvent {
  event: string
  name: string
  run_id: string

  data: {
    chunk?: {
      content?: string
    }

    input?: Record<string, unknown>

    output?: {
      content?: string
      tool_calls?: {
        name: string
        args: Record<string, unknown>
      }[]
    }

    structured?: WeatherOutput
  }
}

export type Block =
  | {
      kind: 'text'
      id: string
      content: string
      done: boolean
    }
  | {
      kind: 'tool_call'
      id: string
      name: string
      args: Record<string, unknown>
    }
  | {
      kind: 'tool_result'
      id: string
      name: string
      output: string | null
    }
  | {
      kind: 'structured'
      id: string
      data: WeatherOutput
    }