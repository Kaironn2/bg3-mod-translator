import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import requests
import openai


load_dotenv()


class ChatGPTService:


    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            raise ValueError('Chave de API da OpenAI não definida.')
        
        self.api_base_url = 'https://api.openai.com/v1/chat/completions'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        self.model = 'gpt-4o-mini'


    def _make_api_call(self, messages: List[Dict[str, str]]) -> str:
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': 0.3,
            'max_tokens': 4000,
        }

        try:
            response = requests.post(self.api_base_url, headers=self.headers, json=payload)
            response.raise_for_status()

            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except requests.exceptions.RequestException as e:
            error_message = f'Erro na chamada de API: {str(e)}'
            if hasattr(e, 'response') and e.response:
                error_message = f'{error_message} - {e.response.text}'
            raise Exception(error_message)

    
    def gpt_chat_completion(self, content: str, system_prompt: str) -> str:
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': content}
        ]
        
        return self._make_api_call(messages)
    

    def generate_image(
            self, 
            prompt: str, 
            model: str = 'dall-e-3', 
            size: str = '1024x1024',
            quality: str = 'standard',
            style: str = 'vivid',
            n: int = 1
        ) -> List[str]:

            image_api_url = 'https://api.openai.com/v1/images/generations'
            
            payload = {
                'model': model,
                'prompt': prompt,
                'n': n,
                'size': size,
                'response_format': 'url'
            }
            
            # Adicionar parâmetros específicos para dall-e-3
            if model == 'dall-e-3':
                payload['quality'] = quality
                payload['style'] = style
            
            try:
                response = requests.post(
                    image_api_url, 
                    headers=self.headers, 
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                image_urls = [img_data['url'] for img_data in result['data']]
                
                return image_urls
            except requests.exceptions.RequestException as e:
                error_message = f'Erro na geração de imagem: {str(e)}'
                if hasattr(e, 'response') and e.response:
                    error_message = f'{error_message} - {e.response.text}'
                raise Exception(error_message)