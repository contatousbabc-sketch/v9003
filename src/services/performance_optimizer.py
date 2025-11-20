#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Otimização de Performance
Otimiza performance do sistema reduzindo tentativas desnecessárias e melhorando processamento
"""

import os
import time
import asyncio
import threading
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from functools import wraps, lru_cache
import weakref

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Métrica de performance"""
    operation: str
    duration: float
    success: bool
    timestamp: datetime
    memory_usage: float
    cpu_usage: float

class PerformanceOptimizer:
    """Sistema de otimização de performance"""
    
    def __init__(self, data_dir: str = "analyses_data"):
        self.data_dir = data_dir
        self.metrics_file = os.path.join(data_dir, "performance_metrics.json")
        
        # Cache inteligente
        self.operation_cache = {}
        self.cache_ttl = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Pool de threads otimizado
        self.max_workers = min(32, (os.cpu_count() or 1) + 4)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Métricas de performance
        self.performance_metrics: List[PerformanceMetric] = []
        self.operation_stats = {}
        
        # Configurações de otimização
        self.enable_caching = True
        self.enable_parallel_processing = True
        self.enable_request_batching = True
        self.batch_size = 10
        self.batch_timeout = 2.0  # segundos
        
        # Batching de requisições
        self.pending_batches = {}
        self.batch_locks = {}
        
        # Weak references para evitar vazamentos de memória
        self.weak_refs = weakref.WeakSet()
        
        os.makedirs(data_dir, exist_ok=True)
        
        logger.info("⚡ Sistema de Otimização de Performance inicializado")
    
    def performance_monitor(self, operation_name: str):
        """Decorator para monitorar performance de operações"""
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = self._get_memory_usage()
                success = False
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    logger.error(f"❌ Erro em {operation_name}: {e}")
                    raise
                finally:
                    duration = time.time() - start_time
                    end_memory = self._get_memory_usage()
                    
                    # Registrar métrica
                    metric = PerformanceMetric(
                        operation=operation_name,
                        duration=duration,
                        success=success,
                        timestamp=datetime.now(),
                        memory_usage=end_memory - start_memory,
                        cpu_usage=0.0  # Placeholder
                    )
                    
                    self._record_metric(metric)
                    
                    # Log se operação for lenta
                    if duration > 5.0:
                        logger.warning(f"⚠️ Operação lenta: {operation_name} ({duration:.2f}s)")
            
            return wrapper
        return decorator
    
    def cached_operation(self, cache_key: str, ttl: int = 300):
        """Decorator para cache de operações"""
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enable_caching:
                    return func(*args, **kwargs)
                
                # Verificar cache
                if cache_key in self.operation_cache:
                    if cache_key in self.cache_ttl:
                        if time.time() - self.cache_ttl[cache_key] < ttl:
                            self.cache_hits += 1
                            logger.debug(f"💾 Cache hit: {cache_key}")
                            return self.operation_cache[cache_key]
                        else:
                            # Cache expirado
                            del self.operation_cache[cache_key]
                            del self.cache_ttl[cache_key]
                
                # Executar operação
                self.cache_misses += 1
                result = func(*args, **kwargs)
                
                # Armazenar no cache
                self.operation_cache[cache_key] = result
                self.cache_ttl[cache_key] = time.time()
                
                logger.debug(f"💾 Cache miss: {cache_key}")
                return result
            
            return wrapper
        return decorator
    
    def batch_requests(self, batch_key: str, batch_size: int = None, timeout: float = None):
        """Decorator para agrupar requisições em lotes"""
        
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.enable_request_batching:
                    return await func(*args, **kwargs)
                
                batch_size_used = batch_size or self.batch_size
                timeout_used = timeout or self.batch_timeout
                
                # Inicializar batch se não existir
                if batch_key not in self.pending_batches:
                    self.pending_batches[batch_key] = []
                    self.batch_locks[batch_key] = asyncio.Lock()
                
                async with self.batch_locks[batch_key]:
                    # Adicionar requisição ao batch
                    future = asyncio.Future()
                    self.pending_batches[batch_key].append({
                        'args': args,
                        'kwargs': kwargs,
                        'future': future
                    })
                    
                    # Se batch está cheio ou timeout, processar
                    if len(self.pending_batches[batch_key]) >= batch_size_used:
                        await self._process_batch(batch_key, func)
                    else:
                        # Agendar processamento por timeout
                        asyncio.create_task(self._process_batch_timeout(batch_key, func, timeout_used))
                    
                    return await future
            
            return wrapper
        return decorator
    
    async def _process_batch(self, batch_key: str, func: Callable):
        """Processa um lote de requisições"""
        
        if batch_key not in self.pending_batches or not self.pending_batches[batch_key]:
            return
        
        batch = self.pending_batches[batch_key]
        self.pending_batches[batch_key] = []
        
        logger.debug(f"📦 Processando lote de {len(batch)} requisições: {batch_key}")
        
        # Processar requisições em paralelo
        tasks = []
        for item in batch:
            task = asyncio.create_task(self._execute_batched_request(func, item))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_batch_timeout(self, batch_key: str, func: Callable, timeout: float):
        """Processa lote por timeout"""
        
        await asyncio.sleep(timeout)
        
        if batch_key in self.batch_locks:
            async with self.batch_locks[batch_key]:
                await self._process_batch(batch_key, func)
    
    async def _execute_batched_request(self, func: Callable, item: Dict[str, Any]):
        """Executa uma requisição do lote"""
        
        try:
            result = await func(*item['args'], **item['kwargs'])
            item['future'].set_result(result)
        except Exception as e:
            item['future'].set_exception(e)
    
    def parallel_execute(self, operations: List[Callable], max_workers: int = None) -> List[Any]:
        """Executa operações em paralelo"""
        
        if not self.enable_parallel_processing:
            return [op() for op in operations]
        
        workers = max_workers or min(len(operations), self.max_workers)
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(op) for op in operations]
            results = []
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"❌ Erro na execução paralela: {e}")
                    results.append(None)
            
            return results
    
    def optimize_api_calls(self, api_calls: List[Dict[str, Any]]) -> List[Any]:
        """Otimiza chamadas de API agrupando por provedor"""
        
        # Agrupar por provedor
        provider_groups = {}
        for call in api_calls:
            provider = call.get('provider', 'unknown')
            if provider not in provider_groups:
                provider_groups[provider] = []
            provider_groups[provider].append(call)
        
        # Executar grupos em paralelo
        results = []
        
        def execute_provider_group(provider, calls):
            provider_results = []
            for call in calls:
                try:
                    # Simular execução da chamada
                    result = self._execute_api_call(call)
                    provider_results.append(result)
                except Exception as e:
                    logger.error(f"❌ Erro na chamada API {provider}: {e}")
                    provider_results.append(None)
            return provider_results
        
        # Executar grupos em paralelo
        group_operations = [
            lambda p=provider, c=calls: execute_provider_group(p, c)
            for provider, calls in provider_groups.items()
        ]
        
        group_results = self.parallel_execute(group_operations)
        
        # Flatten results
        for group_result in group_results:
            if group_result:
                results.extend(group_result)
        
        return results
    
    def _execute_api_call(self, call_config: Dict[str, Any]) -> Any:
        """Executa uma chamada de API (placeholder)"""
        
        # Implementação específica seria feita aqui
        # Por enquanto, simular delay
        time.sleep(0.1)
        return {"status": "success", "data": "mock_data"}
    
    def smart_retry(self, max_retries: int = 3, backoff_factor: float = 1.5):
        """Decorator para retry inteligente com backoff exponencial"""
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        
                        if attempt < max_retries:
                            delay = backoff_factor ** attempt
                            logger.warning(f"⚠️ Tentativa {attempt + 1} falhou, tentando novamente em {delay:.1f}s")
                            time.sleep(delay)
                        else:
                            logger.error(f"❌ Todas as {max_retries + 1} tentativas falharam")
                
                raise last_exception
            
            return wrapper
        return decorator
    
    def memory_efficient_processing(self, data_chunks: List[Any], chunk_processor: Callable) -> List[Any]:
        """Processa dados em chunks para economizar memória"""
        
        results = []
        
        for i, chunk in enumerate(data_chunks):
            logger.debug(f"📊 Processando chunk {i + 1}/{len(data_chunks)}")
            
            try:
                chunk_result = chunk_processor(chunk)
                results.append(chunk_result)
                
                # Forçar garbage collection periodicamente
                if i % 10 == 0:
                    import gc
                    gc.collect()
                    
            except Exception as e:
                logger.error(f"❌ Erro ao processar chunk {i}: {e}")
                results.append(None)
        
        return results
    
    def _record_metric(self, metric: PerformanceMetric):
        """Registra métrica de performance"""
        
        self.performance_metrics.append(metric)
        
        # Manter apenas as últimas 1000 métricas
        if len(self.performance_metrics) > 1000:
            self.performance_metrics = self.performance_metrics[-1000:]
        
        # Atualizar estatísticas
        if metric.operation not in self.operation_stats:
            self.operation_stats[metric.operation] = {
                'count': 0,
                'total_duration': 0,
                'success_count': 0,
                'avg_duration': 0,
                'success_rate': 0
            }
        
        stats = self.operation_stats[metric.operation]
        stats['count'] += 1
        stats['total_duration'] += metric.duration
        
        if metric.success:
            stats['success_count'] += 1
        
        stats['avg_duration'] = stats['total_duration'] / stats['count']
        stats['success_rate'] = stats['success_count'] / stats['count']
    
    def _get_memory_usage(self) -> float:
        """Obtém uso atual de memória"""
        
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gera relatório de performance"""
        
        if not self.performance_metrics:
            return {"error": "Nenhuma métrica disponível"}
        
        # Calcular estatísticas gerais
        total_operations = len(self.performance_metrics)
        successful_operations = sum(1 for m in self.performance_metrics if m.success)
        
        avg_duration = sum(m.duration for m in self.performance_metrics) / total_operations
        
        # Top operações mais lentas
        slowest_operations = sorted(
            self.operation_stats.items(),
            key=lambda x: x[1]['avg_duration'],
            reverse=True
        )[:5]
        
        # Cache statistics
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_cache_requests * 100) if total_cache_requests > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'general_stats': {
                'total_operations': total_operations,
                'successful_operations': successful_operations,
                'success_rate': (successful_operations / total_operations * 100) if total_operations > 0 else 0,
                'avg_duration': avg_duration
            },
            'cache_stats': {
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'hit_rate_percent': cache_hit_rate,
                'cached_operations': len(self.operation_cache)
            },
            'slowest_operations': slowest_operations,
            'operation_stats': dict(self.operation_stats),
            'optimization_settings': {
                'caching_enabled': self.enable_caching,
                'parallel_processing_enabled': self.enable_parallel_processing,
                'request_batching_enabled': self.enable_request_batching,
                'max_workers': self.max_workers,
                'batch_size': self.batch_size
            }
        }
    
    def optimize_system_settings(self):
        """Otimiza configurações do sistema baseado nas métricas"""
        
        if not self.operation_stats:
            return
        
        # Analisar operações lentas
        slow_operations = [
            op for op, stats in self.operation_stats.items()
            if stats['avg_duration'] > 5.0
        ]
        
        if slow_operations:
            logger.info(f"🔧 Detectadas {len(slow_operations)} operações lentas")
            
            # Aumentar cache TTL para operações lentas
            for op in slow_operations:
                cache_key = f"slow_op_{op}"
                if cache_key not in self.cache_ttl:
                    logger.info(f"⚡ Aumentando cache TTL para operação lenta: {op}")
        
        # Ajustar tamanho do batch baseado na performance
        if self.enable_request_batching:
            avg_batch_performance = sum(
                stats['avg_duration'] for stats in self.operation_stats.values()
            ) / len(self.operation_stats)
            
            if avg_batch_performance > 3.0 and self.batch_size > 5:
                self.batch_size = max(5, self.batch_size - 2)
                logger.info(f"🔧 Reduzindo batch size para {self.batch_size}")
            elif avg_batch_performance < 1.0 and self.batch_size < 20:
                self.batch_size = min(20, self.batch_size + 2)
                logger.info(f"🔧 Aumentando batch size para {self.batch_size}")
    
    def clear_cache(self):
        """Limpa cache para liberar memória"""
        
        cleared_items = len(self.operation_cache)
        self.operation_cache.clear()
        self.cache_ttl.clear()
        
        logger.info(f"🧹 Cache limpo: {cleared_items} itens removidos")
    
    def cleanup_expired_cache(self):
        """Remove itens expirados do cache"""
        
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in self.cache_ttl.items():
            if current_time - timestamp > 300:  # 5 minutos
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in self.operation_cache:
                del self.operation_cache[key]
            del self.cache_ttl[key]
        
        if expired_keys:
            logger.debug(f"🧹 Removidos {len(expired_keys)} itens expirados do cache")
    
    def shutdown(self):
        """Finaliza o otimizador de performance"""
        
        logger.info("🔄 Finalizando otimizador de performance...")
        
        # Finalizar thread pool
        self.thread_pool.shutdown(wait=True)
        
        # Salvar métricas finais
        try:
            report = self.get_performance_report()
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar métricas finais: {e}")
        
        logger.info("✅ Otimizador de performance finalizado")

# Instância global
performance_optimizer = PerformanceOptimizer()