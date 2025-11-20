#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Sistema Avançado de Tratamento de Exceções
Sistema robusto para captura, análise e tratamento de exceções
"""

import sys
import traceback
import functools
import asyncio
import time
from typing import Dict, Any, Optional, Callable, Union, List, Type
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path

# Importar sistema de logging otimizado
try:
    from enhanced_logging_system import get_logger, log_performance
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    def log_performance(operation, duration, details=None):
        pass

class ExceptionSeverity(Enum):
    """Níveis de severidade das exceções"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ExceptionCategory(Enum):
    """Categorias de exceções"""
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "auth_error"
    PERMISSION_ERROR = "permission_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    DATA_ERROR = "data_error"
    FILE_ERROR = "file_error"
    SYSTEM_ERROR = "system_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class ExceptionInfo:
    """Informações detalhadas sobre uma exceção"""
    timestamp: str
    exception_type: str
    message: str
    severity: ExceptionSeverity
    category: ExceptionCategory
    function_name: str
    file_name: str
    line_number: int
    traceback_str: str
    context: Dict[str, Any]
    retry_count: int = 0
    resolved: bool = False

class EnhancedExceptionHandler:
    """Sistema Avançado de Tratamento de Exceções V2.0"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Arquivo de log de exceções
        self.exception_log_file = self.log_dir / "exceptions.json"
        
        # Mapeamento de exceções para categorias
        self.exception_mapping = {
            # Erros de API
            'requests.exceptions.HTTPError': ExceptionCategory.API_ERROR,
            'aiohttp.ClientResponseError': ExceptionCategory.API_ERROR,
            'openai.error.APIError': ExceptionCategory.API_ERROR,
            
            # Erros de rede
            'requests.exceptions.ConnectionError': ExceptionCategory.NETWORK_ERROR,
            'requests.exceptions.Timeout': ExceptionCategory.NETWORK_ERROR,
            'aiohttp.ClientConnectorError': ExceptionCategory.NETWORK_ERROR,
            'aiohttp.ServerTimeoutError': ExceptionCategory.NETWORK_ERROR,
            
            # Erros de autenticação
            'requests.exceptions.HTTPError_401': ExceptionCategory.AUTHENTICATION_ERROR,
            'openai.error.AuthenticationError': ExceptionCategory.AUTHENTICATION_ERROR,
            
            # Erros de permissão
            'requests.exceptions.HTTPError_403': ExceptionCategory.PERMISSION_ERROR,
            'PermissionError': ExceptionCategory.PERMISSION_ERROR,
            
            # Erros de rate limit
            'requests.exceptions.HTTPError_429': ExceptionCategory.RATE_LIMIT_ERROR,
            'openai.error.RateLimitError': ExceptionCategory.RATE_LIMIT_ERROR,
            
            # Erros de dados
            'json.JSONDecodeError': ExceptionCategory.DATA_ERROR,
            'ValueError': ExceptionCategory.DATA_ERROR,
            'KeyError': ExceptionCategory.DATA_ERROR,
            
            # Erros de arquivo
            'FileNotFoundError': ExceptionCategory.FILE_ERROR,
            'PermissionError': ExceptionCategory.FILE_ERROR,
            'OSError': ExceptionCategory.FILE_ERROR,
            
            # Erros de sistema
            'MemoryError': ExceptionCategory.SYSTEM_ERROR,
            'SystemError': ExceptionCategory.SYSTEM_ERROR,
        }
        
        # Mapeamento de severidade
        self.severity_mapping = {
            ExceptionCategory.SYSTEM_ERROR: ExceptionSeverity.CRITICAL,
            ExceptionCategory.AUTHENTICATION_ERROR: ExceptionSeverity.HIGH,
            ExceptionCategory.PERMISSION_ERROR: ExceptionSeverity.HIGH,
            ExceptionCategory.API_ERROR: ExceptionSeverity.MEDIUM,
            ExceptionCategory.NETWORK_ERROR: ExceptionSeverity.MEDIUM,
            ExceptionCategory.RATE_LIMIT_ERROR: ExceptionSeverity.MEDIUM,
            ExceptionCategory.DATA_ERROR: ExceptionSeverity.LOW,
            ExceptionCategory.FILE_ERROR: ExceptionSeverity.LOW,
            ExceptionCategory.UNKNOWN_ERROR: ExceptionSeverity.MEDIUM,
        }
        
        # Estratégias de retry
        self.retry_strategies = {
            ExceptionCategory.NETWORK_ERROR: {'max_retries': 3, 'delay': 2, 'backoff': 2},
            ExceptionCategory.RATE_LIMIT_ERROR: {'max_retries': 5, 'delay': 5, 'backoff': 2},
            ExceptionCategory.API_ERROR: {'max_retries': 2, 'delay': 1, 'backoff': 1.5},
        }
        
        # Contador de exceções
        self.exception_counts = {}
        
        logger.info("🛡️ Sistema Avançado de Tratamento de Exceções V2.0 inicializado")
    
    def categorize_exception(self, exception: Exception) -> ExceptionCategory:
        """Categoriza uma exceção"""
        exception_name = type(exception).__name__
        full_exception_name = f"{type(exception).__module__}.{exception_name}"
        
        # Verificar mapeamento específico
        if full_exception_name in self.exception_mapping:
            return self.exception_mapping[full_exception_name]
        
        # Verificar mapeamento por nome
        if exception_name in self.exception_mapping:
            return self.exception_mapping[exception_name]
        
        # Verificar por código de status HTTP
        if hasattr(exception, 'response') and hasattr(exception.response, 'status_code'):
            status_code = exception.response.status_code
            if status_code == 401:
                return ExceptionCategory.AUTHENTICATION_ERROR
            elif status_code == 403:
                return ExceptionCategory.PERMISSION_ERROR
            elif status_code == 429:
                return ExceptionCategory.RATE_LIMIT_ERROR
            elif 400 <= status_code < 500:
                return ExceptionCategory.API_ERROR
            elif 500 <= status_code < 600:
                return ExceptionCategory.API_ERROR
        
        return ExceptionCategory.UNKNOWN_ERROR
    
    def get_severity(self, category: ExceptionCategory) -> ExceptionSeverity:
        """Obtém severidade baseada na categoria"""
        return self.severity_mapping.get(category, ExceptionSeverity.MEDIUM)
    
    def create_exception_info(self, 
                            exception: Exception, 
                            context: Dict[str, Any] = None,
                            retry_count: int = 0) -> ExceptionInfo:
        """Cria informações detalhadas sobre uma exceção"""
        
        # Obter informações do traceback
        tb = traceback.extract_tb(exception.__traceback__)
        if tb:
            frame = tb[-1]
            function_name = frame.name
            file_name = frame.filename
            line_number = frame.lineno
        else:
            function_name = "unknown"
            file_name = "unknown"
            line_number = 0
        
        # Categorizar exceção
        category = self.categorize_exception(exception)
        severity = self.get_severity(category)
        
        # Criar informações
        exception_info = ExceptionInfo(
            timestamp=datetime.now().isoformat(),
            exception_type=type(exception).__name__,
            message=str(exception),
            severity=severity,
            category=category,
            function_name=function_name,
            file_name=file_name,
            line_number=line_number,
            traceback_str=traceback.format_exc(),
            context=context or {},
            retry_count=retry_count
        )
        
        return exception_info
    
    def log_exception(self, exception_info: ExceptionInfo):
        """Registra exceção no log"""
        
        # Incrementar contador
        key = f"{exception_info.category.value}_{exception_info.exception_type}"
        self.exception_counts[key] = self.exception_counts.get(key, 0) + 1
        
        # Log baseado na severidade
        if exception_info.severity == ExceptionSeverity.CRITICAL:
            logger.critical(f"🚨 CRÍTICO: {exception_info.exception_type} em {exception_info.function_name}: {exception_info.message}")
        elif exception_info.severity == ExceptionSeverity.HIGH:
            logger.error(f"❌ ALTO: {exception_info.exception_type} em {exception_info.function_name}: {exception_info.message}")
        elif exception_info.severity == ExceptionSeverity.MEDIUM:
            logger.warning(f"⚠️ MÉDIO: {exception_info.exception_type} em {exception_info.function_name}: {exception_info.message}")
        else:
            logger.info(f"ℹ️ BAIXO: {exception_info.exception_type} em {exception_info.function_name}: {exception_info.message}")
        
        # Salvar em arquivo JSON
        self._save_exception_to_file(exception_info)
    
    def _save_exception_to_file(self, exception_info: ExceptionInfo):
        """Salva exceção em arquivo JSON"""
        try:
            # Carregar exceções existentes
            exceptions = []
            if self.exception_log_file.exists():
                with open(self.exception_log_file, 'r', encoding='utf-8') as f:
                    exceptions = json.load(f)
            
            # Adicionar nova exceção
            exception_dict = asdict(exception_info)
            exception_dict['severity'] = exception_info.severity.value
            exception_dict['category'] = exception_info.category.value
            
            exceptions.append(exception_dict)
            
            # Manter apenas as últimas 1000 exceções
            if len(exceptions) > 1000:
                exceptions = exceptions[-1000:]
            
            # Salvar
            with open(self.exception_log_file, 'w', encoding='utf-8') as f:
                json.dump(exceptions, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar exceção em arquivo: {e}")
    
    def should_retry(self, exception_info: ExceptionInfo) -> bool:
        """Determina se deve tentar novamente"""
        category = exception_info.category
        
        if category not in self.retry_strategies:
            return False
        
        strategy = self.retry_strategies[category]
        return exception_info.retry_count < strategy['max_retries']
    
    def get_retry_delay(self, exception_info: ExceptionInfo) -> float:
        """Calcula delay para retry"""
        category = exception_info.category
        
        if category not in self.retry_strategies:
            return 1.0
        
        strategy = self.retry_strategies[category]
        base_delay = strategy['delay']
        backoff = strategy['backoff']
        
        return base_delay * (backoff ** exception_info.retry_count)
    
    def handle_exception(self, 
                        exception: Exception, 
                        context: Dict[str, Any] = None,
                        retry_count: int = 0) -> ExceptionInfo:
        """Trata uma exceção de forma completa"""
        
        # Criar informações da exceção
        exception_info = self.create_exception_info(exception, context, retry_count)
        
        # Registrar no log
        self.log_exception(exception_info)
        
        return exception_info
    
    def get_exception_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas das exceções"""
        total_exceptions = sum(self.exception_counts.values())
        
        stats = {
            'total_exceptions': total_exceptions,
            'exception_counts': self.exception_counts.copy(),
            'top_exceptions': sorted(
                self.exception_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        }
        
        return stats

# Instância global do handler
_exception_handler = None

def get_exception_handler() -> EnhancedExceptionHandler:
    """Obtém instância global do handler"""
    global _exception_handler
    if _exception_handler is None:
        _exception_handler = EnhancedExceptionHandler()
    return _exception_handler

# Decoradores para tratamento automático de exceções
def handle_exceptions(context: Dict[str, Any] = None, 
                     reraise: bool = True,
                     default_return: Any = None):
    """
    Decorator para tratamento automático de exceções
    
    Args:
        context: Contexto adicional para logging
        reraise: Se deve re-lançar a exceção após tratamento
        default_return: Valor padrão para retornar se não re-lançar
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = get_exception_handler()
                
                # Criar contexto
                func_context = {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys()),
                    **(context or {})
                }
                
                # Tratar exceção
                exception_info = handler.handle_exception(e, func_context)
                
                if reraise:
                    raise
                else:
                    return default_return
        
        return wrapper
    return decorator

def handle_async_exceptions(context: Dict[str, Any] = None, 
                           reraise: bool = True,
                           default_return: Any = None):
    """
    Decorator para tratamento automático de exceções em funções assíncronas
    
    Args:
        context: Contexto adicional para logging
        reraise: Se deve re-lançar a exceção após tratamento
        default_return: Valor padrão para retornar se não re-lançar
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                handler = get_exception_handler()
                
                # Criar contexto
                func_context = {
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys()),
                    'async': True,
                    **(context or {})
                }
                
                # Tratar exceção
                exception_info = handler.handle_exception(e, func_context)
                
                if reraise:
                    raise
                else:
                    return default_return
        
        return wrapper
    return decorator

