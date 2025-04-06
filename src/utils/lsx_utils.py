import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Union
from src.config.paths import MODS_DIR


class LsxUtils:

    @staticmethod
    def load_lsx(lsx_path: Union[str, Path]) -> ET.ElementTree:
        return ET.parse(lsx_path)
    

    @staticmethod
    def save_lsx(tree: ET.ElementTree, file_path: Union[str, Path]) -> None:
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)


    @staticmethod
    def find_attribute_by_id(root: ET.Element, attribute_id: str) -> Optional[ET.Element]:
        for attribute in root.findall(f".//attribute[@id='{attribute_id}']"):
            return attribute
        return None

    
    @staticmethod
    def update_attribute_value(root: ET.Element, attribute_id: str, new_value: str) -> bool:
        attribute = LsxUtils.find_attribute_by_id(root, attribute_id)
        if attribute is not None:
            attribute.set('value', new_value)
            return True
        return False
    

    @staticmethod
    def update_multiple_attributes(root: ET.Element, updates: Dict[str, str]) -> Dict[str, bool]:
        results = {}
        for attribute_id, new_value in updates.items():
            results[attribute_id] = LsxUtils.update_attribute_value(root, attribute_id, new_value)
        return results
    

    @staticmethod
    def find_node_by_id(root: ET.Element, node_id: str) -> Optional[ET.Element]:
        for node in root.findall(f".//node[@id='{node_id}']"):
            return node
        return None
    

    @staticmethod
    def update_mod_info(
        lsx_path: Union[str, Path],
        output_path: Union[str, Path],
        author: Optional[str],
        description: Optional[str],
        uuid: Optional[str],
        target_lang: str,
    ) -> Path:
        
        mod_folder_name = f'{str(Path(lsx_path).parent.name)}_{target_lang}'
        
        tree = LsxUtils.load_lsx(lsx_path)
        root = tree.getroot()
        
        module_info = LsxUtils.find_node_by_id(root, 'ModuleInfo')
        if module_info is None:
            raise ValueError('Nó ModuleInfo não encontrado no arquivo LSX')
        
        updates = {
            'Author': author,
            'Description': description,
            'Folder': mod_folder_name,
            'Name': mod_folder_name,
            'UUID': uuid,
        }
        
        for attr_id, new_value in updates.items():
            if new_value is not None:
                attr = LsxUtils.find_attribute_by_id(module_info, attr_id)
                if attr is not None:
                    attr.set('value', new_value)
                    print(f'Atributo {attr_id} atualizado para: {new_value}')
                else:
                    print(f'Atributo {attr_id} não encontrado')
        
        LsxUtils.save_lsx(tree, output_path)
        print(f'Arquivo LSX modificado salvo em: {output_path}')
        
        return Path(output_path)