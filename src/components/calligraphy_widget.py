"""Widget de Grade de Caligrafia 원고지 (Wongoji) com reconhecimento de traços.

Permite que os alunos pratiquem a escrita de Jamo e sílabas Hangul completas
sobre uma grade de manuscrito tradicional coreana (원고지) com validação
de ordem e direção de traços (Stroke Order) em tempo real.
"""

from __future__ import annotations

import json
import math
import os
from typing import Callable, Optional

import flet as ft
import flet.canvas as cv

from ..jamo_utils import (
    BlockType,
    JAMO_TO_FILENAME,
    decompose,
    get_jamo_layout,
    is_hangul_jamo,
    is_hangul_syllable,
)
from ..theme import Colors, Styles, get_theme_colors


# ============================================================
# Carregador de Dados de Traços (Singleton em memória)
# ============================================================
_STROKE_DATA_CACHE: Optional[dict] = None


def load_stroke_dataset() -> dict:
    """Carrega os dados de stroke order de assets/stroke_order/jamo_strokes.json."""
    global _STROKE_DATA_CACHE
    if _STROKE_DATA_CACHE is not None:
        return _STROKE_DATA_CACHE

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "..", "assets", "stroke_order", "jamo_strokes.json")

    if not os.path.exists(data_path):
        # Fallback se executado de outro diretório de trabalho
        data_path = os.path.join("assets", "stroke_order", "jamo_strokes.json")

    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            _STROKE_DATA_CACHE = json.load(f)
    else:
        _STROKE_DATA_CACHE = {"consonants": {}, "vowels": {}}

    return _STROKE_DATA_CACHE


def get_reference_strokes(char: str) -> list[list[tuple[float, float]]]:
    """Retorna a lista de traços de referência para um Jamo ou Sílaba Hangul.

    Para um Jamo individual (ex: 'ㄱ', 'ㅏ'):
      Retorna as coordenadas normalizadas [0.0, 1.0] dentro da célula.

    Para uma Sílaba Hangul composta (ex: '한'):
      Decompõe em Jamo e projeta cada traço nos slots geométricos do bloco (CV/CVC).

    Returns:
        Lista de traços, onde cada traço é uma lista de pontos (x, y) no intervalo [0.0, 1.0].
    """
    dataset = load_stroke_dataset()
    consonants = dataset.get("consonants", {})
    vowels = dataset.get("vowels", {})

    def _get_jamo_raw_strokes(j: str) -> list[list[tuple[float, float]]]:
        fname = JAMO_TO_FILENAME.get(j, "")
        if fname in consonants:
            return [[(pt[0], pt[1]) for pt in stroke] for stroke in consonants[fname]["strokes"]]
        elif fname in vowels:
            return [[(pt[0], pt[1]) for pt in stroke] for stroke in vowels[fname]["strokes"]]
        return []

    # 1. Jamo individual
    if is_hangul_jamo(char) or len(char) == 1 and not is_hangul_syllable(char):
        return _get_jamo_raw_strokes(char)

    # 2. Sílaba composta
    if is_hangul_syllable(char):
        decomp = decompose(char)
        layout = get_jamo_layout(decomp.block_type)
        all_projected_strokes: list[list[tuple[float, float]]] = []

        parts = [
            ("choseong", decomp.choseong),
            ("jungseong", decomp.jungseong),
        ]
        if decomp.has_batchim:
            parts.append(("jongseong", decomp.jongseong))

        for part_name, jamo in parts:
            if part_name not in layout:
                continue
            box = layout[part_name]
            bx, by, bw, bh = box["x"], box["y"], box["w"], box["h"]
            raw_strokes = _get_jamo_raw_strokes(jamo)

            for raw_stroke in raw_strokes:
                proj_stroke = [
                    (bx + pt[0] * bw, by + pt[1] * bh)
                    for pt in raw_stroke
                ]
                all_projected_strokes.append(proj_stroke)

        return all_projected_strokes

    return []


