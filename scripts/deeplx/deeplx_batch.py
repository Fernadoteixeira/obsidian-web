import os
import glob
import argparse
import time
from deeplx_client import DeepLXClient
from deeplx_md_translator import MarkdownTranslator

def batch_translate_directory(
    directory_path: str,
    target_dir: str = None,
    suffix: str = ".pt-BR",
    base_url: str = "http://127.0.0.1:1188",
    target_lang: str = "PT",
    delay_between_files: float = 1.0,
    recursive: bool = True
):
    """
    Vaste um diretório em busca de arquivos .md e executa a tradução em lote usando DeepLX.
    """
    client = DeepLXClient(base_url=base_url)
    health = client.check_health()
    print(f"Status da API DeepLX ({base_url}):", health)

    if health.get("code") != 200:
        print(f"Erro: Não foi possível conectar à API DeepLX em {base_url}.")
        return

    translator = MarkdownTranslator(client, target_lang=target_lang)

    pattern = os.path.join(directory_path, "**", "*.md") if recursive else os.path.join(directory_path, "*.md")
    md_files = [f for f in glob.glob(pattern, recursive=recursive) if not f.endswith(f"{suffix}.md")]

    print(f"\n--- Encontrados {len(md_files)} arquivos Markdown para tradução em '{directory_path}' ---\n")

    for idx, src_file in enumerate(md_files, 1):
        if target_dir:
            rel_path = os.path.relpath(src_file, directory_path)
            base_rel, ext = os.path.splitext(rel_path)
            dst_file = os.path.join(target_dir, f"{base_rel}{suffix}{ext}")
        else:
            base, ext = os.path.splitext(src_file)
            dst_file = f"{base}{suffix}{ext}"

        print(f"[{idx}/{len(md_files)}] Processando: {src_file}")
        translator.translate_file(src_file, dst_file)
        
        if idx < len(md_files) and delay_between_files > 0:
            time.sleep(delay_between_files)

    print(f"\n✅ Tradução em lote concluída! {len(md_files)} arquivos traduzidos para PT-BR.")

def main():
    parser = argparse.ArgumentParser(description="Tradução em lote de diretórios Markdown via DeepLX / DLX")
    parser.add_argument("dir", help="Diretório contendo os arquivos .md a serem traduzidos")
    parser.add_argument("-t", "--target-dir", help="Diretório de destino dos arquivos traduzidos (opcional)")
    parser.add_argument("--suffix", default=".pt-BR", help="Sufixo para os arquivos traduzidos (padrão: .pt-BR)")
    parser.add_argument("--url", default="http://127.0.0.1:1188", help="URL do servidor DeepLX")
    parser.add_argument("--target-lang", default="PT", help="Idioma de destino (PT ou PT-BR)")
    parser.add_argument("--delay", type=float, default=1.0, help="Intervalo de pausa em segundos entre cada arquivo")
    parser.add_argument("--no-recursive", action="store_true", help="Desativar busca recursiva por subdiretórios")

    args = parser.parse_args()

    batch_translate_directory(
        directory_path=args.dir,
        target_dir=args.target_dir,
        suffix=args.suffix,
        base_url=args.url,
        target_lang=args.target_lang,
        delay_between_files=args.delay,
        recursive=not args.no_recursive
    )

if __name__ == "__main__":
    main()
