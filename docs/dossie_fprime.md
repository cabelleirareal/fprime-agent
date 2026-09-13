# DOSSIÊ F.PRIME — Investigação profunda + Spec do Agente Personalizado

> Gerado por HERMES OMNISYSTEM (enterprise-discovery + agent-factory) em 2026-09-13.
> Fontes: OCR do cartão enviado pelo cliente, BrasilAPI/CNPJ.ws/ReceitaWS (dados oficiais Receita Federal, atualizados 2026-08-08), LinkedIn FPrime Representações, Serasa/cnpja (dados públicos). Inferências estão sinalizadas como tal.

---

## 1. IDENTIFICAÇÃO (verificada)

| Campo | Valor |
|---|---|
| Cartão (imagem) | ESCRITÓRIO DE REPRESENTAÇÃO F.PRIME |
| Razão social | EUS COMÉRCIO DE CONFECÇÕES E REPRESENTAÇÕES LTDA. |
| Nome fantasia | EUS CONFECÇÕES (opera como F.PRIME REPRESENTAÇÕES) |
| CNPJ | 28.875.415/0001-28 |
| Fundação | 17/10/2017 (~8 anos e 11 meses) |
| Situação | ATIVA (desde a abertura) — MATRIZ |
| Porte | EPP (Empresa de Pequeno Porte) |
| Natureza | Sociedade Empresária Limitada |
| Capital social | R$ 40.000,00 |
| Regime | Simples Nacional (optante desde 17/10/2017) |
| Sócio | FELIPE NUNES — Sócio-Administrador (entrada 25/11/2022, 31-40 anos) |
| Endereço fiscal | Rua Dr. Pacheco e Silva, 110 — Canindé, São Paulo-SP, CEP 03029-010 |
| Endereço cartão | Rua Guaranésia, 381 — Vila Maria, São Paulo-SP, CEP 02112-000 |
| Telefone | (11) 2291-2010 |
| E-mail | financeiro@fprime.net.br |
| Inscrição estadual | 151909201111 (ativa) |
| Site | fprime.net (placeholder — sem conteúdo público) |

## 2. ATIVIDADES (CNAEs)

- **Principal:** 8211-3/00 — Serviços combinados de escritório e apoio administrativo
- **Secundárias:**
  - 4616-8/00 — Representantes comerciais e agentes do comércio de têxteis, vestuário, calçados e artigos de viagem ⭐ (o negócio de verdade)
  - 4642-7/01 — Comércio atacadista de artigos do vestuário e acessórios
  - 4781-4/00 — Comércio varejista de artigos do vestuário e acessórios
  - 8299-7/99 — Outras atividades de serviços prestados às empresas

CNAE principal é "escritório administrativo", mas a operação real é **representação comercial de moda** (CNAE secundário 4616-8/00) — perfil típico de escritório de representação.

## 3. NEGÓCIO (LinkedIn, verificado)

> "Somos uma empresa especializada em Representação Comercial no ramo de vestuário e moda, representando mais de 100 fábricas e confecções em todo o território [nacional]." — FPrime Representações (LinkedIn)

**Modelo de negócio:** intermediário B2B entre confecções (representadas) e lojistas/varejo. Ganha **comissão** sobre vendas intermediadas. Portfólio de 100+ fábricas, atuação nacional.

**Cadeia de valor:** FÁBRICA (representada) → F.PRIME (representante) → LOJISTA → consumidor final. O valor entregue: curadoria de fornecedores, catálogo, negociação, logística de informação e relacionamento.

---

## 4. GARGALOS ATUAIS (mapeados)

> Método: Process Discovery + Agent Opportunity Matrix (A=automação simples, B=workflow determinístico, C=agente especializado, D=multiagente, E=humano+agente, F=humano obrigatório).

### 4.1 Carteira de 100+ representadas sem catálogo unificado — **Classe C**
- Cada fábrica tem tabela, coleção, condições e prazo próprios. Informação descentralizada (WhatsApp, PDFs, fotos).
- **Custo:** tempo de busca por produto; erro de preço/prazo; perda de venda.
- **Oportunidade:** catálogo único consultável (produto, preço, coleção, disponibilidade).

