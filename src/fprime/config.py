"""FPOA — Configuração via .env / variáveis de ambiente (credenciais do cliente)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Google Sheets (conta do CLIENTE)
    sheets_credentials_file: str = field(
        default_factory=lambda: os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials/sheets_client.json")
    )
    spreadsheet_id: str = field(default_factory=lambda: os.getenv("FPRIME_SPREADSHEET_ID", ""))

    # Gmail (conta do CLIENTE)
    gmail_credentials_file: str = field(
        default_factory=lambda: os.getenv("GMAIL_CREDENTIALS_FILE", "credentials/gmail_client.json")
    )
    gmail_sender: str = field(default_factory=lambda: os.getenv("GMAIL_SENDER", ""))

    # Telegram (interface do operador)
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_allowed_user_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_ALLOWED_USER_ID", ""))

    # Regras de negócio (padrões ajustáveis)
    default_comissao_pct: float = field(
        default_factory=lambda: float(os.getenv("DEFAULT_COMISSAO_PCT", "5.0"))
    )
    followup_horas: int = field(default_factory=lambda: int(os.getenv("FOLLOWUP_HORAS", "48")))
    recomprar_dias: int = field(default_factory=lambda: int(os.getenv("RECOMPRA_DIAS", "45")))
    divergencia_limite_real: float = field(
        default_factory=lambda: float(os.getenv("DIVERGENCIA_LIMITE_REAL", "100.0"))
    )
    fabrica_inativa_dias: int = field(default_factory=lambda: int(os.getenv("FABRICA_INATIVA_DIAS", "90")))

    @property
    def credentials_dir(self) -> Path:
        return Path("credentials")

    def validar(self) -> list[str]:
        """Retorna lista de avisos de configuração ausente (não bloqueia)."""
        avisos: list[str] = []
        if not self.spreadsheet_id:
            avisos.append("FPRIME_SPREADSHEET_ID não definido — consulta a catálogo offline")
        if not self.telegram_bot_token:
            avisos.append("TELEGRAM_BOT_TOKEN não definido — interface via CLI apenas")
        return avisos