from pathlib import Path

from src.utils.dir_utils import list_files_by_extension, ensure_directory_exists
from src.utils.language_codes import LANGUAGES
from src.config.paths import MODS_DIR, UNPACKED_MODS


class BgModPaths:

    def __init__(self, mod_folder_name: str, source_lang: str, target_lang: str):
        self.mod_folder_name = mod_folder_name
        self.mod_path = UNPACKED_MODS / mod_folder_name
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.xml_paths = {}
        self.lsx_paths = []

        self._get_meta_path()
        self._get_xml_paths()


    def get_relative_path(self, path: Path) -> Path:
        path = Path(path)
        return path.relative_to(UNPACKED_MODS)


    def _get_meta_path(self) -> Path:
        meta_path = None
        lsx_list = list_files_by_extension(self.mod_path, 'lsx', recursive=True)
        for file in lsx_list:
            if Path(file).name == 'meta.lsx':
                meta_path = file
                self.lsx_paths.append(meta_path)
                break
        relative_path = str(MODS_DIR / self.get_relative_path(meta_path)).replace(self.mod_folder_name, f'{self.mod_folder_name}_{self.target_lang}')
        relative_path = Path(relative_path)
        ensure_directory_exists(relative_path.parent)
        self.lsx_paths.append(relative_path)


    def _get_xml_paths(self) -> list[Path]:
        lang_folder_name = LANGUAGES.get(self.source_lang)
        target_lang_folder = LANGUAGES.get(self.target_lang)
        xml_list = list_files_by_extension(self.mod_path, 'xml', recursive=True)

        for xml in xml_list:
            xml = Path(xml)
            if xml.parent.name == lang_folder_name:
                self.xml_paths[xml.stem] = []
                self.xml_paths[xml.stem].append(xml)
                
                xml_relative = str(MODS_DIR / self.get_relative_path(xml)).replace(self.mod_folder_name, f'{self.mod_folder_name}_{self.target_lang}')
                xml_relative = Path(xml_relative)
                xml_relative = xml_relative.parent.parent / target_lang_folder / f'{str(xml.stem).lower().replace('.loca', '')}_{self.target_lang}.xml'
                ensure_directory_exists(xml_relative.parent)
                self.xml_paths[xml.stem].append(xml_relative)



