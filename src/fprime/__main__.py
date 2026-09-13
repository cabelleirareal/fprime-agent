"""FPOA — CLI: python -m fprime 'comando em linguagem natural'."""
from __future__ import annotations

import sys

from .agent import FPOA


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python -m fprime '<comando>'")
        print("Ex.: python -m fprime 'Quanto é o conjunto M da Malhas Prime?'")
        return 2

    comando = " ".join(sys.argv[1:])
    agente = FPOA()
    agente.seed_exemplo()  # em produção: carregar do Sheets/config
    resposta = agente.processar(comando)
    print(resposta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())