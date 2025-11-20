#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Otimizador de Performance
Sistema avançado de otimização de performance para requisições HTTP
"""

import asyncio
import aiohttp
import time
import gzip
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from pathlib import Path
import statistics
import functools

# Importar sistema de logging
try:
    from enhanced_logging_system import get_logger, log_performance
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    def log_performance(operation, duration, details=None):
        pass

# Importar sistema de cache
try:
    from intelligent_cache_system import cache_get, cache_put
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    def cache_get(key, prefix="", default=None):
        return default
    def cache_put(key, value, cache_type="default", ttl=None, prefix=""):
        return ""

@dataclass
class PerformanceMetrics:
    """Métricas de performance de uma requisição"""
    timestamp: str
    url: str
    method: str
    duration: float
    status_code: int
    response_size: int
    compressed: bool
    cached: bool
    retries: int
    error: Optional[str] = None

@dataclass
class ConnectionPoolStats:
    """Estatísticas do pool de conexões"""
    total_connections: int
    active_connections: int
    idle_connections: int
    reused_connections: int
    created_connections: int
    closed_connections: int

class PerformanceOptimizer:
    """Sistema Avançado de Otimização de Performance V2.0"""
    
    def __init__(self, 
                 max_connections: int = 100,
                 max_connections_per_host: int = 30,
                 connection_timeout: float = 30.0,
                 read_timeout: float = 60.0,
                 enable_compression: bool = True,
                 enable_keep_alive: bool = True,
                 metrics_window: int = 1000):
        
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        self.connection_timeout = connection_timeout
        self.read_timeout = read_timeout
        self.enable_compression = enable_compression
        self.enable_keep_alive = enable_keep_alive
        self.metrics_window = metrics_window
        
        # Pool de conexões
        self._connector = None
        self._session = None
        
        # Métricas de performance
        self.metrics_history = deque(maxlen=metrics_window)
        self.host_metrics = defaultdict(lambda: deque(maxlen=100))
        
        # Estatísticas de conexão
        self.connection_stats = ConnectionPoolStats(0, 0, 0, 0, 0, 0)
        
        # Timeouts adaptativos por host
        self.adaptive_timeouts = defaultdict(lambda: {'timeout': read_timeout, 'samples': deque(maxlen=10)})
        
        # Headers otimizados
        self.optimized_headers = {
            'User-Agent': 'ARQV18-Enhanced/3.0 (Performance-Optimized)',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive' if enable_keep_alive else 'close',
        }
        
        if enable_compression:
            self.optimized_headers['Accept-Encoding'] = 'gzip, deflate, br'
        
        logger.info("🚀 Sistema Avançado de Otimização de Performance V2.0 inicializado")
        logger.info(f"📊 Configuração: {max_connections} conexões, timeout {read_timeout}s, compressão {enable_compression}")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self._initialize_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self._close_session()
    
    async def _initialize_session(self):
        """Inicializa sessão HTTP otimizada"""
        if self._session is None:
            # Configurar connector com otimizações
            connector_kwargs = {
                'limit': self.max_connections,
                'limit_per_host': self.max_connections_per_host,
                'ttl_dns_cache': 300,  # Cache DNS por 5 minutos
                'use_dns_cache': True,
                'keepalive_timeout': 30,
                'enable_cleanup_closed': True,
            }
            
            if self.enable_keep_alive:
                connector_kwargs['force_close'] = False
                connector_kwargs['keepalive_timeout'] = 60
            
            self._connector = aiohttp.TCPConnector(**connector_kwargs)
            
            # Configurar timeout
            timeout = aiohttp.ClientTimeout(
                total=float(self.connection_timeout + self.read_timeout),
                connect=float(self.connection_timeout),
                sock_read=float(self.read_timeout)
            )
            
            # Criar sessão
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                timeout=timeout,
                headers=self.optimized_headers,
                auto_decompress=self.enable_compression,
                raise_for_status=False
            )
            
            logger.info("🔗 Sessão HTTP otimizada inicializada")
    
    async def _close_session(self):
        """Fecha sessão HTTP"""
        if self._session:
            await self._session.close()
            self._session = None
        
        if self._connector:
            await self._connector.close()
            self._connector = None
        
        logger.info("🔒 Sessão HTTP fechada")
    
    def _get_adaptive_timeout(self, host: str) -> float:
        """Obtém timeout adaptativo para um host"""
        try:
            host_data = self.adaptive_timeouts[host]
            
            if len(host_data['samples']) < 3:
                return float(host_data['timeout'])
            
            # Calcular timeout baseado na média + 2 desvios padrão
            samples = list(host_data['samples'])
            if not samples:
                return float(self.read_timeout)
                
            mean_time = statistics.mean(samples)
            std_dev = statistics.stdev(samples) if len(samples) > 1 else 0
            
            adaptive_timeout = mean_time + (2 * std_dev)
            
            # Limitar entre 5s e 120s
            adaptive_timeout = max(5.0, min(120.0, adaptive_timeout))
            
            host_data['timeout'] = adaptive_timeout
            return float(adaptive_timeout)
        except Exception as e:
            logger.warning(f"⚠️ Erro ao calcular timeout adaptativo para {host}: {e}")
            return float(self.read_timeout)
    
    def _update_adaptive_timeout(self, host: str, duration: float):
        """Atualiza timeout adaptativo baseado na duração"""
        self.adaptive_timeouts[host]['samples'].append(duration)
    
    def _compress_data(self, data: Union[str, bytes, dict]) -> bytes:
        """Comprime dados para envio"""
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return gzip.compress(data)
    
    def _should_compress_request(self, data: Any, threshold: int = 1024) -> bool:
        """Determina se deve comprimir a requisição"""
        if not self.enable_compression or not data:
            return False
        
        # Estimar tamanho dos dados
        if isinstance(data, dict):
            size = len(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        elif isinstance(data, str):
            size = len(data.encode('utf-8'))
        elif isinstance(data, bytes):
            size = len(data)
        else:
            return False
        
        return size > threshold
    
    async def optimized_request(self,
                              method: str,
                              url: str,
                              headers: Optional[Dict[str, str]] = None,
                              data: Any = None,
                              json_data: Optional[Dict] = None,
                              params: Optional[Dict] = None,
                              use_cache: bool = True,
                              cache_ttl: int = 300) -> Tuple[int, Dict[str, Any], str]:
        """
        Executa requisição HTTP otimizada
        
        Returns:
            Tuple[status_code, headers, response_text]
        """
        start_time = time.time()
        
        # Extrair host da URL
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            host = parsed_url.netloc
        except Exception:
            host = 'unknown'
        
        # Verificar cache primeiro
        cache_key = f"{method}_{url}_{hash(str(params))}"
        if use_cache and CACHE_AVAILABLE and method.upper() == 'GET':
            cached_response = cache_get(cache_key, prefix="http_request")
            if cached_response:
                duration = time.time() - start_time
                
                # Registrar métrica de cache hit
                metric = PerformanceMetrics(
                    timestamp=datetime.now().isoformat(),
                    url=url,
                    method=method,
                    duration=duration,
                    status_code=cached_response.get('status_code', 200),
                    response_size=len(str(cached_response.get('data', ''))),
                    compressed=False,
                    cached=True,
                    retries=0
                )
                
                self._record_metric(metric)
                
                return cached_response['status_code'], cached_response['headers'], cached_response['data']
        
        # Preparar headers
        request_headers = self.optimized_headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Preparar dados
        request_data = data
        if json_data:
            request_data = json_data
            request_headers['Content-Type'] = 'application/json'
        
        # Comprimir dados se necessário
        compressed = False
        if self._should_compress_request(request_data):
            if isinstance(request_data, dict):
                request_data = self._compress_data(request_data)
                request_headers['Content-Encoding'] = 'gzip'
                request_headers['Content-Type'] = 'application/json'
                compressed = True
        
        # Timeout adaptativo
        adaptive_timeout = self._get_adaptive_timeout(host)
        
        # Garantir que adaptive_timeout é um número válido
        if not isinstance(adaptive_timeout, (int, float)) or adaptive_timeout <= 0:
            adaptive_timeout = self.read_timeout
        
        timeout = aiohttp.ClientTimeout(total=float(adaptive_timeout))
        
        # Inicializar sessão se necessário
        if not self._session:
            await self._initialize_session()
        
        retries = 0
        max_retries = 3
        last_error = None
        
        while retries <= max_retries:
            try:
                # Executar requisição
                async with self._session.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    data=request_data if not isinstance(request_data, dict) else None,
                    json=request_data if isinstance(request_data, dict) and not compressed else None,
                    params=params,
                    timeout=timeout
                ) as response:
                    
                    response_text = await response.text()
                    response_headers = dict(response.headers)
                    status_code = response.status
                    
                    duration = time.time() - start_time
                    
                    # Atualizar timeout adaptativo
                    self._update_adaptive_timeout(host, duration)
                    
                    # Registrar métrica
                    metric = PerformanceMetrics(
                        timestamp=datetime.now().isoformat(),
                        url=url,
                        method=method,
                        duration=duration,
                        status_code=status_code,
                        response_size=len(response_text),
                        compressed=compressed,
                        cached=False,
                        retries=retries
                    )
                    
                    self._record_metric(metric)
                    
                    # Cache resposta se for GET e sucesso
                    if (use_cache and CACHE_AVAILABLE and 
                        method.upper() == 'GET' and 
                        200 <= status_code < 300):
                        
                        cache_data = {
                            'status_code': status_code,
                            'headers': response_headers,
                            'data': response_text
                        }
                        cache_put(cache_key, cache_data, cache_type="http_request", ttl=cache_ttl)
                    
                    log_performance(f"HTTP_{method}", duration, {
                        'url': url,
                        'status': status_code,
                        'size': len(response_text),
                        'compressed': compressed,
                        'retries': retries
                    })
                    
                    return status_code, response_headers, response_text
            
            except asyncio.TimeoutError as e:
                last_error = f"Timeout após {adaptive_timeout}s"
                retries += 1
                if retries <= max_retries:
                    await asyncio.sleep(min(2 ** retries, 10))  # Backoff exponencial
                    logger.warning(f"⏱️ Timeout na requisição {url}, tentativa {retries}/{max_retries}")
            
            except Exception as e:
                last_error = str(e)
                retries += 1
                if retries <= max_retries:
                    await asyncio.sleep(min(2 ** retries, 10))
                    logger.warning(f"❌ Erro na requisição {url}, tentativa {retries}/{max_retries}: {e}")
        
        # Registrar métrica de erro
        duration = time.time() - start_time
        metric = PerformanceMetrics(
            timestamp=datetime.now().isoformat(),
            url=url,
            method=method,
            duration=duration,
            status_code=0,
            response_size=0,
            compressed=compressed,
            cached=False,
            retries=retries,
            error=last_error
        )
        
        self._record_metric(metric)
        
        raise Exception(f"Falha na requisição após {max_retries} tentativas: {last_error}")
    
    def _record_metric(self, metric: PerformanceMetrics):
        """Registra métrica de performance"""
        self.metrics_history.append(metric)
        
        # Extrair host da URL
        try:
            from urllib.parse import urlparse
            host = urlparse(metric.url).netloc
            self.host_metrics[host].append(metric)
        except Exception:
            pass
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de performance"""
        if not self.metrics_history:
            return {'message': 'Nenhuma métrica disponível'}
        
        # Estatísticas gerais
        total_requests = len(self.metrics_history)
        successful_requests = sum(1 for m in self.metrics_history if 200 <= m.status_code < 300)
        cached_requests = sum(1 for m in self.metrics_history if m.cached)
        compressed_requests = sum(1 for m in self.metrics_history if m.compressed)
        
        # Estatísticas de tempo
        durations = [m.duration for m in self.metrics_history if m.error is None]
        if durations:
            avg_duration = statistics.mean(durations)
            median_duration = statistics.median(durations)
            p95_duration = sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else max(durations)
        else:
            avg_duration = median_duration = p95_duration = 0
        
        # Estatísticas por host
        host_stats = {}
        for host, metrics in self.host_metrics.items():
            if metrics:
                host_durations = [m.duration for m in metrics if m.error is None]
                host_stats[host] = {
                    'requests': len(metrics),
                    'avg_duration': statistics.mean(host_durations) if host_durations else 0,
                    'success_rate': sum(1 for m in metrics if 200 <= m.status_code < 300) / len(metrics) * 100,
                    'adaptive_timeout': self.adaptive_timeouts[host]['timeout']
                }
        
        # Estatísticas de erro
        error_count = sum(1 for m in self.metrics_history if m.error)
        retry_count = sum(m.retries for m in self.metrics_history)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            'cached_requests': cached_requests,
            'cache_hit_rate': (cached_requests / total_requests * 100) if total_requests > 0 else 0,
            'compressed_requests': compressed_requests,
            'compression_rate': (compressed_requests / total_requests * 100) if total_requests > 0 else 0,
            'avg_duration': avg_duration,
            'median_duration': median_duration,
            'p95_duration': p95_duration,
            'error_count': error_count,
            'error_rate': (error_count / total_requests * 100) if total_requests > 0 else 0,
            'total_retries': retry_count,
            'host_stats': host_stats,
            'connection_stats': asdict(self.connection_stats) if hasattr(self, 'connection_stats') else {}
        }
    
    def get_recommendations(self) -> List[str]:
        """Gera recomendações de otimização"""
        stats = self.get_performance_stats()
        recommendations = []
        
        if 'success_rate' not in stats:
            return ['Colete mais dados para gerar recomendações']
        
        # Recomendações baseadas em taxa de sucesso
        if stats['success_rate'] < 95:
            recommendations.append(f"Taxa de sucesso baixa ({stats['success_rate']:.1f}%) - verificar conectividade")
        
        # Recomendações baseadas em cache
        if stats['cache_hit_rate'] < 20:
            recommendations.append(f"Taxa de cache baixa ({stats['cache_hit_rate']:.1f}%) - considerar aumentar TTL")
        
        # Recomendações baseadas em performance
        if stats['avg_duration'] > 5.0:
            recommendations.append(f"Latência alta ({stats['avg_duration']:.2f}s) - otimizar timeouts ou endpoints")
        
        # Recomendações baseadas em erros
        if stats['error_rate'] > 5:
            recommendations.append(f"Taxa de erro alta ({stats['error_rate']:.1f}%) - implementar retry mais agressivo")
        
        # Recomendações baseadas em compressão
        if stats['compression_rate'] < 30:
            recommendations.append("Baixo uso de compressão - considerar comprimir mais requisições")
        
        # Recomendações por host
        for host, host_data in stats.get('host_stats', {}).items():
            if host_data['success_rate'] < 90:
                recommendations.append(f"Host {host} com problemas ({host_data['success_rate']:.1f}% sucesso)")
        
        if not recommendations:
            recommendations.append("Performance otimizada - sistema funcionando adequadamente")
        
        return recommendations
    
    def generate_performance_report(self) -> str:
        """Gera relatório de performance"""
        stats = self.get_performance_stats()
        recommendations = self.get_recommendations()
        
        report = f"""# Relatório de Performance - {stats.get('timestamp', 'N/A')}

## 📊 Resumo Geral

- **Total de Requisições**: {stats.get('total_requests', 0)}
- **Taxa de Sucesso**: {stats.get('success_rate', 0):.2f}%
- **Taxa de Cache Hit**: {stats.get('cache_hit_rate', 0):.2f}%
- **Taxa de Compressão**: {stats.get('compression_rate', 0):.2f}%

## ⏱️ Métricas de Tempo

- **Duração Média**: {stats.get('avg_duration', 0):.3f}s
- **Duração Mediana**: {stats.get('median_duration', 0):.3f}s
- **P95**: {stats.get('p95_duration', 0):.3f}s

## ❌ Estatísticas de Erro

- **Total de Erros**: {stats.get('error_count', 0)}
- **Taxa de Erro**: {stats.get('error_rate', 0):.2f}%
- **Total de Retries**: {stats.get('total_retries', 0)}

## 🌐 Performance por Host

"""
        
        for host, host_data in stats.get('host_stats', {}).items():
            report += f"""### {host}
- **Requisições**: {host_data['requests']}
- **Duração Média**: {host_data['avg_duration']:.3f}s
- **Taxa de Sucesso**: {host_data['success_rate']:.2f}%
- **Timeout Adaptativo**: {host_data['adaptive_timeout']:.1f}s

"""
        
        report += "## 💡 Recomendações\n\n"
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        return report
    
    async def batch_requests(self, requests: List[Dict[str, Any]]) -> List[Tuple[int, Dict, str]]:
        """Executa múltiplas requisições em batch otimizado"""
        if not requests:
            return []
        
        logger.info(f"🚀 Executando batch de {len(requests)} requisições")
        
        # Criar semáforo para limitar concorrência
        semaphore = asyncio.Semaphore(min(20, len(requests)))
        
        async def execute_request(request_data):
            async with semaphore:
                return await self.optimized_request(**request_data)
        
        # Executar todas as requisições concorrentemente
        tasks = [execute_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Erro na requisição {i}: {result}")
                processed_results.append((0, {}, str(result)))
            else:
                processed_results.append(result)
        
        logger.info(f"✅ Batch concluído: {len(processed_results)} resultados")
        return processed_results

# Instância global do otimizador
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Obtém instância global do otimizador"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

# Decorador para otimização automática
def optimize_http_performance(use_cache: bool = True, cache_ttl: int = 300):
    """Decorator para otimização automática de requisições HTTP"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            optimizer = get_performance_optimizer()
            
            # Extrair parâmetros da função
            method = kwargs.get('method', 'GET')
            url = kwargs.get('url', '')
            
            if not url:
                # Tentar extrair URL dos argumentos posicionais
                if len(args) > 1:
                    url = args[1]
            
            if url:
                # Usar otimizador
                return await optimizer.optimized_request(
                    method=method,
                    url=url,
                    headers=kwargs.get('headers'),
                    data=kwargs.get('data'),
                    json_data=kwargs.get('json'),
                    params=kwargs.get('params'),
                    use_cache=use_cache,
                    cache_ttl=cache_ttl
                )
            else:
                # Executar função original
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Funções de conveniência
async def optimized_get(url: str, **kwargs) -> Tuple[int, Dict, str]:
    """GET otimizado"""
    optimizer = get_performance_optimizer()
    return await optimizer.optimized_request('GET', url, **kwargs)

async def optimized_post(url: str, **kwargs) -> Tuple[int, Dict, str]:
    """POST otimizado"""
    optimizer = get_performance_optimizer()
    return await optimizer.optimized_request('POST', url, **kwargs)

def get_performance_stats() -> Dict[str, Any]:
    """Obtém estatísticas de performance"""
    optimizer = get_performance_optimizer()
    return optimizer.get_performance_stats()

def get_performance_recommendations() -> List[str]:
    """Obtém recomendações de performance"""
    optimizer = get_performance_optimizer()
    return optimizer.get_recommendations()

def generate_performance_report() -> str:
    """Gera relatório de performance"""
    optimizer = get_performance_optimizer()
    return optimizer.generate_performance_report()