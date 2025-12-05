"""
Dashboard de Monitoramento de Dengue em Goiás
Integração com API InfoDengue/Mosqlimate
Desenvolvido com Streamlit
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import logging
from functools import lru_cache
import geopandas as gpd
from geobr import read_municipality

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Dashboard Dengue - Goiás",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main {
        padding: 0rem 0rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .alert-green {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px;
        border-radius: 4px;
    }
    .alert-yellow {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        border-radius: 4px;
    }
    .alert-orange {
        background-color: #ffe5cc;
        border-left: 4px solid #fd7e14;
        padding: 10px;
        border-radius: 4px;
    }
    .alert-red {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 10px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONSTANTES E CONFIGURAÇÕES
# ============================================================================

MOSQLIMATE_API = "https://api.mosqlimate.org/api/datastore/infodengue"
INFODENGUE_API = "https://info.dengue.mat.br/api/alertcity"

# Mapeamento de códigos IBGE para municípios de Goiás (amostra)
GOIAS_MUNICIPALITIES = {
    "3301500": "Goiânia",
    "3302502": "Aparecida de Goiânia",
    "3302155": "Anápolis",
    "3303302": "Jataí",
    "3304159": "Luziânia",
    "3305109": "Itumbiara",
    "3305208": "Jaraguá",
    "3305505": "Mineiros",
    "3305703": "Morrinhos",
    "3306039": "Pirenópolis",
    "3306500": "Rio Verde",
    "3307209": "Senador Canedo",
    "3307500": "Trindade",
}

# ============================================================================
# FUNÇÕES DE CACHE E BUSCA DE DADOS
# ============================================================================

@st.cache_data(ttl=3600)
def fetch_infodengue_state_data(state_code: str = "GO", disease: str = "dengue"):
    """
    Busca dados epidemiológicos do estado via API Mosqlimate.
    Usa cache para evitar requisições desnecessárias.
    
    Args:
        state_code: Código da UF (ex: "GO")
        disease: Tipo de doença (dengue, zika, chikungunya)
    
    Returns:
        DataFrame com dados do estado
    """
    
    try:
        # Definir período: últimas 52 semanas
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        params = {
            "page": 1,
            "per_page": 100,
            "disease": disease,
            "start": str(start_date),
            "end": str(end_date),
            "uf": state_code
        }
        
        logger.info(f"Buscando dados de {disease} para {state_code}")
        
        response = requests.get(MOSQLIMATE_API, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        items = data.get("items", [])
        
        # Verificar se há múltiplas páginas
        pagination = data.get("pagination", {})
        total_pages = pagination.get("total_pages", 1)
        
        all_items = items.copy()
        
        for page in range(2, min(total_pages + 1, 6)):  # Limitar a 5 páginas
            params["page"] = page
            response = requests.get(MOSQLIMATE_API, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            all_items.extend(data.get("items", []))
        
        df = pd.DataFrame(all_items)
        
        # Processar dados
        if not df.empty:
            df = process_dengue_data(df)
        
        logger.info(f"Dados obtidos: {len(df)} registros")
        
        return df
    
    except Exception as e:
        logger.error(f"Erro ao buscar dados: {e}")
        st.warning(f"Erro ao buscar dados da API: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_municipality_data(geocode: str, disease: str = "dengue"):
    """
    Busca dados de um município específico.
    
    Args:
        geocode: Código IBGE do município
        disease: Tipo de doença
    
    Returns:
        DataFrame com dados do município
    """
    
    try:
        current_year = datetime.now().year
        
        params = {
            "geocode": geocode,
            "disease": disease,
            "format": "json",
            "ew_start": 1,
            "ew_end": 53,
            "ey_start": current_year - 1,
            "ey_end": current_year
        }
        
        response = requests.get(INFODENGUE_API, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])
        
        if not df.empty:
            df = process_dengue_data(df)
        
        return df
    
    except Exception as e:
        logger.error(f"Erro ao buscar dados do município {geocode}: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=86400)
def get_goias_geodata():
    """
    Carrega dados geográficos de Goiás usando geobr.
    
    Returns:
        GeoDataFrame com municípios de Goiás
    """
    
    try:
        logger.info("Carregando dados geográficos de Goiás")
        
        # Ler municípios do Brasil
        gdf = read_municipality(code_muni="GO", simplify=True)
        
        logger.info(f"Dados geográficos carregados: {len(gdf)} municípios")
        
        return gdf
    
    except Exception as e:
        logger.error(f"Erro ao carregar dados geográficos: {e}")
        st.warning(f"Erro ao carregar mapa: {e}")
        return None


def process_dengue_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa e limpa dados de dengue.
    
    Args:
        df: DataFrame bruto
    
    Returns:
        DataFrame processado
    """
    
    if df.empty:
        return df
    
    # Converter tipos de dados numéricos
    numeric_cols = [
        'casos_est', 'casos_est_min', 'casos_est_max', 'casos',
        'p_rt1', 'p_inc100k', 'Rt', 'pop', 'receptivo', 'transmissao',
        'umidmax', 'umidmed', 'umidmin', 'tempmax', 'tempmed', 'tempmin',
        'casprov', 'casprov_est', 'casprov_est_min', 'casprov_est_max', 'casconf'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Converter datas
    for date_col in ['data_iniSE', 'data_ini_SE']:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Preencher NaN com 0
    df = df.fillna(0)
    
    # Ordenar por data se disponível
    if 'data_iniSE' in df.columns:
        df = df.sort_values('data_iniSE')
    elif 'data_ini_SE' in df.columns:
        df = df.sort_values('data_ini_SE')
    
    return df


def get_alert_level_info(level: int) -> tuple:
    """
    Retorna nome e cor para o nível de alerta.
    
    Args:
        level: Nível (1-4)
    
    Returns:
        Tupla (nome, cor)
    """
    
    levels = {
        1: ("Verde", "#2ecc71"),
        2: ("Amarelo", "#f39c12"),
        3: ("Laranja", "#e67e22"),
        4: ("Vermelho", "#e74c3c")
    }
    
    return levels.get(int(level), ("Desconhecido", "#95a5a6"))


# ============================================================================
# COMPONENTES DE VISUALIZAÇÃO
# ============================================================================

def create_time_series_chart(df: pd.DataFrame, title: str = "Evolução de Casos Estimados"):
    """
    Cria gráfico de série temporal de casos.
    
    Args:
        df: DataFrame com dados
        title: Título do gráfico
    
    Returns:
        Figura Plotly
    """
    
    if df.empty or 'data_iniSE' not in df.columns:
        return None
    
    # Agrupar por data e somar casos
    df_agg = df.groupby('data_iniSE').agg({
        'casos_est': 'sum',
        'casos': 'sum'
    }).reset_index()
    
    fig = px.line(
        df_agg,
        x='data_iniSE',
        y=['casos_est', 'casos'],
        title=title,
        labels={
            'data_iniSE': 'Data',
            'casos_est': 'Casos Estimados (Nowcasting)',
            'casos': 'Casos Notificados'
        },
        markers=True
    )
    
    fig.update_layout(
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    return fig


def create_choropleth_map(gdf: gpd.GeoDataFrame, df: pd.DataFrame, metric: str = "p_inc100k"):
    """
    Cria mapa coroplético com dados de dengue.
    
    Args:
        gdf: GeoDataFrame com geometrias
        df: DataFrame com dados epidemiológicos
        metric: Métrica a visualizar (p_inc100k, nivel, Rt)
    
    Returns:
        Figura Plotly
    """
    
    if gdf is None or df.empty:
        return None
    
    try:
        # Preparar dados para o mapa
        # Usar o registro mais recente de cada município
        df_latest = df.sort_values('data_iniSE').groupby('municipio_geocodigo').tail(1)
        
        # Merge com dados geográficos
        gdf_merged = gdf.merge(
            df_latest,
            left_on='code_muni',
            right_on='municipio_geocodigo',
            how='left'
        )
        
        # Converter para GeoJSON
        gdf_merged['geometry'] = gdf_merged['geometry'].astype(str)
        
        # Criar mapa
        if metric == "p_inc100k":
            color_col = 'p_inc100k'
            title = "Taxa de Incidência (casos por 100k hab.)"
            colorscale = "YlOrRd"
        elif metric == "nivel":
            color_col = 'nivel'
            title = "Nível de Alerta"
            colorscale = "RdYlGn_r"
        else:  # Rt
            color_col = 'Rt'
            title = "Número Reprodutivo Efetivo (Rt)"
            colorscale = "Viridis"
        
        fig = px.choropleth_mapbox(
            gdf_merged,
            geojson=gdf_merged.geometry,
            locations=gdf_merged.index,
            color=color_col,
            hover_name='name',
            hover_data={
                'municipio_nome': True,
                'pop': ':.0f',
                'casos_est': ':.0f',
                'Rt': ':.2f',
                'p_inc100k': ':.2f',
                'nivel': True,
                'geometry': False,
                'code_muni': False,
                'municipio_geocodigo': False
            },
            color_continuous_scale=colorscale,
            mapbox_style="carto-positron",
            zoom=6,
            center={"lat": -15.7942, "lon": -48.2676},
            title=title,
            labels={color_col: title}
        )
        
        fig.update_layout(
            height=600,
            margin={"r": 0, "t": 30, "l": 0, "b": 0}
        )
        
        return fig
    
    except Exception as e:
        logger.error(f"Erro ao criar mapa: {e}")
        return None


def create_alert_level_distribution(df: pd.DataFrame):
    """
    Cria gráfico de distribuição de níveis de alerta.
    
    Args:
        df: DataFrame com dados
    
    Returns:
        Figura Plotly
    """
    
    if df.empty or 'nivel' not in df.columns:
        return None
    
    # Contar níveis
    df_latest = df.sort_values('data_iniSE').groupby('municipio_geocodigo').tail(1)
    
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


def create_metrics_summary(df: pd.DataFrame):
    """
    Cria resumo de métricas principais.
    
    Args:
        df: DataFrame com dados
    
    Returns:
        Dicionário com métricas
    """
    
    if df.empty:
        return {
            'total_casos': 0,
            'total_casos_est': 0,
            'media_rt': 0,
            'municipios_alerta_vermelho': 0
        }
    
    df_latest = df.sort_values('data_iniSE').groupby('municipio_geocodigo').tail(1)
    
    return {
        'total_casos': int(df_latest['casos'].sum()),
        'total_casos_est': int(df_latest['casos_est'].sum()),
        'media_rt': float(df_latest['Rt'].mean()),
        'municipios_alerta_vermelho': int((df_latest['nivel'] == 4).sum()),
        'municipios_alerta_laranja': int((df_latest['nivel'] == 3).sum()),
        'municipios_alerta_amarelo': int((df_latest['nivel'] == 2).sum()),
        'municipios_alerta_verde': int((df_latest['nivel'] == 1).sum()),
    }


# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================

def main():
    """Função principal do dashboard."""
    
    # Header
    st.markdown("# 🦟 Dashboard de Monitoramento de Dengue em Goiás")
    st.markdown("""
    Sistema de vigilância epidemiológica integrado com dados em tempo real da API InfoDengue/Mosqlimate.
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
    st.sidebar.info("⏳ Carregando dados... (primeira execução pode levar alguns segundos)")
    
    df_state = fetch_infodengue_state_data(state_code="GO", disease=disease)
    gdf = get_goias_geodata()
    
    if df_state.empty:
        st.error("❌ Não foi possível carregar os dados. Verifique a conexão com a API.")
        return
    
    # ========================================================================
    # VISUALIZAÇÃO ESTADUAL
    # ========================================================================
    
    if view_type == "Estadual":
        st.markdown("## 📊 Visão Geral do Estado")
        
        # Métricas principais
        metrics = create_metrics_summary(df_state)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📈 Casos Estimados",
                value=f"{metrics['total_casos_est']:,.0f}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="📋 Casos Notificados",
                value=f"{metrics['total_casos']:,.0f}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="🔴 Rt Médio",
                value=f"{metrics['media_rt']:.2f}",
                delta="Acima de 1 = Epidemia em crescimento" if metrics['media_rt'] > 1 else "Abaixo de 1 = Epidemia em controle"
            )
        
        with col4:
            st.metric(
                label="🚨 Municípios em Alerta Vermelho",
                value=metrics['municipios_alerta_vermelho'],
                delta=None
            )
        
        # Distribuição de níveis de alerta
        st.markdown("### Distribuição de Níveis de Alerta")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_alert = create_alert_level_distribution(df_state)
            if fig_alert:
                st.plotly_chart(fig_alert, use_container_width=True)
        
        with col2:
            st.markdown("#### Resumo por Nível")
            st.markdown(f"""
            - 🟢 **Verde**: {metrics['municipios_alerta_verde']} municípios
            - 🟡 **Amarelo**: {metrics['municipios_alerta_amarelo']} municípios
            - 🟠 **Laranja**: {metrics['municipios_alerta_laranja']} municípios
            - 🔴 **Vermelho**: {metrics['municipios_alerta_vermelho']} municípios
            """)
        
        # Série temporal
        st.markdown("### Evolução Temporal de Casos")
        
        fig_ts = create_time_series_chart(df_state)
        if fig_ts:
            st.plotly_chart(fig_ts, use_container_width=True)
        
        # Mapa coroplético
        st.markdown("### 🗺️ Mapa de Incidência por Município")
        
        metric_choice = st.selectbox(
            "Selecione a métrica para o mapa:",
            options=["p_inc100k", "nivel", "Rt"],
            format_func=lambda x: {
                "p_inc100k": "Taxa de Incidência",
                "nivel": "Nível de Alerta",
                "Rt": "Número Reprodutivo"
            }[x]
        )
        
        fig_map = create_choropleth_map(gdf, df_state, metric=metric_choice)
        if fig_map:
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("⚠️ Não foi possível gerar o mapa. Verifique os dados geográficos.")
    
    # ========================================================================
    # VISUALIZAÇÃO POR MUNICÍPIO
    # ========================================================================
    
    else:
        st.markdown("## 🏘️ Análise por Município")
        
        # Seletor de município
        municipality_options = {v: k for k, v in GOIAS_MUNICIPALITIES.items()}
        selected_municipality = st.selectbox(
            "Selecione um município:",
            options=list(municipality_options.keys())
        )
        
        geocode = municipality_options[selected_municipality]
        
        # Buscar dados do município
        df_muni = fetch_municipality_data(geocode, disease=disease)
        
        if df_muni.empty:
            st.warning(f"⚠️ Não há dados disponíveis para {selected_municipality}")
        else:
            # Métricas do município
            latest = df_muni.iloc[-1] if not df_muni.empty else {}
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Casos Estimados",
                    value=f"{latest.get('casos_est', 0):.0f}"
                )
            
            with col2:
                st.metric(
                    label="Casos Notificados",
                    value=f"{latest.get('casos', 0):.0f}"
                )
            
            with col3:
                st.metric(
                    label="Rt",
                    value=f"{latest.get('Rt', 0):.2f}"
                )
            
            with col4:
                nivel = int(latest.get('nivel', 1))
                nivel_name, nivel_color = get_alert_level_info(nivel)
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
                'data_iniSE', 'casos_est', 'casos', 'p_inc100k', 'Rt', 'nivel',
                'pop', 'receptivo', 'transmissao', 'tempmed', 'umidmed'
            ]
            
            df_display = df_muni[[col for col in cols_to_show if col in df_muni.columns]].copy()
            
            st.dataframe(df_display, use_container_width=True)
    
    # ========================================================================
    # INFORMAÇÕES TÉCNICAS
    # ========================================================================
    
    st.markdown("---")
    
    with st.expander("ℹ️ Informações Técnicas e Metodologia"):
        st.markdown("""
        ### Fontes de Dados
        
        - **API InfoDengue/Mosqlimate**: Dados epidemiológicos em tempo real
        - **IBGE**: Dados geográficos e populacionais
        - **Geobr**: Shapefiles de municípios brasileiros
        
        ### Variáveis Principais
        
        | Variável | Descrição |
        |----------|-----------|
        | **Casos Estimados** | Estimativas via modelo de nowcasting (mais precisas) |
        | **Casos Notificados** | Casos confirmados em laboratório |
        | **Rt** | Número Reprodutivo Efetivo (velocidade de transmissão) |
        | **Incidência** | Casos por 100.000 habitantes |
        | **Nível de Alerta** | Verde (1), Amarelo (2), Laranja (3), Vermelho (4) |
        | **Receptividade** | Condições climáticas para transmissão |
        
        ### Interpretação dos Indicadores
        
        - **Rt > 1**: Epidemia em crescimento exponencial
        - **Rt < 1**: Epidemia em declínio
        - **Incidência > 300/100k**: Nível epidêmico (OMS)
        
        ### Atualização
        
        Os dados são atualizados semanalmente pela API InfoDengue.
        
        ### Limitações
        
        - Dados podem sofrer revisões retrospectivas
        - Pequenos municípios podem ter alta variabilidade
        - Atrasos na notificação afetam dados recentes
        """)
    
    with st.expander("📞 Contato e Suporte"):
        st.markdown("""
        ### Desenvolvedores
        
        - **Dashboard**: Desenvolvido com Streamlit
        - **Dados**: InfoDengue/Mosqlimate - Universidade Federal do Rio de Janeiro
        - **Geobr**: Pacote R para dados geográficos brasileiros
        
        ### Referências
        
        - [InfoDengue](https://info.dengue.mat.br/)
        - [Mosqlimate API](https://api.mosqlimate.org/)
        - [Geobr Documentation](https://ipeagit.github.io/geobr/)
        """)


if __name__ == "__main__":
    main()
