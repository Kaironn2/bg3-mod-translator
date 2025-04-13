from src.pipelines.bg3.nexus_mods import BaldurGate3ModTranslator


# TODO - Identificar tags "tooltip" e manter o padrão de tradução com base na tradução nativa

source_lang = 'en'
target_lang = 'ptbr'
method = 'new'

mod_name = "lanceboard"
mod_folder_name = "lanceboard"

metadata = {
    'author': 'Kaironn2', 
    'description': f'pt-BR translation for {mod_name}'
}


translator = BaldurGate3ModTranslator(
    target_mod_name=mod_name,
    mod_folder_name=mod_folder_name,
    source_lang=source_lang, 
    target_lang=target_lang, 
    metadata=metadata,
)
translator.mod_translate()
