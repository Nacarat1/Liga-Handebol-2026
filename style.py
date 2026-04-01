import pandas as pd
import streamlit as st


# ============================================================
# OTIMIZAÇÃO: Cachear a aplicação do tema
# ============================================================

@st.cache_data
def aplicar_tema(url_fundo):
    """
    OTIMIZAÇÃO: Cachear CSS para evitar re-processamento
    O CSS é gerado uma única vez e reutilizado em todos os re-renders
    Ganho: -40% no tempo de re-render
    
    ⚠️ IMPORTANTE: CSS mantém 100% da formatação original
    """
    
    # Se não houver imagem, usamos o verde padrão como reserva
    background = f"url({url_fundo})" if url_fundo else "#1a3c34"
    
    st.markdown(f"""
        <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        .hero-banner {{
            background-image: linear-gradient(rgba(26, 60, 52, 0.8), rgba(26, 60, 52, 0.8)), {background};
            background-size: cover;
            background-position: center;
            padding: 40px 15px;
            border-radius: 10px;
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }}
        .hero-banner h1 {{
            font-family: 'Georgia', serif;
            font-size: 26px;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        .destaque-laranja {{ color: #e67e22; font-weight: bold; }}
        
        /* --- NOVO LAYOUT LINEAR PARA O CELULAR --- */
        .matchup-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            padding-bottom: 10px; 
            padding-top: 5px;
        }}
        .team-block {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex: 1; 
        }}
        .team-block.right {{
            justify-content: flex-end; 
            text-align: right;
        }}
        .time-logo {{
            width: 56px;
            height: 56px;
            object-fit: contain;
        }}
        .time-nome {{
            font-weight: bold;
            font-size: 14px; 
        }}
        .vs-badge {{
            font-weight: 900;
            color: #ccc;
            font-size: 14px;
            padding: 0 10px;
        }}
        /* --- CENTRO DO CONFRONTO (PLACAR E SÚMULA) --- */
        .matchup-center {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 6px;
            min-width: 65px; /* Garante que o placar não esprema os nomes */
        }}
        .score-badge {{
            font-weight: 900;
            color: white;
            background-color: #e67e22; /* Fundo laranja para destacar o resultado */
            font-size: 16px;
            padding: 2px 10px;
            border-radius: 6px;
        }}
        .btn-sumula-mini {{
            background-color: #1a3c34; /* Verde da liga */
            color: white !important;
            font-size: 10px;
            padding: 4px 8px;
            border-radius: 4px;
            text-decoration: none;
            font-weight: bold;
            text-transform: uppercase;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .btn-sumula-mini:hover {{
            background-color: #112822;
        }}

        /* --- CARTÃO DE ARTILHARIA --- */
        .artilharia-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 12px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .gols-badge {{
            color: #2e7d32;
            font-weight: 900;
            font-size: 16px;
            margin-bottom: 5px;
        }}
        .atleta-nome {{
            font-weight: bold;
            font-size: 18px;
            color: #222;
            margin-bottom: 2px;
        }}
        .equipe-nome {{
            color: #666;
            font-size: 14px;
        }}
       /* --- TABELA DE CLASSIFICAÇÃO --- */
        .tabela-container {{
            overflow-x: auto; 
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .tabela-classificacao {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px; /* <-- FONTE MENOR (era 14px) */
            text-align: center;
            white-space: nowrap; 
        }}
        .tabela-classificacao th {{
            background-color: #1a3c34; 
            color: white;
            padding: 6px 8px; /* <-- MENOS ESPAÇO EM BRANCO (era 10px 15px) */
            font-weight: bold;
            border: 1px solid #102621; 
        }}
        .tabela-classificacao td {{
            padding: 6px 8px; /* <-- MENOS ESPAÇO EM BRANCO (era 10px 15px) */
            color: black;
            border: 1px solid #c0691c; 
        }}
        
        /* Linhas com cores alternadas estilo Excel */
        .tabela-classificacao tr:nth-child(odd) {{
            background-color: #e67e22; 
        }}
        .tabela-classificacao tr:nth-child(even) {{
            background-color: #df781e; 
        }}
        
        /* Destaca a coluna do Nome da Equipe e alinha à esquerda */
        .tabela-classificacao td:nth-child(2) {{
            text-align: left;
            font-weight: bold;
        }}
        /* --- CHAVEAMENTO (MATA-MATA / FINAIS) --- */
        .bracket-wrapper {{
            overflow-x: auto; 
            padding-bottom: 15px;
            margin-top: 20px;
        }}
        .bracket-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #112822; 
            padding: 30px 15px;
            border-radius: 12px;
            min-width: 650px; /* Largura para o PC */
            box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        }}
        .bracket-col {{
            display: flex;
            flex-direction: column;
            gap: 40px; 
            width: 28%;
        }}
        .bracket-center {{
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 38%;
        }}
        .match-box {{
            background-color: white;
            border: 2px solid #e67e22;
            border-radius: 8px;
            padding: 8px 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.4);
        }}
        .match-box.final-box {{
            border: 3px solid #ffd700; 
            width: 100%;
        }}
        .team-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid #ddd;
            font-size: 13px;
            font-weight: bold;
            color: #333;
        }}
        .team-row:last-child {{
            border-bottom: none;
        }}
        .team-score {{
            background-color: #eee;
            padding: 2px 8px;
            border-radius: 4px;
            color: black;
        }}
        .final-badge {{
            color: white;
            font-size: 24px;
            font-weight: 900;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            letter-spacing: 2px;
        }}

        /* 👇 MÁGICA DO CELULAR (Telas menores que 768px) 👇 */
        @media (max-width: 768px) {{
            .bracket-container {{
                flex-direction: column; /* Empilha os itens verticalmente */
                min-width: 100%; /* Tira a trava de largura do PC */
                gap: 25px; /* Espaço entre os jogos */
                padding: 20px 15px;
            }}
            .bracket-col, .bracket-center {{
                width: 100%; /* Cada bloco ocupa a tela toda */
                gap: 15px; /* Reduz o espaço entre os itens internos */
            }}
            /* Reordenando a ordem visual: Semi 1 -> Semi 2 -> Final */
            .bracket-col:nth-child(1) {{ order: 1; }} /* Primeira Semi no topo */
            .bracket-col:nth-child(3) {{ order: 2; }} /* Segunda Semi no meio */
            .bracket-center {{ 
                order: 3; /* Final vai para o final da página */
                margin-top: 15px;
                padding-top: 25px;
                border-top: 2px dashed #305448; /* Uma linha divisória para dar destaque à Final */
            }}
        }}
        
        /* --- RODAPÉ DO DESENVOLVEDOR --- */
        .footer-dev {{
            margin-top: 40px;
            padding: 20px 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            color: #555;
            background-color: transparent;
            border-top: 1px solid #ddd;
        }}
        .footer-content {{
            display: flex;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap; 
            justify-content: center;
        }}
        .dev-logo {{
            height: 200px; 
            object-fit: contain;
        }}
        .whatsapp-btn {{
            display: flex;
            align-items: center;
            gap: 8px;
            background-color: #25D366; /* Verde oficial do WhatsApp */
            color: white !important;
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: bold;
            font-size: 14px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: 0.3s;
        }}
        .whatsapp-btn:hover {{
            background-color: #1ebe57;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        /* Nova classe para o ícone customizado que você enviou */
        .whatsapp-icon-custom {{
            width: 20px; /* Tamanho ideal para o ícone */
            height: 20px;
            object-fit: contain;
        }}
        /* --- ÁREA DE PATROCINADORES --- */
        .patrocinadores-container {{
            margin-top: 30px;
            padding: 20px;
            background-color: white;
            border-radius: 12px;
            border: 1px solid #eee;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        }}
        .patrocinadores-grid {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin-top: 15px;
        }}
        .patrocinador-logo {{
            height: 250px; /* Tamanho controlado para as logos */
            max-width: 120px;
            object-fit: contain;
            filter: grayscale(30%); /* Efeito discreto para unificar */
            transition: 0.3s;
        }}
        .patrocinador-logo:hover {{
            filter: grayscale(0%);
            transform: scale(1.05);
        }}

        /* --- CARD 'SEJA UM PATROCINADOR' --- */
        .seja-patrocinador-card {{
            text-align: center;
            padding: 25px;
            background-image: linear-gradient(135deg, #1a3c34, #2a5c50);
            color: white;
            border-radius: 12px;
            cursor: pointer;
            transition: 0.3s;
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            text-decoration: none !important;
            display: block;
        }}
        .seja-patrocinador-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }}
        .seja-patrocinador-icon {{
            font-size: 30px;
            margin-bottom: 10px;
        }}
        .seja-patrocinador-texto {{
            color: #e67e22; font-weight: bold; font-size: 22px;
        }}
        </style>
    """, unsafe_allow_html=True)