### 4.2 Follow-up de pedidos manual — **Classe C**
- Pedido do lojista → confirmação com a fábrica → faturamento → comissão. Rastreio em planilhas/WhatsApp.
- **Custo:** atraso, pedido perdido, comissão não cobrada.

### 4.3 Dependência de WhatsApp como "sistema" — **Classe B/C**
- Pedidos por foto/áudio, sem registro estruturado. Informação morre na conversa.
- **Custo:** perda de histórico, impossibilidade de análise, retrabalho.

### 4.4 Comissões sem conciliação automatizada — **Classe B**
- Comissão por fábrica × vendedor × mês. Planilhas manuais, erros, atraso no recebimento.
- **Oportunidade:** tracker de comissão com regras por representada.

### 4.5 CRM de lojistas inexistente — **Classe C**
- Sem histórico estruturado de compras por loja. Recompra não é ativada; perfil da loja (segmento, região, ticket) não é usado.

### 4.6 Prestação de contas para representadas — **Classe B**
- Fábricas exigem relatórios (vendas, visitas, clientes novos). Gerados manualmente, consomem dias.

### 4.7 Agenda de visitas e praças sem roteiro otimizado — **Classe B**
- Visitas a lojistas e feiras (ex.: Fenin) sem planejamento por região.

### 4.8 Gargalo humano central (1 sócio-administrador) — **Classe E**
- Felipe Nunes concentra tudo (vendas, admin, financeiro). **Ponto único de falha.**

---

## 5. GARGALOS FUTUROS (projeção coerente)

1. **Escala sem equipe:** crescer de 100 para 200+ representadas dobraria o trabalho administrativo — insustentável sem automação.
2. **Digitalização do lojista:** compra migrando para canais digitais; sem catálogo online, F.PRIME perde para marketplaces B2B (ExpoFeria, FashIn, etc.).
3. **Dados como ativo:** sem CRM/histórico, não há recompra ativa nem previsão de demanda — concorrentes que usam dados capturam os melhores lojistas.
4. **Concentração de risco:** dependência de poucas fábricas grandes na carteira; comissão concentrada.
5. **Sucessão e governança:** operação 100% dependente de 1 pessoa inviabiliza férias, doença ou expansão.
6. **Compliance fiscal das comissões:** crescer a operação sem controles automatizados aumenta risco tributário/previdenciário (retenções, notas).

---

## 6. AGENTE PERSONALIZADO — F.PRIME OPERATIONS AGENT (spec 21 campos)

> Arquitetura mínima capaz de vencer: **1 agente especializado (Classe C) + workflows determinísticos (Classe B)** — não criar 10 agentes. O agente centraliza a operação comercial; os workflows automatizam o repetitivo.

