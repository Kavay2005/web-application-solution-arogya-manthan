# -*- coding: utf-8 -*-
"""
Knowledge Base Loader
Loads and manages disease information from CSV files.
"""

import os
import pandas as pd
from typing import Dict, List, Any


class KnowledgeLoader:
    """Load and manage disease knowledge base"""
    
    def __init__(self, kb_path: str = None):
        self.kb_path = kb_path
        self.kb_dict = {}
        self.load()
    
    def load(self):
        """Load knowledge base from CSV"""
        if not self.kb_path or not os.path.exists(self.kb_path):
            return
        
        try:
            kb_df = pd.read_csv(self.kb_path)
            self.kb_dict = {}
            if 'Disease' in kb_df.columns:
                for _, row in kb_df.iterrows():
                    disease = str(row['Disease']).strip()
                    self.kb_dict[disease] = row.to_dict()
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
    
    def get_disease_info(self, disease: str) -> Dict[str, Any]:
        """Get information about a specific disease"""
        return self.kb_dict.get(disease, {})
    
    def get_all_diseases(self) -> List[str]:
        """Get list of all diseases in knowledge base"""
        return list(self.kb_dict.keys())
