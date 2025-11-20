#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Cache Decorators
Decoradores para facilitar o uso do sistema de cache
"""

import functools
import asyncio
import time
from typing import Any, Callable, Optional, Union, Dict, List

# Importar sistema de cache
try:
    from intelligent_cache_system import cache_get, cache_put, cache_invalidate
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    def cache_get(key, prefix="", default=None):
        return default
    def cache_put(key, value, cache_type="default", ttl=None, prefix=""):
        return ""
    def cache_invalidate(key, prefix=""):
        return False

# Importar sistema de logging
try:
    from enhanced_logging_system import get_logger, log_performance
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    def log_performance(operation, duration, details=None):
        pass

def cached(cache_type: str = 'default', 
           ttl: Optional[int] = None,
           prefix: str = '',
           key_func: Optional[Callable] = None):
    """
    Decorator para cache automático de funções
    
    Args:
        cache_type: Tipo de cache para TTL apropriado
        ttl: TTL customizado em segundos
        prefix: Prefixo para as chaves de cache
        key_func: Função customizada para gerar chave (recebe args, kwargs)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not CACHE_AVAILABLE:
                return func(*args, **kwargs)
            
            start_time = time.time()
            
            # Gerar chave de cache
            if key_func:
                cache_key_data = key_func(*args, **kwargs)
            else:
                # Chave padrão baseada em argumentos
                cache_key_data = {
                    'func': func.__name__,
                    'args': args[:3] if len(args) > 3 else args,  # Limitar args
                    'kwargs': {k: v for k, v in kwargs.items() if k in ['query', 'url', 'model', 'prompt']}
                }
            
            # Tentar recuperar do cache
            cached_result = cache_get(cache_key_data, prefix=prefix)
            if cached_result is not None:
                duration = time.time() - start_time
                log_performance(f'{func.__name__}_cached', duration, {'cache_hit': True})
                logger.debug(f"✅ Cache hit para {func.__name__}")
                return cached_result
            
            # Executar função
            result = func(*args, **kwargs)
            
            # Salvar no cache
            if result is not None:
                cache_put(cache_key_data, result, cache_type, ttl, prefix)
                logger.debug(f"💾 Resultado de {func.__name__} salvo no cache")
            
            duration = time.time() - start_time
            log_performance(f'{func.__name__}_executed', duration, {'cache_hit': False})
            
            return result
        
        return wrapper
    return decorator

def async_cached(cache_type: str = 'default', 
                 ttl: Optional[int] = None,
                 prefix: str = '',
                 key_func: Optional[Callable] = None):
    """
    Decorator para cache automático de funções assíncronas
    
    Args:
        cache_type: Tipo de cache para TTL apropriado
        ttl: TTL customizado em segundos
        prefix: Prefixo para as chaves de cache
        key_func: Função customizada para gerar chave (recebe args, kwargs)
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not CACHE_AVAILABLE:
                return await func(*args, **kwargs)
            
            start_time = time.time()
            
            # Gerar chave de cache
            if key_func:
                cache_key_data = key_func(*args, **kwargs)
            else:
                # Chave padrão baseada em argumentos
                cache_key_data = {
                    'func': func.__name__,
                    'args': args[:3] if len(args) > 3 else args,  # Limitar args
                    'kwargs': {k: v for k, v in kwargs.items() if k in ['query', 'url', 'model', 'prompt']}
                }
            
            # Tentar recuperar do cache
            cached_result = cache_get(cache_key_data, prefix=prefix)
            if cached_result is not None:
                duration = time.time() - start_time
                log_performance(f'{func.__name__}_cached', duration, {'cache_hit': True})
                logger.debug(f"✅ Cache hit para {func.__name__}")
                return cached_result
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Salvar no cache
            if result is not None:
                cache_put(cache_key_data, result, cache_type, ttl, prefix)
                logger.debug(f"💾 Resultado de {func.__name__} salvo no cache")
            
            duration = time.time() - start_time
            log_performance(f'{func.__name__}_executed', duration, {'cache_hit': False})
            
            return result
        
        return wrapper
    return decorator

def cache_search_results(ttl: int = 3600):
    """Decorator específico para resultados de busca"""
    return cached(cache_type='search_results', ttl=ttl, prefix='search')

def cache_api_response(ttl: int = 1800):
    """Decorator específico para respostas de API"""
    return async_cached(cache_type='api_response', ttl=ttl, prefix='api')

def cache_file_content(ttl: int = 7200):
    """Decorator específico para conteúdo de arquivos"""
    return cached(cache_type='file_content', ttl=ttl, prefix='file')

def cache_metadata(ttl: int = 86400):
    """Decorator específico para metadados"""
    return cached(cache_type='metadata', ttl=ttl, prefix='meta')

def cache_temporary(ttl: int = 300):
    """Decorator específico para dados temporários"""
    return cached(cache_type='temporary', ttl=ttl, prefix='temp')

# Funções de utilidade para invalidação de cache
def invalidate_search_cache(query: str):
    """Invalida cache de busca específico"""
    if CACHE_AVAILABLE:
        cache_key_data = {'query': query}
        return cache_invalidate(cache_key_data, prefix='search')
    return False

def invalidate_api_cache(endpoint: str, params: Dict = None):
    """Invalida cache de API específico"""
    if CACHE_AVAILABLE:
        cache_key_data = {'endpoint': endpoint, 'params': params or {}}
        return cache_invalidate(cache_key_data, prefix='api')
    return False

def invalidate_file_cache(file_path: str):
    """Invalida cache de arquivo específico"""
    if CACHE_AVAILABLE:
        cache_key_data = {'file_path': file_path}
        return cache_invalidate(cache_key_data, prefix='file')
    return False

# Exemplo de uso personalizado
def search_key_generator(query: str, limit: int = 10, **kwargs):
    """Gerador de chave personalizado para buscas"""
    return {
        'query': query[:100],  # Limitar tamanho
        'limit': limit,
        'filters': {k: v for k, v in kwargs.items() if k in ['date_range', 'source', 'language']}
    }

def api_key_generator(endpoint: str, data: Dict = None, **kwargs):
    """Gerador de chave personalizado para APIs"""
    return {
        'endpoint': endpoint,
        'data_hash': hash(str(sorted((data or {}).items()))),
        'params': {k: v for k, v in kwargs.items() if k in ['model', 'temperature', 'max_tokens']}
    }

# Decoradores com geradores de chave personalizados
def cache_search_with_key(ttl: int = 3600):
    """Cache de busca com gerador de chave personalizado"""
    return cached(
        cache_type='search_results', 
        ttl=ttl, 
        prefix='search',
        key_func=lambda query, **kwargs: search_key_generator(query, **kwargs)
    )

def cache_api_with_key(ttl: int = 1800):
    """Cache de API com gerador de chave personalizado"""
    return async_cached(
        cache_type='api_response', 
        ttl=ttl, 
        prefix='api',
        key_func=lambda endpoint, data=None, **kwargs: api_key_generator(endpoint, data, **kwargs)
    )