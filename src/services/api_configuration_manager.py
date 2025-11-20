
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v2.0 - API Configuration Manager
Gerenciador automático de configuração e teste de APIs
"""

import os
import logging
from typing import Dict, List, Any, Optional
import requests
import time

logger = logging.getLogger(__name__)

class APIConfigurationManager:
    """Gerenciador de configuração automática de APIs"""

    def __init__(self):
        """Inicializa o gerenciador"""
        self.api_status = {}
        self.test_queries = [
            "teste de conectividade",
            "hello world",
            "análise de mercado"
        ]

    def test_all_apis(self) -> Dict[str, Any]:
        """Testa todas as APIs configuradas"""
        
        logger.info("🔧 Iniciando teste automático de todas as APIs...")
        
        results = {
            'gemini': self._test_gemini(),
            'openai': self._test_openai(), 
            'openrouter': self._test_openrouter(),
            'jina': self._test_jina(),
            'exa': self._test_exa(),
            'youtube': self._test_youtube(),
            'twitter': self._test_twitter()
        }
        
        # Resume dos resultados
        working_apis = [api for api, status in results.items() if status.get('working', False)]
        failed_apis = [api for api, status in results.items() if not status.get('working', False)]
        
        logger.info(f"✅ APIs funcionando: {len(working_apis)} - {', '.join(working_apis)}")
        if failed_apis:
            logger.warning(f"⚠️ APIs com problemas: {len(failed_apis)} - {', '.join(failed_apis)}")
        
        return {
            'summary': {
                'total_tested': len(results),
                'working': len(working_apis),
                'failed': len(failed_apis),
                'working_apis': working_apis,
                'failed_apis': failed_apis
            },
            'detailed_results': results,
            'recommendations': self._generate_recommendations(results)
        }

    def _test_gemini(self) -> Dict[str, Any]:
        """Testa API do Gemini"""
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {'working': False, 'error': 'API key não configurada', 'recommendation': 'Configure GEMINI_API_KEY no .env'}
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            response = model.generate_content("Responda apenas: GEMINI_OK")
            
            if response.text and "GEMINI_OK" in response.text:
                return {'working': True, 'model': 'gemini-2.0-flash-exp', 'response_time': 'normal'}
            else:
                return {'working': False, 'error': 'Resposta inválida', 'recommendation': 'Verifique se a API key tem permissões corretas'}
                
        except Exception as e:
            return {'working': False, 'error': str(e), 'recommendation': 'Verifique se a API key está correta e tem créditos'}

    def _test_openai(self) -> Dict[str, Any]:
        """Testa API do OpenAI"""
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {'working': False, 'error': 'API key não configurada', 'recommendation': 'Configure OPENAI_API_KEY no .env'}
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Responda apenas: OPENAI_OK"}],
                max_tokens=10
            )
            
            if response.choices[0].message.content and "OPENAI_OK" in response.choices[0].message.content:
                return {'working': True, 'model': 'gpt-4o-mini', 'response_time': 'normal'}
            else:
                return {'working': False, 'error': 'Resposta inválida', 'recommendation': 'Verifique se a API key tem permissões corretas'}
                
        except Exception as e:
            error_msg = str(e)
            if 'quota' in error_msg.lower() or '429' in error_msg:
                return {'working': False, 'error': 'Quota excedida', 'recommendation': 'Adicione créditos à conta OpenAI ou aguarde reset da quota'}
            else:
                return {'working': False, 'error': error_msg, 'recommendation': 'Verifique se a API key está correta'}

    def _test_openrouter(self) -> Dict[str, Any]:
        """Testa API do OpenRouter com Google Gemini 2.0 Flash"""
        
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            return {'working': False, 'error': 'API key não configurada', 'recommendation': 'Configure OPENROUTER_API_KEY no .env'}
        
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://arqv18.com',
                'X-Title': 'ARQV18 Enhanced'
            }
            
            data = {
                'model': 'google/gemini-2.0-flash-exp:free',
                'messages': [{'role': 'user', 'content': 'Responda apenas: OPENROUTER_OK'}],
                'max_tokens': 10
            }
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                if content and "OPENROUTER_OK" in content:
                    return {'working': True, 'model': 'google/gemini-2.0-flash-exp:free', 'response_time': 'fast'}
                else:
                    return {'working': False, 'error': 'Resposta inválida', 'recommendation': 'Verifique se a API key tem permissões corretas'}
            else:
                return {'working': False, 'error': f'HTTP {response.status_code}', 'recommendation': 'Verifique se a API key está correta'}
                
        except Exception as e:
            return {'working': False, 'error': str(e), 'recommendation': 'Verifique se a API key está correta'}

    def _test_jina(self) -> Dict[str, Any]:
        """Testa API do Jina"""
        
        api_key = os.getenv('JINA_API_KEY')
        if not api_key:
            return {'working': False, 'error': 'API key não configurada', 'recommendation': 'Configure JINA_API_KEY no .env'}
        
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Accept': 'text/plain'
            }
            
            response = requests.get('https://r.jina.ai/https://example.com', headers=headers, timeout=20)
            
            if response.status_code == 200:
                return {'working': True, 'service': 'jina-reader', 'response_time': 'normal'}
            else:
                return {'working': False, 'error': f'Status code: {response.status_code}', 'recommendation': 'Verifique se a API key está correta'}
                
        except Exception as e:
            return {'working': False, 'error': str(e), 'recommendation': 'Verifique conexão de rede e API key'}

    def _test_exa(self) -> Dict[str, Any]:
        """Testa API do Exa"""
        
        api_key = os.getenv('EXA_API_KEY')
        if not api_key:
            return {'working': False, 'error': 'API key não configurada', 'recommendation': 'Configure EXA_API_KEY no .env'}
        
        try:
            headers = {
                'x-api-key': api_key,
                'Content-Type': 'application/json'
            }
            
            data = {
                'query': 'test search',
                'type': 'neural',
                'numResults': 1
            }
            
            response = requests.post('https://api.exa.ai/search', headers=headers, json=data, timeout=20)
            
            if response.status_code == 200:
                return {'working': True, 'service': 'exa-search', 'response_time': 'normal'}
            else:
                return {'working': False, 'error': f'Status code: {response.status_code}', 'recommendation': 'Verifique se a API key está correta'}
                
        except Exception as e:
            return {'working': False, 'error': str(e), 'recommendation': 'Verifique conexão de rede e API key'}

    def _test_youtube(self) -> Dict[str, Any]:
        """Testa API do YouTube"""
        
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            return {'working': False, 'error': 'API key não configurada', 'recommendation': 'Configure YOUTUBE_API_KEY no .env'}
        
        try:
            url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=test&key={api_key}&maxResults=1"
            response = requests.get(url, timeout=20)
            
            if response.status_code == 200:
                return {'working': True, 'service': 'youtube-v3', 'response_time': 'normal'}
            else:
                return {'working': False, 'error': f'Status code: {response.status_code}', 'recommendation': 'Verifique se a API key está correta e ativa'}
                
        except Exception as e:
            return {'working': False, 'error': str(e), 'recommendation': 'Verifique conexão de rede e API key'}

    def _test_twitter(self) -> Dict[str, Any]:
        """Testa API do Twitter"""
        
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not bearer_token:
            return {'working': False, 'error': 'Bearer token não configurado', 'recommendation': 'Configure TWITTER_BEARER_TOKEN no .env'}
        
        try:
            headers = {
                'Authorization': f'Bearer {bearer_token}'
            }
            
            response = requests.get('https://api.twitter.com/2/tweets/search/recent?query=test&max_results=10', headers=headers, timeout=20)
            
            if response.status_code == 200:
                return {'working': True, 'service': 'twitter-v2', 'response_time': 'normal'}
            else:
                return {'working': False, 'error': f'Status code: {response.status_code}', 'recommendation': 'Verifique se o bearer token está correto'}
                
        except Exception as e:
            return {'working': False, 'error': str(e), 'recommendation': 'Verifique conexão de rede e bearer token'}

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nos resultados dos testes"""
        
        recommendations = []
        
        # Verifica se pelo menos uma IA está funcionando
        ai_apis = ['gemini', 'openai', 'openrouter']
        working_ais = [api for api in ai_apis if results.get(api, {}).get('working', False)]
        
        if not working_ais:
            recommendations.append("🚨 CRÍTICO: Nenhuma API de IA está funcionando! Configure pelo menos uma: Gemini, OpenAI ou OpenRouter")
        elif len(working_ais) == 1:
            recommendations.append(f"⚠️ Apenas {working_ais[0]} funcionando. Configure mais APIs para redundância")
        else:
            recommendations.append(f"✅ {len(working_ais)} APIs de IA funcionando: {', '.join(working_ais)}")
        
        # Verifica APIs de pesquisa
        search_apis = ['jina', 'exa']
        working_search = [api for api in search_apis if results.get(api, {}).get('working', False)]
        
        if not working_search:
            recommendations.append("⚠️ Nenhuma API de pesquisa avançada funcionando. Configure Jina ou Exa para melhores resultados")
        
        # Verifica APIs sociais
        social_apis = ['youtube', 'twitter']
        working_social = [api for api in social_apis if results.get(api, {}).get('working', False)]
        
        if not working_social:
            recommendations.append("⚠️ Nenhuma API de rede social funcionando. Configure YouTube e/ou Twitter para análise completa")
        
        return recommendations

    def auto_configure_environment(self) -> Dict[str, Any]:
        """Configuração automática do ambiente"""
        
        logger.info("🔧 Iniciando configuração automática do ambiente...")
        
        # Testa APIs
        test_results = self.test_all_apis()
        
        # Configura fallbacks baseado nos resultados
        config_changes = []
        
        working_ais = test_results['summary']['working_apis']
        if 'openrouter' in working_ais:
            config_changes.append("OpenRouter com Google Gemini 2.0 Flash definido como provedor primário (mais rápido)")
        elif 'gemini' in working_ais:
            config_changes.append("Gemini definido como provedor primário")
        elif 'openai' in working_ais:
            config_changes.append("OpenAI definido como provedor primário")
        
        return {
            'test_results': test_results,
            'config_changes': config_changes,
            'status': 'completed',
            'ready_for_analysis': len(test_results['summary']['working_apis']) > 0
        }

# Instância global
api_config_manager = APIConfigurationManager()

# Função para teste rápido
def test_apis_now():
    """Função de conveniência para teste rápido"""
    return api_config_manager.test_all_apis()
