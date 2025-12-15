import type {
  ResearchRequest,
  ComparisonResult,
  RecentResearch
} from './types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class SDKClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Execute research with all agents
   */
  async executeResearch(request: ResearchRequest): Promise<ComparisonResult> {
    const response = await fetch(`${this.baseUrl}/api/research`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Research failed: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Get research history
   */
  async getHistory(limit: number = 50): Promise<RecentResearch[]> {
    const response = await fetch(
      `${this.baseUrl}/api/history?limit=${limit}`
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch history: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Get specific research result by ID
   */
  async getResearchById(id: string): Promise<ComparisonResult> {
    const response = await fetch(`${this.baseUrl}/api/research/${id}`)

    if (!response.ok) {
      throw new Error(`Failed to fetch research: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Delete research result
   */
  async deleteResearch(id: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/research/${id}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      throw new Error(`Failed to delete research: ${response.statusText}`)
    }
  }

  /**
   * Get dashboard stats
   */
  async getStats(): Promise<{
    total_research: number
    total_queries: number
    total_tokens: number
    total_cost: number
    active_agents: number
  }> {
    const response = await fetch(`${this.baseUrl}/api/stats`)

    if (!response.ok) {
      throw new Error(`Failed to fetch stats: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Server-Sent Events stream for real-time research updates
   */
  streamResearch(
    request: ResearchRequest,
    onUpdate: (data: any) => void,
    onComplete: (result: ComparisonResult) => void,
    onError: (error: Error) => void
  ): () => void {
    const eventSource = new EventSource(
      `${this.baseUrl}/api/research/stream?` +
      `query=${encodeURIComponent(request.query)}&` +
      `domain=${request.domain}&` +
      `max_tokens=${request.max_tokens || 500}`
    )

    eventSource.addEventListener('update', (event) => {
      onUpdate(JSON.parse(event.data))
    })

    eventSource.addEventListener('complete', (event) => {
      onComplete(JSON.parse(event.data))
      eventSource.close()
    })

    eventSource.addEventListener('error', (event) => {
      onError(new Error('Stream connection failed'))
      eventSource.close()
    })

    // Return cleanup function
    return () => {
      eventSource.close()
    }
  }
}

export const sdkClient = new SDKClient()
