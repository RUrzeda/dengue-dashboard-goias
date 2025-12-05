"""
Script para buscar dados de dengue da API InfoDengue/Mosqlimate
e preparar para visualização no dashboard Streamlit
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API endpoints
MOSQLIMATE_API = "https://api.mosqlimate.org/api/datastore/infodengue"
INFODENGUE_API = "https://info.dengue.mat.br/api/alertcity"

# Estados e municípios de interesse (Goiás como foco principal)
GOIAS_STATE_CODE = "GO"
GOIAS_MUNICIPALITIES = {
    "3301500": "Goiânia",
    "3302502": "Aparecida de Goiânia",
    "3302155": "Anápolis",
    "3303302": "Jataí",
    "3304159": "Luziânia",
    "3304557": "Rio de Janeiro (exemplo)",  # Para comparação
}


def fetch_infodengue_data(
    state: str = "GO",
    start_date: str = None,
    end_date: str = None,
    disease: str = "dengue"
) -> pd.DataFrame:
    """
    Busca dados da API Mosqlimate para um estado específico.
    
    Args:
        state: Código do estado (UF) - ex: "GO", "SP"
        start_date: Data inicial (YYYY-mm-dd)
        end_date: Data final (YYYY-mm-dd)
        disease: Tipo de doença (dengue, zika, chikungunya)
    
    Returns:
        DataFrame com dados epidemiológicos
    """
    
    if start_date is None:
        # Últimos 52 semanas
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
    
    if end_date is None:
        end_date = datetime.now().date()
    
    # Converter para strings se necessário
    start_date = str(start_date)
    end_date = str(end_date)
    
    logger.info(f"Buscando dados de {disease} para {state} de {start_date} a {end_date}")
    
    params = {
        "page": 1,
        "per_page": 100,
        "disease": disease,
        "start": start_date,
        "end": end_date,
        "uf": state
    }
    
    try:
        response = requests.get(MOSQLIMATE_API, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Extrair items da resposta
        items = data.get("items", [])
        
        # Se houver múltiplas páginas, buscar todas
        pagination = data.get("pagination", {})
        total_pages = pagination.get("total_pages", 1)
        
        logger.info(f"Total de páginas: {total_pages}")
        
        all_items = items.copy()
        
        for page in range(2, total_pages + 1):
            params["page"] = page
            response = requests.get(MOSQLIMATE_API, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            all_items.extend(data.get("items", []))
        
        # Converter para DataFrame
        df = pd.DataFrame(all_items)
        
        logger.info(f"Dados obtidos: {len(df)} registros")
        
        return df
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()


def fetch_infodengue_city_data(
    geocode: str,
    disease: str = "dengue",
    ew_start: int = 1,
    ew_end: int = 52,
    ey_start: int = 2024,
    ey_end: int = 2024
) -> pd.DataFrame:
    """
    Busca dados de uma cidade específica usando a API InfoDengue.
    
    Args:
        geocode: Código IBGE do município
        disease: Tipo de doença
        ew_start: Semana epidemiológica inicial
        ew_end: Semana epidemiológica final
        ey_start: Ano inicial
        ey_end: Ano final
    
    Returns:
        DataFrame com dados da cidade
    """
    
    logger.info(f"Buscando dados para geocode {geocode}")
    
    url = INFODENGUE_API
    params = {
        "geocode": geocode,
        "disease": disease,
        "format": "json",
        "ew_start": ew_start,
        "ew_end": ew_end,
        "ey_start": ey_start,
        "ey_end": ey_end
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data)
        
        logger.info(f"Dados obtidos para {geocode}: {len(df)} registros")
        
        return df
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao buscar dados da cidade: {e}")
        return pd.DataFrame()


def process_dengue_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa e limpa dados de dengue.
    
    Args:
        df: DataFrame bruto da API
    
    Returns:
        DataFrame processado
    """
    
    if df.empty:
        return df
    
    # Converter tipos de dados
    numeric_cols = [
        'casos_est', 'casos_est_min', 'casos_est_max', 'casos',
        'p_rt1', 'p_inc100k', 'Rt', 'pop', 'receptivo', 'transmissao',
        'umidmax', 'umidmed', 'umidmin', 'tempmax', 'tempmed', 'tempmin'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Converter datas
    if 'data_iniSE' in df.columns:
        df['data_iniSE'] = pd.to_datetime(df['data_iniSE'], errors='coerce')
    
    # Preencher valores faltantes
    df = df.fillna(0)
    
    # Ordenar por data
    if 'data_iniSE' in df.columns:
        df = df.sort_values('data_iniSE')
    
    return df


def get_alert_level_name(level: int) -> str:
    """
    Converte nível de alerta numérico para nome.
    
    Args:
        level: Nível (1-4)
    
    Returns:
        Nome do nível
    """
    
    levels = {
        1: "Verde",
        2: "Amarelo",
        3: "Laranja",
        4: "Vermelho"
    }
    
    return levels.get(level, "Desconhecido")


def get_alert_level_color(level: int) -> str:
    """
    Retorna cor para o nível de alerta.
    
    Args:
        level: Nível (1-4)
    
    Returns:
        Cor em hex
    """
    
    colors = {
        1: "#2ecc71",  # Verde
        2: "#f39c12",  # Amarelo
        3: "#e67e22",  # Laranja
        4: "#e74c3c"   # Vermelho
    }
    
    return colors.get(level, "#95a5a6")


if __name__ == "__main__":
    # Teste: buscar dados de Goiás
    df = fetch_infodengue_data(state="GO")
    
    if not df.empty:
        df = process_dengue_data(df)
        print(f"Dados processados: {len(df)} registros")
        print(df.head())
        print("\nColunas disponíveis:")
        print(df.columns.tolist())
    else:
        print("Nenhum dado obtido")
