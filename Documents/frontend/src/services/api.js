const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:5000";

export const ChatService = {
  async initChat() {
    return this._fetch('/api/chat', 'POST', { etapa: 'inicio' });
  },

  async sendMessage(data) {
    return this._fetch('/api/chat', 'POST', data);
  },

  async _fetch(endpoint, method, body) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method,
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      const textData = await response.text();
      return textData ? JSON.parse(textData) : null;

    } catch (error) {
      console.error("Erro na requisição:", error);
      throw new Error(error.message || "Falha na comunicação");
    }
  }
};