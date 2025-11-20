#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Instagram Bypass Utilities
Sistema robusto para contornar bloqueios do Instagram
"""

import random
import time
import logging
from typing import Dict, List, Optional
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class InstagramBypass:
    """Sistema para contornar bloqueios do Instagram"""
    
    def __init__(self):
        self.user_agents = [
            # Chrome Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            
            # Firefox Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
            
            # Safari macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            
            # Mobile
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        ]
        
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_delay = 2.0  # Delay mínimo entre requisições
        
    def get_headers(self, mobile: bool = False) -> Dict[str, str]:
        """Gera headers realistas para requisições"""
        
        if mobile:
            user_agent = random.choice([ua for ua in self.user_agents if 'Mobile' in ua or 'iPhone' in ua])
        else:
            user_agent = random.choice([ua for ua in self.user_agents if 'Mobile' not in ua and 'iPhone' not in ua])
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # Adicionar headers específicos do Instagram
        if 'instagram.com' in str(headers.get('Referer', '')):
            headers.update({
                'X-Instagram-AJAX': '1',
                'X-CSRFToken': self._generate_csrf_token(),
                'X-Requested-With': 'XMLHttpRequest'
            })
        
        return headers
    
    def _generate_csrf_token(self) -> str:
        """Gera um token CSRF válido"""
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def _respect_rate_limit(self):
        """Respeita rate limit entre requisições"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_delay:
            sleep_time = self.min_delay - elapsed + random.uniform(0.5, 1.5)
            logger.debug(f"Rate limit: aguardando {sleep_time:.1f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_alternative_urls(self, instagram_url: str) -> List[str]:
        """Gera URLs alternativas para tentar acessar o conteúdo"""
        
        parsed = urlparse(instagram_url)
        path = parsed.path.strip('/')
        
        alternatives = []
        
        # Extrair shortcode do post
        shortcode = None
        if '/p/' in path:
            shortcode = path.split('/p/')[-1].split('/')[0]
        elif '/reel/' in path:
            shortcode = path.split('/reel/')[-1].split('/')[0]
        
        if shortcode:
            # URLs alternativas com diferentes estratégias
            alternatives.extend([
                # Embed URLs (menos bloqueadas)
                f"https://www.instagram.com/p/{shortcode}/embed/",
                f"https://www.instagram.com/p/{shortcode}/embed/captioned/",
                
                # URLs com parâmetros que podem contornar bloqueios
                f"https://www.instagram.com/p/{shortcode}/?__a=1",
                f"https://www.instagram.com/p/{shortcode}/?__a=1&__d=dis",
                
                # URLs mobile (menos restritivas)
                f"https://m.instagram.com/p/{shortcode}/",
                f"https://m.instagram.com/p/{shortcode}/?taken-by=",
                
                # URLs com diferentes parâmetros
                f"https://www.instagram.com/p/{shortcode}/?utm_source=ig_web_copy_link",
                f"https://www.instagram.com/p/{shortcode}/?hl=en",
                f"https://www.instagram.com/p/{shortcode}/?hl=pt-br",
                
                # URLs sem www
                f"https://instagram.com/p/{shortcode}/",
                
                # URL original
                instagram_url
            ])
        else:
            # Se não conseguir extrair shortcode, usa URL original
            alternatives.append(instagram_url)
        
        return list(set(alternatives))  # Remove duplicatas
    
    def safe_request(self, url: str, max_retries: int = 3, use_mobile: bool = False) -> Optional[requests.Response]:
        """Faz requisição segura com bypass de bloqueios"""
        
        # Extrair shortcode para uso nas estratégias de bypass
        shortcode = None
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if '/p/' in path:
            shortcode = path.split('/p/')[-1].split('/')[0]
        elif '/reel/' in path:
            shortcode = path.split('/reel/')[-1].split('/')[0]
        
        alternatives = self.get_alternative_urls(url)
        
        for attempt in range(max_retries):
            for alt_url in alternatives:
                try:
                    self._respect_rate_limit()
                    
                    headers = self.get_headers(mobile=use_mobile)
                    
                    # Usar sessão para manter cookies
                    response = self.session.get(
                        alt_url,
                        headers=headers,
                        timeout=30,
                        allow_redirects=True,
                        verify=True
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Sucesso com {alt_url}")
                        return response
                    elif response.status_code == 403:
                        logger.warning(f"⚠️ 403 Forbidden para {alt_url}")
                        # Para 403, tenta estratégias específicas
                        if 'embed' not in alt_url and shortcode:
                            # Se não é embed, tenta versão embed
                            embed_url = f"https://www.instagram.com/p/{shortcode}/embed/"
                            try:
                                embed_response = self.session.get(
                                    embed_url,
                                    headers=self.get_headers(mobile=True),
                                    timeout=30,
                                    allow_redirects=True
                                )
                                if embed_response.status_code == 200:
                                    logger.info(f"✅ Sucesso com embed: {embed_url}")
                                    return embed_response
                            except:
                                pass
                        continue
                    elif response.status_code == 429:
                        logger.warning(f"⚠️ Rate limit para {alt_url}")
                        time.sleep(random.uniform(5, 15))
                        continue
                    elif response.status_code == 404:
                        logger.debug(f"404 Not Found para {alt_url} - post pode ter sido removido")
                        continue
                    else:
                        logger.debug(f"Status {response.status_code} para {alt_url}")
                        
                except requests.exceptions.RequestException as e:
                    logger.debug(f"Erro de requisição para {alt_url}: {e}")
                    continue
            
            # Se chegou aqui, todas as alternativas falharam nesta tentativa
            if attempt < max_retries - 1:
                delay = random.uniform(3, 8) * (attempt + 1)
                logger.info(f"🔄 Tentativa {attempt + 1} falhou. Aguardando {delay:.1f}s...")
                time.sleep(delay)
        
        logger.error(f"❌ Todas as tentativas falharam para {url}")
        return None
    
    def extract_from_embed(self, instagram_url: str) -> Optional[Dict[str, str]]:
        """Tenta extrair dados usando a versão embed do Instagram"""
        
        try:
            parsed = urlparse(instagram_url)
            path = parsed.path.strip('/')
            
            if '/p/' in path:
                shortcode = path.split('/p/')[-1].split('/')[0]
                embed_url = f"https://www.instagram.com/p/{shortcode}/embed/"
                
                response = self.safe_request(embed_url, use_mobile=True)
                
                if response and response.status_code == 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extrair dados básicos do embed
                    result = {}
                    
                    # Título/Caption
                    title_elem = soup.find('title')
                    if title_elem:
                        result['title'] = title_elem.get_text().strip()
                    
                    # Meta description
                    meta_desc = soup.find('meta', {'name': 'description'})
                    if meta_desc:
                        result['description'] = meta_desc.get('content', '').strip()
                    
                    # Open Graph data
                    og_title = soup.find('meta', {'property': 'og:title'})
                    if og_title:
                        result['og_title'] = og_title.get('content', '').strip()
                    
                    og_desc = soup.find('meta', {'property': 'og:description'})
                    if og_desc:
                        result['og_description'] = og_desc.get('content', '').strip()
                    
                    return result if result else None
                    
        except Exception as e:
            logger.debug(f"Erro ao extrair do embed: {e}")
        
        return None
    
    def try_external_apis(self, instagram_url: str) -> Optional[Dict[str, str]]:
        """Tenta usar APIs externas para extrair dados do Instagram"""
        
        # Lista de APIs que podem extrair dados do Instagram
        external_apis = [
            self._try_oembed_api,
            self._try_instagram_basic_display,
            self._try_third_party_scrapers
        ]
        
        for api_method in external_apis:
            try:
                result = api_method(instagram_url)
                if result:
                    logger.info(f"✅ Sucesso com API externa: {api_method.__name__}")
                    return result
            except Exception as e:
                logger.debug(f"API externa {api_method.__name__} falhou: {e}")
                continue
        
        return None
    
    def _try_oembed_api(self, instagram_url: str) -> Optional[Dict[str, str]]:
        """Tenta usar a API oEmbed do Instagram"""
        try:
            oembed_url = f"https://api.instagram.com/oembed/?url={instagram_url}"
            
            response = self.session.get(
                oembed_url,
                headers=self.get_headers(),
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', ''),
                    'description': data.get('author_name', ''),
                    'html': data.get('html', ''),
                    'thumbnail_url': data.get('thumbnail_url', ''),
                    'provider': 'instagram_oembed'
                }
        except Exception as e:
            logger.debug(f"oEmbed API falhou: {e}")
        
        return None
    
    def _try_instagram_basic_display(self, instagram_url: str) -> Optional[Dict[str, str]]:
        """Placeholder para Instagram Basic Display API (requer token)"""
        # Esta API requer autenticação, então por enquanto retorna None
        # Pode ser implementada se houver tokens disponíveis
        return None
    
    def _try_third_party_scrapers(self, instagram_url: str) -> Optional[Dict[str, str]]:
        """Tenta usar scrapers de terceiros como fallback"""
        
        # Lista de serviços que podem extrair dados do Instagram
        scrapers = [
            f"https://www.instagram.com/p/{self._extract_shortcode(instagram_url)}/embed/",
            # Outros scrapers podem ser adicionados aqui
        ]
        
        for scraper_url in scrapers:
            try:
                response = self.safe_request(scraper_url, use_mobile=True)
                if response and response.status_code == 200:
                    return self._parse_embed_response(response.text)
            except Exception as e:
                logger.debug(f"Scraper {scraper_url} falhou: {e}")
                continue
        
        return None
    
    def _extract_shortcode(self, instagram_url: str) -> str:
        """Extrai shortcode de uma URL do Instagram"""
        parsed = urlparse(instagram_url)
        path = parsed.path.strip('/')
        
        if '/p/' in path:
            return path.split('/p/')[-1].split('/')[0]
        elif '/reel/' in path:
            return path.split('/reel/')[-1].split('/')[0]
        
        return ""
    
    def _parse_embed_response(self, html_content: str) -> Optional[Dict[str, str]]:
        """Parseia resposta HTML do embed para extrair dados"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            result = {}
            
            # Extrair dados do embed
            title_elem = soup.find('title')
            if title_elem:
                result['title'] = title_elem.get_text().strip()
            
            # Meta tags
            for meta in soup.find_all('meta'):
                if meta.get('property') == 'og:title':
                    result['og_title'] = meta.get('content', '').strip()
                elif meta.get('property') == 'og:description':
                    result['og_description'] = meta.get('content', '').strip()
                elif meta.get('name') == 'description':
                    result['description'] = meta.get('content', '').strip()
            
            return result if result else None
            
        except Exception as e:
            logger.debug(f"Erro ao parsear embed: {e}")
            return None
    
    def comprehensive_extract(self, instagram_url: str) -> Optional[Dict[str, str]]:
        """Método principal que tenta todas as estratégias disponíveis"""
        
        logger.info(f"🔍 Tentando extração abrangente para: {instagram_url}")
        
        # Estratégia 1: Requisição direta com bypass
        response = self.safe_request(instagram_url, max_retries=2)
        if response and response.status_code == 200:
            result = self._parse_embed_response(response.text)
            if result:
                result['extraction_method'] = 'direct_bypass'
                return result
        
        # Estratégia 2: Versão embed
        embed_result = self.extract_from_embed(instagram_url)
        if embed_result:
            embed_result['extraction_method'] = 'embed'
            return embed_result
        
        # Estratégia 3: APIs externas
        api_result = self.try_external_apis(instagram_url)
        if api_result:
            api_result['extraction_method'] = 'external_api'
            return api_result
        
        logger.warning(f"❌ Todas as estratégias falharam para: {instagram_url}")
        return None

# Instância global
instagram_bypass = InstagramBypass()