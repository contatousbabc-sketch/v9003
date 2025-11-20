#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Intelligent Rate Limiter
Sistema inteligente de rate limiting com delays adaptativos
"""

import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Configuração de rate limiting para uma API"""
    api_name: str
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    burst_limit: int = 10
    backoff_multiplier: float = 1.5
    max_backoff_seconds: int = 300
    adaptive_enabled: bool = True

@dataclass
class RequestRecord:
    """Registro de uma requisição"""
    timestamp: datetime
    success: bool
    response_time: float
    rate_limited: bool = False

class IntelligentRateLimiter:
    """Sistema inteligente de rate limiting com adaptação automática"""
    
    def __init__(self):
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.current_delays: Dict[str, float] = defaultdict(float)
        self.last_request_time: Dict[str, datetime] = {}
        self.consecutive_rate_limits: Dict[str, int] = defaultdict(int)
        self.lock = threading.Lock()
        
        # Configurações padrão por API
        self.api_configs = {
            'openrouter': RateLimitConfig('openrouter', 20, 1200, 5, 2.0, 300),
            'gemini': RateLimitConfig('gemini', 15, 900, 3, 2.0, 300),
            'openai': RateLimitConfig('openai', 60, 3600, 10, 1.5, 180),
            'serper': RateLimitConfig('serper', 30, 1800, 5, 2.0, 300),
            'exa': RateLimitConfig('exa', 60, 3600, 10, 1.5, 180),
            'jina': RateLimitConfig('jina', 100, 6000, 20, 1.2, 120),
            'firecrawl': RateLimitConfig('firecrawl', 20, 1200, 5, 2.0, 300),
            'apify': RateLimitConfig('apify', 30, 1800, 8, 1.5, 240),
            'supadata': RateLimitConfig('supadata', 60, 3600, 10, 1.5, 180),
            'tavily': RateLimitConfig('tavily', 60, 3600, 10, 1.5, 180),
        }
    
    def should_wait_before_request(self, api_name: str) -> Tuple[bool, float]:
        """
        Verifica se deve aguardar antes de fazer uma requisição
        
        Returns:
            Tuple[bool, float]: (should_wait, wait_seconds)
        """
        with self.lock:
            config = self.api_configs.get(api_name, RateLimitConfig(api_name))
            now = datetime.now()
            
            # Verifica se há delay atual em vigor
            current_delay = self.current_delays.get(api_name, 0)
            if current_delay > 0:
                last_request = self.last_request_time.get(api_name)
                if last_request:
                    time_since_last = (now - last_request).total_seconds()
                    if time_since_last < current_delay:
                        wait_time = current_delay - time_since_last
                        return True, wait_time
            
            # Verifica rate limiting baseado no histórico
            history = self.request_history[api_name]
            
            # Remove registros antigos (mais de 1 hora)
            cutoff_time = now - timedelta(hours=1)
            while history and history[0].timestamp < cutoff_time:
                history.popleft()
            
            # Conta requisições no último minuto
            minute_ago = now - timedelta(minutes=1)
            recent_requests = sum(1 for record in history if record.timestamp > minute_ago)
            
            # Verifica se excedeu limite por minuto
            if recent_requests >= config.requests_per_minute:
                wait_time = 60 - (now - minute_ago).total_seconds()
                return True, max(wait_time, 1)
            
            # Verifica burst limit
            last_10_seconds = now - timedelta(seconds=10)
            burst_requests = sum(1 for record in history if record.timestamp > last_10_seconds)
            
            if burst_requests >= config.burst_limit:
                return True, 10  # Aguarda 10 segundos
            
            return False, 0
    
    def wait_if_needed(self, api_name: str) -> float:
        """
        Aguarda se necessário antes de fazer uma requisição
        
        Returns:
            float: Tempo aguardado em segundos
        """
        should_wait, wait_time = self.should_wait_before_request(api_name)
        
        if should_wait:
            logger.info(f"⏳ Rate limiting {api_name}: aguardando {wait_time:.1f}s")
            time.sleep(wait_time)
            return wait_time
        
        return 0
    
    async def async_wait_if_needed(self, api_name: str) -> float:
        """Versão assíncrona do wait_if_needed"""
        should_wait, wait_time = self.should_wait_before_request(api_name)
        
        if should_wait:
            logger.info(f"⏳ Rate limiting {api_name}: aguardando {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            return wait_time
        
        return 0
    
    def record_request(self, api_name: str, success: bool, response_time: float, rate_limited: bool = False):
        """Registra uma requisição para análise adaptativa"""
        with self.lock:
            now = datetime.now()
            
            # Registra a requisição
            record = RequestRecord(now, success, response_time, rate_limited)
            self.request_history[api_name].append(record)
            self.last_request_time[api_name] = now
            
            # Atualiza contadores de rate limiting consecutivos
            if rate_limited:
                self.consecutive_rate_limits[api_name] += 1
                self._increase_delay(api_name)
            else:
                # Reset contador se requisição foi bem-sucedida
                if self.consecutive_rate_limits[api_name] > 0:
                    self.consecutive_rate_limits[api_name] = max(0, self.consecutive_rate_limits[api_name] - 1)
                    if self.consecutive_rate_limits[api_name] == 0:
                        self._decrease_delay(api_name)
    
    def _increase_delay(self, api_name: str):
        """Aumenta o delay para uma API com rate limiting"""
        config = self.api_configs.get(api_name, RateLimitConfig(api_name))
        
        if not config.adaptive_enabled:
            return
        
        current_delay = self.current_delays.get(api_name, 0)
        consecutive_limits = self.consecutive_rate_limits[api_name]
        
        # Calcula novo delay com backoff exponencial
        if current_delay == 0:
            new_delay = 60  # Começa com 1 minuto
        else:
            new_delay = min(current_delay * config.backoff_multiplier, config.max_backoff_seconds)
        
        self.current_delays[api_name] = new_delay
        
        logger.warning(f"📈 Aumentando delay para {api_name}: {new_delay:.1f}s (rate limits consecutivos: {consecutive_limits})")
    
    def _decrease_delay(self, api_name: str):
        """Diminui o delay para uma API que voltou a funcionar"""
        current_delay = self.current_delays.get(api_name, 0)
        
        if current_delay > 0:
            new_delay = max(current_delay * 0.5, 0)  # Reduz pela metade
            if new_delay < 5:  # Se menor que 5 segundos, remove completamente
                new_delay = 0
            
            self.current_delays[api_name] = new_delay
            
            if new_delay == 0:
                logger.info(f"📉 Removendo delay para {api_name}: API voltou ao normal")
            else:
                logger.info(f"📉 Reduzindo delay para {api_name}: {new_delay:.1f}s")
    
    def get_api_status(self, api_name: str) -> Dict[str, Any]:
        """Retorna status atual de uma API"""
        with self.lock:
            history = self.request_history[api_name]
            now = datetime.now()
            
            # Estatísticas do último minuto
            minute_ago = now - timedelta(minutes=1)
            recent_requests = [r for r in history if r.timestamp > minute_ago]
            
            # Estatísticas da última hora
            hour_ago = now - timedelta(hours=1)
            hourly_requests = [r for r in history if r.timestamp > hour_ago]
            
            return {
                'api_name': api_name,
                'current_delay': self.current_delays.get(api_name, 0),
                'consecutive_rate_limits': self.consecutive_rate_limits[api_name],
                'last_request': self.last_request_time.get(api_name),
                'requests_last_minute': len(recent_requests),
                'requests_last_hour': len(hourly_requests),
                'success_rate_last_hour': (
                    sum(1 for r in hourly_requests if r.success) / len(hourly_requests)
                    if hourly_requests else 1.0
                ),
                'rate_limited_requests_last_hour': sum(1 for r in hourly_requests if r.rate_limited),
                'avg_response_time': (
                    sum(r.response_time for r in hourly_requests) / len(hourly_requests)
                    if hourly_requests else 0
                )
            }
    
    def get_global_status(self) -> Dict[str, Any]:
        """Retorna status global de todas as APIs"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'apis': {},
            'summary': {
                'total_apis': len(self.api_configs),
                'apis_with_delays': 0,
                'apis_rate_limited': 0,
                'total_requests_last_hour': 0
            }
        }
        
        for api_name in self.api_configs.keys():
            api_status = self.get_api_status(api_name)
            status['apis'][api_name] = api_status
            
            if api_status['current_delay'] > 0:
                status['summary']['apis_with_delays'] += 1
            
            if api_status['consecutive_rate_limits'] > 0:
                status['summary']['apis_rate_limited'] += 1
            
            status['summary']['total_requests_last_hour'] += api_status['requests_last_hour']
        
        return status
    
    def reset_api_delays(self, api_name: str = None):
        """Reset delays para uma API específica ou todas"""
        with self.lock:
            if api_name:
                self.current_delays[api_name] = 0
                self.consecutive_rate_limits[api_name] = 0
                logger.info(f"🔄 Reset delays para {api_name}")
            else:
                self.current_delays.clear()
                self.consecutive_rate_limits.clear()
                logger.info("🔄 Reset delays para todas as APIs")

# Instância global
intelligent_rate_limiter = IntelligentRateLimiter()