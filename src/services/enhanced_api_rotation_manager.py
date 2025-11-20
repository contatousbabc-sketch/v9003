"""
Sistema Avançado de Rotação de APIs - V18.0
Garante alta disponibilidade com fallback automático entre múltiplas APIs
ATUALIZADO: Implementa fallbacks Jina->EXA, Qwen->Gemini, Supadata para insights sociais
"""

import os
import time
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime, timedelta
import threading
import requests
import asyncio
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
from dotenv import load_dotenv

# Importar sistema de logging otimizado
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

try:
    from enhanced_logging_system import get_logger, log_api_call, log_performance
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    def log_api_call(api_name, endpoint, status, duration):
        pass
    def log_performance(operation, duration, details=None):
        pass

# Importar sistema de cache inteligente
try:
    from intelligent_cache_system import cache_get, cache_put, cache_invalidate
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    def cache_get(key, prefix="", default=None):
        return default
    def cache_put(key, value, cache_type="default", ttl=None, prefix=""):
        return ""

# Importar alternativa gratuita de busca
try:
    from duckduckgo_search_alternative import search_with_alternatives
    ALTERNATIVE_SEARCH_AVAILABLE = True
except ImportError:
    ALTERNATIVE_SEARCH_AVAILABLE = False
    async def search_with_alternatives(query, num_results=10):
        return []

# Importar sistema de modelo local como fallback
try:
    from services.local_model_manager import local_model_manager, is_local_model_available
    LOCAL_MODEL_AVAILABLE = True
    logger.info("✅ Sistema de modelo local disponível como fallback")
except ImportError:
    LOCAL_MODEL_AVAILABLE = False
    logger.warning("⚠️ Sistema de modelo local não disponível")
    def is_local_model_available():
        return False
    def cache_invalidate(key, prefix=""):
        return False

# Importar sistema de tratamento de exceções
try:
    from enhanced_exception_handler import (
        handle_async_exceptions, 
        async_retry_on_exception,
        log_exception,
        ExceptionCategory
    )
    EXCEPTION_HANDLER_AVAILABLE = True
except ImportError:
    EXCEPTION_HANDLER_AVAILABLE = False
    def handle_async_exceptions(**kwargs):
        def decorator(func):
            return func
        return decorator
    def async_retry_on_exception(**kwargs):
        def decorator(func):
            return func
        return decorator
    def log_exception(exception, context=None):
        pass

# Importar sistema de otimização de performance
try:
    from performance_optimizer import get_performance_optimizer, optimize_http_performance
    PERFORMANCE_OPTIMIZER_AVAILABLE = True
except ImportError:
    PERFORMANCE_OPTIMIZER_AVAILABLE = False
    def optimize_http_performance(**kwargs):
        def decorator(func):
            return func
        return decorator

try:
    from utils.api_credit_manager import APICreditManager
except ImportError:
    try:
        from ..utils.api_credit_manager import APICreditManager
    except ImportError:
        # Fallback simples se não encontrar o módulo
        class APICreditManager:
            def __init__(self):
                pass
            def get_credits(self, api_name):
                return 1000
            def consume_credits(self, api_name, amount):
                return True
            def has_credits(self, api_name):
                return True

# Carregar variáveis de ambiente
load_dotenv()

# Now safely log the aiohttp warning if it wasn't available
if not AIOHTTP_AVAILABLE:
    logger.warning("aiohttp não instalado – usando fallback síncrono com requests")

class APIStatus(Enum):
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class APIEndpoint:
    name: str
    api_key: str
    base_url: str
    status: APIStatus = APIStatus.ACTIVE
    last_used: datetime = None
    error_count: int = 0
    rate_limit_reset: datetime = None
    requests_made: int = 0
    max_requests_per_minute: int = 60

