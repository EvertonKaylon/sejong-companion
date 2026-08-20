import json
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import flet as ft
from .models import FlashcardItem, Unit, UnitIntroData, UnitOneData, UnitData, MemoryNode, PedagogicalEvent

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
        return DataService.get_unit("unit_01")

    @staticmethod
    def get_unit(unit_id: str) -> Optional[UnitData]:
        """Carrega qualquer unidade (01–10) pelo ID genérico."""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, "data", "units", f"{unit_id}.json")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return UnitData(**data)
        except Exception as e:
            print(f"Error loading {unit_id}: {type(e).__name__}")
            return None

    @staticmethod
    def _get_all_unit_ids() -> List[str]:
        """Retorna os IDs de todas as unidades dos livros 1A e 1B em ordem sequencial."""
        unit_ids = [f"unit_{n:02d}" for n in range(1, 11)]
        unit_ids += [f"unit_1b_{n:02d}" for n in range(1, 13)]
        return unit_ids

    @staticmethod
    def _flashcard_difficulty(unit_number: int, word: str, category: str) -> str:
        """Classifica o material sem exigir uma segunda cópia dos JSONs.

        Itens básicos permanecem fáceis mesmo quando reaparecem em unidades
        posteriores. Estruturas gramaticais avançadas e o conteúdo das últimas
        unidades entram na trilha difícil.
        """
        normalized = f"{word} {category}".lower()
        easy_terms = ("cumpr", "pronom", "numero", "수", "인사", "나라")
        hard_markers = ("았", "었", "겠", "싶", "까요", "불규칙", "ㅂ", "classificador", "단위", "보다", "에게", "니까", "어야", "려고", "수 있")
        if any(term in normalized for term in easy_terms) or unit_number <= 2:
            return "easy"
        if any(marker in normalized for marker in hard_markers) or unit_number >= 6:
            return "hard"
        return "medium"

    @staticmethod
    def get_all_flashcards(difficulty: Optional[str] = None) -> List[FlashcardItem]:
        """Compila o vocabulário de todas as unidades dos livros 1A e 1B em cartões consistentes."""
        cards: List[FlashcardItem] = []
        for idx, unit_id in enumerate(DataService._get_all_unit_ids(), start=1):
            unit = DataService.get_unit(unit_id)
            if not unit:
                continue
            for index, vocab in enumerate(unit.vocabulary):
                level = DataService._flashcard_difficulty(idx, vocab.word, vocab.category or "")
                if difficulty and difficulty != level:
                    continue
                cards.append(FlashcardItem(
                    id=f"{unit_id}:vocab:{index}",
                    unit_id=unit_id,
                    korean=vocab.word,
                    portuguese=vocab.meaning,
                    difficulty=level,
                    category=vocab.category or "vocabulário",
                    example_kr=vocab.example_kr,
                    example_pt=vocab.example_pt,
                    lusophone_tip=vocab.neuro_tip,
                ))
        return cards

    @staticmethod
    def get_sentence_builder_challenges(difficulty: str) -> List[dict]:
        """Extrai desafios SOV existentes para não duplicar o currículo."""
        if difficulty not in {"easy", "medium", "hard"}:
            return []
        challenges: List[dict] = []
        for idx, unit_id in enumerate(DataService._get_all_unit_ids(), start=1):
            unit = DataService.get_unit(unit_id)
            if not unit:
                continue
            for exercise in unit.exercises:
                if exercise.type != "drag_and_drop_sov" or not exercise.correct_order:
                    continue
                category = "sintaxe"
                level = DataService._flashcard_difficulty(idx, " ".join(exercise.correct_order), category)
                if level != difficulty:
                    continue
                prompt = exercise.question.split(":", 1)[-1].strip()
                challenges.append({
                    "id": f"builder:{unit_id}:{exercise.id}",
                    "unit_id": unit_id,
                    "difficulty": level,
                    "prompt_pt": prompt,
                    "answer": " ".join(exercise.correct_order),
                    "words": list(exercise.words or exercise.correct_order),
                    "correct_order": list(exercise.correct_order),
                    "sov_breakdown": [item.model_dump() for item in (exercise.sov_items or [])],
                    "explanation": exercise.explanation or "",
                })
        return challenges

    @staticmethod
    def get_priority_audio_texts() -> List[str]:
        """Retorna o lote prioritário para aquecimento rápido no Splash (Hangul + Lab Oclusivo + Unit 01)."""
        texts: List[str] = []
        # 1. Hangul Básico e Oclusivas
        intro = DataService.get_unit_intro()
        if intro:
            texts.extend([v.char for v in intro.vowels if v.char])
            texts.extend([c.char for c in intro.consonants if c.char])
            if intro.aspirated_consonants:
                texts.extend([c.char for c in intro.aspirated_consonants if c.char])
            if intro.tense_consonants:
                texts.extend([c.char for c in intro.tense_consonants if c.char])

        # 2. Consoantes e Sons Vocalizados do Laboratório Fonético Oclusivo ([ㅏ])
        texts.extend(["ㄱ", "ㅋ", "ㄲ", "ㄷ", "ㅌ", "ㄸ", "ㅂ", "ㅍ", "ㅃ", "ㅈ", "ㅊ", "ㅉ"])
        texts.extend(["가", "카", "까", "다", "타", "따", "바", "파", "빠", "자", "차", "짜"])

        # 3. Vocabulário da Unidade 01
        u1 = DataService.get_unit("unit_01")
        if u1:
            for v in u1.vocabulary:
                if v.word:
                    texts.append(v.word)

        # Deduplicação mantendo ordem
        seen = set()
        deduped = []
        for t in texts:
            clean = t.strip()
            if clean and clean not in seen:
                seen.add(clean)
                deduped.append(clean)
        return deduped

    @staticmethod
    def get_all_audio_texts() -> List[str]:
        """Extrai e desduplica TODOS os textos com áudio do currículo completo (1A e 1B)."""
        texts = list(DataService.get_priority_audio_texts())

        # 1. Sílabas do Hangul
        intro = DataService.get_unit_intro()
        if intro and intro.syllables:
            texts.extend([s.block for s in intro.syllables if s.block])

        # 2. Todas as Unidades 1A e 1B (Vocabulário e Frases de Exemplo)
        for unit_id in DataService._get_all_unit_ids():
            unit = DataService.get_unit(unit_id)
            if not unit:
                continue
            for v in unit.vocabulary:
                if v.word:
                    texts.append(v.word)
                if v.example_kr:
                    texts.append(v.example_kr)
            for g in unit.grammar:
                for ex in g.examples:
                    if ex.kr:
                        texts.append(ex.kr)

        # Deduplicação mantendo ordem
        seen = set()
        deduped = []
        for t in texts:
            clean = t.strip()
            if clean and clean not in seen:
                seen.add(clean)
                deduped.append(clean)
        return deduped