# ============================================================
# Algoritmo de Validação de Traço (Path Matching & Distância)
# ============================================================
def calculate_stroke_similarity(
    drawn_points: list[tuple[float, float]],
    reference_points: list[tuple[float, float]],
    tolerance: float = 0.30,
) -> tuple[bool, float]:
    """Calcula a similaridade entre os pontos desenhados pelo aluno e o traço de referência.

    Verifica:
      1. Proximidade do ponto inicial (start point)
      2. Proximidade do ponto final (end point)
      3. Coerência direcional (vetor geral do traço)
      4. Distância média ponto-segmento ao longo da trajetória

    Args:
        drawn_points: Pontos capturados do toque [(x, y), ...] normalizados [0.0, 1.0].
        reference_points: Pontos do traço de referência [(x, y), ...].
        tolerance: Limiar de tolerância normalizada (padrão 0.30).

    Returns:
        (is_valid, similarity_score_0_to_1)
    """
    if len(drawn_points) < 2 or len(reference_points) < 2:
        return False, 0.0

    # 1. Ponto Inicial e Ponto Final
    d_start = drawn_points[0]
    d_end = drawn_points[-1]
    r_start = reference_points[0]
    r_end = reference_points[-1]

    dist_start = math.hypot(d_start[0] - r_start[0], d_start[1] - r_start[1])
    dist_end = math.hypot(d_end[0] - r_end[0], d_end[1] - r_end[1])

    # 2. Vetores de Direção
    d_vx = d_end[0] - d_start[0]
    d_vy = d_end[1] - d_start[1]
    r_vx = r_end[0] - r_start[0]
    r_vy = r_end[1] - r_start[1]

    d_len = math.hypot(d_vx, d_vy)
    r_len = math.hypot(r_vx, r_vy)

    # Penalidade se o traço foi desenhado na direção invertida
    dot_product = (d_vx * r_vx + d_vy * r_vy) if (d_len > 0.01 and r_len > 0.01) else 1.0
    cos_sim = dot_product / (d_len * r_len) if (d_len > 0.01 and r_len > 0.01) else 1.0

    if cos_sim < -0.2:
        # Traço desenhado claramente no sentido oposto (ex: baixo para cima ao invés de cima para baixo)
        return False, 0.2

    # 3. Distância média dos pontos desenhados para a polilinha de referência
    total_dist = 0.0
    for px, py in drawn_points:
        min_seg_dist = float("inf")
        for i in range(len(reference_points) - 1):
            ax, ay = reference_points[i]
            bx, by = reference_points[i + 1]
            seg_len_sq = (bx - ax) ** 2 + (by - ay) ** 2
            if seg_len_sq < 1e-6:
                d = math.hypot(px - ax, py - ay)
            else:
                t = max(0.0, min(1.0, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / seg_len_sq))
                proj_x = ax + t * (bx - ax)
                proj_y = ay + t * (by - ay)
                d = math.hypot(px - proj_x, py - proj_y)
            if d < min_seg_dist:
                min_seg_dist = d
        total_dist += min_seg_dist

    avg_dist = total_dist / len(drawn_points)

    # Score de 0.0 a 1.0 (1.0 = perfeito, 0.0 = fora do alvo)
    combined_error = (dist_start * 0.35 + dist_end * 0.35 + avg_dist * 0.30)
    score = max(0.0, 1.0 - (combined_error / tolerance))

    is_valid = combined_error <= tolerance and score >= 0.40
    return is_valid, round(score, 3)


# ============================================================
def get_syllable_structure_label(char: str) -> str:
    """Retorna a classificação morfológica e estrutural do caractere coreano."""
    if is_hangul_jamo(char) or len(char) == 1 and not is_hangul_syllable(char):
        dataset = load_stroke_dataset()
        fname = JAMO_TO_FILENAME.get(char, "")
        if fname in dataset.get("consonants", {}):
            return "Consoante Inicial (초성)"
        elif fname in dataset.get("vowels", {}):
            return "Vogal Medial (중성)"
        return "Jamo Individual"
    if is_hangul_syllable(char):
        decomp = decompose(char)
        if decomp.has_batchim:
            return "Bloco com Batchim (초성+중성+종성)"
        return "Consoante + Vogal (초성+중성)"
    return "Hangul (한글)"


