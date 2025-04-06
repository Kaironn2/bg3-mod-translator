class BaldurGate3Prompt:

    def __init__(self, source_lang: str, target_lang: str, max_context_examples: int = 20, preview_length: int = 100):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.translation_examples = []
        self.max_context_examples = max_context_examples
        self.preview_length = preview_length  # Adicionado parâmetro para controlar tamanho do preview

    def add_translation_example(self, source_text: str, target_text: str):
        """Adiciona um exemplo de tradução ao contexto e mantém apenas os mais recentes"""
        self.translation_examples.insert(0, (source_text, target_text))

        if len(self.translation_examples) > self.max_context_examples:
            self.translation_examples = self.translation_examples[:self.max_context_examples]

    def select_relevant_examples(self, current_text: str, num_examples: int = 5) -> list:
        if not self.translation_examples or not current_text:
            return self.translation_examples[:num_examples]
        
        def similarity(text1, text2):
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            common_words = words1.intersection(words2)
            return len(common_words) / max(len(words1) + len(words2), 1)  # Evita divisão por zero
        
        scored_examples = [(ex, similarity(current_text, ex[0])) 
                          for ex in self.translation_examples]
        scored_examples.sort(key=lambda x: x[1], reverse=True)
        
        return [ex[0] for ex in scored_examples[:num_examples]]

    def build_context_section(self, max_tokens: int = 1000, current_text: str = None) -> str:
        """
        Constrói seção de contexto do prompt, otimizada por tokens e relevância.
        
        Args:
            max_tokens: Número máximo de tokens para a seção de contexto
            current_text: Texto atual para selecionar exemplos relevantes
            
        Returns:
            Seção de contexto formatada
        """
        if not self.translation_examples:
            return ''
        
        # Selecionar exemplos - por relevância se current_text for fornecido
        examples_to_use = []
        if current_text:
            # Usar os exemplos mais relevantes para o texto atual
            examples_to_use = self.select_relevant_examples(current_text, num_examples=min(10, self.max_context_examples))
        else:
            # Usar os exemplos mais recentes
            examples_to_use = self.translation_examples[:self.max_context_examples]
        
        context = f'\n\nExemplos de traduções ({len(examples_to_use)}):\n'
        token_count = len(context.split())
        
        for i, (source, target) in enumerate(examples_to_use, 1):
            # Reduzir tamanho para economizar tokens
            source_preview = source[:self.preview_length] + "..." if len(source) > self.preview_length else source
            target_preview = target[:self.preview_length] + "..." if len(target) > self.preview_length else target
            
            example = f'{i}. {self.source_lang}: {source_preview}\n   {self.target_lang}: {target_preview}\n'
            example_tokens = len(example.split())
            
            # Parar se adicionar este exemplo excederia o limite
            if token_count + example_tokens > max_tokens:
                context += f"(limite de tokens atingido - {i-1} exemplos incluídos)"
                break
                
            context += example
            token_count += example_tokens
        
        return context

    def general_prompt(self, current_text: str = None, max_context_tokens: int = 1000):
        """
        Gera o prompt completo para tradução
        
        Args:
            current_text: Texto atual para selecionar exemplos relevantes
            max_context_tokens: Máximo de tokens para a seção de contexto
        """
        base_prompt = (
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
        )

        # Gerar contexto otimizado por tokens E relevância
        context_section = self.build_context_section(
            max_tokens=max_context_tokens, 
            current_text=current_text
        )

        return base_prompt + context_section
