"""Testes Unitários do Serviço Háptico e Sensorial (HapticService).

Valida registro do controle ft.HapticFeedback em page.services,
mapeamento de impactos para mecânicas neuropedagógicas (snap, tensas, recuo, acerto)
e resiliência em ambientes de teste headless (page=None).
"""

from unittest.mock import AsyncMock, MagicMock
import pytest
import flet as ft

from src.haptic_service import HapticService


class MockHapticPage:
    def __init__(self):
        self.services = []
        self.overlay = []


def test_haptic_service_registers_service_on_page():
    """Valida que instanciar HapticService(page) anexa um ft.HapticFeedback a page.services."""
    page = MockHapticPage()
    service = HapticService(page)

    assert service.haptic is not None
    assert isinstance(service.haptic, ft.HapticFeedback)
    assert service.haptic in page.services


@pytest.mark.asyncio
async def test_snap_success_uses_light_impact():
    """Valida que snap_success chama light_impact do Flutter Engine."""
    page = MockHapticPage()
    service = HapticService(page)
    service.haptic.light_impact = AsyncMock()

    await service.snap_success()
    service.haptic.light_impact.assert_awaited_once()


@pytest.mark.asyncio
async def test_tense_consonant_uses_heavy_impact():
    """Valida que consoantes tensas (ㄲ, ㄸ, ㅃ, ㅆ, ㅉ) ativam heavy_impact."""
    page = MockHapticPage()
    service = HapticService(page)
    service.haptic.heavy_impact = AsyncMock()

    await service.tense_consonant()
    service.haptic.heavy_impact.assert_awaited_once()


@pytest.mark.asyncio
async def test_tap_light_uses_selection_click():
    """Valida que toque sutil (tap_light) ativa selection_click."""
    page = MockHapticPage()
    service = HapticService(page)
    service.haptic.selection_click = AsyncMock()

    await service.tap_light()
    service.haptic.selection_click.assert_awaited_once()


@pytest.mark.asyncio
async def test_rejection_shake_uses_two_real_impacts():
    """Valida que o feedback de recuo executa medium_impact seguido de light_impact."""
    page = MockHapticPage()
    service = HapticService(page)
    service.haptic.medium_impact = AsyncMock()
    service.haptic.light_impact = AsyncMock()

    await service.rejection_shake()
    service.haptic.medium_impact.assert_awaited_once()
    service.haptic.light_impact.assert_awaited_once()


@pytest.mark.asyncio
async def test_correct_answer_uses_two_real_impacts():
    """Valida celebração de acerto com heavy_impact seguido de light_impact."""
    page = MockHapticPage()
    service = HapticService(page)
    service.haptic.heavy_impact = AsyncMock()
    service.haptic.light_impact = AsyncMock()

    await service.correct_answer()
    service.haptic.heavy_impact.assert_awaited_once()
    service.haptic.light_impact.assert_awaited_once()


@pytest.mark.asyncio
async def test_haptic_service_headless_resilience():
    """Garante que quando page=None ou o dispositivo não suporta háptica, nenhum método levanta erro."""
    service = HapticService(page=None)
    assert service.haptic is None

    # Todos os métodos devem executar graciosamente sem lançar exceções
    await service.light_impact()
    await service.medium_impact()
    await service.heavy_impact()
    await service.selection_click()
    await service.vibrate()
    await service.snap_success()
    await service.tense_consonant()
    await service.tap_light()
    await service.rejection_shake()
    await service.correct_answer()
