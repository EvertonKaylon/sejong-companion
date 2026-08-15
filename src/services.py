import json
import os
from typing import List, Optional
from datetime import datetime, date
import flet as ft
from .models import FlashcardItem, Unit, UnitIntroData, UnitOneData, UnitData, MemoryNode

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
    def _flashcard_difficulty(unit_number: int, word: str, category: str) -> str:
        """Classifica o material sem exigir uma segunda cópia dos JSONs.

        Itens básicos permanecem fáceis mesmo quando reaparecem em unidades
        posteriores. Estruturas gramaticais avançadas e o conteúdo das últimas
        unidades entram na trilha difícil.
        """
        normalized = f"{word} {category}".lower()
        easy_terms = ("cumpr", "pronom", "numero", "수", "인사", "나라")
        hard_markers = ("았", "었", "겠", "싶", "까요", "불규칙", "ㅂ", "classificador", "단위")
        if any(term in normalized for term in easy_terms) or unit_number <= 2:
            return "easy"
        if any(marker in normalized for marker in hard_markers) or unit_number >= 6:
            return "hard"
        return "medium"

    @staticmethod
    def get_all_flashcards(difficulty: Optional[str] = None) -> List[FlashcardItem]:
        """Compila o vocabulário das unidades 01–10 em cartões consistentes."""
        cards: List[FlashcardItem] = []
        for number in range(1, 11):
            unit_id = f"unit_{number:02d}"
            unit = DataService.get_unit(unit_id)
            if not unit:
                continue
            for index, vocab in enumerate(unit.vocabulary):
                level = DataService._flashcard_difficulty(number, vocab.word, vocab.category or "")
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
        for number in range(1, 11):
            unit_id = f"unit_{number:02d}"
            unit = DataService.get_unit(unit_id)
            if not unit:
                continue
            for exercise in unit.exercises:
                if exercise.type != "drag_and_drop_sov" or not exercise.correct_order:
                    continue
                category = "sintaxe"
                level = DataService._flashcard_difficulty(number, " ".join(exercise.correct_order), category)
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
        """Extrai e desduplica TODOS os textos com áudio do currículo completo (00 a 10)."""
        texts = list(DataService.get_priority_audio_texts())

        # 1. Sílabas do Hangul
        intro = DataService.get_unit_intro()
        if intro and intro.syllables:
            texts.extend([s.block for s in intro.syllables if s.block])

        # 2. Todas as Unidades 01 a 10 (Vocabulário e Frases de Exemplo)
        for number in range(1, 11):
            unit_id = f"unit_{number:02d}"
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
    """Gerenciador de progresso com persistência em disco e isolamento por sessão.
    
    Cada sessão Flet (aba do navegador / conexão) recebe um UUID único, garantindo
    que múltiplos usuários simultâneos em modo web não compartilhem progresso.
    Os dados são persistidos em data/sessions/{session_id}.json de forma atômica.
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
    }

    @staticmethod
    def _get_session_id(page) -> str:
        """Obtém ou gera um UUID único para a sessão desta page."""
        if page is None:
            return "__default__"
        if not hasattr(page, '_sejong_session_id'):
            import uuid
            page._sejong_session_id = uuid.uuid4().hex[:12]
        return page._sejong_session_id

    @classmethod
    def _get_storage_path(cls, session_id: str) -> str:
        if cls._file_path_override:
            return cls._file_path_override
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "data", "sessions", f"{session_id}.json")

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

    # ─── HLR / SRS (Half-Life Regression de Ebbinghaus) ───

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
        """Atualiza HLR com os multiplicadores explícitos da autoavaliação."""
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
