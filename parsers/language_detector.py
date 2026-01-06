import os
from typing import Optional

class LanguageDetector:
    """
    Detects programming language from file extension.
    """
    
    # Mapping of extension (with dot) to language name
    EXTENSION_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'react',
        '.ts': 'typescript',
        '.tsx': 'react-ts',
        '.html': 'html',
        '.css': 'css',
        '.go': 'go',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.md': 'markdown'
    }

    @classmethod
    def detect_language(cls, filepath: str) -> Optional[str]:
        """
        Detects the language of a file based on its extension.
        """
        _, ext = os.path.splitext(filepath)
        return cls.EXTENSION_MAP.get(ext.lower())

    @classmethod
    def is_supported(cls, filepath: str) -> bool:
        """
        Checks if the file's language is supported for analysis.
        """
        _, ext = os.path.splitext(filepath)
        return ext.lower() in cls.EXTENSION_MAP
