from src.services.chatgpt_service import ChatGPTService
from src.prompts.keepdriving import KeepDrivingPrompt
from typing import List, Dict, Any
import csv
import os

class TrasnlateKdrFiles:

    def __init__(
            self, kdr_path, kdr_output, 
            id_field: str, fields_to_translte: List[str],
            source_lang: str = 'en', target_lang: str = 'pt-BR',            
    ):
        self.chatgpt_service = ChatGPTService()
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.prompts = KeepDrivingPrompt(self.source_lang, self.target_lang)
        self.kdr_path = kdr_path
        self.kdr_output = kdr_output
        self.id_field = id_field
        self.fields_to_translate = fields_to_translte
        self.kdr_content = self.load_kdr()

        # criando o csv de acompanhamento
        self.csv_file = os.path.join(
            os.path.dirname(self.kdr_output), 
            f'translation_tracking_{os.path.basename(self.kdr_path)}.csv'
        )

        if not os.path.exists(self.csv_file):
            os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'ref', 'source_text', 'translated_text'])


    def load_kdr(self) -> list[dict]:
        """
        Carrega um arquivo KDR preservando o formato exato dos valores
        e lidando com chaves repetidas.
        """
        with open(self.kdr_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks = []
        current_block = ''
        brace_count = 0 
        in_block = False

        for char in content:
            if char == '{':
                brace_count += 1
                if not in_block:
                    in_block = True
                    current_block = '{'
                else:
                    current_block += char
            elif char == '}':
                brace_count -= 1
                current_block += char
                if brace_count == 0 and in_block:
                    in_block = False
                    blocks.append(current_block)
                    current_block = ''
            elif in_block:
                current_block += char

        result = []
        for block in blocks:
            block_content = block.strip()[1:-1].strip()
            
            # Mantém o conteúdo original do bloco para preservação
            original_content = block_content
            
            # Fazemos um parse modificado que mantém todas as linhas originais, incluindo ordem e repetições
            lines = [line.strip() for line in block_content.split('\n') if line.strip()]
            
            # Usamos uma estrutura que preserva a ordem e permite chaves repetidas
            entry = {
                '_original_content': original_content,  # Salva o conteúdo original
                '_lines': []  # Lista que armazenará cada linha como um par chave-valor
            }
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Armazena cada linha como um par chave-valor
                    entry['_lines'].append((key, value))
                    
                    # Também mantemos um acesso rápido às chaves
                    # Se a chave já existe, convertemos para lista
                    if key in entry:
                        if not isinstance(entry[key], list):
                            entry[key] = [entry[key]]
                        entry[key].append(value)
                    else:
                        entry[key] = value
                else:
                    # Linha sem o formato chave:valor
                    entry['_lines'].append(('_raw_line', line))
            
            if entry:
                result.append(entry)
        
        return result

    def translate_kdr(self):
        """
        Traduz os campos especificados em cada bloco do conteúdo KDR,
        lidando com chaves repetidas.
        """
        total_blocks = len(self.kdr_content)
        translated_count = 0
        
        for block_index, block in enumerate(self.kdr_content):
            # Obtém o ID do bloco (pode ser único ou uma lista)
            id_value = block.get(self.id_field, '')
            if isinstance(id_value, list):
                id_value = id_value[0]  # Usamos o primeiro ID se houver vários
            
            # Para rastrear quais linhas foram traduzidas
            translated_lines = []
            
            # Itera sobre as linhas do bloco
            for line_index, (key, value) in enumerate(block['_lines']):
                # Se a chave está na lista de campos a serem traduzidos
                if key in self.fields_to_translate:
                    source_text = value
                    
                    # Pula strings vazias
                    if not source_text.strip():
                        continue
                    
                    # Traduz o texto
                    translated_text = self.chatgpt_service.gpt_chat_completion(
                        source_text, self.source_lang, self.target_lang, 
                        self.prompts.dialogue_prompt()
                    )
                    
                    # Atualiza o valor na lista _lines
                    block['_lines'][line_index] = (key, translated_text)
                    
                    # Registra a tradução para o CSV
                    self._write_translation_to_csv(id_value, key, source_text, translated_text)
                    
                    translated_lines.append((key, source_text, translated_text))
                    
            # Se alguma linha foi traduzida, conta o bloco
            if translated_lines:
                translated_count += 1
                print(f"Bloco {block_index+1}/{total_blocks} traduzido: {id_value if id_value else 'sem ID'}")
                for key, source, translated in translated_lines:
                    print(f"  - {key}: '{source}' -> '{translated}'")
        
        print(f"Tradução concluída: {translated_count} de {total_blocks} blocos foram traduzidos")

    def _write_translation_to_csv(self, id_value, field, source_text, translated_text):
        """Registra uma tradução no arquivo CSV de rastreamento."""
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([id_value, field, source_text, translated_text])

    def save_kdr(self) -> None:
        """
        Salva o conteúdo KDR no arquivo de saída, preservando o formato exato
        incluindo a ordem das linhas e repetições de chaves.
        """
        os.makedirs(os.path.dirname(self.kdr_output), exist_ok=True)
        
        with open(self.kdr_output, 'w', encoding='utf-8') as f:
            for block in self.kdr_content:
                f.write('{\n')
                
                # Escreve cada linha na ordem original, mas com os valores traduzidos
                for key, value in block['_lines']:
                    if key == '_raw_line':
                        # Linhas sem formato chave:valor
                        f.write(f'\t{value}\n')
                    else:
                        f.write(f'\t{key}: {value}\n')
                
                f.write('}\n\n')


    def main(self):
        self.translate_kdr()
        self.save_kdr()