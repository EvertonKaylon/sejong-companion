"""Utilitários de decomposição, layout e stroke order de Jamo Hangul.

Decompõe sílabas Hangul (가-힣) em Choseong / Jungseong / Jongseong
via aritmética Unicode (KS X 1001), classifica o tipo geométrico do
bloco silábico, posiciona cada jamo na célula 원고지 e carrega os
vetores de 획순 em `assets/stroke_order/jamo_strokes.json`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from pathlib import Path

# ============================================================
# Constantes Unicode do Hangul
# ============================================================
# Bloco de sílabas pré-compostas: U+AC00 (가) a U+D7A3 (힣)
HANGUL_SYLLABLE_BASE = 0xAC00
HANGUL_SYLLABLE_END = 0xD7A3

CHOSEONG_COUNT = 19
JUNGSEONG_COUNT = 21
JONGSEONG_COUNT = 28  # inclui "sem jongseong" (índice 0)
JUNGSEONG_JONGSEONG_BLOCK = JUNGSEONG_COUNT * JONGSEONG_COUNT

STROKE_CATALOG_CATEGORIES = ("consonants", "vowels", "compounds")

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

JAMO_TO_FILENAME = {
    "ㄱ": "giyeok", "ㄲ": "ssang_giyeok", "ㄴ": "nieun",
    "ㄷ": "digeut", "ㄸ": "ssang_digeut", "ㄹ": "rieul",
    "ㅁ": "mieum", "ㅂ": "bieup", "ㅃ": "ssang_bieup",
    "ㅅ": "siot", "ㅆ": "ssang_siot", "ㅇ": "ieung",
    "ㅈ": "jieut", "ㅉ": "ssang_jieut", "ㅊ": "chieut",
    "ㅋ": "kieuk", "ㅌ": "tieut", "ㅍ": "pieup", "ㅎ": "hieut",
    "ㄳ": "giyeok_siot", "ㄵ": "nieun_jieut", "ㄶ": "nieun_hieut",
    "ㄺ": "rieul_giyeok", "ㄻ": "rieul_mieum", "ㄼ": "rieul_bieup",
    "ㄽ": "rieul_siot", "ㄾ": "rieul_tieut", "ㄿ": "rieul_pieup",
    "ㅀ": "rieul_hieut", "ㅄ": "bieup_siot",
    "ㅏ": "a", "ㅐ": "ae", "ㅑ": "ya", "ㅒ": "yae",
    "ㅓ": "eo", "ㅔ": "e", "ㅕ": "yeo", "ㅖ": "ye",
    "ㅗ": "o", "ㅘ": "wa", "ㅙ": "wae", "ㅚ": "oe",
    "ㅛ": "yo", "ㅜ": "u", "ㅝ": "wo", "ㅞ": "we",
    "ㅟ": "wi", "ㅠ": "yu", "ㅡ": "eu", "ㅢ": "ui",
    "ㅣ": "i",
}

CHOSEONG_INDEX = {jamo: i for i, jamo in enumerate(CHOSEONG_TABLE)}
JUNGSEONG_INDEX = {jamo: i for i, jamo in enumerate(JUNGSEONG_TABLE)}
JONGSEONG_INDEX = {jamo: i for i, jamo in enumerate(JONGSEONG_TABLE)}

VERTICAL_VOWELS = frozenset({"ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅣ"})
HORIZONTAL_VOWELS = frozenset({"ㅗ", "ㅛ", "ㅜ", "ㅠ", "ㅡ"})
COMPOUND_VOWELS = frozenset({"ㅘ", "ㅙ", "ㅚ", "ㅝ", "ㅞ", "ㅟ", "ㅢ"})


class BlockType(str, Enum):
    """Tipo geométrico do bloco silábico Hangul.

    Determina como os jamo são posicionados dentro da célula da grade.
    """
    CV_VERTICAL = "cv_vertical"
    CV_HORIZONTAL = "cv_horizontal"
    CV_COMPOUND = "cv_compound"
    CVC_VERTICAL = "cvc_vertical"
    CVC_HORIZONTAL = "cvc_horizontal"
    CVC_COMPOUND = "cvc_compound"


@dataclass(frozen=True)
class JamoStrokeData:
    """Vetores de 획순 de um jamo, no espaço normalizado [0, 1]."""
    jamo: str
    name: str
    romanization: str
    stroke_count: int
    strokes: tuple[tuple[tuple[float, float], ...], ...]

    @property
    def key(self) -> str:
        return self.romanization


@dataclass(frozen=True)
class JamoDecomposition:
    """Resultado da decomposição de uma sílaba Hangul."""
    syllable: str
    choseong: str
    jungseong: str
    jongseong: str
    choseong_index: int
    jungseong_index: int
    jongseong_index: int
    block_type: BlockType

    @property
    def has_batchim(self) -> bool:
        return self.jongseong_index > 0

    @property
    def jamo_list(self) -> list[str]:
        result = [self.choseong, self.jungseong]
        if self.has_batchim:
            result.append(self.jongseong)
        return result

    @property
    def stroke_filenames(self) -> list[str]:
        """Chaves do catálogo de stroke order na ordem de escrita."""
        return [jamo_to_key(jamo) for jamo in self.jamo_list]

    def stroke_data(self) -> list[JamoStrokeData]:
        return [get_stroke_data(jamo) for jamo in self.jamo_list]


def is_hangul_syllable(char: str) -> bool:
    """Verifica se um caractere é uma sílaba Hangul pré-composta (가-힣)."""
    if len(char) != 1:
        return False
    code = ord(char)
    return HANGUL_SYLLABLE_BASE <= code <= HANGUL_SYLLABLE_END


def is_hangul_jamo(char: str) -> bool:
    """Verifica se um caractere é um jamo Hangul individual catalogado."""
    return char in JAMO_TO_FILENAME


def jamo_to_key(jamo: str) -> str:
    """Converte um jamo no identificador do catálogo (ex: ㄱ → giyeok)."""
    try:
        return JAMO_TO_FILENAME[jamo]
    except KeyError as exc:
        raise ValueError(f"Jamo sem chave de stroke order: {jamo!r}") from exc


def classify_block_type(jungseong: str, has_batchim: bool) -> BlockType:
    """Classifica o tipo geométrico do bloco a partir da vogal e do batchim."""
    if jungseong in VERTICAL_VOWELS:
        return BlockType.CVC_VERTICAL if has_batchim else BlockType.CV_VERTICAL
    if jungseong in HORIZONTAL_VOWELS:
        return BlockType.CVC_HORIZONTAL if has_batchim else BlockType.CV_HORIZONTAL
    if jungseong in COMPOUND_VOWELS:
        return BlockType.CVC_COMPOUND if has_batchim else BlockType.CV_COMPOUND
    raise ValueError(f"Jungseong inválido para classificação de bloco: {jungseong!r}")


def decompose(syllable: str) -> JamoDecomposition:
    """Decompõe uma sílaba Hangul pré-composta em seus jamo constituintes.

    Usa aritmética Unicode padrão (KS X 1001):
      code = 0xAC00 + (choseong * 21 + jungseong) * 28 + jongseong
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

    return JamoDecomposition(
        syllable=syllable,
        choseong=choseong,
        jungseong=jungseong,
        jongseong=jongseong,
        choseong_index=choseong_idx,
        jungseong_index=jungseong_idx,
        jongseong_index=jongseong_idx,
        block_type=classify_block_type(jungseong, jongseong_idx > 0),
    )


