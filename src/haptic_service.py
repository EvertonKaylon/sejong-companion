"""Serviço centralizado de Feedback Háptico e Sensorial do Saebom Companion.

Gerencia vibrações, toques sutis (snap feedback), impactos fonéticos (consoantes tensas)
e comemorações multissensoriais utilizando ft.HapticFeedback do Flutter Engine.
Possui tolerância total para execução em ambientes headless/testes sem página ativa.
"""

import asyncio
from typing import Optional
import flet as ft


class HapticService:
    """Gerenciador de feedback tátil e vibrações fonotáticas do aplicativo."""

    def __init__(self, page: Optional[ft.Page] = None):
        self.page = page
        self.haptic: Optional[ft.HapticFeedback] = None

        if page is not None:
            self.haptic = ft.HapticFeedback()
            if hasattr(page, "services"):
                if page.services is None:
                    page.services = []
                page.services.append(self.haptic)
            elif hasattr(page, "overlay"):
                page.overlay.append(self.haptic)

    async def light_impact(self):
        """Executa impacto leve no dispositivo."""
        if self.haptic and hasattr(self.haptic, "light_impact"):
            try:
                res = self.haptic.light_impact()
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass

    async def medium_impact(self):
        """Executa impacto médio no dispositivo."""
        if self.haptic and hasattr(self.haptic, "medium_impact"):
            try:
                res = self.haptic.medium_impact()
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass

    async def heavy_impact(self):
        """Executa impacto pesado no dispositivo."""
        if self.haptic and hasattr(self.haptic, "heavy_impact"):
            try:
                res = self.haptic.heavy_impact()
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass

    async def selection_click(self):
        """Executa clique sutil de seleção/hover no dispositivo."""
        if self.haptic and hasattr(self.haptic, "selection_click"):
            try:
                res = self.haptic.selection_click()
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass

    async def vibrate(self):
        """Vibração padrão do sistema."""
        if self.haptic and hasattr(self.haptic, "vibrate"):
            try:
                res = self.haptic.vibrate()
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass

    async def snap_success(self):
        """Feedback háptico para encaixe correto de peça, slot SOV ou sílaba montada."""
        await self.light_impact()

    async def tense_consonant(self):
        """Feedback háptico pesado para consoantes tensas (ㄲ, ㄸ, ㅃ, ㅆ, ㅉ) com fechamento laríngeo."""
        await self.heavy_impact()

    async def tap_light(self):
        """Feedback tátil leve ao tocar em cards ou itens da interface."""
        await self.selection_click()

    async def rejection_shake(self):
        """Feedback de recuo em erro pedagógico: dois impactos rápidos (médio + leve)."""
        await self.medium_impact()
        await asyncio.sleep(0.06)
        await self.light_impact()

    async def correct_answer(self):
        """Feedback comemorativo de acerto: impacto pesado seguido de leve."""
        await self.heavy_impact()
        await asyncio.sleep(0.08)
        await self.light_impact()
