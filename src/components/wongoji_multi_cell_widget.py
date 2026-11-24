"""Widget de Grade Multi-Célula 원고지 (Wongoji Lab) para palavras e frases em TouchScreen.

Combina uma Fita de Visão Geral (Overview Strip) com uma Célula de Foco Ativo (210x210px),
garantindo conforto anatômico total para desenho com dedos em celulares, tablets e desktops.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

import flet as ft
import flet.canvas as cv

from ..theme import Styles, get_theme_colors
from .calligraphy_widget import (
    _REFERENCE_BITMAP_SIZE,
    _RASTER_STROKE_WIDTH,
    _IOU_TOLERANCE_RADIUS,
    _get_reference_bitmap,
    render_strokes_bitmap,
    calculate_tolerant_iou,
    generate_diagnostic_overlay,
)


class WongojiMultiCellWidget(ft.Container):
    """Grade ergonômica multi-célula para palavras e frases em telas sensíveis ao toque."""

    def __init__(
        self,
        target_text: str = "한국",
        cell_size: float = 210.0,
        is_dark: bool = False,
        show_ghost: bool = True,
        min_iou: float = 0.40,
        on_evaluated: Optional[Callable[[str, bool, float, dict[int, float]], None]] = None,
    ):
        super().__init__()
        self.target_text = target_text if target_text else "한국"
        self.active_cell_size = 210.0  # Tamanho ergonômico padrão para touchscreen
        self.strip_cell_size = 46.0   # Tamanho de miniatura na fita de visão geral
        self.is_dark = is_dark
        self.show_ghost = show_ghost
        self.min_iou = min_iou
        self.on_evaluated = on_evaluated

        self.colors = get_theme_colors(is_dark)
        self.num_cells = len(self.target_text)

        # Encontrar o primeiro índice não-espaço para iniciar o foco
        self.active_index = self._get_next_valid_index(-1, forward=True) or 0

        # Memória de traços por célula: {cell_index: [stroke1, stroke2, ...]}
        self.strokes_by_cell: dict[int, list[list[tuple[float, float]]]] = {
            i: [] for i in range(self.num_cells)
        }
        self.current_drawn_points: list[tuple[float, float]] = []

        # Estado da avaliação por célula
        self.scores_by_cell: dict[int, float] = {}
        self.diag_by_cell: dict[int, dict[str, list[tuple[int, int]]]] = {}
        self.cell_status: dict[int, str] = {i: "PENDENTE" for i in range(self.num_cells)}
        self.is_evaluated = False
        self.show_overlay = False

        self._build_ui()

    def _get_next_valid_index(self, current: int, forward: bool = True) -> Optional[int]:
        step = 1 if forward else -1
        idx = current + step
        while 0 <= idx < self.num_cells:
            if self.target_text[idx] != " ":
                return idx
            idx += step
        return None

    def set_target_text(self, text: str):
        """Atualiza o texto alvo da fita e reinicia os estados de escrita."""
        self.target_text = text if text else "한국"
        self.num_cells = len(self.target_text)
        self.active_index = self._get_next_valid_index(-1, forward=True) or 0
        self.reset()

    def reset(self):
        """Limpa todos os traços desenhados e reseta a avaliação."""
        self.strokes_by_cell = {i: [] for i in range(self.num_cells)}
        self.current_drawn_points = []
        self.scores_by_cell.clear()
        self.diag_by_cell.clear()
        self.cell_status = {i: "PENDENTE" for i in range(self.num_cells)}
        self.is_evaluated = False
        self.show_overlay = False
        self._refresh_strip()
        self._refresh_active_canvas(refresh_guide=True)
        self._update_navigation_controls()

    def reset_current_cell(self):
        """Limpa apenas os traços da célula ativa atual."""
        self.strokes_by_cell[self.active_index] = []
        self.current_drawn_points = []
        if self.active_index in self.scores_by_cell:
            del self.scores_by_cell[self.active_index]
        if self.active_index in self.diag_by_cell:
            del self.diag_by_cell[self.active_index]
        self.cell_status[self.active_index] = "PENDENTE"
        self._refresh_strip()
        self._refresh_active_canvas(refresh_guide=True)

    def select_cell(self, index: int):
        """Muda o foco para uma célula específica."""
        if 0 <= index < self.num_cells and self.target_text[index] != " ":
            self.active_index = index
            self._refresh_strip()
            self._refresh_active_canvas(refresh_guide=True)
            self._update_navigation_controls()

    def prev_cell(self, e=None):
        prev_idx = self._get_next_valid_index(self.active_index, forward=False)
        if prev_idx is not None:
            self.select_cell(prev_idx)

    def next_cell(self, e=None):
        next_idx = self._get_next_valid_index(self.active_index, forward=True)
        if next_idx is not None:
            self.select_cell(next_idx)

    def _build_ui(self):
        sz = self.active_cell_size

        # 1. Fita de Visão Geral (Strip)
        self.strip_row = ft.Row(
            controls=self._generate_strip_controls(),
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        )

        # 2. Canvas Estático de Guia da Célula Ativa (210x210px)
        self.guide_canvas = cv.Canvas(
            shapes=self._generate_active_guide_shapes(),
            width=sz,
            height=sz,
        )

        # 3. Canvas Dinâmico de Traços da Célula Ativa
        self.dynamic_canvas = cv.Canvas(
            shapes=self._generate_active_dynamic_shapes(),
            width=sz,
            height=sz,
        )

        # 4. Stack de Desenho com GestureDetector
        self.drawing_surface = ft.Stack(
            controls=[self.guide_canvas, self.dynamic_canvas],
            width=sz,
            height=sz,
        )

        self.gesture_detector = ft.GestureDetector(
            content=self.drawing_surface,
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
            on_pan_cancel=self._on_pan_cancel,
            drag_interval=16,
            mouse_cursor=ft.MouseCursor.PRECISE,
        )

        # 5. Barra de Navegação entre Células
        self.btn_prev_cell = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT_ROUNDED,
            icon_color=self.colors["primary"],
            tooltip="Sílaba anterior",
            on_click=self.prev_cell,
        )
        self.lbl_cell_indicator = ft.Text(
            self._get_indicator_text(),
            size=13,
            weight=ft.FontWeight.W_600,
            color=self.colors["text"],
        )
        self.btn_next_cell = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT_ROUNDED,
            icon_color=self.colors["primary"],
            tooltip="Próxima sílaba",
            on_click=self.next_cell,
        )

        self.nav_row = ft.Row(
            controls=[self.btn_prev_cell, self.lbl_cell_indicator, self.btn_next_cell],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )
        self._update_navigation_controls()

        # Montagem do Layout Principal
        self.content = ft.Column(
            controls=[
                # Fita no topo se houver mais de 1 caractere
                ft.Container(
                    content=self.strip_row,
                    padding=ft.Padding.symmetric(horizontal=4, vertical=4),
                    visible=(self.num_cells > 1),
                ),
                # Card de Foco Central Ergonômico (210x210px)
                ft.Container(
                    content=self.gesture_detector,
                    width=sz,
                    height=sz,
                    border_radius=Styles.BORDER_RADIUS_MD,
                    bgcolor=self.colors["card_bg"],
                    alignment=ft.Alignment.CENTER,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
                # Barra de Navegação
                ft.Container(
                    content=self.nav_row,
                    visible=(self.num_cells > 1),
                ),
            ],
            spacing=6,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _get_indicator_text(self) -> str:
        current_char = self.target_text[self.active_index] if 0 <= self.active_index < self.num_cells else ""
        non_space_chars = [c for c in self.target_text if c != " "]
        current_pos = [i for i, c in enumerate(self.target_text) if c != " "].index(self.active_index) + 1 if self.active_index in [i for i, c in enumerate(self.target_text) if c != " "] else 1
        return f"Sílaba {current_pos} de {len(non_space_chars)}: '{current_char}'"

    def _update_navigation_controls(self):
        prev_idx = self._get_next_valid_index(self.active_index, forward=False)
        next_idx = self._get_next_valid_index(self.active_index, forward=True)
        self.btn_prev_cell.disabled = (prev_idx is None)
        self.btn_next_cell.disabled = (next_idx is None)
        self.lbl_cell_indicator.value = self._get_indicator_text()
        try:
            self.nav_row.update()
        except Exception:
            pass

    def _generate_strip_controls(self) -> list[ft.Control]:
        controls = []
        sz = self.strip_cell_size

        for idx, char in enumerate(self.target_text):
            is_active = (idx == self.active_index)
            st = self.cell_status.get(idx, "PENDENTE")

            if char == " ":
                # Célula de Espaço
                controls.append(
                    ft.Container(
                        width=sz * 0.6,
                        height=sz,
                        border=ft.Border.all(1, "#CBD5E1" if not self.is_dark else "#334155"),
                        border_radius=4,
                        bgcolor="#F1F5F9" if not self.is_dark else "#18181B",
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text("␣", size=14, color="#94A3B8" if not self.is_dark else "#475569"),
                    )
                )
                continue

            # Cor de Borda e Fundo
            if self.is_evaluated:
                border_color = "#10B981" if st == "CORRETO" else "#EF4444"
                border_width = 2
            elif is_active:
                border_color = self.colors["primary"]
                border_width = 2.5
            else:
                border_color = "#EF4444" if not self.is_dark else "#F87171"
                border_width = 1

            has_strokes = len(self.strokes_by_cell.get(idx, [])) > 0
            text_color = self.colors["text"] if has_strokes else ("#94A3B8" if not self.is_dark else "#52525B")

            cell_btn = ft.Container(
                width=sz,
                height=sz,
                border=ft.Border.all(border_width, border_color),
                border_radius=6,
                bgcolor=self.colors["card_bg"] if not is_active else (ft.Colors.with_opacity(0.10, self.colors["primary"]) if not self.is_dark else ft.Colors.with_opacity(0.19, self.colors["primary"])),
                alignment=ft.Alignment.CENTER,
                on_click=lambda _, i=idx: self.select_cell(i),
                content=ft.Text(
                    char,
                    size=sz * 0.52,
                    font_family="Kyobo Handwriting",
                    weight=ft.FontWeight.BOLD if has_strokes else ft.FontWeight.NORMAL,
                    color=text_color,
                ),
            )
            controls.append(cell_btn)

        return controls

    def _generate_active_guide_shapes(self) -> list:
        shapes = []
        sz = self.active_cell_size
        char = self.target_text[self.active_index] if 0 <= self.active_index < self.num_cells else ""
        st = self.cell_status.get(self.active_index, "PENDENTE")

        wongoji_border = "#EF4444" if not self.is_dark else "#F87171"
        wongoji_guide = "#FCA5A5" if not self.is_dark else "#7F1D1D"
        ghost_color = "#E2E8F0" if not self.is_dark else "#3F3F46"

        if self.is_evaluated and char != " ":
            border_paint = ft.Paint(color="#10B981" if st == "CORRETO" else "#EF4444", stroke_width=2.5, style=ft.PaintingStyle.STROKE)
        else:
            border_paint = ft.Paint(color=wongoji_border, stroke_width=1.5, style=ft.PaintingStyle.STROKE)

        # Moldura Externa
        shapes.append(
            cv.Rect(
                x=6, y=6,
                width=sz - 12, height=sz - 12,
                border_radius=4,
                paint=border_paint,
            )
        )

        # Cruzeta Pontilhada
        meio = sz / 2
        shapes.append(
            cv.Line(
                x1=meio, y1=6,
                x2=meio, y2=sz - 6,
                paint=ft.Paint(color=wongoji_guide, stroke_width=1.0, stroke_dash_pattern=[4, 4]),
            )
        )
        shapes.append(
            cv.Line(
                x1=6, y1=meio,
                x2=sz - 6, y2=meio,
                paint=ft.Paint(color=wongoji_guide, stroke_width=1.0, stroke_dash_pattern=[4, 4]),
            )
        )

        # Letra Modelo Fantasma (Kyobo Handwriting)
        if self.show_ghost and not self.show_overlay and char != " ":
            shapes.append(
                cv.Text(
                    x=sz * 0.50,
                    y=sz * 0.48,
                    value=char,
                    alignment=ft.Alignment.CENTER,
                    style=ft.TextStyle(
                        size=sz * 0.68,
                        font_family="Kyobo Handwriting",
                        color=ghost_color,
                    ),
                )
            )

        return shapes

    def _generate_active_dynamic_shapes(self) -> list:
        shapes = []
        sz = self.active_cell_size
        stroke_width = max(3.5, sz * _RASTER_STROKE_WIDTH / _REFERENCE_BITMAP_SIZE)
        stroke_color = "#1C1917" if not self.is_dark else "#F5F5F4"

        # 1. Renderizar traços da célula ativa
        paint_stroke = ft.Paint(
            color=stroke_color,
            stroke_width=stroke_width,
            style=ft.PaintingStyle.STROKE,
            stroke_cap=ft.StrokeCap.ROUND,
            stroke_join=ft.StrokeJoin.ROUND,
        )

        strokes = self.strokes_by_cell.get(self.active_index, [])
        for stroke in strokes:
            if not stroke:
                continue
            if len(stroke) == 1:
                shapes.append(cv.Circle(x=stroke[0][0] * sz, y=stroke[0][1] * sz, radius=stroke_width / 2, paint=ft.Paint(color=stroke_color, style=ft.PaintingStyle.FILL)))
            else:
                path = cv.Path(
                    [cv.Path.MoveTo(stroke[0][0] * sz, stroke[0][1] * sz)],
                    paint=paint_stroke,
                )
                for pt in stroke[1:]:
                    path.elements.append(cv.Path.LineTo(pt[0] * sz, pt[1] * sz))
                shapes.append(path)

        # 2. Renderizar traço ativo em tempo real
        if self.current_drawn_points:
            paint_active = ft.Paint(
                color="#0D9488" if not self.is_dark else "#2DD4BF",
                stroke_width=stroke_width,
                style=ft.PaintingStyle.STROKE,
                stroke_cap=ft.StrokeCap.ROUND,
                stroke_join=ft.StrokeJoin.ROUND,
            )
            path_active = cv.Path(
                [cv.Path.MoveTo(self.current_drawn_points[0][0] * sz, self.current_drawn_points[0][1] * sz)],
                paint=paint_active,
            )
            for pt in self.current_drawn_points[1:]:
                path_active.elements.append(cv.Path.LineTo(pt[0] * sz, pt[1] * sz))
            shapes.append(path_active)

        # 3. Renderizar Overlay de Diagnóstico
        if self.show_overlay and self.active_index in self.diag_by_cell:
            diag = self.diag_by_cell[self.active_index]
            cell_pixel_sz = sz / _REFERENCE_BITMAP_SIZE
            for key, color in (("miss_cells", "#94A3B8"), ("excess_cells", "#EF4444"), ("hit_cells", "#10B981")):
                for r, c in diag.get(key, []):
                    shapes.append(
                        cv.Rect(
                            x=c * cell_pixel_sz,
                            y=r * cell_pixel_sz,
                            width=cell_pixel_sz + 0.3,
                            height=cell_pixel_sz + 0.3,
                            paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL),
                        )
                    )

        return shapes

    def _extract_coords(self, e: Any) -> Optional[tuple[float, float]]:
        if hasattr(e, "local_position") and e.local_position is not None:
            return float(e.local_position.x), float(e.local_position.y)
        if hasattr(e, "local_x") and hasattr(e, "local_y"):
            return float(e.local_x), float(e.local_y)
        if hasattr(e, "x") and hasattr(e, "y"):
            return float(e.x), float(e.y)
        return None

    def _on_pan_start(self, e: ft.DragStartEvent):
        coords = self._extract_coords(e)
        if not coords:
            return

        norm_x = max(0.0, min(1.0, coords[0] / self.active_cell_size))
        norm_y = max(0.0, min(1.0, coords[1] / self.active_cell_size))
        self.current_drawn_points = [(norm_x, norm_y)]

        guide_changed = self.show_overlay
        if guide_changed:
            self.show_overlay = False

        self._refresh_active_canvas(refresh_guide=guide_changed)

    def _on_pan_update(self, e: ft.DragUpdateEvent):
        if not self.current_drawn_points:
            return

        coords = self._extract_coords(e)
        if not coords:
            return

        norm_x = max(0.0, min(1.0, coords[0] / self.active_cell_size))
        norm_y = max(0.0, min(1.0, coords[1] / self.active_cell_size))
        self.current_drawn_points.append((norm_x, norm_y))

        self._refresh_active_canvas()

    def _on_pan_end(self, e: ft.DragEndEvent):
        if self.current_drawn_points:
            self.strokes_by_cell[self.active_index].append(list(self.current_drawn_points))
        self.current_drawn_points = []
        self._refresh_strip()
        self._refresh_active_canvas()

    def _on_pan_cancel(self, e: Any):
        self.current_drawn_points = []
        self._refresh_active_canvas()

    def _refresh_strip(self):
        self.strip_row.controls = self._generate_strip_controls()
        try:
            self.strip_row.update()
        except Exception:
            pass

    def _refresh_active_canvas(self, refresh_guide: bool = False):
        self.dynamic_canvas.shapes = self._generate_active_dynamic_shapes()
        if refresh_guide:
            self.guide_canvas.shapes = self._generate_active_guide_shapes()
        try:
            self.dynamic_canvas.update()
            if refresh_guide:
                self.guide_canvas.update()
        except Exception:
            pass

    def evaluate(self) -> tuple[bool, float, dict[int, float]]:
        """Avalia cada célula individualmente e calcula o score global."""
        scores: dict[int, float] = {}
        diags: dict[int, dict[str, list[tuple[int, int]]]] = {}
        all_passed = True
        total_score = 0.0
        evaluated_cells_count = 0

        for idx, char in enumerate(self.target_text):
            if char == " ":
                continue

            ref_bitmap = _get_reference_bitmap(char)
            drawn_bitmap = render_strokes_bitmap(
                self.strokes_by_cell.get(idx, []),
                size=_REFERENCE_BITMAP_SIZE,
                stroke_width=_RASTER_STROKE_WIDTH,
            )

            score = calculate_tolerant_iou(ref_bitmap, drawn_bitmap, tolerance_radius=_IOU_TOLERANCE_RADIUS)
            diag = generate_diagnostic_overlay(ref_bitmap, drawn_bitmap, tolerance_radius=_IOU_TOLERANCE_RADIUS)

            scores[idx] = score
            diags[idx] = diag
            total_score += score
            evaluated_cells_count += 1

            if score >= self.min_iou:
                self.cell_status[idx] = "CORRETO"
            else:
                self.cell_status[idx] = "ERRO"
                all_passed = False

        avg_score = (total_score / evaluated_cells_count) if evaluated_cells_count > 0 else 0.0

        self.scores_by_cell = scores
        self.diag_by_cell = diags
        self.is_evaluated = True
        self.show_overlay = True

        self._refresh_strip()
        self._refresh_active_canvas(refresh_guide=True)

        if self.on_evaluated:
            self.on_evaluated(self.target_text, all_passed, avg_score, scores)

        return all_passed, avg_score, scores
