"""
MCP Tool: Git repository inspection (log, blame, diff).
"""
import subprocess
import os
from typing import Dict, Any, List, Optional

WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

def git_log(limit: int = 5, path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve recent git commit history with hashes, authors, messages, and timestamps."""
    cmd = ["git", "log", f"-n{limit}", "--pretty=format:%H|%an|%ae|%at|%s"]
    if path:
        cmd.extend(["--", path])
    try:
        res = subprocess.run(cmd, cwd=WORKSPACE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        commits = []
        for line in res.stdout.strip().splitlines():
            if not line:
                continue
            parts = line.split("|", 4)
            if len(parts) == 5:
                commits.append({
                    "commit_hash": parts[0],
                    "author_name": parts[1],
                    "author_email": parts[2],
                    "timestamp": int(parts[3]),
                    "message": parts[4]
                })
        return commits
    except Exception as e:
        return [{"error": f"Failed to read git log: {str(e)}"}]

def git_diff_commit(commit_hash: str = "HEAD") -> Dict[str, Any]:
    """Retrieve full diff introduced by a commit or HEAD."""
    try:
        res = subprocess.run(["git", "show", "--stat", "--patch", commit_hash], cwd=WORKSPACE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        return {"commit": commit_hash, "diff": res.stdout[:5000]}
    except Exception as e:
        return {"error": f"Failed to retrieve diff for {commit_hash}: {str(e)}"}

def git_blame(file_path: str, start_line: int = 1, end_line: int = 30) -> List[Dict[str, Any]]:
    """Examine git blame for a specific file range."""
    try:
        cmd = ["git", "blame", "-L", f"{start_line},{end_line}", "--porcelain", file_path]
        res = subprocess.run(cmd, cwd=WORKSPACE_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        return [{"file": file_path, "blame_output": res.stdout[:2000]}]
    except Exception as e:
        return [{"error": f"Blame failed on {file_path}: {str(e)}"}]
