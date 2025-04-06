from src.services.chatgpt_service import ChatGPTService
from src.prompts.prompt_model import Prompter
from src.database.repositories import EnPtbrRepository
from src.config.paths import MODS_DIR, UNPACKED_MODS
from src.utils.dictionary_manager import DictionaryManager
from src.utils.language_codes import LANGUAGES
from src.utils.xml_utils import XmlUtils
from src.utils.lsx_utils import LsxUtils
from src.utils.dir_utils import ensure_directory_exists
from src.utils.bg_dir_utils import BgModPaths

from time import sleep
from uuid import uuid4
from pathlib import Path
import pandas as pd


class BaldurGate3ModTranslator:

    def __init__(self, target_mod_name: str, mod_folder_name, source_lang: str, target_lang: str, metadata: dict):
        self.prompter = Prompter(source_lang, target_lang)
        self.dict_manager = DictionaryManager(source_lang, target_lang)
        self.gpt_service = ChatGPTService()
        self.xml_utils = XmlUtils()
        self.lsx_utils = LsxUtils()
        self.bg_mod_paths = BgModPaths(mod_folder_name, source_lang, target_lang)

        self.metadata = metadata
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.mod_name = target_mod_name + '_' + target_lang
        self.mod_folder_name = mod_folder_name + '_' + target_lang

        self.gpt_requests = 0
        

    def load_xml(self, xml_path: Path) -> None:
        source_df = self.xml_utils.xml_to_dataframe(xml_path)
        return source_df


    def create_meta_lsx(self, lsx_path: Path, lsx_output_path: Path) -> None:
        uuid = str(uuid4())

        self.lsx_utils.update_mod_info(
            lsx_path=lsx_path,
            output_path=lsx_output_path,
            author=self.metadata.get('author'),
            description=self.metadata.get('description'),
            uuid=uuid,
            target_lang=self.target_lang
        )
    

    def translate(self) -> None:
        for source_value in self.source_values:
            self.counter += 1
            
            dictionary = EnPtbrRepository.find_by_en(source_value)
            
            if dictionary is not None:
                target_value = dictionary.get('ptbr')
                self.translations['en'].append(source_value)
                self.translations['ptbr'].append(target_value)
                print(f'[{self.counter}/{self.total_rows}] - {source_value} -> {target_value}')
                continue
            
            if self.gpt_requests % 50 == 0 and self.gpt_requests > 0:
                print('Esperando 5 segundos para evitar excesso de requests...')
                sleep(5)

            prompt = self.prompter.get_prompt(source_value)
            target_value = self.gpt_service.gpt_chat_completion(source_value, prompt)
            self.translations['en'].append(source_value)
            self.translations['ptbr'].append(target_value)
            EnPtbrRepository.add_one(source_value, target_value, self.mod_name)
            self.gpt_requests += 1
            print(f'[{self.counter}/{self.total_rows}] GPT 4-o-mini traduziu - {source_value} -> {target_value}')

        if self.total_rows != len(self.translations['ptbr']):
            raise Exception('Erro ao traduzir! Número de linhas origem e destino diferente!')

        self.translated_df = self.source_df.copy()
        self.translated_df['text'] = self.translations[self.target_lang]

    
    def mod_translate(self) -> None:
        
        for xml, paths in self.bg_mod_paths.xml_paths.items():
            print('XML Path:', paths[0])
            source_df = self.load_xml(paths[0])
            source_values = source_df['text'].tolist()

            counter = 0
            total_rows = len(source_values)
            translations = {self.source_lang: [], self.target_lang: []}

            for source_value in source_values:
                counter += 1

                dictionary = EnPtbrRepository.find_by_en(source_value)

                if dictionary is not None:
                    target_value = dictionary.get('ptbr')
                    translations['en'].append(source_value)
                    translations['ptbr'].append(target_value)
                    print(f'[{xml} {counter}/{total_rows}] - {source_value} -> {target_value}')
                    continue

                if self.gpt_requests % 50 == 0 and self.gpt_requests > 0:
                    print('Esperando 5 segundos para evitar excesso de requests...')
                    sleep(5)

                prompt = self.prompter.get_prompt(source_value)
                target_value = self.gpt_service.gpt_chat_completion(source_value, prompt)
                translations['en'].append(source_value)
                translations['ptbr'].append(target_value)
                EnPtbrRepository.add_one(source_value, target_value, self.mod_name)
                self.gpt_requests += 1
                print(f'[{xml} {counter}/{total_rows}] GPT 4-o-mini traduziu - {source_value} -> {target_value}')

            if total_rows != len(translations['ptbr']):
                raise Exception('Erro ao traduzir! Número de linhas origem e destino diferente!')

            translated_df = source_df.copy()
            translated_df['text'] = translations[self.target_lang]

            self.xml_utils.dataframe_to_xml(translated_df, paths[1])
        
        self.create_meta_lsx(self.bg_mod_paths.lsx_paths[0], self.bg_mod_paths.lsx_paths[1])
