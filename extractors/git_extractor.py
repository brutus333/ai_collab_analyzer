from typing import List, Dict, Any, Optional
from pydriller import Repository as PyDrillerRepository
from ai_collab_analyzer.core.repository import Repository
from ai_collab_analyzer.core.commit import Commit

class GitExtractor:
    """
    Extracts data from a Git repository using PyDriller.
    """
    def __init__(self):
        from .prompt_extractor import PromptExtractor
        self.prompt_extractor = PromptExtractor()

    def extract_repository(self, path: str) -> Repository:
        """
        Extract data from a local git repository and return a Repository object.
        
        Args:
            path: Filesystem path to the repository
            
        Returns:
            Populated Repository object
        """
        repository = Repository(path)
        repository.remote_url = self._get_remote_url(path)
        
        commits = self.extract_commits(path)
        repository.add_commits(commits)
        
        return repository

    def _get_remote_url(self, path: str) -> Optional[str]:
        """
        Try to get the remote URL 'origin'.
        """
        import subprocess
        try:
            url = subprocess.check_output(
                ["git", "remote", "get-url", "origin"], 
                cwd=path, 
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
            return url
        except Exception:
            return None

    def _is_hard_excluded(self, filepath: str) -> bool:
        """
        Files that should NEVER be analyzed (binaries, metadata, dependencies, configs).
        We hard-exclude these to prevent noise in the repository structure.
        """
        if not filepath:
            return True
            
        filename = filepath.split('/')[-1].split('\\')[-1].lower()
            
        # 1. Infrastructure, Docker & Binary/Media
        binary_extensions = (
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.ico', '.svg',
            '.zip', '.tar', '.gz', '.7z', '.rar', '.xz',
            '.exe', '.dll', '.so', '.dylib', '.bin', '.obj', '.o',
            '.pyc', '.pyo', '.pyd', '.class', '.jar', '.war',
            '.wav', '.mp3', '.mp4', '.mov', '.avi', '.ttf', '.woff', '.woff2',
            '.pdf', '.docx', '.odt', '.rst', '.adoc'
        )
        if filename.endswith(binary_extensions) or filename.startswith('dockerfile') or filename in ['docker-compose.yml', 'docker-compose.yaml', 'vagrantfile']:
            return True
            
        # 2. Configuration, Data & Databases
        # Hard-exclude these as requested previously to avoid noise
        config_extensions = (
            '.json', '.yaml', '.yml', '.toml', '.lock', '.xml', '.csv', '.config', 
            '.ini', '.prop', '.properties', '.db', '.sqlite', '.sqlite3'
        )
        if filename.endswith(config_extensions):
            return True

        # 3. Git, IDE & Build Metadata
        metadata_names = {'.gitignore', '.gitattributes', '.editorconfig', '.eslintignore', '.prettierignore', 'makefile', 'license', 'copying', 'notice', 'authors'}
        if filename in metadata_names or '.vscode' in filepath or '.idea' in filepath or 'node_modules' in filepath or '__pycache__' in filepath:
            return True

        return False

    def _is_code(self, filepath: str) -> bool:
        """
        Identify files that count as "source code" for metrics.
        Documentation (.md, .txt) is scannable but NOT considered code for metrics.
        """
        filename = filepath.split('/')[-1].split('\\')[-1].lower()
        if filename.endswith(('.md', '.txt')):
            return False
        return True

    def extract_commits(self, repo_path: str) -> List[Commit]:
        """
        Extract commits from the repository.
        Includes documentation (.md, .txt) for scanning but only counts code files for metrics.
        """
        commits = []
        
        # Traverse commits using PyDriller
        for pd_commit in PyDrillerRepository(repo_path).traverse_commits():
            
            # Recalculate metrics based on filtered files
            relevant_files = []
            total_insertions = 0
            total_deletions = 0
            instructional_snippets = []
            
            for f in pd_commit.modified_files:
                path = f.new_path if f.new_path else f.old_path
                
                if path and not self._is_hard_excluded(path):
                    # We only allow MD and TXT to pass through as "metadata scannable"
                    relevant_files.append(path)
                    
                    # Detect instructions in added lines of documents
                    if not self._is_code(path) and f.diff_parsed:
                        added_text = "\n".join([line[1] for line in f.diff_parsed['added']])
                        snippets = self.prompt_extractor.detect_instructions(added_text)
                        if snippets:
                            instructional_snippets.extend(snippets)

                    # Only count code files for churn/lines metrics
                    if self._is_code(path):
                        total_insertions += f.added_lines
                        total_deletions += f.deleted_lines

            # Map PyDriller commit to our Commit model with recalculated stats
            commit_data = {
                "hash": pd_commit.hash,
                "author_name": pd_commit.author.name,
                "author_email": pd_commit.author.email,
                "author_date": pd_commit.author_date,
                "msg": pd_commit.msg,
                "merge": pd_commit.merge,
                "insertions": total_insertions,
                "deletions": total_deletions,
                "lines": total_insertions + total_deletions,
                "files": relevant_files,
                "instructional_changes": instructional_snippets
            }
            
            commits.append(Commit(commit_data))
            
        return commits

