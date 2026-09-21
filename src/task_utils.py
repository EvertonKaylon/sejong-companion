"""Utilitário para despacho de tarefas assíncronas em segundo plano desacopladas."""

import asyncio
from typing import Any, Coroutine, Optional


def fire_and_forget(coro: Coroutine, page: Optional[Any] = None) -> Optional[asyncio.Task]:
    """Despacha uma corrotina assíncrona em segundo plano de forma resiliente.

    Tenta utilizar `page.run_task` se o objeto `page` for fornecido e possuir o método;
    caso contrário, despacha no loop de eventos assíncrono atual (`asyncio.get_running_loop()`).
    Em ambientes de teste unitário síncronos sem loop ativo, captura `RuntimeError`
    graciosamente sem propagar exceção.
    """
    if page is not None and hasattr(page, "run_task") and callable(page.run_task):
        try:
            return page.run_task(lambda: coro)
        except Exception:
            pass

    try:
        loop = asyncio.get_running_loop()
        return loop.create_task(coro)
    except RuntimeError:
        # Nenhum event loop assíncrono ativo no contexto atual (ex: execução headless síncrona)
        return None


class TaskUtils:
    """Classe utilitária para gerenciamento de tarefas assíncronas."""

    @staticmethod
    def fire_and_forget(coro: Coroutine, page: Optional[Any] = None) -> Optional[asyncio.Task]:
        """Atalho estático para fire_and_forget."""
        return fire_and_forget(coro, page)
