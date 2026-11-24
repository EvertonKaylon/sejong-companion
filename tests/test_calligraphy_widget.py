"""Testes automatizados para o CalligraphyWidget (Wongoji Lab) e motor de visão/IoU."""

import pytest
import flet.canvas as cv
from src.components.calligraphy_widget import (
    CalligraphyWidget,
    calculate_iou,
    calculate_tolerant_iou,
    generate_diagnostic_overlay,
    get_syllable_structure_label,
    render_reference_bitmap,
    render_strokes_bitmap,
)


class TestCalligraphyVisionEngine:
    """Testes para o motor de rasterização tipográfica e comparação de bitmaps."""

    def test_render_reference_bitmap_hangul_syllables(self):
        # Sílaba básica
        bm_ga = render_reference_bitmap("가", size=48)
        assert len(bm_ga) == 48
        assert len(bm_ga[0]) == 48
        total_pixels_ga = sum(sum(row) for row in bm_ga)
        assert total_pixels_ga > 50

        # Sílaba complexa com batchim
        bm_han = render_reference_bitmap("한", size=48)
        total_pixels_han = sum(sum(row) for row in bm_han)
        assert total_pixels_han > total_pixels_ga

    def test_render_reference_bitmap_jamo(self):
        bm_g = render_reference_bitmap("ㄱ", size=48)
        total_pixels_g = sum(sum(row) for row in bm_g)
        assert total_pixels_g > 30

    def test_render_strokes_bitmap(self):
        strokes = [
            [(0.2, 0.2), (0.8, 0.2)],
            [(0.8, 0.2), (0.8, 0.8)],
        ]
        bm = render_strokes_bitmap(strokes, size=48, stroke_width=3)
        assert len(bm) == 48
        total_pixels = sum(sum(row) for row in bm)
        assert total_pixels > 20

    def test_calculate_iou_identical_bitmaps(self):
        bm = [[1 if (r > 10 and c > 10) else 0 for c in range(30)] for r in range(30)]
        score = calculate_iou(bm, bm)
        assert score == 1.0

    def test_calculate_iou_disjoint_bitmaps(self):
        bm1 = [[1 if r < 10 else 0 for _ in range(30)] for r in range(30)]
        bm2 = [[1 if r >= 20 else 0 for _ in range(30)] for r in range(30)]
        score = calculate_iou(bm1, bm2)
        assert score == 0.0

    def test_calculate_iou_partial_overlap(self):
        bm_ref = render_reference_bitmap("가", size=48)
        # Traço curto ancorado em um pixel real do glifo, sem depender da
        # geometria de uma fonte específica.
        row, col = next(
            (r, c)
            for r, values in enumerate(bm_ref)
            for c, value in enumerate(values)
            if value
        )
        strokes = [
            [
                (col / 47, row / 47),
                (min(col + 2, 47) / 47, row / 47),
            ],
        ]
        bm_drawn = render_strokes_bitmap(strokes, size=48)
        score = calculate_iou(bm_ref, bm_drawn)
        assert 0.0 < score < 1.0

    def test_tolerant_iou_rewards_small_handwriting_offset(self):
        reference = [[0 for _ in range(9)] for _ in range(9)]
        reference[4][2:7] = [1] * 5
        shifted = [[0 for _ in range(9)] for _ in range(9)]
        shifted[5][2:7] = [1] * 5

        assert calculate_iou(reference, shifted) == 0.0
        assert calculate_tolerant_iou(reference, shifted, tolerance_radius=1) >= 0.5

    def test_generate_diagnostic_overlay(self):
        bm_ref = [
            [1, 1, 0],
            [0, 1, 0],
            [0, 0, 0],
        ]
        bm_drawn = [
            [1, 0, 0],
            [0, 1, 1],
            [0, 0, 0],
        ]
        diag = generate_diagnostic_overlay(bm_ref, bm_drawn)
        # Acertos (1 e 1): (0,0), (1,1)
        assert (0, 0) in diag["hit_cells"]
        assert (1, 1) in diag["hit_cells"]
        # Omissões (ref=1, drawn=0): (0,1)
        assert (0, 1) in diag["miss_cells"]
        # Excessos (ref=0, drawn=1): (1,2)
        assert (1, 2) in diag["excess_cells"]


