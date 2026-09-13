"""FPOA — Pipeline de pedidos: cotação → pedido → follow-up → faturamento → comissão."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from .catalog import Catalog
from .models import Fabrica, ItemPedido, Lojista, Pedido, StatusPedido


class OrderPipeline:
    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog
        self._pedidos: dict[str, Pedido] = {}
        self._lojistas: dict[str, Lojista] = {}
        self._proximo_id = 1

    # --- Lojistas ---
    def add_lojista(self, lojista: Lojista) -> None:
        self._lojistas[lojista.id_lojista] = lojista

    def get_lojista(self, id_lojista: str) -> Optional[Lojista]:
        return self._lojistas.get(id_lojista)

    def buscar_lojista(self, termo: str) -> Optional[Lojista]:
        t = termo.strip().lower()
        for lj in self._lojistas.values():
            if t in " ".join([lj.nome_loja, lj.contato, lj.cidade]).lower():
                return lj
        return None

    # --- Pedidos ---
    @property
    def pedidos(self) -> list[Pedido]:
        return sorted(self._pedidos.values(), key=lambda p: p.data, reverse=True)

    def get_pedido(self, id_pedido: str) -> Optional[Pedido]:
        return self._pedidos.get(id_pedido)

    def criar_pedido(
        self,
        id_lojista: str,
        id_fabrica: str,
        itens: list[ItemPedido],
    ) -> tuple[Pedido, Optional[str]]:
        """Cria pedido com valor_total + comissão prevista. Retorna (pedido, erro)."""
        fabrica = self.catalog.get_fabrica(id_fabrica)
        if fabrica is None:
            return None, "Fábrica não encontrada no catálogo."
        if not fabrica.ativo:
            return None, f"Fábrica {fabrica.nome_fantasia} está inativa."
        if self.get_lojista(id_lojista) is None:
            return None, "Lojista não encontrado no CRM."

        valor_total = sum(i.preco_unit * i.quantidade for i in itens)
        comissao = round(valor_total * fabrica.comissao_pct / 100.0, 2)

        pedido = Pedido(
            id_pedido=f"P{self._proximo_id:04d}",
            id_lojista=id_lojista,
            id_fabrica=id_fabrica,
            itens=itens,
            valor_total=valor_total,
            comissao_prevista=comissao,
        )
        self._proximo_id += 1
        pedido.registrar(
            f"Pedido criado: {len(itens)} itens, total R$ {valor_total:.2f}, "
            f"comissão R$ {comissao:.2f} ({fabrica.comissao_pct:.1f}%)"
        )
        self._pedidos[pedido.id_pedido] = pedido
        return pedido, None

    def transicionar(self, id_pedido: str, novo_status: StatusPedido, evento: str = "") -> Optional[str]:
        """Muda o status (nunca deleta). Retorna erro se transição inválida."""
        pedido = self.get_pedido(id_pedido)
        if pedido is None:
            return f"Pedido {id_pedido} não encontrado."
        if pedido.status in (StatusPedido.cancelado, StatusPedido.entregue):
            return f"Pedido já está em estado final ({pedido.status.value})."

        pedido.status = novo_status
        pedido.registrar(evento or f"Status → {novo_status.value}")
        return None

    def pedidos_parados(self, horas: int = 48) -> list[Pedido]:
        """Pedidos em `enviado` parados há mais de `horas` sem atualização."""
        agora = datetime.now()
        limite = timedelta(hours=horas)
        return [
            p
            for p in self._pedidos.values()
            if p.status == StatusPedido.enviado and (agora - p.data_atualizacao) > limite
        ]

    def pedidos_do_mes(self, mes: str) -> list[Pedido]:
        out = []
        for p in self._pedidos.values():
            if p.data.strftime("%Y-%m") == mes and p.status == StatusPedido.entregue:
                out.append(p)
        return out

    def resumo(self) -> dict:
        from collections import Counter

        por_status = Counter(p.status.value for p in self._pedidos.values())
        total = sum(p.valor_total for p in self._pedidos.values())
        comissao = sum(p.comissao_prevista for p in self._pedidos.values())
        return {
            "total_pedidos": len(self._pedidos),
            "por_status": dict(por_status),
            "valor_total": round(total, 2),
            "comissao_prevista_total": round(comissao, 2),
            "parados_48h": len(self.pedidos_parados()),
        }