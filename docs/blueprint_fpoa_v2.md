# BLUEPRINT FPOA v2 — F.PRIME OPERATIONS AGENT (Implementação Detalhada)

> Gerado por HERMES OMNISYSTEM (agent-factory, 13 fases) em 2026-09-13.
> Princípio guia: **arquitetura mínima capaz de vencer** — 1 agente especializado + workflows determinísticos, rodando no Hermes já existente, SEM API paga nova.

---

## 0. DECISÕES DE ARQUITETURA (POR QUÊ)

| Decisão | Escolha | Justificativa |
|---|---|---|
| Runtime | Hermes (este agente), via Telegram DM | Já opera 24/7, tem as integrações, Felipe já usa |
| Estado | Google Sheets (planilha mestre privada) | Já conectado (Conta do Felipe), persistente, editável por humano, zero custo, formulas de KPI |
| Automação | Cron jobs do Hermes | Já funcionam; dispensa servidor novo |
| Comunicação externa | Gmail (templates) | Já conectado; fábricas/lojistas respondem por e-mail |
| Entrada de tabelas | PDF/foto → OCR (rapidocr local) + confirmação humana | Sem custo; evita erro de preço |
| Interface | Chat em linguagem natural (Telegram) | Felipe conversa; o agente alimenta tudo |

**Por que Sheets e não Supabase na v1:** o negócio tem 1 usuário (Felipe) e ~100 fábricas — uma planilha resolve, é auditável e ele entende. Supabase entra na v2 se crescer para múltiplos usuários/agentes.

---

## 1. PLANILHA MESTRE "FPRIME OPS" (Google Sheets — conta cabelleirareal@gmail.com)

### Aba: `fabricas` (representadas)
`id_fabrica | razao_social | nome_fantasia | contato | email | whatsapp | linha (categoria) | condicoes (prazo pgto) | comissao_pct | prazo_entrega_dias | tabela_link | status(ativo/inativo)`

### Aba: `catalogo` (produtos por fábrica)
`id_produto | id_fabrica | sku_fabrica | nome | categoria | colecao | preco_unit | preco_min | disponibilidade (estoque/sob-consulta) | foto_url | atualizado_em`

### Aba: `lojistas` (CRM)
`id_lojista | nome_loja | contato | cidade | uf | segmento (moda-feminina/masculina/infantil/íntima) | ticket_medio | whatsapp | email | ultima_compra | frequencia_dias | tags | anotacoes`

### Aba: `pedidos` (pipeline — a coluna `status` NUNCA é deletada, só muda)
`id_pedido | data | id_lojista | id_fabrica | itens (json: sku x qtd x preco) | valor_total | status | comissao_prevista | historico (timeline do agente) | data_atualizacao`

Status: `orcamento → enviado → confirmado → faturado → entregue → cancelado`

### Aba: `comissoes` (mensal)
`mes (AAAA-MM) | id_fabrica | valor_vendido | comissao_devida | status (a-receber/recebido/divergencia) | data_pagamento | observacao`

### Aba: `visitas` (agenda)
`data | id_lojista | cidade | objetivo | resultado | proximo_passo`

### Aba: `audit` (log imutável — anexa linhas, nunca edita)
`ts | quem (felipe/fpoa) | acao | aba | id_registro | detalhe`

### Aba: `dashboard` (KPIs via FÓRMULAS — o agente não escreve aqui, só lê)
- Pedidos este mês (COUNTIF por mês)
- Ticket médio (AVERAGEIF)
- Comissão a receber (SUMIF status=a-receber)
- Pedidos por status (COUNTIF por status)
- Lojistas ativos (COUNTIF ultima_compra > 90 dias)
- Top 5 fábricas por venda (QUERY)

---

## 2. WORKFLOWS DETALHADOS (TRIGGER → PASSOS → TOOLS → HANDOFF → ERRO)

### WF1 — Cadastrar representada / atualizar catálogo
- **Trigger:** Felipe envia tabela/PDF/foto ou "cadastra a fábrica X".
- **Passos:**
  1. Extrair texto via OCR (rapidocr) ou leitura do PDF.
  2. Estruturar em linhas de catálogo (sku, nome, preço, coleção).
  3. **CONFIRMAR com Felipe antes de gravar** (mostrar prévia: "achei 34 itens, preço de R$ 29,90 a R$ 189,90, confirma?").
  4. Gravar na aba `fabricas` + `catalogo` (upsert por sku_fabrica).
  5. Registrar em `audit`.
