import pandas as pd
from rapidfuzz import process, fuzz
from typing import List, Dict
from src.config.paths import DICTIONARIES_DIR
from src.database.repositories import EnPtbrRepository
import gc


class TranslationSimilaritySearch:
    
    def __init__(self, source_language: str, target_language: str):

        self.dictionaries_folder = DICTIONARIES_DIR / f'{source_language}_{target_language}'
        self.source_col = source_language
        self.target_col = target_language
    
    
    def _create_temp_df(self) -> None:
        self.df = pd.DataFrame(EnPtbrRepository.get_all())
        self.df.drop_duplicates(inplace=True, keep='last')


    def find_similar(self, query: str, limit: int = 5) -> List[Dict]:
        matches = process.extract(
            query,
            self.source_texts,
            scorer=fuzz.token_sort_ratio,
            limit=limit
        )

        results = []
        for text, score, idx in matches:
            target_text = self.df.iloc[idx][self.target_col]
            results.append({
                'source': text,
                'target': target_text,
                'score': score
            })

        return results
    

    def get_context_string(self, query: str, limit: int = 5) -> str:
        self._create_temp_df()
        self.source_texts = self.df[self.source_col].tolist()

        similar_texts = self.find_similar(query, limit)

        context = 'Exemplos de traduções semelhantes:\n\n'
        for i, item in enumerate(similar_texts, 1):
            context += f'{i}. {self.source_col}: {item['source']}\n'
            context += f'   {self.target_col}: {item['target']}\n\n'

        del self.df
        del self.source_texts
        gc.collect()

        return context