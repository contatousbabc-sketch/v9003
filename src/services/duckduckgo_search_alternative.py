#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuckDuckGo Search Alternative - Alternativa gratuita ao Google CSE
Implementa busca usando DuckDuckGo como fallback gratuito
"""

import asyncio
import aiohttp
import json
import time
import random
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import logging

# Importar bibliotecas de busca
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    from googlesearch import search as google_search
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False

logger = logging.getLogger(__name__)

class DuckDuckGoSearchAlternative:
    """
    Alternativa gratuita ao Google CSE usando DuckDuckGo
    """
    
    def __init__(self):
        self.request_delay = 2  # Delay entre requisições para evitar rate limiting
        self.max_results = 50
        self.region = 'br-pt'
        
    async def __aenter__(self):
        """Context manager entry"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass
    
    async def search(self, query: str, num_results: int = 10, region: str = 'br-pt') -> List[Dict[str, Any]]:
        """
        Realiza busca no DuckDuckGo usando a biblioteca duckduckgo-search
        
        Args:
            query: Termo de busca
            num_results: Número de resultados desejados
            region: Região da busca (br-pt para Brasil)
            
        Returns:
            Lista de resultados da busca
        """
        try:
            if not DDGS_AVAILABLE:
                logger.warning("⚠️ Biblioteca duckduckgo-search não disponível")
                return await self._fallback_search(query, num_results)
            
            # Usar a biblioteca duckduckgo-search
            results = []
            
            # Executar busca em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            search_results = await loop.run_in_executor(
                None, 
                self._sync_ddgs_search, 
                query, 
                num_results, 
                region
            )
            
            # Converter para formato padrão
            for result in search_results:
                formatted_result = {
                    'title': result.get('title', ''),
                    'link': result.get('href', ''),
                    'snippet': result.get('body', ''),
                    'displayLink': self._extract_domain(result.get('href', '')),
                    'source': 'duckduckgo'
                }
                results.append(formatted_result)
            
            logger.info(f"✅ DuckDuckGo: {len(results)} resultados para '{query}'")
            return results[:num_results]
                    
        except Exception as e:
            logger.error(f"❌ Erro na busca DuckDuckGo: {str(e)}")
            return await self._fallback_search(query, num_results)
    
    def _sync_ddgs_search(self, query: str, num_results: int, region: str) -> List[Dict[str, Any]]:
        """
        Busca síncrona usando DDGS
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    keywords=query,
                    region=region,
                    safesearch='moderate',
                    timelimit=None,
                    max_results=num_results
                ))
                return results
        except Exception as e:
            logger.error(f"❌ Erro na busca DDGS síncrona: {str(e)}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """
        Extrai o domínio de uma URL
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url.split('/')[2] if '/' in url else url
    
    async def _fallback_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """
        Busca de fallback usando googlesearch-python
        """
        try:
            if not GOOGLE_SEARCH_AVAILABLE:
                logger.warning("⚠️ Nenhuma biblioteca de busca disponível")
                return []
            
            # Executar busca em thread separada
            loop = asyncio.get_event_loop()
            urls = await loop.run_in_executor(
                None,
                self._sync_google_search,
                query,
                num_results
            )
            
            results = []
            for i, url in enumerate(urls):
                if i >= num_results:
                    break
                    
                result = {
                    'title': f'Resultado {i+1}',
                    'link': url,
                    'snippet': f'Resultado encontrado para: {query}',
                    'displayLink': self._extract_domain(url),
                    'source': 'google_fallback'
                }
                results.append(result)
            
            logger.info(f"✅ Google Fallback: {len(results)} resultados para '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro na busca de fallback: {str(e)}")
            return []
    
    def _sync_google_search(self, query: str, num_results: int) -> List[str]:
        """
        Busca síncrona usando googlesearch-python
        """
        try:
            urls = []
            for url in google_search(query, num_results=num_results, lang='pt', pause=2):
                urls.append(url)
                if len(urls) >= num_results:
                    break
            return urls
        except Exception as e:
            logger.error(f"❌ Erro na busca Google síncrona: {str(e)}")
            return []
    


class AlternativeSearchManager:
    """
    Gerenciador de buscas alternativas gratuitas
    """
    
    def __init__(self):
        self.alternatives = {
            'duckduckgo': DuckDuckGoSearchAlternative(),
            'bing': self._bing_search,
            'yahoo': self._yahoo_search
        }
        self.current_alternative = 'duckduckgo'
        
    async def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Realiza busca usando alternativas gratuitas
        """
        results = []
        
        # Tentar DuckDuckGo primeiro
        try:
            async with DuckDuckGoSearchAlternative() as ddg:
                results = await ddg.search(query, num_results)
                
            if results:
                logger.info(f"✅ DuckDuckGo: {len(results)} resultados para '{query}'")
                return results
                
        except Exception as e:
            logger.error(f"Erro no DuckDuckGo: {str(e)}")
        
        # Fallback para outras alternativas
        try:
            bing_results = await self._bing_search(query, num_results)
            if bing_results:
                results.extend(bing_results)
                logger.info(f"✅ Bing: {len(bing_results)} resultados para '{query}'")
                
        except Exception as e:
            logger.error(f"Erro no Bing: {str(e)}")
        
        return results[:num_results]
    
    async def _bing_search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca usando Bing (método simplificado)
        """
        try:
            import aiohttp
            
            url = "https://www.bing.com/search"
            params = {
                'q': query,
                'count': num_results,
                'offset': 0
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_bing_results(html)
                        
        except Exception as e:
            logger.error(f"Erro na busca Bing: {str(e)}")
            
        return []
    
    def _parse_bing_results(self, html: str) -> List[Dict[str, Any]]:
        """
        Parse dos resultados do Bing
        """
        results = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Encontrar elementos de resultado do Bing
            result_elements = soup.find_all('li', class_='b_algo')
            
            for element in result_elements:
                title_elem = element.find('h2')
                link_elem = title_elem.find('a') if title_elem else None
                snippet_elem = element.find('p')
                
                if title_elem and link_elem:
                    result = {
                        'title': title_elem.get_text(strip=True),
                        'link': link_elem.get('href', ''),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'displayLink': link_elem.get('href', '').split('/')[2] if '/' in link_elem.get('href', '') else '',
                        'source': 'bing'
                    }
                    results.append(result)
                    
        except Exception as e:
            logger.error(f"Erro ao fazer parse dos resultados Bing: {str(e)}")
            
        return results
    
    async def _yahoo_search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca usando Yahoo (método simplificado)
        """
        # Implementação similar ao Bing
        return []

# Instância global
alternative_search_manager = AlternativeSearchManager()

async def search_with_alternatives(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """
    Função utilitária para busca com alternativas gratuitas
    """
    return await alternative_search_manager.search(query, num_results)

if __name__ == "__main__":
    # Teste da funcionalidade
    async def test_search():
        results = await search_with_alternatives("python programming", 5)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['link']}")
            print(f"   {result['snippet'][:100]}...")
            print()
    
    asyncio.run(test_search())