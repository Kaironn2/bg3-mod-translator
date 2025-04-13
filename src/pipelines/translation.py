from src.utils.dictionary_manager import DictionaryManager
from src.services.chatgpt_service import ChatGPTService
from src.prompts.baldurgate3 import BaldurGate3Prompt
from src.utils.language_codes import LANGUAGES
from src.config.paths import MODS_DIR
from src.utils.xml_utils import XmlUtils
from src.utils.dir_utils import ensure_directory_exists
from pathlib import Path
import pandas as pd
from time import sleep


class Bg3Translator:

    def __init__(self, source_lang: str, target_lang: str, xml_file_path: Path, nexus: bool, mod_io: bool):
        self.nexus = nexus
        self.mod_io = mod_io

        self.xml_file_path = xml_file_path
        self.mod_name = str(self.xml_file_path.stem).replace('.loca', '')
        self.df = XmlUtils.xml_to_dataframe(self.xml_file_path)

        self.source_lang = source_lang
        self.target_lang = target_lang
        self.sorted_langs = sorted([source_lang, target_lang])
        self.translation_model = {self.source_lang: [], self.target_lang: []}

        self.dict_manager = DictionaryManager(source_lang, target_lang)
        self.chatgpt_service = ChatGPTService()
        self.prompter = BaldurGate3Prompt(source_lang, target_lang, 100)

        self._get_dictionary()
        self._get_prompt()


    def _get_dictionary(self) -> None:
        self.dict_manager.load_dictionaries()
        self.translation_dict = dict(zip(
            self.dict_manager.loaded_dictionary[self.source_lang],
            self.dict_manager.loaded_dictionary[self.target_lang]
        ))
    

    def _get_prompt(self) -> None:
        for _, row in self.dict_manager.loaded_dictionary.iterrows():
            self.prompter.add_translation_example(row[self.source_lang], row[self.target_lang])
        self.prompt = self.prompter.general_prompt()


    def _save_incremental_translations(self, translations: dict) -> None:

        if not translations[self.source_lang]:
            return
        
        temp_df = pd.DataFrame(translations)
        filename = f'{self.mod_name}_{self.source_lang}_{self.target_lang}'

        self.dict_manager.append_to_dictionary(temp_df, filename)
        print(f'✓ Salvas {len(translations[self.source_lang])} traduções incrementalmente')


    def _append_to_dictionary(self, df:pd.DataFrame) -> None:
        dict_df = self.dict_manager.loaded_dictionary


    def translate(self) -> str:
        translation_dict = self.translation_dict
        session_translations = {self.source_lang: [], self.target_lang: []}

        saving_frequency = 5
        pending_translations = {self.source_lang: [], self.target_lang: []}

        total_rows = len(self.df)
        counter = 0
        gpt_counter = 0

        source_values = self.df['text'].values

        for source_value in source_values:
            counter += 1

            print(f'{counter}/{total_rows}')

            target_value = translation_dict.get(source_value)

            if target_value is not None:
                session_translations[self.source_lang].append(source_value)
                session_translations[self.target_lang].append(target_value)
                print(f'✓ {source_value} já traduzido -> {target_value}')
                self.prompter.add_translation_example(source_value, target_value)
                continue

            target_value = self.chatgpt_service.gpt_chat_completion(source_value, self.prompt)
            gpt_counter += 1
            if gpt_counter % 90 == 0:
                print('Esperando 30 segundos para evitar limites de uso')
                sleep(30)
                gpt_counter = 0

            print(f'Traduzido pelo gpt {source_value} -> {target_value}')

            session_translations[self.source_lang].append(source_value)
            session_translations[self.target_lang].append(target_value)

            pending_translations[self.source_lang].append(source_value)
            pending_translations[self.target_lang].append(target_value)

            translation_dict[source_value] = target_value
            self.prompter.add_translation_example(source_value, target_value)

            if len(pending_translations[self.source_lang]) >= saving_frequency:
                self._save_incremental_translations(pending_translations)
                pending_translations = {self.source_lang: [], self.target_lang: []}

        if len(pending_translations[self.source_lang]) > 0:
            self._save_incremental_translations(pending_translations)

        self.dict_manager.save_dictionary(pd.DataFrame(session_translations), f'{self.mod_name}_{self.source_lang}_{self.target_lang}')

        if len(session_translations[self.target_lang]) == len(self.df):
            translated_df = self.df.copy()
            translated_df['text'] = session_translations[self.target_lang]
            
            print('Primeiras 3 linhas para verificação:')
            for i in range(min(3, len(translated_df))):
                print(f'ID: {translated_df['contentuid'].iloc[i]}')
                print(f'Texto traduzido: {translated_df['text'].iloc[i]}')
                print('-' * 40)
            
            if self.nexus:
                mod_folder = str(self.xml_file_path.stem).replace('.loca', f'') + f'_{self.target_lang}'
                lang_folder = LANGUAGES.get(self.target_lang)
                mod_file = str(self.xml_file_path.stem).replace('.loca', '') + f'_{self.target_lang}.xml'
                output_folder = MODS_DIR / mod_folder / 'Localization' / lang_folder
                ensure_directory_exists(output_folder)
                output_path = MODS_DIR / mod_folder / 'Localization' / lang_folder / mod_file

            if self.mod_io:
                mod_folder = str(self.xml_file_path.parent.parent.parent.name) + f'_{self.target_lang}'
                lang_folder = LANGUAGES.get(self.target_lang)
                output_folder = MODS_DIR / mod_folder / 'Mods' / mod_folder / 'Localization' / lang_folder
                ensure_directory_exists(output_folder)
                output_path = MODS_DIR / mod_folder / 'Mods' / mod_folder / 'Localization' / lang_folder / f'{mod_folder}_{self.target_lang}.xml'

            print(f'Salvando traduções em {output_path}')
            XmlUtils.dataframe_to_xml(translated_df, output_path)
        else:
            print('Erro: número de traduções não corresponde ao número de linhas')
