#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Timeout Handler
Gerenciador robusto de timeouts com retry e fallback
"""

import time
import logging
import asyncio
import requests
from typing import Any, Callable, Optional, Dict, List
from functools import wraps
import concurrent.futures
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class TimeoutConfig:
    """Configurações de timeout para diferentes operações"""
    
    # Timeouts para APIs externas - OTIMIZADOS
    API_TIMEOUT_SHORT = 15      # APIs rápidas (Jina, etc) - aumentado de 10s
    API_TIMEOUT_MEDIUM = 45     # APIs médias (Tavily, etc) - aumentado de 30s
    API_TIMEOUT_LONG = 90       # APIs lentas (Scraping, etc) - aumentado de 60s
    
    # Timeouts para operações internas - OTIMIZADOS
    ANALYSIS_TIMEOUT = 960      # Análises complexas - DOBRADO para 16 min (Etapa 1)
    SCRAPING_TIMEOUT = 60       # Web scraping - aumentado de 45s
    AI_GENERATION_TIMEOUT = 180 # Geração de IA - aumentado de 120s (3 min)
    
    # Configurações de retry
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    BACKOFF_MULTIPLIER = 2.0

class TimeoutHandler:
    """Gerenciador robusto de timeouts com retry automático"""
    
    def __init__(self, config: Optional[TimeoutConfig] = None):
        self.config = config or TimeoutConfig()
        self.logger = logging.getLogger(__name__)
    
    def with_timeout(self, timeout: float, max_retries: int = None, 
                    retry_delay: float = None, fallback_value: Any = None):
        """
        Decorator para adicionar timeout e retry a funções
        """
        max_retries = max_retries or self.config.MAX_RETRIES
        retry_delay = retry_delay or self.config.RETRY_DELAY
        
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        # Executa com timeout
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(func, *args, **kwargs)
                            try:
                                result = future.result(timeout=timeout)
                                if attempt > 0:
                                    self.logger.info(f"✅ Sucesso na tentativa {attempt + 1} para {func.__name__}")
                                return result
                            except concurrent.futures.TimeoutError:
                                future.cancel()
                                raise TimeoutError(f"Timeout de {timeout}s excedido para {func.__name__}")
                    
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries:
                            delay = retry_delay * (self.config.BACKOFF_MULTIPLIER ** attempt)
                            self.logger.warning(f"⚠️ Tentativa {attempt + 1} falhou para {func.__name__}: {e}. Tentando novamente em {delay}s...")
                            time.sleep(delay)
                        else:
                            self.logger.error(f"❌ Todas as tentativas falharam para {func.__name__}: {e}")
                
                # Se chegou aqui, todas as tentativas falharam
                if fallback_value is not None:
                    self.logger.info(f"🔄 Usando valor fallback para {func.__name__}")
                    return fallback_value
                
                raise last_exception
            
            return wrapper
        return decorator
    
    def safe_request(self, url: str, method: str = 'GET', timeout: float = None, 
                    max_retries: int = None, **kwargs) -> Optional[requests.Response]:
        """
        Faz requisição HTTP com timeout e retry robusto
        """
        timeout = timeout or self.config.API_TIMEOUT_MEDIUM
        max_retries = max_retries or self.config.MAX_RETRIES
        
        session = requests.Session()
        
        # Headers padrão para evitar bloqueios
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        headers = kwargs.get('headers', {})
        headers.update(default_headers)
        kwargs['headers'] = headers
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                response = session.request(
                    method=method,
                    url=url,
                    timeout=timeout,
                    **kwargs
                )
                
                if response.status_code == 200:
                    if attempt > 0:
                        self.logger.info(f"✅ Requisição bem-sucedida na tentativa {attempt + 1} para {url}")
                    return response
                elif response.status_code in [429, 503, 504]:
                    # Rate limit ou servidor sobrecarregado - retry
                    raise requests.exceptions.RequestException(f"Status {response.status_code}")
                else:
                    # Outros erros HTTP - não retry
                    self.logger.warning(f"⚠️ Status HTTP {response.status_code} para {url}")
                    return response
                    
            except (requests.exceptions.Timeout, 
                   requests.exceptions.ConnectionError,
                   requests.exceptions.RequestException) as e:
                last_exception = e
                
                if attempt < max_retries:
                    delay = self.config.RETRY_DELAY * (self.config.BACKOFF_MULTIPLIER ** attempt)
                    self.logger.warning(f"⚠️ Tentativa {attempt + 1} falhou para {url}: {e}. Tentando novamente em {delay}s...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"❌ Todas as tentativas falharam para {url}: {e}")
        
        return None
    
    async def async_with_timeout(self, coro, timeout: float, fallback_value: Any = None):
        """
        Executa corrotina com timeout
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.warning(f"⚠️ Timeout de {timeout}s excedido para operação async")
            if fallback_value is not None:
                return fallback_value
            raise
    
    @contextmanager
    def timeout_context(self, timeout: float, operation_name: str = "operação"):
        """
        Context manager para timeout
        """
        start_time = time.time()
        try:
            yield
        except Exception as e:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                self.logger.error(f"❌ Timeout de {timeout}s excedido para {operation_name}")
            raise
        else:
            elapsed = time.time() - start_time
            if elapsed > timeout * 0.8:  # Aviso se chegou perto do timeout
                self.logger.warning(f"⚠️ {operation_name} levou {elapsed:.1f}s (próximo do timeout de {timeout}s)")

# Instância global para uso fácil
timeout_handler = TimeoutHandler()

# Decorators prontos para uso
def api_timeout(timeout: float = TimeoutConfig.API_TIMEOUT_MEDIUM, **kwargs):
    """Decorator para APIs com timeout padrão"""
    return timeout_handler.with_timeout(timeout, **kwargs)

def analysis_timeout(timeout: float = TimeoutConfig.ANALYSIS_TIMEOUT, **kwargs):
    """Decorator para análises com timeout longo"""
    return timeout_handler.with_timeout(timeout, **kwargs)

def scraping_timeout(timeout: float = TimeoutConfig.SCRAPING_TIMEOUT, **kwargs):
    """Decorator para scraping com timeout médio"""
    return timeout_handler.with_timeout(timeout, **kwargs)

def ai_timeout(timeout: float = TimeoutConfig.AI_GENERATION_TIMEOUT, **kwargs):
    """Decorator para geração de IA com timeout"""
    return timeout_handler.with_timeout(timeout, **kwargs)