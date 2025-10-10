"""
核心 Embedding 比對系統
純粹的 embedding 相似度匹配，無複雜邏輯
"""

from .embedding_matcher import EmbeddingMatcher, MatchResult

__all__ = ['EmbeddingMatcher', 'MatchResult']

