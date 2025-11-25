# WS Transportes | Painel de Envio WhatsApp

Aplicação em Streamlit para envio de mensagens via **WPPConnect** a partir de uma planilha Excel.

## Funcionalidades

- Tela de login para conectar na API do WPPConnect:
  - Session
  - API Base URL
  - Token (Bearer)
- Upload de planilha Excel com os campos:
  - `NOME / RAZÃO SOCIAL`
  - `TELEFONE`
  - `INTEGRACAO`
  - `Nº`
  - `VENDEDOR`
  - `DATA ENTREGA`
  - `OptOut`
- Pré-visualização da base antes do envio.
- Envio de mensagens via API do WPPConnect.
- Modo teste (simula envios sem chamar a API).
- Geração de relatório em Excel com o status de cada cliente.

## Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
