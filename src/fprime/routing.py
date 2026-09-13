"""FPOA — Roteiro de visitas por região (agrupa lojistas por cidade/bairro)."""
from __future__ import annotations

from collections import defaultdict, OrderedDict

from .models import Lojista, Visita


class RoutePlanner:
    def __init__(self, lojistas: dict[str, Lojista]) -> None:
        self._lojistas = lojistas

    def montar_roteiro(self, cidade: str = "", uf: str = "") -> list[dict]:
        """Agrupa lojistas por cidade, ordena por ticket médio. Sem mapa físico (v1)."""
        grupos: dict[str, list[Lojista]] = defaultdict(list)
        for lj in self._lojistas.values():
            if cidade and lj.cidade.lower() != cidade.lower():
                continue
            if uf and lj.uf.upper() != uf.upper():
                continue
            grupos[lj.cidade].append(lj)

        roteiro = []
        for cidade_nome, lojistas in sorted(grupos.items()):
            ordenados = sorted(lojistas, key=lambda l: l.ticket_medio, reverse=True)
            roteiro.append(
                {
                    "cidade": cidade_nome,
                    "uf": ordenados[0].uf if ordenados else "",
                    "lojistas": [
                        {
                            "loja": l.nome_loja,
                            "contato": l.contato,
                            "whatsapp": l.whatsapp,
                            "ticket_medio": l.ticket_medio,
                            "segmento": l.segmento,
                        }
                        for l in ordenados
                    ],
                    "total_lojistas": len(ordenados),
                }
            )
        return roteiro

    def formatar_roteiro(self, roteiro: list[dict]) -> str:
        if not roteiro:
            return "Nenhum lojista encontrado para a região."
        linhas = ["Roteiro de visitas:"]
        for grupo in roteiro:
            linhas.append(f"\n📍 {grupo['cidade']}/{grupo['uf']} ({grupo['total_lojistas']} lojistas):")
            for lj in grupo["lojistas"]:
                linhas.append(
                    f"  - {lj['loja']} — {lj['contato']} — {lj['whatsapp']} — "
                    f"ticket R$ {lj['ticket_medio']:.2f} ({lj['segmento']})"
                )
        return "\n".join(linhas)