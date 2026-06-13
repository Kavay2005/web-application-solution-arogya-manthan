# -*- coding: utf-8 -*-
"""
Precaution Loader
Loads disease precautions from CSV files.
"""

import os
import pandas as pd
from typing import Dict, List


class PrecautionLoader:
    """Load and manage disease precautions"""
    
    def __init__(self, precaution_path: str = None):
        self.precaution_path = precaution_path
        self.prec_dict = {}
        self.load()
    
    def load(self):
        """Load precautions from CSV"""
        if not self.precaution_path or not os.path.exists(self.precaution_path):
            return
        
        try:
            prec_df = pd.read_csv(self.precaution_path)
            self.prec_dict = {}
            if 'Disease' in prec_df.columns:
                cols = [c for c in prec_df.columns if c != 'Disease']
                for _, row in prec_df.iterrows():
                    disease = str(row['Disease']).strip()
                    precautions = [
                        str(row[c]).strip() for c in cols 
                        if pd.notna(row[c]) and str(row[c]).strip() != 'nan'
                    ]
                    self.prec_dict[disease] = precautions
        except Exception as e:
            print(f"Error loading precautions: {e}")
    
    def get_precautions(self, disease: str) -> List[str]:
        """Get precautions for a specific disease"""
        return self.prec_dict.get(disease, [])
    
    def get_all_diseases_with_precautions(self) -> List[str]:
        """Get list of all diseases with precautions"""
        return list(self.prec_dict.keys())