def retry_on_exception(max_retries: int = 3, 
                      delay: float = 1.0, 
                      backoff: float = 2.0,
                      exceptions: tuple = (Exception,)):
    """
    Decorator para retry automático em caso de exceções
    
    Args:
        max_retries: Número máximo de tentativas
        delay: Delay inicial entre tentativas
        backoff: Multiplicador do delay
        exceptions: Tupla de exceções que devem gerar retry
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            handler = get_exception_handler()
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    # Criar contexto
                    func_context = {
                        'function': func.__name__,
                        'attempt': attempt + 1,
                        'max_retries': max_retries
                    }
                    
                    # Tratar exceção
                    exception_info = handler.handle_exception(e, func_context, attempt)
                    
                    if attempt < max_retries:
                        retry_delay = delay * (backoff ** attempt)
                        logger.info(f"🔄 Tentativa {attempt + 1}/{max_retries + 1} falhou, tentando novamente em {retry_delay}s")
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"❌ Todas as {max_retries + 1} tentativas falharam")
                        break
            
            # Re-lançar última exceção
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

def async_retry_on_exception(max_retries: int = 3, 
                            delay: float = 1.0, 
                            backoff: float = 2.0,
                            exceptions: tuple = (Exception,)):
    """
    Decorator para retry automático em funções assíncronas
    
    Args:
        max_retries: Número máximo de tentativas
        delay: Delay inicial entre tentativas
        backoff: Multiplicador do delay
        exceptions: Tupla de exceções que devem gerar retry
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            handler = get_exception_handler()
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    # Criar contexto
                    func_context = {
                        'function': func.__name__,
                        'attempt': attempt + 1,
                        'max_retries': max_retries,
                        'async': True
                    }
                    
                    # Tratar exceção
                    exception_info = handler.handle_exception(e, func_context, attempt)
                    
                    if attempt < max_retries:
                        retry_delay = delay * (backoff ** attempt)
                        logger.info(f"🔄 Tentativa {attempt + 1}/{max_retries + 1} falhou, tentando novamente em {retry_delay}s")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"❌ Todas as {max_retries + 1} tentativas falharam")
                        break
            
            # Re-lançar última exceção
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

# Funções de conveniência
def log_exception(exception: Exception, context: Dict[str, Any] = None):
    """Função de conveniência para registrar exceção"""
    handler = get_exception_handler()
    return handler.handle_exception(exception, context)

def get_exception_stats() -> Dict[str, Any]:
    """Função de conveniência para obter estatísticas"""
    handler = get_exception_handler()
    return handler.get_exception_stats()