def compose(choseong: str, jungseong: str, jongseong: str = "") -> str:
    """Compõe jamo individuais em uma sílaba Hangul pré-composta."""
    if choseong not in CHOSEONG_INDEX:
        raise ValueError(f"Choseong inválido: '{choseong}'")
    if jungseong not in JUNGSEONG_INDEX:
        raise ValueError(f"Jungseong inválido: '{jungseong}'")
    if jongseong not in JONGSEONG_INDEX:
        raise ValueError(f"Jongseong inválido: '{jongseong}'")

    cho_idx = CHOSEONG_INDEX[choseong]
    jung_idx = JUNGSEONG_INDEX[jungseong]
    jong_idx = JONGSEONG_INDEX[jongseong]
    code = (
        HANGUL_SYLLABLE_BASE
        + (cho_idx * JUNGSEONG_COUNT + jung_idx) * JONGSEONG_COUNT
        + jong_idx
    )
    return chr(code)


def decompose_string(text: str) -> list[JamoDecomposition | str]:
    """Decompõe uma string mista em JamoDecomposition (sílabas) ou str."""
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
BLOCK_LAYOUTS: dict[BlockType, dict[str, dict[str, float]]] = {
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
    """Retorna as caixas normalizadas de cada jamo no tipo de bloco."""
    return BLOCK_LAYOUTS[block_type]


def map_strokes_to_box(
    strokes: tuple[tuple[tuple[float, float], ...], ...] | list[list[list[float]]],
    box: dict[str, float],
) -> list[list[tuple[float, float]]]:
    """Projeta traços do quadrado unitário para a caixa {x, y, w, h} da célula."""
    x0, y0, w, h = box["x"], box["y"], box["w"], box["h"]
    mapped: list[list[tuple[float, float]]] = []
    for stroke in strokes:
        mapped.append([(x0 + px * w, y0 + py * h) for px, py in stroke])
    return mapped


def layout_syllable_strokes(syllable: str) -> list[list[tuple[float, float]]]:
    """Traços de todos os jamo da sílaba já posicionados na célula 원고지."""
    decomp = decompose(syllable)
    layout = get_jamo_layout(decomp.block_type)
    roles = ("choseong", "jungseong", "jongseong") if decomp.has_batchim else ("choseong", "jungseong")
    placed: list[list[tuple[float, float]]] = []
    for jamo, role in zip(decomp.jamo_list, roles, strict=True):
        placed.extend(map_strokes_to_box(get_stroke_data(jamo).strokes, layout[role]))
    return placed


# ============================================================
# Catálogo de Stroke Order
# ============================================================
def _stroke_catalog_path() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "stroke_order" / "jamo_strokes.json"


def _parse_stroke_entry(raw: dict) -> JamoStrokeData:
    strokes = tuple(
        tuple((float(x), float(y)) for x, y in stroke)
        for stroke in raw["strokes"]
    )
    return JamoStrokeData(
        jamo=raw["jamo"],
        name=raw["name"],
        romanization=raw["romanization"],
        stroke_count=int(raw["stroke_count"]),
        strokes=strokes,
    )


@lru_cache(maxsize=1)
def load_stroke_catalog() -> dict[str, JamoStrokeData]:
    """Carrega o JSON de 획순 indexado por jamo e por chave romanizada."""
    path = _stroke_catalog_path()
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    catalog: dict[str, JamoStrokeData] = {}
    for category in STROKE_CATALOG_CATEGORIES:
        for key, raw in payload.get(category, {}).items():
            entry = _parse_stroke_entry(raw)
            if entry.stroke_count != len(entry.strokes):
                raise ValueError(
                    f"stroke_count inconsistente em '{key}': "
                    f"{entry.stroke_count} != {len(entry.strokes)}"
                )
            catalog[key] = entry
            catalog[entry.jamo] = entry
    return catalog


def get_stroke_data(jamo_or_key: str) -> JamoStrokeData:
    """Retorna os traços de um jamo (caractere) ou de sua chave (giyeok, a, …)."""
    catalog = load_stroke_catalog()
    try:
        return catalog[jamo_or_key]
    except KeyError as exc:
        raise KeyError(f"Jamo ausente em jamo_strokes.json: {jamo_or_key!r}") from exc
