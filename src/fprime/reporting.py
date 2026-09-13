"""FPOA — Prestação de contas por representada."""
from __future__ import annotations

from collections import defaultdict

from .catalog import Catalog
from .models import Pedido


class Reporting:
    def __init__(self, catalog: Catalog, lojistas: dict) -> None:
        self.catalog = catalog
        self._lojistas = lojistas

    def prestacao_contas(self, id_fabrica: str, pedidos: list[Pedido]) -> dict:
        """Relatório por fábrica: clientes novos, pedidos, volume, comissão."""
        fabrica = self.catalog.get_fabrica(id_fabrica)
        if fabrica is None:
            return {"erro": f"Fábrica {id_fabrica} não encontrada."}

        pedidos_fab = [p for p in pedidos if p.id_fabrica == id_fabrica]
        por_lojista: dict[str, list[Pedido]] = defaultdict(list)
        for p in pedidos_fab:
            por_lojista[p.id_lojista].append(p)

        lojistas_ativos: set[str] = set()
        for p in pedidos:
            lojistas_ativos.add(p.id_lojista)

        clientes = []
        for id_lojista, ps in por_lojista.items():
            lj = self._lojistas.get(id_lojista)
            clientes.append(
                {
                    "lojista": lj.nome_loja if lj else id_lojista,
                    "cidade": lj.cidade if lj else "",
                    "pedidos": len(ps),
                    "volume": round(sum(p.valor_total for p in ps), 2),
                    "novo": id_lojista not in lojistas_ativos,
                }
            )

        return {
            "fabrica": fabrica.nome_fantasia,
            "periodo_pedidos": len(pedidos_fab),
            "volume_total": round(sum(p.valor_total for p in pedidos_fab), 2),
            "comissao_total": round(sum(p.comissao_prevista for p in pedidos_fab), 2),
            "clientes": sorted(clientes, key=lambda c: c["volume"], reverse=True),
            "clientes_novos": sum(1 for c in clientes if c["novo"]),
        }

    def formatar_relatorio(self, relatorio: dict) -> str:
        if "erro" in relatorio:
            return relatorio["erro"]
        linhas = [
            f"Relatório — {relatorio['fabrica']}",
            f"Pedidos: {relatorio['periodo_pedidos']} | Volume: R$ {relatorio['volume_total']:.2f} | "
            f"Comissão: R$ {relatorio['comissao_total']:.2f} | Clientes novos: {relatorio['clientes_novos']}",
        ]
        for c in relatorio["clientes"]:
            novo = " [NOVO]" if c["novo"] else ""
            linhas.append(
                f"  - {c['lojista']} ({c['cidade']}): {c['pedidos']} pedidos, R$ {c['volume']:.2f}{novo}"
            )
        return "\n".join(linhas)