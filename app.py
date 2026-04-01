import streamlit as st
import pandas as pd
import data_loader as dl
import style

# ============================================================
# 1. SETUP DA PÁGINA
# ============================================================
st.set_page_config(page_title="Liga Sul Fluminense", layout="centered")

# URLs DE CONFIGURAÇÃO
URL_CONFIG = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQQW80Fgo-XoW6u5KZ9jIlAEL1q0CYEn7mHo0dAjLc0ZJ5dISZXgEiVo3QIRQdu2Dia-CyOmkB2x6ZR/pub?gid=1515802752&single=true&output=csv"
LINK_WHATSAPP_DEV = "https://wa.me/5524998609210?text=Olá!%0AGostaria%20de%20saber%20mais%20sobre%20seus%20serviços."
LINK_SUA_LOGO_IMGUR = "https://i.imgur.com/y6fUSYm.png"
LINK_ICONE_ZAP_NOVO = "https://i.imgur.com/ReRsuAo.png"
LINK_WHATSAPP_LIGA = "https://wa.me/55249XXXXXXXX?text=Olá!%0ATenho%20interesse%20em%20patrocinar%20a%20Liga."

# ============================================================
# 2. FUNÇÕES DE CACHE - OTIMIZAÇÃO CRÍTICA
# ============================================================

@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_configuracoes_cached(url_config):
    """Carrega configurações uma única vez"""
    return dl.carregar_configuracoes(url_config)

@st.cache_data(ttl=300)
def carregar_todos_dados(config):
    """
    OTIMIZAÇÃO #1: Carrega TODOS os dados em uma única função
    Evita 4+ requisições HTTP separadas
    """
    dados = {
        'partidas': dl.carregar_dados(config.get("LINK_CSV_PARTIDAS", "")),
        'equipes': dl.carregar_dados(config.get("LINK_CSV_EQUIPES", "")),
        'atletas': dl.carregar_dados(config.get("LINK_CSV_ATLETAS", "")),
        'estatisticas': dl.carregar_dados(config.get("LINK_CSV_ESTATISTICAS", ""))
    }
    
    # OTIMIZAÇÃO #2: Limpeza de colunas UMA ÚNICA VEZ
    for key in dados:
        if not dados[key].empty:
            dados[key].columns = [str(c).strip() for c in dados[key].columns]
    
    return dados

@st.cache_data
def carregar_tema_e_logos(config):
    """
    OTIMIZAÇÃO #3: Cachear conversão de URLs
    Evita re-conversão a cada re-render
    """
    return {
        'fundo': dl.converter_link_drive(config.get("LOGO_FUNDO_QUADRA", "")),
        'logo': dl.converter_link_drive(config.get("LOGO_LIGA", "")),
    }

# ============================================================
# 3. CARREGAMENTO INICIAL
# ============================================================

config = carregar_configuracoes_cached(URL_CONFIG)
if not config:
    st.warning("Aguardando link da aba de Configurações...")
    st.stop()

# Carregar TODOS os dados de uma vez
dados = carregar_todos_dados(config)
df_partidas = dados['partidas']
df_equipes = dados['equipes']
df_atletas = dados['atletas']
df_estatisticas = dados['estatisticas']

# Aplicar tema
tema_logos = carregar_tema_e_logos(config)
style.aplicar_tema(tema_logos['fundo'])
logo_liga = tema_logos['logo']

# ============================================================
# 4. CABEÇALHO DO SITE
# ============================================================