class ProgressService:
    """Motor de Gestão do Aluno, Progresso e Retenção Adaptativa por Meia-Vida.
    
    Arquitetura de 4 Pilares Ortogonais:
      1. XP (Motivação): Cosmético e atrativo; recompensa disciplina e presença sem afetar a pedagogia.
      2. Mastery (Aprendizagem): Domínio morfossintático medido por acertos consistentes.
      3. Retention (Memória): Estabilidade temporal de evocação modelada por meia-vida (SRS).
      4. Completion (Progresso Curricular): Cobertura formal das lições e desbloqueio de unidades.
    
    A persistência opera via Persistent Student ID (page.client_storage no cliente) e
    gravação atômica em data/sessions/student_{id}.json.
    """
    
    _file_path_override: Optional[str] = None  # Override para testes
    _sessions: dict = {}  # {session_id: store_dict}
    DAILY_XP = 10
    MILESTONE_XP = 50

    # Cadeia de desbloqueio progressivo: ao completar a chave, desbloqueia o valor
    _UNLOCK_CHAIN: dict = {
        "unit_intro": "unit_01",
        "unit_01": "unit_02",
        "unit_02": "unit_03",
        "unit_03": "unit_04",
        "unit_04": "unit_05",
        "unit_05": "unit_06",
        "unit_06": "unit_07",
        "unit_07": "unit_08",
        "unit_08": "unit_09",
        "unit_09": "unit_10",
        "unit_10": "unit_1b_01",
        "unit_1b_01": "unit_1b_02",
        "unit_1b_02": "unit_1b_03",
        "unit_1b_03": "unit_1b_04",
        "unit_1b_04": "unit_1b_05",
        "unit_1b_05": "unit_1b_06",
        "unit_1b_06": "unit_1b_07",
        "unit_1b_07": "unit_1b_08",
        "unit_1b_08": "unit_1b_09",
        "unit_1b_09": "unit_1b_10",
        "unit_1b_10": "unit_1b_11",
        "unit_1b_11": "unit_1b_12",
    }

    @staticmethod
    def _get_session_id(page) -> str:
        """Obtém ou recupera a identidade persistente do aluno (Persistent Student ID).
        
        Prioriza o client_storage (localStorage do navegador / SharedPreferences nativo)
        para que fechar/reabrir o navegador preserve o mesmo ID e arquivo de progresso.
        """
        if page is None:
            return "__default__"

        # 1. Se já cacheado em memória no objeto page da sessão ativa
        if hasattr(page, "_sejong_student_id") and page._sejong_student_id:
            return str(page._sejong_student_id)
        if hasattr(page, "_sejong_session_id") and page._sejong_session_id:
            return str(page._sejong_session_id)

        # 2. Tenta recuperar do client_storage do dispositivo
        student_id = None
        try:
            if hasattr(page, "client_storage") and page.client_storage:
                student_id = page.client_storage.get("sejong_student_id")
        except Exception:
            student_id = None

        if student_id and isinstance(student_id, str) and student_id.strip():
            safe_id = student_id.strip()
            page._sejong_student_id = safe_id
            page._sejong_session_id = safe_id
            return safe_id

        # 3. Se é o primeiro acesso deste cliente, gera e persiste
        import uuid
        new_id = f"student_{uuid.uuid4().hex[:12]}"
        try:
            if hasattr(page, "client_storage") and page.client_storage:
                page.client_storage.set("sejong_student_id", new_id)
        except Exception:
            pass

        page._sejong_student_id = new_id
        page._sejong_session_id = new_id
        return new_id

    @classmethod
    def _get_storage_path(cls, session_id: str) -> str:
        if cls._file_path_override:
            return cls._file_path_override
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ("-", "_")) or "default"
        return os.path.join(base_dir, "data", "sessions", f"{safe_id}.json")

    @classmethod
    def _load_from_disk(cls, session_id: str) -> dict:
        path = cls._get_storage_path(session_id)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception as e:
                print(f"[ProgressService] Warning: Error reading session {session_id}: {e}")
        return {}

    @classmethod
    def _save_to_disk(cls, session_id: str, data: dict) -> None:
        path = cls._get_storage_path(session_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp_path = f"{path}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, path)
        except Exception as e:
            print(f"[ProgressService] Error writing session {session_id}: {e}")
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def __init__(self, page=None):
        self.page = page
        self._session_id = self._get_session_id(page)
        # Inicializar store desta sessão a partir do disco, se ainda não carregada
        if self._session_id not in ProgressService._sessions:
            ProgressService._sessions[self._session_id] = self._load_from_disk(self._session_id)

    @property
    def _store(self) -> dict:
        """Retorna o store isolado desta sessão."""
        return ProgressService._sessions.setdefault(self._session_id, {})

    def get_student_id(self) -> str:
        """Retorna a identidade persistente do aluno."""
        return self._session_id

    def get_student_name(self) -> str:
        """Retorna o nome personalizado do aluno ou o padrão."""
        return str(self._store.get("student_name", "Estudante Sejong"))

    def set_student_name(self, name: str) -> str:
        """Atualiza o nome do aluno no perfil e sincroniza."""
        clean_name = name.strip() or "Estudante Sejong"
        self._store["student_name"] = clean_name
        ProgressService._save_to_disk(self._session_id, self._store)
        try:
            if hasattr(self.page, "client_storage") and self.page.client_storage:
                self.page.client_storage.set("sejong_student_name", clean_name)
        except Exception:
            pass
        return clean_name

    def export_backup(self) -> str:
        """Exporta o progresso completo e nós de memória em formato JSON string."""
        payload = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "student_id": self._session_id,
            "data": self._store,
        }
        return json.dumps(payload, indent=2, ensure_ascii=False)

    def import_backup(self, backup_json: str) -> bool:
        """Restaura o progresso a partir de uma string JSON de backup válida."""
        try:
            raw = json.loads(backup_json)
            if not isinstance(raw, dict):
                return False
            data_to_restore = raw.get("data") if "data" in raw and isinstance(raw["data"], dict) else raw
            if not isinstance(data_to_restore, dict):
                return False
            self._store.clear()
            self._store.update(data_to_restore)
            ProgressService._save_to_disk(self._session_id, self._store)
            return True
        except Exception as e:
            print(f"[ProgressService] Erro ao importar backup: {e}")
            return False

    def get_progress(self, unit_id: str) -> float:
        val = self._store.get(f"progress_{unit_id}", 0.0)
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    def save_progress(self, unit_id: str, progress: float) -> None:
        val = float(progress)
        self._store[f"progress_{unit_id}"] = val

        # Desbloqueio progressivo via cadeia data-driven
        if val >= 1.0 and unit_id in ProgressService._UNLOCK_CHAIN:
            next_unit = ProgressService._UNLOCK_CHAIN[unit_id]
            self._store[f"unlocked_{next_unit}"] = True

        # Gravação persistente atômica em disco
        ProgressService._save_to_disk(self._session_id, self._store)

    def is_unlocked(self, unit_id: str) -> bool:
        if unit_id in ["unit_intro", "unit_01"]:
            return True
        return bool(self._store.get(f"unlocked_{unit_id}", False))

    def reset_progress(self) -> None:
        """Reseta o progresso da sessão atual."""
        self._store.clear()
        ProgressService._save_to_disk(self._session_id, self._store)

    def get_all_progress(self) -> dict:
        """Retorna uma cópia dos dados de progresso desta sessão."""
        return dict(self._store)

    # ─── SRS (Modelo Heurístico de Retenção Baseado em Meia-Vida) ───

    def get_memory_node(self, unit_id: str) -> MemoryNode:
        """Obtém ou cria o MemoryNode de uma unidade."""
        key = f"memory_{unit_id}"
        raw = self._store.get(key)
        if raw and isinstance(raw, dict):
            return MemoryNode(**raw)
        return MemoryNode(unit_id=unit_id)

    def save_memory_node(self, node: MemoryNode) -> None:
        """Salva o MemoryNode no store e persiste em disco."""
        key = f"memory_{node.unit_id}"
        self._store[key] = node.model_dump()
        ProgressService._save_to_disk(self._session_id, self._store)

    def record_review(self, unit_id: str, is_correct: bool, response_time_ms: int = 2000) -> MemoryNode:
        """Registra uma revisão de uma unidade e atualiza a meia-vida."""
        node = self.get_memory_node(unit_id)
        node.update_performance(is_correct, response_time_ms)
        self.save_memory_node(node)
        return node

    def get_vitality(self, unit_id: str) -> str:
        """Retorna o nível de vitalidade ('high', 'medium', 'low') de uma unidade."""
        node = self.get_memory_node(unit_id)
        if not node.last_reviewed:
            return "none"  # Nunca estudada
        return node.vitality_level()

    # ─── Revisão diária por item ───

    def get_item_memory_node(self, item_id: str) -> MemoryNode:
        """Obtém a memória individual sem colidir com nós legados de unidade."""
        key = f"memory_item_{item_id}"
        raw = self._store.get(key)
        if raw and isinstance(raw, dict):
            return MemoryNode(**raw)
        return MemoryNode(unit_id=item_id)

    def _save_item_memory_node(self, item_id: str, node: MemoryNode) -> None:
        self._store[f"memory_item_{item_id}"] = node.model_dump()
        ProgressService._save_to_disk(self._session_id, self._store)

    def get_due_reviews(self) -> List[dict]:
        """Retorna apenas cartões já estudados com retenção abaixo de 75%."""
        due_reviews: List[dict] = []
        cards = {card.id: card for card in DataService.get_all_flashcards()}
        for key, raw in self._store.items():
            if not key.startswith("memory_item_") or not isinstance(raw, dict):
                continue
            item_id = key.removeprefix("memory_item_")
            card = cards.get(item_id)
            if not card:
                continue
            try:
                node = MemoryNode(**raw)
                retention = node.calculate_stability()
            except Exception:
                continue
            if node.last_reviewed and retention < 0.75:
                due_reviews.append({
                    "item": card,
                    "retention": retention,
                    "half_life": node.half_life,
                    "last_reviewed": node.last_reviewed,
                })
        return sorted(due_reviews, key=lambda review: review["retention"])

    def record_item_recall(self, item_id: str, rating: str, response_time_ms: int = 2000) -> MemoryNode:
        """Atualiza a meia-vida com os multiplicadores heurísticos da autoavaliação."""
        rating = rating.lower().strip()
        multipliers = {"again": 0.3, "hard": 0.3, "good": 1.5, "easy": 2.2}
        if rating not in multipliers:
            raise ValueError("rating deve ser again, hard, good ou easy")
        node = self.get_item_memory_node(item_id)
        node.half_life = max(0.01, node.half_life * multipliers[rating])
        if rating in {"again", "hard"}:
            node.error_count += 1
        elif node.error_count:
            node.error_count -= 1
        node.last_reviewed = datetime.now().isoformat()
        self._save_item_memory_node(item_id, node)
        self.record_daily_activity()
        return node

    def get_daily_streak(self) -> int:
        """Compatibilidade para o contador de dias estudados.

        O nome histórico é preservado para não quebrar a aplicação, mas ele
        não representa uma sequência consecutiva: faltar um dia nunca reduz
        este número.
        """
        return int(self._store.get("study_days", self._store.get("daily_streak", 0)) or 0)

    def get_study_days(self, year: Optional[int] = None) -> int:
        """Conta dias distintos de estudo; por padrão, no ano atual."""
        target_year = year or date.today().year
        dates = self._store.get("study_dates", [])
        if isinstance(dates, list):
            return sum(1 for value in set(dates) if str(value).startswith(f"{target_year}-"))
        return 0

    def get_total_xp(self) -> int:
        """XP de presença, acumulado e nunca penalizado por ausências."""
        return int(self._store.get("total_xp", 0) or 0)

    @classmethod
    def _is_milestone(cls, study_days: int) -> bool:
        """Marcos: 7 dias e, depois, 15, 20, 25, 30..."""
        return study_days == 7 or (study_days >= 15 and study_days % 5 == 0)

    def record_daily_activity(self) -> int:
        """Registra presença uma vez ao dia, sem quebrar sequência por falta.

        Cada novo dia soma o XP padrão. Os marcos de disciplina recebem XP
        extra, sem depender de acertos, velocidade ou quantidade de cartões.
        """
        today = date.today()
        today_value = today.isoformat()
        recorded_dates = self._store.get("study_dates", [])
        recorded_dates = recorded_dates if isinstance(recorded_dates, list) else []
        # Dados anteriores tinham apenas a última data + streak. Mantemos a
        # contagem legada como piso, sem fingir conhecer as datas antigas.
        total_days = self.get_daily_streak()
        if today_value in recorded_dates or self._store.get("last_activity_date") == today_value:
            return total_days

        recorded_dates.append(today_value)
        total_days += 1
        bonus = ProgressService.MILESTONE_XP if self._is_milestone(total_days) else 0
        earned = ProgressService.DAILY_XP + bonus
        self._store["study_dates"] = recorded_dates
        self._store["study_days"] = total_days
        # Mantém o nome antigo para instalações que já persistiam esse campo.
        self._store["daily_streak"] = total_days
        self._store["last_activity_date"] = today.isoformat()
        self._store["total_xp"] = self.get_total_xp() + earned
        self._store["last_activity_reward"] = {
            "date": today_value,
            "base_xp": ProgressService.DAILY_XP,
            "bonus_xp": bonus,
            "total_xp": earned,
            "milestone": total_days if bonus else None,
        }
        ProgressService._save_to_disk(self._session_id, self._store)
        return total_days


