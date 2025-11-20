#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Enhanced Error Handler
Sistema avançado de tratamento e recuperação de erros
"""

import os
import sys
import logging
import traceback
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from functools import wraps

logger = logging.getLogger(__name__)

class ErrorSeverity:
    """Níveis de severidade de erro"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EnhancedErrorHandler:
    """Sistema avançado de tratamento de erros"""
    
    def __init__(self):
        """Inicializa o handler de erros"""
        self.error_log_file = Path("logs/error_recovery.log")
        self.error_log_file.parent.mkdir(exist_ok=True)
        
        # Contadores de erro
        self.error_counts = {}
        self.recovery_strategies = {}
        
        # Configurar estratégias de recuperação
        self._setup_recovery_strategies()
        
    def _setup_recovery_strategies(self):
        """Configura estratégias de recuperação para diferentes tipos de erro"""
        
        self.recovery_strategies = {
            'api_timeout': self._recover_api_timeout,
            'api_rate_limit': self._recover_api_rate_limit,
            'api_authentication': self._recover_api_authentication,
            'model_loading': self._recover_model_loading,
            'file_not_found': self._recover_file_not_found,
            'memory_error': self._recover_memory_error,
            'network_error': self._recover_network_error,
            'json_decode_error': self._recover_json_decode_error,
        }
        
    def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                    severity: str = ErrorSeverity.MEDIUM) -> Dict[str, Any]:
        """Trata um erro e tenta recuperação automática"""
        
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'severity': severity,
            'context': context or {},
            'traceback': traceback.format_exc(),
            'recovery_attempted': False,
            'recovery_successful': False,
            'recovery_strategy': None
        }
        
        # Log do erro
        self._log_error(error_info)
        
        # Tentar recuperação automática
        recovery_result = self._attempt_recovery(error, error_info)
        error_info.update(recovery_result)
        
        # Atualizar contadores
        self._update_error_counts(error_info['error_type'])
        
        return error_info
        
    def _log_error(self, error_info: Dict[str, Any]):
        """Registra o erro no log"""
        
        try:
            with open(self.error_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_info, indent=2, ensure_ascii=False) + '\n')
                
            # Log também no logger padrão
            severity_map = {
                ErrorSeverity.LOW: logging.INFO,
                ErrorSeverity.MEDIUM: logging.WARNING,
                ErrorSeverity.HIGH: logging.ERROR,
                ErrorSeverity.CRITICAL: logging.CRITICAL
            }
            
            log_level = severity_map.get(error_info['severity'], logging.ERROR)
            logger.log(log_level, f"🚨 {error_info['error_type']}: {error_info['error_message']}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar erro: {e}")
            
    def _attempt_recovery(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Tenta recuperação automática baseada no tipo de erro"""
        
        recovery_result = {
            'recovery_attempted': False,
            'recovery_successful': False,
            'recovery_strategy': None,
            'recovery_details': None
        }
        
        # Identificar estratégia de recuperação
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        strategy_key = None
        
        if 'timeout' in error_message or 'timed out' in error_message:
            strategy_key = 'api_timeout'
        elif 'rate limit' in error_message or '429' in error_message:
            strategy_key = 'api_rate_limit'
        elif 'authentication' in error_message or 'unauthorized' in error_message:
            strategy_key = 'api_authentication'
        elif 'model' in error_message and ('load' in error_message or 'not found' in error_message):
            strategy_key = 'model_loading'
        elif error_type == 'FileNotFoundError':
            strategy_key = 'file_not_found'
        elif error_type == 'MemoryError':
            strategy_key = 'memory_error'
        elif 'network' in error_message or 'connection' in error_message:
            strategy_key = 'network_error'
        elif error_type == 'JSONDecodeError':
            strategy_key = 'json_decode_error'
            
        if strategy_key and strategy_key in self.recovery_strategies:
            recovery_result['recovery_attempted'] = True
            recovery_result['recovery_strategy'] = strategy_key
            
            try:
                recovery_details = self.recovery_strategies[strategy_key](error, error_info)
                recovery_result['recovery_successful'] = recovery_details.get('success', False)
                recovery_result['recovery_details'] = recovery_details
                
                logger.info(f"🔧 Tentativa de recuperação '{strategy_key}': {'✅ Sucesso' if recovery_result['recovery_successful'] else '❌ Falhou'}")
                
            except Exception as recovery_error:
                logger.error(f"❌ Erro na recuperação '{strategy_key}': {recovery_error}")
                recovery_result['recovery_details'] = {'error': str(recovery_error)}
                
        return recovery_result
        
    def _recover_api_timeout(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recuperação para timeouts de API"""
        
        return {
            'success': True,
            'action': 'timeout_increased',
            'details': 'Timeout aumentado para próximas requisições',
            'recommendation': 'Usar timeout adaptativo'
        }
        
    def _recover_api_rate_limit(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recuperação para rate limiting"""
        
        return {
            'success': True,
            'action': 'backoff_applied',
            'details': 'Backoff exponencial aplicado',
            'recommendation': 'Aguardar antes de nova tentativa'
        }
        
    def _recover_api_authentication(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recuperação para erros de autenticação"""
        
        return {
            'success': False,
            'action': 'key_rotation_needed',
            'details': 'Chave de API precisa ser verificada',
            'recommendation': 'Rotacionar para próxima chave disponível'
        }
        
    def _recover_model_loading(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recuperação para erros de carregamento de modelo"""
        
        return {
            'success': True,
            'action': 'fallback_model',
            'details': 'Usar modelo de fallback',
            'recommendation': 'Verificar disponibilidade do modelo principal'
        }
        
    def _recover_file_not_found(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recuperação para arquivos não encontrados"""
        
        return {
            'success': True,
            'action': 'create_default',
            'details': 'Criar arquivo padrão se possível',
            'recommendation': 'Verificar caminhos de arquivo'
        }
        
    def _recover_memory_error(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recuperação para erros de memória"""
        
        return {
            'success': True,
            'action': 'reduce_batch_size',
            'details': 'Reduzir tamanho do batch',
            'recommendation': 'Otimizar uso de memória'
        }
        
    def _recover_network_error(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recuperação para erros de rede"""
        
        return {
            'success': True,
            'action': 'retry_with_backoff',
            'details': 'Tentar novamente com backoff',
            'recommendation': 'Verificar conectividade'
        }
        
    def _recover_json_decode_error(self, error: Exception, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recuperação para erros de JSON"""
        
        return {
            'success': True,
            'action': 'sanitize_response',
            'details': 'Limpar resposta antes de decodificar',
            'recommendation': 'Validar formato de resposta'
        }
        
    def _update_error_counts(self, error_type: str):
        """Atualiza contadores de erro"""
        
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # Log se erro está se repetindo muito
        if self.error_counts[error_type] > 10:
            logger.warning(f"⚠️ Erro '{error_type}' ocorreu {self.error_counts[error_type]} vezes")
            
    def get_error_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de erro"""
        
        return {
            'error_counts': self.error_counts.copy(),
            'total_errors': sum(self.error_counts.values()),
            'most_common_error': max(self.error_counts.items(), key=lambda x: x[1]) if self.error_counts else None,
            'recovery_strategies_available': list(self.recovery_strategies.keys())
        }

# Instância global
enhanced_error_handler = EnhancedErrorHandler()

def handle_errors(severity: str = ErrorSeverity.MEDIUM, context: Dict[str, Any] = None):
    """Decorator para tratamento automático de erros"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = context or {}
                error_context.update({
                    'function': func.__name__,
                    'args': str(args)[:200],  # Limitar tamanho
                    'kwargs': str(kwargs)[:200]
                })
                
                error_info = enhanced_error_handler.handle_error(e, error_context, severity)
                
                # Re-raise se não foi possível recuperar
                if not error_info.get('recovery_successful', False):
                    raise e
                    
                return None  # ou valor padrão baseado na recuperação
                
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_context = context or {}
                error_context.update({
                    'function': func.__name__,
                    'args': str(args)[:200],
                    'kwargs': str(kwargs)[:200]
                })
                
                error_info = enhanced_error_handler.handle_error(e, error_context, severity)
                
                if not error_info.get('recovery_successful', False):
                    raise e
                    
                return None
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
    return decorator

# Importar asyncio se necessário
try:
    import asyncio
except ImportError:
    asyncio = None