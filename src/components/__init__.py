"""Componentes reutilizáveis da interface do Saebom Companion."""

from .hangul_card import HangulCard
from .layout import CONTENT_MAX_WIDTH, DEFAULT_VIEWPORT_WIDTH, centered_content
from .oclusive_lab import build_oclusive_lab
from .quiz_widget import QuizWidget
from .vocab_card import VocabCard
from .flashcard_widget import FlashcardWidget
from .sentence_builder_widget import SentenceBuilderWidget
from .wongoji_multi_cell_widget import WongojiMultiCellWidget
from .air_particle_effect import AirParticleEffect
from .syllable_factory import SyllableFactory
from .number_training import NumberTraining
from .spatial_stage import SpatialStage
from .whats_new_dialog import WhatsNewDialog
from .calligraphy_widget import (
    CalligraphyWidget,
    calculate_iou,
    generate_diagnostic_overlay,
    render_reference_bitmap,
    render_strokes_bitmap,
)

__all__ = [
    "CONTENT_MAX_WIDTH",
    "DEFAULT_VIEWPORT_WIDTH",
    "CalligraphyWidget",
    "WongojiMultiCellWidget",
    "HangulCard",
    "QuizWidget",
    "VocabCard",
    "FlashcardWidget",
    "SentenceBuilderWidget",
    "SyllableFactory",
    "NumberTraining",
    "SpatialStage",
    "AirParticleEffect",
    "WhatsNewDialog",
    "build_oclusive_lab",
    "calculate_iou",
    "generate_diagnostic_overlay",
    "render_reference_bitmap",
    "render_strokes_bitmap",
    "centered_content",
]