class FullscreenService:
    """Serviço para alternância de Tela Cheia (Fullscreen) e responsividade Mobile/PWA."""

    @staticmethod
    def toggle_fullscreen(page: ft.Page):
        new_state = False
        try:
            # 1. Toggle via propriedade oficial Flet
            if hasattr(page, "window"):
                current_state = bool(getattr(page.window, "full_screen", False))
                new_state = not current_state
                page.window.full_screen = new_state
                page.update()
        except Exception as e:
            print(f"Error toggling page.window.full_screen: {e}")

        # 2. Tentar via JS launch_url para navegadores Web
        js_code = (
            "if(!document.fullscreenElement && !document.webkitFullscreenElement){"
            "var d=document.documentElement;var r=d.requestFullscreen||d.webkitRequestFullscreen;"
            "if(r){r.call(d);}"
            "}else{"
            "var x=document.exitFullscreen||document.webkitExitFullscreen;"
            "if(x){x.call(document);}"
            "}"
        )

        async def _exec_js():
            # BUGFIX (11/08): page.launch_url() NÃO executa JS na página -- ele delega
            # pro plugin Flutter url_launcher, que trata a string como uma URL/link
            # externo. Em contexto web isso pelo menos tenta rodar como "javascript:"
            # URI; em janela desktop nativa (AppView.FLET_APP, o padrão do ft.app()
            # quando não se passa view=) não existe documento HTML nenhum, e o
            # Windows não sabe abrir um link "javascript:...". Isso derruba a conexão
            # do cliente Flutter, que reconecta automaticamente, recriando a sessão
            # e disparando este mesmo código de novo -- loop infinito de
            # "RuntimeError: Session closed" / "attempt to fetch destroyed session".
            # Guard com page.web (mesmo padrão usado internamente pelo próprio Flet
            # para o fluxo de OAuth) resolve na raiz.
            if not getattr(page, "web", False):
                return
            try:
                if hasattr(page, 'launch_url'):
                    await page.launch_url(f"javascript:{js_code}")
            except Exception:
                pass

        try:
            if hasattr(page, 'run_task'):
                page.run_task(_exec_js)
        except Exception:
            pass

        # 3. Notificação visual de confirmação ao usuário
        try:
            msg = "📱 Modo Tela Cheia Ativado! (Dica: no celular, você também pode 'Adicionar à Tela de Início' para abrir como App Nativo)" if new_state else "📱 Modo Tela Cheia Desativado"
            snack = ft.SnackBar(
                content=ft.Text(msg, size=12, weight=ft.FontWeight.BOLD),
                duration=2500,
                open=True
            )
            page.overlay.append(snack)
            page.update()
        except Exception:
            pass

    @staticmethod
    def setup_mobile_responsive_viewport(page: ft.Page):
        """Injeta meta-tags de viewport e PWA para o navegador mobile se comportar como App instalado."""
        js_meta = (
            "(function(){"
            "var m=document.querySelector('meta[name=\"viewport\"]');"
            "if(!m){m=document.createElement('meta');m.name='viewport';document.head.appendChild(m);}"
            "m.content='width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover';"
            "var t=document.querySelector('meta[name=\"theme-color\"]');"
            "if(!t){t=document.createElement('meta');t.name='theme-color';document.head.appendChild(t);}"
            "t.content='#02060E';"
            "var ap=document.createElement('meta');ap.name='apple-mobile-web-app-capable';ap.content='yes';document.head.appendChild(ap);"
            "var st=document.createElement('meta');st.name='apple-mobile-web-app-status-bar-style';st.content='black-translucent';document.head.appendChild(st);"
            "})();"
        )

        async def _exec_meta():
            # BUGFIX (11/08): mesma causa raiz do _exec_js em toggle_fullscreen (ver
            # comentário lá). Esta função em especial roda incondicionalmente em TODA
            # sessão (chamada direto em main.py), então era a origem do loop de
            # reconexão infinita reportado ao rodar `python main.py` no Windows sem
            # view=WEB_BROWSER (ft.app() abre janela desktop nativa por padrão).
            # Meta tags de viewport/PWA também só fazem sentido em navegador --
            # não existe <head> HTML numa janela desktop nativa.
            if not getattr(page, "web", False):
                return
            try:
                if hasattr(page, 'launch_url'):
                    await page.launch_url(f"javascript:{js_meta}")
            except Exception:
                pass

        try:
            if hasattr(page, 'run_task'):
                page.run_task(_exec_meta)
        except Exception:
            pass

    @staticmethod
    def create_fullscreen_button(page: ft.Page, colors: dict) -> ft.IconButton:
        """Cria um botão com ícone de entrar/sair da Tela Cheia para ser usado nas AppBars."""
        return ft.IconButton(
            icon=ft.Icons.FULLSCREEN_ROUNDED,
            icon_color=colors["primary"],
            on_click=lambda e: FullscreenService.toggle_fullscreen(page),
            tooltip="Alternar Modo Tela Cheia (Fullscreen)",
        )


