import math
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

# Curriculum Models
class Unit(BaseModel):
    id: str
    number: int
    title_kr: str
    title_pt: str
    description: str
    is_unlocked: bool
    progress: float

# ─── Hangul Models (Unit Intro) ───

class AntiRomanizationNotice(BaseModel):
    """Aviso pedagógico sobre a ausência intencional de romanização."""
    title: str
    content: str
    icon: str

class HangulVowel(BaseModel):
    char: str
    name: str  # Nome em 한글 (ex: 아, 어, 오)
    pronunciation: str  # Descrição fonética em português
    mnemonic: str
    audio_wave_profile: Optional[str] = "default"
    mouth_shape_id: Optional[str] = None
    contrast_pair_id: Optional[str] = None

class HangulConsonant(BaseModel):
    char: str
    name: str  # Nome em 한글 (ex: 기역, 니은)
    pronunciation: str  # Descrição fonética em português
    type: Optional[str] = "plain"
    base: Optional[str] = None  # Para aspiradas/tensas, a consoante base
    audio_wave_profile: Optional[str] = "default"
    mouth_shape_id: Optional[str] = None
    contrast_pair_id: Optional[str] = None

class HangulSyllable(BaseModel):
    block: str
    spelling: str
    meaning: str
    snap_anchor: Optional[str] = "square"

class NeutralizationRule(BaseModel):
    position: str
    batchim_chars: List[str]
    sound: str
    tip: str
    example_word: Optional[str] = None
    example_meaning: Optional[str] = None

class LusophoneWarning(BaseModel):
    title: str
    content: str
    icon: str

class BatchimGuide(BaseModel):
    title: str
    explanation: str
    lusophone_warning: Optional[LusophoneWarning] = None
    neutralization_rules: List[NeutralizationRule]

class WritingAlert(BaseModel):
    title: str
    content: str
    icon: str

# ─── Quiz Models (Genérico — suporta múltiplos tipos) ───

class QuizQuestion(BaseModel):
    """Modelo unificado de questão de quiz.
    - type='multiple_choice': usa options + correct_index
    - type='order_words': usa words + correct_order
    - type='drag_and_drop_sov': usa words + correct_order
    """
    id: str
    type: str  # 'multiple_choice' | 'order_words' | 'drag_and_drop_sov'
    question: str
    explanation: Optional[str] = ""
    # Campos para multiple_choice
    options: Optional[List[str]] = None
    correct_index: Optional[int] = None
    # Campos para order_words / drag_and_drop_sov (unscrambling)
    words: Optional[List[str]] = None
    correct_order: Optional[List[str]] = None

class UnitIntroData(BaseModel):
    unit_id: str
    title: str
    anti_romanization_notice: Optional[AntiRomanizationNotice] = None
    vowels: List[HangulVowel]
    consonants: List[HangulConsonant]
    aspirated_consonants: Optional[List[HangulConsonant]] = []
    tense_consonants: Optional[List[HangulConsonant]] = []
    batchim_guide: Optional[BatchimGuide] = None
    syllables: List[HangulSyllable]
    writing_alert: Optional[WritingAlert] = None
    exercises: List[QuizQuestion]

# ─── Unit 1+ Models ───

class VocabItem(BaseModel):
    """Item de vocabulário — SEM romanização, conforme metodologia Sejong."""
    word: str
    meaning: str
    example_kr: str
    example_pt: str
    category: Optional[str] = None
    neuro_tip: Optional[str] = None
    snap_anchor: Optional[str] = None  # "square" (com 받침) | "round" (com vogal)
    magnetic_slot_role: Optional[str] = None  # "SUBJECT" | "OBJECT" | "VERB" | "PARTICLE" | "PREDICATE"

class GrammarExample(BaseModel):
    kr: str
    pt: str

class GrammarSection(BaseModel):
    id: Optional[str] = None
    title: str
    explanation: str
    examples: List[GrammarExample]
    lusophone_tip: Optional[str] = None

class CulturalNote(BaseModel):
    title: str
    content: str
    icon: str

class UnitOneData(BaseModel):
    unit_id: str
    title: str
    vocabulary: List[VocabItem]
    grammar: List[GrammarSection]
    cultural_notes: Optional[List[CulturalNote]] = []
    exercises: List[QuizQuestion]

# Alias genérico: qualquer unidade 01–10 usa o mesmo schema
UnitData = UnitOneData


# ─── Memory / SRS (Half-Life Regression de Ebbinghaus) ───

class MemoryNode(BaseModel):
    """Entidade central do Algoritmo Half-Life Regression (HLR).
    
    Modela a curva de esquecimento de Ebbinghaus:
      R = 2^(-t / h)
    onde R é a retenção (0–1), t o tempo decorrido e h a meia-vida.
    """
    unit_id: str
    half_life: float = 5.0          # Meia-vida em dias
    last_reviewed: str = ""         # ISO timestamp
    error_count: int = 0

    def calculate_stability(self, now: Optional[datetime] = None) -> float:
        """Retorna o nível de retenção atual (0.0 a 1.0)."""
        if not self.last_reviewed:
            return 0.0
        now = now or datetime.now()
        try:
            last = datetime.fromisoformat(self.last_reviewed)
        except (ValueError, TypeError):
            return 0.0
        elapsed_seconds = (now - last).total_seconds()
        half_life_seconds = self.half_life * 24 * 60 * 60
        if half_life_seconds <= 0:
            return 0.0
        stability = math.pow(2, -elapsed_seconds / half_life_seconds)
        return max(0.0, min(1.0, stability))

    def update_performance(self, is_correct: bool, response_time_ms: int = 2000) -> None:
        """Atualiza o nó com base na performance do Active Recall."""
        speed_factor = 1.0 / (1.0 + (response_time_ms / 2000.0))
        if is_correct:
            self.half_life = self.half_life * (1.5 + (1.2 * speed_factor))
            if self.error_count > 0:
                self.error_count -= 1
        else:
            self.error_count += 1
            self.half_life = self.half_life * (0.3 / (self.error_count * 0.5))
        self.half_life = max(0.01, self.half_life)
        self.last_reviewed = datetime.now().isoformat()

    def vitality_level(self, now: Optional[datetime] = None) -> str:
        """Retorna 'high', 'medium' ou 'low' baseado na retenção."""
        s = self.calculate_stability(now)
        if s >= 0.75:
            return "high"
        elif s >= 0.35:
            return "medium"
        else:
            return "low"
