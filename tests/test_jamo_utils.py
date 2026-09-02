"""Testes unitários para o módulo jamo_utils e dados de stroke order."""

import json
import os
import pytest
from src.jamo_utils import (
    BlockType,
    JAMO_TO_FILENAME,
    classify_block_type,
    compose,
    decompose,
    decompose_string,
    get_jamo_layout,
    get_stroke_data,
    is_hangul_jamo,
    is_hangul_syllable,
    jamo_to_key,
    layout_syllable_strokes,
    load_stroke_catalog,
)


class TestJamoUtils:
    """Testes para decomposição e composição de Hangul."""

    def test_is_hangul_syllable(self):
        assert is_hangul_syllable("가") is True
        assert is_hangul_syllable("힣") is True
        assert is_hangul_syllable("한") is True
        assert is_hangul_syllable("글") is True
        assert is_hangul_syllable("ㄱ") is False
        assert is_hangul_syllable("ㅏ") is False
        assert is_hangul_syllable("A") is False
        assert is_hangul_syllable("1") is False
        assert is_hangul_syllable(" ") is False
        assert is_hangul_syllable("") is False
        assert is_hangul_syllable("한글") is False

    def test_is_hangul_jamo(self):
        assert is_hangul_jamo("ㄱ") is True
        assert is_hangul_jamo("ㅎ") is True
        assert is_hangul_jamo("ㅏ") is True
        assert is_hangul_jamo("ㅣ") is True
        assert is_hangul_jamo("가") is False
        assert is_hangul_jamo("A") is False

    def test_decompose_cv_vertical(self):
        d = decompose("가")
        assert d.syllable == "가"
        assert d.choseong == "ㄱ"
        assert d.jungseong == "ㅏ"
        assert d.jongseong == ""
        assert d.has_batchim is False
        assert d.block_type == BlockType.CV_VERTICAL
        assert d.jamo_list == ["ㄱ", "ㅏ"]
        assert d.stroke_filenames == ["giyeok", "a"]

    def test_decompose_cv_horizontal(self):
        d = decompose("고")
        assert d.syllable == "고"
        assert d.choseong == "ㄱ"
        assert d.jungseong == "ㅗ"
        assert d.jongseong == ""
        assert d.has_batchim is False
        assert d.block_type == BlockType.CV_HORIZONTAL
        assert d.jamo_list == ["ㄱ", "ㅗ"]
        assert d.stroke_filenames == ["giyeok", "o"]

    def test_decompose_cv_compound(self):
        d = decompose("과")
        assert d.syllable == "과"
        assert d.choseong == "ㄱ"
        assert d.jungseong == "ㅘ"
        assert d.jongseong == ""
        assert d.has_batchim is False
        assert d.block_type == BlockType.CV_COMPOUND

    def test_decompose_cvc_vertical(self):
        d = decompose("한")
        assert d.syllable == "한"
        assert d.choseong == "ㅎ"
        assert d.jungseong == "ㅏ"
        assert d.jongseong == "ㄴ"
        assert d.has_batchim is True
        assert d.block_type == BlockType.CVC_VERTICAL
        assert d.jamo_list == ["ㅎ", "ㅏ", "ㄴ"]
        assert d.stroke_filenames == ["hieut", "a", "nieun"]

    def test_decompose_cvc_horizontal(self):
        d = decompose("글")
        assert d.syllable == "글"
        assert d.choseong == "ㄱ"
        assert d.jungseong == "ㅡ"
        assert d.jongseong == "ㄹ"
        assert d.has_batchim is True
        assert d.block_type == BlockType.CVC_HORIZONTAL
        assert d.jamo_list == ["ㄱ", "ㅡ", "ㄹ"]
        assert d.stroke_filenames == ["giyeok", "eu", "rieul"]

    def test_decompose_cvc_compound(self):
        d = decompose("광")
        assert d.syllable == "광"
        assert d.choseong == "ㄱ"
        assert d.jungseong == "ㅘ"
        assert d.jongseong == "ㅇ"
        assert d.has_batchim is True
        assert d.block_type == BlockType.CVC_COMPOUND

    def test_decompose_invalid_raises(self):
        with pytest.raises(ValueError):
            decompose("A")
        with pytest.raises(ValueError):
            decompose("ㄱ")
        with pytest.raises(ValueError):
            decompose("")

    def test_compose_basic(self):
        assert compose("ㄱ", "ㅏ") == "가"
        assert compose("ㅎ", "ㅏ", "ㄴ") == "한"
        assert compose("ㄱ", "ㅡ", "ㄹ") == "글"
        assert compose("ㅅ", "ㅔ", "") == "세"
        assert compose("ㅈ", "ㅗ", "ㅇ") == "종"

    def test_roundtrip_all_sample_syllables(self):
        samples = ["세", "종", "대", "왕", "한", "국", "어", "학", "당", "컴", "패", "니", "언"]
        for s in samples:
            d = decompose(s)
            c = compose(d.choseong, d.jungseong, d.jongseong)
            assert c == s

    def test_decompose_string_mixed(self):
        result = decompose_string("한글 101!")
        assert len(result) == 7
        assert result[0].syllable == "한"
        assert result[1].syllable == "글"
        assert result[2] == " "
        assert result[3] == "1"
        assert result[4] == "0"
        assert result[5] == "1"
        assert result[6] == "!"

    def test_get_jamo_layout(self):
        for bt in BlockType:
            layout = get_jamo_layout(bt)
            assert "choseong" in layout
            assert "jungseong" in layout
            if "cvc" in bt.value:
                assert "jongseong" in layout
            for part, coords in layout.items():
                assert 0.0 <= coords["x"] <= 1.0
                assert 0.0 <= coords["y"] <= 1.0
                assert 0.0 < coords["w"] <= 1.0
                assert 0.0 < coords["h"] <= 1.0

    def test_classify_block_type_rejects_unknown_vowel(self):
        with pytest.raises(ValueError):
            classify_block_type("A", False)

    def test_jamo_to_key(self):
        assert jamo_to_key("ㄱ") == "giyeok"
        assert jamo_to_key("ㅘ") == "wa"
        assert jamo_to_key("ㄳ") == "giyeok_siot"
        with pytest.raises(ValueError):
            jamo_to_key("가")

    def test_stroke_data_on_decomposition(self):
        strokes = decompose("한").stroke_data()
        assert [item.jamo for item in strokes] == ["ㅎ", "ㅏ", "ㄴ"]
        assert all(item.stroke_count == len(item.strokes) for item in strokes)

    def test_layout_syllable_strokes_in_unit_square(self):
        placed = layout_syllable_strokes("한")
        assert len(placed) > 0
        for stroke in placed:
            for x, y in stroke:
                assert 0.0 <= x <= 1.0
                assert 0.0 <= y <= 1.0


