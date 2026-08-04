from typing import List, Optional
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
    """
    id: str
    type: str  # 'multiple_choice' | 'order_words'
    question: str
    explanation: str
    # Campos para multiple_choice
    options: Optional[List[str]] = None
    correct_index: Optional[int] = None
    # Campos para order_words (unscrambling)
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
