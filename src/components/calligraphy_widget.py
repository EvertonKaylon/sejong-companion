"""Widget de Grade de Caligrafia 원고지 (Wongoji Lab) com escrita livre e diagnóstico visual.

Permite que os alunos pratiquem a escrita de Jamo e sílabas Hangul completas
de forma 100% livre sobre uma grade tradicional de manuscrito coreano (원고지).
A avaliação é feita por análise de forma real (Bitmap IoU 48x48 com a fonte
Kyobo Handwriting) e gera um mapa visual de diagnóstico (Verde = acerto, Vermelho = excesso,
Cinza = faltou), acompanhado de telemetria viva e feedback de áudio nativo.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Optional

import flet as ft
import flet.canvas as cv
from PIL import Image, ImageDraw, ImageFont

from ..jamo_utils import (
    BlockType,
    decompose,
    is_hangul_jamo,
    is_hangul_syllable,
)
from ..theme import Styles, get_theme_colors


# ============================================================
# Cache e Carregador de Fonte Tipográfica Hangul
# ============================================================
_FONT_CACHE: dict[int, ImageFont.FreeTypeFont] = {}
_REFERENCE_BITMAP_SIZE = 48
_REFERENCE_BITMAP_CACHE: dict[str, list[list[int]]] = {}
_RASTER_STROKE_WIDTH = 3
_IOU_TOLERANCE_RADIUS = 1


def _get_korean_font(size: int) -> ImageFont.FreeTypeFont:
    """Carrega e armazena em cache a fonte Kyobo Handwriting para rasterização."""
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]

    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "..", "..", "assets", "fonts", "KyoboHandwriting2025lyb.otf")

    if not os.path.exists(font_path):
        font_path = os.path.join("assets", "fonts", "KyoboHandwriting2025lyb.otf")

    try:
        font = ImageFont.truetype(font_path, size)
    except Exception:
        font = ImageFont.load_default()

    _FONT_CACHE[size] = font
    return font


# ============================================================
# Motor de Rasterização Matricial e Comparação por Bitmap (IoU)
# ============================================================
def render_reference_bitmap(char: str, size: int = 48) -> list[list[int]]:
    """Gera um mapa binário 48x48 do caractere Hangul usando a fonte oficial.

    Args:
        char: Caractere Hangul (Jamo ou sílaba composta).
        size: Resolução da matriz (padrão 48x48).

    Returns:
        Matriz 2D binária (1 para pixels da letra, 0 para fundo).
    """
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)

    # Proporção tipográfica ajustada para centralização na célula
    font_size = int(size * 0.68)
    font = _get_korean_font(font_size)

    # Obter bounding box exato para centralizar perfeitamente
    bbox = draw.textbbox((0, 0), char, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Centralizar deslocando pelo offset do bbox
    offset_x = (size - text_w) // 2 - bbox[0]
    offset_y = (size - text_h) // 2 - bbox[1]

    draw.text((offset_x, offset_y), char, fill=255, font=font)

    bitmap = []
    for y in range(size):
        row = []
        for x in range(size):
            row.append(1 if img.getpixel((x, y)) > 60 else 0)
        bitmap.append(row)

    return bitmap


def _get_reference_bitmap(char: str) -> list[list[int]]:
    """Retorna a mesma matriz usada tanto pelo guia quanto pela avaliação."""
    if char not in _REFERENCE_BITMAP_CACHE:
        _REFERENCE_BITMAP_CACHE[char] = render_reference_bitmap(
            char, size=_REFERENCE_BITMAP_SIZE
        )
    return _REFERENCE_BITMAP_CACHE[char]


def render_strokes_bitmap(
    strokes: list[list[tuple[float, float]]],
    size: int = 48,
    stroke_width: int = 3,
) -> list[list[int]]:
    """Rasteriza a sequência de traços livres do aluno em uma matriz binária.

    Args:
        strokes: Lista de traços com coordenadas normalizadas [0.0, 1.0].
        size: Resolução da matriz (padrão 48x48).
        stroke_width: Espessura do pincel na grade 48x48.

    Returns:
        Matriz 2D binária (1 para traço desenhado, 0 para fundo).
    """
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)

    for stroke in strokes:
        if not stroke:
            continue
        if len(stroke) == 1:
            # Traço pontual (toque único)
            px = int(stroke[0][0] * (size - 1))
            py = int(stroke[0][1] * (size - 1))
            r = stroke_width // 2
            draw.ellipse((px - r, py - r, px + r, py + r), fill=255)
        else:
            coords = [
                (int(pt[0] * (size - 1)), int(pt[1] * (size - 1)))
                for pt in stroke
            ]
            draw.line(coords, fill=255, width=stroke_width, joint="curve")

    bitmap = []
    for y in range(size):
        row = []
        for x in range(size):
            row.append(1 if img.getpixel((x, y)) > 60 else 0)
        bitmap.append(row)

    return bitmap


def calculate_iou(bitmap_ref: list[list[int]], bitmap_drawn: list[list[int]]) -> float:
    """Calcula o índice Intersection over Union (IoU) entre dois bitmaps.

    Returns:
        Score de similaridade entre 0.0 (sem sobreposição) e 1.0 (sobreposição perfeita).
    """
    if not bitmap_ref or not bitmap_drawn:
        return 0.0

    intersection = 0
    union = 0
    rows = len(bitmap_ref)
    cols = len(bitmap_ref[0]) if rows > 0 else 0

    for r in range(rows):
        for c in range(cols):
            val_r = bitmap_ref[r][c]
            val_d = bitmap_drawn[r][c]
            if val_r == 1 and val_d == 1:
                intersection += 1
            if val_r == 1 or val_d == 1:
                union += 1

    if union == 0:
        return 0.0

    return round(intersection / union, 4)


def _dilate_bitmap(bitmap: list[list[int]], radius: int) -> list[list[int]]:
    """Expande uma máscara binária para absorver pequenas imprecisões humanas."""
    if radius <= 0 or not bitmap:
        return bitmap

    rows = len(bitmap)
    cols = len(bitmap[0])
    expanded = [[0 for _ in range(cols)] for _ in range(rows)]
    for r, row in enumerate(bitmap):
        for c, pixel in enumerate(row):
            if not pixel:
                continue
            for rr in range(max(0, r - radius), min(rows, r + radius + 1)):
                for cc in range(max(0, c - radius), min(cols, c + radius + 1)):
                    expanded[rr][cc] = 1
    return expanded


def calculate_tolerant_iou(
    bitmap_ref: list[list[int]],
    bitmap_drawn: list[list[int]],
    tolerance_radius: int = _IOU_TOLERANCE_RADIUS,
) -> float:
    """Calcula IoU após tolerar desvios de poucos pixels da escrita manual."""
    return calculate_iou(
        _dilate_bitmap(bitmap_ref, tolerance_radius),
        _dilate_bitmap(bitmap_drawn, tolerance_radius),
    )


def generate_diagnostic_overlay(
    bitmap_ref: list[list[int]],
    bitmap_drawn: list[list[int]],
    tolerance_radius: int = 0,
) -> dict[str, list[tuple[int, int]]]:
    """Gera o mapa de calor em 3 zonas de diagnóstico pedagógico:

    - hit_cells: Pixels onde o aluno cobriu a letra (Verde - Acerto).
    - miss_cells: Pixels da letra que não foram cobertos (Cinza - Omissão).
    - excess_cells: Pixels desenhados fora da área da letra (Vermelho - Excesso).
    """
    hits: list[tuple[int, int]] = []
    misses: list[tuple[int, int]] = []
    excess: list[tuple[int, int]] = []

    tolerated_ref = _dilate_bitmap(bitmap_ref, tolerance_radius)
    tolerated_drawn = _dilate_bitmap(bitmap_drawn, tolerance_radius)
    rows = len(bitmap_ref)
    cols = len(bitmap_ref[0]) if rows > 0 else 0

    for r in range(rows):
        for c in range(cols):
            vr = bitmap_ref[r][c]
            vd = bitmap_drawn[r][c]
            if vr == 1 and tolerated_drawn[r][c] == 1:
                hits.append((r, c))
            elif vr == 1:
                misses.append((r, c))
            elif vd == 1 and tolerated_ref[r][c] == 0:
                excess.append((r, c))

    return {
        "hit_cells": hits,
        "miss_cells": misses,
        "excess_cells": excess,
    }


def get_syllable_structure_label(char: str) -> str:
    """Retorna a classificação morfológica e estrutural do caractere coreano."""
    if is_hangul_jamo(char) or (len(char) == 1 and not is_hangul_syllable(char)):
        return "Jamo Individual (자모)"
    if is_hangul_syllable(char):
        decomp = decompose(char)
        if decomp.has_batchim:
            return "Bloco com Batchim (초성 + 중성 + 종성)"
        return "Consoante + Vogal (초성 + 중성)"
    return "Hangul (한글)"


# ============================================================
# Componente de Interface: CalligraphyWidget (Flet)
# ============================================================
class CalligraphyWidget(ft.Container):
    """Grade interativa 원고지 para prática de caligrafia Hangul (Wongoji Lab).

    Oferece escrita livre contínua, telemetria ao vivo, avaliação real por IoU
    e mapa visual de diagnóstico colorido (Acerto, Excesso, Omissão).
    """

    def __init__(
        self,
        target_char: str = "가",
        size: float = 240,
        is_dark: bool = False,
        show_ghost: bool = True,
        on_completed: Optional[Callable[[str, float], None]] = None,
        on_evaluated: Optional[Callable[[str, float, dict], None]] = None,
    ):
        super().__init__()
        self.target_char = target_char
        self.grid_size = size
        self.is_dark = is_dark
        self.show_ghost = show_ghost
        self.on_completed = on_completed
        self.on_evaluated = on_evaluated

        self.colors = get_theme_colors(is_dark)

        # Estado da escrita livre
        self.all_strokes: list[list[tuple[float, float]]] = []
        self.current_drawn_points: list[tuple[float, float]] = []
        self.sampled_points_count = 0
        self.stroke_count = 0
        self._current_stroke_samples = 0

        # Estado da avaliação e diagnóstico
        self.last_score: Optional[float] = None
        self.is_evaluated = False
        self.show_overlay = False
        self.diagnostic_data: Optional[dict[str, list[tuple[int, int]]]] = None

        # Montar UI
        self._build_ui()

    def _build_ui(self):
        """Monta a hierarquia de controles do widget."""
        # 1. Canvas de Desenho e Grade
        self.guide_canvas = cv.Canvas(
            shapes=self._generate_static_canvas_shapes(),
            width=self.grid_size,
            height=self.grid_size,
        )
        self.canvas_shapes = self._generate_dynamic_canvas_shapes()
        self.canvas = cv.Canvas(
            shapes=self.canvas_shapes,
            width=self.grid_size,
            height=self.grid_size,
        )
        self.drawing_surface = ft.Stack(
            controls=[self.guide_canvas, self.canvas],
            width=self.grid_size,
            height=self.grid_size,
        )

        # 2. GestureDetector para captura de toque livre
        self.gesture_detector = ft.GestureDetector(
            content=self.drawing_surface,
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
            on_pan_cancel=self._on_pan_cancel,
            # 60 fps limita as mensagens enviadas ao servidor sem gerar fila de
            # eventos durante a escrita, que deixava o pincel aparentemente preso.
            drag_interval=16,
            mouse_cursor=ft.MouseCursor.PRECISE,
        )

        # 3. Informações de Status e Controles
        self.status_text = ft.Text(
            self._get_status_label(),
            size=11,
            weight=ft.FontWeight.BOLD,
            color=self.colors["text_sec"],
        )

        self.btn_reset = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CLEANING_SERVICES_ROUNDED, size=15, color=self.colors["text"]),
                    ft.Text("Limpar", size=11, weight=ft.FontWeight.BOLD, color=self.colors["text"]),
                ],
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            style=ft.ButtonStyle(
                bgcolor=self.colors["card_bg"],
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
                side=ft.BorderSide(1, self.colors["border"]),
            ),
            tooltip="Limpar traços e recomeçar",
            on_click=lambda _: self.reset(),
        )

        self.btn_evaluate = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=15, color=ft.Colors.WHITE),
                    ft.Text("Avaliar Sílaba", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ],
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            style=ft.ButtonStyle(
                bgcolor=self.colors["primary"],
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                shape=ft.RoundedRectangleBorder(radius=Styles.BORDER_RADIUS_SM),
            ),
            tooltip="Avaliar a forma desenhada e gerar diagnóstico",
            on_click=lambda _: self.evaluate(),
        )

        self.btn_toggle_ghost = ft.IconButton(
            icon=ft.Icons.VISIBILITY if self.show_ghost else ft.Icons.VISIBILITY_OFF,
            icon_color=self.colors["secondary"],
            icon_size=18,
            visual_density=ft.VisualDensity.COMPACT,
            padding=2,
            tooltip="Mostrar/ocultar guia",
            on_click=lambda _: self.toggle_ghost(),
        )

        self.btn_toggle_overlay = ft.IconButton(
            icon=ft.Icons.PALETTE_OUTLINED,
            icon_color=self.colors["accent"],
            icon_size=18,
            visual_density=ft.VisualDensity.COMPACT,
            padding=2,
            tooltip="Alternar mapa de diagnóstico colorido",
            visible=False,
            on_click=lambda _: self.toggle_overlay(),
        )

        # 4. Mini-Dashboard de Telemetria e Diagnóstico
        self.metric_points_text = ft.Text("0", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.metric_strokes_text = ft.Text("0", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.metric_iou_text = ft.Text("Aguardando avaliação", size=10, weight=ft.FontWeight.BOLD, color="#FBBF24")
        self.metric_structure_text = ft.Text(get_syllable_structure_label(self.target_char), size=10, weight=ft.FontWeight.BOLD, color="#FDE68A")

        paper_bg = "#FAF8F5" if not self.is_dark else "#1C1917"
        paper_border = "#EF4444" if not self.is_dark else "#F87171"

        # Legenda explicativa de diagnóstico
        self.legend_row = ft.Row(
            controls=[
                ft.Row(controls=[ft.Container(width=8, height=8, bgcolor="#10B981", border_radius=2), ft.Text("Acerto", size=8, color="#A8A29E")], spacing=2),
                ft.Row(controls=[ft.Container(width=8, height=8, bgcolor="#EF4444", border_radius=2), ft.Text("Excesso", size=8, color="#A8A29E")], spacing=2),
                ft.Row(controls=[ft.Container(width=8, height=8, bgcolor="#94A3B8", border_radius=2), ft.Text("Faltou", size=8, color="#A8A29E")], spacing=2),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            visible=False,
        )

        self.dashboard_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Pontos:", size=9, color="#A8A29E"),
                                        self.metric_points_text,
                                    ],
                                    spacing=1,
                                ),
                                bgcolor="#292524",
                                padding=ft.Padding.symmetric(horizontal=6, vertical=3),
                                border_radius=4,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text("Traços:", size=9, color="#A8A29E"),
                                        self.metric_strokes_text,
                                    ],
                                    spacing=1,
                                ),
                                bgcolor="#292524",
                                padding=ft.Padding.symmetric(horizontal=6, vertical=3),
                                border_radius=4,
                                expand=True,
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text("Similaridade (IoU):", size=9, color="#D6D3D1"),
                                        self.metric_iou_text,
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Text("Estrutura:", size=9, color="#D6D3D1"),
                                        self.metric_structure_text,
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ],
                            spacing=1,
                        ),
                        bgcolor="#292524",
                        padding=ft.Padding.symmetric(horizontal=6, vertical=4),
                        border_radius=4,
                    ),
                    self.legend_row,
                ],
                spacing=3,
            ),
            width=self.grid_size,
            bgcolor="#1C1917",
            padding=5,
            border_radius=Styles.BORDER_RADIUS_SM,
        )

        # 5. Estrutura Principal
        self.content = ft.Column(
            controls=[
                # Célula Wongoji com papel de caligrafia tradicional
                ft.Container(
                    content=self.gesture_detector,
                    width=self.grid_size,
                    height=self.grid_size,
                    bgcolor=paper_bg,
                    border=ft.Border.all(2, paper_border),
                    border_radius=Styles.BORDER_RADIUS_MD,
                    shadow=Styles.CARD_SHADOW,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
                # Barra de Ações com Botões de Controle
                ft.Row(
                    controls=[
                        self.btn_reset,
                        ft.Row(
                            controls=[
                                self.btn_toggle_overlay,
                                self.btn_toggle_ghost,
                            ],
                            spacing=0,
                        ),
                        self.btn_evaluate,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=self.grid_size,
                ),
                # Mini Dashboard de Análise Silábica e Diagnóstico
                self.dashboard_card,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )

    def _get_status_label(self) -> str:
        if self.last_score is not None:
            pct = int(self.last_score * 100)
            if self.last_score >= 0.65:
                return f"🌟 Excelente! ({pct}%)"
            elif self.last_score >= 0.40:
                return f"✅ Bom traço! ({pct}%)"
            else:
                return f"🟠 Tente ajustar a forma ({pct}%)"
        if self.sampled_points_count > 0:
            return f"Desenhando ({self.stroke_count} traços)"
        return f"Escreva: {self.target_char}"

    def _generate_static_canvas_shapes(self, size: Optional[float] = None) -> list:
        """Gera a grade e o guia, que não devem ser reenviados a cada ponto."""
        shapes = []
        sz = size if size is not None else self.grid_size

        wongoji_border = "#EF4444" if not self.is_dark else "#F87171"
        wongoji_guide = "#F87171" if not self.is_dark else "#F87171"

        # ── Grade Wongoji (Moldura Externa e Cruz Central Pontilhada) ──
        shapes.append(
            cv.Rect(
                x=6, y=6,
                width=sz - 12, height=sz - 12,
                border_radius=4,
                paint=ft.Paint(color=wongoji_border, stroke_width=1.5, style=ft.PaintingStyle.STROKE),
            )
        )
        shapes.append(
            cv.Line(
                x1=sz / 2, y1=6,
                x2=sz / 2, y2=sz - 6,
                paint=ft.Paint(color=wongoji_guide, stroke_width=1, stroke_dash_pattern=[4, 4]),
            )
        )
        shapes.append(
            cv.Line(
                x1=6, y1=sz / 2,
                x2=sz - 6, y2=sz / 2,
                paint=ft.Paint(color=wongoji_guide, stroke_width=1, stroke_dash_pattern=[4, 4]),
            )
        )

        # ── Camada Modelo ──
        # O guia usa a Kyobo como texto vetorial para preservar seus contornos
        # manuscritos; a referência do IoU usa o mesmo arquivo de fonte via Pillow.
        if self.show_ghost and not self.show_overlay:
            ghost_color = "#E2E8F0" if not self.is_dark else "#3F3F46"
            shapes.append(
                cv.Text(
                    x=sz * 0.50,
                    y=sz * 0.48,
                    value=self.target_char,
                    alignment=ft.Alignment.CENTER,
                    style=ft.TextStyle(
                        size=sz * 0.68,
                        font_family="Kyobo Handwriting",
                        color=ghost_color,
                    ),
                )
            )

        return shapes

    def _generate_dynamic_canvas_shapes(self, size: Optional[float] = None) -> list:
        """Gera tinta e diagnóstico, as únicas camadas mutáveis durante o traço."""
        shapes = []
        sz = size if size is not None else self.grid_size
        stroke_width = sz * _RASTER_STROKE_WIDTH / _REFERENCE_BITMAP_SIZE
        stroke_color = "#1C1917" if not self.is_dark else "#F5F5F4"
        if self.show_overlay:
            stroke_color = "#1E293B"

        for stroke in self.all_strokes:
            if len(stroke) == 1:
                shapes.append(cv.Circle(x=stroke[0][0] * sz, y=stroke[0][1] * sz, radius=stroke_width / 2, paint=ft.Paint(color=stroke_color, style=ft.PaintingStyle.FILL)))
            else:
                for p1, p2 in zip(stroke, stroke[1:]):
                    shapes.append(cv.Line(x1=p1[0] * sz, y1=p1[1] * sz, x2=p2[0] * sz, y2=p2[1] * sz, paint=ft.Paint(color=stroke_color, stroke_width=stroke_width, stroke_cap=ft.StrokeCap.ROUND)))

        for p1, p2 in zip(self.current_drawn_points, self.current_drawn_points[1:]):
            shapes.append(cv.Line(x1=p1[0] * sz, y1=p1[1] * sz, x2=p2[0] * sz, y2=p2[1] * sz, paint=ft.Paint(color="#0D9488" if not self.is_dark else "#2DD4BF", stroke_width=stroke_width, stroke_cap=ft.StrokeCap.ROUND)))

        # O diagnóstico é a camada mais alta, para não ser encoberto pela tinta.
        if self.show_overlay and self.diagnostic_data:
            cell_sz = sz / _REFERENCE_BITMAP_SIZE
            for key, color in (("miss_cells", "#94A3B8"), ("excess_cells", "#EF4444"), ("hit_cells", "#10B981")):
                for r, c in self.diagnostic_data.get(key, []):
                    shapes.append(cv.Rect(x=c * cell_sz, y=r * cell_sz, width=cell_sz + 0.3, height=cell_sz + 0.3, paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL)))
        return shapes

    def _generate_canvas_shapes(self, size: Optional[float] = None) -> list:
        """Combina camadas para prévias estáticas fora do editor de escrita."""
        return self._generate_static_canvas_shapes(size) + self._generate_dynamic_canvas_shapes(size)

    def _extract_coords(self, e: Any) -> Optional[tuple[float, float]]:
        if hasattr(e, "local_position") and e.local_position is not None:
            return float(e.local_position.x), float(e.local_position.y)
        if hasattr(e, "local_x") and hasattr(e, "local_y"):
            return float(e.local_x), float(e.local_y)
        if hasattr(e, "x") and hasattr(e, "y"):
            return float(e.x), float(e.y)
        return None

    # ── Handlers de Gestos (Escrita Livre) ──
    def _on_pan_start(self, e: ft.DragStartEvent):
        coords = self._extract_coords(e)
        if not coords:
            return
        sz = self.grid_size
        norm_x = max(0.0, min(1.0, coords[0] / sz))
        norm_y = max(0.0, min(1.0, coords[1] / sz))
        self.current_drawn_points = [(norm_x, norm_y)]
        self.sampled_points_count += 1
        self.stroke_count += 1
        self._current_stroke_samples = 1

        self.metric_points_text.value = str(self.sampled_points_count)
        self.metric_strokes_text.value = str(self.stroke_count)
        self.metric_iou_text.value = "Desenhando..."
        self.metric_iou_text.color = ft.Colors.AMBER_400
        self.status_text.value = self._get_status_label()

        # Ocultar overlay se voltar a desenhar
        guide_changed = self.show_overlay
        if guide_changed:
            self.show_overlay = False
            self.btn_toggle_overlay.visible = False
            self.legend_row.visible = False

        self._refresh_canvas(refresh_guide=guide_changed)

    def _on_pan_update(self, e: ft.DragUpdateEvent):
        if not self.current_drawn_points:
            return
        coords = self._extract_coords(e)
        if not coords:
            return
        sz = self.grid_size
        norm_x = max(0.0, min(1.0, coords[0] / sz))
        norm_y = max(0.0, min(1.0, coords[1] / sz))
        self.current_drawn_points.append((norm_x, norm_y))
        self.sampled_points_count += 1
        self._current_stroke_samples += 1

        self.metric_points_text.value = str(self.sampled_points_count)
        self._refresh_canvas()

    def _on_pan_end(self, e: ft.DragEndEvent):
        if self.current_drawn_points:
            self.all_strokes.append(list(self.current_drawn_points))
            self.current_drawn_points = []
            self._current_stroke_samples = 0
            self.metric_iou_text.value = "Clique em Avaliar"
            self.metric_iou_text.color = "#FBBF24"
            self.status_text.value = self._get_status_label()
            self._refresh_canvas()

    def _on_pan_cancel(self, e: Any):
        """Descarta um traço interrompido por outro reconhecedor de gesto."""
        if self.current_drawn_points:
            self.sampled_points_count = max(0, self.sampled_points_count - self._current_stroke_samples)
            self.stroke_count = max(0, self.stroke_count - 1)
            self.metric_points_text.value = str(self.sampled_points_count)
            self.metric_strokes_text.value = str(self.stroke_count)
        self.current_drawn_points = []
        self._current_stroke_samples = 0
        self.status_text.value = self._get_status_label()
        self._refresh_canvas()

    def evaluate(self):
        """Avalia a forma desenhada contra o caractere de referência via Bitmap IoU."""
        if not self.all_strokes and not self.current_drawn_points:
            self.metric_iou_text.value = "Desenhe antes de avaliar"
            self.metric_iou_text.color = "#FB923C"
            self._refresh_canvas()
            return

        if self.current_drawn_points:
            self.all_strokes.append(list(self.current_drawn_points))
            self.current_drawn_points = []
            self._current_stroke_samples = 0

        # 1. Rasterizar bitmaps 48x48
        ref_bitmap = _get_reference_bitmap(self.target_char)
        drawn_bitmap = render_strokes_bitmap(
            self.all_strokes,
            size=_REFERENCE_BITMAP_SIZE,
            stroke_width=_RASTER_STROKE_WIDTH,
        )

        # 2. Calcular IoU e gerar diagnóstico
        score = calculate_tolerant_iou(
            ref_bitmap,
            drawn_bitmap,
            tolerance_radius=_IOU_TOLERANCE_RADIUS,
        )
        diag = generate_diagnostic_overlay(
            ref_bitmap,
            drawn_bitmap,
            tolerance_radius=_IOU_TOLERANCE_RADIUS,
        )

        self.last_score = score
        self.diagnostic_data = diag
        self.is_evaluated = True
        self.show_overlay = True
        self.btn_toggle_overlay.visible = True
        self.legend_row.visible = True

        pct = int(score * 100)
        self.metric_iou_text.value = f"{pct}% de similaridade"

        if score >= 0.65:
            self.metric_iou_text.color = "#34D399"
        elif score >= 0.40:
            self.metric_iou_text.color = "#FBBF24"
        else:
            self.metric_iou_text.color = "#FB923C"

        self.status_text.value = self._get_status_label()

        if self.on_evaluated:
            self.on_evaluated(self.target_char, score, diag)

        if score >= 0.40 and self.on_completed:
            self.on_completed(self.target_char, score)

        self._refresh_canvas(refresh_guide=True)

    def _refresh_canvas(self, refresh_guide: bool = False):
        self.canvas.shapes = self._generate_dynamic_canvas_shapes()
        if refresh_guide:
            self.guide_canvas.shapes = self._generate_static_canvas_shapes()
        try:
            self.update()
        except Exception:
            pass

    def reset(self):
        """Reinicia os traços e telemetria da grade."""
        self.all_strokes = []
        self.current_drawn_points = []
        self.sampled_points_count = 0
        self.stroke_count = 0
        self._current_stroke_samples = 0
        self.last_score = None
        self.is_evaluated = False
        self.show_overlay = False
        self.diagnostic_data = None
        self.btn_toggle_overlay.visible = False
        self.legend_row.visible = False

        self.status_text.value = self._get_status_label()
        self.metric_points_text.value = "0"
        self.metric_strokes_text.value = "0"
        self.metric_iou_text.value = "Aguardando avaliação"
        self.metric_iou_text.color = "#FBBF24"
        self.metric_structure_text.value = get_syllable_structure_label(self.target_char)
        self._refresh_canvas(refresh_guide=True)

    def toggle_ghost(self):
        """Alterna a exibição do caractere modelo (ghost)."""
        self.show_ghost = not self.show_ghost
        self.btn_toggle_ghost.icon = (
            ft.Icons.VISIBILITY if self.show_ghost else ft.Icons.VISIBILITY_OFF
        )
        self._refresh_canvas(refresh_guide=True)

    def toggle_overlay(self):
        """Alterna a exibição do mapa de diagnóstico colorido."""
        if not self.diagnostic_data:
            return
        self.show_overlay = not self.show_overlay
        self.legend_row.visible = self.show_overlay
        self._refresh_canvas(refresh_guide=True)

    def set_target_character(self, new_char: str):
        """Altera o caractere de treino."""
        self.target_char = new_char
        self.reset()
