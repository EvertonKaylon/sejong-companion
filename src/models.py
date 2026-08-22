import math
from collections import Counter
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator

# Curriculum Models
class Unit(BaseModel):
    id: str
    number: int
    title_kr: str
    title_pt: str
    description: str
    is_unlocked: bool
    progress: float
    book: Optional[str] = "1A"

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

class SovWordItem(BaseModel):
    """Palavra arrastável e seu papel sintático no exercício SOV."""
    word: str
    role: str
    snap_anchor: Optional[str] = "square"


class SovSlotDefinition(BaseModel):
    """Contrato semântico de um slot de montagem de frase."""
    role: str
    label: str
    accepted_roles: List[str]


def is_role_accepted(word_role: str, accepted_roles: List[str]) -> bool:
    """Retorna se o papel da palavra pode ser encaixado no slot.

    ``ANY`` é reservado para compatibilidade com conteúdos legados e não é
    usado pelos exercícios SOV semânticos.
    """
    return "ANY" in accepted_roles or word_role in accepted_roles

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
    # Metadados obrigatórios para a variante de drag-and-drop semântico.
    sov_items: Optional[List[SovWordItem]] = None
    sov_slots: Optional[List[SovSlotDefinition]] = None

    @model_validator(mode="after")
    def validate_sov_metadata(self):
        """Impede que uma questão SOV chegue à UI sem seu contrato semântico."""
        if self.type != "drag_and_drop_sov":
            return self
        if not self.sov_items or not self.sov_slots:
            raise ValueError("drag_and_drop_sov requer sov_items e sov_slots")
        if not self.correct_order:
            raise ValueError("drag_and_drop_sov requer correct_order")
        if len(self.sov_items) != len(self.sov_slots):
            raise ValueError("sov_items e sov_slots devem ter o mesmo tamanho")
        if Counter(item.word for item in self.sov_items) != Counter(self.correct_order):
            raise ValueError("correct_order deve conter exatamente as palavras de sov_items")
        if any(not slot.accepted_roles for slot in self.sov_slots):
            raise ValueError("todo slot SOV precisa aceitar ao menos um papel")
        item_roles = {item.role for item in self.sov_items}
        for slot in self.sov_slots:
            if "ANY" not in slot.accepted_roles and not item_roles.intersection(slot.accepted_roles):
                raise ValueError(f"slot SOV sem papel disponível: {slot.label}")
        return self

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


# ─── Memory / SRS (Modelo Heurístico de Retenção Baseado em Meia-Vida) ───

class MemoryNode(BaseModel):
    """Entidade central do Modelo Heurístico de Retenção Baseado em Meia-Vida.
    
    Modela o decaimento temporal inspirado na curva de esquecimento exponencial:
      R = 2^(-t / h)
    onde R é a retenção estimada (0.0–1.0), t o tempo decorrido e h a meia-vida (em dias).
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
        self.half_life = max(0.2, self.half_life)
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


# ─── Active recall / flashcards ───

class FlashcardItem(BaseModel):
    """Cartão de estudo derivado do conteúdo oficial de uma unidade.

    O conteúdo continua sendo data-driven (``data/units``); este modelo apenas
    apresenta uma forma uniforme para a revisão espaçada e a interface.
    """
    id: str
    unit_id: str
    korean: str
    portuguese: str
    difficulty: str  # easy | medium | hard
    category: str = "vocabulário"
    example_kr: Optional[str] = None
    example_pt: Optional[str] = None
    lusophone_tip: Optional[str] = None
    sov_breakdown: Optional[List[dict]] = None


class ReviewSessionState(BaseModel):
    """Estado serializável de uma sessão de revisão diária."""
    due_cards: List[FlashcardItem] = []
    current_index: int = 0
    streak: int = 0
    xp_earned: int = 0
    history: List[dict] = []


# ─── Telemetria Pedagógica Local (Zero PII) ───

class PedagogicalEvent(BaseModel):
    """Evento atômico de interação pedagógica para calibração do algoritmo adaptativo.
    
    Zero PII (dados pessoais): armazena exclusivamente identificadores didáticos,
    métricas de desempenho (tempo de resposta, acertos, autoavaliações) e timestamps.
    """
    event_type: str  # ex: 'question_answered', 'flashcard_rated', 'lesson_opened', 'quiz_completed'
    unit_id: str  # ex: 'unit_01'
    item_id: Optional[str] = None  # ex: 'unit_01:vocab:03', 'u01_q01'
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    payload: Dict[str, Any] = Field(default_factory=dict)