- **Tools:** OCR local, Google Sheets (googlesheets), Gmail se precisar pedir linha oficial.
- **Handoff:** nenhum (Felipe aprova).
- **Erro:** OCR ilegível → pedir imagem melhor/PDF; NUNCA chutar preço (Reality Constraint). Se a fábrica não tiver tabela, cadastrar só a ficha da fábrica e marcar "tabela pendente".

### WF2 — Cotação → Pedido → Follow-up → Faturamento → Comissão (o coração)
- **Trigger:** mensagem do Felipe: "quanto é X?", "anota pedido: loja Y, 20 unidades de Z".
- **Passos:**
  1. Consultar `catalogo` (preço vigente, disponibilidade) → responder em <1 min.
  2. Criar pedido: buscar/criar lojista em `lojistas`; montar linha em `pedidos` com status `orcamento`, valor_total e comissao_prevista (preco × qtd × comissao_pct da fábrica).
  3. Enviar e-mail de **confirmação de pedido** à fábrica (template Gmail: pedido #id, itens, lojista, entrega).
  4. Follow-up automático: se pedido ficar em `enviado` sem resposta da fábrica por 48h → e-mail de cobrança + alerta no Telegram do Felipe.
  5. Quando fábrica confirmar → status `confirmado`; quando faturar → `faturado`; lojista recebe → `entregue`.
  6. Ao `entregue`, lançar (ou atualizar) a linha de comissão do mês em `comissoes`.
- **Tools:** Sheets (tudo), Gmail (templates), Telegram (interface + alertas).
- **Handoff:** condição especial/preço fora da política → para Felipe decidir (humano no loop).
- **Erro:** fábrica não cadastrada → cadastrar primeiro (WF1 enxuto) ou recusar com aviso; divergência de preço → escalar, não chutar.

### WF3 — Conciliação mensal de comissões (cron)
- **Trigger:** dia 5 de cada mês (cron) + "fechou comissão de agosto".
- **Passos:**
  1. Ler `pedidos` do mês anterior com status `entregue`.
  2. Agrupar por fábrica, somar valores, aplicar taxa da `fabricas.comissao_pct`.
  3. Comparar com o que a fábrica enviou (se houver) → marcar divergências.
  4. Enviar resumo ao Felipe: total a receber por fábrica + pendências.
- **Tools:** Sheets, Telegram.
- **Erro:** divergência > R$ X → status `divergencia` + alerta; não auto-resolve.

### WF4 — Recompra ativa (cron semanal)
- **Trigger:** toda segunda 09:00 (cron).
- **Passos:**
  1. Selecionar lojistas com `ultima_compra` > 45 dias e que não estão em `visitas` futuras.
  2. Gerar lista priorizada por ticket/segmento.
  3. Enviar ao Felipe: "essas 8 lojas não compram há 45+ dias — sugestão: oferta da fábrica X (coleção nova)". Felipe decide o contato (humano mantém o relacionamento).
- **Tools:** Sheets, Telegram. (Sem envio automático de oferta — venda é relação pessoal.)

### WF5 — Prestação de contas por representada (cron mensal ou sob demanda)
- **Trigger:** dia 1 do mês (cron) ou "relatório da fábrica X".
- **Passos:**
  1. Filtrar pedidos por fábrica/periodo, agrupar por lojista/status.
  2. Montar resumo: clientes novos, pedidos, volume, comissão.
  3. Enviar e-mail à fábrica com o relatório (Gmail) + cópia ao Felipe.
- **Tools:** Sheets, Gmail.

### WF6 — Roteiro de visitas
- **Trigger:** "monta roteiro de quinta" ou cron semanal.
- **Passos:**
  1. Ler `visitas` agendadas + lojistas da região.
  2. Agrupar por cidade/bairro, ordenar por relevância, sugerir janela de horário.
  3. Criar eventos no Google Calendar do Felipe.
- **Tools:** Sheets, Google Calendar.

---

## 3. COMANDOS (linguagem natural → ação)

| Felipe diz | FPOA faz |
|---|---|
| "Cadastra a Malhas Prime, linha moletom, comissão 6%" | WF1 (ficha) |
| "Anota essa tabela" (PDF/foto) | WF1 (catálogo + confirmação) |
| "Quanto é o conjunto de moletom M da Malhas Prime?" | Consulta catálogo e responde com preço, estoque, prazo |
| "Anota pedido: Bela Moda, 30 conjuntos a 89,90" | WF2 — cria pedido, calcula comissão, confirma |
| "Status do #1042" | Timeline do pedido |
| "Fechou comissão de agosto" | WF3 |
| "Quem não compra há 60 dias?" | WF4 (consulta) |
| "Relatório da Malhas Prime" | WF5 |
| "Roteiro de quinta" | WF6 |
| "O que está travado?" | Lista pedidos parados + alertas |

---

## 4. AUTOMAÇÕES (CRON JOBS NO HERMES)

| Horário | Rotina | Entrega |
|---|---|---|
| Diário 08:00 | Pedidos parados >48h + agenda do dia | Telegram |
| Diário 18:00 | Resumo do dia (pedidos criados/faturados, pendências) | Telegram |
| Segunda 09:00 | WF4 recompra + sugestão de roteiro | Telegram |
| Dia 1 mensal | WF5 prestação de contas (todas as fábricas ativas) | Gmail + Telegram |
| Dia 5 mensal | WF3 conciliação de comissões | Telegram |

---

## 5. TRATAMENTO DE ERRO E ESCALONAMENTO (detalhado)

- **Tabela ilegível:** pedir nova imagem; nunca inventar preço.
- **Pedido parado >48h em `enviado`:** alerta + e-mail automático de follow-up à fábrica.
- **Preço fora da política / condição especial:** bloqueia, notifica Felipe (humano no loop).
- **Divergência de comissão:** marca `divergencia`, não resolve sozinho.
- **Fábrica inativa (tabela velha >90 dias):** aviso ao cadastrar pedido.
- **Ferramenta falhou (Sheets/Gmail):** retry com backoff; se persistir, declara e pede comando.
- **Ambiguação (2 fábricas com mesmo produto):** pergunta objetiva, não assume.

---

## 6. SEGURANÇA / PERMISSÕES (menor privilégio)

- Acesso só via DM do Felipe (allowlist do Telegram).
- Sheets: agente escreve em `fabricas/catalogo/lojistas/pedidos/comissoes/visitas/audit`; `dashboard` só leitura.
- NUNCA deleta linha — muda status / anexa `audit`.
- Sem acesso a dados bancários; comissão = valor devido (não pagamento).
- Tabelas de preço são sensíveis → planilha privada, sem link compartilhado.
- E-mails enviados apenas dos templates aprovados, com cópia ao Felipe.

---

## 7. KPI / OBSERVABILIDADE

- Tempo de resposta a pedido de preço (meta < 1 min).
- Pedidos sem follow-up (meta = 0).
- % pedidos parados >48h (meta < 5%).
- Comissão a receber (total e por fábrica) — visível no dashboard sempre.
- Lojistas com recompra ativa (meta +15% recorrência em 6 meses).
- Relatórios entregues no prazo (meta 100%).

---

## 8. ROADMAP DE IMPLEMENTAÇÃO (fases)

**Fase 0 — Fundação (dia 1):**
- Criar planilha "FPRIME OPS" com as 8 abas + fórmulas do dashboard.
- Criar skill `fprime-ops` (workflows, comandos, templates) no Hermes.
- Testar conexão Sheets/Gmail/Calendar com Felipe (1 pedido fake fim-a-fim).

**Fase 1 — Coração (semana 1):**
- WF1 + WF2 operacionais. Cadastrar as 20 fábricas top (regra 80/20) + catálogo das 5 mais vendidas.
- Ajustar templates de e-mail com aprovação do Felipe.

**Fase 2 — Dinheiro (semana 2):**
- WF3 (comissões) + WF5 (prestação de contas). Primeira conciliação real.

**Fase 3 — Crescimento (semana 3):**
- WF4 (recompra) + WF6 (roteiro). Ligar todos os crons.

**Fase 4 — Avaliação (mês 2):**
- Revisar KPIs, red team do fluxo (simular pedido perdido, divergência, tabela errada), ajustar.

**v2 (se necessário):** migrar pedidos para Supabase quando houver +1 usuário ou necessidade de app.

---

## 9. RED TEAM DO PRÓPRIO PLANO (riscos e mitigações)

| Risco | Mitigação |
|---|---|
| Felipe esquece de alimentar planilha | Ele não alimenta — conversa com o agente; tudo entra por chat |
| OCR erra preço | Confirmação humana obrigatória antes de publicar tabela |
| 100+ fábricas = cadastro longo | Começar pelas 20 top (pareto); o resto entra sob demanda |
| Vazamento de tabela de preço | Planilha privada; sem compartilhamento; auditoria |
| Agente "achando" que entendeu errado | Toda ação destrutiva/irreversível exige confirmação |
| Dependência de 1 humano (Felipe) | O agente é exatamente o que remove esse gargalo |

---

**Reality Constraint:** este blueprint é o DESIGN completo. A execução começa na Fase 0 (criar planilha + skill), que depende apenas da autorização do Senhor para tocar a conta Google já conectada.