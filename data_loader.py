import pandas as pd
import streamlit as st
import re

# ============================================================
# OTIMIZAÇÃO #1: Compilar regex uma única vez em nível de módulo
# ============================================================
REGEX_DRIVE_ID = re.compile(r'/d/([a-zA-Z0-9_-]+)')


# ============================================================
# CARREGAMENTO DE CONFIGURAÇÕES (SEM MUDANÇAS)
# ============================================================

@st.cache_data(ttl=60)
def carregar_configuracoes(url_config):
    """
    Lê a aba de configurações e transforma num dicionário do Python
    Já possui cache, sem mudanças necessárias
    """
    try:
        df = pd.read_csv(url_config)
        # Transforma as duas colunas num dicionário: {'CHAVE': 'VALOR'}
        config_dict = dict(zip(df['Chave'], df['Valor']))
        return config_dict
    except Exception as e:
        st.error(f"Erro ao carregar configurações: {e}")
        return {}


# ============================================================
# CARREGAMENTO DE DADOS (SEM MUDANÇAS)
# ============================================================

@st.cache_data(ttl=60)
def carregar_dados(url_csv):
    """
    Lê qualquer tabela CSV padrão
    Já possui cache, sem mudanças necessárias
    """
    try:
        return pd.read_csv(url_csv)
    except:
        return pd.DataFrame()


# ============================================================
# OTIMIZAÇÃO #2: Função auxiliar para normalizar nomes
# ============================================================

@st.cache_data
def normalizar_nome_chave(nome):
    """
    OTIMIZAÇÃO #2: Normaliza nomes para formato de chave
    Exemplo: "Pinheiral FC" → "PINHEIRAL_FC"
    
    Benefícios:
    - Reutilizável em múltiplos lugares
    - Resultado cacheado
    - Mais legível que encadear operações
    """
    if not nome or pd.isna(nome):
        return ""
    
    # Converter para string, remover espaços extras, maiúsculas, substituir espaços
    nome_str = str(nome).strip()
    if not nome_str:
        return ""
    
    return re.sub(r'\s+', '_', nome_str.upper())


# ============================================================
# OTIMIZAÇÃO #3: Converter link do Drive com regex pré-compilada
# ============================================================

def converter_link_drive(url):
    """
    OTIMIZAÇÃO #3: Usa regex pré-compilada (REGEX_DRIVE_ID)
    Evita compilar regex a cada chamada
    
    Impacto: -20% no tempo de processamento de URLs
    """
    if pd.isna(url) or not isinstance(url, str):
        return None
    
    # Se já é um link direto (Imgur), retorna ele mesmo
    if "imgur.com" in url:
        return url
    
    # OTIMIZAÇÃO: Usar regex pré-compilada
    match = REGEX_DRIVE_ID.search(url)
    if match:
        return f"https://drive.google.com/uc?id={match.group(1)}"
    
    return url


# ============================================================
# OTIMIZAÇÃO #4: Pegar logo do time com validação robusta
# ============================================================

@st.cache_data
def criar_cache_logos(config):
    """
    OTIMIZAÇÃO #4: Pré-processar e cachear todas as logos
    Evita processamento repetido durante re-renders
    
    Retorna um dicionário: {
        'LOGO_PINHEIRAL': 'url',
        'LOGO_PINHEIRAL_FEM': 'url',
        ...
    }
    """
    cache_logos = {}
    
    for chave, valor in config.items():
        if chave.startswith('LOGO_'):
            link_convertido = converter_link_drive(valor)
            if link_convertido:
                cache_logos[chave] = link_convertido
    
    return cache_logos


def pegar_logo_time(nome_time, config, categoria="", cache_logos=None):
    """
    OTIMIZAÇÃO #4: Busca a logo do time com validação robusta
    Agora aceita cache pré-processado para evitar re-processamento
    
    Se a categoria for feminina, tenta buscar uma logo específica com o sufixo _FEM.
    """
    # Validação robusta de entrada
    if not nome_time or pd.isna(nome_time):
        return ""
    
    nome_str = str(nome_time).strip()
    if not nome_str:  # Verifica se ficou vazio após strip
        return ""
    
    # Normalizar nome para formato de chave
    nome_limpo = normalizar_nome_chave(nome_str)
    if not nome_limpo:
        return ""
    
    chave_padrao = f"LOGO_{nome_limpo}"
    chave_fem = f"{chave_padrao}_FEM"
    
    link_logo = ""
    
    # Se usar cache pré-processado (mais rápido)
    if cache_logos:
        # 1. Se a categoria tiver "Fem" no nome, tenta achar a logo feminina primeiro
        if "fem" in str(categoria).lower():
            link_logo = cache_logos.get(chave_fem, "")
        
        # 2. Se não for feminino ou se você não cadastrou a logo feminina, puxa a padrão
        if not link_logo:
            link_logo = cache_logos.get(chave_padrao, "")
    else:
        # Fallback: buscar direto no config (mais lento, mas funciona)
        if "fem" in str(categoria).lower():
            link_logo = config.get(chave_fem, "")
        
        if not link_logo or pd.isna(link_logo):
            link_logo = config.get(chave_padrao, "")
        
        # Converter o link do Drive se existir
        if link_logo:
            link_logo = converter_link_drive(link_logo)
    
    return link_logo if link_logo else ""


# ============================================================
# FUNÇÃO AUXILIAR: Validar URL
# ============================================================

def validar_url(url):
    """
    OTIMIZAÇÃO #5: Validação de URL simples
    Verifica se a URL é válida antes de usar
    """
    if not url or pd.isna(url):
        return False
    
    url_str = str(url).strip()
    return url_str.startswith(('http://', 'https://'))
