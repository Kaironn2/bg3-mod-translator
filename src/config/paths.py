import os
from pathlib import Path
from src.utils.language_codes import LANGUAGES

ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

DB_DIR = ROOT_DIR / 'db'
DB_PATH = DB_DIR / 'dictionarys.db'
DB_URL = f'sqlite:///{DB_PATH}'

MODDERS_DIR = ROOT_DIR / 'modders_multitools'
UNPACKED_MODS = MODDERS_DIR / 'UnpackedMods'

MODS_DIR = ROOT_DIR / 'mods'

SRC_DIR = ROOT_DIR / 'src'

TEMP_DIR = ROOT_DIR / 'temp'

DATA_DIR = SRC_DIR / 'data'
DICTIONARIES_DIR = DATA_DIR / 'dictionaries'


def get_mods_dir(mod_name: str, source_lang: str, xml_name: str, import_method: str) -> dict[str, Path]:
    lang_folder_name = LANGUAGES.get(source_lang)

    if import_method == 'default':
        mods_folder = UNPACKED_MODS / mod_name
        xml_path = mods_folder / 'Localization' / lang_folder_name / f'{xml_name}.xml'
        meta_path = mods_folder / 'mods' / mod_name / 'meta.lsx'
        return {'xml_path': xml_path, 'meta_path': meta_path}
    
    if import_method == 'new':
        xml_path = UNPACKED_MODS / mod_name / 'Mods' / mod_name / 'Localization' / lang_folder_name / f'{xml_name}.xml'
        meta_path = UNPACKED_MODS / mod_name / 'Mods' / mod_name / 'meta.lsx'
        return {'xml_path': xml_path, 'meta_path': meta_path}
