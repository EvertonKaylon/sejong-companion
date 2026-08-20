import pytest
import os
import json
import re
from src.services import DataService
from src.models import UnitData, UnitIntroData

def test_curriculum_json_count():
    """Valida se todas as 23 unidades estão devidamente registradas no curriculum.json."""
    curriculum = DataService.get_curriculum()
    assert len(curriculum) == 23
    
    # 1 Intro + 10 do 1A + 12 do 1B
    intro_units = [u for u in curriculum if u.id == "unit_intro"]
    book_1a_units = [u for u in curriculum if getattr(u, "book", "1A") == "1A" and u.id != "unit_intro"]
    book_1b_units = [u for u in curriculum if getattr(u, "book", "") == "1B" or u.id.startswith("unit_1b_")]
    
    assert len(intro_units) == 1
    assert len(book_1a_units) == 10
    assert len(book_1b_units) == 12

def test_all_23_units_pydantic_schema():
    """Valida a conformidade de schema Pydantic de todos os 23 arquivos de unidades."""
    curriculum = DataService.get_curriculum()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    units_dir = os.path.join(base_dir, "data", "units")

    for unit in curriculum:
        file_path = os.path.join(units_dir, f"{unit.id}.json")
        assert os.path.exists(file_path), f"Arquivo não encontrado: {file_path}"

        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        if unit.id == "unit_intro":
            parsed = UnitIntroData(**raw_data)
            assert parsed.unit_id == "unit_intro"
            assert len(parsed.vowels) > 0
            assert len(parsed.consonants) > 0
        else:
            parsed = UnitData(**raw_data)
            assert parsed.unit_id == unit.id
            assert len(parsed.vocabulary) >= 5, f"{unit.id} deve ter pelo menos 5 itens de vocabulário"
            assert len(parsed.grammar) >= 1, f"{unit.id} deve ter pelo menos 1 seção de gramática"
            assert len(parsed.exercises) >= 3, f"{unit.id} deve ter pelo menos 3 exercícios"

def test_zero_romanization_policy():
    """Garante que nenhum campo de texto coreano contenha romanização acidental."""
    curriculum = DataService.get_curriculum()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    units_dir = os.path.join(base_dir, "data", "units")

    # Regex para identificar letras latinas em campos estritamente 한글
    latin_regex = re.compile(r"[a-zA-Z]")

    for unit in curriculum:
        if unit.id == "unit_intro":
            continue

        file_path = os.path.join(units_dir, f"{unit.id}.json")
        with open(file_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # 1. Vocabulário: campo 'word' não pode ter caracteres latinos
        for idx, item in enumerate(raw.get("vocabulary", [])):
            word_text = item.get("word", "")
            assert not latin_regex.search(word_text), (
                f"[{unit.id}] Vocabulário '{word_text}' (idx {idx}) contém caracteres latinos / romanização!"
            )

        # 2. Exercícios SOV: palavras e correct_order não podem ter caracteres latinos
        for q in raw.get("exercises", []):
            if q.get("type") == "drag_and_drop_sov":
                for item in q.get("sov_items", []):
                    assert not latin_regex.search(item.get("word", "")), (
                        f"[{unit.id}] Palavra SOV '{item.get('word')}' contém letras latinas!"
                    )

def test_global_id_uniqueness():
    """Valida a unicidade de IDs de flashcards e questões em todo o escopo global."""
    all_cards = DataService.get_all_flashcards()
    card_ids = [c.id for c in all_cards]
    assert len(card_ids) == len(set(card_ids)), f"Existem IDs de flashcards duplicados: {len(card_ids)} vs {len(set(card_ids))}"

    all_challenges = DataService.get_sentence_builder_challenges()
    challenge_ids = [ch["id"] for ch in all_challenges]
    assert len(challenge_ids) == len(set(challenge_ids)), "Existem IDs de sentenças duplicados!"

def test_sov_exercises_integrity():
    """Valida estritamente a consistência semântica e sintática de 100% dos exercícios SOV."""
    curriculum = DataService.get_curriculum()
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    units_dir = os.path.join(base_dir, "data", "units")

    valid_roles = {
        "SUBJECT", "OBJECT", "VERB", "PREDICATE", "LOCATION",
        "ADVERB", "TIME", "COMPLEMENT", "MODIFIER", "QUANTITY",
        "COUNTER", "CONNECTIVE", "PARTICLE", "ANY"
    }

    for unit in curriculum:
        if unit.id == "unit_intro":
            continue

        file_path = os.path.join(units_dir, f"{unit.id}.json")
        with open(file_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        for q in raw.get("exercises", []):
            if q.get("type") == "drag_and_drop_sov":
                items = q.get("sov_items", [])
                slots = q.get("sov_slots", [])
                correct_order = q.get("correct_order", [])

                assert len(items) == len(slots), f"[{unit.id}:{q.get('id')}] sov_items e sov_slots devem ter o mesmo tamanho"
                assert len(items) == len(correct_order), f"[{unit.id}:{q.get('id')}] sov_items e correct_order devem ter o mesmo tamanho"

                # Verificar se todos os itens estão presentes no correct_order
                item_words = {it["word"] for it in items}
                assert item_words == set(correct_order), f"[{unit.id}:{q.get('id')}] Palavras dos itens não batem com correct_order"

                # Verificar papéis válidos
                for it in items:
                    role = it.get("role")
                    assert role in valid_roles, f"[{unit.id}:{q.get('id')}] Papel SOV inválido: {role}"
                for sl in slots:
                    for r in sl.get("accepted_roles", []):
                        assert r in valid_roles or r == "ANY", f"[{unit.id}:{q.get('id')}] Papel esperado inválido: {r}"