| Campo | Definição |
|---|---|
| **NAME** | F.PRIME OPERATIONS AGENT (FPOA) |
| **PURPOSE** | Eliminar os gargalos 4.1–4.8: centralizar catálogo, pedidos, comissões, CRM e prestação de contas num único assistente operado por chat (Telegram/WhatsApp) — sem API paga, usando as integrações já conectadas. |
| **ROLE** | Assistente operacional-comercial do escritório: coordena o fluxo representada → lojista → pedido → comissão → relatório. |
| **OBJECTIVES** | 1) Catálogo unificado das 100+ representadas consultável em segundos; 2) zero pedido sem rastreio (da cotação à comissão); 3) comissões conciliadas por mês automaticamente; 4) CRM de lojistas com recompra ativa; 5) relatórios de prestação de contas sob demanda; 6) roteiro de visitas por região. |
| **INPUTS** | Mensagens de chat (pedidos, dúvidas, fotos/PDFs de tabelas), planilhas de comissão, catálogo das fábricas, agenda, histórico de vendas. |
| **OUTPUTS** | Respostas de status de pedido; ficha de produto/preço; extrato de comissão; relatório de prestação de contas (PDF/planilha); roteiro de visitas; alerta de recompra de lojista. |
| **SKILLS** | `enterprise-discovery` (contexto), `agent-factory` (evolução), `failure-recovery` (resiliência), + skills operacionais: catálogo, CRM, comissão, relatório. |
| **KNOWLEDGE** | Portfólio (fábricas × linhas × preços × condições), política de comissão por representada, praças/regiões atendidas, perfil de lojistas. |
| **MEMORY** | Working: pedidos em aberto. Episódica: histórico de negociações. Semântica: regras por fábrica. Procedural: fluxos (cotação→pedido→fatura→comissão). |
| **TOOLS** | Google Sheets (catálogo + CRM + comissões), Gmail (comunicação com fábricas/lojistas), Google Calendar (visitas), Telegram/WhatsApp (interface), Supabase (base de pedidos), Firecrawl/Apify (coleta de catálogos e precificação de mercado). TUDO já conectado — zero custo de API nova. |
| **PERMISSIONS** | Leitura/escrita apenas nas planilhas do escritório; envio de e-mail apenas de conta corporativa; sem acesso a dados bancários; sem exclusão de registros (somente arquivamento). Menor privilégio. |
| **CONSTRAINTS** | Não prometer prazo de fábrica; não inventar preço (usar tabela vigente); confirmar com humano antes de enviar proposta/proforma; operar em pt-BR. |
| **WORKFLOWS** | (1) Cadastro/atualização de catálogo; (2) cotação→pedido→follow-up→fatura→comissão; (3) conciliação mensal de comissões; (4) alerta de recompra por lojista; (5) geração de prestação de contas; (6) roteiro de visitas. |
| **TRIGGERS** | Mensagem de lojista/fábrica; pedido criado; fatura emitida; fim do mês (comissão); vencimento de recompra; pedido parado há X dias (escalar). |
| **HANDOFF RULES** | Lojista→FPOA→Felipe (decisão de preço/condição especial); FPOA→fábrica (confirmação de pedido via e-mail padrão); FPOA→Felipe em proposta fora da política. |
| **ESCALATION RULES** | Pedido parado >48h, divergência de comissão > R$ X, reclamação de lojista, tabela desatualizada → notificar Felipe via Telegram imediatamente. |
| **ERROR RECOVERY** | Falha de integração → re-tentar com backoff; dado não encontrado → declarar limitação (Reality Constraint) e pedir a fonte; divergência de preço → não chutar, escalar. |
| **OBSERVABILITY** | Log de pedidos por status; métricas: nº pedidos/mês, ticket médio, comissão a receber, tempo de follow-up, lojistas ativos. |
| **EVALUATION** | Precisão de preços informados (100% contra tabela), pedidos sem follow-up = 0, comissões conciliadas no prazo, satisfação de representadas (relatórios entregues). |
| **SECURITY** | Acesso por identidade (Telegram/WhatsApp do dono), escopo por planilha, auditoria de alterações, sem exposição de dados sensíveis em chat. |
| **SUCCESS METRICS** | Tempo de resposta a lojista < 5 min; comissão a receber rastreada 100%; relatório de prestação de contas em < 1 dia; recompra ativa com +15% de recorrência em 6 meses. |

---

## 7. CAMINHO DE IMPLEMENTAÇÃO (sem API paga)

1. **Planilha-base no Google Sheets** (já conectado): abas Catálogo, Lojistas (CRM), Pedidos, Comissões.
2. **Skill `fprime-ops`** no Hermes: implementa os 6 workflows com as ferramentas conectadas (Sheets, Gmail, Calendar, Telegram).
3. **Interface:** o agente vive no Telegram/WhatsApp do Felipe — ele conversa com o FPOA como com um assistente.
4. **Cron de rotina:** alerta diário de pedidos parados + comissões a vencer; relatório mensal automático.
5. **Evolução:** quando a operação crescer, o FPOA vira orquestrador de módulos (catálogo, comissão, CRM) — ainda 1 agente, não 10.

> **Reality Constraint:** esta spec descreve o agente em DESIGN. A implementação real (planilhas, skill, cron) é o próximo passo — posso executar sob comando do Senhor.