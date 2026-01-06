from typing import List, Dict, Any, Tuple
from collections import Counter
import re

class TopicExtractor:
    """
    Extracts main topics from a collection of messages.
    """
    
    def extract_topics(self, messages: List[str], top_n: int = 5) -> List[Tuple[str, int]]:
        """
        Extracts the most frequent significant keywords as topics.
        """
        all_words = []
        stop_words = {
            "the", "and", "for", "with", "this", "that", "from", "was", "were",
            "been", "have", "has", "had", "will", "would", "should", "could"
        }
        
        for msg in messages:
            # Tokenize and filter
            words = re.findall(r"\b[a-zA-Z]{4,}\b", msg.lower())
            filtered = [w for w in words if w not in stop_words]
            all_words.extend(filtered)
            
        counter = Counter(all_words)
        return counter.most_common(top_n)

    def group_by_topic(self, commits_with_messages: List[Tuple[Any, str]]) -> Dict[str, List[Any]]:
        """
        Groups commit objects by their primary keyword topic.
        """
        # Very simple: check if message contains any of the top keywords
        all_msgs = [m for _, m in commits_with_messages]
        top_topics = [topic for topic, count in self.extract_topics(all_msgs)]
        
        groups = {topic: [] for topic in top_topics}
        groups["other"] = []
        
        for commit, msg in commits_with_messages:
            found = False
            for topic in top_topics:
                if topic in msg.lower():
                    groups[topic].append(commit)
                    found = True
                    break
            if not found:
                groups["other"].append(commit)
                
        return groups