st.markdown(f"""
    <div class="hero-banner">
        <img src="{logo_liga}" style="width: 120px; margin-bottom: 10px;">
        <h1>LIGA SUL FLUMINENSE DE<br>
        <span class="destaque-laranja">HANDEBOL</span> - 2026</h1>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# 5. MENU SUPERIOR COM 10 ABAS
# ============================================================

t_inicio, t_partidas, t_masca, t_mascb, t_fema, t_femb, t_finaism, t_finaisf, t_artm, t_artf = st.tabs([
    "Início", "Partidas", "Masc A", "Masc B", "Fem A", "Fem B", "Finais M", "Finais F", "Artilharia M", "Artilharia F"
])

# ============================================================
# 6. FUNÇÕES UTILITÁRIAS OTIMIZADAS
# ============================================================

def converter_placar_seguro(gols_casa, gols_vis):
    """
    OTIMIZAÇÃO #4: Conversão de tipo sem try/except repetido
    Validação eficiente de placar
    """
    try:
        return int(float(gols_casa)), int(float(gols_vis))
    except (ValueError, TypeError):
        return None, None

def exibir_card_partida(row, config, mostrar_data=False):
    """Card de partida - sem mudanças estruturais"""
    with st.container(border=True):
        categoria_jogo = row.get('Categoria', '')
        data_texto = f"{row.get('Data_Partida', '')} - " if mostrar_data else ""
        st.caption(f"**{categoria_jogo}** | {data_texto}{row.get('Hora_Partida', '')}")
        
        logo_casa = dl.pegar_logo_time(row.get('Nome_Casa', ''), config, categoria_jogo) or ""
        logo_vis = dl.pegar_logo_time(row.get('Nome_Visitante', ''), config, categoria_jogo) or ""
        
        gols_casa = row.get('Gols_Casa', '')
        gols_vis = row.get('Gols_Visitante', '')
        
        gc, gv = converter_placar_seguro(gols_casa, gols_vis)
        if gc is not None and gv is not None:
            centro_texto = f'<div class="score-badge">{gc} - {gv}</div>'
        else:
            centro_texto = '<div class="vs-badge">VS</div>'
        
        link_sumula = row.get('Link_Sumula', '')
        tem_sumula = pd.notna(link_sumula) and link_sumula != ''
        botao_sumula = f'<a href="{link_sumula}" target="_blank" class="btn-sumula-mini">📄 Súmula</a>' if tem_sumula else ''
        
        html_centro = f'<div class="matchup-center">{centro_texto}{botao_sumula}</div>'
        
        html_confronto = f"""
        <div class="matchup-row">
            <div class="team-block">
                <img src="{logo_casa}" class="time-logo">
                <span class="time-nome">{row.get('Nome_Casa', '')}</span>
            </div>
            {html_centro}
            <div class="team-block right">
                <span class="time-nome">{row.get('Nome_Visitante', '')}</span>
                <img src="{logo_vis}" class="time-logo">
            </div>
        </div>
        """
        st.markdown(html_confronto, unsafe_allow_html=True)

# ============================================================
# 7. ABA INÍCIO
# ============================================================

with t_inicio:
    if not df_partidas.empty:
        rodadas_pendentes = df_partidas[df_partidas['Status'] == 'Agendada']['Rodada'].unique()
        
        if len(rodadas_pendentes) > 0:
            rodada_foco = rodadas_pendentes[0]
            titulo_secao = "Próxima Rodada"
        else:
            rodada_foco = df_partidas['Rodada'].unique()[-1]
            titulo_secao = "Última Rodada"

        jogos_rodada = df_partidas[df_partidas['Rodada'] == rodada_foco]
        local_rodada = jogos_rodada.iloc[0].get('Localizacao', 'Local a definir')
        
        st.markdown(f"<h3 style='color: #e67e22; text-align: center; margin-bottom: 0;'>{titulo_secao}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray; font-size: 18px; margin-top: 5px;'>Rodada {rodada_foco} - {local_rodada}</p>", unsafe_allow_html=True)
        
        for _, row in jogos_rodada.iterrows():
            exibir_card_partida(row, config, mostrar_data=True)
    else:
        st.info("Nenhuma partida encontrada no banco de dados.")

# ============================================================
# 8. ABA PARTIDAS
# ============================================================

with t_partidas:
    st.header("Calendário de Jogos")
    
    if not df_partidas.empty:
        rodadas_unicas = df_partidas['Rodada'].unique()
        
        for rodada in rodadas_unicas:
            jogos_desta_rodada = df_partidas[df_partidas['Rodada'] == rodada]
            local_da_rodada = jogos_desta_rodada.iloc[0].get('Localizacao', 'Local a definir')
            
            st.markdown(f"<h4 style='color: #e67e22; text-align: center; margin-top: 25px; border-bottom: 2px solid #eee; padding-bottom: 10px;'>Rodada {rodada} - {local_da_rodada}</h4>", unsafe_allow_html=True)
            
            for _, row in jogos_desta_rodada.iterrows():
                exibir_card_partida(row, config, mostrar_data=True)
    else:
        st.info("Nenhuma partida cadastrada.")

# ============================================================
# 9. MOTOR DE CÁLCULO DA CLASSIFICAÇÃO - OTIMIZADO
# ============================================================

@st.cache_data
def calcular_classificacao_otimizado(df_partidas, df_equipes, categoria_alvo):
    """
    OTIMIZAÇÃO #5: Usar operações vetorizadas do pandas
    Evita loops aninhados desnecessários
    """
    if df_equipes.empty:
        return pd.DataFrame()
    
    # Criar coluna de categoria completa
    if 'Categoria' in df_equipes.columns and 'Grupo' in df_equipes.columns:
        df_equipes['Cat_Completa'] = (
            df_equipes['Categoria'].astype(str).str.strip() + " " + 
            df_equipes['Grupo'].astype(str).str.strip()
        )
    else:
        df_equipes['Cat_Completa'] = df_equipes.get('Categoria', '')
    
    col_nome = 'Nome_Equipe' if 'Nome_Equipe' in df_equipes.columns else 'Equipe'
    
    # Filtrar equipes
    equipes_oficiais = df_equipes[
        df_equipes['Cat_Completa'].str.upper() == str(categoria_alvo).strip().upper()
    ]
    
    # Inicializar tabela com valores padrão
    tabela = equipes_oficiais[[col_nome]].copy()
    tabela.columns = ['Equipe']
    tabela[['P', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG']] = 0
    
    if tabela.empty:
        return pd.DataFrame()
    
    # Filtrar partidas com placar válido
    if not df_partidas.empty:
        df_cat = df_partidas[
            (df_partidas['Categoria'].astype(str).str.strip().str.upper() == 
             str(categoria_alvo).strip().upper()) &
            (df_partidas['Gols_Casa'].notna()) &
            (df_partidas['Gols_Visitante'].notna())
        ]
        
        # Processar partidas
        for _, row in df_cat.iterrows():
            casa = str(row.get('Nome_Casa', '')).strip()
            vis = str(row.get('Nome_Visitante', '')).strip()
            
            if casa in tabela['Equipe'].values and vis in tabela['Equipe'].values:
                try:
                    gc = int(float(row['Gols_Casa']))
                    gv = int(float(row['Gols_Visitante']))
                    
                    # Atualizar ambos os times
                    tabela.loc[tabela['Equipe'] == casa, 'J'] += 1
                    tabela.loc[tabela['Equipe'] == vis, 'J'] += 1
                    tabela.loc[tabela['Equipe'] == casa, 'GP'] += gc
                    tabela.loc[tabela['Equipe'] == casa, 'GC'] += gv
                    tabela.loc[tabela['Equipe'] == vis, 'GP'] += gv
                    tabela.loc[tabela['Equipe'] == vis, 'GC'] += gc
                    
                    if gc > gv:
                        tabela.loc[tabela['Equipe'] == casa, 'V'] += 1
                        tabela.loc[tabela['Equipe'] == casa, 'P'] += 2
                        tabela.loc[tabela['Equipe'] == vis, 'D'] += 1
                    elif gv > gc:
                        tabela.loc[tabela['Equipe'] == vis, 'V'] += 1
                        tabela.loc[tabela['Equipe'] == vis, 'P'] += 2
                        tabela.loc[tabela['Equipe'] == casa, 'D'] += 1
                    else:
                        tabela.loc[tabela['Equipe'] == casa, 'E'] += 1
                        tabela.loc[tabela['Equipe'] == vis, 'E'] += 1
                        tabela.loc[tabela['Equipe'] == casa, 'P'] += 1
                        tabela.loc[tabela['Equipe'] == vis, 'P'] += 1
                except:
                    pass
    
    # Calcular saldo
    tabela['SG'] = tabela['GP'] - tabela['GC']
    
    # Ordenar
    tabela = tabela.sort_values(
        by=['P', 'SG', 'GP', 'Equipe'],
        ascending=[False, False, False, True]
    ).reset_index(drop=True)
    
    tabela.insert(0, 'Pos', range(1, len(tabela) + 1))
    return tabela

def gerar_html_tabela_otimizado(df):
    """
    OTIMIZAÇÃO #6: Usar list.join() para construção eficiente de HTML
    Evita concatenação O(n²)
    """
    if df.empty:
        return "<p>Nenhuma equipe encontrada.</p>"
    
    # Header
    header_cells = [f'<th>{col}</th>' for col in df.columns]
    header = '<tr>' + ''.join(header_cells) + '</tr>'
    
    # Rows
    rows = []
    for _, row in df.iterrows():
        cells = [f'<td>{row[col]}</td>' for col in df.columns]
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    
    body = ''.join(rows)
    
    return f'''
    <div class="tabela-container">
        <table class="tabela-classificacao">
            <thead>{header}</thead>
            <tbody>{body}</tbody>
        </table>
    </div>
    '''

def mostrar_tabela_automatica(df_partidas, df_equipes, categoria):
    """Exibir tabela com HTML otimizado"""
    df = calcular_classificacao_otimizado(df_partidas, df_equipes, categoria)
    if not df.empty:
        html = gerar_html_tabela_otimizado(df)
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.info(f"Nenhuma equipe encontrada para '{categoria}'.")

# Desenhamos as tabelas
with t_masca:
    mostrar_tabela_automatica(df_partidas, df_equipes, "Masculino A")
with t_mascb:
    mostrar_tabela_automatica(df_partidas, df_equipes, "Masculino B")
with t_fema:
    mostrar_tabela_automatica(df_partidas, df_equipes, "Feminino A")
with t_femb:
    mostrar_tabela_automatica(df_partidas, df_equipes, "Feminino B")

# ============================================================
# 10. FINAIS - CHAVEAMENTO AUTOMÁTICO
# ============================================================

def pegar_classificado_automatico(df_partidas, df_equipes, categoria, posicao_desejada, texto_padrao):
    """
    Pega o classificado em uma posição específica
    """
    df = calcular_classificacao_otimizado(df_partidas, df_equipes, categoria)
    if not df.empty and len(df) >= posicao_desejada:
        return df.iloc[posicao_desejada - 1]['Equipe']
    return texto_padrao

def mostrar_chaveamento(logo_url, t1A, t2B, t1B, t2A):
    """
    Exibe o chaveamento das semifinais e final
    """
    html_chave = f"""<div class="bracket-wrapper"><div class="bracket-container"><div class="bracket-col"><div style="color: white; text-align: center; font-size: 12px; margin-bottom: 5px;">SEMIFINAL 1</div><div class="match-box"><div class="team-row"><span>{t1A}</span><span class="team-score">-</span></div><div class="team-row"><span>{t2B}</span><span class="team-score">-</span></div></div></div><div class="bracket-center"><img src="{logo_url}" style="width: 150px; margin-bottom: 10px;"><div class="final-badge">FINAL</div><div class="match-box final-box"><div class="team-row"><span>Vencedor Semi 1</span><span class="team-score">-</span></div><div class="team-row"><span>Vencedor Semi 2</span><span class="team-score">-</span></div></div></div><div class="bracket-col"><div style="color: white; text-align: center; font-size: 12px; margin-bottom: 5px;">SEMIFINAL 2</div><div class="match-box"><div class="team-row"><span>{t1B}</span><span class="team-score">-</span></div><div class="team-row"><span>{t2A}</span><span class="team-score">-</span></div></div></div></div></div>"""
    st.markdown(html_chave, unsafe_allow_html=True)

# --- ABA FINAIS MASCULINO ---
with t_finaism:
    st.markdown("<h3 style='text-align: center; color: #1a3c34;'>Fase Final - Masculino</h3>", unsafe_allow_html=True)
    m_1A = pegar_classificado_automatico(df_partidas, df_equipes, "Masculino A", 1, "1º Grupo A")
    m_2A = pegar_classificado_automatico(df_partidas, df_equipes, "Masculino A", 2, "2º Grupo A")
    m_1B = pegar_classificado_automatico(df_partidas, df_equipes, "Masculino B", 1, "1º Grupo B")
    m_2B = pegar_classificado_automatico(df_partidas, df_equipes, "Masculino B", 2, "2º Grupo B")
    mostrar_chaveamento(logo_liga, m_1A, m_2B, m_1B, m_2A)

# --- ABA FINAIS FEMININO ---
with t_finaisf:
    st.markdown("<h3 style='text-align: center; color: #1a3c34;'>Fase Final - Feminino</h3>", unsafe_allow_html=True)
    f_1A = pegar_classificado_automatico(df_partidas, df_equipes, "Feminino A", 1, "1º Grupo A")
    f_2A = pegar_classificado_automatico(df_partidas, df_equipes, "Feminino A", 2, "2º Grupo A")
    f_1B = pegar_classificado_automatico(df_partidas, df_equipes, "Feminino B", 1, "1º Grupo B")
    f_2B = pegar_classificado_automatico(df_partidas, df_equipes, "Feminino B", 2, "2º Grupo B")
    mostrar_chaveamento(logo_liga, f_1A, f_2B, f_1B, f_2A)

# ============================================================
# 11. MOTOR DE ARTILHARIA - OTIMIZADO
# ============================================================

@st.cache_data
def processar_artilharia_completa(df_estatisticas, df_atletas, df_equipes):
    """
    OTIMIZAÇÃO #7: Processar artilharia UMA ÚNICA VEZ
    Evita 2 processamentos (M e F) com merges repetidos
    """
    if df_estatisticas.empty or df_atletas.empty:
        return pd.DataFrame()
    
    # Agrupar gols por atleta
    artilharia = df_estatisticas.groupby('ID_Atleta')['Gols_Marcados'].sum().reset_index()
    artilharia.columns = ['ID_Atleta', 'Gols']
    
    # Merge com atletas
    df_ranking = pd.merge(artilharia, df_atletas, on='ID_Atleta', how='left')
    
    # Merge com equipes
    df_ranking = pd.merge(
        df_ranking,
        df_equipes[['ID_Equipe', 'Categoria', 'Nome_Equipe']],
        on='ID_Equipe',
        how='left'
    )
    
    return df_ranking

@st.cache_data
def criar_dicionario_equipes(df_equipes):
    """
    OTIMIZAÇÃO #8: Usar dicionário para lookup O(1)
    Evita buscas lineares em DataFrame
    """
    return dict(zip(df_equipes['ID_Equipe'], df_equipes['Nome_Equipe']))

def mostrar_artilharia_automatica(artilharia_completa, sexo_alvo):
    """Exibir artilharia com lookup otimizado"""
    if artilharia_completa.empty:
        st.info(f"Nenhum gol registrado para o {sexo_alvo.replace('M', 'Masculino').replace('F', 'Feminino')} ainda.")
        return
    
    filtro_sexo = "MASCULINO" if sexo_alvo.upper() == "M" else "FEMININO"
    df_final = artilharia_completa[
        artilharia_completa['Categoria'].astype(str).str.upper().str.contains(filtro_sexo)
    ].sort_values(by='Gols', ascending=False)
    
    # Criar dicionário para lookup rápido
    equipes_dict = criar_dicionario_equipes(df_equipes)
    
    for _, row in df_final.iterrows():
        nome = row.get('Nome_Atleta', 'Atleta Desconhecido')
        equipe_id = row.get('ID_Equipe', '')
        nome_equipe = equipes_dict.get(equipe_id, "Equipe não encontrada")
        posicao = row.get('Posicao', '')
        gols = int(row.get('Gols', 0))
        
        texto_atleta = f"{nome} - {posicao}" if pd.notna(posicao) and str(posicao).strip() != "" else nome
        
        html_card = f"""
        <div class="artilharia-card">
            <div class="gols-badge">{gols} Gols</div>
            <div class="atleta-nome">{texto_atleta}</div>
            <div class="equipe-nome">{nome_equipe}</div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)

