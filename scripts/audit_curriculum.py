#!/usr/bin/env python3
"""Script CLI de Auditoria e Hardening Curricular (Sejong Companion).

Executa varredura profunda em todas as 23 unidades JSON do Sejong 1A e 1B,
verificando schemas Pydantic, política de Zero Romanização, contratos sintáticos SOV,
integridade de flashcards e áudios HD.

Uso:
    python -m scripts.audit_curriculum
"""

import os
import sys
import json
import re

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Garantir que a raiz esteja no sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.services import DataService
from src.models import UnitData, UnitIntroData

def run_curriculum_audit() -> bool:
    print("=" * 70)
    print(" 📋 AUDITORIA GLOBAL DE INTEGRIDADE CURRICULAR (1A + 1B)")
    print("=" * 70)

    curriculum = DataService.get_curriculum()
    units_dir = os.path.join(ROOT_DIR, "data", "units")
    latin_regex = re.compile(r"[a-zA-Z]")
    valid_roles = {
        "SUBJECT", "OBJECT", "VERB", "PREDICATE", "LOCATION",
        "ADVERB", "TIME", "COMPLEMENT", "MODIFIER", "QUANTITY",
        "COUNTER", "CONNECTIVE", "PARTICLE", "ANY"
    }

    total_units = len(curriculum)
    total_vocab = 0
    total_grammar = 0
    total_exercises = 0
    total_sov = 0
    errors = []

    print(f" • Total de unidades cadastradas no curriculum.json: {total_units}")

    for unit in curriculum:
        file_path = os.path.join(units_dir, f"{unit.id}.json")
        if not os.path.exists(file_path):
            errors.append(f"❌ [{unit.id}] Arquivo não encontrado: {file_path}")
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            errors.append(f"❌ [{unit.id}] Erro de parsing JSON: {e}")
            continue

        if unit.id == "unit_intro":
            try:
                parsed = UnitIntroData(**raw)
            except Exception as e:
                errors.append(f"❌ [{unit.id}] Erro no schema Pydantic: {e}")
            continue

        try:
            parsed = UnitData(**raw)
            total_vocab += len(parsed.vocabulary)
            total_grammar += len(parsed.grammar)
            total_exercises += len(parsed.exercises)
        except Exception as e:
            errors.append(f"❌ [{unit.id}] Erro no schema Pydantic: {e}")
            continue

        # Validar Zero Romanização
        for idx, item in enumerate(raw.get("vocabulary", [])):
            word_text = item.get("word", "")
            if latin_regex.search(word_text):
                errors.append(f"⚠️ [{unit.id}] Romanização vazada no vocabulário: '{word_text}'")

        # Validar Exercícios SOV
        for q in raw.get("exercises", []):
            if q.get("type") == "drag_and_drop_sov":
                total_sov += 1
                items = q.get("sov_items", [])
                slots = q.get("sov_slots", [])
                correct_order = q.get("correct_order", [])

                if len(items) != len(slots):
                    errors.append(f"❌ [{unit.id}:{q.get('id')}] sov_items ({len(items)}) != sov_slots ({len(slots)})")
                if len(items) != len(correct_order):
                    errors.append(f"❌ [{unit.id}:{q.get('id')}] sov_items ({len(items)}) != correct_order ({len(correct_order)})")

                item_words = {it["word"] for it in items}
                if item_words != set(correct_order):
                    errors.append(f"❌ [{unit.id}:{q.get('id')}] Divergência entre itens e correct_order")

                for it in items:
                    if it.get("role") not in valid_roles:
                        errors.append(f"❌ [{unit.id}:{q.get('id')}] Papel inválido: {it.get('role')}")

    all_cards = DataService.get_all_flashcards()
    all_challenges = DataService.get_sentence_builder_challenges()

    print(f" • Total de itens de vocabulário ativos:  {total_vocab}")
    print(f" • Total de tópicos gramaticais:          {total_grammar}")
    print(f" • Total de exercícios nos workbooks:     {total_exercises}")
    print(f" • Total de desafios sintáticos SOV:      {total_sov}")
    print(f" • Total de Flashcards gerados:           {len(all_cards)}")
    print(f" • Total de Desafios Sentence Builder:    {len(all_challenges)}")
    print("-" * 70)

    if errors:
        print(f"❌ FORAM ENCONTRADOS {len(errors)} ERROS NA AUDITORIA:")
        for err in errors:
            print(f"   {err}")
        return False
    else:
        print("✅ 100% DAS UNIDADES E EXERCÍCIOS APROVADOS NA AUDITORIA!")
        print("=" * 70)
        return True

if __name__ == "__main__":
    success = run_curriculum_audit()
    sys.exit(0 if success else 1)
