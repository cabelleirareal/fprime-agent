"""FPOA — Intérprete de comandos em linguagem natural (interface do Felipe)."""
from __future__ import annotations

import re
from datetime import date, datetime
from typing import Optional

from .catalog import Catalog
from .commissions import CommissionEngine
from .crm import CustomerCRM
from .models import Fabrica, ItemPedido, Lojista, Produto, StatusComissao, StatusPedido
from .orders import OrderPipeline
from .reporting import Reporting
from .routing import RoutePlanner


class FPOA:
    """O agente: recebe texto, executa workflow, devolve resposta. Sempre honesto (Reality Constraint)."""

    def __init__(self) -> None:
        self.catalog = Catalog()
        self.orders = OrderPipeline(self.catalog)
        self.commissions = CommissionEngine(self.catalog)
        self.crm = CustomerCRM(self.orders._lojistas)
        self.reporting = Reporting(self.catalog, self.orders._lojistas)
        self.routing = RoutePlanner(self.orders._lojistas)

    # ---------- seed (dados de exemplo para teste; em produção vem do Sheets) ----------
    def seed_exemplo(self) -> None:
        f1 = Fabrica(id_fabrica="F001", razao_social="MALHAS PRIME LTDA", nome_fantasia="Malhas Prime",
                     linha="moletom", comissao_pct=6.0, status="ativo")
        f2 = Fabrica(id_fabrica="F002", razao_social="TECIDOS BELLA LTDA", nome_fantasia="Bella Tecidos",
                     linha="malha fina", comissao_pct=5.0, status="ativo")
        self.catalog.add_fabrica(f1)
        self.catalog.add_fabrica(f2)
        self.catalog.add_produto(Produto(id_produto="P01", id_fabrica="F001", sku_fabrica="ML-001",
                                         nome="Conjunto Moletom M", categoria="moletom", colecao="2026-2",
                                         preco_unit=89.90, preco_min=79.90, disponibilidade="estoque"))
        self.catalog.add_produto(Produto(id_produto="P02", id_fabrica="F001", sku_fabrica="ML-002",
                                         nome="Conjunto Moletom G", categoria="moletom", colecao="2026-2",
                                         preco_unit=94.90, preco_min=84.90, disponibilidade="estoque"))
        self.catalog.add_produto(Produto(id_produto="P03", id_fabrica="F002", sku_fabrica="BT-100",
                                         nome="Vestido Malha Fina", categoria="vestido", colecao="2026-2",
                                         preco_unit=59.90, preco_min=49.90, disponibilidade="sob-consulta"))
        self.orders.add_lojista(Lojista(id_lojista="L001", nome_loja="Bela Moda", contato="Maria",
                                        cidade="São Paulo", uf="SP", segmento="moda-feminina",
                                        ticket_medio=2500, whatsapp="11999990000"))
        self.orders.add_lojista(Lojista(id_lojista="L002", nome_loja="Casa da Moda", contato="João",
                                        cidade="Guarulhos", uf="SP", segmento="moda-masculina",
                                        ticket_medio=1500, whatsapp="11988880000"))

    # ---------- dispatch ----------
    def processar(self, texto: str) -> str:
        t = texto.strip().lower()
        if not t:
            return "Diga o que precisa: preço, pedido, status, comissão, relatório, roteiro."
        if "quanto" in t or "preço" in t or "preco" in t or "valor" in t:
            return self._cmd_preco(t)
        if t.startswith("anota pedido") or "pedido:" in t or "anota:" in t:
            return self._cmd_pedido(texto)
        if "status" in t and "#" in t:
            return self._cmd_status(texto)
        if "fechou comiss" in t or "comissão de" in t or "comissao de" in t:
            return self._cmd_comissao(t)
        if "não compra" in t or "nao compra" in t or "recompra" in t or "sem compra" in t:
            return self._cmd_recompra(t)
        if "relatório" in t or "relatorio" in t:
            return self._cmd_relatorio(t)
        if "roteiro" in t:
            return self._cmd_roteiro(t)
        if "travad" in t or "parado" in t:
            return self._cmd_travados()
        if "cadastra" in t or "cadastr" in t:
            return self._cmd_cadastro(texto)
        if "resumo" in t:
            return self._cmd_resumo()
        return self._fallback()

    # ---------- comandos ----------
    def _cmd_preco(self, t: str) -> str:
        # Buscar primeiro pelo nome do produto completo (sem remover letras soltas)
        hits = self.catalog.buscar(t)
        if hits:
            p, f = hits[0]
            disp = "em estoque" if p.disponibilidade == "estoque" else "sob consulta"
            return (f"{p.nome} ({f.nome_fantasia}): R$ {p.preco_unit:.2f} "
                    f"(mín. R$ {p.preco_min:.2f}) — {disp}. Prazo: {f.prazo_entrega_dias}d.")
        # Fallback: filtrar por fábrica e buscar só o produto
        for fab in self.catalog.fabricas_ativas():
            if fab.nome_fantasia.lower() in t:
                resto = t.replace(fab.nome_fantasia.lower(), "").strip()
                hits_fab = self.catalog.buscar(resto)
                # restringe aos produtos da fábrica
                hits_fab = [(p, f) for (p, f) in hits_fab if p.id_fabrica == fab.id_fabrica]
                if hits_fab:
                    p, f = hits_fab[0]
                    disp = "em estoque" if p.disponibilidade == "estoque" else "sob consulta"
                    return (f"{p.nome} ({f.nome_fantasia}): R$ {p.preco_unit:.2f} "
                            f"(mín. R$ {p.preco_min:.2f}) — {disp}. Prazo: {f.prazo_entrega_dias}d.")
        return "Não encontrei esse produto no catálogo. Pode me mandar a tabela da fábrica? (não chuto preço)"

    def _cmd_pedido(self, texto: str) -> str:
        # Padrão: "Anota pedido: LOJA, QTD UNIDADES a PRECO" ou "LOJA, QTDx PRODUTO a PRECO"
        m = re.search(r"anota pedido:?\s*(.+?),\s*(\d+)\s*(?:unidades|und|conjuntos|conjunto)?\s*(?:de\s+)?(.+?)\s*a\s*(?:R\$\s*)?([\d.,]+)", texto, re.I)
        if not m:
            return "Não entendi o pedido. Formato: 'Anota pedido: Loja, 30 conjuntos de <produto> a 89,90'"
        loja_termo, qtd, produto_termo, preco_str = m.groups()
        lojista = self.orders.buscar_lojista(loja_termo.strip())
        if lojista is None:
            return f"Lojista '{loja_termo.strip()}' não está no CRM. Cadastra primeiro: 'Cadastra loja X, contato Y, cidade Z'"
        preco = float(preco_str.replace(".", "").replace(",", "."))
        hit = self.catalog.precificar(produto_termo.strip())
        if hit is None:
            return f"Não encontrei '{produto_termo.strip()}' no catálogo. Confere o nome?"
        produto, fabrica = hit
        item = ItemPedido(sku_fabrica=produto.sku_fabrica, quantidade=int(qtd), preco_unit=preco)
        pedido, erro = self.orders.criar_pedido(lojista.id_lojista, fabrica.id_fabrica, [item])
        if erro:
            return f"Não consegui criar o pedido: {erro}"
        return (f"✅ Pedido {pedido.id_pedido} criado: {produto.nome} x{qtd} — "
                f"R$ {pedido.valor_total:.2f} | comissão {fabrica.comissao_pct:.1f}% = R$ {pedido.comissao_prevista:.2f} | "
                f"lojista {lojista.nome_loja} | status: orçamento")

    def _cmd_status(self, texto: str) -> str:
        m = re.search(r"#(\w+)", texto)
        if not m:
            return "Qual pedido? Ex: 'Status do #P0001'"
        pedido = self.orders.get_pedido(m.group(1).upper())
        if pedido is None:
            return f"Pedido {m.group(1)} não encontrado."
        lojista = self.orders.get_lojista(pedido.id_lojista)
        fabrica = self.catalog.get_fabrica(pedido.id_fabrica)
        linhas = [
            f"Pedido {pedido.id_pedido} — {pedido.status.value}",
            f"Loja: {lojista.nome_loja if lojista else pedido.id_lojista} | Fábrica: {fabrica.nome_fantasia if fabrica else pedido.id_fabrica}",
            f"Total: R$ {pedido.valor_total:.2f} | Comissão: R$ {pedido.comissao_prevista:.2f}",
        ]
        if pedido.historico:
            linhas.append("Histórico:")
            linhas += [f"  - {h}" for h in pedido.historico[-5:]]
        return "\n".join(linhas)

    def _cmd_comissao(self, t: str) -> str:
        # "Fechou comissão de agosto" → mês anterior; aceita "AAAA-MM"
        m = re.search(r"(\d{4}-\d{2})", t)
        if m:
            mes = m.group(1)
        else:
            agora = datetime.now()
            mes = (agora.replace(day=1) - __import__("datetime").timedelta(days=1)).strftime("%Y-%m")
        entregues = self.orders.pedidos_do_mes(mes)
        comissoes = self.commissions.conciliar(mes, entregues)
        if not comissoes:
            return f"Nenhum pedido entregue em {mes} para conciliar."
        total = sum(c.comissao_devida for c in comissoes)
        linhas = [f"Comissões de {mes}: total R$ {total:.2f}"]
        for c in comissoes:
            fab = self.catalog.get_fabrica(c.id_fabrica)
            linhas.append(f"  - {fab.nome_fantasia if fab else c.id_fabrica}: vendido R$ {c.valor_vendido:.2f} → comissão R$ {c.comissao_devida:.2f} ({c.status.value})")
        return "\n".join(linhas)

    def _cmd_recompra(self, t: str) -> str:
        dias = 45
        m = re.search(r"(\d+)\s*(?:dias|d)", t)
        if m:
            dias = int(m.group(1))
        alvo = self.crm.recomprar(self.orders.pedidos, dias=dias)
        if not alvo:
            return f"Nenhum lojista parado há mais de {dias} dias. 🎉"
        linhas = [f"Lojistas sem compra há {dias}+ dias ({len(alvo)}):"]
        for lj in alvo:
            linhas.append(f"  - {lj.nome_loja} ({lj.cidade}/{lj.uf}) — ticket R$ {lj.ticket_medio:.2f} — {lj.contato} {lj.whatsapp}")
        return "\n".join(linhas)

    def _cmd_relatorio(self, t: str) -> str:
        # ex.: "Relatório da Malhas Prime"
        for fab in self.catalog.fabricas_ativas():
            if fab.nome_fantasia.lower() in t:
                rel = self.reporting.prestacao_contas(fab.id_fabrica, self.orders.pedidos)
                return self.reporting.formatar_relatorio(rel)
        return "De qual fábrica? Ex: 'Relatório da Malhas Prime'"

    def _cmd_roteiro(self, t: str) -> str:
        cidade = ""
        m = re.search(r"de\s+([A-Za-zÀ-ú\s]+)", t)
        if m:
            cidade = m.group(1).strip().title()
        roteiro = self.routing.montar_roteiro(cidade=cidade)
        return self.routing.formatar_roteiro(roteiro)

    def _cmd_travados(self) -> str:
        parados = self.orders.pedidos_parados(horas=48)
        if not parados:
            return "Nenhum pedido parado há 48h+. 👍"
        linhas = [f"Pedidos parados >48h ({len(parados)}):"]
        for p in parados:
            fab = self.catalog.get_fabrica(p.id_fabrica)
            linhas.append(f"  - {p.id_pedido} — {fab.nome_fantasia if fab else p.id_fabrica} — parado desde {p.data_atualizacao:%d/%m %H:%M}")
        return "\n".join(linhas)

    def _cmd_cadastro(self, texto: str) -> str:
        # Simples: "Cadastra a <nome>, linha <linha>, comissão <pct>%"
        m = re.search(r"cadastra\s+(?:a\s+|o\s+)?(.+?)(?:,|\s*linha\s+(.+?))?(?:,|\s*comissão\s+([\d.]+)\s*%)?", texto, re.I)
        if not m:
            return "Formato: 'Cadastra a Malhas Prime, linha moletom, comissão 6%'"
        nome = m.group(1).strip().title()
        id_fab = "F" + str(len(self.catalog.fabricas_ativas()) + 1).zfill(3)
        pct = float((m.group(3) or "5").replace(",", "."))
        fab = Fabrica(id_fabrica=id_fab, razao_social=nome.upper(), nome_fantasia=nome,
                      linha=m.group(2).strip() if m.group(2) else "", comissao_pct=pct, status="ativo")
        self.catalog.add_fabrica(fab)
        return f"✅ Fábrica cadastrada: {nome} (ID {id_fab}), linha '{fab.linha}', comissão {pct:.1f}%. Agora é só mandar a tabela de produtos (foto/PDF) para eu cadastrar o catálogo."

    def _cmd_resumo(self) -> str:
        r = self.orders.resumo()
        comissao = self.commissions.total_a_receber()
        return (f"Resumo: {r['total_pedidos']} pedidos ({r['por_status']}) | "
                f"valor R$ {r['valor_total']:.2f} | comissão prevista R$ {r['comissao_prevista_total']:.2f} | "
                f"a receber R$ {comissao:.2f} | parados 48h: {r['parados_48h']}")

    def _fallback(self) -> str:
        return ("Entendi o pedido? Ainda não. Posso: preço, pedido, status, comissão, recompra, "
                "relatório, roteiro, travados, cadastro, resumo. Ex: 'Quanto é o conjunto M da Malhas Prime?'")