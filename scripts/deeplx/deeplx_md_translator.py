import sys
import os
import re
import argparse
from typing import List
from deeplx_client import DeepLXClient

class MarkdownTranslator:
    """
    Tradutor de arquivos Markdown integrando com DeepLX / DLX.
    Preserva a estrutura do Markdown (código inline, blocos de código, YAML frontmatter, links).
    """
    def __init__(self, client: DeepLXClient, target_lang: str = "PT"):
        self.client = client
        self.target_lang = target_lang

    def _protect_inline_code_and_links(self, text: str):
        """
        Substitui temporariamente trechos de código inline (`...`) e links `[texto](url)` 
        por placeholders para que o tradutor não corrompa a sintaxe ou URLs.
        """
        placeholders = {}
        counter = 0

        # Proteger links [texto](url) -> preservar a URL
        def link_replacer(match):
            nonlocal counter
            label = match.group(1)
            url = match.group(2)
            # Traduzir apenas o rótulo do link se houver texto
            translated_label = self.client.translate(label, target_lang=self.target_lang) if label.strip() else label
            placeholder = f"__LINK_PLACEHOLDER_{counter}__"
            counter += 1
            placeholders[placeholder] = f"[{translated_label}]({url})"
            return placeholder

        # Expressão regular para links markdown: [texto](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_replacer, text)

        # Proteger código inline `code`
        def code_replacer(match):
            nonlocal counter
            placeholder = f"__CODE_PLACEHOLDER_{counter}__"
            counter += 1
            placeholders[placeholder] = match.group(0)
            return placeholder

        text = re.sub(r'`[^`]+`', code_replacer, text)

        return text, placeholders

    def _restore_placeholders(self, text: str, placeholders: dict) -> str:
        for placeholder, original in placeholders.items():
            text = text.replace(placeholder, original)
        return text

    def translate_line(self, line: str) -> str:
        """
        Traduz uma linha de prosa mantendo elementos do Markdown (cabeçalhos #, marcadores de lista -, *, números).
        """
        stripped = line.strip()
        if not stripped:
            return line

        # Preservar recuo inicial
        indent = line[:len(line) - len(line.lstrip())]

        # Verificar se é um cabeçalho Markdown (# , ## , ### , etc)
        header_match = re.match(r'^(#{1,6}\s+)(.*)', stripped)
        if header_match:
            h_prefix = header_match.group(1)
            h_content = header_match.group(2)
            protected_content, placeholders = self._protect_inline_code_and_links(h_content)
            translated = self.client.translate(protected_content, target_lang=self.target_lang)
            restored = self._restore_placeholders(translated, placeholders)
            return indent + h_prefix + restored

        # Verificar se é um item de lista (- , * , + ou 1. )
        list_match = re.match(r'^([-*+]\s+|\d+\.\s+)(.*)', stripped)
        if list_match:
            l_prefix = list_match.group(1)
            l_content = list_match.group(2)
            protected_content, placeholders = self._protect_inline_code_and_links(l_content)
            translated = self.client.translate(protected_content, target_lang=self.target_lang)
            restored = self._restore_placeholders(translated, placeholders)
            return indent + l_prefix + restored

        # Linha de texto normal de prosa
        protected_line, placeholders = self._protect_inline_code_and_links(stripped)
        translated = self.client.translate(protected_line, target_lang=self.target_lang)
        restored = self._restore_placeholders(translated, placeholders)

        return indent + restored

    def translate_file(self, src_path: str, dst_path: str) -> bool:
        """
        Lê o arquivo Markdown de origem, traduz a prosa linha por linha (ignorando blocos de código e YAML frontmatter)
        e grava o arquivo traduzido no destino.
        """
        if not os.path.exists(src_path):
            print(f"Erro: Arquivo {src_path} não encontrado.")
            return False

        print(f"[MarkdownTranslator] Traduzindo '{src_path}' -> '{dst_path}'...")

        with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        output_lines: List[str] = []
        in_code_block = False
        in_yaml_frontmatter = False

        for i, raw_line in enumerate(lines):
            line = raw_line.rstrip("\r\n")

            # Detectar início/fim de YAML frontmatter (na primeira linha)
            if i == 0 and line.strip() == "---":
                in_yaml_frontmatter = True
                output_lines.append(line)
                continue
            elif in_yaml_frontmatter:
                output_lines.append(line)
                if line.strip() == "---":
                    in_yaml_frontmatter = False
                continue

            # Detectar blocos de código fenced ``` ou ~~~
            if line.strip().startswith("```") or line.strip().startswith("~~~"):
                in_code_block = not in_code_block
                output_lines.append(line)
                continue

            # Se estiver dentro de bloco de código ou linha vazia, manter inalterado
            if in_code_block or not line.strip():
                output_lines.append(line)
                continue

            # Traduzir linha de prosa
            translated_line = self.translate_line(line)
            output_lines.append(translated_line)

        # Salvar arquivo traduzido
        dst_dir = os.path.dirname(dst_path)
        if dst_dir and not os.path.exists(dst_dir):
            os.makedirs(dst_dir, exist_ok=True)

        with open(dst_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines) + "\n")

        print(f"[MarkdownTranslator] Concluído! {len(output_lines)} linhas processadas.")
        return True

def main():
    parser = argparse.ArgumentParser(description="Tradutor de arquivos Markdown usando DeepLX / DLX API")
    parser.add_argument("input", help="Caminho do arquivo Markdown de entrada")
    parser.add_argument("-o", "--output", help="Caminho do arquivo traduzido de saída (padrão: <input>.pt-BR.md)")
    parser.add_argument("--url", default="http://127.0.0.1:1188", help="URL base da API DeepLX (ex: http://127.0.0.1:1188)")
    parser.add_argument("--target", default="PT", help="Idioma alvo (ex: PT ou PT-BR)")

    args = parser.parse_args()

    out_path = args.output
    if not out_path:
        base, ext = os.path.splitext(args.input)
        out_path = f"{base}.pt-BR{ext}"

    client = DeepLXClient(base_url=args.url)
    health = client.check_health()
    if health.get("code") != 200:
        print(f"Aviso: Servidor DeepLX em {args.url} não respondeu 200 OK. Resposta: {health}")

    translator = MarkdownTranslator(client, target_lang=args.target)
    translator.translate_file(args.input, out_path)

if __name__ == "__main__":
    main()
