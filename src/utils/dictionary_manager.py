import os
import pandas as pd
from src.utils.dir_utils import list_files_by_extension, ensure_directory_exists
from src.config.paths import DICTIONARIES_DIR


class DictionaryManager:

    def __init__(self, source_lang: str = None, target_lang: str = None):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.sorted_langs = sorted([source_lang, target_lang])
        self.loaded_dictionary = pd.DataFrame(columns=[self.sorted_langs[0], self.sorted_langs[1]])
        self.dictionary_folder = DICTIONARIES_DIR / f'{self.sorted_langs[0]}_{self.sorted_langs[1]}'


    def load_dictionaries(self) -> None:

        if not os.path.exists(self.dictionary_folder):
            return

        dictionaries = list_files_by_extension(self.dictionary_folder, 'csv')
        for dictionary in dictionaries:
            temp_dict = pd.read_csv(dictionary, sep=',')
            self.loaded_dictionary = pd.concat([self.loaded_dictionary, temp_dict], ignore_index=True)

        self.loaded_dictionaries = dict(zip(
            self.loaded_dictionary[self.source_lang],
            self.loaded_dictionary[self.target_lang]
        ))


    def save_dictionary(self, df_translated: pd.DataFrame, dictionary_name) -> None:
        ensure_directory_exists(self.dictionary_folder)

        dictionary_path = self.dictionary_folder / f'{dictionary_name}.csv'
        df_translated.to_csv(dictionary_path, index=False)


    def append_to_dictionary(self, df: pd.DataFrame, dictionary_name) -> None:
        dictionary_path = self.dictionary_folder / f'{dictionary_name}.csv'

        if dictionary_path.exists():
            existing_df = pd.read_csv(dictionary_path, sep=',')
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.drop_duplicates(subset=[self.sorted_langs[0]], keep='last', inplace=True)
            combined_df.to_csv(dictionary_path, index=False)
        else:
            self.save_dictionary(df, dictionary_name)