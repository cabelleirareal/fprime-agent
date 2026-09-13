"""FPOA — Adaptador de interface (Telegram/WhatsApp/CLI) para o agente."""
from __future__ import annotations

import os
from typing import Callable


class ChatAdapter:
    """Envia mensagens para o operador. v1: stdout; pode trocar por Telegram/WhatsApp."""

    def __init__(self, send: Callable[[str], None] = print) -> None:
        self._send = send

    def enviar(self, msg: str) -> None:
        self._send(msg)


def adaptador_telegram(token: str, allowed_user_id: str) -> ChatAdapter:
    """Cria adaptador Telegram (requer python-telegram-bot instalado pelo cliente)."""
    if not token or not allowed_user_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN e TELEGRAM_ALLOWED_USER_ID são obrigatórios para Telegram.")

    try:
        from telegram import Bot
        from telegram.error import TelegramError
    except ImportError:
        raise RuntimeError("Instale python-telegram-bot para usar o adaptador Telegram.")

    bot = Bot(token=token)

    def send(msg: str) -> None:
        try:
            bot.send_message(chat_id=allowed_user_id, text=msg)
        except TelegramError as e:
            print(f"[telegram] erro ao enviar: {e}")

    return ChatAdapter(send=send)