"""Mapping service implementing automatic matching algorithms."""
from __future__ import annotations

from dataclasses import dataclass
import re
from difflib import SequenceMatcher
from typing import Iterable, Tuple
from loguru import logger


@dataclass(slots=True)
class MappingResult:
    account_id: int | None
    dolphin_id: str | None
    dolphin_name: str | None
    confidence: float
    method: str


class MappingService:
    """Provides automatic matching between local accounts (display names) and external (Dolphin) accounts.

    Matching priority:
      1. Exact
      2. Ignore case
      3. Ignore spaces
      4. Replace "_" "-" "." with spaces
      5. Fuzzy matching (SequenceMatcher)

    Returns MappingResult with confidence in 0..1
    """

    @staticmethod
    def _normalize_variant_a(name: str) -> str:
        return name.strip()

    @staticmethod
    def _normalize_variant_b(name: str) -> str:
        return name.strip().lower()

    @staticmethod
    def _normalize_ignore_spaces(name: str) -> str:
        return re.sub(r"\s+", "", name).lower()

    @staticmethod
    def _normalize_replace_chars(name: str) -> str:
        return re.sub(r"[_\-\.]", " ", name).lower()

    def match(self, local_name: str, candidates: Iterable[Tuple[int, str, str]]) -> MappingResult:
        """Match local_name to candidates.

        candidates: iterable of (account_id, dolphin_id, dolphin_name)
        """
        if not local_name:
            return MappingResult(None, None, None, 0.0, "none")

        local_exact = self._normalize_variant_a(local_name)
        local_ci = self._normalize_variant_b(local_name)
        local_nospace = self._normalize_ignore_spaces(local_name)
        local_repl = self._normalize_replace_chars(local_name)

        best: MappingResult = MappingResult(None, None, None, 0.0, "none")

        for account_id, dolphin_id, dolphin_name in candidates:
            if not dolphin_name:
                continue
            # 1 Exact
            if dolphin_name == local_exact:
                logger.info("Mapping exact match: {local} -> {dolphin}", local=local_name, dolphin=dolphin_name)
                return MappingResult(account_id, dolphin_id, dolphin_name, 1.0, "exact")
            # 2 Ignore case
            if dolphin_name.lower() == local_ci and best.confidence < 0.95:
                logger.info("Mapping ignore-case: {local} -> {dolphin}", local=local_name, dolphin=dolphin_name)
                best = MappingResult(account_id, dolphin_id, dolphin_name, 0.95, "ignore_case")
            # 3 Ignore spaces
            if re.sub(r"\s+", "", dolphin_name).lower() == local_nospace and best.confidence < 0.9:
                logger.info("Mapping ignore-spaces: {local} -> {dolphin}", local=local_name, dolphin=dolphin_name)
                best = MappingResult(account_id, dolphin_id, dolphin_name, 0.9, "ignore_spaces")
            # 4 Replace chars
            if re.sub(r"[_\-\.]", " ", dolphin_name).lower() == local_repl and best.confidence < 0.85:
                logger.info("Mapping replace-chars: {local} -> {dolphin}", local=local_name, dolphin=dolphin_name)
                best = MappingResult(account_id, dolphin_id, dolphin_name, 0.85, "replace_chars")
            # 5 Fuzzy
            ratio = SequenceMatcher(None, dolphin_name.lower(), local_name.lower()).ratio()
            if ratio > best.confidence and ratio > 0.6:
                logger.info("Mapping fuzzy: {local} -> {dolphin} ratio={ratio:.2f}", local=local_name, dolphin=dolphin_name, ratio=ratio)
                best = MappingResult(account_id, dolphin_id, dolphin_name, ratio, "fuzzy")

        return best

    def batch_match(self, local_names: Iterable[Tuple[int, str]], candidates: Iterable[Tuple[int, str, str]]) -> list[MappingResult]:
        """Match multiple local names. local_names: iterable of (account_id, display_name)"""
        results: list[MappingResult] = []
        cand_list = list(candidates)
        for account_id, display_name in local_names:
            res = self.match(display_name, cand_list)
            results.append(res)
            logger.debug("Batch match result for {local}: {res}", local=display_name, res=res)
        return results
