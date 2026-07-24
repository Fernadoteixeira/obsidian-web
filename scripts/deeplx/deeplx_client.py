import json
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

DEFAULT_DEEPLX_URL = "http://127.0.0.1:1188"

class DeepLXClient:
    """
    Cliente para a API de tradução DeepLX / DLX (OwO-Network/DLX).
    Suporta verificação de status, tradução de texto simples e retentativas automáticas.
    """
    def __init__(self, base_url: str = DEFAULT_DEEPLX_URL, timeout: int = 15, max_retries: int = 5, retry_delay: float = 2.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def check_health(self) -> Dict[str, Any]:
        """
        Verifica a conexão com a API DeepLX no endpoint raiz (GET /).
        Retorna o JSON retornado pela API (ex: code 200, DLX Translation API message).
        """
        req = urllib.request.Request(
            f"{self.base_url}/",
            headers={"User-Agent": "DeepLX-Python-Client/1.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = resp.read().decode("utf-8")
                return json.loads(data)
        except Exception as e:
            return {"code": 500, "error": str(e)}

    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "PT") -> str:
        """
        Traduz um texto utilizando POST /translate no servidor DeepLX.
        Aplica retentativa em caso de erro 429 (Too Many Requests) ou falhas temporárias de rede.
        """
        if not text or not text.strip():
            return text

        url = f"{self.base_url}/translate"
        payload = {
            "text": text,
            "source_lang": source_lang.upper(),
            "target_lang": target_lang.upper()
        }
        json_payload = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "DeepLX-Python-Client/1.0"
        }

        delay = self.retry_delay
        for attempt in range(1, self.max_retries + 1):
            try:
                req = urllib.request.Request(url, data=json_payload, headers=headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    res_body = resp.read().decode("utf-8")
                    data = json.loads(res_body)

                    if isinstance(data, dict):
                        if data.get("code") == 200 and "data" in data:
                            return data["data"]
                        elif "data" in data and isinstance(data["data"], str):
                            return data["data"]
                        elif "translated_text" in data:
                            return data["translated_text"]

                    raise ValueError(f"Resposta inesperada do DeepLX: {data}")

            except urllib.error.HTTPError as err:
                if err.code == 429 and attempt < self.max_retries:
                    print(f"[DeepLX] Erro 429 (Limitação de taxa). Aguardando {delay:.1f}s (Tentativa {attempt}/{self.max_retries})...")
                    time.sleep(delay)
                    delay *= 2.0  # Backoff exponencial
                elif attempt < self.max_retries:
                    print(f"[DeepLX] HTTP Error {err.code}. Aguardando {delay:.1f}s...")
                    time.sleep(delay)
                else:
                    print(f"[DeepLX] Falha ao traduzir após {self.max_retries} tentativas: HTTP {err.code}")
                    return text
            except Exception as ex:
                if attempt < self.max_retries:
                    time.sleep(delay)
                else:
                    print(f"[DeepLX] Erro de conexão/processamento: {ex}")
                    return text

        return text

if __name__ == "__main__":
    client = DeepLXClient()
    print("--- Testando Conexão com DeepLX API ---")
    status = client.check_health()
    print("Status do Servidor:", status)
    
    if status.get("code") == 200:
        sample_text = "Hello world! DeepLX translation service is ready."
        print(f"\nTexto Original: {sample_text}")
        result = client.translate(sample_text, target_lang="PT")
        print(f"Tradução PT-BR: {result}")
