"""FPOA — Conciliação mensal de comissões por fábrica."""
from __future__ import annotations

from collections import defaultdict
from datetime import date

from .catalog import Catalog
from .models import Comissao, Fabrica, Pedido, StatusComissao


class CommissionEngine:
    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog
        self._comissoes: dict[tuple[str, str], Comissao] = {}  # (mes, id_fabrica)

    def conciliar(self, mes: str, pedidos: list[Pedido]) -> list[Comissao]:
        """Agrupa pedidos entregues por fábrica e calcula comissão devida."""
        por_fabrica: dict[str, float] = defaultdict(float)
        for p in pedidos:
            por_fabrica[p.id_fabrica] += p.valor_total

        resultado: list[Comissao] = []
        for id_fabrica, valor_vendido in por_fabrica.items():
            fabrica = self.catalog.get_fabrica(id_fabrica)
            if fabrica is None:
                continue
            devida = round(valor_vendido * fabrica.comissao_pct / 100.0, 2)
            comissao = Comissao(
                mes=mes,
                id_fabrica=id_fabrica,
                valor_vendido=round(valor_vendido, 2),
                comissao_devida=devida,
            )
            self._comissoes[(mes, id_fabrica)] = comissao
            resultado.append(comissao)
        return resultado

    def marcar_divergencia(self, mes: str, id_fabrica: str, observacao: str) -> Optional[str]:
        key = (mes, id_fabrica)
        if key not in self._comissoes:
            return f"Comissão de {id_fabrica} em {mes} não encontrada."
        self._comissoes[key].status = StatusComissao.divergencia
        self._comissoes[key].observacao = observacao
        return None

    def registrar_recebimento(self, mes: str, id_fabrica: str, data: date) -> Optional[str]:
        key = (mes, id_fabrica)
        if key not in self._comissoes:
            return f"Comissão de {id_fabrica} em {mes} não encontrada."
        self._comissoes[key].status = StatusComissao.recebido
        self._comissoes[key].data_pagamento = data
        return None

    def total_a_receber(self) -> float:
        return round(
            sum(
                c.comissao_devida
                for c in self._comissoes.values()
                if c.status == StatusComissao.a_receber
            ),
            2,
        )

    def resumo_mes(self, mes: str) -> list[Comissao]:
        return [c for (m, _), c in sorted(self._comissoes.items()) if m == mes]

    def divergencias(self) -> list[Comissao]:
        return [c for c in self._comissoes.values() if c.status == StatusComissao.divergencia]