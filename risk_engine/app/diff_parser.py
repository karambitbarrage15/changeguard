"""
Git unified diff parser and file categorization engine.
"""
import re
from typing import List, Dict, Any

class DiffParser:
    FILE_CATEGORIES = {
        "database": [r"\.sql$", r"migrations?\/", r"schema\.", r"models?\.py$"],
        "infra": [r"Dockerfile", r"docker-compose", r"\.tf$", r"\.yaml$", r"\.yml$", r"k8s\/", r"helm\/"],
        "security": [r"auth", r"jwt", r"permission", r"secret", r"token", r"crypt"],
        "core_telemetry": [r"telemetry", r"ingest", r"pipeline", r"stream", r"kafka", r"mqtt"],
        "dependencies": [r"requirements\.txt$", r"package\.json$", r"go\.mod$", r"Cargo\.toml$"],
        "docs": [r"\.md$", r"\.rst$", r"docs?\/", r"LICENSE"]
    }

    @classmethod
    def parse(cls, diff_text: str) -> Dict[str, Any]:
        lines = diff_text.strip().splitlines()
        files: List[Dict[str, Any]] = []
        current_file: Dict[str, Any] = None
        total_added = 0
        total_deleted = 0

        for line in lines:
            if line.startswith("diff --git"):
                if current_file:
                    files.append(current_file)
                match = re.search(r"b\/(.*)$", line)
                filename = match.group(1) if match else "unknown"
                current_file = {
                    "filename": filename,
                    "category": cls._categorize_file(filename),
                    "added_lines": 0,
                    "deleted_lines": 0,
                    "hunks": []
                }
            elif line.startswith("+++ b/"):
                if current_file:
                    current_file["filename"] = line.replace("+++ b/", "")
                    current_file["category"] = cls._categorize_file(current_file["filename"])
            elif line.startswith("@@"):
                if current_file:
                    current_file["hunks"].append(line)
            elif line.startswith("+") and not line.startswith("+++"):
                if current_file:
                    current_file["added_lines"] += 1
                total_added += 1
            elif line.startswith("-") and not line.startswith("---"):
                if current_file:
                    current_file["deleted_lines"] += 1
                total_deleted += 1

        if current_file:
            files.append(current_file)

        # Fallback if raw patch didn't have git headers
        if not files and diff_text.strip():
            files.append({
                "filename": "patch.diff",
                "category": "core_telemetry",
                "added_lines": sum(1 for l in lines if l.startswith("+") and not l.startswith("+++")),
                "deleted_lines": sum(1 for l in lines if l.startswith("-") and not l.startswith("---")),
                "hunks": [l for l in lines if l.startswith("@@")]
            })

        categories_found = list({f["category"] for f in files})

        return {
            "total_files": len(files),
            "total_added": total_added,
            "total_deleted": total_deleted,
            "categories": categories_found,
            "files": files
        }

    @classmethod
    def _categorize_file(cls, filename: str) -> str:
        for category, patterns in cls.FILE_CATEGORIES.items():
            for pattern in patterns:
                if re.search(pattern, filename, re.IGNORECASE):
                    return category
        return "application_logic"
