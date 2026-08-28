"""Testes automatizados para o CalligraphyWidget e algoritmo de validação de traços."""

import pytest
from src.components.calligraphy_widget import (
    CalligraphyWidget,
    calculate_stroke_similarity,
    get_reference_strokes,
    load_stroke_dataset,
)


class TestCalligraphyLogic:
    """Testes para algoritmos puros de extração de traços e similaridade."""

    def test_load_stroke_dataset(self):
        data = load_stroke_dataset()
        assert "consonants" in data
        assert "vowels" in data
        assert len(data["consonants"]) >= 14
        assert len(data["vowels"]) >= 11

    def test_get_reference_strokes_jamo(self):
        strokes_g = get_reference_strokes("ㄱ")
        assert len(strokes_g) == 2
        # Verifica normalização 0.0 - 1.0
        for stroke in strokes_g:
            for pt in stroke:
                assert 0.0 <= pt[0] <= 1.0
                assert 0.0 <= pt[1] <= 1.0

        strokes_a = get_reference_strokes("ㅏ")
        assert len(strokes_a) == 2

    def test_get_reference_strokes_composed_syllable(self):
        # '가' = ㄱ (2 strokes) + ㅏ (2 strokes) = 4 strokes
        strokes_ga = get_reference_strokes("가")
        assert len(strokes_ga) == 4

        # '한' = ㅎ (3 strokes) + ㅏ (2 strokes) + ㄴ (2 strokes) = 7 strokes
        strokes_han = get_reference_strokes("한")
        assert len(strokes_han) == 7

        # '고' = ㄱ (2 strokes) + ㅗ (2 strokes) = 4 strokes
        strokes_go = get_reference_strokes("고")
        assert len(strokes_go) == 4

    def test_calculate_stroke_similarity_perfect_match(self):
        ref = [(0.2, 0.2), (0.5, 0.2), (0.8, 0.2)]
        drawn = [(0.2, 0.2), (0.5, 0.2), (0.8, 0.2)]
        is_valid, score = calculate_stroke_similarity(drawn, ref)
        assert is_valid is True
        assert score >= 0.90

    def test_calculate_stroke_similarity_close_match(self):
        ref = [(0.2, 0.2), (0.8, 0.2)]
        # Leve desvio de 3% no eixo Y
        drawn = [(0.22, 0.23), (0.50, 0.21), (0.78, 0.22)]
        is_valid, score = calculate_stroke_similarity(drawn, ref, tolerance=0.30)
        assert is_valid is True
        assert score >= 0.60

    def test_calculate_stroke_similarity_reversed_direction_fails(self):
        ref = [(0.2, 0.2), (0.8, 0.2)]
        # Desenhado da direita para a esquerda (direção invertida)
        drawn = [(0.8, 0.2), (0.5, 0.2), (0.2, 0.2)]
        is_valid, score = calculate_stroke_similarity(drawn, ref)
        assert is_valid is False

    def test_calculate_stroke_similarity_wrong_location_fails(self):
        ref = [(0.1, 0.1), (0.9, 0.1)]
        # Desenhado na parte inferior
        drawn = [(0.1, 0.9), (0.9, 0.9)]
        is_valid, score = calculate_stroke_similarity(drawn, ref, tolerance=0.30)
        assert is_valid is False

    def test_calculate_stroke_similarity_empty_or_single_point(self):
        ref = [(0.1, 0.1), (0.9, 0.1)]
        assert calculate_stroke_similarity([], ref) == (False, 0.0)
        assert calculate_stroke_similarity([(0.1, 0.1)], ref) == (False, 0.0)


class TestCalligraphyWidgetUI:
    """Testes de inicialização e ciclo de vida do CalligraphyWidget."""

    def test_widget_initialization(self):
        completed_data = []

        def on_done(char, score):
            completed_data.append((char, score))

        w = CalligraphyWidget(target_char="가", is_dark=False, on_completed=on_done)
        assert w.target_char == "가"
        assert len(w.reference_strokes) == 4
        assert w.current_stroke_index == 0
        assert w.is_completed is False
        assert "Traço 1 de 4" in w.status_text.value
        assert len(w.canvas.shapes) > 0

    def test_widget_toggle_ghost(self):
        w = CalligraphyWidget(target_char="가", show_ghost=True)
        assert w.show_ghost is True
        w.toggle_ghost()
        assert w.show_ghost is False
        w.toggle_ghost()
        assert w.show_ghost is True

    def test_widget_set_target_character(self):
        w = CalligraphyWidget(target_char="가")
        assert len(w.reference_strokes) == 4
        w.set_target_character("한")
        assert w.target_char == "한"
        assert len(w.reference_strokes) == 7
        assert w.current_stroke_index == 0
        assert "Traço 1 de 7" in w.status_text.value

    def test_widget_reset(self):
        w = CalligraphyWidget(target_char="가")
        w.current_stroke_index = 2
        w.is_completed = True
        w.scores = [0.85, 0.90]
        w.reset()
        assert w.current_stroke_index == 0
        assert w.is_completed is False
        assert len(w.scores) == 0
        assert len(w.completed_strokes) == 0
        assert "Traço 1 de 4" in w.status_text.value
