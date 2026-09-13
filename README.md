# F.PRIME OPERATIONS AGENT (FPOA)

Agente operacional-comercial para escritórios de representação comercial de vestuário e moda.
Construído para o caso F.PRIME (EUS COMÉRCIO DE CONFECÇÕES E REPRESENTAÇÕES LTDA — CNPJ 28.875.415/0001-28), mas projetado para ser configurável para qualquer representação comercial.

> **Autoria e segurança:** este repositório contém **apenas código e documentação**. Nenhuma credencial, token ou conta pessoal está embutida. Todas as integrações (Google Sheets, Gmail, Calendar, Telegram) são configuradas pelo **cliente/operador** através de variáveis de ambiente ou arquivo `.env` local. Nenhuma conta do autor é usada para operar negócios de terceiros.

## O que resolve

- Catálogo unificado das fábricas/confecções representadas (preço, coleção, disponibilidade)
- Pipeline de pedidos: cotação → pedido → follow-up → faturamento → comissão
- Conciliação mensal de comissões por fábrica
- CRM de lojistas com alerta de recompra
- Prestação de contas por representada
- Roteiro de visitas por região

## Arquitetura

```
src/fprime/
  models.py        # Modelos de dados (Fabrica, Produto, Lojista, Pedido, Comissao)
  catalog.py       # Catálogo unificado + consulta de preço
  orders.py        # Pipeline de pedidos + follow-up + comissão prevista
  commissions.py   # Conciliação mensal de comissões
  crm.py           # CRM de lojistas + recompra ativa
  reporting.py     # Prestação de contas por representada
  routing.py       # Roteiro de visitas por região
  sheets.py        # Adaptador Google Sheets (implementação via API do cliente)
  gmail.py         # Adaptador Gmail (templates)
  telegram.py      # Adaptador Telegram (interface)
  cli.py           # CLI do agente (comandos em linguagem natural)
  config.py        # Configuração via .env / variáveis de ambiente
tests/             # Testes unitários (pytest)
docs/              # Dossiê da empresa + blueprint de implementação
data/              # Dados de exemplo (CSV/JSON, sem informações sensíveis)
```

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configuração (nunca commitar .env)
cp .env.example .env
# Preencha: credenciais do CLIENTE (Sheets/Gmail/Telegram) — nunca as do autor
```

## Uso (CLI)

```bash
python -m fprime "Quanto é o conjunto de moletom M da Malhas Prime?"
python -m fprime "Anota pedido: Bela Moda, 30 conjuntos a 89,90"
python -m fprime "Status do #1042"
python -m fprime "Fechou comissão de agosto"
python -m fprime "Quem não compra há 60 dias?"
python -m fprime "Relatório da Malhas Prime"
python -m fprime "Roteiro de quinta"
```

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

## Estrutura de dados (Google Sheets "FPRIME OPS")

Abas: `fabricas`, `catalogo`, `lojistas`, `pedidos`, `comissoes`, `visitas`, `audit`, `dashboard`.

## Licença

MIT © 2026. Software de uso geral; cada operador configura suas próprias integrações.