class TestStrokeOrderData:
    """Testes para o dataset de stroke order (jamo_strokes.json)."""

    @pytest.fixture
    def stroke_data(self):
        data_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "stroke_order", "jamo_strokes.json"
        )
        assert os.path.exists(data_path), f"Arquivo não encontrado: {data_path}"
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_consonants_present(self, stroke_data):
        consonants = stroke_data.get("consonants", {})
        expected = [
            "giyeok", "ssang_giyeok", "nieun", "digeut", "ssang_digeut", "rieul",
            "mieum", "bieup", "ssang_bieup", "siot", "ssang_siot", "ieung",
            "jieut", "ssang_jieut", "chieut", "kieuk", "tieut", "pieup", "hieut",
        ]
        for name in expected:
            assert name in consonants, f"Consoante {name} ausente em jamo_strokes.json"

    def test_vowels_present(self, stroke_data):
        vowels = stroke_data.get("vowels", {})
        expected = [
            "a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o",
            "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i",
        ]
        for name in expected:
            assert name in vowels, f"Vogal {name} ausente em jamo_strokes.json"

    def test_compound_batchim_present(self, stroke_data):
        compounds = stroke_data.get("compounds", {})
        expected = [
            "giyeok_siot", "nieun_jieut", "nieun_hieut", "rieul_giyeok",
            "rieul_mieum", "rieul_bieup", "rieul_siot", "rieul_tieut",
            "rieul_pieup", "rieul_hieut", "bieup_siot",
        ]
        for name in expected:
            assert name in compounds, f"Batchim composto {name} ausente em jamo_strokes.json"

    def test_catalog_covers_all_jamo_keys(self, stroke_data):
        listed = set()
        for category in ("consonants", "vowels", "compounds"):
            listed.update(stroke_data.get(category, {}))
        assert listed == set(JAMO_TO_FILENAME.values())

    def test_stroke_count_matches_path_length(self, stroke_data):
        for category in ("consonants", "vowels", "compounds"):
            for name, item in stroke_data.get(category, {}).items():
                strokes = item.get("strokes", [])
                assert item["stroke_count"] == len(strokes), f"{name}: stroke_count divergente"
                assert item["romanization"] == name

    def test_stroke_coordinates_valid(self, stroke_data):
        for category in ("consonants", "vowels", "compounds"):
            for name, item in stroke_data.get(category, {}).items():
                strokes = item.get("strokes", [])
                assert len(strokes) > 0, f"{name} não possui strokes definidos"
                for stroke in strokes:
                    assert len(stroke) >= 2, f"Stroke em {name} possui menos de 2 pontos"
                    for point in stroke:
                        assert len(point) == 2, f"Ponto inválido em {name}: {point}"
                        x, y = point
                        assert 0.0 <= x <= 1.0, f"X fora do intervalo em {name}: {x}"
                        assert 0.0 <= y <= 1.0, f"Y fora do intervalo em {name}: {y}"

    def test_load_stroke_catalog_indexes_jamo_and_key(self):
        catalog = load_stroke_catalog()
        giyeok = get_stroke_data("ㄱ")
        assert giyeok is catalog["giyeok"]
        assert giyeok.jamo == "ㄱ"
        assert giyeok.stroke_count == 2
        assert get_stroke_data("wa").jamo == "ㅘ"
        with pytest.raises(KeyError):
            get_stroke_data("unknown_jamo")
