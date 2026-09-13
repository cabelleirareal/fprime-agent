"""FPOA — CRM de lojistas + recompra ativa."""
from __future__ import annotations

from datetime import date, timedelta

from .models import Lojista, Pedido


class CustomerCRM:
    def __init__(self, lojistas: dict[str, Lojista]) -> None:
        self._lojistas = lojistas

    def recomprar(self, pedidos: list[Pedido], dias: int = 45) -> list[Lojista]:
        """Lojistas sem compra há mais de `dias` (recompra ativa)."""
        hoje = date.today()
        ultima: dict[str, date] = {}
        for p in pedidos:
            if p.id_lojista not in ultima or p.data.date() > ultima[p.id_lojista]:
                ultima[p.id_lojista] = p.data.date()

        alvo: list[Lojista] = []
        for lj in self._lojistas.values():
            ult = ultima.get(lj.id_lojista)
            if ult is None or (hoje - ult).days > dias:
                alvo.append(lj)
        return sorted(alvo, key=lambda l: l.ticket_medio, reverse=True)

    def perfil(self, id_lojista: str) -> Lojista | None:
        return self._lojistas.get(id_lojista)

    def lojistas_ativos(self, pedidos: list[Pedido], dias: int = 90) -> list[Lojista]:
        """Lojistas com compra nos últimos `dias`."""
        hoje = date.today()
        ativos: set[str] = set()
        for p in pedidos:
            if (hoje - p.data.date()).days <= dias:
                ativos.add(p.id_lojista)
        return [lj for lj in self._lojistas.values() if lj.id_lojista in ativos]

    def segmentos(self) -> dict[str, int]:
        from collections import Counter

        return dict(Counter(lj.segmento for lj in self._lojistas.values()))