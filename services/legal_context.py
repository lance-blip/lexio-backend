import os
from typing import Dict, List
from pathlib import Path

class LegalContextManager:
    def __init__(self):
        self.context_dir = Path("prompts/legal_knowledge")
        self.context_cache: Dict[str, str] = {}
        self._load_all_contexts()
    
    def _load_all_contexts(self):
        """Load all legal context files into memory"""
        if self.context_dir.exists():
            for file_path in self.context_dir.glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.context_cache[file_path.stem] = f.read()
    
    def get_relevant_context(self, query: str) -> str:
        """Simple keyword matching for relevant legal context"""
        query_lower = query.lower()
        
        keyword_rules = {
            'lra_key_sections': ['dismiss', 'fire', 'fired', 'employer', 'employee', 'work', 'job', 'ccma', 'labour', 'strike', 'retrench'],
            'bcea_key_sections': ['hours', 'leave', 'overtime', 'wage', 'salary', 'holiday', 'sick', 'maternity', 'minimum wage'],
            'cpa_key_sections': ['consumer', 'refund', 'warranty', 'product', 'shop', 'buy', 'return', 'defective'],
            'rental_housing_key_sections': ['landlord', 'tenant', 'rent', 'evict', 'lease', 'deposit', 'housing'],
            'criminal_procedure_key_sections': ['arrest', 'police', 'crime', 'bail', 'court', 'charge', 'criminal', 'rights when arrested'],
            'popia_key_sections': ['data', 'privacy', 'popia', 'information', 'personal', 'consent'],
            'domestic_violence_key_sections': ['violence', 'abuse', 'protection order', 'domestic', 'restraining'],
            'pie_act_key_sections': ['eviction', 'evict', 'illegal eviction', 'occupy', 'squatter'],
        }
        
        matched_files = set()
        for filename, keywords in keyword_rules.items():
            if any(keyword in query_lower for keyword in keywords):
                if filename in self.context_cache:
                    matched_files.add(filename)
        
        # Always include constitution as baseline
        if 'constitution_bill_of_rights' in self.context_cache:
            matched_files.add('constitution_bill_of_rights')
        
        contexts = []
        for filename in matched_files:
            if filename in self.context_cache:
                contexts.append(self.context_cache[filename])
        
        return "\n\n---\n\n".join(contexts) if contexts else "No specific legislation context available. Answer based on general South African legal principles."
    
    def get_all_context(self) -> str:
        """Get all legal context for scenario analysis"""
        return "\n\n---\n\n".join(self.context_cache.values())
