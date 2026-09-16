import os
import glob
import urllib.parse
from typing import Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_MODEL

def get_llm(model: Optional[str] = None, temperature: float = 0.2) -> ChatGoogleGenerativeAI:
    """Fábrica de clientes LLM utilizando o modelo configurado centralmente."""
    nome_modelo = model or GEMINI_MODEL
    return ChatGoogleGenerativeAI(
        model=nome_modelo,
        temperature=temperature,
    )

def extrair_texto(resposta: Any) -> str:
    """Extrai texto limpo e unificado de retornos do LangChain/Gemini."""
    if hasattr(resposta, "content"):
        conteudo = resposta.content
    else:
        conteudo = resposta

    if isinstance(conteudo, list):
        textos = []
        for item in conteudo:
            if isinstance(item, dict):
                textos.append(item.get("text", ""))
            elif hasattr(item, "text"):
                textos.append(item.text)
            else:
                textos.append(str(item))
        return "\n".join(textos).strip()
    return str(conteudo).strip()

def gerar_link_busca_linkedin(empresa: str, cargo: str = "Manutenção Elétrica") -> str:
    """Gera link de busca direta de decisores no LinkedIn devidamente codificado."""
    query = f"{cargo.strip()} {empresa.strip()}"
    query_encoded = urllib.parse.quote(query)
    return f"https://www.linkedin.com/search/results/people/?keywords={query_encoded}"

def salvar_markdown_saida(nome_arquivo: str, conteudo: str, pasta: str = "output") -> str:
    """Salva o conteúdo Markdown na pasta de destino de forma segura com encoding UTF-8."""
    os.makedirs(pasta, exist_ok=True)
    caminho_completo = os.path.join(pasta, nome_arquivo)
    with open(caminho_completo, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return caminho_completo

def carregar_acervo_tecnico(pasta_acervo: str = "acervo") -> str:
    """Lê todos os templates e normas da pasta do acervo técnico."""
    if not os.path.exists(pasta_acervo):
        return ""
    
    conteudos = []
    arquivos = sorted(
        glob.glob(os.path.join(pasta_acervo, "*.md")) + 
        glob.glob(os.path.join(pasta_acervo, "*.txt"))
    )
    for caminho in arquivos:
        nome_arquivo = os.path.basename(caminho)
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                texto = f.read().strip()
                if texto:
                    conteudos.append(f"=== REFERÊNCIA DO ACERVO: {nome_arquivo} ===\n{texto}")
        except Exception as e:
            print(f"⚠️ Erro ao ler documento do acervo '{nome_arquivo}': {e}")
            
    return "\n\n".join(conteudos)