class TestCalligraphyWidgetUI:
    """Testes de inicialização, ciclo de vida e interação do CalligraphyWidget."""

    def test_widget_initialization(self):
        completed_data = []

        def on_done(char, score):
            completed_data.append((char, score))

        w = CalligraphyWidget(target_char="가", is_dark=False, on_completed=on_done)
        assert w.target_char == "가"
        assert w.stroke_count == 0
        assert w.sampled_points_count == 0
        assert w.is_evaluated is False
        assert "Escreva: 가" in w.status_text.value
        assert len(w.guide_canvas.shapes) > 0

    def test_widget_toggle_ghost(self):
        w = CalligraphyWidget(target_char="가", show_ghost=True)
        assert w.show_ghost is True
        w.toggle_ghost()
        assert w.show_ghost is False
        w.toggle_ghost()
        assert w.show_ghost is True

    def test_widget_set_target_character(self):
        w = CalligraphyWidget(target_char="가")
        w.set_target_character("한")
        assert w.target_char == "한"
        assert "Escreva: 한" in w.status_text.value
        assert "Batchim" in w.metric_structure_text.value

    def test_widget_reset(self):
        w = CalligraphyWidget(target_char="가")
        w.stroke_count = 3
        w.sampled_points_count = 50
        w.last_score = 0.85
        w.is_evaluated = True
        w.show_overlay = True

        w.reset()
        assert w.stroke_count == 0
        assert w.sampled_points_count == 0
        assert w.last_score is None
        assert w.is_evaluated is False
        assert w.show_overlay is False
        assert w.metric_points_text.value == "0"
        assert w.metric_strokes_text.value == "0"

    def test_widget_freeform_drawing_and_evaluate(self):
        evaluated_records = []

        def on_eval(char, score, diag):
            evaluated_records.append((char, score, diag))

        w = CalligraphyWidget(target_char="가", on_evaluated=on_eval)

        # 1. Simular desenho de traço
        class MockDragStartEvent:
            local_position = type("Pos", (), {"x": 50.0, "y": 50.0})()

        class MockDragUpdateEvent:
            local_position = type("Pos", (), {"x": 100.0, "y": 50.0})()

        class MockDragEndEvent:
            pass

        w._on_pan_start(MockDragStartEvent())
        w._on_pan_update(MockDragUpdateEvent())
        w._on_pan_end(MockDragEndEvent())

        assert w.stroke_count == 1
        assert w.sampled_points_count == 2
        assert len(w.all_strokes) == 1

        # 2. Avaliar
        w.evaluate()
        assert w.is_evaluated is True
        assert w.show_overlay is True
        assert w.last_score is not None
        assert len(evaluated_records) == 1
        assert evaluated_records[0][0] == "가"
        assert "hit_cells" in evaluated_records[0][2]

    def test_pan_cancel_discards_unfinished_stroke(self):
        w = CalligraphyWidget()

        # Um gesto cancelado por outro reconhecedor não mantém um traço parcial.
        w.current_drawn_points = [(0.2, 0.2)]
        w._on_pan_cancel(object())
        assert w.current_drawn_points == []

    def test_preview_shapes_scale_without_changing_drawing_state(self):
        w = CalligraphyWidget(size=300)
        w.all_strokes = [[(0.2, 0.2), (0.8, 0.8)]]

        preview_shapes = w._generate_canvas_shapes(size=180)

        assert preview_shapes
        assert w.grid_size == 300
        assert w.all_strokes == [[(0.2, 0.2), (0.8, 0.8)]]

    def test_guide_uses_the_kyobo_font_used_by_iou_reference(self):
        w = CalligraphyWidget(target_char="가", size=240)

        guide = w.guide_canvas.shapes[-1]
        assert isinstance(guide, cv.Text)
        assert guide.value == "가"
        assert guide.style.font_family == "Kyobo Handwriting"

    def test_stroke_width_scales_from_the_iou_raster(self):
        w = CalligraphyWidget(size=240)
        w.all_strokes = [[(0.2, 0.2), (0.8, 0.8)]]

        shapes = w._generate_dynamic_canvas_shapes()

        assert shapes[0].paint.stroke_width == 15

    def test_syllable_structure_classification(self):
        assert "Jamo" in get_syllable_structure_label("ㄱ")
        assert "Consoante + Vogal" in get_syllable_structure_label("가")
        assert "Batchim" in get_syllable_structure_label("한")
