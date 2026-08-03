import json
import os
from typing import List, Optional
import flet as ft
from .models import Unit, UnitIntroData, UnitOneData

class DataService:
    @staticmethod
    def get_curriculum() -> List[Unit]:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "data", "curriculum.json")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Unit(**item) for item in data]
        except Exception as e:
            print(f"Error loading curriculum: {e}")
            return []

    @staticmethod
    def get_unit_intro() -> Optional[UnitIntroData]:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "data", "units", "unit_intro.json")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return UnitIntroData(**data)
        except Exception as e:
            print(f"Error loading unit_intro: {e}")
            return None

    @staticmethod
    def get_unit_one() -> Optional[UnitOneData]:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "data", "units", "unit_01.json")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return UnitOneData(**data)
        except Exception as e:
            print(f"Error loading unit_01: {e}")
            return None

class ProgressService:
    """Gerenciador de progresso e preferências em memória (alpha).
    Usa um dicionário simples ao invés de shared_preferences (assíncrono)
    para compatibilidade com a construção síncrona das views do Flet."""
    
    _store: dict = {}

    def __init__(self, page: ft.Page):
        self.page = page

    def get_progress(self, unit_id: str) -> float:
        val = ProgressService._store.get(f"progress_{unit_id}", 0.0)
        return float(val)

    def save_progress(self, unit_id: str, progress: float) -> None:
        ProgressService._store[f"progress_{unit_id}"] = float(progress)
        
        # Lógica de desbloqueio simples para o Beta
        if progress >= 1.0:
            if unit_id == "unit_intro":
                ProgressService._store["unlocked_unit_01"] = True
            elif unit_id == "unit_01":
                ProgressService._store["unlocked_unit_02"] = True

    def is_unlocked(self, unit_id: str) -> bool:
        if unit_id in ["unit_intro", "unit_01"]:
            return True
        return bool(ProgressService._store.get(f"unlocked_{unit_id}", False))


