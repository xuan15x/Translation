"""
模糊匹配模块
"""
from typing import Any, Dict, List, Optional, Tuple
from thefuzz import fuzz


class FuzzyMatcher:
    """模糊匹配器"""

    @staticmethod
    def find_best_match(query: str, snapshot_items: List[Tuple[str, str]], threshold: int) -> Optional[Dict]:
        if not snapshot_items:
            return None
        best_match, highest_score = None, 0
        for hist_source, hist_trans in snapshot_items:
            score = fuzz.ratio(query, hist_source)
            if score > highest_score:
                highest_score = score
                best_match = {"original": hist_source, "translation": hist_trans, "score": score}
                if score == 100:
                    break
        return best_match if highest_score >= threshold else None
