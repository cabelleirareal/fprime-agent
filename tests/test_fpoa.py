"""Testes do FPOA — validam os workflows centrais."""
from datetime import datetime, timedelta

from fprime.agent import FPOA
from fprime.commissions import CommissionEngine
from fprime.crm import CustomerCRM
from fprime.models import (Comissao, Fabrica, ItemPedido, Lojista, Pedido,
                           Produto, StatusComissao, StatusPedido)
from fprime.orders import OrderPipeline


def _agente_seed() -> FPOA:
    a = FPOA()
    a.seed_exemplo()
    return a


# --- Catálogo ---
def test_preco_produto_existe():
    a = _agente_seed()
    resp = a.processar("Quanto é o conjunto moletom M da Malhas Prime?")
    assert "89.90" in resp
    assert "Malhas Prime" in resp


def test_preco_produto_inexistente_nao_chuta():
    a = _agente_seed()
    resp = a.processar("Quanto é o casaco de lã da Fábrica X?")
    assert "não encontrei" in resp.lower() or "não chuto" in resp.lower()


# --- Pedidos ---
def test_criar_pedido_calcula_comissao():
    a = _agente_seed()
    resp = a.processar("Anota pedido: Bela Moda, 30 conjuntos de moletom M a 89,90")
    assert "P0001" in resp
    assert "comissão 6.0%" in resp
    assert "2697.00" in resp  # 30 x 89,90


def test_pedido_lojista_inexistente_orienta():
    a = _agente_seed()
    resp = a.processar("Anota pedido: Loja Fantasma, 10 conjuntos de moletom M a 89,90")
    assert "não está no CRM" in resp


def test_pedido_produto_inexistente():
    a = _agente_seed()
    resp = a.processar("Anota pedido: Bela Moda, 10 unidades de casaco de lã a 50,00")
    assert "não encontrei" in resp.lower()


# --- Pipeline / transições ---
def test_transicionar_status_e_historico():
    a = _agente_seed()
    a.processar("Anota pedido: Bela Moda, 10 conjuntos de moletom M a 89,90")
    p = a.orders.get_pedido("P0001")
    assert p is not None
    assert p.status == StatusPedido.orcamento
    err = a.orders.transicionar("P0001", StatusPedido.enviado, "Enviado à fábrica")
    assert err is None
    assert p.status == StatusPedido.enviado
    assert any("Enviado à fábrica" in h for h in p.historico)


def test_estado_final_bloqueia_transicao():
    a = _agente_seed()
    a.processar("Anota pedido: Bela Moda, 5 conjuntos de moletom M a 89,90")
    a.orders.transicionar("P0001", StatusPedido.cancelado)
    err = a.orders.transicionar("P0001", StatusPedido.enviado)
    assert err is not None


# --- Comissões ---
def test_conciliacao_comissao_por_fabrica():
    a = _agente_seed()
    a.processar("Anota pedido: Bela Moda, 30 conjuntos de moletom M a 89,90")  # 2697.00, 6% = 161.82
    a.orders.transicionar("P0001", StatusPedido.entregue)
    mes = datetime.now().strftime("%Y-%m")
    entregues = a.orders.pedidos_do_mes(mes)
    comissoes = a.commissions.conciliar(mes, entregues)
    assert len(comissoes) == 1
    c = comissoes[0]
    assert c.id_fabrica == "F001"
    assert abs(c.comissao_devida - 161.82) < 0.01


def test_divergencia_marcada_nao_auto_resolve():
    a = _agente_seed()
    a.processar("Anota pedido: Bela Moda, 10 conjuntos de moletom M a 89,90")
    a.orders.transicionar("P0001", StatusPedido.entregue)
    mes = datetime.now().strftime("%Y-%m")
    a.commissions.conciliar(mes, a.orders.pedidos_do_mes(mes))
    err = a.commissions.marcar_divergencia(mes, "F001", "Fábrica reportou valor menor")
    assert err is None
    assert len(a.commissions.divergencias()) == 1


# --- CRM / recompra ---
def test_recompra_lista_lojistas_parados():
    a = _agente_seed()
    # nenhuma compra registrada → ambos parados
    alvo = a.crm.recomprar(a.orders.pedidos, dias=45)
    assert len(alvo) == 2


# --- Relatório ---
def test_relatorio_prestacao_contas():
    a = _agente_seed()
    a.processar("Anota pedido: Bela Moda, 30 conjuntos de moletom M a 89,90")
    a.orders.transicionar("P0001", StatusPedido.entregue)
    rel = a.reporting.prestacao_contas("F001", a.orders.pedidos)
    assert rel["periodo_pedidos"] == 1
    assert abs(rel["volume_total"] - 2697.00) < 0.01
    assert abs(rel["comissao_total"] - 161.82) < 0.01


# --- Roteiro ---
def test_roteiro_agrupa_por_cidade():
    a = _agente_seed()
    roteiro = a.routing.montar_roteiro()
    assert len(roteiro) >= 2  # São Paulo + Guarulhos
    cidades = {g["cidade"] for g in roteiro}
    assert "São Paulo" in cidades
    assert "Guarulhos" in cidades