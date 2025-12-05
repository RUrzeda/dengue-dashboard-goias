# 📦 Guia Completo de Deploy - Dashboard Dengue Goiás

Este guia fornece instruções passo a passo para fazer o deploy do dashboard no Streamlit Cloud.

## 📋 Pré-requisitos

Antes de começar, certifique-se de que você tem:

1. ✅ Conta no GitHub (https://github.com/signup)
2. ✅ Conta no Streamlit Cloud (https://streamlit.io/cloud)
3. ✅ Git instalado no seu computador
4. ✅ Acesso ao repositório do projeto

## 🔑 Passo 1: Preparar o Repositório GitHub

### 1.1 Criar um novo repositório no GitHub

1. Acesse https://github.com/new
2. Preencha os dados:
   - **Repository name**: `dengue-dashboard-goias`
   - **Description**: "Dashboard interativo de monitoramento de dengue em Goiás"
   - **Visibility**: Public (necessário para Streamlit Cloud)
   - **Initialize this repository with**: Deixe desmarcado

3. Clique em "Create repository"

### 1.2 Fazer upload dos arquivos

Existem duas formas:

#### Opção A: Via Git (Recomendado)

```bash
# Navegue até o diretório do projeto
cd dengue-dashboard-goias

# Inicialize o repositório Git
git init

# Adicione todos os arquivos
git add .

# Faça o commit inicial
git commit -m "Initial commit: Dengue Dashboard for Goiás"

# Renomeie a branch para 'main' (padrão do GitHub)
git branch -M main

# Adicione o repositório remoto
git remote add origin https://github.com/SEU_USUARIO/dengue-dashboard-goias.git

# Faça o push dos arquivos
git push -u origin main
```

#### Opção B: Via Interface Web

1. No seu repositório GitHub, clique em "Add file" > "Upload files"
2. Arraste e solte os arquivos ou selecione-os
3. Clique em "Commit changes"

## 🚀 Passo 2: Deploy no Streamlit Cloud

### 2.1 Conectar GitHub ao Streamlit Cloud

1. Acesse https://share.streamlit.io/
2. Clique em "New app"
3. Você será redirecionado para fazer login (use sua conta GitHub)

### 2.2 Configurar a aplicação

1. Após fazer login, clique em "New app"
2. Preencha os campos:
   - **Repository**: `seu-usuario/dengue-dashboard-goias`
   - **Branch**: `main`
   - **Main file path**: `app.py`

3. Clique em "Deploy"

### 2.3 Aguardar o deploy

- O Streamlit Cloud irá:
  1. Clonar seu repositório
  2. Instalar as dependências do `requirements.txt`
  3. Executar o `app.py`
  4. Disponibilizar a URL pública

- Este processo pode levar **2-5 minutos** na primeira execução

## ✅ Passo 3: Verificar o Deploy

### 3.1 Acessar o dashboard

Após o deploy ser concluído, seu dashboard estará disponível em:

```
https://share.streamlit.io/seu-usuario/dengue-dashboard-goias/main/app.py
```

Ou você pode acessar através da interface do Streamlit Cloud.

### 3.2 Testar funcionalidades

1. **Carregamento de dados**: Verifique se os dados estão sendo carregados
2. **Visualizações**: Teste os gráficos e o mapa
3. **Filtros**: Teste a seleção de arbovirose e município
4. **Performance**: Verifique se o dashboard responde rapidamente

## 🔄 Passo 4: Atualizações Futuras

Sempre que você fazer alterações no código:

```bash
# Faça as alterações necessárias

# Adicione os arquivos modificados
git add .

# Faça o commit
git commit -m "Descrição das alterações"

# Faça o push
git push origin main
```

O Streamlit Cloud detectará automaticamente as mudanças e fará o redeploy.

## 🛠️ Troubleshooting

### Erro: "Repository not found"

**Problema**: O Streamlit Cloud não consegue acessar o repositório.

**Solução**:
1. Verifique se o repositório é **público**
2. Verifique se você está usando a URL correta do repositório
3. Reconecte sua conta GitHub ao Streamlit Cloud

### Erro: "ModuleNotFoundError"

**Problema**: Uma dependência não foi instalada.

**Solução**:
1. Verifique se todas as dependências estão em `requirements.txt`
2. Verifique a ortografia dos nomes dos pacotes
3. Atualize o arquivo e faça um novo push

### Dashboard carrega lentamente

**Problema**: A primeira requisição à API leva muito tempo.

**Solução**:
1. O cache do Streamlit Cloud pode levar alguns minutos para ser populado
2. Atualize a página após alguns minutos
3. Verifique a disponibilidade da API InfoDengue

### Mapa não aparece

**Problema**: O mapa geográfico não está sendo renderizado.

**Solução**:
1. Verifique se `geopandas` e `geobr` foram instalados corretamente
2. Verifique a conexão com a internet
3. Limpe o cache do navegador (Ctrl+Shift+Del)

## 📊 Monitoramento Pós-Deploy

### Logs do Streamlit Cloud

1. Acesse https://share.streamlit.io/
2. Selecione seu aplicativo
3. Clique em "Manage app" > "Logs"

### Métricas de Performance

- **Tempo de carregamento inicial**: Deve ser < 30 segundos
- **Tempo de resposta**: Deve ser < 5 segundos
- **Taxa de erro**: Deve ser 0%

## 🔐 Segurança

### Boas Práticas

1. ✅ Nunca commite credenciais ou chaves de API
2. ✅ Use variáveis de ambiente para dados sensíveis
3. ✅ Mantenha o repositório público (dados são públicos)
4. ✅ Revise o código antes de fazer push

### Variáveis de Ambiente (se necessário)

Se precisar adicionar variáveis de ambiente:

1. No Streamlit Cloud, clique em "Manage app"
2. Vá para "Secrets"
3. Adicione suas variáveis no formato TOML

## 📞 Suporte

Se encontrar problemas:

1. **Documentação Streamlit**: https://docs.streamlit.io/
2. **Forum Streamlit**: https://discuss.streamlit.io/
3. **Issues no GitHub**: Abra uma issue no seu repositório
4. **InfoDengue**: https://info.dengue.mat.br/ (para problemas com dados)

## ✨ Próximos Passos

Após o deploy bem-sucedido:

1. **Compartilhe o link**: Envie a URL para colegas e stakeholders
2. **Configure um domínio customizado**: (Recurso premium do Streamlit)
3. **Implemente autenticação**: Se necessário (Streamlit Cloud Pro)
4. **Monitore métricas**: Acompanhe o uso e performance
5. **Atualize regularmente**: Mantenha as dependências atualizadas

## 📝 Checklist Final

- [ ] Repositório GitHub criado e público
- [ ] Todos os arquivos fazem push corretamente
- [ ] `requirements.txt` contém todas as dependências
- [ ] `app.py` está na raiz do repositório
- [ ] Deploy no Streamlit Cloud concluído
- [ ] Dashboard acessível via URL pública
- [ ] Dados carregam corretamente
- [ ] Visualizações funcionam
- [ ] Mapa é renderizado
- [ ] Sem erros nos logs

---

**Parabéns!** 🎉 Seu dashboard está pronto para produção!

Para mais informações, consulte a [Documentação do Streamlit Cloud](https://docs.streamlit.io/streamlit-cloud).
