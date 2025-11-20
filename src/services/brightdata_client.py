#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BrightData API Client - Cliente para integração com BrightData
Implementa extração de dados do Instagram e conteúdo web com rotação de APIs
"""

import os
import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class BrightDataConfig:
    """Configuração do BrightData"""
    api_key: str
    endpoint: str = "https://api.brightdata.com/v1"
    timeout: int = 30
    max_retries: int = 3
    enabled: bool = True

class BrightDataClient:
    """
    Cliente para BrightData API com rotação automática
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.session = None
        self.request_count = 0
        self.last_request_time = 0
        self.rate_limit_delay = 1  # 1 segundo entre requisições
        
    def _load_config(self) -> BrightDataConfig:
        """Carrega configuração do ambiente"""
        return BrightDataConfig(
            api_key=os.getenv('BRIGHTDATA_API_KEY', ''),
            endpoint=os.getenv('BRIGHTDATA_ENDPOINT', 'https://api.brightdata.com/v1'),
            timeout=int(os.getenv('BRIGHTDATA_TIMEOUT', '30')),
            max_retries=int(os.getenv('BRIGHTDATA_MAX_RETRIES', '3')),
            enabled=os.getenv('BRIGHTDATA_ENABLED', 'True').lower() == 'true'
        )
    
    async def __aenter__(self):
        """Context manager entry"""
        if not self.session:
            headers = {
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'ARQ-BETA-V1000/1.0'
            }
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _rate_limit(self):
        """Implementa rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    async def extract_instagram_images(self, username: str, max_posts: int = 20) -> List[Dict[str, Any]]:
        """
        Extrai imagens do Instagram usando BrightData
        
        Args:
            username: Nome de usuário do Instagram
            max_posts: Número máximo de posts para extrair
            
        Returns:
            Lista de dados dos posts com imagens
        """
        if not self.config.enabled or not self.config.api_key:
            logger.warning("⚠️ BrightData não configurado")
            return []
        
        try:
            await self._rate_limit()
            
            # Endpoint para extração do Instagram
            url = f"{self.config.endpoint}/instagram/profile"
            
            payload = {
                "username": username,
                "max_posts": max_posts,
                "include_images": True,
                "include_metadata": True,
                "format": "json"
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_instagram_data(data)
                elif response.status == 429:
                    logger.warning("⚠️ Rate limit atingido no BrightData")
                    await asyncio.sleep(5)
                    return []
                else:
                    logger.error(f"❌ Erro BrightData Instagram: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"❌ Erro na extração Instagram BrightData: {str(e)}")
            return []
    
    def _process_instagram_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Processa dados do Instagram retornados pela API
        """
        processed_posts = []
        
        try:
            posts = data.get('posts', [])
            
            for post in posts:
                processed_post = {
                    'id': post.get('id', ''),
                    'url': post.get('url', ''),
                    'image_url': post.get('image_url', ''),
                    'caption': post.get('caption', ''),
                    'likes': post.get('likes', 0),
                    'comments': post.get('comments', 0),
                    'timestamp': post.get('timestamp', ''),
                    'engagement_rate': self._calculate_engagement_rate(post),
                    'hashtags': self._extract_hashtags(post.get('caption', '')),
                    'source': 'brightdata_instagram'
                }
                processed_posts.append(processed_post)
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar dados Instagram: {str(e)}")
            
        return processed_posts
    
    def _calculate_engagement_rate(self, post: Dict[str, Any]) -> float:
        """Calcula taxa de engajamento"""
        try:
            likes = post.get('likes', 0)
            comments = post.get('comments', 0)
            followers = post.get('followers', 1)  # Evitar divisão por zero
            
            engagement = (likes + comments) / followers * 100
            return round(engagement, 2)
        except:
            return 0.0
    
    def _extract_hashtags(self, caption: str) -> List[str]:
        """Extrai hashtags da legenda"""
        import re
        hashtags = re.findall(r'#\w+', caption)
        return [tag.lower() for tag in hashtags]
    
    async def scrape_web_content(self, url: str, extract_images: bool = True) -> Dict[str, Any]:
        """
        Extrai conteúdo web usando BrightData
        
        Args:
            url: URL para extrair conteúdo
            extract_images: Se deve extrair imagens
            
        Returns:
            Dados extraídos da página
        """
        if not self.config.enabled or not self.config.api_key:
            logger.warning("⚠️ BrightData não configurado")
            return {}
        
        try:
            await self._rate_limit()
            
            # Endpoint para web scraping
            scrape_url = f"{self.config.endpoint}/web/scrape"
            
            payload = {
                "url": url,
                "extract_text": True,
                "extract_images": extract_images,
                "extract_links": True,
                "format": "json",
                "wait_for": 2000  # Aguardar 2 segundos para carregamento
            }
            
            async with self.session.post(scrape_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_web_data(data, url)
                elif response.status == 429:
                    logger.warning("⚠️ Rate limit atingido no BrightData")
                    await asyncio.sleep(5)
                    return {}
                else:
                    logger.error(f"❌ Erro BrightData Web Scraping: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Erro no web scraping BrightData: {str(e)}")
            return {}
    
    def _process_web_data(self, data: Dict[str, Any], original_url: str) -> Dict[str, Any]:
        """
        Processa dados web retornados pela API
        """
        try:
            processed_data = {
                'url': original_url,
                'title': data.get('title', ''),
                'text': data.get('text', ''),
                'images': data.get('images', []),
                'links': data.get('links', []),
                'metadata': data.get('metadata', {}),
                'timestamp': datetime.now().isoformat(),
                'source': 'brightdata_web',
                'success': True
            }
            
            # Filtrar e processar imagens
            if processed_data['images']:
                processed_data['images'] = self._filter_images(processed_data['images'])
            
            return processed_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar dados web: {str(e)}")
            return {
                'url': original_url,
                'success': False,
                'error': str(e),
                'source': 'brightdata_web'
            }
    
    def _filter_images(self, images: List[str]) -> List[Dict[str, Any]]:
        """
        Filtra e processa lista de imagens
        """
        filtered_images = []
        
        for img_url in images:
            if self._is_valid_image_url(img_url):
                img_data = {
                    'url': img_url,
                    'hash': hashlib.md5(img_url.encode()).hexdigest(),
                    'type': self._get_image_type(img_url),
                    'size_estimate': self._estimate_image_size(img_url)
                }
                filtered_images.append(img_data)
        
        return filtered_images
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Verifica se URL é de imagem válida"""
        if not url or not isinstance(url, str):
            return False
        
        # Extensões de imagem válidas
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        url_lower = url.lower()
        
        return any(ext in url_lower for ext in valid_extensions)
    
    def _get_image_type(self, url: str) -> str:
        """Determina tipo da imagem pela URL"""
        url_lower = url.lower()
        
        if '.jpg' in url_lower or '.jpeg' in url_lower:
            return 'jpeg'
        elif '.png' in url_lower:
            return 'png'
        elif '.gif' in url_lower:
            return 'gif'
        elif '.webp' in url_lower:
            return 'webp'
        elif '.svg' in url_lower:
            return 'svg'
        else:
            return 'unknown'
    
    def _estimate_image_size(self, url: str) -> str:
        """Estima tamanho da imagem pela URL"""
        url_lower = url.lower()
        
        if any(size in url_lower for size in ['thumb', 'small', '150x', '200x']):
            return 'small'
        elif any(size in url_lower for size in ['medium', '400x', '500x']):
            return 'medium'
        elif any(size in url_lower for size in ['large', 'big', '800x', '1000x', '1200x']):
            return 'large'
        else:
            return 'unknown'
    
    async def get_api_status(self) -> Dict[str, Any]:
        """
        Verifica status da API BrightData
        """
        try:
            await self._rate_limit()
            
            status_url = f"{self.config.endpoint}/status"
            
            async with self.session.get(status_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'status': 'active',
                        'requests_made': self.request_count,
                        'api_response': data,
                        'last_check': datetime.now().isoformat()
                    }
                else:
                    return {
                        'status': 'error',
                        'status_code': response.status,
                        'requests_made': self.request_count,
                        'last_check': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'requests_made': self.request_count,
                'last_check': datetime.now().isoformat()
            }

# Instância global
brightdata_client = BrightDataClient()

async def extract_instagram_with_brightdata(username: str, max_posts: int = 20) -> List[Dict[str, Any]]:
    """
    Função utilitária para extração do Instagram
    """
    async with brightdata_client as client:
        return await client.extract_instagram_images(username, max_posts)

async def scrape_web_with_brightdata(url: str, extract_images: bool = True) -> Dict[str, Any]:
    """
    Função utilitária para web scraping
    """
    async with brightdata_client as client:
        return await client.scrape_web_content(url, extract_images)

if __name__ == "__main__":
    # Teste da funcionalidade
    async def test_brightdata():
        async with BrightDataClient() as client:
            # Teste status
            status = await client.get_api_status()
            print(f"Status: {status}")
            
            # Teste web scraping
            web_data = await client.scrape_web_content("https://example.com")
            print(f"Web data: {len(web_data)} campos")
    
    asyncio.run(test_brightdata())