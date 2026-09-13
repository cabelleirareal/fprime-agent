"""FPOA — Modelos de dados do agente F.PRIME Operations."""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class StatusPedido(str, Enum):
    orcamento = "orcamento"
    enviado = "enviado"
    confirmado = "confirmado"
    faturado = "faturado"
    entregue = "entregue"
    cancelado = "cancelado"


class StatusComissao(str, Enum):
    a_receber = "a-receber"
    recebido = "recebido"
    divergencia = "divergencia"


class Fabrica(BaseModel):
    id_fabrica: str
    razao_social: str
    nome_fantasia: str = ""
    contato: str = ""
    email: str = ""
    whatsapp: str = ""
    linha: str = ""
    condicoes: str = ""
    comissao_pct: float = Field(default=5.0, ge=0, le=30)
    prazo_entrega_dias: int = Field(default=30, ge=0)
    tabela_link: str = ""
    status: str = "ativo"  # ativo | inativo

    @property
    def ativo(self) -> bool:
        return self.status == "ativo"


class Produto(BaseModel):
    id_produto: str
    id_fabrica: str
    sku_fabrica: str
    nome: str
    categoria: str = ""
    colecao: str = ""
    preco_unit: float = Field(ge=0)
    preco_min: float = Field(default=0, ge=0)
    disponibilidade: str = "estoque"  # estoque | sob-consulta
    foto_url: str = ""
    atualizado_em: Optional[date] = None


class Lojista(BaseModel):
    id_lojista: str
    nome_loja: str
    contato: str = ""
    cidade: str = ""
    uf: str = ""
    segmento: str = ""
    ticket_medio: float = Field(default=0, ge=0)
    whatsapp: str = ""
    email: str = ""
    ultima_compra: Optional[date] = None
    frequencia_dias: int = Field(default=0, ge=0)
    tags: str = ""
    anotacoes: str = ""


class ItemPedido(BaseModel):
    sku_fabrica: str
    quantidade: int = Field(ge=1)
    preco_unit: float = Field(ge=0)


class Pedido(BaseModel):
    id_pedido: str
    data: datetime = Field(default_factory=datetime.now)
    id_lojista: str
    id_fabrica: str
    itens: list[ItemPedido]
    valor_total: float = Field(ge=0)
    status: StatusPedido = StatusPedido.orcamento
    comissao_prevista: float = Field(default=0, ge=0)
    historico: list[str] = Field(default_factory=list)
    data_atualizacao: datetime = Field(default_factory=datetime.now)

    def registrar(self, evento: str) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.historico.append(f"[{ts}] {evento}")
        self.data_atualizacao = datetime.now()


class Comissao(BaseModel):
    mes: str  # AAAA-MM
    id_fabrica: str
    valor_vendido: float = Field(ge=0)
    comissao_devida: float = Field(ge=0)
    status: StatusComissao = StatusComissao.a_receber
    data_pagamento: Optional[date] = None
    observacao: str = ""


class Visita(BaseModel):
    data: date
    id_lojista: str
    cidade: str = ""
    objetivo: str = ""
    resultado: str = ""
    proximo_passo: str = ""