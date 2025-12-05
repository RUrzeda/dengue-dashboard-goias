# ⚡ Quick Start - Dashboard Dengue Goiás

Comece em **5 minutos**!

## 🚀 Opção 1: Deploy Direto (Recomendado)

### Sem instalar nada localmente!

1. **Faça um Fork** deste repositório no GitHub
   - Clique em "Fork" no GitHub

2. **Acesse Streamlit Cloud**
   - Vá para https://share.streamlit.io/
   - Clique em "New app"

3. **Configure o Deploy**
   - Repository: `seu-usuario/dengue-dashboard-goias`
   - Branch: `main`
   - Main file: `app.py`
   - Clique em "Deploy"

4. **Pronto!** 🎉
   - Aguarde 2-3 minutos
   - Seu dashboard estará online!

## 💻 Opção 2: Executar Localmente

### Pré-requisitos
- Python 3.8+
- Git

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/dengue-dashboard-goias.git
cd dengue-dashboard-goias

# 2. Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o dashboard
streamlit run app.py
```

O dashboard abrirá em `http://localhost:8501`

## 📊 O que você verá

✅ **Visão Estadual**
- Métricas de Goiás
- Distribuição de alertas
- Série temporal de casos

✅ **Mapa Interativo**
- Municípios coloridos por risco
- Dados ao passar o mouse
- Múltiplas métricas disponíveis

✅ **Análise por Município**
- Dados detalhados
- Série temporal individual
- Indicadores epidemiológicos

## 🔗 Links Úteis

| Link | Descrição |
|------|-----------|
| [Documentação Completa](README.md) | Guia detalhado |
| [Guia de Deploy](DEPLOY.md) | Instruções passo a passo |
| [InfoDengue](https://info.dengue.mat.br/) | Fonte de dados |
| [Streamlit Cloud](https://streamlit.io/cloud) | Plataforma de hosting |

## ❓ Problemas Comuns

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### "Connection timeout"
- Verifique sua conexão com a internet
- A API InfoDengue pode estar temporariamente indisponível

### Mapa não carrega
- Limpe o cache: `streamlit cache clear`
- Recarregue a página

## 📞 Suporte Rápido

- **Documentação**: Veja [README.md](README.md)
- **Problemas**: Abra uma [Issue no GitHub](https://github.com/seu-usuario/dengue-dashboard-goias/issues)
- **InfoDengue**: https://info.dengue.mat.br/

---

**Pronto para começar?** 🚀

Escolha uma opção acima e em poucos minutos você terá seu dashboard rodando!

Qualquer dúvida, consulte a [documentação completa](README.md).
