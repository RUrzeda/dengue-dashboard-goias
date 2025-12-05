"""
Dashboard de Monitoramento de Dengue em Goiás - Versão Simplificada

Este dashboard fornece visualizações interativas de dados epidemiológicos
de dengue em Goiás usando dados da API InfoDengue/Mosqlimate.

Autor: Manus AI
Data: Dezembro 2024
Licença: MIT
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import logging
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

st.set_page_config(
    page_title="Dashboard Dengue Goiás",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# APIs
INFODENGUE_API = "https://info.dengue.mat.br/api/alertcity"

# Municípios de Goiás (amostra)
GOIAS_MUNICIPALITIES = {
    5103403: "Goiânia",
    5104402: "Anápolis",
    5103809: "Aparecida de Goiânia",
    5104304: "Abadia de Goiás",
    5104700: "Aragarças",
    5105002: "Arenópolis",
    5105101: "Argolândia",
    5105408: "Aurilândia",
    5105507: "Avelinópolis",
    5105606: "Baliza",
    5105705: "Bom Jardim de Goiás",
    5105804: "Britânia",
    5106001: "Buriti Alegre",
    5106100: "Cachoeira de Goiás",
    5106209: "Caçu",
    5106308: "Caiapônia",
    5106407: "Caldas Novas",
    5106506: "Caldazinha",
    5106605: "Campestre de Goiás",
    5106704: "Campinaçu",
}

# ============================================================================
# FUNÇÕES DE BUSCA DE DADOS
# ============================================================================

@st.cache_data(ttl=3600)
def fetch_infodengue_data(geocode: str, disease: str = "dengue"):
    """
    Busca dados epidemiológicos via API InfoDengue.
    
    Args:
        geocode: Código IBGE do município
        disease: Tipo de doença (dengue, zika, chikungunya)
    
    Returns:
        DataFrame com dados
    """
    
    try:
        params = {
            "geocode": geocode,
            "disease": disease,
            "format": "json"
        }
        
        response = requests.get(INFODENGUE_API, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            return pd.DataFrame()
        
        # Converter colunas de data
        for col in ['data_iniSE', 'data_ini_SE', 'data']:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass
        
        return df
    
    except Exception as e:
        logger.error(f"Erro ao buscar dados para {geocode}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_all_municipalities_data(disease: str = "dengue"):
    """
    Busca dados de todos os municípios.
    
    Args:
        disease: Tipo de doença
    
    Returns:
        DataFrame consolidado
    """
    
    all_data = []
    
    for geocode, municipality_name in GOIAS_MUNICIPALITIES.items():
        df = fetch_infodengue_data(str(geocode), disease)
        if not df.empty:
            df['municipio_nome'] = municipality_name
            df['municipio_geocodigo'] = geocode
            all_data.append(df)
    
    if not all_data:
        return pd.DataFrame()
    
    return pd.concat(all_data, ignore_index=True)

# ============================================================================
# FUNÇÕES DE VISUALIZAÇÃO
# ============================================================================

def create_time_series_chart(df: pd.DataFrame, title: str = "Evolução de Casos"):
    """Cria gráfico de série temporal."""
    
    if df.empty:
        return None
    
    try:
        # Identificar coluna de data
        date_col = None
        for col in ['data_iniSE', 'data_ini_SE', 'data']:
            if col in df.columns:
                date_col = col
                break
        
        if date_col is None:
            return None
        
        # Preparar dados
        agg_dict = {}
        if 'casos_est' in df.columns:
            agg_dict['casos_est'] = 'sum'
        if 'casos' in df.columns:
            agg_dict['casos'] = 'sum'
        
        if not agg_dict:
            return None
        
        df_agg = df.groupby(date_col).agg(agg_dict).reset_index()
        
        # Criar gráfico
        y_cols = [col for col in ['casos_est', 'casos'] if col in df_agg.columns]
        
        fig = px.line(
            df_agg,
            x=date_col,
            y=y_cols,
            title=title,
            labels={'casos_est': 'Casos Estimados', 'casos': 'Casos Notificados'},
            markers=True
        )
        
        fig.update_layout(height=400, hovermode='x unified')
        
        return fig
    
    except Exception as e:
        logger.error(f"Erro ao criar série temporal: {e}")
        return None


def create_alert_distribution(df: pd.DataFrame):
    """Cria gráfico de distribuição de alertas."""
    
    if df.empty or 'nivel' not in df.columns:
        return None
    
    try:
        # Usar registro mais recente por município
        date_col = 'data_iniSE' if 'data_iniSE' in df.columns else 'data_ini_SE'
        geocode_col = 'municipio_geocodigo' if 'municipio_geocodigo' in df.columns else 'geocode'
        
        if geocode_col in df.columns:
            df_latest = df.sort_values(date_col).groupby(geocode_col).tail(1)
        else:
            df_latest = df.sort_values(date_col).tail(len(df.drop_duplicates(subset=['municipio_nome'])))
        
        nivel_counts = df_latest['nivel'].value_counts().sort_index()
        
        nivel_names = {1: "Verde", 2: "Amarelo", 3: "Laranja", 4: "Vermelho"}
        nivel_colors = {1: "#2ecc71", 2: "#f39c12", 3: "#e67e22", 4: "#e74c3c"}
        
        labels = [nivel_names.get(i, f"Nível {i}") for i in nivel_counts.index]
        colors = [nivel_colors.get(i, "#95a5a6") for i in nivel_counts.index]
        
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=nivel_counts.values,
                marker_color=colors,
                text=nivel_counts.values,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Distribuição de Municípios por Nível de Alerta",
            xaxis_title="Nível de Alerta",
            yaxis_title="Número de Municípios",
            height=400,
            template='plotly_white'
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Erro ao criar distribuição de alertas: {e}")
        return None


def create_municipalities_table(df: pd.DataFrame):
    """Cria tabela com dados de municípios."""
    
    if df.empty:
        return None
    
    try:
        date_col = 'data_iniSE' if 'data_iniSE' in df.columns else 'data_ini_SE'
        geocode_col = 'municipio_geocodigo' if 'municipio_geocodigo' in df.columns else 'geocode'
        
        if geocode_col in df.columns:
            df_latest = df.sort_values(date_col).groupby(geocode_col).tail(1)
        else:
            df_latest = df.sort_values(date_col).tail(len(df.drop_duplicates(subset=['municipio_nome'])))
        
        # Selecionar colunas para exibição
        cols_to_show = [
            'municipio_nome', 'casos_est', 'casos', 'p_inc100k', 'Rt', 'nivel'
        ]
        
        df_display = df_latest[[col for col in cols_to_show if col in df_latest.columns]].copy()
        
        # Renomear colunas
        df_display.columns = [
            'Município',
            'Casos Estimados',
            'Casos Notificados',
            'Taxa de Incidência',
            'Rt',
            'Nível'
        ]
        
        return df_display
    
    except Exception as e:
        logger.error(f"Erro ao criar tabela: {e}")
        return None

# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================

def main():
    """Função principal do dashboard."""
    
    # Header
    st.markdown("# 🦟 Dashboard de Monitoramento de Dengue em Goiás")
    st.markdown("""
    Sistema de vigilância epidemiológica integrado com dados em tempo real da API InfoDengue.
    Dados atualizados semanalmente com modelos de nowcasting para estimativas mais precisas.
    """)
    
    # Sidebar
    st.sidebar.markdown("## ⚙️ Configurações")
    
    disease = st.sidebar.selectbox(
        "Selecione a Arbovirose:",
        options=["dengue", "zika", "chikungunya"],
        index=0
    )
    
    view_type = st.sidebar.radio(
        "Tipo de Visualização:",
        options=["Estadual", "Por Município"],
        index=0
    )
    
    # Buscar dados
    st.sidebar.info("⏳ Carregando dados...")
    
    df_state = fetch_all_municipalities_data(disease=disease)
    
    if df_state.empty:
        st.error("❌ Não foi possível carregar os dados. Verifique a conexão com a API.")
        return
    
    # ========================================================================
    # VISUALIZAÇÃO ESTADUAL
    # ========================================================================
    
    if view_type == "Estadual":
        st.markdown("## 📊 Visão Geral do Estado")
        
        # Identificar colunas
        date_col = 'data_iniSE' if 'data_iniSE' in df_state.columns else 'data_ini_SE'
        geocode_col = 'municipio_geocodigo' if 'municipio_geocodigo' in df_state.columns else 'geocode'
        
        # Métricas principais
        if geocode_col in df_state.columns:
            df_latest = df_state.sort_values(date_col).groupby(geocode_col).tail(1)
        else:
            df_latest = df_state.sort_values(date_col).tail(len(df_state.drop_duplicates(subset=['municipio_nome'])))
        
        total_casos_est = df_latest['casos_est'].sum() if 'casos_est' in df_latest.columns else 0
        total_casos = df_latest['casos'].sum() if 'casos' in df_latest.columns else 0
        media_rt = df_latest['Rt'].mean() if 'Rt' in df_latest.columns else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📈 Casos Estimados",
                value=f"{total_casos_est:,.0f}"
            )
        
        with col2:
            st.metric(
                label="📋 Casos Notificados",
                value=f"{total_casos:,.0f}"
            )
        
        with col3:
            st.metric(
                label="🔴 Rt Médio",
                value=f"{media_rt:.2f}",
                delta="Epidemia em crescimento" if media_rt > 1 else "Epidemia em controle"
            )
        
        with col4:
            if 'nivel' in df_latest.columns:
                vermelho = (df_latest['nivel'] == 4).sum()
            else:
                vermelho = 0
            st.metric(
                label="🚨 Municípios em Alerta Vermelho",
                value=vermelho
            )
        
        # Distribuição de níveis de alerta
        st.markdown("### Distribuição de Níveis de Alerta")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_alert = create_alert_distribution(df_state)
            if fig_alert:
                st.plotly_chart(fig_alert, use_container_width=True)
        
        with col2:
            if 'nivel' in df_latest.columns:
                verde = (df_latest['nivel'] == 1).sum()
                amarelo = (df_latest['nivel'] == 2).sum()
                laranja = (df_latest['nivel'] == 3).sum()
                vermelho = (df_latest['nivel'] == 4).sum()
            else:
                verde = amarelo = laranja = vermelho = 0
            
            st.markdown("#### Resumo por Nível")
            st.markdown(f"""
            - 🟢 **Verde**: {verde} municípios
            - 🟡 **Amarelo**: {amarelo} municípios
            - 🟠 **Laranja**: {laranja} municípios
            - 🔴 **Vermelho**: {vermelho} municípios
            """)
        
        # Série temporal
        st.markdown("### Evolução Temporal de Casos")
        
        fig_ts = create_time_series_chart(df_state)
        if fig_ts:
            st.plotly_chart(fig_ts, use_container_width=True)
        
        # Tabela de municípios
        st.markdown("### 📋 Dados por Município")
        
        df_table = create_municipalities_table(df_state)
        if df_table is not None:
            st.dataframe(df_table, use_container_width=True)
    
    # ========================================================================
    # VISUALIZAÇÃO POR MUNICÍPIO
    # ========================================================================
    
    else:
        st.markdown("## 🏘️ Análise por Município")
        
        # Seletor de município
        municipality_options = {v: k for k, v in GOIAS_MUNICIPALITIES.items()}
        selected_municipality = st.selectbox(
            "Selecione um município:",
            options=sorted(list(municipality_options.keys()))
        )
        
        geocode = municipality_options[selected_municipality]
        
        # Buscar dados do município
        df_muni = fetch_infodengue_data(str(geocode), disease=disease)
        
        if df_muni.empty:
            st.warning(f"⚠️ Não há dados disponíveis para {selected_municipality}")
        else:
            # Métricas do município
            date_col = 'data_iniSE' if 'data_iniSE' in df_muni.columns else 'data_ini_SE'
            latest = df_muni.sort_values(date_col).iloc[-1] if not df_muni.empty else {}
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                casos_est = latest.get('casos_est', 0)
                st.metric(label="Casos Estimados", value=f"{casos_est:.0f}")
            
            with col2:
                casos = latest.get('casos', 0)
                st.metric(label="Casos Notificados", value=f"{casos:.0f}")
            
            with col3:
                rt = latest.get('Rt', 0)
                st.metric(label="Rt", value=f"{rt:.2f}")
            
            with col4:
                nivel = int(latest.get('nivel', 1))
                nivel_names = {1: "Verde", 2: "Amarelo", 3: "Laranja", 4: "Vermelho"}
                nivel_colors = {1: "#2ecc71", 2: "#f39c12", 3: "#e67e22", 4: "#e74c3c"}
                
                nivel_name = nivel_names.get(nivel, "Desconhecido")
                nivel_color = nivel_colors.get(nivel, "#95a5a6")
                
                st.markdown(f"""
                <div style="background-color: {nivel_color}; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3 style="color: white; margin: 0;">Nível: {nivel_name}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            # Série temporal do município
            st.markdown("### Evolução de Casos")
            
            fig_ts_muni = create_time_series_chart(df_muni, title=f"Evolução de Casos - {selected_municipality}")
            if fig_ts_muni:
                st.plotly_chart(fig_ts_muni, use_container_width=True)
            
            # Dados detalhados
            st.markdown("### Dados Detalhados")
            
            cols_to_show = [
                'data_iniSE', 'data_ini_SE', 'casos_est', 'casos', 'p_inc100k', 'Rt', 'nivel'
            ]
            
            df_display = df_muni[[col for col in cols_to_show if col in df_muni.columns]].copy()
            
            st.dataframe(df_display, use_container_width=True)
    
    # ========================================================================
    # INFORMAÇÕES TÉCNICAS
    # ========================================================================
    
    st.markdown("---")
    
    with st.expander("ℹ️ Informações Técnicas"):
        st.markdown("""
        ### Fontes de Dados
        
        - **API InfoDengue**: Dados epidemiológicos em tempo real
        - **IBGE**: Dados geográficos e populacionais
        
        ### Variáveis Principais
        
        | Variável | Descrição |
        |----------|-----------|
        | **Casos Estimados** | Estimativas via modelo de nowcasting |
        | **Casos Notificados** | Casos confirmados em laboratório |
        | **Rt** | Número Reprodutivo Efetivo |
        | **Incidência** | Casos por 100.000 habitantes |
        | **Nível de Alerta** | 1=Verde, 2=Amarelo, 3=Laranja, 4=Vermelho |
        
        ### Atualização
        
        Os dados são atualizados semanalmente. Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """)

if __name__ == "__main__":
    main()
