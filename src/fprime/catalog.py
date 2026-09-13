"""FPOA — Catálogo unificado (fábricas × produtos) com consulta de preço."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from .models import Fabrica, Produto


class Catalog:
    """Catálogo em memória (a implementação de persistência fica no adaptador do cliente)."""

    def __init__(self) -> None:
        self._fabricas: dict[str, Fabrica] = {}
        self._produtos: dict[str, Produto] = {}

    # --- Fábricas ---
    def add_fabrica(self, fabrica: Fabrica) -> None:
        self._fabricas[fabrica.id_fabrica] = fabrica

    def get_fabrica(self, id_fabrica: str) -> Optional[Fabrica]:
        return self._fabricas.get(id_fabrica)

    def fabricas_ativas(self) -> list[Fabrica]:
        return [f for f in self._fabricas.values() if f.ativo]

    def fabricas_inativas(self, dias: int = 90) -> list[tuple[Fabrica, int]]:
        """Fábricas com tabela desatualizada (sem atualização há `dias`)."""
        hoje = date.today()
        out: list[tuple[Fabrica, int]] = []
        for f in self._fabricas.values():
            if not f.ativo:
                continue
            atualizado = max(
                (p.atualizado_em for p in self._produtos.values() if p.id_fabrica == f.id_fabrica),
                default=None,
            )
            if atualizado is None:
                continue
            idade = (hoje - atualizado).days
            if idade > dias:
                out.append((f, idade))
        return out

    # --- Produtos ---
    def add_produto(self, produto: Produto) -> None:
        produto.atualizado_em = date.today()
        self._produtos[produto.id_produto] = produto

    def get_produto(self, id_produto: str) -> Optional[Produto]:
        return self._produtos.get(id_produto)

    def buscar(self, termo: str) -> list[tuple[Produto, Fabrica]]:
        """Busca por nome/categoria/coleção/fábrica (case-insensitive, token match).

        Extrai tokens (palavras ≥3 chars, ignorando stopwords comuns) e retorna
        produtos cujo texto contenha TODOS os tokens do termo.
        """
        import re as _re

        _STOP = {"quanto", "que", "para", "com", "por", "uma", "um", "dos", "das",
                 "tem", "ser", "está", "esta", "sao", "são", "não", "nao"}

        tokens = [
            w for w in _re.findall(r"[a-zà-ú0-9]+", termo.lower())
            if len(w) >= 3 and w not in _STOP
        ]
        if not tokens:
            return []

        out: list[tuple[Produto, Fabrica]] = []
        for p in self._produtos.values():
            f = self._fabricas.get(p.id_fabrica)
            if f is None or not f.ativo:
                continue
            alvo = " ".join(
                [p.nome, p.categoria, p.colecao, f.nome_fantasia, f.razao_social]
            ).lower()
            if all(tok in alvo for tok in tokens):
                out.append((p, f))
        return out

    def precificar(self, termo: str) -> Optional[tuple[Produto, Fabrica]]:
        """Retorna o produto + fábrica para um termo; None se não encontrado (Reality Constraint)."""
        hits = self.buscar(termo)
        if not hits:
            return None
        return hits[0]

    def produtos_da_fabrica(self, id_fabrica: str) -> list[Produto]:
        return [p for p in self._produtos.values() if p.id_fabrica == id_fabrica]