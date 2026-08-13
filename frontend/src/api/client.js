/**
 * API Client — all requests go through FastAPI backend.
 * Uses environment variable configuration for base URL.
 */

const normalizeBaseUrl = (rawUrl) => {
  const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production';
  
  if (!rawUrl || typeof rawUrl !== 'string' || !rawUrl.trim()) {
    if (isProd) {
      throw new Error(
        'VITE_API_BASE_URL environment variable is missing in production build. Please set VITE_API_BASE_URL in Vercel settings.'
      );
    }
    return 'http://localhost:8000';
  }

  const cleaned = rawUrl.trim().replace(/['"]/g, '').replace(/\/+$/, '');
  if (cleaned.includes('example.com') || cleaned.includes('api.yourdomain.com')) {
    if (isProd) {
      throw new Error(
        `Invalid VITE_API_BASE_URL "${cleaned}" configured in production build.`
      );
    }
    return 'http://localhost:8000';
  }

  return cleaned;
};

const API_BASE = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL);

class ApiClient {
  getBaseUrl() {
    return API_BASE;
  }

  /**
   * Make a fetch request with standard error handling.
   */
  async _fetch(url, options = {}) {
    const config = {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    };

    const endpointUrl = `${API_BASE}${url.startsWith('/') ? url : `/${url}`}`;

    try {
      const response = await fetch(endpointUrl, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Request failed with status ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
        throw new Error(
          `Unable to connect to the backend server at ${API_BASE}. Please verify backend server status.`
        );
      }
      throw error;
    }
  }


  // --- Chat ---
  async sendChat(query, threadId = null) {
    return this._fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ query, thread_id: threadId }),
    });
  }

  /**
   * Stream real-time agent execution progress via Server-Sent Events (SSE).
   */
  async streamChat(query, threadId = null, onProgress, onComplete, onError) {
    try {
      const response = await fetch(`${API_BASE}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, thread_id: threadId }),
      });

      if (!response.ok) {
        throw new Error(`Streaming failed with status ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep remaining incomplete line in buffer

        for (const line of lines) {
          const trimmed = line.strip ? line.strip() : line.trim();
          if (trimmed.startsWith('data: ')) {
            const jsonStr = trimmed.slice(6);
            try {
              const data = JSON.parse(jsonStr);
              if (data.event === 'finish') {
                onComplete && onComplete(data);
              } else if (data.event === 'error') {
                onError && onError(new Error(data.error || 'Stream error'));
              } else {
                onProgress && onProgress(data);
              }
            } catch (e) {
              console.warn('Malformed SSE JSON payload:', jsonStr);
            }
          }
        }
      }
    } catch (err) {
      onError && onError(err);
    }
  }

  // --- Recommendations (ML Engine) ---
  async getRecommendations(criteria) {
    return this._fetch('/api/recommend', {
      method: 'POST',
      body: JSON.stringify(criteria),
    });
  }

  // --- Players ---
  async searchPlayers(query, season = null) {
    const params = new URLSearchParams({ q: query });
    if (season) params.append('season', season);
    return this._fetch(`/api/players/search?${params}`);
  }

  async getPlayerNews(name) {
    return this._fetch(`/api/players/news?name=${encodeURIComponent(name)}`);
  }

  async comparePlayers(player1, player2) {
    return this._fetch('/api/players/compare', {
      method: 'POST',
      body: JSON.stringify({ player1, player2 }),
    });
  }

  // --- Scout ---
  async runScout(requirements, threadId = null) {
    return this._fetch('/api/scout', {
      method: 'POST',
      body: JSON.stringify({ requirements, thread_id: threadId }),
    });
  }

  // --- Health ---
  async healthCheck() {
    return this._fetch('/api/health');
  }
}

const api = new ApiClient();
export default api;