# ─── Telemetria e Evidência Pedagógica Local (Zero PII) ───

class TelemetryService:
    """Serviço de registro de eventos pedagógicos em disco local (append-only JSONL).
    
    Garante persistência de interação atômica e leve O(1) sem carregar logs na RAM.
    Zero dados pessoais (PII) — coleta estritamente métricas didáticas e temporais.
    """
    _telemetry_dir_override: Optional[str] = None

    @classmethod
    def _get_telemetry_dir(cls) -> str:
        if cls._telemetry_dir_override:
            os.makedirs(cls._telemetry_dir_override, exist_ok=True)
            return cls._telemetry_dir_override
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        telemetry_dir = os.path.join(base_dir, "data", "telemetry")
        os.makedirs(telemetry_dir, exist_ok=True)
        return telemetry_dir

    @classmethod
    def _get_log_path(cls, session_id: str) -> str:
        safe_id = "".join(c for c in session_id if c.isalnum() or c in ("-", "_")) or "default"
        return os.path.join(cls._get_telemetry_dir(), f"events_{safe_id}.jsonl")

    @classmethod
    def record(cls, session_id: str, event: PedagogicalEvent) -> bool:
        """Grava um evento pedagógico no arquivo JSONL da sessão em modo append."""
        try:
            path = cls._get_log_path(session_id)
            with open(path, "a", encoding="utf-8") as f:
                f.write(event.model_dump_json() + "\n")
            return True
        except Exception as e:
            print(f"[TelemetryService] Erro ao gravar evento: {e}")
            return False

    @classmethod
    def get_events(cls, session_id: Optional[str] = None) -> List[PedagogicalEvent]:
        """Carrega eventos registrados de uma sessão específica ou de todas as sessões."""
        events: List[PedagogicalEvent] = []
        target_dir = cls._get_telemetry_dir()
        if not os.path.exists(target_dir):
            return events

        if session_id:
            files = [cls._get_log_path(session_id)]
        else:
            files = [
                os.path.join(target_dir, f)
                for f in os.listdir(target_dir)
                if f.startswith("events_") and f.endswith(".jsonl")
            ]

        for file_path in files:
            if not os.path.exists(file_path):
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line_str = line.strip()
                        if not line_str:
                            continue
                        try:
                            raw = json.loads(line_str)
                            events.append(PedagogicalEvent(**raw))
                        except Exception:
                            # Ignora linhas corrompidas sem quebrar a leitura
                            continue
            except Exception as e:
                print(f"[TelemetryService] Erro ao ler {file_path}: {e}")

        # Ordenar cronologicamente
        events.sort(key=lambda ev: ev.timestamp)
        return events

    @classmethod
    def clear_events(cls, session_id: Optional[str] = None) -> int:
        """Remove arquivos de log de eventos (útil para testes ou reset de dados)."""
        target_dir = cls._get_telemetry_dir()
        if not os.path.exists(target_dir):
            return 0
        removed = 0
        if session_id:
            path = cls._get_log_path(session_id)
            if os.path.exists(path):
                os.remove(path)
                removed += 1
        else:
            for f in os.listdir(target_dir):
                if f.startswith("events_") and f.endswith(".jsonl"):
                    os.remove(os.path.join(target_dir, f))
                    removed += 1
        return removed