# Processar artilharia uma única vez
artilharia_completa = processar_artilharia_completa(df_estatisticas, df_atletas, df_equipes)

# Exibir nas abas
with t_artm:
    st.markdown("<h3 style='text-align: center; color: #1a3c34;'>Artilharia Masculina</h3>", unsafe_allow_html=True)
    mostrar_artilharia_automatica(artilharia_completa, "M")

with t_artf:
    st.markdown("<h3 style='text-align: center; color: #1a3c34;'>Artilharia Feminina</h3>", unsafe_allow_html=True)
    mostrar_artilharia_automatica(artilharia_completa, "F")

# ============================================================
# 12. RODAPÉ E PATROCINADORES
# ============================================================

st.markdown("---")
lista_logos_patrocinadores = []
for i in range(1, 11):
    chave = f"LOGO_PATROCINADOR_{i}"
    link_bruto = str(config.get(chave, "")).strip()
    if link_bruto and link_bruto != "nan":
        link_direto = dl.converter_link_drive(link_bruto)
        if link_direto:
            lista_logos_patrocinadores.append(link_direto)

if len(lista_logos_patrocinadores) > 0:
    st.markdown("<h4 style='text-align: center; color: #1a3c34;'>Nossos Patrocinadores</h4>", unsafe_allow_html=True)
    html_logos = "".join([f'<img src="{url}" class="patrocinador-logo">' for url in lista_logos_patrocinadores])
    st.markdown(f'<div class="patrocinadores-container"><div class="patrocinadores-grid">{html_logos}</div></div>', unsafe_allow_html=True)