# ============================================================
# Componente de Interface: CalligraphyWidget (Flet)
# ============================================================
class CalligraphyWidget(ft.Container):
    """Grade interativa 원고지 para prática de caligrafia Hangul.

    Renderiza uma célula tradicional de papel manuscrito coreano com
    linhas guia em coral/rubi, dashboard de telemetria silábica em tempo
    real e validação tátil contínua com feedback sonoro.
    """

    def __init__(
        self,
        target_char: str = "가",
        size: float = 240,
        is_dark: bool = False,
        show_ghost: bool = True,
        on_completed: Optional[Callable[[str, float], None]] = None,
        on_stroke_validated: Optional[Callable[[int, int, bool], None]] = None,
    ):
        super().__init__()
        self.target_char = target_char
        self.grid_size = size
        self.is_dark = is_dark
        self.show_ghost = show_ghost
        self.on_completed = on_completed
        self.on_stroke_validated = on_stroke_validated

        self.colors = get_theme_colors(is_dark)

        # Estado dos traços e telemetria
        self.reference_strokes = get_reference_strokes(self.target_char)
        self.current_stroke_index = 0
        self.completed_strokes: list[list[tuple[float, float]]] = []
        self.current_drawn_points: list[tuple[float, float]] = []
        self.is_completed = False
        self.scores: list[float] = []
        self.sampled_points_count = 0

        # Inicializar UI
        self._build_ui()

    def _build_ui(self):
        """Monta a hierarquia de controles do widget."""
        # 1. Canvas de Desenho e Grade
        self.canvas_shapes = self._generate_canvas_shapes()
        self.canvas = cv.Canvas(
            shapes=self.canvas_shapes,
            width=self.grid_size,
            height=self.grid_size,
        )

        # 2. GestureDetector para captura de toque
        self.gesture_detector = ft.GestureDetector(
            content=self.canvas,
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
            drag_interval=10,
            mouse_cursor=ft.MouseCursor.PRECISE,
        )

        # 3. Informações de Status e Controles
        self.status_text = ft.Text(
            self._get_status_label(),
            size=11,
            weight=ft.FontWeight.BOLD,
            color=self.colors["text_sec"],
        )

        self.btn_reset = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_color=self.colors["primary"],
            icon_size=20,
            visual_density=ft.VisualDensity.COMPACT,
            padding=2,
            tooltip="Limpar e recomeçar",
            on_click=lambda _: self.reset(),
        )

        self.btn_toggle_ghost = ft.IconButton(
            icon=ft.Icons.VISIBILITY if self.show_ghost else ft.Icons.VISIBILITY_OFF,
            icon_color=self.colors["secondary"],
            icon_size=20,
            visual_density=ft.VisualDensity.COMPACT,
            padding=2,
            tooltip="Mostrar/ocultar guia",
            on_click=lambda _: self.toggle_ghost(),
        )

        # 4. Mini-Dashboard de Telemetria Silábica (Estilo Laboratório Wongoji)
        self.metric_points_text = ft.Text("0", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.metric_strokes_text = ft.Text(f"0/{len(self.reference_strokes)}", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.metric_dtw_text = ft.Text("Aguardando traço", size=10, weight=ft.FontWeight.BOLD, color="#FBBF24")
        self.metric_structure_text = ft.Text(get_syllable_structure_label(self.target_char), size=10, weight=ft.FontWeight.BOLD, color="#FDE68A")

        paper_bg = "#FAF8F5" if not self.is_dark else "#1C1917"
        paper_border = "#EF4444" if not self.is_dark else "#F87171"

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
                                        ft.Text("Ordem (DTW):", size=9, color="#D6D3D1"),
                                        self.metric_dtw_text,
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
                # Barra inferior de controles
                ft.Row(
                    controls=[
                        self.status_text,
                        ft.Row(
                            controls=[
                                self.btn_toggle_ghost,
                                self.btn_reset,
                            ],
                            spacing=0,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=self.grid_size,
                ),
                # Mini Dashboard de Análise Silábica
                self.dashboard_card,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=3,
        )

    def _get_status_label(self) -> str:
        total = len(self.reference_strokes)
        if self.is_completed:
            avg_score = int((sum(self.scores) / max(1, len(self.scores))) * 100)
            return f"✅ Concluído! Precisão: {avg_score}%"
        if total == 0:
            return f"Escreva: {self.target_char}"
        current = min(self.current_stroke_index + 1, total)
        return f"Traço {current} de {total}"

    def _generate_canvas_shapes(self) -> list:
        """Gera as formas do Canvas: linhas da grade 원고지, ghost e traços desenhados."""
        shapes = []
        sz = self.grid_size

        # Cores tradicionais da grade 원고지 (Paper & Coral)
        wongoji_border = "#EF4444" if not self.is_dark else "#F87171"
        wongoji_guide = "#F87171" if not self.is_dark else "#F87171"
        ink_color = "#1C1917" if not self.is_dark else "#F5F5F4"

        # ── Grade Wongoji (Moldura Externa e Cruz Central Pontilhada) ──
        # Moldura interna de margem tradicional
        shapes.append(
            cv.Rect(
                x=6, y=6,
                width=sz - 12, height=sz - 12,
                border_radius=4,
                paint=ft.Paint(color=wongoji_border, stroke_width=1.5, style=ft.PaintingStyle.STROKE),
            )
        )
        # Linha vertical central pontilhada
        shapes.append(
            cv.Line(
                x1=sz / 2, y1=6,
                x2=sz / 2, y2=sz - 6,
                paint=ft.Paint(color=wongoji_guide, stroke_width=1, stroke_dash_pattern=[4, 4]),
            )
        )
        # Linha horizontal central pontilhada
        shapes.append(
            cv.Line(
                x1=6, y1=sz / 2,
                x2=sz - 6, y2=sz / 2,
                paint=ft.Paint(color=wongoji_guide, stroke_width=1, stroke_dash_pattern=[4, 4]),
            )
        )

        # ── Camada Modelo (Ghost) ──
        if self.show_ghost and not self.is_completed:
            ghost_color = "#E2E8F0" if not self.is_dark else "#3F3F46"
            active_ghost_color = "#FB7185" if not self.is_dark else "#FDA4AF"

            for idx, stroke in enumerate(self.reference_strokes):
                is_active = (idx == self.current_stroke_index)
                color = active_ghost_color if is_active else ghost_color
                width = 5 if is_active else 3

                # Desenhar linha do traço de referência
                for i in range(len(stroke) - 1):
                    p1 = stroke[i]
                    p2 = stroke[i + 1]
                    shapes.append(
                        cv.Line(
                            x1=p1[0] * sz, y1=p1[1] * sz,
                            x2=p2[0] * sz, y2=p2[1] * sz,
                            paint=ft.Paint(
                                color=color,
                                stroke_width=width,
                                stroke_cap=ft.StrokeCap.ROUND,
                            ),
                        )
                    )

                # Ponto de início (start dot) no traço ativo
                if is_active and len(stroke) > 0:
                    start_pt = stroke[0]
                    shapes.append(
                        cv.Circle(
                            x=start_pt[0] * sz,
                            y=start_pt[1] * sz,
                            radius=5.5,
                            paint=ft.Paint(color="#EF4444", style=ft.PaintingStyle.FILL),
                        )
                    )

        # ── Traços Já Validados com Sucesso (Tinta Caligráfica) ──
        for completed_stroke in self.completed_strokes:
            for i in range(len(completed_stroke) - 1):
                p1 = completed_stroke[i]
                p2 = completed_stroke[i + 1]
                shapes.append(
                    cv.Line(
                        x1=p1[0] * sz, y1=p1[1] * sz,
                        x2=p2[0] * sz, y2=p2[1] * sz,
                        paint=ft.Paint(
                            color=ink_color,
                            stroke_width=6,
                            stroke_cap=ft.StrokeCap.ROUND,
                        ),
                    )
                )

        # ── Traço Atual Sendo Desenhado em Tempo Real (Teal/Emerald) ──
        if len(self.current_drawn_points) > 1:
            for i in range(len(self.current_drawn_points) - 1):
                p1 = self.current_drawn_points[i]
                p2 = self.current_drawn_points[i + 1]
                shapes.append(
                    cv.Line(
                        x1=p1[0] * sz, y1=p1[1] * sz,
                        x2=p2[0] * sz, y2=p2[1] * sz,
                        paint=ft.Paint(
                            color="#0D9488" if not self.is_dark else "#2DD4BF",
                            stroke_width=5.5,
                            stroke_cap=ft.StrokeCap.ROUND,
                        ),
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

    # ── Handlers de Gestos (Toque / Mouse) ──
    def _on_pan_start(self, e: ft.DragStartEvent):
        if self.is_completed:
            return
        coords = self._extract_coords(e)
        if not coords:
            return
        sz = self.grid_size
        norm_x = max(0.0, min(1.0, coords[0] / sz))
        norm_y = max(0.0, min(1.0, coords[1] / sz))
        self.current_drawn_points = [(norm_x, norm_y)]
        self.sampled_points_count += 1
        self.metric_points_text.value = str(self.sampled_points_count)
        self.metric_dtw_text.value = "Desenhando..."
        self.metric_dtw_text.color = ft.Colors.AMBER_400
        self._refresh_canvas()

    def _on_pan_update(self, e: ft.DragUpdateEvent):
        if self.is_completed or not self.current_drawn_points:
            return
        coords = self._extract_coords(e)
        if not coords:
            return
        sz = self.grid_size
        norm_x = max(0.0, min(1.0, coords[0] / sz))
        norm_y = max(0.0, min(1.0, coords[1] / sz))
        self.current_drawn_points.append((norm_x, norm_y))
        self.sampled_points_count += 1
        self.metric_points_text.value = str(self.sampled_points_count)
        self._refresh_canvas()

    def _on_pan_end(self, e: ft.DragEndEvent):
        if self.is_completed or not self.current_drawn_points:
            return

        total_strokes = len(self.reference_strokes)
        if self.current_stroke_index < total_strokes:
            validated_count = 0
            best_score = 0.0

            # 1. Tentar validar traço individual atual
            ref_stroke = self.reference_strokes[self.current_stroke_index]
            is_valid, score = calculate_stroke_similarity(
                self.current_drawn_points, ref_stroke, tolerance=0.36
            )
            if is_valid:
                validated_count = 1
                best_score = score
            else:
                # 2. Reconhecimento Fluido Contínuo: testar se o usuário fez múltiplos traços contínuos juntos
                for m in range(2, total_strokes - self.current_stroke_index + 1):
                    sub_strokes = self.reference_strokes[self.current_stroke_index : self.current_stroke_index + m]
                    combined_ref = []
                    for s in sub_strokes:
                        combined_ref.extend(s)

                    is_comb_valid, comb_score = calculate_stroke_similarity(
                        self.current_drawn_points, combined_ref, tolerance=0.40
                    )
                    if is_comb_valid:
                        validated_count = m
                        best_score = comb_score
                        break

            if validated_count > 0:
                self.completed_strokes.append(list(self.current_drawn_points))
                for _ in range(validated_count):
                    self.scores.append(best_score)
                self.current_stroke_index += validated_count

                if self.on_stroke_validated:
                    self.on_stroke_validated(
                        self.current_stroke_index, total_strokes, True
                    )

                self.metric_strokes_text.value = f"{self.current_stroke_index}/{total_strokes}"
                self.metric_dtw_text.value = f"Aprovado ({int(best_score * 100)}%)"
                self.metric_dtw_text.color = "#34D399"

                # Verificar se todos os traços foram completados
                if self.current_stroke_index >= total_strokes:
                    self.is_completed = True
                    avg_score = sum(self.scores) / max(1, len(self.scores))
                    self.metric_dtw_text.value = f"Concluído ({int(avg_score * 100)}%)"
                    self.metric_dtw_text.color = "#34D399"
                    if self.on_completed:
                        self.on_completed(self.target_char, round(avg_score, 3))
            else:
                self.metric_dtw_text.value = "Tente novamente"
                self.metric_dtw_text.color = "#FB923C"
                if self.on_stroke_validated:
                    self.on_stroke_validated(
                        self.current_stroke_index, total_strokes, False
                    )

        self.current_drawn_points = []
        self.status_text.value = self._get_status_label()
        self._refresh_canvas()

    def _refresh_canvas(self):
        self.canvas.shapes = self._generate_canvas_shapes()
        try:
            self.update()
        except Exception:
            pass

    def reset(self):
        """Reinicia o exercício de caligrafia atual."""
        total_strokes = len(self.reference_strokes)
        self.current_stroke_index = 0
        self.completed_strokes = []
        self.current_drawn_points = []
        self.is_completed = False
        self.scores = []
        self.sampled_points_count = 0
        self.status_text.value = self._get_status_label()
        self.metric_points_text.value = "0"
        self.metric_strokes_text.value = f"0/{total_strokes}"
        self.metric_dtw_text.value = "Aguardando traço"
        self.metric_dtw_text.color = "#FBBF24"
        self.metric_structure_text.value = get_syllable_structure_label(self.target_char)
        self._refresh_canvas()

    def toggle_ghost(self):
        """Alterna a exibição das linhas modelo (ghost layer)."""
        self.show_ghost = not self.show_ghost
        self.btn_toggle_ghost.icon = (
            ft.Icons.VISIBILITY if self.show_ghost else ft.Icons.VISIBILITY_OFF
        )
        self._refresh_canvas()

    def set_target_character(self, new_char: str):
        """Altera o caractere de treino."""
        self.target_char = new_char
        self.reference_strokes = get_reference_strokes(new_char)
        self.reset()