class PedagogicalAnalyzer:
    """Motor analítico determinístico local para extrair evidência pedagógica dos logs."""

    @staticmethod
    def analyze(events: List[PedagogicalEvent]) -> Dict[str, Any]:
        """Processa a lista de eventos e retorna diagnósticos pedagógicos estruturados."""
        total_events = len(events)
        if total_events == 0:
            return {
                "total_events": 0,
                "hardest_questions": [],
                "drop_off_units": [],
                "critical_vocab": [],
                "avg_response_times": {},
                "session_summary": {"total_quizzes_completed": 0, "total_reviews_completed": 0},
            }

        # 1. Estatísticas de Questões
        question_stats = defaultdict(lambda: {
            "unit_id": "",
            "total": 0,
            "errors": 0,
            "times": [],
            "types": set(),
        })

        # 2. Estatísticas de Unidades (Abertura vs Conclusão)
        units_opened = defaultdict(int)
        units_completed = defaultdict(int)

        # 3. Estatísticas de Flashcards (Avaliações no Active Recall)
        cards_ratings = defaultdict(lambda: {
            "unit_id": "",
            "again": 0,
            "hard": 0,
            "good": 0,
            "easy": 0,
            "times": [],
        })

        # 4. Tempos de resposta agregados
        times_by_type = defaultdict(list)
        total_quizzes_completed = 0
        total_reviews_completed = 0

        for ev in events:
            # Questões respondidas
            if ev.event_type == "question_answered":
                qid = ev.item_id or "unknown"
                q = question_stats[qid]
                q["unit_id"] = ev.unit_id
                q["total"] += 1
                is_correct = bool(ev.payload.get("correct", False))
                if not is_correct:
                    q["errors"] += 1
                resp_time = ev.payload.get("response_time_ms")
                if isinstance(resp_time, (int, float)) and resp_time > 0:
                    q["times"].append(resp_time)
                    q_type = ev.payload.get("question_type", "multiple_choice")
                    times_by_type[f"quiz_{q_type}"].append(resp_time)

            # Abertura e conclusão de lição
            elif ev.event_type == "lesson_opened":
                units_opened[ev.unit_id] += 1
            elif ev.event_type == "lesson_completed":
                units_completed[ev.unit_id] += 1

            # Quiz concluído
            elif ev.event_type == "quiz_completed":
                total_quizzes_completed += 1

            # Revisão de Flashcard
            elif ev.event_type == "flashcard_rated":
                cid = ev.item_id or "unknown"
                c = cards_ratings[cid]
                c["unit_id"] = ev.unit_id
                rating = str(ev.payload.get("rating", "good")).lower().strip()
                if rating in ("again", "hard", "good", "easy"):
                    c[rating] += 1
                resp_time = ev.payload.get("response_time_ms")
                if isinstance(resp_time, (int, float)) and resp_time > 0:
                    c["times"].append(resp_time)
                    times_by_type["flashcard_recall"].append(resp_time)

            # Revisão diária concluída
            elif ev.event_type == "review_completed":
                total_reviews_completed += 1

        # Compilar Questões mais difíceis (ordenadas por taxa de erro desc)
        hardest_questions: List[dict] = []
        for qid, data in question_stats.items():
            total = data["total"]
            errors = data["errors"]
            error_rate = (errors / total) if total > 0 else 0.0
            avg_time = (sum(data["times"]) / len(data["times"])) if data["times"] else 0.0
            hardest_questions.append({
                "question_id": qid,
                "unit_id": data["unit_id"],
                "total_attempts": total,
                "errors": errors,
                "error_rate": round(error_rate, 4),
                "avg_response_time_ms": round(avg_time, 1),
            })
        hardest_questions.sort(key=lambda x: (x["error_rate"], x["total_attempts"]), reverse=True)

        # Compilar Abandono de Unidades
        drop_off_units: List[dict] = []
        all_units = set(units_opened.keys()).union(set(units_completed.keys()))
        for uid in sorted(all_units):
            opened = units_opened.get(uid, 0)
            completed = units_completed.get(uid, 0)
            drop_rate = 1.0 - (completed / opened) if opened > 0 else 0.0
            drop_off_units.append({
                "unit_id": uid,
                "opened_count": opened,
                "completed_count": completed,
                "drop_off_rate": round(max(0.0, drop_rate), 4),
            })
        drop_off_units.sort(key=lambda x: x["drop_off_rate"], reverse=True)

        # Compilar Vocabulário Crítico (ordenado por contagem e taxa de 'again')
        critical_vocab: List[dict] = []
        for cid, data in cards_ratings.items():
            total_reviews = data["again"] + data["hard"] + data["good"] + data["easy"]
            again_rate = (data["again"] / total_reviews) if total_reviews > 0 else 0.0
            avg_time = (sum(data["times"]) / len(data["times"])) if data["times"] else 0.0
            critical_vocab.append({
                "item_id": cid,
                "unit_id": data["unit_id"],
                "again_count": data["again"],
                "hard_count": data["hard"],
                "good_count": data["good"],
                "easy_count": data["easy"],
                "total_reviews": total_reviews,
                "again_rate": round(again_rate, 4),
                "avg_response_time_ms": round(avg_time, 1),
            })
        critical_vocab.sort(key=lambda x: (x["again_count"], x["again_rate"]), reverse=True)

        # Tempos médios de resposta por tipo de atividade
        avg_response_times = {}
        for act_type, t_list in times_by_type.items():
            if t_list:
                avg_response_times[act_type] = round(sum(t_list) / len(t_list), 1)

        return {
            "total_events": total_events,
            "hardest_questions": hardest_questions,
            "drop_off_units": drop_off_units,
            "critical_vocab": critical_vocab,
            "avg_response_times": avg_response_times,
            "session_summary": {
                "total_quizzes_completed": total_quizzes_completed,
                "total_reviews_completed": total_reviews_completed,
            },
        }


