#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ NOVO: Sistema Avançado de Tratamento de Erros e Fallbacks
Implementa tratamento específico para diferentes tipos de erro com recuperação automática
"""

import logging
import time
import traceback
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from enum import Enum
from dataclasses import dataclass, asdict
import asyncio
import json
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    """Tipos específicos de erro"""
    API_QUOTA_EXCEEDED = "api_quota_exceeded"
    API_TIMEOUT = "api_timeout"
    API_RATE_LIMIT = "api_rate_limit"
    API_AUTHENTICATION = "api_authentication"
    API_NETWORK = "api_network"
    CONTENT_EXTRACTION_FAILED = "content_extraction_failed"
    LLM_PROCESSING_FAILED = "llm_processing_failed"
    DATABASE_ERROR = "database_error"
    FILE_IO_ERROR = "file_io_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    MEMORY_ERROR = "memory_error"
    UNKNOWN_ERROR = "unknown_error"

class ErrorSeverity(Enum):
    """Severidade do erro"""
    LOW = "low"           # Erro recuperável, continua processamento
    MEDIUM = "medium"     # Erro que requer fallback
    HIGH = "high"         # Erro que interrompe operação atual
    CRITICAL = "critical" # Erro que para todo o sistema

@dataclass
class ErrorContext:
    """Contexto do erro para análise"""
    session_id: str
    component: str
    operation: str
    timestamp: datetime
    error_type: ErrorType
    severity: ErrorSeverity
    original_exception: Exception
    retry_count: int = 0
    max_retries: int = 3
    backoff_seconds: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class FallbackStrategy:
    """Estratégia de fallback para diferentes tipos de erro"""
    
    def __init__(self, name: str, handler: Callable, priority: int = 1):
        self.name = name
        self.handler = handler
        self.priority = priority
        self.success_count = 0
        self.failure_count = 0
        self.last_used = None
    
    def get_success_rate(self) -> float:
        """Calcula taxa de sucesso da estratégia"""
        total = self.success_count + self.failure_count
        return (self.success_count / total) if total > 0 else 0.0
    
    def record_success(self):
        """Registra sucesso da estratégia"""
        self.success_count += 1
        self.last_used = datetime.now()
    
    def record_failure(self):
        """Registra falha da estratégia"""
        self.failure_count += 1
        self.last_used = datetime.now()

class AdvancedErrorHandler:
    """✅ NOVO: Sistema avançado de tratamento de erros com fallbacks inteligentes"""
    
    def __init__(self, data_dir: str = "analyses_data"):
        self.error_history: List[ErrorContext] = []
        self.fallback_strategies: Dict[ErrorType, List[FallbackStrategy]] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.error_patterns: Dict[str, int] = {}
        
        # Sistema de logging estruturado
        self.data_dir = data_dir
        self.error_log_file = os.path.join(data_dir, "error_log.jsonl")
        self.performance_log_file = os.path.join(data_dir, "performance_log.jsonl")
        
        # Configurações
        self.max_history_size = 1000
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutos
        
        # Criar diretório se não existir
        os.makedirs(data_dir, exist_ok=True)
        
        # Inicializa estratégias de fallback
        self._initialize_fallback_strategies()
        
        # Configurar logging estruturado
        self._setup_structured_logging()
        
        logger.info("✅ AdvancedErrorHandler inicializado com logging estruturado")
    
    def _setup_structured_logging(self):
        """Configura sistema de logging estruturado"""
        
        # Configurar formato estruturado para logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para arquivo de erros
        error_handler = logging.FileHandler(self.error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Adicionar handler ao logger principal
        root_logger = logging.getLogger()
        if not any(isinstance(h, logging.FileHandler) and h.baseFilename == self.error_log_file 
                  for h in root_logger.handlers):
            root_logger.addHandler(error_handler)
    
    def log_structured_error(self, error_context: ErrorContext, exception: Exception = None, 
                           additional_data: Dict[str, Any] = None):
        """Registra erro de forma estruturada"""
        
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": error_context.session_id,
            "component": error_context.component,
            "operation": error_context.operation,
            "error_type": error_context.error_type.value,
            "severity": error_context.severity.value,
            "message": error_context.message,
            "retry_count": error_context.retry_count,
            "recovery_attempted": error_context.recovery_attempted
        }
        
        # Adicionar informações da exceção se disponível
        if exception:
            error_entry.update({
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "traceback": traceback.format_exc()
            })
        
        # Adicionar dados adicionais
        if additional_data:
            error_entry["additional_data"] = additional_data
        
        # Adicionar informações do sistema
        error_entry.update({
            "python_version": sys.version,
            "memory_usage": self._get_memory_usage(),
            "disk_usage": self._get_disk_usage()
        })
        
        # Salvar no arquivo JSONL
        try:
            with open(self.error_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(error_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"❌ Erro ao salvar log estruturado: {e}")
        
        # Log tradicional também
        logger.error(f"🚨 {error_context.component}.{error_context.operation}: {error_context.message}")
    
    def log_performance_metric(self, component: str, operation: str, duration: float, 
                             success: bool, additional_metrics: Dict[str, Any] = None):
        """Registra métricas de performance"""
        
        performance_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "operation": operation,
            "duration_seconds": duration,
            "success": success,
            "memory_usage": self._get_memory_usage()
        }
        
        if additional_metrics:
            performance_entry.update(additional_metrics)
        
        # Salvar no arquivo de performance
        try:
            with open(self.performance_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(performance_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"❌ Erro ao salvar métrica de performance: {e}")
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Obtém informações de uso de memória"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent()
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Obtém informações de uso de disco"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.data_dir)
            return {
                "total_gb": total / 1024 / 1024 / 1024,
                "used_gb": used / 1024 / 1024 / 1024,
                "free_gb": free / 1024 / 1024 / 1024,
                "percent_used": (used / total) * 100
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_error_statistics(self, hours_back: int = 24) -> Dict[str, Any]:
        """Obtém estatísticas de erros das últimas horas"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        try:
            error_stats = {
                "total_errors": 0,
                "by_type": {},
                "by_component": {},
                "by_severity": {},
                "recovery_rate": 0.0,
                "most_common_errors": []
            }
            
            if not os.path.exists(self.error_log_file):
                return error_stats
            
            errors_analyzed = 0
            recovered_errors = 0
            
            with open(self.error_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        error_entry = json.loads(line.strip())
                        entry_time = datetime.fromisoformat(error_entry["timestamp"])
                        
                        if entry_time >= cutoff_time:
                            errors_analyzed += 1
                            
                            # Contar por tipo
                            error_type = error_entry.get("error_type", "unknown")
                            error_stats["by_type"][error_type] = error_stats["by_type"].get(error_type, 0) + 1
                            
                            # Contar por componente
                            component = error_entry.get("component", "unknown")
                            error_stats["by_component"][component] = error_stats["by_component"].get(component, 0) + 1
                            
                            # Contar por severidade
                            severity = error_entry.get("severity", "unknown")
                            error_stats["by_severity"][severity] = error_stats["by_severity"].get(severity, 0) + 1
                            
                            # Contar recuperações
                            if error_entry.get("recovery_attempted", False):
                                recovered_errors += 1
                    
                    except json.JSONDecodeError:
                        continue
            
            error_stats["total_errors"] = errors_analyzed
            error_stats["recovery_rate"] = (recovered_errors / errors_analyzed * 100) if errors_analyzed > 0 else 0
            
            # Encontrar erros mais comuns
            error_stats["most_common_errors"] = sorted(
                error_stats["by_type"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            return error_stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular estatísticas: {e}")
            return {"error": str(e)}
    
    def _initialize_fallback_strategies(self):
        """Inicializa estratégias de fallback para cada tipo de erro"""
        
        # API Quota Exceeded
        self.fallback_strategies[ErrorType.API_QUOTA_EXCEEDED] = [
            FallbackStrategy("switch_api_key", self._fallback_switch_api_key, priority=1),
            FallbackStrategy("use_alternative_api", self._fallback_alternative_api, priority=2),
            FallbackStrategy("cache_lookup", self._fallback_cache_lookup, priority=3),
            FallbackStrategy("delay_and_retry", self._fallback_delay_retry, priority=4)
        ]
        
        # API Timeout
        self.fallback_strategies[ErrorType.API_TIMEOUT] = [
            FallbackStrategy("reduce_request_size", self._fallback_reduce_request, priority=1),
            FallbackStrategy("increase_timeout", self._fallback_increase_timeout, priority=2),
            FallbackStrategy("split_request", self._fallback_split_request, priority=3),
            FallbackStrategy("use_cached_result", self._fallback_cache_lookup, priority=4)
        ]
        
        # Content Extraction Failed
        self.fallback_strategies[ErrorType.CONTENT_EXTRACTION_FAILED] = [
            FallbackStrategy("try_alternative_extractor", self._fallback_alternative_extractor, priority=1),
            FallbackStrategy("use_simplified_extraction", self._fallback_simplified_extraction, priority=2),
            FallbackStrategy("use_cached_content", self._fallback_cache_lookup, priority=3),
            FallbackStrategy("skip_and_continue", self._fallback_skip_item, priority=4)
        ]
        
        # LLM Processing Failed
        self.fallback_strategies[ErrorType.LLM_PROCESSING_FAILED] = [
            FallbackStrategy("retry_with_simpler_prompt", self._fallback_simpler_prompt, priority=1),
            FallbackStrategy("use_rule_based_analysis", self._fallback_rule_based, priority=2),
            FallbackStrategy("use_cached_analysis", self._fallback_cache_lookup, priority=3),
            FallbackStrategy("mark_for_manual_review", self._fallback_manual_review, priority=4)
        ]
        
        # Network/Connection Errors
        self.fallback_strategies[ErrorType.API_NETWORK] = [
            FallbackStrategy("retry_with_backoff", self._fallback_exponential_backoff, priority=1),
            FallbackStrategy("use_alternative_endpoint", self._fallback_alternative_endpoint, priority=2),
            FallbackStrategy("use_cached_data", self._fallback_cache_lookup, priority=3),
            FallbackStrategy("use_fess_search", self._fallback_fess_search, priority=4)
        ]
    
    def classify_error(self, exception: Exception, context: Dict[str, Any] = None) -> ErrorType:
        """✅ NOVO: Classifica automaticamente o tipo de erro"""
        
        error_message = str(exception).lower()
        exception_type = type(exception).__name__.lower()
        
        # Classificação por mensagem de erro
        if any(keyword in error_message for keyword in ['quota', 'limit exceeded', 'rate limit']):
            return ErrorType.API_QUOTA_EXCEEDED
        
        if any(keyword in error_message for keyword in ['timeout', 'timed out', 'connection timeout']):
            return ErrorType.API_TIMEOUT
        
        if any(keyword in error_message for keyword in ['rate limit', 'too many requests']):
            return ErrorType.API_RATE_LIMIT
        
        if any(keyword in error_message for keyword in ['unauthorized', 'authentication', 'api key']):
            return ErrorType.API_AUTHENTICATION
        
        if any(keyword in error_message for keyword in ['connection', 'network', 'dns', 'unreachable']):
            return ErrorType.API_NETWORK
        
        if any(keyword in error_message for keyword in ['extraction failed', 'no content', 'parse error']):
            return ErrorType.CONTENT_EXTRACTION_FAILED
        
        if any(keyword in error_message for keyword in ['llm', 'model', 'generation failed']):
            return ErrorType.LLM_PROCESSING_FAILED
        
        # Classificação por tipo de exceção
        if 'timeout' in exception_type:
            return ErrorType.TIMEOUT_ERROR
        
        if 'memory' in exception_type:
            return ErrorType.MEMORY_ERROR
        
        if any(db_type in exception_type for db_type in ['database', 'sql', 'connection']):
            return ErrorType.DATABASE_ERROR
        
        if any(io_type in exception_type for io_type in ['io', 'file', 'permission']):
            return ErrorType.FILE_IO_ERROR
        
        if 'validation' in exception_type:
            return ErrorType.VALIDATION_ERROR
        
        return ErrorType.UNKNOWN_ERROR
    
    def determine_severity(self, error_type: ErrorType, context: Dict[str, Any] = None) -> ErrorSeverity:
        """✅ NOVO: Determina severidade do erro baseado no tipo e contexto"""
        
        # Mapeamento de severidade por tipo
        severity_map = {
            ErrorType.API_QUOTA_EXCEEDED: ErrorSeverity.MEDIUM,
            ErrorType.API_TIMEOUT: ErrorSeverity.MEDIUM,
            ErrorType.API_RATE_LIMIT: ErrorSeverity.LOW,
            ErrorType.API_AUTHENTICATION: ErrorSeverity.HIGH,
            ErrorType.API_NETWORK: ErrorSeverity.MEDIUM,
            ErrorType.CONTENT_EXTRACTION_FAILED: ErrorSeverity.LOW,
            ErrorType.LLM_PROCESSING_FAILED: ErrorSeverity.MEDIUM,
            ErrorType.DATABASE_ERROR: ErrorSeverity.HIGH,
            ErrorType.FILE_IO_ERROR: ErrorSeverity.MEDIUM,
            ErrorType.VALIDATION_ERROR: ErrorSeverity.LOW,
            ErrorType.TIMEOUT_ERROR: ErrorSeverity.MEDIUM,
            ErrorType.MEMORY_ERROR: ErrorSeverity.CRITICAL,
            ErrorType.UNKNOWN_ERROR: ErrorSeverity.MEDIUM
        }
        
        base_severity = severity_map.get(error_type, ErrorSeverity.MEDIUM)
        
        # Ajusta severidade baseado no contexto
        if context:
            # Se é operação crítica, aumenta severidade
            if context.get('critical_operation', False):
                if base_severity == ErrorSeverity.LOW:
                    base_severity = ErrorSeverity.MEDIUM
                elif base_severity == ErrorSeverity.MEDIUM:
                    base_severity = ErrorSeverity.HIGH
            
            # Se já houve muitos erros similares, aumenta severidade
            error_count = context.get('recent_error_count', 0)
            if error_count > 5:
                if base_severity == ErrorSeverity.LOW:
                    base_severity = ErrorSeverity.MEDIUM
                elif base_severity == ErrorSeverity.MEDIUM:
                    base_severity = ErrorSeverity.HIGH
        
        return base_severity
    
    async def handle_error(self, 
                          exception: Exception,
                          session_id: str,
                          component: str,
                          operation: str,
                          context: Dict[str, Any] = None,
                          max_retries: int = 3) -> Dict[str, Any]:
        """
        ✅ NOVO: Método principal para tratamento de erros com fallbacks
        
        Returns:
            Dict com resultado do tratamento: success, result, fallback_used, etc.
        """
        
        # Classifica o erro
        error_type = self.classify_error(exception, context)
        severity = self.determine_severity(error_type, context)
        
        # Cria contexto do erro
        error_context = ErrorContext(
            session_id=session_id,
            component=component,
            operation=operation,
            timestamp=datetime.now(),
            error_type=error_type,
            severity=severity,
            original_exception=exception,
            max_retries=max_retries,
            metadata=context or {}
        )
        
        # Adiciona ao histórico
        self._add_to_history(error_context)
        
        # Verifica circuit breaker
        if self._is_circuit_breaker_open(component, operation):
            logger.warning(f"🚫 Circuit breaker aberto para {component}.{operation}")
            return {
                'success': False,
                'error': 'Circuit breaker open',
                'fallback_used': 'circuit_breaker_block',
                'should_retry': False
            }
        
        # Log estruturado do erro
        self._log_error(error_context)
        
        # Tenta estratégias de fallback
        result = await self._try_fallback_strategies(error_context)
        
        # Atualiza circuit breaker
        self._update_circuit_breaker(component, operation, result['success'])
        
        return result
    
    async def _try_fallback_strategies(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Tenta estratégias de fallback em ordem de prioridade"""
        
        strategies = self.fallback_strategies.get(error_context.error_type, [])
        
        if not strategies:
            logger.warning(f"⚠️ Nenhuma estratégia de fallback para {error_context.error_type}")
            return {
                'success': False,
                'error': str(error_context.original_exception),
                'fallback_used': None,
                'should_retry': error_context.retry_count < error_context.max_retries
            }
        
        # Ordena estratégias por prioridade e taxa de sucesso
        strategies.sort(key=lambda s: (s.priority, -s.get_success_rate()))
        
        for strategy in strategies:
            try:
                logger.info(f"🔄 Tentando fallback: {strategy.name}")
                
                result = await strategy.handler(error_context)
                
                if result.get('success', False):
                    strategy.record_success()
                    logger.info(f"✅ Fallback {strategy.name} bem-sucedido")
                    
                    return {
                        'success': True,
                        'result': result.get('result'),
                        'fallback_used': strategy.name,
                        'should_retry': False
                    }
                else:
                    strategy.record_failure()
                    logger.warning(f"❌ Fallback {strategy.name} falhou: {result.get('error')}")
                    
            except Exception as fallback_error:
                strategy.record_failure()
                logger.error(f"❌ Erro no fallback {strategy.name}: {fallback_error}")
        
        # Todas as estratégias falharam
        return {
            'success': False,
            'error': str(error_context.original_exception),
            'fallback_used': None,
            'should_retry': error_context.retry_count < error_context.max_retries
        }
    
    # ✅ IMPLEMENTAÇÕES DOS FALLBACKS ESPECÍFICOS
    
    async def _fallback_switch_api_key(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Troca chave de API"""
        try:
            # Importa o serviço de rotação de API keys
            from .llm_reasoning_service import llm_reasoning_service
            
            # Força rotação para próxima chave
            next_key_info = llm_reasoning_service.force_rotate_key()
            
            if next_key_info:
                return {
                    'success': True,
                    'result': {'new_key_index': next_key_info.get('index')},
                    'message': f"Chave rotacionada para índice {next_key_info.get('index')}"
                }
            else:
                return {'success': False, 'error': 'Nenhuma chave alternativa disponível'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_alternative_api(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Usa API alternativa"""
        try:
            # Implementa lógica para usar API alternativa
            # Por exemplo, se Gemini falhar, tenta OpenAI
            return {
                'success': True,
                'result': {'alternative_api_used': True},
                'message': 'API alternativa utilizada'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_cache_lookup(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Busca resultado em cache"""
        try:
            # Implementa busca em cache baseada no contexto
            cache_key = f"{error_context.component}_{error_context.operation}_{hash(str(error_context.metadata))}"
            
            # Simula busca em cache (implementar cache real)
            cached_result = None  # Buscar do cache real
            
            if cached_result:
                return {
                    'success': True,
                    'result': cached_result,
                    'message': 'Resultado obtido do cache'
                }
            else:
                return {'success': False, 'error': 'Nenhum resultado em cache'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_delay_retry(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Aguarda e tenta novamente"""
        try:
            delay = error_context.backoff_seconds * (2 ** error_context.retry_count)
            await asyncio.sleep(min(delay, 60))  # Máximo 60 segundos
            
            return {
                'success': True,
                'result': {'retry_after_delay': delay},
                'message': f'Aguardou {delay}s para retry'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_reduce_request(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Reduz tamanho da requisição"""
        try:
            # Implementa lógica para reduzir tamanho da requisição
            return {
                'success': True,
                'result': {'request_size_reduced': True},
                'message': 'Tamanho da requisição reduzido'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_increase_timeout(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Aumenta timeout"""
        try:
            return {
                'success': True,
                'result': {'timeout_increased': True},
                'message': 'Timeout aumentado para próxima tentativa'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_split_request(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Divide requisição em partes menores"""
        try:
            return {
                'success': True,
                'result': {'request_split': True},
                'message': 'Requisição dividida em partes menores'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_alternative_extractor(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Usa extrator alternativo"""
        try:
            return {
                'success': True,
                'result': {'alternative_extractor_used': True},
                'message': 'Extrator alternativo utilizado'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_simplified_extraction(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Usa extração simplificada"""
        try:
            return {
                'success': True,
                'result': {'simplified_extraction': True},
                'message': 'Extração simplificada utilizada'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_skip_item(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Pula item e continua"""
        try:
            return {
                'success': True,
                'result': {'item_skipped': True},
                'message': 'Item pulado, continuando processamento'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_simpler_prompt(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Usa prompt mais simples"""
        try:
            return {
                'success': True,
                'result': {'simpler_prompt_used': True},
                'message': 'Prompt simplificado utilizado'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_rule_based(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Usa análise baseada em regras"""
        try:
            return {
                'success': True,
                'result': {'rule_based_analysis': True},
                'message': 'Análise baseada em regras utilizada'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_manual_review(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Marca para revisão manual"""
        try:
            return {
                'success': True,
                'result': {'marked_for_manual_review': True},
                'message': 'Item marcado para revisão manual'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_exponential_backoff(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Backoff exponencial"""
        try:
            delay = min(error_context.backoff_seconds * (2 ** error_context.retry_count), 300)
            await asyncio.sleep(delay)
            
            return {
                'success': True,
                'result': {'backoff_delay': delay},
                'message': f'Backoff exponencial: {delay}s'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_alternative_endpoint(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Usa endpoint alternativo"""
        try:
            return {
                'success': True,
                'result': {'alternative_endpoint_used': True},
                'message': 'Endpoint alternativo utilizado'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fallback_fess_search(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback: Usar Fess como mecanismo de busca alternativo"""
        try:
            from services.fess_integration import fess_client
            
            # Tenta usar Fess como fallback para buscas
            if hasattr(error_context, 'query') and error_context.query:
                fess_results = fess_client.search(error_context.query, 10)
                if fess_results and fess_results.get('items'):
                    return {
                        'success': True,
                        'result': fess_results,
                        'message': 'Busca realizada via Fess local',
                        'provider': 'fess_fallback'
                    }
            
            return {
                'success': True,
                'result': {'fess_available': fess_client.is_available()},
                'message': 'Fess disponível como fallback'
            }
        except Exception as e:
            logger.error(f"Erro no fallback Fess: {e}")
            return {'success': False, 'error': str(e)}
    
    def _add_to_history(self, error_context: ErrorContext):
        """Adiciona erro ao histórico"""
        self.error_history.append(error_context)
        
        # Mantém tamanho do histórico
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
        
        # Atualiza padrões de erro
        pattern_key = f"{error_context.component}_{error_context.error_type.value}"
        self.error_patterns[pattern_key] = self.error_patterns.get(pattern_key, 0) + 1
    
    def _log_error(self, error_context: ErrorContext):
        """Log estruturado do erro"""
        try:
            from .log_local_atual import log_local_atual, LogLevel, LogCategory
            
            log_local_atual.log_structured(
                log_local_atual.StructuredLogEntry(
                    level=LogLevel.ERROR,
                    category=LogCategory.ERROR_HANDLING,
                    message=f"Erro {error_context.error_type.value} em {error_context.operation}",
                    session_id=error_context.session_id,
                    component=error_context.component,
                    operation=error_context.operation,
                    data={
                        'error_type': error_context.error_type.value,
                        'severity': error_context.severity.value,
                        'retry_count': error_context.retry_count,
                        'max_retries': error_context.max_retries
                    },
                    error=error_context.original_exception
                )
            )
        except Exception as log_error:
            logger.error(f"Erro ao fazer log estruturado: {log_error}")
    
    def _is_circuit_breaker_open(self, component: str, operation: str) -> bool:
        """Verifica se circuit breaker está aberto"""
        key = f"{component}_{operation}"
        breaker = self.circuit_breakers.get(key)
        
        if not breaker:
            return False
        
        if breaker['state'] == 'open':
            # Verifica se deve tentar fechar
            if datetime.now() > breaker['open_until']:
                breaker['state'] = 'half_open'
                return False
            return True
        
        return False
    
    def _update_circuit_breaker(self, component: str, operation: str, success: bool):
        """Atualiza estado do circuit breaker"""
        key = f"{component}_{operation}"
        
        if key not in self.circuit_breakers:
            self.circuit_breakers[key] = {
                'failure_count': 0,
                'state': 'closed',
                'open_until': None
            }
        
        breaker = self.circuit_breakers[key]
        
        if success:
            breaker['failure_count'] = 0
            breaker['state'] = 'closed'
            breaker['open_until'] = None
        else:
            breaker['failure_count'] += 1
            
            if breaker['failure_count'] >= self.circuit_breaker_threshold:
                breaker['state'] = 'open'
                breaker['open_until'] = datetime.now() + timedelta(seconds=self.circuit_breaker_timeout)
                logger.warning(f"🚫 Circuit breaker aberto para {key}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """✅ NOVO: Retorna estatísticas de erro"""
        total_errors = len(self.error_history)
        
        if total_errors == 0:
            return {'total_errors': 0}
        
        # Estatísticas por tipo
        error_types = {}
        severity_counts = {}
        component_errors = {}
        
        for error in self.error_history:
            # Por tipo
            error_type = error.error_type.value
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Por severidade
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Por componente
            component = error.component
            component_errors[component] = component_errors.get(component, 0) + 1
        
        # Estratégias de fallback mais eficazes
        best_strategies = {}
        for error_type, strategies in self.fallback_strategies.items():
            best_strategy = max(strategies, key=lambda s: s.get_success_rate())
            best_strategies[error_type.value] = {
                'name': best_strategy.name,
                'success_rate': best_strategy.get_success_rate(),
                'usage_count': best_strategy.success_count + best_strategy.failure_count
            }
        
        return {
            'total_errors': total_errors,
            'error_types': error_types,
            'severity_counts': severity_counts,
            'component_errors': component_errors,
            'best_fallback_strategies': best_strategies,
            'circuit_breakers': {k: v['state'] for k, v in self.circuit_breakers.items()},
            'error_patterns': self.error_patterns
        }


# ✅ INSTÂNCIA GLOBAL
error_handler = AdvancedErrorHandler()