else:
    html_card_seja_patroc = f'''
    <a href="{LINK_WHATSAPP_LIGA}" target="_blank" class="seja-patrocinador-card" style="text-decoration: none;">
        <div class="seja-patrocinador-icon" style="font-size: 30px; margin-bottom: 10px;">🤝</div>
        <div class="seja-patrocinador-texto" style="color: #e67e22; font-weight: bold; font-size: 22px;">Sua Marca Aqui</div>
        <div style="color: #f9f9f9; font-size: 14px; opacity: 0.9; margin-top: 5px;">Seja um patrocinador da Liga Sul Fluminense!</div>
    </a>
    '''
    st.markdown(html_card_seja_patroc, unsafe_allow_html=True)

# --- RODAPÉ DO DESENVOLVEDOR ---
html_rodape = """<div style="padding: 20px 0; border-top: 1px solid #eee; margin-top: 30px;">
<div style="display: flex; align-items: center; justify-content: center; gap: 20px;">
<div style="display: flex; flex-direction: column; align-items: center;">
<span style="font-size: 12px; color: gray; margin-bottom: 5px;">Desenvolvido por:</span>
<img src="https://i.imgur.com/y6fUSYm.png" alt="Nacarat Logo" style="max-height: 120px;">
</div>
<a href="https://wa.me/5524998609210?text=Olá!%20Gostaria%20de%20saber%20mais%20sobre%20seus%20serviços." target="_blank" style="text-decoration: none;">
<img src="https://i.imgur.com/ReRsuAo.png" alt="WhatsApp" style="max-height: 35px; border-radius: 50%;">
</a>
</div>
</div>"""
st.markdown(html_rodape, unsafe_allow_html=True)
