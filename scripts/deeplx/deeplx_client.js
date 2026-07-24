/**
 * Cliente de tradução DeepLX / DLX em Node.js (OwO-Network/DLX)
 * Suporta retentativa com backoff exponencial para contornar erros 429.
 */

const DEFAULT_URL = 'http://127.0.0.1:1188';

class DeepLXClient {
  constructor(baseUrl = DEFAULT_URL, options = {}) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.maxRetries = options.maxRetries || 5;
    this.retryDelay = options.retryDelay || 2000;
  }

  /**
   * Verifica a saúde da API DeepLX no endpoint raiz (GET /)
   */
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseUrl}/`);
      const data = await response.json();
      return data;
    } catch (err) {
      return { code: 500, error: err.message };
    }
  }

  /**
   * Traduz um texto para o idioma desejado (ex: PT / PT-BR)
   */
  async translate(text, sourceLang = 'auto', targetLang = 'PT') {
    if (!text || !text.trim()) return text;

    const url = `${this.baseUrl}/translate`;
    const body = JSON.stringify({
      text: text,
      source_lang: sourceLang.toUpperCase(),
      target_lang: targetLang.toUpperCase(),
    });

    let currentDelay = this.retryDelay;

    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: body,
        });

        if (res.status === 429) {
          console.warn(`[DeepLX] 429 Rate Limit (tentativa ${attempt}/${this.maxRetries}). Aguardando ${currentDelay}ms...`);
          await new Promise((resolve) => setTimeout(resolve, currentDelay));
          currentDelay *= 2;
          continue;
        }

        if (!res.ok) {
          throw new Error(`HTTP Error ${res.status}: ${res.statusText}`);
        }

        const data = await res.json();
        if (data.code === 200 && data.data) {
          return data.data;
        } else if (data.data && typeof data.data === 'string') {
          return data.data;
        }

        throw new Error(`Resposta inesperada: ${JSON.stringify(data)}`);
      } catch (err) {
        if (attempt === this.maxRetries) {
          console.error(`[DeepLX] Falha ao traduzir após ${this.maxRetries} tentativas:`, err.message);
          return text;
        }
        await new Promise((resolve) => setTimeout(resolve, currentDelay));
      }
    }

    return text;
  }
}

module.exports = { DeepLXClient };

// Exemplo de uso se executado diretamente
if (require.main === module) {
  (async () => {
    const client = new DeepLXClient();
    console.log('--- Testando DeepLX Client JS ---');
    const health = await client.checkHealth();
    console.log('Status da API:', health);

    if (health.code === 200) {
      const translated = await client.translate('Hello world from Node.js DeepLX Client!', 'auto', 'PT');
      console.log('Tradução PT-BR:', translated);
    }
  })();
}
