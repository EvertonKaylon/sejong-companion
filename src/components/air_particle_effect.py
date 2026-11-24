"""Simulador 2D Canvas de Rajada de Ar para Consoantes Aspiradas Coreanas (VOT > 70ms).

Para consoantes aspiradas (ㅋ, ㅌ, ㅍ, ㅊ), a explosão de ar pulmonar é projetada
como partículas radiais que se expandem e dissipam em milissegundos.
"""

import asyncio
import math
import random
from typing import List
import flet as ft


class AirParticleEffect(ft.Container):
    """Componente Canvas para visualização de sopro de ar em consoantes aspiradas."""

    def __init__(
        self,
        base_color: str = "#38BDF8",
        box_width: int = 100,
        num_particles: int = 10,
    ):
        self.base_color = base_color
        self.box_width = box_width
        self.num_particles = num_particles
        self.is_animating = False
        self.shapes: List[ft.canvas.Circle] = []

        self._init_shapes()

        self.canvas = ft.canvas.Canvas(
            shapes=self.shapes,
            width=self.box_width,
            height=self.box_width,
        )

        super().__init__(
            content=self.canvas,
            width=self.box_width,
            height=self.box_width,
            alignment=ft.Alignment.CENTER,
        )

    def _init_shapes(self):
        """Inicializa os círculos de partículas na origem central com opacidade zero."""
        self.shapes.clear()
        cx = self.box_width / 2.0
        cy = self.box_width / 2.0

        for _ in range(self.num_particles):
            circle = ft.canvas.Circle(
                x=cx,
                y=cy,
                radius=3.0,
                paint=ft.Paint(
                    color=ft.Colors.with_opacity(0.0, self.base_color),
                    style=ft.PaintingStyle.FILL,
                ),
            )
            self.shapes.append(circle)

    async def emit(self, steps: int = 10, duration_ms: int = 80):
        """Dispara uma explosão radial de partículas simulando a rajada de ar aspirada."""
        if self.is_animating:
            return
        self.is_animating = True
        cx = self.box_width / 2.0
        cy = self.box_width / 2.0
        max_dist = self.box_width * 0.42

        try:
            # Gerar vetores de dispersão angular para cada partícula
            particles_data = []
            for i in range(self.num_particles):
                angle = (2.0 * math.pi * i / self.num_particles) + (random.uniform(-0.25, 0.25))
                speed = random.uniform(0.65, 1.0)
                particles_data.append((angle, speed))

            interval = (duration_ms / 1000.0) / max(steps, 1)

            for step in range(steps):
                progress = (step + 1) / steps
                opacity_val = max(0.0, min(1.0, 1.0 - progress))

                for idx, circle in enumerate(self.shapes):
                    angle, speed = particles_data[idx]
                    curr_dist = max_dist * progress * speed
                    circle.x = cx + math.cos(angle) * curr_dist
                    circle.y = cy + math.sin(angle) * curr_dist
                    circle.radius = 3.0 * (1.0 + 0.5 * progress)
                    circle.paint.color = ft.Colors.with_opacity(opacity_val, self.base_color)

                try:
                    self.update()
                except Exception:
                    pass

                await asyncio.sleep(interval)
        finally:
            # Reset final
            for circle in self.shapes:
                circle.x = cx
                circle.y = cy
                circle.radius = 3.0
                circle.paint.color = ft.Colors.with_opacity(0.0, self.base_color)

            self.is_animating = False
            try:
                self.update()
            except Exception:
                pass
