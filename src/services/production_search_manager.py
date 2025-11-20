#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Production Search Manager
Gerenciador de produção para múltiplos serviços de busca com rotação de APIs
"""

import os
import logging
import time
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class ProductionSearchManager:
    """Gerenciador de buscas de produção com rotação de APIs"""
    
    def __init__(self):
        """Inicializa o gerenciador de buscas de produção"""
        self.providers = {
            'google': {
                'available': bool(os.getenv('GOOGLE_SEARCH_KEY')),
                'priority': 1,
                'rate_limit_reset': None,
                'error_count': 0,
                'api_key': os.getenv('GOOGLE_SEARCH_KEY'),
                'cse_id': os.getenv('GOOGLE_CSE_ID')
            },
            'serper': {
                'available': bool(os.getenv('SERPER_API_KEY')),
                'priority': 2,
                'rate_limit_reset': None,
                'error_count': 0,
                'api_keys': [
                    os.getenv('SERPER_API_KEY'),
                    os.getenv('SERPER_API_KEY_1'),
                    os.getenv('SERPER_API_KEY_2'),
                    os.getenv('SERPER_API_KEY_3')
                ],
                'current_key_index': 0
            },
            'exa': {
                'available': bool(os.getenv('EXA_API_KEY')),
                'priority': 3,
                'rate_limit_reset': None,
                'error_count': 0,
                'api_keys': [
                    os.getenv('EXA_API_KEY'),
                    os.getenv('EXA_API_KEY_1')
                ],
                'current_key_index': 0
            },
            'firecrawl': {
                'available': bool(os.getenv('FIRECRAWL_API_KEY')),
                'priority': 4,
                'rate_limit_reset': None,
                'error_count': 0,
                'api_keys': [
                    os.getenv('FIRECRAWL_API_KEY'),
                    os.getenv('FIRECRAWL_API_KEY_1'),
                    os.getenv('FIRECRAWL_API_KEY_2')
                ],
                'current_key_index': 0
            },
            'fess': {
                'available': True,  # Sempre disponível como fallback local
                'priority': 5,
                'rate_limit_reset': None,
                'error_count': 0,
                'base_url': 'http://localhost:8080',
                'endpoint': '/json/',
                'description': 'Fess Local Search Engine - Fallback'
            }
        }
        
        # Remove chaves None
        for provider in self.providers.values():
            if 'api_keys' in provider:
                provider['api_keys'] = [key for key in provider['api_keys'] if key]
        
        self._check_providers()
        logger.info(f"Production Search Manager inicializado com {len([p for p in self.providers.values() if p['available']])} provedores")
    
    def _check_providers(self):
        """Verifica disponibilidade dos provedores"""
        for name, provider in self.providers.items():
            if name == 'google':
                provider['available'] = bool(provider['api_key'] and provider['cse_id'])
            elif 'api_keys' in provider:
                provider['available'] = bool(provider['api_keys'])
            
            if provider['available']:
                logger.info(f"✅ {name.upper()}: Disponível")
            else:
                logger.warning(f"❌ {name.upper()}: Não disponível")
    
    def rotate_api_key(self, provider_name: str):
        """Rotaciona a chave de API para o provedor especificado"""
        if provider_name not in self.providers:
            return False
            
        provider = self.providers[provider_name]
        if 'api_keys' not in provider or not provider['api_keys']:
            return False
        
        provider['current_key_index'] = (provider['current_key_index'] + 1) % len(provider['api_keys'])
        current_key = provider['api_keys'][provider['current_key_index']]
        
        logger.info(f"🔄 Rotação de API para {provider_name}: chave {provider['current_key_index'] + 1}/{len(provider['api_keys'])}")
        return True
    
    def get_current_api_key(self, provider_name: str) -> Optional[str]:
        """Obtém a chave de API atual para o provedor"""
        if provider_name not in self.providers:
            return None
            
        provider = self.providers[provider_name]
        
        if provider_name == 'google':
            return provider.get('api_key')
        elif 'api_keys' in provider and provider['api_keys']:
            return provider['api_keys'][provider['current_key_index']]
        
        return None
    
    def search_google(self, query: str, num_results: int = 10) -> List[Dict]:
        """Busca usando Google Custom Search"""
        try:
            api_key = self.get_current_api_key('google')
            cse_id = self.providers['google']['cse_id']
            
            if not api_key or not cse_id:
                logger.warning("Google Search: API key ou CSE ID não configurados")
                return []
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': cse_id,
                'q': query,
                'num': min(num_results, 10)
            }
            
            response = requests.get(url, params=params, timeout=60)
            
            if response.status_code == 429:
                logger.warning("Google Search: Rate limit atingido")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'google'
                })
            
            logger.info(f"Google Search: {len(results)} resultados para '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Erro no Google Search: {e}")
            return []
    
    def search_serper(self, query: str, num_results: int = 10) -> List[Dict]:
        """Busca usando Serper API com rotação de chaves"""
        try:
            api_key = self.get_current_api_key('serper')
            if not api_key:
                logger.warning("Serper: API key não configurada")
                return []
            
            url = "https://google.serper.dev/search"
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': num_results
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 429:
                logger.warning("Serper: Rate limit atingido, tentando rotacionar chave")
                if self.rotate_api_key('serper'):
                    return self.search_serper(query, num_results)
                return []
            
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('organic', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'serper'
                })
            
            logger.info(f"Serper: {len(results)} resultados para '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Erro no Serper: {e}")
            return []
    
    def search_fess(self, query: str, num_results: int = 10) -> List[Dict]:
        """Busca usando Fess local search engine"""
        try:
            from services.fess_integration import FessIntegration
            
            fess_client = FessIntegration(self.providers['fess']['base_url'])
            
            if not fess_client.is_available():
                logger.warning("Fess não está disponível")
                return []
            
            logger.info(f"Buscando no Fess: {query}")
            fess_results = fess_client.search(query, num_results)
            
            results = []
            if fess_results and isinstance(fess_results, dict):
                items = fess_results.get('items', []) or fess_results.get('documents', [])
                
                for item in items:
                    if isinstance(item, dict):
                        title = item.get('title', '') or item.get('doc_title', '')
                        url = item.get('link', '') or item.get('url', '') or item.get('doc_url', '')
                        snippet = item.get('snippet', '') or item.get('content_description', '')
                        
                        if title or url or snippet:
                            results.append({
                                'title': title[:200] if title else f"Resultado Fess: {query}",
                                'url': url if url else f"fess://search/{query}",
                                'snippet': snippet[:300] if snippet else f"Conteúdo local para: {query}",
                                'source': 'fess_local',
                                'provider': 'fess'
                            })
            
            logger.info(f"Fess: {len(results)} resultados para '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Erro no Fess: {e}")
            return []
    
    def search_multiple_providers(self, query: str, num_results: int = 10) -> List[Dict]:
        """Busca usando múltiplos provedores"""
        all_results = []
        
        # Tenta Google primeiro
        if self.providers['google']['available']:
            google_results = self.search_google(query, num_results)
            all_results.extend(google_results)
        
        # Se não tiver resultados suficientes, tenta Serper
        if len(all_results) < num_results and self.providers['serper']['available']:
            serper_results = self.search_serper(query, num_results - len(all_results))
            all_results.extend(serper_results)
        
        # Se ainda não tiver resultados suficientes, tenta Fess como fallback
        if len(all_results) < num_results and self.providers['fess']['available']:
            fess_results = self.search_fess(query, num_results - len(all_results))
            all_results.extend(fess_results)
        
        # Remove duplicatas baseado na URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        logger.info(f"Busca múltipla: {len(unique_results)} resultados únicos para '{query}'")
        return unique_results[:num_results]
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Retorna o status de todos os provedores"""
        status = {}
        for name, provider in self.providers.items():
            status[name] = {
                'available': provider['available'],
                'error_count': provider['error_count'],
                'current_key_index': provider.get('current_key_index', 0),
                'total_keys': len(provider.get('api_keys', [])) if 'api_keys' in provider else 1
            }
        return status

# Instância global
production_search_manager = ProductionSearchManager()