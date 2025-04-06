from src.config.paths import DICTIONARIES_DIR
from src.prompts.search_similarity import TranslationSimilaritySearch

class Prompter:

    def __init__(self, source_lang: str, target_lang: str):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.similarity_searcher = TranslationSimilaritySearch(source_lang, target_lang)
        self.dictionaries_dir = DICTIONARIES_DIR / f'{source_lang}_{target_lang}'

    
    def get_prompt(self, query: str, limit: int = 5) -> str:
        context = self.similarity_searcher.get_context_string(query, limit)
                
        prompt = (
            f'Você é um tradutor especializado em localização de jogos, traduzindo de {self.source_lang} para {self.target_lang}. '
            f'Você foi contratado para traduzir especificamente conteúdo do jogo Baldur Gate 3. '
            f'Você pode também utilizar termos de Dungeons & Dragons, como "d20", "d8", "dungeon master", etc. '
            f'Siga estas regras críticas:\n'
            f'1. NÃO traduza nomes de variáveis, tags ou placeholders (como [Player], <CHAR>, {0}, etc.)\n'
            f'2. Você irá encontrar tags no seguinte formato -> &lt;LSTag Type="Status" Tooltip="BLINDED"&gt;Blinded&lt;/LSTag&gt; <- Nesse caso, você irá traduzir apenas o Blinded que é o texto. NÃO altere nenhuma outra informação da tag.\n'
            f'3. Mantenha toda formatação original (espaçamento, quebras de linha)\n'
            f'4. Preserve todos os símbolos especiais e pontuação\n'
            f'5. Adapte expressões idiomáticas para soar natural no idioma alvo\n'
            f'6. Traduza apenas o texto que seria visível ao jogador\n'
            f'7. Retorne APENAS o texto traduzido, sem explicações\n'
            f'8. Traduza o contéudo interno das LSTAG AttackRoll como "Rolagem de Ataque", SavingThrow como "Teste de Resistência" e "AbilityCheck" como "Teste de Habilidade"'
            f'\n\n{context}'
        )

        return prompt