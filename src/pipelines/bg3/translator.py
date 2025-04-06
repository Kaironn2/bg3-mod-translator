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

    def __init__(self, mod_name: str, mod_folder_name, source_lang: str, target_lang: str, xml_path: Path, lsx_path: Path, export_method: str, metadata: dict):
        self.prompter = Prompter(source_lang, target_lang)
        self.dict_manager = DictionaryManager(source_lang, target_lang)
        self.gpt_service = ChatGPTService()
        self.xml_utils = XmlUtils()
        self.lsx_utils = LsxUtils()
        self.bg_mod_paths = BgModPaths(mod_folder_name, source_lang)

        self.xml_path = xml_path
        self.lsx_path = lsx_path
        self.export_method = export_method
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.metadata = metadata
        self.mod_name = mod_name + '_' + target_lang
        self.mod_folder_name = mod_folder_name + '_' + target_lang

        self._load_xml()
        self._get_paths()

        self.counter = 0
        self.gpt_requests = 0
        self.total_rows = len(self.source_values)
        self.translations = {source_lang: [], target_lang: []}
        

    def _load_xml(self) -> None:
        self.source_df = self.xml_utils.xml_to_dataframe(self.xml_path)
        self.source_values = self.source_df['text'].tolist()


    def _get_paths_default(self) -> None:
        language_folder = LANGUAGES.get(self.target_lang)
        mod_folder = MODS_DIR / self.mod_folder_name

        self.xml_output_folder = mod_folder / 'Localization' / language_folder
        self.lsx_output_folder = mod_folder / 'Mods' / self.mod_folder_name
        ensure_directory_exists(self.xml_output_folder)
        ensure_directory_exists(self.lsx_output_folder)

        self.xml_output_path = self.xml_output_folder / f'{self.mod_name}.xml'
        self.lsx_output_path = self.lsx_output_folder / 'meta.lsx'

    
    def _get_paths_new(self) -> None:
        language_folder = LANGUAGES.get(self.target_lang)
        mod_folder = MODS_DIR / self.mod_folder_name / 'Mods' / self.mod_folder_name

        self.xml_output_folder = mod_folder / 'Localization' / language_folder
        self.lsx_output_folder = mod_folder
        ensure_directory_exists(self.xml_output_folder)
        ensure_directory_exists(self.lsx_output_folder)

        self.xml_output_path = self.xml_output_folder / f'{self.mod_name}.xml'
        self.lsx_output_path = self.lsx_output_folder / 'meta.lsx'
    

    def _get_paths(self) -> None:
        if self.export_method == 'default':
            self._get_paths_default()
        elif self.export_method == 'new':
            self._get_paths_new()
        else:
            raise Exception('Método de exportação inválido!')


    def _create_meta_lsx(self) -> None:
        uuid = str(uuid4())

        self.lsx_utils.update_mod_info(
            lsx_path=self.lsx_path,
            output_path=self.lsx_output_path,
            target_lang=self.target_lang,
            author=self.metadata.get('author'),
            description=self.metadata.get('description'),
            uuid=uuid,
        )
    

    def _translate(self) -> None:
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
        self._translate()
        self._create_meta_lsx()
        self.xml_utils.dataframe_to_xml(self.translated_df, self.xml_output_path)
