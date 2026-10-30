"""
Markdown Post-Mortem parser and RAG retriever.
"""
import os
import glob
import re
from typing import List, Dict, Any
from .embeddings import DocumentIndex

class RAGRetriever:
    def __init__(self, knowledge_base_dir: str):
        self.kb_dir = knowledge_base_dir
        self.index = DocumentIndex()
        self.load_documents()

    def load_documents(self):
        docs = []
        md_files = glob.glob(os.path.join(self.kb_dir, "*.md"))
        for fpath in md_files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = title_match.group(1) if title_match else os.path.basename(fpath)

                severity_match = re.search(r"\*\*Severity:\*\*\s*(.+)$", content, re.MULTILINE)
                severity = severity_match.group(1).strip() if severity_match else "P2"

                symptoms_match = re.search(r"\*\*Symptoms:\*\*\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
                symptoms = symptoms_match.group(1).strip() if symptoms_match else ""

                root_cause_match = re.search(r"##\s+Root Cause\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
                root_cause = root_cause_match.group(1).strip() if root_cause_match else ""

                remediation_match = re.search(r"##\s+Remediation.*?\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
                remediation = remediation_match.group(1).strip() if remediation_match else ""

                docs.append({
                    "id": os.path.basename(fpath),
                    "title": title,
                    "severity": severity,
                    "symptoms": symptoms,
                    "root_cause": root_cause,
                    "remediation": remediation,
                    "content": content
                })
            except Exception as e:
                print(f"Error loading {fpath}: {e}")

        self.index.build_index(docs)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        return self.index.search(query, top_k=top_k)

    def get_all(self) -> List[Dict[str, Any]]:
        return self.index.documents
