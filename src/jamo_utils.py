"""Utilitários de decomposição e classificação de Jamo Hangul para caligrafia.

Decompõe sílabas Hangul (가-힣) em seus componentes Jamo
(Choseong / Jungseong / Jongseong) usando aritmética Unicode,
classifica o tipo geométrico do bloco silábico e mapeia
cada jamo para seus dados de stroke order.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# ============================================================
# Constantes Unicode do Hangul
# ============================================================
# Bloco de sílabas pré-compostas: U+AC00 (가) a U+D7A3 (힣)
HANGUL_SYLLABLE_BASE = 0xAC00
HANGUL_SYLLABLE_END = 0xD7A3

# Quantidades de cada tipo de jamo
CHOSEONG_COUNT = 19
JUNGSEONG_COUNT = 21
JONGSEONG_COUNT = 28  # inclui "sem jongseong" (índice 0)

# Bloco por sílaba = JUNGSEONG_COUNT * JONGSEONG_COUNT = 588
JUNGSEONG_JONGSEONG_BLOCK = JUNGSEONG_COUNT * JONGSEONG_COUNT

# ============================================================
# Tabelas de Jamo
# ============================================================
CHOSEONG_TABLE = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
    "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
]

JUNGSEONG_TABLE = [
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ",
    "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ",
    "ㅣ",
]

JONGSEONG_TABLE = [
    "",   # índice 0 = sem batchim
    "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ",
    "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ",
    "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
]

# Mapeamento de jamo para nomes de arquivo (romanização padrão)
JAMO_TO_FILENAME = {
    # Choseong / Jongseong (consoantes)
    "ㄱ": "giyeok", "ㄲ": "ssang_giyeok", "ㄴ": "nieun",
    "ㄷ": "digeut", "ㄸ": "ssang_digeut", "ㄹ": "rieul",
    "ㅁ": "mieum", "ㅂ": "bieup", "ㅃ": "ssang_bieup",
    "ㅅ": "siot", "ㅆ": "ssang_siot", "ㅇ": "ieung",
    "ㅈ": "jieut", "ㅉ": "ssang_jieut", "ㅊ": "chieut",
    "ㅋ": "kieuk", "ㅌ": "tieut", "ㅍ": "pieup", "ㅎ": "hieut",
    # Jongseong compostos
    "ㄳ": "giyeok_siot", "ㄵ": "nieun_jieut", "ㄶ": "nieun_hieut",
    "ㄺ": "rieul_giyeok", "ㄻ": "rieul_mieum", "ㄼ": "rieul_bieup",
    "ㄽ": "rieul_siot", "ㄾ": "rieul_tieut", "ㄿ": "rieul_pieup",
    "ㅀ": "rieul_hieut", "ㅄ": "bieup_siot",
    # Jungseong (vogais)
    "ㅏ": "a", "ㅐ": "ae", "ㅑ": "ya", "ㅒ": "yae",
    "ㅓ": "eo", "ㅔ": "e", "ㅕ": "yeo", "ㅖ": "ye",
    "ㅗ": "o", "ㅘ": "wa", "ㅙ": "wae", "ㅚ": "oe",
    "ㅛ": "yo", "ㅜ": "u", "ㅝ": "wo", "ㅞ": "we",
    "ㅟ": "wi", "ㅠ": "yu", "ㅡ": "eu", "ㅢ": "ui",
    "ㅣ": "i",
}

# Vogais "verticais" (traço principal vertical — ㅏ,ㅐ,ㅑ,ㅒ,ㅓ,ㅔ,ㅕ,ㅖ,ㅣ)
# ficam à direita do choseong
VERTICAL_VOWELS = {"ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅣ"}

# Vogais "horizontais" (traço principal horizontal — ㅗ,ㅛ,ㅜ,ㅠ,ㅡ)
# ficam abaixo do choseong
HORIZONTAL_VOWELS = {"ㅗ", "ㅛ", "ㅜ", "ㅠ", "ㅡ"}

# Vogais compostas (combinam vertical + horizontal — ㅘ,ㅙ,ㅚ,ㅝ,ㅞ,ㅟ,ㅢ)
# envolvem o choseong em L invertido
COMPOUND_VOWELS = {"ㅘ", "ㅙ", "ㅚ", "ㅝ", "ㅞ", "ㅟ", "ㅢ"}


class BlockType(str, Enum):
    """Tipo geométrico do bloco silábico Hangul.

    Determina como os jamo são posicionados dentro da célula da grade.
    """
    # Sem batchim (jongseong)
    CV_VERTICAL = "cv_vertical"      # C + V vertical  (가, 나, 디)
    CV_HORIZONTAL = "cv_horizontal"  # C + V horizontal (고, 누, 두)
    CV_COMPOUND = "cv_compound"      # C + V composta   (과, 뉘, 의)

    # Com batchim (jongseong)
    CVC_VERTICAL = "cvc_vertical"    # C + V vertical + C  (간, 달, 밤)
    CVC_HORIZONTAL = "cvc_horizontal"  # C + V horizontal + C (곤, 눈, 둥)
    CVC_COMPOUND = "cvc_compound"    # C + V composta + C   (광, 뒹, 읽)


@dataclass(frozen=True)
class JamoDecomposition:
    """Resultado da decomposição de uma sílaba Hangul."""
    syllable: str
    choseong: str
    jungseong: str
    jongseong: str  # string vazia se sem batchim
    choseong_index: int
    jungseong_index: int
    jongseong_index: int
    block_type: BlockType

    @property
    def has_batchim(self) -> bool:
        return self.jongseong_index > 0

    @property
    def jamo_list(self) -> list[str]:
        """Retorna a lista ordenada de jamo (sem o jongseong vazio)."""
        result = [self.choseong, self.jungseong]
        if self.has_batchim:
            result.append(self.jongseong)
        return result

    @property
    def stroke_filenames(self) -> list[str]:
        """Retorna os nomes de arquivo SVG para cada jamo na ordem de escrita."""
        filenames = [
            JAMO_TO_FILENAME.get(self.choseong, "unknown"),
            JAMO_TO_FILENAME.get(self.jungseong, "unknown"),
        ]
        if self.has_batchim:
            filenames.append(JAMO_TO_FILENAME.get(self.jongseong, "unknown"))
        return filenames


def is_hangul_syllable(char: str) -> bool:
    """Verifica se um caractere é uma sílaba Hangul pré-composta (가-힣)."""
    if len(char) != 1:
        return False
    code = ord(char)
    return HANGUL_SYLLABLE_BASE <= code <= HANGUL_SYLLABLE_END


def is_hangul_jamo(char: str) -> bool:
    """Verifica se um caractere é um jamo Hangul individual."""
    return char in JAMO_TO_FILENAME


def classify_block_type(jungseong: str, has_batchim: bool) -> BlockType:
    """Classifica o tipo geométrico do bloco a partir da vogal e presença de batchim."""
    if jungseong in VERTICAL_VOWELS:
        return BlockType.CVC_VERTICAL if has_batchim else BlockType.CV_VERTICAL
    elif jungseong in HORIZONTAL_VOWELS:
        return BlockType.CVC_HORIZONTAL if has_batchim else BlockType.CV_HORIZONTAL
    else:  # COMPOUND_VOWELS
        return BlockType.CVC_COMPOUND if has_batchim else BlockType.CV_COMPOUND


def decompose(syllable: str) -> JamoDecomposition:
    """Decompõe uma sílaba Hangul pré-composta em seus jamo constituintes.

    Usa aritmética Unicode padrão (KS X 1001):
      code = 0xAC00 + (choseong * 21 + jungseong) * 28 + jongseong

    Args:
        syllable: Um único caractere Hangul (가-힣).

    Returns:
        JamoDecomposition com todos os componentes e metadados.

    Raises:
        ValueError: Se o caractere não for uma sílaba Hangul válida.
    """
    if not is_hangul_syllable(syllable):
        codepoint_info = f" (U+{ord(syllable):04X})" if len(syllable) == 1 else ""
        raise ValueError(
            f"'{syllable}'{codepoint_info} não é uma sílaba Hangul "
            f"pré-composta (intervalo U+AC00 a U+D7A3)."
        )

    code = ord(syllable) - HANGUL_SYLLABLE_BASE

    choseong_idx = code // JUNGSEONG_JONGSEONG_BLOCK
    remainder = code % JUNGSEONG_JONGSEONG_BLOCK
    jungseong_idx = remainder // JONGSEONG_COUNT
    jongseong_idx = remainder % JONGSEONG_COUNT

    choseong = CHOSEONG_TABLE[choseong_idx]
    jungseong = JUNGSEONG_TABLE[jungseong_idx]
    jongseong = JONGSEONG_TABLE[jongseong_idx]

    has_batchim = jongseong_idx > 0
    block_type = classify_block_type(jungseong, has_batchim)

    return JamoDecomposition(
        syllable=syllable,
        choseong=choseong,
        jungseong=jungseong,
        jongseong=jongseong,
        choseong_index=choseong_idx,
        jungseong_index=jungseong_idx,
        jongseong_index=jongseong_idx,
        block_type=block_type,
    )


def compose(choseong: str, jungseong: str, jongseong: str = "") -> str:
    """Compõe jamo individuais em uma sílaba Hangul pré-composta.

    Args:
        choseong: Consoante inicial (ㄱ-ㅎ).
        jungseong: Vogal medial (ㅏ-ㅣ).
        jongseong: Consoante final/batchim (opcional, string vazia = sem batchim).

    Returns:
        Caractere Hangul composto (ex: "한").

    Raises:
        ValueError: Se algum jamo for inválido.
    """
    if choseong not in CHOSEONG_TABLE:
        raise ValueError(f"Choseong inválido: '{choseong}'")
    if jungseong not in JUNGSEONG_TABLE:
        raise ValueError(f"Jungseong inválido: '{jungseong}'")
    if jongseong and jongseong not in JONGSEONG_TABLE:
        raise ValueError(f"Jongseong inválido: '{jongseong}'")

    cho_idx = CHOSEONG_TABLE.index(choseong)
    jung_idx = JUNGSEONG_TABLE.index(jungseong)
    jong_idx = JONGSEONG_TABLE.index(jongseong) if jongseong else 0

    code = HANGUL_SYLLABLE_BASE + (cho_idx * JUNGSEONG_COUNT + jung_idx) * JONGSEONG_COUNT + jong_idx
    return chr(code)


def decompose_string(text: str) -> list[JamoDecomposition | str]:
    """Decompõe uma string mista, retornando JamoDecomposition para sílabas Hangul
    e strings originais para os demais caracteres.

    Args:
        text: Texto com possíveis sílabas Hangul misturadas com outros caracteres.

    Returns:
        Lista onde cada elemento é JamoDecomposition (para sílabas) ou str (para outros).
    """
    result: list[JamoDecomposition | str] = []
    for char in text:
        if is_hangul_syllable(char):
            result.append(decompose(char))
        else:
            result.append(char)
    return result


# ============================================================
# Layout de Posicionamento dos Jamo dentro da Célula
# ============================================================
# Coordenadas normalizadas (0.0 a 1.0) para cada jamo dentro
# de uma célula da grade, por tipo de bloco.
# Formato: {"x": float, "y": float, "w": float, "h": float}

BLOCK_LAYOUTS: dict[str, dict[str, dict[str, float]]] = {
    # ── Sem Batchim ──────────────────────────────────
    BlockType.CV_VERTICAL: {
        "choseong":  {"x": 0.05, "y": 0.10, "w": 0.50, "h": 0.80},
        "jungseong": {"x": 0.55, "y": 0.10, "w": 0.40, "h": 0.80},
    },
    BlockType.CV_HORIZONTAL: {
        "choseong":  {"x": 0.10, "y": 0.05, "w": 0.80, "h": 0.50},
        "jungseong": {"x": 0.10, "y": 0.55, "w": 0.80, "h": 0.40},
    },
    BlockType.CV_COMPOUND: {
        "choseong":  {"x": 0.05, "y": 0.05, "w": 0.50, "h": 0.50},
        "jungseong": {"x": 0.05, "y": 0.05, "w": 0.90, "h": 0.90},
    },
    # ── Com Batchim ──────────────────────────────────
    BlockType.CVC_VERTICAL: {
        "choseong":  {"x": 0.05, "y": 0.05, "w": 0.50, "h": 0.55},
        "jungseong": {"x": 0.55, "y": 0.05, "w": 0.40, "h": 0.55},
        "jongseong": {"x": 0.10, "y": 0.62, "w": 0.80, "h": 0.33},
    },
    BlockType.CVC_HORIZONTAL: {
        "choseong":  {"x": 0.10, "y": 0.05, "w": 0.80, "h": 0.33},
        "jungseong": {"x": 0.10, "y": 0.38, "w": 0.80, "h": 0.27},
        "jongseong": {"x": 0.10, "y": 0.65, "w": 0.80, "h": 0.30},
    },
    BlockType.CVC_COMPOUND: {
        "choseong":  {"x": 0.05, "y": 0.05, "w": 0.50, "h": 0.38},
        "jungseong": {"x": 0.05, "y": 0.05, "w": 0.90, "h": 0.60},
        "jongseong": {"x": 0.10, "y": 0.65, "w": 0.80, "h": 0.30},
    },
}


def get_jamo_layout(block_type: BlockType) -> dict[str, dict[str, float]]:
    """Retorna as coordenadas normalizadas de posicionamento para cada jamo
    de acordo com o tipo geométrico do bloco."""
    return BLOCK_LAYOUTS[block_type]
