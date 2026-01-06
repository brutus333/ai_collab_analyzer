from typing import List, Dict, Any

class SentimentAnalyzer:
    """
    Performs rule-based sentiment analysis on text.
    """
    
    POSITIVE_WORDS = {
        "great", "good", "excellent", "awesome", "better", "improved", 
        "stable", "success", "resolved", "fixed", "working", "perfect",
        "clean", "easy", "thanks", "wow", "nice", "properly"
    }
    
    NEGATIVE_WORDS = {
        "bad", "wrong", "broken", "error", "fail", "failed", "frustrating",
        "stupid", "dumb", "worse", "slow", "heavy", "complex", "mess",
        "hard", "difficult", "confusing", "why", "broken", "garbage"
    }

    def analyze_sentiment(self, text: str) -> float:
        """
        Calculates a sentiment score from -1.0 (negative) to 1.0 (positive).
        """
        if not text:
            return 0.0
            
        words = text.lower().split()
        pos_count = sum(1 for w in words if w in self.POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in self.NEGATIVE_WORDS)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
            
        return (pos_count - neg_count) / total

    def track_sentiment_trend(self, messages: List[str]) -> List[float]:
        """
        Returns a timeline of sentiment scores.
        """
        return [self.analyze_sentiment(m) for m in messages]
