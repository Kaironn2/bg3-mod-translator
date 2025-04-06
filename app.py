from src.config.paths import UNPACKED_MODS, get_mods_dir
from src.utils.language_codes import LANGUAGES
from src.pipelines.bg3.nexus_mods import BaldurGate3ModTranslator


# TODO - Fazer uma interface gráfica para ler nosso BD e nos permitir editar o source e target
# TODO - Fazer lógica para identificar tags e traduzir elas com o mesmo nome


source_lang = 'en'
target_lang = 'ptbr'
method = 'new'

mod_name = "MystraSpells"
mod_folder_name = "MystraSpells"

metadata = {'author': 'Kaironn2', 'description': f'pt-BR translation for {mod_name}'}


translator = BaldurGate3ModTranslator(
    target_mod_name=mod_name,
    mod_folder_name=mod_folder_name,
    source_lang=source_lang, 
    target_lang=target_lang, 
    metadata=metadata,
)
translator.mod_translate()
