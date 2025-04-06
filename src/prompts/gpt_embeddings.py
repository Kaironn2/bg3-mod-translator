from pathlib import Path
import pandas as pd

from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from src.utils.dir_utils import ensure_directory_exists, list_files_by_extension
from src.config.paths import TEMP_DIR


class GPTEmbeddings:

    def __init__(self, csv_files_path: Path):
        self.csv_files_path = csv_files_path
        self.folder_name = csv_files_path.name
        self.temp_csv_path = TEMP_DIR / f'temp_{self.folder_name}.csv'
        self.csv_files = list_files_by_extension(csv_files_path, 'csv')

        self._create_temp_csv()
        self._load_temp_csv_file()
        self._create_faiss_index()


    def _create_temp_csv(self):
        print('Criando csv temporário com todos os arquivos...')
        self.temp_df = pd.DataFrame()
        for file in self.csv_files:
            self.temp_df = pd.concat([self.temp_df, pd.read_csv(file, encoding='utf-8')])
        
        ensure_directory_exists(TEMP_DIR)
        self.temp_df.to_csv(self.temp_csv_path, index=False, encoding='utf-8')


    def _load_temp_csv_file(self) -> list:
        print('Carregando documentos do csv temporário...')
        loader = CSVLoader(self.temp_csv_path, encoding='utf-8')
        self.documents = loader.load()
    

    def _create_faiss_index(self):
        print('Criando índice FAISS com embeddings OpenAI...')
        embeddings = OpenAIEmbeddings()
        self.db = FAISS.from_documents(self.documents, embeddings)

    
    def retrieve_info(self, query: str):
        similar_response = self.db.similarity_search(query, k=10)
        unique_responses = set([doc.page_content for doc in similar_response])
        return unique_responses