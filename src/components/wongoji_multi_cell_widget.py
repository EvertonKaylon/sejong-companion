"""Widget de Grade Multi-Célula 원고지 (Wongoji Lab) para palavras e frases em Canvas Único.

Renderiza uma fita horizontal de células de manuscrito tradicional coreano em um
único Canvas Flet, mapeando toques aritmeticamente em tempo constante O(1) e
gerando traços otimizados via cv.Path. Suporta regras de 띄어쓰기 (células de espaço).
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
    """Grade multi-célula em Canvas Único para prática de palavras e frases em 원고지."""

    def __init__(
        self,
        target_text: str = "한국",
        cell_size: float = 72.0,
        is_dark: bool = False,
        show_ghost: bool = True,
        min_iou: float = 0.40,
        on_evaluated: Optional[Callable[[str, bool, float, dict[int, float]], None]] = None,
    ):
        super().__init__()
        self.target_text = target_text if target_text else "한국"
        self.cell_size = max(55.0, cell_size)
        self.is_dark = is_dark
        self.show_ghost = show_ghost
        self.min_iou = min_iou
        self.on_evaluated = on_evaluated

        self.colors = get_theme_colors(is_dark)

        # Dimensões da fita de células
        self.num_cells = len(self.target_text)
        self.width_total = self.num_cells * self.cell_size
        self.height_total = self.cell_size

        # Memória de traços por célula: {cell_index: [stroke1, stroke2, ...]}
        self.strokes_by_cell: dict[int, list[list[tuple[float, float]]]] = {
            i: [] for i in range(self.num_cells)
        }
        self.current_drawn_points: list[tuple[float, float]] = []
        self.active_cell: Optional[int] = None

        # Estado da avaliação por célula
        self.scores_by_cell: dict[int, float] = {}
        self.diag_by_cell: dict[int, dict[str, list[tuple[int, int]]]] = {}
        self.cell_status: dict[int, str] = {i: "PENDENTE" for i in range(self.num_cells)}
        self.is_evaluated = False
        self.show_overlay = False

        self._build_ui()

    def set_target_text(self, text: str):
        """Atualiza o texto alvo da fita e reinicia os estados de escrita."""
        self.target_text = text if text else "한국"
        self.num_cells = len(self.target_text)
        self.width_total = self.num_cells * self.cell_size
        self.reset()

    def reset(self):
        """Limpa todos os traços desenhados e reseta a avaliação."""
        self.strokes_by_cell = {i: [] for i in range(self.num_cells)}
        self.current_drawn_points = []
        self.active_cell = None
        self.scores_by_cell.clear()
        self.diag_by_cell.clear()
        self.cell_status = {i: "PENDENTE" for i in range(self.num_cells)}
        self.is_evaluated = False
        self.show_overlay = False
        self._refresh_canvas(refresh_guide=True)

    def _build_ui(self):
        # 1. Canvas Estático de Guia (Molduras, Cruzetas e Letras Fantasma)
        self.guide_canvas = cv.Canvas(
            shapes=self._generate_guide_shapes(),
            width=self.width_total,
            height=self.height_total,
        )

        # 2. Canvas Dinâmico de Traços e Diagnóstico
        self.dynamic_canvas = cv.Canvas(
            shapes=self._generate_dynamic_shapes(),
            width=self.width_total,
            height=self.height_total,
        )

        # 3. Stack de Desenho
        self.drawing_surface = ft.Stack(
            controls=[self.guide_canvas, self.dynamic_canvas],
            width=self.width_total,
            height=self.height_total,
        )

        # 4. GestureDetector Único com Mapeamento de Célula
        self.gesture_detector = ft.GestureDetector(
            content=self.drawing_surface,
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
            on_pan_cancel=self._on_pan_cancel,
            drag_interval=16,
            mouse_cursor=ft.MouseCursor.PRECISE,
        )

        # Container rolável horizontal para acomodar frases de qualquer tamanho
        self.content = ft.Row(
            controls=[
                ft.Container(
                    content=self.gesture_detector,
                    width=self.width_total,
                    height=self.height_total,
                    border_radius=Styles.BORDER_RADIUS_SM,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _get_cell_index(self, x: float) -> Optional[int]:
        col = int(x // self.cell_size)
        if 0 <= col < self.num_cells:
            return col
        return None

    def _generate_guide_shapes(self) -> list:
        shapes = []
        sz = self.cell_size
        wongoji_border = "#EF4444" if not self.is_dark else "#F87171"
        wongoji_guide = "#FCA5A5" if not self.is_dark else "#7F1D1D"
        ghost_color = "#E2E8F0" if not self.is_dark else "#3F3F46"
        space_bg = "#F1F5F9" if not self.is_dark else "#18181B"

        for idx, char in enumerate(self.target_text):
            x0 = idx * sz
            st = self.cell_status.get(idx, "PENDENTE")

            # Cor da borda com base no status da célula
            if self.is_evaluated and char != " ":
                if st == "CORRETO":
                    border_paint = ft.Paint(color="#10B981", stroke_width=2.0, style=ft.PaintingStyle.STROKE)
                elif st == "ERRO":
                    border_paint = ft.Paint(color="#EF4444", stroke_width=2.0, style=ft.PaintingStyle.STROKE)
                else:
                    border_paint = ft.Paint(color=wongoji_border, stroke_width=1.2, style=ft.PaintingStyle.STROKE)
            else:
                border_paint = ft.Paint(color=wongoji_border, stroke_width=1.2, style=ft.PaintingStyle.STROKE)

            # Célula de Espaço (띄어쓰기)
            if char == " ":
                shapes.append(
                    cv.Rect(
                        x=x0 + 3, y=3,
                        width=sz - 6, height=sz - 6,
                        border_radius=3,
                        paint=ft.Paint(color=space_bg, style=ft.PaintingStyle.FILL),
                    )
                )
                shapes.append(
                    cv.Rect(
                        x=x0 + 3, y=3,
                        width=sz - 6, height=sz - 6,
                        border_radius=3,
                        paint=ft.Paint(color="#CBD5E1" if not self.is_dark else "#334155", stroke_width=1, style=ft.PaintingStyle.STROKE, stroke_dash_pattern=[3, 3]),
                    )
                )
                # Indicador visual de espaço (V invertido discreto no canto superior)
                shapes.append(
                    cv.Text(
                        x=x0 + sz * 0.5,
                        y=sz * 0.48,
                        value="␣",
                        alignment=ft.Alignment.CENTER,
                        style=ft.TextStyle(size=sz * 0.35, color="#94A3B8" if not self.is_dark else "#475569"),
                    )
                )
                continue

            # Moldura externa da célula Wongoji
            shapes.append(
                cv.Rect(
                    x=x0 + 3, y=3,
                    width=sz - 6, height=sz - 6,
                    border_radius=3,
                    paint=border_paint,
                )
            )

            # Cruzeta central pontilhada
            meio = sz / 2
            shapes.append(
                cv.Line(
                    x1=x0 + meio, y1=3,
                    x2=x0 + meio, y2=sz - 3,
                    paint=ft.Paint(color=wongoji_guide, stroke_width=0.8, stroke_dash_pattern=[3, 3]),
                )
            )
            shapes.append(
                cv.Line(
                    x1=x0 + 3, y1=meio,
                    x2=x0 + sz - 3, y2=meio,
                    paint=ft.Paint(color=wongoji_guide, stroke_width=0.8, stroke_dash_pattern=[3, 3]),
                )
            )

            # Letra Modelo Fantasma (Ghost Layer)
            if self.show_ghost and not self.show_overlay:
                shapes.append(
                    cv.Text(
                        x=x0 + sz * 0.50,
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

    def _generate_dynamic_shapes(self) -> list:
        shapes = []
        sz = self.cell_size
        stroke_width = max(2.5, sz * _RASTER_STROKE_WIDTH / _REFERENCE_BITMAP_SIZE)
        stroke_color = "#1C1917" if not self.is_dark else "#F5F5F4"

        # 1. Renderizar traços finalizados usando cv.Path otimizado
        paint_stroke = ft.Paint(
            color=stroke_color,
            stroke_width=stroke_width,
            style=ft.PaintingStyle.STROKE,
            stroke_cap=ft.StrokeCap.ROUND,
            stroke_join=ft.StrokeJoin.ROUND,
        )

        for cell_idx, strokes in self.strokes_by_cell.items():
            x0 = cell_idx * sz
            for stroke in strokes:
                if not stroke:
                    continue
                if len(stroke) == 1:
                    px = x0 + stroke[0][0] * sz
                    py = stroke[0][1] * sz
                    shapes.append(cv.Circle(x=px, y=py, radius=stroke_width / 2, paint=ft.Paint(color=stroke_color, style=ft.PaintingStyle.FILL)))
                else:
                    path = cv.Path(
                        [cv.Path.MoveTo(x0 + stroke[0][0] * sz, stroke[0][1] * sz)],
                        paint=paint_stroke,
                    )
                    for pt in stroke[1:]:
                        path.elements.append(cv.Path.LineTo(x0 + pt[0] * sz, pt[1] * sz))
                    shapes.append(path)

        # 2. Renderizar traço ativo em tempo real
        if self.current_drawn_points and self.active_cell is not None:
            x0 = self.active_cell * sz
            paint_active = ft.Paint(
                color="#0D9488" if not self.is_dark else "#2DD4BF",
                stroke_width=stroke_width,
                style=ft.PaintingStyle.STROKE,
                stroke_cap=ft.StrokeCap.ROUND,
                stroke_join=ft.StrokeJoin.ROUND,
            )
            path_active = cv.Path(
                [cv.Path.MoveTo(x0 + self.current_drawn_points[0][0] * sz, self.current_drawn_points[0][1] * sz)],
                paint=paint_active,
            )
            for pt in self.current_drawn_points[1:]:
                path_active.elements.append(cv.Path.LineTo(x0 + pt[0] * sz, pt[1] * sz))
            shapes.append(path_active)

        # 3. Renderizar Overlay de Diagnóstico por Célula
        if self.show_overlay and self.diag_by_cell:
            cell_pixel_sz = sz / _REFERENCE_BITMAP_SIZE
            for cell_idx, diag in self.diag_by_cell.items():
                x0 = cell_idx * sz
                for key, color in (("miss_cells", "#94A3B8"), ("excess_cells", "#EF4444"), ("hit_cells", "#10B981")):
                    for r, c in diag.get(key, []):
                        shapes.append(
                            cv.Rect(
                                x=x0 + c * cell_pixel_sz,
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

        col = self._get_cell_index(coords[0])
        if col is None or self.target_text[col] == " ":
            self.active_cell = None
            return

        self.active_cell = col
        x_local = coords[0] - col * self.cell_size
        y_local = coords[1]

        norm_x = max(0.0, min(1.0, x_local / self.cell_size))
        norm_y = max(0.0, min(1.0, y_local / self.cell_size))
        self.current_drawn_points = [(norm_x, norm_y)]

        guide_changed = self.show_overlay
        if guide_changed:
            self.show_overlay = False

        self._refresh_canvas(refresh_guide=guide_changed)

    def _on_pan_update(self, e: ft.DragUpdateEvent):
        if self.active_cell is None or not self.current_drawn_points:
            return

        coords = self._extract_coords(e)
        if not coords:
            return

        col = self.active_cell
        x_local = coords[0] - col * self.cell_size
        y_local = coords[1]

        norm_x = max(0.0, min(1.0, x_local / self.cell_size))
        norm_y = max(0.0, min(1.0, y_local / self.cell_size))
        self.current_drawn_points.append((norm_x, norm_y))

        self._refresh_canvas()

    def _on_pan_end(self, e: ft.DragEndEvent):
        if self.active_cell is not None and self.current_drawn_points:
            self.strokes_by_cell[self.active_cell].append(list(self.current_drawn_points))
        self.current_drawn_points = []
        self.active_cell = None
        self._refresh_canvas()

    def _on_pan_cancel(self, e: Any):
        self.current_drawn_points = []
        self.active_cell = None
        self._refresh_canvas()

    def _refresh_canvas(self, refresh_guide: bool = False):
        self.dynamic_canvas.shapes = self._generate_dynamic_shapes()
        if refresh_guide:
            self.guide_canvas.shapes = self._generate_guide_shapes()
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

        self._refresh_canvas(refresh_guide=True)

        if self.on_evaluated:
            self.on_evaluated(self.target_text, all_passed, avg_score, scores)

        return all_passed, avg_score, scores
