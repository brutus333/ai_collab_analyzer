import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PromptArtifact:
    content: str
    filepath: Optional[str] = None
    line_number: Optional[int] = None
    source_type: str = "comment" # 'comment' or 'commit_message'

class PromptExtractor:
    """
    Extracts AI-related prompts from code comments and commit messages.
    """
    
    # Regex patterns to identify prompts
    # Matches: "AI:", "Prompt:", "LLM:", "ChatGPT:" followed by text
    PATTERN = re.compile(r'(?:AI|Prompt|LLM|ChatGPT|Copilot)\s*:\s*(.*)', re.IGNORECASE)

    def is_code_file(self, filepath: str) -> bool:
        """
        Check if a file's extension suggests it's a code/text file.
        Only scan these to avoid false positives in binary data.
        """
        if not filepath:
            return False
        
        code_extensions = (
            '.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp', '.cs',
            '.go', '.rs', '.php', '.rb', '.kt', '.swift', '.scala', '.sh',
            '.html', '.css', '.vue', '.svelte', '.sql', '.md', '.txt'
        )
        return filepath.lower().endswith(code_extensions)

    def extract_from_content(self, content: str, filepath: str) -> List[PromptArtifact]:
        """
        Scan file content for prompt markers in comments.
        Only scans files with recognized code extensions.
        """
        if not self.is_code_file(filepath):
            return []

        prompts = []
        lines = content.split('\n')
        is_doc = filepath.lower().endswith(('.md', '.txt'))
        
        for i, line in enumerate(lines):
            # For code files, we look for prompts in comments.
            # For documentation files (MD/TXT), we scan every line.
            if is_doc or '#' in line or '//' in line:
                match = self.PATTERN.search(line)
                if match:
                    prompt_text = match.group(1).strip()
                    prompts.append(PromptArtifact(
                        content=prompt_text,
                        filepath=filepath,
                        line_number=i + 1,
                        source_type="comment"
                    ))
        return prompts

    def extract_from_commit_message(self, message: str) -> Optional[PromptArtifact]:
        """
        Scan commit message for prompt markers.
        """
        match = self.PATTERN.search(message)
        if match:
            prompt_text = match.group(1).strip()
            return PromptArtifact(
                content=prompt_text,
                source_type="commit_message"
            )
        return None

    def detect_instructions(self, text: str) -> List[str]:
        """
        Identify lines that look like instructions or rules for an agent.
        Heuristics: Bullet points with imperative verbs, rules, or core requirements.
        """
        instructions = []
        lines = text.split('\n')
        
        # Keywords suggesting instructions/rules
        instr_keywords = [
            r"rule\s*:", r"instruction\s*:", r"always", r"never", 
            r"requirement\s*:", r"must", r"should not", r"don't", r"ensure"
        ]
        
        # Common imperative verbs at start of list items or sentences
        imperatives = [
            "Add", "Use", "Implement", "Refactor", "Fix", "Ensure", 
            "Create", "Remove", "Update", "Don't", "Always", "Avoid"
        ]
        
        for line in lines:
            original_line = line.strip()
            # Strip markdown list markers
            line = original_line.lstrip('-').lstrip('*').lstrip('1234567890.').strip()
            if len(line) < 10: continue # Skip very short lines
            
            # Rule 1: Starts with imperative (check first word)
            first_word = line.split(' ')[0].rstrip(',').rstrip(':')
            starts_with_imp = any(first_word.lower() == v.lower() for v in imperatives)
            
            # Rule 2: Contains instructional keywords
            has_keywords = any(re.search(kw, line, re.IGNORECASE) for kw in instr_keywords)
            
            if starts_with_imp or has_keywords:
                instructions.append(line)
                
        return instructions
