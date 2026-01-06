from typing import Optional

class LinkGenerator:
    """
    Generates web links for repository artifacts based on remote URL.
    Supports GitHub and GitLab style URLs.
    """
    
    def __init__(self, remote_url: Optional[str]):
        self.remote_url = remote_url
        self.base_url = self._parse_base_url(remote_url)
        
    def _parse_base_url(self, remote_url: Optional[str]) -> Optional[str]:
        if not remote_url:
            return None
            
        # Handle SSH style: git@github.com:user/repo.git
        if remote_url.startswith("git@"):
            url = remote_url.replace(":", "/").replace("git@", "https://")
        else:
            url = remote_url
            
        # Remove .git suffix
        if url.endswith(".git"):
            url = url[:-4]
            
        return url

    def generate_commit_link(self, commit_hash: str) -> Optional[str]:
        """
        Generate link to a specific commit.
        """
        if not self.base_url:
            return None
            
        # GitHub/GitLab implementation
        return f"{self.base_url}/commit/{commit_hash}"
        
    def generate_file_link(self, filepath: str, commit_hash: str = "master") -> Optional[str]:
        """
        Generate link to a file at a specific commit/branch.
        """
        if not self.base_url:
            return None
            
        # GitHub/GitLab use 'blob' for files
        return f"{self.base_url}/blob/{commit_hash}/{filepath}"