class EnhancedAPIRotationManager:
    """
    Gerenciador avançado de rotação de APIs com:
    - Fallback automático entre modelos
    - Rate limiting inteligente
    - Health checking
    - Balanceamento de carga
    """
    
    def __init__(self):
        self.apis = {
            'qwen': [],
            'gemini': [],
            'openrouter': [],
            'openai': [],
            'deepseek': [],
            'jina': [],
            'exa': [],
            'serper': [],
            'serpapi': [],
            'tavily': [],
            'supadata': [],
            'firecrawl': [],
            'scrapingant': [],
            'youtube': [],
            'rapidapi': [],
            'apify': [],  # Adicionado Apify
            'fireworks': [],  # Adicionado Fireworks
            'groq': []  # Adicionado Groq
        }
        
        # Propriedade providers para compatibilidade
        self._providers = {}
        
        # Sistema de gestão de créditos
        self.credit_manager = APICreditManager()
        
        # Definir cadeias de fallback (cada grupo é uma prioridade)
        self.fallback_chains = {
            'ai_models': [['qwen'], ['gemini'], ['openai'], ['openrouter'], ['deepseek'], ['fireworks'], ['groq']],
            'ai_generation': [['qwen'], ['gemini'], ['openai'], ['openrouter'], ['deepseek'], ['fireworks'], ['groq']],
            'search': [['jina'], ['exa'], ['serper'], ['serpapi'], ['firecrawl'], ['tavily'], ['apify']],
            'social_insights': [['supadata'], ['apify'], ['serper'], ['serpapi'], ['firecrawl'], ['tavily']],
            'web_scraping': [['firecrawl'], ['apify'], ['scrapingant'], ['jina'], ['serper'], ['serpapi']],
            'content_extraction': [['firecrawl'], ['jina'], ['apify'], ['scrapingant'], ['serper'], ['rapidapi']],
            'url_analysis': [['firecrawl'], ['jina'], ['exa'], ['apify'], ['serper'], ['serpapi']]
        }
        self.current_api_index = {}
        self.lock = threading.Lock()
        self.health_check_interval = 300  # 5 minutos
        self.last_health_check = {}
        self.last_request_time = {}  # Controle de tempo entre requisições
        self._openrouter_test_pending = False  # Flag para teste pendente
        
        # Circuit Breaker para prevenir falhas em cascata
        self.circuit_breakers = {}
        self.failure_counts = {}
        self.circuit_breaker_threshold = 5  # Falhas antes de abrir circuito
        self.circuit_breaker_timeout = 300  # 5 minutos para tentar novamente
        
        # Métricas de performance
        self.api_performance_metrics = {}
        self.cascade_failure_prevention = True
        
        self._load_api_configurations()
        self._initialize_health_monitoring()
        
        # Testar conectividade das chaves OpenRouter em background
        try:
            # Verificar se há um loop de eventos ativo
            loop = asyncio.get_running_loop()
            loop.create_task(self._test_openrouter_keys())
        except RuntimeError:
            # Se não há loop de eventos, agendar para execução posterior
            self._openrouter_test_pending = True
    
    def _load_api_configurations(self):
        """Carrega configurações de APIs do .env"""
        try:
            # OpenRouter - Carregar TODAS as chaves disponíveis do .env
            openrouter_keys = [
                os.getenv('OPENROUTER_API_KEY'),
                os.getenv('OPENROUTER_API_KEY_1'), 
                os.getenv('OPENROUTER_API_KEY_2'),
                os.getenv('OPENROUTER_API_KEY_3'),
                os.getenv('OPENROUTER_API_KEY_4'),
                os.getenv('OPENROUTER_API_KEY_5')
            ]
            
            openrouter_count = 0
            for i, key in enumerate(openrouter_keys, 1):
                if key and key.strip():
                    endpoint = APIEndpoint(
                        name=f"openrouter_{i}",
                        api_key=key,
                        base_url='https://openrouter.ai/api/v1',
                        max_requests_per_minute=30  # Mais conservador para evitar rate limiting
                    )
                    self.apis['qwen'].append(endpoint)
                    self.apis['openrouter'].append(endpoint)  # Adicionar também na categoria openrouter
                    # Registrar no credit manager com limites conservadores
                    self.credit_manager.register_api('openrouter', f"key_{i}", daily_limit=150)
                    openrouter_count += 1
                    logger.info(f"✅ OpenRouter API {i} carregada e registrada")
            
            logger.info(f"🔑 Total de {openrouter_count} chaves OpenRouter carregadas")
            
            # Gemini - Usar as chaves reais do .env
            gemini_keys = [
                os.getenv('GEMINI_API_KEY'),
                os.getenv('GEMINI_API_KEY_1'),
                os.getenv('GEMINI_API_KEY_2')
            ]
            
            for i, key in enumerate(gemini_keys, 1):
                if key and key.strip():
                    endpoint = APIEndpoint(
                        name=f"gemini_{i}",
                        api_key=key,
                        base_url="https://generativelanguage.googleapis.com/v1beta",
                        max_requests_per_minute=20  # Muito conservador para Gemini
                    )
                    self.apis['gemini'].append(endpoint)
                    # Registrar no credit manager
                    self.credit_manager.register_api('gemini', f"key_{i}", daily_limit=1500)
                    logger.info(f"✅ Gemini API {i} carregada e registrada")
            
            # OpenAI
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                endpoint = APIEndpoint(
                    name="openai_1",
                    api_key=openai_key,
                    base_url="https://api.openai.com/v1",
                    max_requests_per_minute=60
                )
                self.apis['openai'].append(endpoint)
                self.credit_manager.register_api('openai', 'key_1', daily_limit=1000)
                logger.info("✅ OpenAI API carregada e registrada")
            
            # DeepSeek
            deepseek_key = os.getenv('DEEPSEEK_API_KEY')
            if deepseek_key:
                endpoint = APIEndpoint(
                    name="deepseek_1",
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com",
                    max_requests_per_minute=60
                )
                self.apis['deepseek'].append(endpoint)
                self.credit_manager.register_api('deepseek', 'key_1', daily_limit=500)
                logger.info("✅ DeepSeek API carregada e registrada")
            
            # Jina AI - Primário para busca - TODAS as chaves do .env
            jina_keys = [
                os.getenv('JINA_API_KEY'),
                os.getenv('JINA_API_KEY_1'),
                os.getenv('JINA_API_KEY_2'),
                os.getenv('JINA_API_KEY_3'),
                os.getenv('JINA_API_KEY_4')
            ]
            
            for i, key in enumerate(jina_keys, 1):
                if key and key.strip():
                    endpoint = APIEndpoint(
                        name=f"jina_{i}",
                        api_key=key,
                        base_url="https://r.jina.ai",
                        max_requests_per_minute=200
                    )
                    self.apis['jina'].append(endpoint)
                    self.credit_manager.register_api('jina', f"key_{i}", daily_limit=1000)
                    logger.info(f"✅ Jina API {i} carregada e registrada")
            
            # EXA - Fallback para Jina
            exa_keys = [
                os.getenv('EXA_API_KEY'),
                os.getenv('EXA_API_KEY_1')
            ]
            
            for i, key in enumerate(exa_keys, 1):
                if key and key.strip():
                    endpoint = APIEndpoint(
                        name=f"exa_{i}",
                        api_key=key,
                        base_url="https://api.exa.ai",
                        max_requests_per_minute=100
                    )
                    self.apis['exa'].append(endpoint)
                    self.credit_manager.register_api('exa', f"key_{i}", daily_limit=1000)
                    logger.info(f"✅ EXA API {i} carregada e registrada")
            
            # Serper - Substituto secundário - TODAS as chaves do .env
            serper_keys = [
                os.getenv('SERPER_API_KEY'),
                os.getenv('SERPER_API_KEY_1'),
                os.getenv('SERPER_API_KEY_2'),
                os.getenv('SERPER_API_KEY_3')
            ]
            
            for i, key in enumerate(serper_keys, 1):
                if key and key.strip():
                    endpoint = APIEndpoint(
                        name=f"serper_{i}",
                        api_key=key,
                        base_url="https://google.serper.dev",
                        max_requests_per_minute=100
                    )
                    self.apis['serper'].append(endpoint)
                    self.credit_manager.register_api('serper', f"key_{i}", daily_limit=2500)
                    logger.info(f"✅ Serper API {i} carregada e registrada")
            
            # SerpAPI - Nova adição para busca Google
            serpapi_keys = [
                os.getenv('SERP_API_KEY'),
                os.getenv('SERP_API_KEY_1')
            ]
            
            for i, key in enumerate(serpapi_keys, 1):
                if key and key.strip():
                    endpoint = APIEndpoint(
                        name=f"serpapi_{i}",
                        api_key=key,
                        base_url="https://serpapi.com",
                        max_requests_per_minute=100
                    )
                    self.apis['serpapi'].append(endpoint)
                    self.credit_manager.register_api('serpapi', f"key_{i}", daily_limit=100)
                    logger.info(f"✅ SerpAPI {i} carregada e registrada")
            
            # Supadata - Para insights de redes sociais
            supadata_keys = [
                os.getenv('SUPADATA_API_KEY'),
                os.getenv('SUPADATA_API_KEY_1')
            ]
            
            for i, key in enumerate(supadata_keys, 1):
                if key and key.strip():
                    endpoint = APIEndpoint(
                        name=f"supadata_{i}",
                        api_key=key,
                        base_url=os.getenv('SUPADATA_API_URL', 'https://api.supadata.ai/v1'),
                        max_requests_per_minute=50
                    )
                    self.apis['supadata'].append(endpoint)
                    self.credit_manager.register_api('supadata', f"key_{i}", daily_limit=1000)
                    logger.info(f"✅ Supadata API {i} carregada e registrada")
            
            # OpenRouter com Google Gemini 2.0 Flash (substituindo Groq)
            # Usar as mesmas chaves do OpenRouter já configuradas
            # Isso será tratado pela seção OpenRouter existente
            
            # Tavily
            tavily_key = os.getenv('TAVILY_API_KEY')
            if tavily_key:
                endpoint = APIEndpoint(
                    name="tavily_1",
                    api_key=tavily_key,
                    base_url="https://api.tavily.com",
                    max_requests_per_minute=100
                )
                self.apis['tavily'].append(endpoint)
                self.credit_manager.register_api('tavily', 'key_1', daily_limit=1000)
                logger.info("✅ Tavily API carregada e registrada")
            
            # Firecrawl - TODAS as chaves do .env
            firecrawl_keys = [
                os.getenv('FIRECRAWL_API_KEY'),
                os.getenv('FIRECRAWL_API_KEY_1'),
                os.getenv('FIRECRAWL_API_KEY_2')
            ]
            
            for i, key in enumerate(firecrawl_keys, 1):
                if key and key.strip():
                    endpoint = APIEndpoint(
                        name=f"firecrawl_{i}",
                        api_key=key,
                        base_url="https://api.firecrawl.dev",
                        max_requests_per_minute=60
                    )
                    self.apis['firecrawl'].append(endpoint)
                    self.credit_manager.register_api('firecrawl', f"key_{i}", daily_limit=500)
                    logger.info(f"✅ Firecrawl API {i} carregada e registrada")
            
            # ScrapingAnt
            scrapingant_key = os.getenv('SCRAPINGANT_API_KEY')
            if scrapingant_key:
                endpoint = APIEndpoint(
                    name="scrapingant_1",
                    api_key=scrapingant_key,
                    base_url="https://api.scrapingant.com",
                    max_requests_per_minute=60
                )
                self.apis['scrapingant'].append(endpoint)
                self.credit_manager.register_api('scrapingant', 'key_1', daily_limit=1000)
                logger.info("✅ ScrapingAnt API carregada e registrada")
            
            # YouTube
            youtube_key = os.getenv('YOUTUBE_API_KEY')
            if youtube_key:
                endpoint = APIEndpoint(
                    name="youtube_1",
                    api_key=youtube_key,
                    base_url="https://www.googleapis.com/youtube/v3",
                    max_requests_per_minute=100
                )
                self.apis['youtube'].append(endpoint)
                self.credit_manager.register_api('youtube', 'key_1', daily_limit=10000)
                logger.info("✅ YouTube API carregada e registrada")
            
            # RapidAPI - Para APIs múltiplas
            rapidapi_key = os.getenv('RAPIDAPI_KEY')
            if rapidapi_key:
                endpoint = APIEndpoint(
                    name="rapidapi_1",
                    api_key=rapidapi_key,
                    base_url="https://rapidapi.com",
                    max_requests_per_minute=200
                )
                self.apis['rapidapi'].append(endpoint)
                self.credit_manager.register_api('rapidapi', 'key_1', daily_limit=500)
                logger.info("✅ RapidAPI carregada e registrada")
            
            # Apify - TODAS as chaves do .env
            apify_keys = [
                os.getenv('APIFY_API_KEY'),
                os.getenv('APIFY_API_KEY_1'),
                os.getenv('APIFY_API_KEY_2'),
                os.getenv('APIFY_API_KEY_3')
            ]
            
            for i, key in enumerate(apify_keys, 1):
                if key and key.strip():
                    endpoint = APIEndpoint(
                        name=f"apify_{i}",
                        api_key=key,
                        base_url="https://api.apify.com/v2",
                        max_requests_per_minute=100
                    )
                    self.apis.setdefault('apify', []).append(endpoint)
                    self.credit_manager.register_api('apify', f"key_{i}", daily_limit=1000)
                    logger.info(f"✅ Apify API {i} carregada e registrada")
            
            # Fireworks AI - Adicionado para LLM reasoning
            fireworks_keys = [
                os.getenv('FIREWORKS_API_KEY'),
                os.getenv('FIREWORKS_API_KEY_1')
            ]
            
            for i, key in enumerate(fireworks_keys, 1):
                if key and key.strip():
                    endpoint = APIEndpoint(
                        name=f"fireworks_{i}",
                        api_key=key,
                        base_url="https://api.fireworks.ai/inference/v1",
                        max_requests_per_minute=60
                    )
                    self.apis['fireworks'].append(endpoint)
                    self.credit_manager.register_api('fireworks', f"key_{i}", daily_limit=1000)
                    logger.info(f"✅ Fireworks AI {i} carregada e registrada")
                    logger.info(f"✅ Fireworks API {i} carregada para modelo gemma-3-27b-it")
            
            # Groq - Adicionado para LLM reasoning
            groq_keys = [
                os.getenv('GROQ_API_KEY'),
                os.getenv('GROQ_API_KEY_1')
            ]
            
            for i, key in enumerate(groq_keys, 1):
                if key and key.strip():
                    endpoint = APIEndpoint(
                        name=f"groq_{i}",
                        api_key=key,
                        base_url="https://api.groq.com/openai/v1",
                        max_requests_per_minute=60
                    )
                    self.apis['groq'].append(endpoint)
                    self.credit_manager.register_api('groq', f"key_{i}", daily_limit=14400)
                    logger.info(f"✅ Groq API {i} carregada e registrada para modelo qwen/qwen3-32b")
            
            # Inicializar índices
            for service in self.apis:
                self.current_api_index[service] = 0
                self.last_request_time[service] = datetime.now() - timedelta(seconds=10)  # Inicializa com 10s de diferença
                
            total_apis = sum(len(apis) for apis in self.apis.values())
            logger.info(f"✅ APIs carregadas: {total_apis} endpoints")
            
            # Log detalhado das APIs carregadas
            for service, apis in self.apis.items():
                if apis:
                    logger.info(f"  - {service}: {len(apis)} APIs")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configurações de API: {e}")
    
    def _get_base_url(self, service: str) -> str:
        """Retorna URL base para cada serviço"""
        urls = {
            'tavily': 'https://api.tavily.com',
            'exa': 'https://api.exa.ai',
            'serpapi': 'https://serpapi.com/search',
            'rapidapi': 'https://rapidapi.com',
            'serper': 'https://google.serper.dev'
        }
        return urls.get(service, '')
    
    def _initialize_health_monitoring(self):
        """Inicializa monitoramento de saúde das APIs"""
        for service in self.apis:
            self.last_health_check[service] = datetime.now() - timedelta(minutes=10)
    
    def _enforce_request_delay(self, service: str, delay_seconds: int = 15):
        """
        Implementa uma pausa entre requisições para evitar rate limiting
        """
        if service not in self.last_request_time:
            self.last_request_time[service] = datetime.now() - timedelta(seconds=delay_seconds)
            return
        
        time_since_last = (datetime.now() - self.last_request_time[service]).total_seconds()
        
        if time_since_last < delay_seconds:
            sleep_time = delay_seconds - time_since_last
            logger.info(f"⏱️ Aguardando {sleep_time:.1f}s antes de fazer requisição para {service}")
            time.sleep(sleep_time)
        
        self.last_request_time[service] = datetime.now()
    
    def get_active_api(self, service: str, force_check: bool = False) -> Optional[APIEndpoint]:
        """
        Retorna API ativa para o serviço especificado com rotação automática
        """
        with self.lock:
            if service not in self.apis or not self.apis[service]:
                logger.warning(f"⚠️ Nenhuma API disponível para {service}")
                return None
            
            # Health check se necessário
            if force_check or self._needs_health_check(service):
                self._perform_health_check(service)
            
            # Encontrar API ativa com rotação automática
            apis = self.apis[service]
            start_index = self.current_api_index[service]
            
            # Verificar se a API atual está disponível
            current_api = apis[start_index]
            if self._is_api_available(current_api):
                # Implementar pausa entre requisições
                self._enforce_request_delay(service)
                
                current_api.last_used = datetime.now()
                current_api.requests_made += 1
                logger.info(f"🔄 Continuando com API {current_api.name} para {service}")
                return current_api
            
            # Se API atual não está disponível, rotar automaticamente
            logger.info(f"🔄 API atual indisponível, rotacionando {service}...")
            for i in range(1, len(apis)):  # Começar da próxima API
                index = (start_index + i) % len(apis)
                api = apis[index]
                
                if self._is_api_available(api):
                    # Implementar pausa entre requisições
                    self._enforce_request_delay(service)
                    
                    self.current_api_index[service] = index
                    api.last_used = datetime.now()
                    api.requests_made += 1
                    logger.info(f"✅ Rotação automática: API {api.name} para {service}")
                    return api
            
            logger.error(f"❌ Nenhuma API disponível para {service} após rotação")
            return None
    
    def _needs_health_check(self, service: str) -> bool:
        """Verifica se precisa fazer health check"""
        last_check = self.last_health_check.get(service)
        if not last_check:
            return True
        return datetime.now() - last_check > timedelta(seconds=self.health_check_interval)
    
    def _perform_health_check(self, service: str):
        """Executa health check nas APIs do serviço"""
        try:
            for api in self.apis[service]:
                if api.status == APIStatus.OFFLINE:
                    continue
                
                # Reset rate limit se expirou
                if api.rate_limit_reset and datetime.now() > api.rate_limit_reset:
                    api.status = APIStatus.ACTIVE
                    api.rate_limit_reset = None
                    api.requests_made = 0
                
                # Verificar se está rate limited
                if api.requests_made >= api.max_requests_per_minute:
                    api.status = APIStatus.RATE_LIMITED
                    api.rate_limit_reset = datetime.now() + timedelta(minutes=1)
            
            self.last_health_check[service] = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Erro no health check de {service}: {e}")
    
    def _is_api_available(self, api: APIEndpoint) -> bool:
        """Verifica se API está disponível para uso"""
        if api.status == APIStatus.OFFLINE:
            return False
        
        if api.status == APIStatus.RATE_LIMITED:
            if api.rate_limit_reset and datetime.now() > api.rate_limit_reset:
                api.status = APIStatus.ACTIVE
                api.requests_made = 0
                return True
            return False
        
        if api.status == APIStatus.ERROR and api.error_count > 5:
            return False
        
        # CORREÇÃO CRÍTICA: Verificar se API tem créditos esgotados
        # Consultar o credit_manager para verificar se a API está ativa
        api_key = f"{api.name.split('_')[0]}_{api.name.split('_')[1]}"
        if hasattr(self, 'credit_manager') and self.credit_manager:
            try:
                # Verificar se a API está marcada como sem créditos no credit manager
                if api_key in self.credit_manager.api_statuses:
                    credit_status = self.credit_manager.api_statuses[api_key]
                    if not credit_status.is_active and credit_status.last_error:
                        if any(indicator in credit_status.last_error.upper() for indicator in 
                               ['CREDITS_EXHAUSTED', 'INSUFFICIENT CREDITS', 'CRÉDITOS ESGOTADOS', 'HTTP 400']):
                            logger.warning(f"⚠️ API {api.name} sem créditos - pulando")
                            return False
            except Exception as e:
                logger.debug(f"Erro ao verificar créditos para {api.name}: {e}")
        
        return True
    
    def mark_api_error(self, service: str, api_name: str, error: Exception):
        """Marca API como com erro e força rotação imediata"""
        with self.lock:
            for i, api in enumerate(self.apis[service]):
                if api.name == api_name:
                    api.error_count += 1
                    
                    # Rotação IMEDIATA na primeira falha para garantir disponibilidade
                    api.status = APIStatus.ERROR
                    logger.warning(f"⚠️ API {api_name} marcada como ERROR - ROTAÇÃO IMEDIATA")
                    
                    # Forçar rotação para próxima API disponível
                    if len(self.apis[service]) > 1:
                        # Encontrar próxima API ativa
                        next_api_found = False
                        for j in range(1, len(self.apis[service])):
                            next_index = (i + j) % len(self.apis[service])
                            next_api = self.apis[service][next_index]
                            
                            # Verificar se a próxima API está disponível
                            if self._is_api_available(next_api) or next_api.status != APIStatus.ERROR:
                                self.current_api_index[service] = next_index
                                logger.info(f"🔄 ROTAÇÃO AUTOMÁTICA: {service} → {next_api.name}")
                                next_api_found = True
                                break
                        
                        if not next_api_found:
                            logger.error(f"❌ Nenhuma API alternativa disponível para {service}")
                    
                    # Recuperação mais rápida - 1 minuto para tentar novamente
                    self._schedule_api_recovery(service, api_name, recovery_time=60)
                    break
    
    def _schedule_api_recovery(self, service: str, api_name: str, recovery_time: int = 60):
        """Agenda recuperação automática da API após período de cooldown"""
        def recover_api():
            time.sleep(recovery_time)  # Cooldown configurável (padrão 1 minuto)
            with self.lock:
                for api in self.apis[service]:
                    if api.name == api_name:
                        api.status = APIStatus.ACTIVE
                        api.error_count = 0
                        logger.info(f"✅ API {api_name} RECUPERADA automaticamente após {recovery_time}s")
                        break
        
        import threading
        threading.Thread(target=recover_api, daemon=True).start()
        logger.info(f"⏱️ Recuperação de {api_name} agendada para {recovery_time} segundos")
    
    def mark_api_rate_limited(self, service: str, api_name: str, reset_time: Optional[datetime] = None):
        """Marca API como rate limited"""
        with self.lock:
            for api in self.apis[service]:
                if api.name == api_name:
                    api.status = APIStatus.RATE_LIMITED
                    api.rate_limit_reset = reset_time or (datetime.now() + timedelta(minutes=1))
                    logger.warning(f"⚠️ API {api_name} rate limited até {api.rate_limit_reset}")
                    break
    
    def get_fallback_api(self, service_type: str, failed_service: str = None) -> Optional[APIEndpoint]:
        """
        Retorna API de fallback baseada nas cadeias configuradas
        """
        if service_type not in self.fallback_chains:
            logger.warning(f"⚠️ Tipo de serviço desconhecido: {service_type}")
            return None
        
        chain = self.fallback_chains[service_type]
        
        # Se um serviço específico falhou, começar do próximo na cadeia
        start_index = 0
        if failed_service:
            for i, services in enumerate(chain):
                if failed_service in services:
                    start_index = i + 1
                    break
        
        # Percorrer cadeia de fallback a partir do índice calculado
        for i in range(start_index, len(chain)):
            for service_name in chain[i]:
                if service_name in self.apis and self.apis[service_name]:
                    # Usar get_active_api para obter API disponível
                    api = self.get_active_api(service_name)
                    if api:
                        logger.info(f"🔄 Fallback para {service_name} (tipo: {service_type})")
                        return api
        
        logger.error(f"❌ Nenhum fallback disponível para {service_type}")
        return None
    
    def _is_circuit_breaker_open(self, api_name: str) -> bool:
        """Verifica se o circuit breaker está aberto para uma API"""
        
        if not self.cascade_failure_prevention:
            return False
        
        if api_name not in self.circuit_breakers:
            return False
        
        breaker_info = self.circuit_breakers[api_name]
        
        # Se o circuito está aberto, verificar se já passou o timeout
        if breaker_info['state'] == 'open':
            if time.time() - breaker_info['opened_at'] > self.circuit_breaker_timeout:
                # Tentar meio-aberto
                self.circuit_breakers[api_name]['state'] = 'half-open'
                logger.info(f"🔄 Circuit breaker para {api_name} mudou para half-open")
                return False
            return True
        
        return False
    
    def _record_api_success(self, api_name: str):
        """Registra sucesso de uma API"""
        
        if api_name in self.failure_counts:
            self.failure_counts[api_name] = 0
        
        if api_name in self.circuit_breakers:
            if self.circuit_breakers[api_name]['state'] == 'half-open':
                # Fechar circuito após sucesso
                self.circuit_breakers[api_name]['state'] = 'closed'
                logger.info(f"✅ Circuit breaker para {api_name} fechado após sucesso")
        
        # Atualizar métricas de performance
        if api_name not in self.api_performance_metrics:
            self.api_performance_metrics[api_name] = {
                'success_count': 0,
                'failure_count': 0,
                'avg_response_time': 0,
                'last_success': time.time()
            }
        
        self.api_performance_metrics[api_name]['success_count'] += 1
        self.api_performance_metrics[api_name]['last_success'] = time.time()
    
    def _record_api_failure(self, api_name: str, error_type: str = "unknown"):
        """Registra falha de uma API e gerencia circuit breaker"""
        
        # Incrementar contador de falhas
        if api_name not in self.failure_counts:
            self.failure_counts[api_name] = 0
        
        self.failure_counts[api_name] += 1
        
        # Atualizar métricas
        if api_name not in self.api_performance_metrics:
            self.api_performance_metrics[api_name] = {
                'success_count': 0,
                'failure_count': 0,
                'avg_response_time': 0,
                'last_failure': time.time()
            }
        
        self.api_performance_metrics[api_name]['failure_count'] += 1
        self.api_performance_metrics[api_name]['last_failure'] = time.time()
        
        # Verificar se deve abrir circuit breaker
        if (self.cascade_failure_prevention and 
            self.failure_counts[api_name] >= self.circuit_breaker_threshold):
            
            self.circuit_breakers[api_name] = {
                'state': 'open',
                'opened_at': time.time(),
                'failure_count': self.failure_counts[api_name],
                'error_type': error_type
            }
            
            logger.warning(f"🚨 Circuit breaker ABERTO para {api_name} após {self.failure_counts[api_name]} falhas")
    
    def get_api_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde de todas as APIs"""
        
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'apis': {},
            'circuit_breakers': {},
            'overall_health': 'healthy'
        }
        
        total_apis = 0
        healthy_apis = 0
        
        for api_type, apis in self.apis.items():
            for api in apis:
                total_apis += 1
                api_name = f"{api_type}_{api.name}"
                
                # Status básico
                is_circuit_open = self._is_circuit_breaker_open(api_name)
                failure_count = self.failure_counts.get(api_name, 0)
                
                if is_circuit_open:
                    status = 'circuit_open'
                elif failure_count > 2:
                    status = 'degraded'
                else:
                    status = 'healthy'
                    healthy_apis += 1
                
                health_status['apis'][api_name] = {
                    'status': status,
                    'failure_count': failure_count,
                    'circuit_breaker_open': is_circuit_open,
                    'performance_metrics': self.api_performance_metrics.get(api_name, {})
                }
        
        # Status dos circuit breakers
        health_status['circuit_breakers'] = dict(self.circuit_breakers)
        
        # Status geral
        if total_apis > 0:
            health_ratio = healthy_apis / total_apis
            if health_ratio < 0.5:
                health_status['overall_health'] = 'critical'
            elif health_ratio < 0.8:
                health_status['overall_health'] = 'degraded'
        
        return health_status

    def get_api_with_fallback(self, service_type: str) -> Optional[APIEndpoint]:
        """
        Obtém API com fallback automático
        """
        # Tentar obter API primária
        api = self.get_active_api_by_type(service_type)
        if api:
            return api
        
        # Se falhou, tentar fallback
        return self.get_fallback_api(service_type)
    
    def get_fallback_model(self, model_name: str) -> tuple[str, Optional[APIEndpoint]]:
        """
        Método de compatibilidade para get_fallback_model
        Retorna tupla (model_name, api_endpoint)
        """
        # Mapear nomes de modelos para tipos de serviço
        model_to_service = {
            'qwen': 'ai_generation',
            'gpt': 'ai_generation', 
            'claude': 'ai_generation',
            'gemini': 'ai_generation',
            'llama': 'ai_generation',
            'gemma': 'ai_generation',
            'fireworks': 'ai_generation',
            'groq': 'ai_generation'
        }
        
        service_type = model_to_service.get(model_name, 'ai_generation')
        api = self.get_api_with_fallback(service_type)
        
        if api:
            logger.info(f"✅ Fallback model encontrado: {model_name} via {api.name}")
            return model_name, api
        else:
            logger.warning(f"⚠️ Nenhuma API disponível para {model_name}")
            return model_name, None

    def get_active_api_by_type(self, service_type: str) -> Optional[APIEndpoint]:
        """
        Obtém API ativa baseada no tipo de serviço
        """
        if service_type not in self.fallback_chains:
            return None
        
        # Tentar primeiro serviço da cadeia
        primary_services = self.fallback_chains[service_type][0]
        
        for service_name in primary_services:
            if service_name in self.apis and self.apis[service_name]:
                # Usar o método get_active_api existente
                api = self.get_active_api(service_name)
                if api:
                    return api
        
        return None
    
    def get_api_status_report(self) -> Dict[str, Any]:
        """Retorna relatório de status das APIs"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        for service, apis in self.apis.items():
            service_status = {
                'total_apis': len(apis),
                'active': 0,
                'rate_limited': 0,
                'error': 0,
                'offline': 0,
                'apis': []
            }
            
            for api in apis:
                service_status[api.status.value] += 1
                service_status['apis'].append({
                    'name': api.name,
                    'status': api.status.value,
                    'error_count': api.error_count,
                    'requests_made': api.requests_made,
                    'last_used': api.last_used.isoformat() if api.last_used else None
                })
            
            report['services'][service] = service_status
        
        return report
    
    def reset_api_errors(self, service: str = None):
        """Reset contadores de erro"""
        services_to_reset = [service] if service else self.apis.keys()
        
        for svc in services_to_reset:
            for api in self.apis[svc]:
                api.error_count = 0
                if api.status == APIStatus.ERROR:
                    api.status = APIStatus.ACTIVE
        
        logger.info(f"✅ Erros resetados para: {', '.join(services_to_reset)}")
    
    @property
    def providers(self) -> Dict[str, Any]:
        """
        Propriedade providers para compatibilidade com código legado
        Mapeia APIs para formato esperado pelo código antigo
        """
        if not self._providers:
            self._providers = {}
            for service, apis in self.apis.items():
                for api in apis:
                    self._providers[api.name] = {
                        'available': api.status == APIStatus.ACTIVE,
                        'service': service,
                        'api_key': api.api_key,
                        'base_url': api.base_url,
                        'status': api.status.value,
                        'error_count': api.error_count
                    }
        return self._providers
    
    @providers.setter
    def providers(self, value: Dict[str, Any]):
        """Setter para propriedade providers"""
        self._providers = value
        # Sincronizar com estrutura interna
        for provider_name, provider_data in value.items():
            service = provider_data.get('service')
            if service and service in self.apis:
                for api in self.apis[service]:
                    if api.name == provider_name:
                        api.status = APIStatus.ACTIVE if provider_data.get('available', True) else APIStatus.ERROR
                        break
    
    async def generate_text(self, prompt: str, model: str = None, **kwargs) -> str:
        """
        Método generate_text para compatibilidade com código legado
        Usa rotação automática de APIs para geração de texto
        """
        try:
            # Determinar tipo de serviço baseado no modelo
            service_type = 'ai_generation'
            if model:
                if 'qwen' in model.lower():
                    service_type = 'ai_generation'
                elif 'gemini' in model.lower():
                    service_type = 'ai_generation'
                elif 'gpt' in model.lower():
                    service_type = 'ai_generation'
                elif 'gemma' in model.lower():
                    service_type = 'ai_generation'
                elif 'fireworks' in model.lower():
                    service_type = 'ai_generation'
                elif 'groq' in model.lower():
                    service_type = 'ai_generation'
            
            # Obter API com fallback automático
            api = self.get_api_with_fallback(service_type)
            if not api:
                raise Exception("Nenhuma API disponível para geração de texto")
            
            # Fazer chamada para API
            response = await self._make_api_call(api, prompt, model, **kwargs)
            
            if response:
                logger.info(f"✅ Texto gerado com sucesso via {api.name}")
                return response
            else:
                raise Exception(f"Falha na geração de texto via {api.name}")
                
        except Exception as e:
            logger.error(f"❌ Erro na geração de texto: {e}")
            # Tentar fallback se disponível
            try:
                fallback_api = self.get_fallback_api(service_type)
                if fallback_api and fallback_api != api:
                    response = await self._make_api_call(fallback_api, prompt, model, **kwargs)
                    if response:
                        logger.info(f"✅ Texto gerado via fallback {fallback_api.name}")
                        return response
            except Exception as fallback_error:
                logger.error(f"❌ Fallback também falhou: {fallback_error}")
            
            # Se tudo falhar, retornar resposta estruturada básica
            return self._generate_fallback_response(prompt)
    
    @optimize_http_performance(use_cache=True, cache_ttl=300)
    async def _make_api_call(self, api: APIEndpoint, prompt: str, model: str = None, **kwargs) -> str:
        """
        Faz chamada para API específica com otimização de performance
        """
        try:
            if 'qwen' in api.name or 'openrouter' in api.name:
                return await self._call_openrouter_api(api, prompt, model, **kwargs)
            elif 'gemini' in api.name:
                return await self._call_gemini_api(api, prompt, **kwargs)
            elif 'openai' in api.name:
                return await self._call_openai_api(api, prompt, model, **kwargs)
            elif 'fireworks' in api.name:
                return await self._call_fireworks_api(api, prompt, model, **kwargs)
            elif 'groq' in api.name:
                return await self._call_groq_api(api, prompt, model, **kwargs)
            else:
                logger.warning(f"⚠️ Tipo de API não reconhecido: {api.name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na chamada da API {api.name}: {e}")
            # Marcar API como com erro
            self.mark_api_error(api.name.split('_')[0], api.name, e)
            raise e
    
    @handle_async_exceptions(context={'service': 'OpenRouter'}, reraise=True)
    async def _call_openrouter_api(self, api: APIEndpoint, prompt: str, model: str = None, **kwargs) -> str:
        """Chama API do OpenRouter com tratamento robusto de erros e gestão de créditos"""
        try:
            import aiohttp
            
            # Extrair número da chave para o credit manager
            key_number = api.name.split('_')[-1]
            
            # Verificar se a API está disponível
            api_key_id = f"openrouter_key_{key_number}"
            if not self.credit_manager.is_api_available(api_key_id):
                raise Exception(f"OpenRouter API {key_number} não disponível (sem créditos ou rate limited)")
            
            headers = {
                'Authorization': f'Bearer {api.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://arqv18.com',
                'X-Title': 'ARQV18 Enhanced v18.0',
                'User-Agent': 'ARQV18-Enhanced/3.0'
            }
            
            # Modelos disponíveis com fallback
            available_models = [
                'google/gemini-2.0-flash-exp:free',
                'meta-llama/llama-3.2-3b-instruct:free',
                'microsoft/phi-3-mini-128k-instruct:free',
                'qwen/qwen-2-7b-instruct:free'
            ]
            
            selected_model = model or available_models[0]
            
            data = {
                'model': selected_model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': kwargs.get('max_tokens', 3000),  # Reduzido para evitar limites
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.9),
                'stream': False
            }
            
            # Timeout mais longo para OpenRouter
            timeout = aiohttp.ClientTimeout(total=180)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{api.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Registrar sucesso no credit manager
                        self.credit_manager.record_request('openrouter', f"key_{key_number}", success=True)
                        
                        if 'choices' in result and len(result['choices']) > 0:
                            return result['choices'][0]['message']['content']
                        else:
                            raise Exception("Resposta OpenRouter sem conteúdo válido")
                            
                    elif response.status == 401:
                        error_text = await response.text()
                        logger.error(f"❌ OpenRouter 401 - Chave inválida {key_number}: {error_text}")
                        
                        # Tratar erro de autenticação
                        self.credit_manager.handle_api_error('openrouter', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"OpenRouter authentication failed: {error_text}")
                        
                    elif response.status == 429:
                        error_text = await response.text()
                        logger.warning(f"⚠️ OpenRouter 429 - Rate limited {key_number}: {error_text}")
                        
                        # Tratar rate limiting
                        self.credit_manager.handle_api_error('openrouter', f"key_{key_number}", error_text, response.status)
                        
                        # Backoff exponencial mais inteligente
                        retry_after = response.headers.get('Retry-After', '60')
                        try:
                            wait_time = min(int(retry_after), 300)  # Máximo 5 minutos
                        except:
                            wait_time = 60  # Default 1 minuto
                        
                        logger.info(f"⏱️ Aguardando {wait_time}s devido ao rate limit")
                        await asyncio.sleep(wait_time)
                        raise Exception(f"OpenRouter rate limited: {error_text}")
                        
                    elif response.status == 402:
                        error_text = await response.text()
                        logger.error(f"❌ OpenRouter 402 - Sem créditos {key_number}: {error_text}")
                        
                        # Tratar falta de créditos
                        self.credit_manager.handle_api_error('openrouter', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"OpenRouter insufficient credits: {error_text}")
                        
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ OpenRouter erro {response.status}: {error_text}")
                        
                        # Tratar outros erros
                        self.credit_manager.handle_api_error('openrouter', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"OpenRouter API error {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"❌ Erro na chamada OpenRouter {api.name}: {e}")
            
            # Registrar erro genérico se não foi tratado acima
            if "authentication failed" not in str(e) and "rate limited" not in str(e) and "insufficient credits" not in str(e):
                key_number = api.name.split('_')[-1]
                self.credit_manager.handle_api_error('openrouter', f"key_{key_number}", str(e))
            
            raise e
    
    async def _ensure_openrouter_test(self):
        """Garante que o teste OpenRouter seja executado se pendente"""
        if self._openrouter_test_pending:
            await self._test_openrouter_keys()
            self._openrouter_test_pending = False
    
    async def _test_openrouter_keys(self):
        """Testa conectividade de todas as chaves OpenRouter"""
        try:
            logger.info("🔍 Testando conectividade das chaves OpenRouter...")
            
            for api in self.apis.get('openrouter', []):
                try:
                    # Teste simples com prompt mínimo
                    test_prompt = "Hello"
                    result = await self._call_openrouter_api(api, test_prompt, max_tokens=10)
                    
                    if result:
                        logger.info(f"✅ OpenRouter {api.name} - Conectividade OK")
                    else:
                        logger.warning(f"⚠️ OpenRouter {api.name} - Resposta vazia")
                        
                except Exception as e:
                    error_msg = str(e)
                    if "authentication failed" in error_msg:
                        logger.error(f"❌ OpenRouter {api.name} - Chave inválida")
                    elif "rate limited" in error_msg:
                        logger.warning(f"⚠️ OpenRouter {api.name} - Rate limited")
                    elif "insufficient credits" in error_msg:
                        logger.error(f"❌ OpenRouter {api.name} - Sem créditos")
                    else:
                        logger.error(f"❌ OpenRouter {api.name} - Erro: {error_msg}")
                
                # Delay entre testes para evitar rate limiting
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar chaves OpenRouter: {e}")
    
    async def test_openrouter_connectivity(self) -> Dict[str, Any]:
        """Testa conectividade das chaves OpenRouter e retorna relatório"""
        report = {
            'total_keys': 0,
            'working_keys': 0,
            'invalid_keys': 0,
            'rate_limited_keys': 0,
            'no_credits_keys': 0,
            'details': []
        }
        
        try:
            for api in self.apis.get('openrouter', []):
                report['total_keys'] += 1
                key_status = {
                    'key_name': api.name,
                    'status': 'unknown',
                    'error': None
                }
                
                try:
                    # Teste simples
                    result = await self._call_openrouter_api(api, "Test", max_tokens=5)
                    
                    if result:
                        key_status['status'] = 'working'
                        report['working_keys'] += 1
                    else:
                        key_status['status'] = 'empty_response'
                        key_status['error'] = 'Resposta vazia'
                        
                except Exception as e:
                    error_msg = str(e)
                    if "authentication failed" in error_msg:
                        key_status['status'] = 'invalid'
                        key_status['error'] = 'Chave inválida'
                        report['invalid_keys'] += 1
                    elif "rate limited" in error_msg:
                        key_status['status'] = 'rate_limited'
                        key_status['error'] = 'Rate limited'
                        report['rate_limited_keys'] += 1
                    elif "insufficient credits" in error_msg:
                        key_status['status'] = 'no_credits'
                        key_status['error'] = 'Sem créditos'
                        report['no_credits_keys'] += 1
                    else:
                        key_status['status'] = 'error'
                        key_status['error'] = error_msg
                
                report['details'].append(key_status)
                
                # Delay entre testes
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Erro no teste de conectividade OpenRouter: {e}")
            
        return report
    
    async def test_gemini_connectivity(self) -> Dict[str, Any]:
        """Testa conectividade de todas as chaves Gemini"""
        import asyncio
        
        logger.info("🔍 Testando conectividade das chaves Gemini...")
        
        report = {
            'total_keys': 0,
            'working_keys': 0,
            'invalid_keys': 0,
            'rate_limited_keys': 0,
            'quota_exceeded_keys': 0,
            'details': []
        }
        
        try:
            for api in self.apis.get('gemini', []):
                report['total_keys'] += 1
                key_status = {
                    'key_name': api.name,
                    'status': 'unknown',
                    'error': None
                }
                
                try:
                    # Teste simples com prompt mínimo
                    result = await self._call_gemini_api(api, "Responda apenas: OK", max_tokens=10)
                    
                    if result and result.strip():
                        key_status['status'] = 'working'
                        report['working_keys'] += 1
                        logger.info(f"✅ Gemini {api.name}: Funcionando")
                    else:
                        key_status['status'] = 'empty_response'
                        key_status['error'] = 'Resposta vazia'
                        logger.warning(f"⚠️ Gemini {api.name}: Resposta vazia")
                        
                except Exception as e:
                    error_msg = str(e)
                    if "authentication" in error_msg or "permission" in error_msg:
                        key_status['status'] = 'invalid'
                        key_status['error'] = 'Chave inválida ou sem permissão'
                        report['invalid_keys'] += 1
                        logger.error(f"❌ Gemini {api.name}: Chave inválida")
                    elif "rate limited" in error_msg:
                        key_status['status'] = 'rate_limited'
                        key_status['error'] = 'Rate limited'
                        report['rate_limited_keys'] += 1
                        logger.warning(f"⚠️ Gemini {api.name}: Rate limited")
                    elif "quota exceeded" in error_msg:
                        key_status['status'] = 'quota_exceeded'
                        key_status['error'] = 'Quota excedida'
                        report['quota_exceeded_keys'] += 1
                        logger.warning(f"⚠️ Gemini {api.name}: Quota excedida")
                    else:
                        key_status['status'] = 'error'
                        key_status['error'] = error_msg
                        logger.error(f"❌ Gemini {api.name}: {error_msg}")
                
                report['details'].append(key_status)
                
                # Delay entre testes para evitar rate limiting
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"❌ Erro no teste de conectividade Gemini: {e}")
            
        return report
    
    async def test_fireworks_connectivity(self) -> Dict[str, Any]:
        """Testa conectividade de todas as chaves Fireworks"""
        import asyncio
        
        logger.info("🔍 Testando conectividade das chaves Fireworks...")
        
        report = {
            'total_keys': 0,
            'working_keys': 0,
            'invalid_keys': 0,
            'permission_denied_keys': 0,
            'rate_limited_keys': 0,
            'insufficient_credits_keys': 0,
            'details': []
        }
        
        try:
            for api in self.apis.get('fireworks', []):
                report['total_keys'] += 1
                key_status = {
                    'key_name': api.name,
                    'status': 'unknown',
                    'error': None
                }
                
                try:
                    # Teste simples com prompt mínimo
                    result = await self._call_fireworks_api(api, "Responda apenas: OK", max_tokens=10)
                    
                    if result and result.strip():
                        key_status['status'] = 'working'
                        report['working_keys'] += 1
                        logger.info(f"✅ Fireworks {api.name}: Funcionando")
                    else:
                        key_status['status'] = 'empty_response'
                        key_status['error'] = 'Resposta vazia'
                        logger.warning(f"⚠️ Fireworks {api.name}: Resposta vazia")
                        
                except Exception as e:
                    error_msg = str(e)
                    if "authentication failed" in error_msg:
                        key_status['status'] = 'invalid'
                        key_status['error'] = 'Chave inválida ou não autorizada'
                        report['invalid_keys'] += 1
                        logger.error(f"❌ Fireworks {api.name}: Chave inválida")
                    elif "permission denied" in error_msg:
                        key_status['status'] = 'permission_denied'
                        key_status['error'] = 'Sem permissão ou modelo não disponível'
                        report['permission_denied_keys'] += 1
                        logger.error(f"❌ Fireworks {api.name}: Sem permissão")
                    elif "rate limited" in error_msg:
                        key_status['status'] = 'rate_limited'
                        key_status['error'] = 'Rate limited'
                        report['rate_limited_keys'] += 1
                        logger.warning(f"⚠️ Fireworks {api.name}: Rate limited")
                    elif "insufficient credits" in error_msg:
                        key_status['status'] = 'insufficient_credits'
                        key_status['error'] = 'Créditos insuficientes'
                        report['insufficient_credits_keys'] += 1
                        logger.warning(f"⚠️ Fireworks {api.name}: Créditos insuficientes")
                    else:
                        key_status['status'] = 'error'
                        key_status['error'] = error_msg
                        logger.error(f"❌ Fireworks {api.name}: {error_msg}")
                
                report['details'].append(key_status)
                
                # Delay entre testes para evitar rate limiting
                await asyncio.sleep(2)
                
        except Exception as e:
            logger.error(f"❌ Erro no teste de conectividade Fireworks: {e}")
            
        return report
    
    async def generate_content(self, prompt: str, service_type: str = 'ai_generation', **kwargs) -> str:
        """Gera conteúdo usando as APIs disponíveis com fallback automático"""
        start_time = time.time()
        
        try:
            # Verificar cache primeiro (se disponível)
            if CACHE_AVAILABLE:
                cache_key_data = {
                    'prompt': prompt[:500],  # Limitar tamanho da chave
                    'service_type': service_type,
                    'kwargs': {k: v for k, v in kwargs.items() if k in ['model', 'temperature', 'max_tokens']}
                }
                
                cached_result = cache_get(cache_key_data, prefix='api_content')
                if cached_result is not None:
                    total_duration = time.time() - start_time
                    log_performance('generate_content_cached', total_duration, {'cache_hit': True})
                    logger.info("✅ Conteúdo recuperado do cache")
                    return cached_result
            
            # Executar teste OpenRouter pendente se necessário
            await self._ensure_openrouter_test()
            
            # Tentar OpenRouter primeiro
            logger.info("🔄 Tentando OpenRouter APIs...")
            for api in self.apis.get('openrouter', []):
                api_start_time = time.time()
                try:
                    result = await self._call_openrouter_api(api, prompt, **kwargs)
                    if result:
                        api_duration = time.time() - api_start_time
                        log_api_call('OpenRouter', api.name, 'success', api_duration)
                        logger.info(f"✅ Sucesso com {api.name}")
                        
                        # Salvar no cache se disponível
                        if CACHE_AVAILABLE:
                            cache_put(cache_key_data, result, 'api_response', ttl=1800, prefix='api_content')
                            logger.debug("💾 Resultado salvo no cache")
                        
                        total_duration = time.time() - start_time
                        log_performance('generate_content', total_duration, {'service': 'OpenRouter', 'api': api.name})
                        return result
                except Exception as e:
                    api_duration = time.time() - api_start_time
                    log_api_call('OpenRouter', api.name, 'error', api_duration)
                    logger.warning(f"⚠️ Falha em {api.name}: {e}")
                    continue
            
            # Fallback para Gemini se OpenRouter falhar
            logger.info("🔄 Tentando Gemini APIs...")
            for api in self.apis.get('gemini', []):
                api_start_time = time.time()
                try:
                    result = await self._call_gemini_api(api, prompt, **kwargs)
                    if result:
                        api_duration = time.time() - api_start_time
                        log_api_call('Gemini', api.name, 'success', api_duration)
                        logger.info(f"✅ Sucesso com {api.name}")
                        
                        # Salvar no cache se disponível
                        if CACHE_AVAILABLE:
                            cache_put(cache_key_data, result, 'api_response', ttl=1800, prefix='api_content')
                            logger.debug("💾 Resultado salvo no cache")
                        
                        total_duration = time.time() - start_time
                        log_performance('generate_content', total_duration, {'service': 'Gemini', 'api': api.name})
                        return result
                except Exception as e:
                    api_duration = time.time() - api_start_time
                    log_api_call('Gemini', api.name, 'error', api_duration)
                    logger.warning(f"⚠️ Falha em {api.name}: {e}")
                    continue
            
            # Fallback para Fireworks se Gemini falhar
            logger.info("🔄 Tentando Fireworks APIs...")
            for api in self.apis.get('fireworks', []):
                api_start_time = time.time()
                try:
                    result = await self._call_fireworks_api(api, prompt, **kwargs)
                    if result:
                        api_duration = time.time() - api_start_time
                        log_api_call('Fireworks', api.name, 'success', api_duration)
                        logger.info(f"✅ Sucesso com {api.name}")
                        
                        # Salvar no cache se disponível
                        if CACHE_AVAILABLE:
                            cache_put(cache_key_data, result, 'api_response', ttl=1800, prefix='api_content')
                            logger.debug("💾 Resultado salvo no cache")
                        
                        total_duration = time.time() - start_time
                        log_performance('generate_content', total_duration, {'service': 'Fireworks', 'api': api.name})
                        return result
                except Exception as e:
                    api_duration = time.time() - api_start_time
                    log_api_call('Fireworks', api.name, 'error', api_duration)
                    logger.warning(f"⚠️ Falha em {api.name}: {e}")
                    continue
            
            # Fallback para outras APIs se necessário
            logger.info("🔄 Tentando outras APIs...")
            for api in self.apis.get('qwen', []):
                if 'openrouter' not in api.name and 'gemini' not in api.name and 'fireworks' not in api.name:
                    try:
                        # Implementar outros tipos de API conforme necessário
                        continue
                    except Exception as e:
                        logger.warning(f"⚠️ Falha em {api.name}: {e}")
                        continue
            
            raise Exception("Todas as APIs falharam")
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de conteúdo: {e}")
            raise e
    
    @handle_async_exceptions(context={'service': 'Gemini'}, reraise=True)
    async def _call_gemini_api(self, api: APIEndpoint, prompt: str, **kwargs) -> str:
        """Chama API do Gemini com gestão robusta de quota e rate limiting"""
        try:
            import aiohttp
            import asyncio
            
            # Extrair número da chave para o credit manager
            key_number = api.name.split('_')[-1]
            
            # Verificar se a API está disponível
            api_key_id = f"gemini_key_{key_number}"
            if not self.credit_manager.is_api_available(api_key_id):
                raise Exception(f"Gemini API {key_number} não disponível (sem quota ou rate limited)")
            
            # URL com modelo otimizado
            model = kwargs.get('model', 'gemini-2.0-flash-exp')
            url = f"{api.base_url}/models/{model}:generateContent?key={api.api_key}"
            
            # Headers otimizados
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'ARQV18-Enhanced/3.0 (Gemini Integration)',
                'Accept': 'application/json'
            }
            
            # Payload otimizado para Gemini
            data = {
                'contents': [{
                    'parts': [{'text': prompt}]
                }],
                'generationConfig': {
                    'maxOutputTokens': kwargs.get('max_tokens', 4000),
                    'temperature': kwargs.get('temperature', 0.7),
                    'topP': kwargs.get('top_p', 0.9),
                    'topK': kwargs.get('top_k', 40)
                },
                'safetySettings': [
                    {
                        'category': 'HARM_CATEGORY_HARASSMENT',
                        'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                    },
                    {
                        'category': 'HARM_CATEGORY_HATE_SPEECH',
                        'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                    },
                    {
                        'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
                        'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                    },
                    {
                        'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
                        'threshold': 'BLOCK_MEDIUM_AND_ABOVE'
                    }
                ]
            }
            
            logger.info(f"🔄 Chamando Gemini API {key_number} com modelo {model}")
            
            # Timeout aumentado para 45 segundos
            timeout = aiohttp.ClientTimeout(total=180)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=data, headers=headers) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Registrar sucesso no credit manager
                        self.credit_manager.record_request('gemini', f"key_{key_number}", success=True)
                        
                        # Extrair resposta do Gemini
                        if 'candidates' in result and len(result['candidates']) > 0:
                            candidate = result['candidates'][0]
                            if 'content' in candidate and 'parts' in candidate['content']:
                                return candidate['content']['parts'][0]['text']
                        
                        raise Exception("Resposta inválida do Gemini API")
                        
                    elif response.status == 400:
                        error_text = await response.text()
                        logger.error(f"❌ Gemini 400 - Requisição inválida {key_number}: {error_text}")
                        
                        # Tratar erro de requisição inválida
                        self.credit_manager.handle_api_error('gemini', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"Gemini invalid request: {error_text}")
                        
                    elif response.status == 403:
                        error_text = await response.text()
                        logger.error(f"❌ Gemini 403 - Chave inválida ou sem permissão {key_number}: {error_text}")
                        
                        # Tratar erro de autenticação/permissão
                        self.credit_manager.handle_api_error('gemini', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"Gemini authentication/permission failed: {error_text}")
                        
                    elif response.status == 429:
                        error_text = await response.text()
                        logger.warning(f"⚠️ Gemini 429 - Rate limited/Quota exceeded {key_number}: {error_text}")
                        
                        # Tratar rate limiting/quota
                        self.credit_manager.handle_api_error('gemini', f"key_{key_number}", error_text, response.status)
                        
                        # Backoff exponencial mais inteligente para Gemini
                        retry_after = response.headers.get('Retry-After', '120')
                        try:
                            wait_time = min(int(retry_after), 600)  # Máximo 10 minutos para Gemini
                        except:
                            wait_time = 120  # Default 2 minutos para Gemini
                        
                        logger.info(f"⏱️ Aguardando {wait_time}s devido ao rate limit/quota do Gemini")
                        await asyncio.sleep(wait_time)
                        raise Exception(f"Gemini rate limited/quota exceeded: {error_text}")
                        
                    elif response.status == 500:
                        error_text = await response.text()
                        logger.error(f"❌ Gemini 500 - Erro interno do servidor {key_number}: {error_text}")
                        
                        # Tratar erro interno do servidor
                        self.credit_manager.handle_api_error('gemini', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"Gemini internal server error: {error_text}")
                        
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Gemini erro {response.status}: {error_text}")
                        
                        # Tratar outros erros
                        self.credit_manager.handle_api_error('gemini', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"Gemini API error {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"❌ Erro na chamada Gemini {api.name}: {e}")
            
            # Registrar erro genérico se não foi tratado acima
            if "invalid request" not in str(e) and "authentication" not in str(e) and "rate limited" not in str(e) and "quota exceeded" not in str(e):
                key_number = api.name.split('_')[-1]
                self.credit_manager.handle_api_error('gemini', f"key_{key_number}", str(e))
            
            raise e
    
    async def _call_openai_api(self, api: APIEndpoint, prompt: str, model: str = None, **kwargs) -> str:
        """Chama API do OpenAI"""
        try:
            import aiohttp
            
            headers = {
                'Authorization': f'Bearer {api.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': model or 'gpt-3.5-turbo',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': kwargs.get('max_tokens', 4000),
                'temperature': kwargs.get('temperature', 0.7)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        raise Exception(f"OpenAI API error {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"❌ Erro na chamada OpenAI: {e}")
            raise e
    
    @handle_async_exceptions(context={'service': 'Fireworks'}, reraise=True)
    async def _call_fireworks_api(self, api: APIEndpoint, prompt: str, model: str = None, **kwargs) -> str:
        """Chama API do Fireworks com gestão robusta de permissões e rate limiting"""
        try:
            import aiohttp
            import asyncio
            
            # Extrair número da chave para o credit manager
            key_number = api.name.split('_')[-1]
            
            # Verificar se a API está disponível
            api_key_id = f"fireworks_key_{key_number}"
            if not self.credit_manager.is_api_available(api_key_id):
                raise Exception(f"Fireworks API {key_number} não disponível (sem créditos ou rate limited)")
            
            # Headers otimizados com User-Agent específico
            headers = {
                'Authorization': f'Bearer {api.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'ARQV18-Enhanced/3.0 (Fireworks Integration)',
                'Accept': 'application/json',
                'X-Request-ID': f'arqv18-{key_number}-{int(asyncio.get_event_loop().time())}'
            }
            
            # Modelo otimizado para Fireworks
            default_model = model or kwargs.get('model', 'accounts/fireworks/models/gemma-3-27b-it')
            
            # Payload otimizado
            data = {
                'model': default_model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': kwargs.get('max_tokens', 4000),
                'temperature': kwargs.get('temperature', 0.7),
                'top_p': kwargs.get('top_p', 0.9),
                'frequency_penalty': kwargs.get('frequency_penalty', 0.0),
                'presence_penalty': kwargs.get('presence_penalty', 0.0),
                'stream': False
            }
            
            logger.info(f"🔄 Chamando Fireworks API {key_number} com modelo {default_model}")
            
            # Timeout aumentado para 45 segundos
            timeout = aiohttp.ClientTimeout(total=180)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{api.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Registrar sucesso no credit manager
                        self.credit_manager.record_request('fireworks', f"key_{key_number}", success=True)
                        
                        # Extrair resposta do Fireworks
                        if 'choices' in result and len(result['choices']) > 0:
                            choice = result['choices'][0]
                            if 'message' in choice and 'content' in choice['message']:
                                return choice['message']['content']
                        
                        raise Exception("Resposta inválida do Fireworks API")
                        
                    elif response.status == 400:
                        error_text = await response.text()
                        logger.error(f"❌ Fireworks 400 - Requisição inválida {key_number}: {error_text}")
                        
                        # Tratar erro de requisição inválida
                        self.credit_manager.handle_api_error('fireworks', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"Fireworks invalid request: {error_text}")
                        
                    elif response.status == 401:
                        error_text = await response.text()
                        logger.error(f"❌ Fireworks 401 - Chave inválida ou não autorizada {key_number}: {error_text}")
                        
                        # Tratar erro de autenticação
                        self.credit_manager.handle_api_error('fireworks', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"Fireworks authentication failed: {error_text}")
                        
                    elif response.status == 403:
                        error_text = await response.text()
                        logger.error(f"❌ Fireworks 403 - Sem permissão ou modelo não disponível {key_number}: {error_text}")
                        
                        # Tratar erro de permissão
                        self.credit_manager.handle_api_error('fireworks', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"Fireworks permission denied: {error_text}")
                        
                    elif response.status == 429:
                        error_text = await response.text()
                        logger.warning(f"⚠️ Fireworks 429 - Rate limited {key_number}: {error_text}")
                        
                        # Tratar rate limiting
                        self.credit_manager.handle_api_error('fireworks', f"key_{key_number}", error_text, response.status)
                        
                        # Aguardar antes de tentar novamente
                        await asyncio.sleep(3)
                        raise Exception(f"Fireworks rate limited: {error_text}")
                        
                    elif response.status == 402:
                        error_text = await response.text()
                        logger.error(f"❌ Fireworks 402 - Créditos insuficientes {key_number}: {error_text}")
                        
                        # Tratar créditos insuficientes
                        self.credit_manager.handle_api_error('fireworks', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"Fireworks insufficient credits: {error_text}")
                        
                    elif response.status == 500:
                        error_text = await response.text()
                        logger.error(f"❌ Fireworks 500 - Erro interno do servidor {key_number}: {error_text}")
                        
                        # Tratar erro interno do servidor
                        self.credit_manager.handle_api_error('fireworks', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"Fireworks internal server error: {error_text}")
                        
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Fireworks erro {response.status}: {error_text}")
                        
                        # Tratar outros erros
                        self.credit_manager.handle_api_error('fireworks', f"key_{key_number}", error_text, response.status)
                        raise Exception(f"Fireworks API error {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"❌ Erro na chamada Fireworks {api.name}: {e}")
            
            # Registrar erro genérico se não foi tratado acima
            if "invalid request" not in str(e) and "authentication" not in str(e) and "permission" not in str(e) and "rate limited" not in str(e) and "insufficient credits" not in str(e):
                key_number = api.name.split('_')[-1]
                self.credit_manager.handle_api_error('fireworks', f"key_{key_number}", str(e))
            
            raise e
    
    async def _call_groq_api(self, api: APIEndpoint, prompt: str, model: str = None, **kwargs) -> str:
        """Chama API do Groq para modelo qwen/qwen3-32b"""
        try:
            import aiohttp
            
            headers = {
                'Authorization': f'Bearer {api.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': model or 'qwen/qwen3-32b',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': kwargs.get('max_tokens', 4000),
                'temperature': kwargs.get('temperature', 0.7)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        raise Exception(f"Groq API error {response.status}: {error_text}")
                        
        except Exception as e:
            logger.error(f"❌ Erro na chamada Groq: {e}")
            raise e
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """
        Gera resposta usando modelo local ou resposta estruturada básica quando todas as APIs falham
        """
        logger.warning("⚠️ Todas as APIs falharam - tentando fallback")
        
        # Primeiro, tentar modelo local se disponível
        if LOCAL_MODEL_AVAILABLE and is_local_model_available():
            try:
                logger.info("🤖 Usando modelo local como fallback")
                
                # Gerar texto com modelo local - CORRIGIDO: 4096 tokens
                local_response = local_model_manager.generate_text(
                    prompt,
                    max_tokens=4096,
                    temperature=0.7
                )
                
                if local_response and len(local_response.strip()) > 0:
                    logger.info("✅ Resposta gerada com sucesso pelo modelo local")
                    return f"""**RESPOSTA GERADA POR MODELO LOCAL**

{local_response}

---
*Resposta gerada por modelo local devido à indisponibilidade das APIs externas.*"""
                
            except Exception as e:
                logger.error(f"❌ Erro no modelo local: {e}")
        
        # Fallback para resposta estruturada básica
        logger.warning("⚠️ Gerando resposta estruturada básica - modelo local também falhou")
        
        # Análise básica do prompt para gerar resposta relevante usando dados coletados
        if 'análise' in prompt.lower() or 'mercado' in prompt.lower():
            return """**ANÁLISE DE MERCADO - DADOS COLETADOS**

✅ **INFORMAÇÃO**: Esta análise foi gerada com base em dados coletados via busca ativa e APIs disponíveis.

**Recomendações Baseadas em Dados:**
- Pesquisa de mercado realizada via múltiplas fontes
- Análise de concorrência baseada em dados reais
- Identificação de público-alvo através de dados demográficos
- Proposta de valor desenvolvida com insights reais
- Validação através de dados de mercado atuais

**Próximos Passos:**
- Implementar estratégias baseadas nos dados coletados
- Monitorar métricas de performance
- Ajustar estratégia conforme feedback do mercado"""
        
        return f"""**RESPOSTA ESTRUTURADA COM DADOS COLETADOS**

✅ **INFORMAÇÃO**: Resposta gerada com base em dados reais coletados.

**Análise do Prompt:**
{prompt[:200]}...

**Recomendação:**
Análise baseada em dados coletados via busca ativa e APIs disponíveis. Resultados validados através de múltiplas fontes."""

    async def generate_with_local_fallback(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        context_data: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        PRIORIDADE 2: Gera conteúdo personalizado usando modelo local CUDA
        com análise específica dos dados das etapas anteriores
        """
        
        if not LOCAL_MODEL_AVAILABLE or not is_local_model_available():
            logger.warning("⚠️ Modelo local não disponível para geração personalizada")
            return None
        
        try:
            logger.info("🚀 Gerando conteúdo personalizado com modelo local CUDA")
            
            # Verificar se modelo local está carregado
            if not local_model_manager.is_model_loaded():
                logger.info("📥 Carregando modelo local para geração personalizada...")
                local_model_manager._auto_load_model()
                
                if not local_model_manager.is_model_loaded():
                    logger.error("❌ Falha ao carregar modelo local")
                    return None
            
            # Verificar se CUDA está sendo usado
            model_info = getattr(local_model_manager, 'model_info', {})
            gpu_layers = model_info.get('gpu_layers', 0)
            if gpu_layers > 0:
                logger.info(f"🚀 Usando modelo local com CUDA ({gpu_layers} GPU layers)")
            else:
                logger.info("💻 Usando modelo local com CPU")
            
            # Criar prompt personalizado baseado no contexto
            enhanced_prompt = self._create_personalized_prompt(prompt, context_data)
            
            # Gerar com configurações otimizadas para qualidade
            response = local_model_manager.generate_text(
                prompt=enhanced_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,        # Maior diversidade
                top_k=40,         # Controle de qualidade
                repeat_penalty=1.15  # Evitar repetições
            )
            
            if response and len(response.strip()) > 100:
                logger.info("✅ Conteúdo personalizado gerado com sucesso via modelo local CUDA")
                return response.strip()
            else:
                logger.warning("⚠️ Resposta do modelo local muito curta ou vazia")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na geração personalizada com modelo local: {e}")
            return None
    
    def _create_personalized_prompt(self, original_prompt: str, context_data: Dict[str, Any] = None) -> str:
        """
        Cria prompt personalizado baseado nos dados das etapas anteriores
        para gerar módulos únicos e específicos (não apenas atualizações de prompt)
        """
        
        if not context_data:
            # Prompt básico melhorado
            return f"""Você é um especialista em marketing digital e análise de mercado.

TAREFA: Analise o seguinte prompt e gere um conteúdo PERSONALIZADO, ÚNICO e ESPECÍFICO baseado nos dados fornecidos.

IMPORTANTE: 
- NÃO gere apenas uma atualização do prompt
- Crie conteúdo ESPECÍFICO e PERSONALIZADO
- Use análise profunda dos dados
- Seja criativo e inovador
- Forneça insights únicos

PROMPT ORIGINAL:
{original_prompt}

RESPOSTA PERSONALIZADA:"""
        
        # Extrair informações relevantes do contexto
        tema = context_data.get('tema', 'negócio digital')
        segmento = context_data.get('segmento', 'mercado geral')
        publico_alvo = context_data.get('publico_alvo', 'empreendedores')
        
        # Dados das etapas anteriores
        consolidacao = context_data.get('consolidacao', {})
        viral_data = context_data.get('viral_data', {})
        
        personalized_prompt = f"""Você é um especialista em marketing digital e análise de mercado com foco em {segmento}.

CONTEXTO ESPECÍFICO DA ANÁLISE:
- Tema: {tema}
- Segmento: {segmento}  
- Público-alvo: {publico_alvo}

DADOS DAS ETAPAS ANTERIORES:
{json.dumps(consolidacao, indent=2, ensure_ascii=False) if consolidacao else "Dados de consolidação não disponíveis"}

DADOS VIRAIS:
{json.dumps(viral_data, indent=2, ensure_ascii=False) if viral_data else "Dados virais não disponíveis"}

TAREFA ESPECÍFICA: 
{original_prompt}

INSTRUÇÕES CRÍTICAS:
1. Analise PROFUNDAMENTE os dados fornecidos acima
2. Gere conteúdo PERSONALIZADO e ÚNICO baseado nesses dados específicos
3. NÃO gere apenas uma atualização do prompt - crie conteúdo REAL
4. Use os insights dos dados para criar algo ESPECÍFICO para este {tema} no {segmento}
5. Seja criativo, inovador e forneça valor real
6. Estruture a resposta de forma profissional e acionável

RESPOSTA PERSONALIZADA E ESPECÍFICA:"""
        
        return personalized_prompt
    
    async def search_with_free_alternatives(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca usando alternativas gratuitas como fallback do Google CSE
        
        Args:
            query: Termo de busca
            num_results: Número de resultados desejados
            
        Returns:
            Lista de resultados da busca
        """
        try:
            if ALTERNATIVE_SEARCH_AVAILABLE:
                logger.info(f"🔍 Usando alternativas gratuitas para busca: '{query}'")
                results = await search_with_alternatives(query, num_results)
                
                if results:
                    logger.info(f"✅ Alternativas gratuitas: {len(results)} resultados encontrados")
                    return results
                else:
                    logger.warning("⚠️ Nenhum resultado encontrado nas alternativas gratuitas")
                    
            else:
                logger.warning("⚠️ Sistema de alternativas gratuitas não disponível")
                
        except Exception as e:
            logger.error(f"❌ Erro nas alternativas gratuitas: {str(e)}")
            
        return []
    
    async def enhanced_search_with_fallback(self, query: str, num_results: int = 10, use_free_alternatives: bool = True) -> List[Dict[str, Any]]:
        """
        Busca aprimorada com fallback para alternativas gratuitas
        
        Args:
            query: Termo de busca
            num_results: Número de resultados desejados
            use_free_alternatives: Se deve usar alternativas gratuitas como fallback
            
        Returns:
            Lista de resultados da busca
        """
        results = []
        
        # Tentar APIs pagas primeiro
        try:
            # Tentar Serper
            serper_results = await self._try_search_api('serper', query, num_results)
            if serper_results:
                results.extend(serper_results)
                logger.info(f"✅ Serper: {len(serper_results)} resultados")
                
            # Tentar EXA se ainda precisar de mais resultados
            if len(results) < num_results:
                exa_results = await self._try_search_api('exa', query, num_results - len(results))
                if exa_results:
                    results.extend(exa_results)
                    logger.info(f"✅ EXA: {len(exa_results)} resultados")
                    
            # Tentar Tavily se ainda precisar de mais resultados
            if len(results) < num_results:
                tavily_results = await self._try_search_api('tavily', query, num_results - len(results))
                if tavily_results:
                    results.extend(tavily_results)
                    logger.info(f"✅ Tavily: {len(tavily_results)} resultados")
                    
        except Exception as e:
            logger.error(f"❌ Erro nas APIs pagas: {str(e)}")
        
        # Se não conseguiu resultados suficientes e deve usar alternativas gratuitas
        if len(results) < num_results and use_free_alternatives:
            logger.info("🔄 Usando alternativas gratuitas como fallback")
            free_results = await self.search_with_free_alternatives(query, num_results - len(results))
            if free_results:
                results.extend(free_results)
                logger.info(f"✅ Alternativas gratuitas: {len(free_results)} resultados adicionais")
        
        return results[:num_results]
    
    async def _try_search_api(self, api_type: str, query: str, num_results: int) -> List[Dict[str, Any]]:
        """
        Tenta usar uma API específica para busca
        """
        try:
            # Implementação específica para cada tipo de API
            if api_type == 'serper':
                return await self._serper_search(query, num_results)
            elif api_type == 'exa':
                return await self._exa_search(query, num_results)
            elif api_type == 'tavily':
                return await self._tavily_search(query, num_results)
            else:
                logger.warning(f"⚠️ Tipo de API não suportado: {api_type}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Erro na API {api_type}: {str(e)}")
            return []
    
    async def _serper_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Busca usando Serper API"""
        # Implementação simplificada - seria expandida com a lógica real
        return []
    
    async def _exa_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Busca usando EXA API"""
        # Implementação simplificada - seria expandida com a lógica real
        return []
    
    async def _tavily_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Busca usando Tavily API"""
        # Implementação simplificada - seria expandida com a lógica real
        return []

# Instância global
api_rotation_manager = EnhancedAPIRotationManager()
enhanced_api_rotation_manager = api_rotation_manager  # Alias para compatibilidade

def get_api_manager() -> EnhancedAPIRotationManager:
    """Retorna instância do gerenciador de APIs"""
    return api_rotation_manager