class AdminService:
    """Serviço de Gestão Administrativa e Consolidação Pedagógica Multi-Student.
    
    Responsável por autenticação de professores/administradores, varredura de
    todas as sessões de alunos em disco (data/sessions/), compilação de KPIs globais
    e geração de relatórios pedagógicos executivos.
    """

    DEFAULT_PIN: str = "sejong2026"

    @classmethod
    def authenticate(cls, pin: str) -> bool:
        """Verifica se o PIN fornecido corresponde ao PIN configurado ou ao padrão."""
        if not pin:
            return False
        expected = os.environ.get("SEJONG_ADMIN_PIN", cls.DEFAULT_PIN).strip()
        return pin.strip() == expected

    @classmethod
    def _get_sessions_dir(cls, custom_dir: Optional[str] = None) -> str:
        """Retorna o diretório de sessões dos alunos."""
        if custom_dir:
            return custom_dir
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "data", "sessions")

    @classmethod
    def get_all_students_summary(cls, sessions_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lê e resume todas as sessões de estudantes cadastradas no disco."""
        directory = cls._get_sessions_dir(sessions_dir)
        if not os.path.exists(directory):
            return []

        students: List[Dict[str, Any]] = []
        curriculum = DataService.get_curriculum()
        total_units_count = len(curriculum) if curriculum else 23

        # Listar todos os arquivos .json na pasta de sessões
        for filename in os.listdir(directory):
            if not filename.endswith(".json"):
                continue

            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Erro ao ler sessão {filename}: {e}")
                continue

            if not isinstance(data, dict):
                continue

            # Extrair student_id
            s_id = data.get("student_id")
            if not s_id:
                # Extrair do nome do arquivo: student_{id}.json ou {uuid}.json
                if filename.startswith("student_") and filename.endswith(".json"):
                    s_id = filename[8:-5]
                else:
                    s_id = filename[:-5]

            s_name = data.get("student_name") or "Aluno Anônimo"
            streak = data.get("streak", 0)
            total_xp = data.get("total_xp", 0)
            last_date = data.get("last_study_date") or data.get("updated_at") or "—"
            created_at = data.get("created_at") or "—"

            # Calcular progresso e conclusões
            completed_1a = 0
            completed_1b = 0
            total_completed = 0
            progress_sum = 0.0

            for unit in curriculum:
                u_prog = data.get(f"progress_{unit.id}", 0.0)
                progress_sum += u_prog
                if u_prog >= 1.0:
                    total_completed += 1
                    if unit.id.startswith("unit_1b_"):
                        completed_1b += 1
                    else:
                        completed_1a += 1

            avg_progress_pct = (progress_sum / total_units_count) if total_units_count > 0 else 0.0

            # Calcular saúde de memória (SRS)
            nodes_to_eval = []
            if isinstance(data.get("memory_nodes"), dict):
                for k, v in data["memory_nodes"].items():
                    if isinstance(v, dict):
                        nodes_to_eval.append((k, v))

            for k, v in data.items():
                if (k.startswith("memory_") or k.startswith("memory_item_")) and isinstance(v, dict) and k != "memory_nodes":
                    nodes_to_eval.append((k, v))

            nodes_count = len(nodes_to_eval)
            retention_sum = 0.0

            now = datetime.now()
            for key, node_raw in nodes_to_eval:
                try:
                    h_life = float(node_raw.get("half_life", node_raw.get("half_life_days", 5.0)))
                    l_rev = str(node_raw.get("last_reviewed", node_raw.get("last_reviewed_at", "")))
                    node = MemoryNode(unit_id=key, half_life=h_life, last_reviewed=l_rev)
                    retention = node.calculate_stability(now)
                    retention_sum += retention
                except Exception:
                    retention_sum += 0.5

            avg_retention_pct = (retention_sum / nodes_count) if nodes_count > 0 else 0.0

            students.append({
                "student_id": s_id,
                "student_name": s_name,
                "streak": streak,
                "total_xp": total_xp,
                "last_study_date": last_date,
                "created_at": created_at,
                "completed_1a_count": completed_1a,
                "completed_1b_count": completed_1b,
                "completed_total_count": total_completed,
                "total_units_count": total_units_count,
                "overall_progress_pct": round(avg_progress_pct, 4),
                "memory_nodes_count": nodes_count,
                "avg_retention_pct": round(avg_retention_pct, 4),
            })

        # Ordenar: alunos com atividade mais recente primeiro
        students.sort(key=lambda s: (s["last_study_date"], s["overall_progress_pct"]), reverse=True)
        return students

    @classmethod
    def get_global_kpis(cls, sessions_dir: Optional[str] = None) -> Dict[str, Any]:
        """Calcula os indicadores-chave de desempenho (KPIs) de toda a base de alunos."""
        students = cls.get_all_students_summary(sessions_dir)
        total_students = len(students)

        total_progress = sum(s["overall_progress_pct"] for s in students) if total_students > 0 else 0.0
        avg_progress = (total_progress / total_students) if total_students > 0 else 0.0

        students_with_memory = [s for s in students if s["memory_nodes_count"] > 0]
        total_retention = sum(s["avg_retention_pct"] for s in students_with_memory)
        avg_retention = (total_retention / len(students_with_memory)) if students_with_memory else 0.0
        total_nodes = sum(s["memory_nodes_count"] for s in students)

        telemetry_events = TelemetryService.get_events()
        telemetry_analysis = PedagogicalAnalyzer.analyze(telemetry_events)

        return {
            "total_students": total_students,
            "avg_progress_pct": round(avg_progress, 4),
            "avg_retention_pct": round(avg_retention, 4),
            "total_memory_nodes": total_nodes,
            "total_telemetry_events": len(telemetry_events),
            "total_quizzes_completed": telemetry_analysis["session_summary"]["total_quizzes_completed"],
            "total_reviews_completed": telemetry_analysis["session_summary"]["total_reviews_completed"],
        }

    @classmethod
    def get_pedagogical_diagnostics(cls) -> Dict[str, Any]:
        """Retorna a análise diagnóstica consolidada de telemetria pedagógica."""
        events = TelemetryService.get_events()
        return PedagogicalAnalyzer.analyze(events)

    @classmethod
    def export_report_markdown(cls, sessions_dir: Optional[str] = None) -> str:
        """Gera um relatório executivo pedagógico completo formatado em Markdown."""
        kpis = cls.get_global_kpis(sessions_dir)
        diagnostics = cls.get_pedagogical_diagnostics()
        students = cls.get_all_students_summary(sessions_dir)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "# 🏛️ Relatório Executivo & Diagnóstico Pedagógico — Sejong Companion",
            f"*Gerado em: {now_str} | Corpo Docente CCCB / Sejong Hakdang*",
            "",
            "---",
            "",
            "## 📈 1. Indicadores Globais de Aprendizagem (KPIs)",
            "",
            f"- **👥 Total de Alunos Cadastrados:** {kpis['total_students']}",
            f"- **📊 Progresso Médio Curricular:** {kpis['avg_progress_pct']:.1%}",
            f"- **🧠 Retenção Média de Vocabulário (SRS):** {kpis['avg_retention_pct']:.1%}",
            f"- **🃏 Nós de Memória Ativos na Turma:** {kpis['total_memory_nodes']}",
            f"- **📝 Quizzes Avaliativos Concluídos:** {kpis['total_quizzes_completed']}",
            f"- **🔄 Sessões de Revisão Diária:** {kpis['total_reviews_completed']}",
            "",
            "---",
            "",
            "## ⚠️ 2. Questões Críticas com Maior Taxa de Erro (Top 5)",
            "",
        ]

        hardest = diagnostics.get("hardest_questions", [])[:5]
        if hardest:
            lines.extend([
                "| ID da Questão | Unidade | Tentativas | Erros | Taxa de Erro | Tempo Médio |",
                "| :--- | :--- | :---: | :---: | :---: | :---: |",
            ])
            for q in hardest:
                lines.append(
                    f"| `{q['question_id']}` | `{q['unit_id']}` | {q['total_attempts']} | "
                    f"{q['errors']} | **{q['error_rate']:.1%}** | {q['avg_response_time_ms']}ms |"
                )
        else:
            lines.append("*Nenhum dado de questão avaliativa registrado ainda.*")

        lines.extend([
            "",
            "---",
            "",
            "## 📉 3. Funil de Abandono por Unidade (Opened vs Completed)",
            "",
        ])

        drop_offs = diagnostics.get("drop_off_units", [])
        if drop_offs:
            lines.extend([
                "| Unidade | Aberturas | Conclusões | Taxa de Abandono |",
                "| :--- | :---: | :---: | :---: |",
            ])
            for u in drop_offs:
                lines.append(
                    f"| `{u['unit_id']}` | {u['opened_count']} | {u['completed_count']} | **{u['drop_off_rate']:.1%}** |"
                )
        else:
            lines.append("*Nenhum dado de abandono registrado ainda.*")

        lines.extend([
            "",
            "---",
            "",
            "## 🔄 4. Vocabulário Crítico com Reincidência de 'Again' (Top 5)",
            "",
        ])

        critical = diagnostics.get("critical_vocab", [])[:5]
        if critical:
            lines.extend([
                "| Item | Unidade | Again (Errei) | Hard | Good | Easy | Taxa de Again |",
                "| :--- | :--- | :---: | :---: | :---: | :---: | :---: |",
            ])
            for c in critical:
                lines.append(
                    f"| `{c['item_id']}` | `{c['unit_id']}` | **{c['again_count']}** | "
                    f"{c['hard_count']} | {c['good_count']} | {c['easy_count']} | {c['again_rate']:.1%} |"
                )
        else:
            lines.append("*Nenhum dado de avaliação de flashcard registrado ainda.*")

        lines.extend([
            "",
            "---",
            "",
            "## 🎓 5. Roster de Alunos Cadastrados",
            "",
        ])

        if students:
            lines.extend([
                "| Student ID | Nome / Aluno | 1A Concluídas | 1B Concluídas | Progresso Geral | Retenção SRS | Streak | XP | Último Acesso |",
                "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
            ])
            for s in students:
                lines.append(
                    f"| `{s['student_id']}` | **{s['student_name']}** | {s['completed_1a_count']}/11 | "
                    f"{s['completed_1b_count']}/12 | {s['overall_progress_pct']:.1%} | {s['avg_retention_pct']:.1%} | "
                    f"{s['streak']}🔥 | {s['total_xp']} | {s['last_study_date']} |"
                )
        else:
            lines.append("*Nenhum perfil de aluno localizado em data/sessions/.*")

        return "\n".join(lines)

