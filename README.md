# 🦟 Dashboard de Monitoramento de Dengue em Goiás

Um dashboard interativo desenvolvido com Streamlit para monitoramento em tempo real de casos de dengue em Goiás, integrando dados da API InfoDengue/Mosqlimate com visualizações geoespaciais.

## 🎯 Funcionalidades

- **Visão Estadual**: Métricas agregadas de Goiás com distribuição de níveis de alerta
- **Série Temporal**: Evolução de casos estimados vs. notificados ao longo do tempo
- **Mapa Interativo**: Visualização coroplética de municípios com múltiplas métricas:
  - Taxa de Incidência (casos por 100.000 habitantes)
  - Nível de Alerta (semáforo epidemiológico)
  - Número Reprodutivo Efetivo (Rt)
- **Análise por Município**: Dados detalhados e série temporal para cada município
- **Indicadores Epidemiológicos**: Rt, incidência, receptividade climática, transmissão
- **Cache Inteligente**: Otimização de performance com cache de dados

## 📊 Dados Utilizados

### Fontes Principais

1. **API InfoDengue/Mosqlimate**
   - Dados epidemiológicos em tempo real
   - Estimativas via modelo de nowcasting
   - Atualização semanal

2. **IBGE**
   - Dados populacionais para cálculo de incidência
   - Códigos de municípios (IBGE geocode)

3. **Geobr**
   - Shapefiles de municípios brasileiros
   - Geometrias simplificadas para performance

### Variáveis Disponíveis

| Variável | Descrição | Fonte |
|----------|-----------|-------|
| `casos_est` | Casos estimados (nowcasting) | InfoDengue |
| `casos` | Casos notificados | InfoDengue |
| `p_inc100k` | Taxa de incidência por 100k hab. | InfoDengue |
| `Rt` | Número reprodutivo efetivo | InfoDengue |
| `nivel` | Nível de alerta (1-4) | InfoDengue |
| `receptivo` | Receptividade climática | InfoDengue |
| `transmissao` | Evidência de transmissão | InfoDengue |
| `pop` | População estimada | IBGE |

## 🚀 Como Usar Localmente

### Pré-requisitos

- Python 3.8+
- pip ou conda

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/dengue-dashboard-goias.git
cd dengue-dashboard-goias
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Executar Localmente

```bash
streamlit run app.py
```

O dashboard será aberto em `http://localhost:8501`

## 🌐 Deploy no Streamlit Cloud

### Pré-requisitos

1. Conta no GitHub
2. Conta no Streamlit Cloud (https://streamlit.io/cloud)

### Passos para Deploy

1. **Prepare o repositório GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Dengue Dashboard"
   git branch -M main
   git remote add origin https://github.com/seu-usuario/dengue-dashboard-goias.git
   git push -u origin main
   ```

2. **Acesse Streamlit Cloud**:
   - Vá para https://share.streamlit.io/
   - Clique em "New app"
   - Selecione seu repositório GitHub
   - Escolha a branch (main)
   - Defina o caminho do arquivo: `app.py`

3. **Configurações Recomendadas**:
   - Python version: 3.11
   - Deixe as demais opções com valores padrão

4. **Deploy**:
   - Clique em "Deploy"
   - Aguarde a compilação (pode levar 2-3 minutos na primeira vez)

### URL Pública

Após o deploy, seu dashboard estará disponível em:
```
https://share.streamlit.io/seu-usuario/dengue-dashboard-goias/main/app.py
```

## 📈 Interpretação dos Indicadores

### Nível de Alerta

- 🟢 **Verde (1)**: Situação sob controle
- 🟡 **Amarelo (2)**: Atenção, casos acima do esperado
- 🟠 **Laranja (3)**: Alerta, transmissão ativa
- 🔴 **Vermelho (4)**: Emergência, situação crítica

### Número Reprodutivo (Rt)

- **Rt > 1**: Epidemia em crescimento exponencial
- **Rt = 1**: Epidemia estável
- **Rt < 1**: Epidemia em declínio

### Taxa de Incidência

- **< 100/100k**: Baixa transmissão
- **100-300/100k**: Transmissão moderada
- **> 300/100k**: Transmissão alta (nível epidêmico - OMS)

## 🔧 Estrutura do Projeto

```
dengue-dashboard-goias/
├── app.py                 # Aplicação principal Streamlit
├── fetch_data.py          # Funções para buscar dados da API
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── .gitignore            # Arquivos a ignorar no Git
└── .streamlit/
    └── config.toml       # Configurações do Streamlit
```

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'geobr'"

**Solução**: Instale as dependências de sistema necessárias:
```bash
# Ubuntu/Debian
sudo apt-get install libgdal-dev libgeos-dev libproj-dev

# macOS
brew install gdal geos proj

# Depois reinstale
pip install --upgrade geopandas geobr
```

### Erro: "Connection timeout" ao buscar dados da API

**Solução**: A API pode estar temporariamente indisponível. O dashboard tentará novamente na próxima execução. Verifique:
- Conexão com a internet
- Status da API em https://info.dengue.mat.br/

### Mapa não carrega

**Solução**: Verifique se:
- Você tem conexão com a internet
- O arquivo de configuração `.streamlit/config.toml` está correto
- Limpe o cache: `streamlit cache clear`

## 📚 Referências

- [Documentação Streamlit](https://docs.streamlit.io/)
- [InfoDengue](https://info.dengue.mat.br/)
- [Mosqlimate API](https://api.mosqlimate.org/)
- [Geobr Documentation](https://ipeagit.github.io/geobr/)
- [Plotly Documentation](https://plotly.com/python/)

## 📝 Notas Técnicas

### Performance

- Implementação de cache com `@st.cache_data` para otimizar requisições à API
- TTL (Time To Live) de 1 hora para dados epidemiológicos
- TTL de 24 horas para dados geográficos (menos voláteis)
- Simplificação de geometrias para reduzir tamanho do mapa

### Qualidade de Dados

- Dados passam por validação e limpeza automática
- Valores faltantes são preenchidos com 0
- Tipos de dados são convertidos apropriadamente
- Datas são padronizadas em formato ISO 8601

### Segurança

- Sem armazenamento de dados sensíveis
- Sem autenticação necessária (dados públicos)
- HTTPS obrigatório em Streamlit Cloud
- XSRF protection ativada

## 👥 Contribuições

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Contato

- **Desenvolvedor**: [Seu Nome]
- **Email**: seu.email@example.com
- **GitHub**: https://github.com/seu-usuario

## 🙏 Agradecimentos

- Equipe InfoDengue/Mosqlimate - UFRJ
- Projeto Alerta Dengue
- Comunidade Streamlit
- IBGE pelos dados geográficos

---

**Última atualização**: Dezembro 2024

**Status**: ✅ Em produção

**Versão**: 1.0.0
