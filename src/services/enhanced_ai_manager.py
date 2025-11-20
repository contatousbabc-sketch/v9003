#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Enhanced AI Manager
Gerenciador de IA com hierarquia OpenRouter: Gemini-2.0 Flash → Gemini Direct e fallbacks robustos
ZERO SIMULAÇÃO - Apenas modelos reais funcionais
Com delay de 10s entre requisições e rotação inteligente de APIs
"""

import os
import logging
import asyncio
import json
import aiohttp
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dotenv import load_dotenv
import time
from pathlib import Path
from utils.advanced_credit_manager import advanced_credit_manager

# Carregar variáveis de ambiente do diretório correto
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logging.info(f"✅ Variáveis de ambiente carregadas de: {env_path}")
else:
    # Fallback para buscar .env em diretórios pais
    current_dir = Path(__file__).parent
    for _ in range(5):  # Buscar até 5 níveis acima
        env_file = current_dir / '.env'
        if env_file.exists():
            load_dotenv(env_file)
            logging.info(f"✅ Variáveis de ambiente carregadas de: {env_file}")
            break
        current_dir = current_dir.parent
    else:
        logging.warning("⚠️ Arquivo .env não encontrado")
        load_dotenv()  # Fallback para comportamento padrão

logger = logging.getLogger(__name__)

class EnhancedAIManager:
    """Gerenciador de IA aprimorado com hierarquia OpenRouter e fallbacks"""

    def __init__(self):
        """Inicializa o gerenciador aprimorado com hierarquia OpenRouter"""
        # Carregar chaves OpenRouter
        self.openrouter_keys = self._load_openrouter_keys()
        self.current_key_index = 0
        
        # Carregar chaves Gemini para fallback
        self.gemini_keys = self._load_gemini_keys()
        self.current_gemini_key_index = 0
        
        # Configurar hierarquia de modelos: 1º Gemini Direct, 2º OpenRouter, 3º Modelo Local
        self.model_hierarchy = [
            {
                'name': 'gemini-2.0-flash-exp',
                'provider': 'gemini_direct',
                'priority': 1,
                'max_tokens': 8000,
                'temperature': 0.7
            },
            {
                'name': 'google/gemini-2.0-flash-exp:free',
                'provider': 'openrouter',
                'priority': 2,
                'max_tokens': 8000,
                'temperature': 0.7
            },
            {
                'name': 'qwen/qwen3-32b',
                'provider': 'groq',
                'priority': 3,
                'max_tokens': 4000,
                'temperature': 0.7
            },
            {
                'name': 'gemma-3-27b-it',
                'provider': 'fireworks',
                'priority': 4,
                'max_tokens': 4000,
                'temperature': 0.7
            },
            {
                'name': 'gpt-4o-mini',
                'provider': 'openai',
                'priority': 5,
                'max_tokens': 4000,
                'temperature': 0.7
            },
            {
                'name': 'local_model',
                'provider': 'local',
                'priority': 6,
                'max_tokens': 4000,
                'temperature': 0.7
            }
        ]
        
        # Controle de rate limiting e delays
        self.last_request_time = 0
        self.request_delay = 10  # 10 segundos entre requisições
        self.request_lock = asyncio.Lock()
        
        # PRIORIDADE 3: Sistema de monitoramento de erros de API
        self.api_error_counts = {}
        self.api_success_counts = {}
        self.last_api_errors = {}
        self.api_health_check_interval = 300  # 5 minutos
        self.api_circuit_breakers = {}  # Circuit breaker para APIs problemáticas
        self.circuit_breaker_timeout = 600  # 10 minutos para reativar API
        
        self.search_orchestrator = None
        
        # Importar search orchestrator se disponível
        try:
            from .real_search_orchestrator import RealSearchOrchestrator
            self.search_orchestrator = RealSearchOrchestrator()
            logger.info("✅ Search Orchestrator carregado")
        except ImportError:
            logger.warning("⚠️ Search Orchestrator não disponível")

        logger.info("🤖 Enhanced AI Manager inicializado com hierarquia Gemini Direct → OpenRouter → Modelo Local")
        logger.info(f"🔑 {len(self.openrouter_keys)} chaves OpenRouter carregadas")
        logger.info(f"🔑 {len(self.gemini_keys)} chaves Gemini carregadas")
        logger.info(f"⏱️ Delay configurado: {self.request_delay}s entre requisições")
    
    def _load_openrouter_keys(self) -> List[str]:
        """Carrega múltiplas chaves OpenRouter"""
        keys = []
        
        # Chave principal
        main_key = os.getenv('OPENROUTER_API_KEY')
        if main_key and main_key.strip():
            keys.append(main_key.strip())
            
        # Chaves numeradas
        for i in range(1, 6):
            key = os.getenv(f'OPENROUTER_API_KEY_{i}')
            if key and key.strip():
                keys.append(key.strip())
                
        logger.info(f"✅ {len(keys)} chaves OpenRouter carregadas")
        return keys
    
    def _load_gemini_keys(self) -> List[str]:
        """Carrega múltiplas chaves Gemini"""
        keys = []
        
        # Chave principal
        main_key = os.getenv('GEMINI_API_KEY')
        if main_key and main_key.strip():
            keys.append(main_key.strip())
            
        # Chaves numeradas
        for i in range(1, 4):
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key and key.strip():
                keys.append(key.strip())
                
        logger.info(f"✅ {len(keys)} chaves Gemini carregadas")
        return keys
    
    def _get_next_openrouter_key(self) -> Optional[str]:
        """Obtém próxima chave OpenRouter com rotação"""
        if not self.openrouter_keys:
            return None
            
        key = self.openrouter_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.openrouter_keys)
        logger.info(f"🔄 Rotacionando para chave OpenRouter #{self.current_key_index + 1}/{len(self.openrouter_keys)}")
        return key
    
    def _get_next_gemini_key(self) -> Optional[str]:
        """Obtém próxima chave Gemini com rotação"""
        if not self.gemini_keys:
            return None
            
        key = self.gemini_keys[self.current_gemini_key_index]
        self.current_gemini_key_index = (self.current_gemini_key_index + 1) % len(self.gemini_keys)
        logger.info(f"🔄 Rotacionando para chave Gemini #{self.current_gemini_key_index + 1}/{len(self.gemini_keys)}")
        return key

    async def _apply_rate_limit_delay(self):
        """Aplica delay de 10 segundos entre requisições"""
        async with self.request_lock:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            
            if time_since_last_request < self.request_delay:
                wait_time = self.request_delay - time_since_last_request
                logger.info(f"⏱️ Aguardando {wait_time:.2f}s antes da próxima requisição...")
                await asyncio.sleep(wait_time)
            
            self.last_request_time = time.time()

    def _record_api_result(self, provider: str, model: str, success: bool, error: str = None):
        """PRIORIDADE 3: Registra resultado de API para monitoramento"""
        api_key = f"{provider}_{model}"
        
        if success:
            self.api_success_counts[api_key] = self.api_success_counts.get(api_key, 0) + 1
            logger.info(f"✅ API {api_key} sucesso (total: {self.api_success_counts[api_key]})")
        else:
            self.api_error_counts[api_key] = self.api_error_counts.get(api_key, 0) + 1
            self.last_api_errors[api_key] = {
                'error': error,
                'timestamp': time.time(),
                'count': self.api_error_counts[api_key]
            }
            logger.error(f"❌ API {api_key} erro #{self.api_error_counts[api_key]}: {error}")
    
    def _get_api_health_status(self) -> Dict[str, Any]:
        """PRIORIDADE 3: Retorna status de saúde das APIs"""
        health_status = {}
        
        for api_key in set(list(self.api_success_counts.keys()) + list(self.api_error_counts.keys())):
            success_count = self.api_success_counts.get(api_key, 0)
            error_count = self.api_error_counts.get(api_key, 0)
            total_requests = success_count + error_count
            
            if total_requests > 0:
                success_rate = success_count / total_requests
                health_status[api_key] = {
                    'success_count': success_count,
                    'error_count': error_count,
                    'success_rate': success_rate,
                    'status': 'healthy' if success_rate > 0.8 else 'degraded' if success_rate > 0.5 else 'unhealthy',
                    'last_error': self.last_api_errors.get(api_key, {}).get('error', 'None')
                }
        
        return health_status
    
    def _should_skip_api(self, provider: str, model: str) -> bool:
        """PRIORIDADE 3: Verifica se deve pular API com muitos erros (Circuit Breaker)"""
        api_key = f"{provider}_{model}"
        error_count = self.api_error_counts.get(api_key, 0)
        success_count = self.api_success_counts.get(api_key, 0)
        current_time = time.time()
        
        # Verificar circuit breaker
        if api_key in self.api_circuit_breakers:
            breaker_time = self.api_circuit_breakers[api_key]
            if current_time - breaker_time < self.circuit_breaker_timeout:
                logger.warning(f"🔴 Circuit breaker ativo para {api_key} - aguardando {int(self.circuit_breaker_timeout - (current_time - breaker_time))}s")
                return True
            else:
                # Timeout expirou, remover circuit breaker
                del self.api_circuit_breakers[api_key]
                logger.info(f"🟢 Circuit breaker removido para {api_key} - tentando novamente")
        
        # Ativar circuit breaker se muitos erros
        if error_count > 8 and success_count == 0:
            self.api_circuit_breakers[api_key] = current_time
            logger.error(f"🔴 Circuit breaker ativado para {api_key} - muitos erros ({error_count})")
            return True
        
        # Pular se taxa de erro for muito alta (>85%)
        total_requests = success_count + error_count
        if total_requests > 15 and (error_count / total_requests) > 0.85:
            self.api_circuit_breakers[api_key] = current_time
            logger.error(f"🔴 Circuit breaker ativado para {api_key} - taxa de erro alta ({error_count}/{total_requests})")
            return True
        
        return False

    async def _generate_with_openrouter(
        self,
        prompt: str,
        model_name: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        max_retries: int = 3
    ) -> Optional[str]:
        """Gera conteúdo usando OpenRouter com rotação de chaves, delay e retry logic aprimorado"""
        
        # Preparar mensagens
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # PRIORIDADE 3: Verificar se deve pular esta API
        if self._should_skip_api('openrouter', model_name):
            logger.warning(f"⚠️ Pulando OpenRouter {model_name} devido a muitos erros")
            return None
        
        # Tentar com todas as chaves disponíveis
        for attempt in range(len(self.openrouter_keys)):
            # Aplicar delay antes de cada requisição
            await self._apply_rate_limit_delay()
            
            api_key = self._get_next_openrouter_key()
            if not api_key:
                continue
            
            # Retry logic para cada chave
            for retry in range(max_retries):
                try:
                    # Delay adicional para retries
                    if retry > 0:
                        delay = min(2 ** retry, 10)  # Exponential backoff, max 30s
                        logger.info(f"⏱️ Aguardando {delay}s antes do retry {retry + 1}")
                        await asyncio.sleep(delay)
                    
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/joscarmao/v1800finalv2",
                        "X-Title": "ARQV18 Enhanced v18.0"
                    }
                    
                    payload = {
                        "model": model_name,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "stream": False
                    }
                    
                    logger.info(f"📤 OpenRouter ({model_name}) - Chave {attempt + 1}/{len(self.openrouter_keys)}, Retry {retry + 1}/{max_retries}")
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=180, connect=30)
                        ) as response:
                            
                            if response.status == 200:
                                result = await response.json()
                                if result.get("choices") and len(result["choices"]) > 0:
                                    content = result["choices"][0]["message"]["content"]
                                    logger.info(f"✅ OpenRouter {model_name} sucesso (chave #{self.current_key_index}, retry {retry + 1})")
                                    # PRIORIDADE 3: Registrar sucesso
                                    self._record_api_result('openrouter', model_name, True)
                                    return content
                                else:
                                    logger.warning(f"⚠️ OpenRouter resposta vazia")
                                    # PRIORIDADE 3: Registrar erro
                                    self._record_api_result('openrouter', model_name, False, "Resposta vazia")
                                    continue
                            elif response.status == 429:
                                # Rate limit - aguardar com backoff exponencial
                                wait_time = min(10 * (2 ** retry), 60)  # Máximo 60s
                                logger.warning(f"⚠️ Rate limit OpenRouter - aguardando {wait_time}s (backoff)")
                                # PRIORIDADE 3: Registrar erro de rate limit
                                self._record_api_result('openrouter', model_name, False, f"Rate limit {response.status}")
                                await asyncio.sleep(wait_time)
                                continue
                            elif response.status in [500, 502, 503, 504]:
                                # Erro do servidor - retry com backoff
                                error_text = await response.text()
                                wait_time = min(5 * (2 ** retry), 30)  # Backoff para erros de servidor
                                logger.warning(f"⚠️ Erro servidor OpenRouter {response.status}: {error_text[:100]} - aguardando {wait_time}s")
                                # PRIORIDADE 3: Registrar erro de servidor
                                self._record_api_result('openrouter', model_name, False, f"Erro servidor {response.status}")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                error_text = await response.text()
                                logger.warning(f"⚠️ OpenRouter key {attempt + 1} falhou: {response.status} - {error_text[:200]}")
                                # PRIORIDADE 3: Registrar erro geral
                                self._record_api_result('openrouter', model_name, False, f"HTTP {response.status}: {error_text[:100]}")
                                break  # Não retry para outros erros
                                
                except asyncio.TimeoutError:
                    logger.warning(f"⏱️ Timeout OpenRouter key {attempt + 1}, retry {retry + 1}")
                    # PRIORIDADE 3: Registrar timeout
                    self._record_api_result('openrouter', model_name, False, "Timeout")
                    continue
                except Exception as e:
                    logger.warning(f"⚠️ Erro OpenRouter key {attempt + 1}, retry {retry + 1}: {str(e)[:100]}")
                    # PRIORIDADE 3: Registrar exceção
                    self._record_api_result('openrouter', model_name, False, f"Exception: {str(e)[:100]}")
                    continue
            
            # Se chegou aqui, todos os retries falharam para esta chave
        
        logger.error(f"❌ Todas as {len(self.openrouter_keys)} chaves OpenRouter falharam para {model_name}")
        return None
    
    async def _generate_with_gemini_direct(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Gera conteúdo usando Gemini direto com rotação de chaves e delay"""
        
        try:
            import google.generativeai as genai
            
            # PRIORIDADE 3: Verificar se deve pular esta API
            if self._should_skip_api('gemini', 'gemini-2.0-flash-exp'):
                logger.warning(f"⚠️ Pulando Gemini devido a muitos erros")
                return None
            
            # Tentar com todas as chaves Gemini
            for attempt in range(len(self.gemini_keys)):
                # Aplicar delay antes de cada requisição
                await self._apply_rate_limit_delay()
                
                api_key = self._get_next_gemini_key()
                if not api_key:
                    continue
                    
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-2.0-flash-exp")
                    
                    # Combinar system prompt e user prompt se necessário
                    full_prompt = prompt
                    if system_prompt:
                        full_prompt = f"{system_prompt}\n\n{prompt}"
                    
                    generation_config = {
                        'temperature': temperature,
                        'top_p': 0.95,
                        'top_k': 64,
                        'max_output_tokens': max_tokens,
                    }
                    
                    logger.info(f"📤 Enviando requisição para Gemini Direct - Tentativa {attempt + 1}/{len(self.gemini_keys)}")
                    
                    response = model.generate_content(
                        full_prompt,
                        generation_config=generation_config
                    )
                    
                    if response.text:
                        logger.info(f"✅ Gemini direto sucesso (chave #{self.current_gemini_key_index})")
                        # PRIORIDADE 3: Registrar sucesso
                        self._record_api_result('gemini', 'gemini-2.0-flash-exp', True)
                        return response.text
                    else:
                        # PRIORIDADE 3: Registrar resposta vazia
                        self._record_api_result('gemini', 'gemini-2.0-flash-exp', False, "Resposta vazia")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro Gemini key {attempt + 1}: {str(e)[:100]}")
                    # PRIORIDADE 3: Registrar erro
                    self._record_api_result('gemini', 'gemini-2.0-flash-exp', False, f"Exception: {str(e)[:100]}")
                    continue
            
            logger.error(f"❌ Todas as {len(self.gemini_keys)} chaves Gemini falharam")
            return None
            
        except ImportError:
            logger.error("❌ google-generativeai não instalado")
            return None
    
    def generate_response(
        self,
        prompt: str,
        model: str = "google/gemini-2.0-flash-exp:free",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Gera resposta síncrona usando hierarquia de modelos"""
        try:
            # Executar geração assíncrona de forma síncrona
            import asyncio
            
            async def _async_generate():
                return await self.generate_text(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    model_override=model
                )
            
            # Tentar obter loop existente ou criar novo
            try:
                loop = asyncio.get_running_loop()
                # Se já há um loop rodando, criar task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _async_generate())
                    content = future.result(timeout=360)
            except RuntimeError:
                # Nenhum loop rodando, executar diretamente
                content = asyncio.run(_async_generate())
            
            return {
                'success': True,
                'content': content,
                'model': model,
                'provider': 'hierarchy',
                'tokens_used': len(content.split()) * 1.3  # Estimativa
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de resposta: {e}")
            return {
                'success': False,
                'content': 'Erro interno ao gerar resposta',
                'error': str(e)
            }

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        model_override: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        PRIORIDADE 2: Gera texto usando hierarquia de modelos com fallback CUDA personalizado
        Gemini-2.0 Flash → Gemini Direct → Modelo Local CUDA com contexto
        
        Args:
            prompt: Prompt do usuário
            system_prompt: Prompt do sistema (opcional)
            max_tokens: Máximo de tokens (opcional)
            temperature: Temperatura (opcional)
            model_override: Modelo específico (opcional)
            context_data: Dados das etapas anteriores para personalização (opcional)
        
        Returns:
            String com a resposta da IA personalizada
        """
        max_tokens = max_tokens or 4000
        temperature = temperature or 0.7
        
        # PRIORIDADE 3: Log de status de saúde das APIs periodicamente
        current_time = time.time()
        if not hasattr(self, '_last_health_check') or (current_time - self._last_health_check) > self.api_health_check_interval:
            health_status = self._get_api_health_status()
            if health_status:
                logger.info("📊 Status de saúde das APIs:")
                for api_key, status in health_status.items():
                    status_emoji = "✅" if status['status'] == 'healthy' else "⚠️" if status['status'] == 'degraded' else "❌"
                    logger.info(f"  {status_emoji} {api_key}: {status['success_rate']:.1%} sucesso ({status['success_count']}/{status['success_count'] + status['error_count']})")
            self._last_health_check = current_time
        
        # Se modelo específico foi solicitado, tentar apenas ele
        if model_override:
            target_models = [m for m in self.model_hierarchy if m['name'] == model_override]
            if not target_models:
                # Se modelo não encontrado, usar hierarquia normal
                target_models = self.model_hierarchy
        else:
            target_models = self.model_hierarchy
        
        # Tentar cada modelo na hierarquia
        for model_config in target_models:
            try:
                logger.info(f"🤖 Tentando {model_config['name']} ({model_config['provider']})")
                
                if model_config['provider'] == 'openrouter':
                    result = await self._generate_with_openrouter(
                        prompt=prompt,
                        model_name=model_config['name'],
                        max_tokens=min(max_tokens, model_config['max_tokens']),
                        temperature=temperature,
                        system_prompt=system_prompt
                    )
                    
                elif model_config['provider'] == 'gemini_direct':
                    result = await self._generate_with_gemini_direct(
                        prompt=prompt,
                        max_tokens=min(max_tokens, model_config['max_tokens']),
                        temperature=temperature,
                        system_prompt=system_prompt
                    )
                    
                elif model_config['provider'] in ['groq', 'fireworks', 'openai']:
                    # Usar enhanced_api_rotation_manager para outros providers
                    result = await self._generate_with_enhanced_api(
                        prompt=prompt,
                        model_name=model_config['name'],
                        provider=model_config['provider'],
                        max_tokens=min(max_tokens, model_config['max_tokens']),
                        temperature=temperature,
                        system_prompt=system_prompt
                    )
                
                elif model_config['provider'] == 'local':
                    # Usar modelo local como fallback com contexto personalizado
                    result = await self._generate_with_local_model(
                        prompt=prompt,
                        max_tokens=min(max_tokens, model_config['max_tokens']),
                        temperature=temperature,
                        system_prompt=system_prompt,
                        context_data=context_data  # NOVO: Passar contexto para personalização
                    )
                else:
                    logger.warning(f"⚠️ Provider desconhecido: {model_config['provider']}")
                    continue
                
                if result:
                    logger.info(f"✅ Sucesso com {model_config['name']}")
                    return result
                else:
                    logger.warning(f"⚠️ {model_config['name']} não retornou resultado")
                    
            except Exception as e:
                logger.error(f"❌ Erro com {model_config['name']}: {str(e)[:100]}")
                continue
        
        # Se todos os modelos falharam, usar fallback básico
        logger.error("❌ Todos os modelos da hierarquia falharam")
        raise Exception("Todos os modelos de IA falharam. Verifique as configurações das APIs.")
    
    async def _generate_with_enhanced_api(
        self,
        prompt: str,
        model_name: str,
        provider: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Gera texto usando enhanced_api_rotation_manager"""
        try:
            # Importar api_rotation_manager
            from services.enhanced_api_rotation_manager import api_rotation_manager
            
            # Preparar prompt completo
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Usar api_rotation_manager para gerar
            result = await api_rotation_manager.generate_text(
                prompt=full_prompt,
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if result and result.strip():
                logger.info(f"✅ {provider.upper()} ({model_name}) retornou resultado")
                return result.strip()
            else:
                logger.warning(f"⚠️ {provider.upper()} ({model_name}) não retornou resultado")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro {provider.upper()} ({model_name}): {str(e)[:100]}")
            return None
    
    def generate_text_sync(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        model_override: Optional[str] = None
    ) -> str:
        """Versão síncrona da geração de texto"""
        try:
            import asyncio
            
            async def _async_wrapper():
                return await self.generate_text(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    model_override=model_override
                )
            
            try:
                loop = asyncio.get_running_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, _async_wrapper())
                    return future.result(timeout=360)
            except RuntimeError:
                return asyncio.run(_async_wrapper())
                
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"❌ Erro de conexão ao gerar texto (sync): {str(e)}")
            raise
        except (ValueError, KeyError) as e:
            logger.error(f"❌ Erro de parâmetros ao gerar texto (sync): {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao gerar texto (sync): {str(e)}")
            raise

    async def _perform_smart_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Realiza busca inteligente com fallbacks Serper → Jina → EXA"""
        
        if not self.search_orchestrator:
            logger.warning("⚠️ Search Orchestrator não disponível")
            return []
        
        try:
            # 1. Tentar Serper primeiro
            logger.info(f"🔍 Tentando busca Serper para: {query}")
            serper_results = await self.search_orchestrator.search_serper(query, max_results)
            
            if serper_results:
                logger.info(f"✅ Serper retornou {len(serper_results)} resultados")
                return serper_results
            
            # 2. Fallback para Jina
            logger.info(f"🔍 Fallback: Tentando busca Jina para: {query}")
            jina_results = await self.search_orchestrator.search_jina(query, max_results)
            
            if jina_results:
                logger.info(f"✅ Jina retornou {len(jina_results)} resultados")
                return jina_results
            
            # 3. Fallback para EXA
            logger.info(f"🔍 Fallback: Tentando busca EXA para: {query}")
            exa_results = await self.search_orchestrator.search_exa(query, max_results)
            
            if exa_results:
                logger.info(f"✅ EXA retornou {len(exa_results)} resultados")
                return exa_results
            
            logger.warning("⚠️ Todos os serviços de busca falharam")
            return []
            
        except Exception as e:
            logger.error(f"❌ Erro na busca inteligente: {e}")
            return []

    async def generate_with_active_search(
        self,
        prompt: str,
        context: str = "",
        session_id: str = None,
        max_search_iterations: int = 3,
        preferred_model: str = None,
        min_processing_time: int = 0
    ) -> str:
        """
        Gera conteúdo com busca ativa usando hierarquia Gemini-2.0 Flash → Gemini Direct
        Com delay de 10s entre requisições
        """
        logger.info(f"🔍 Iniciando geração com busca ativa (modelo: {preferred_model or 'hierarquia'})")
        
        # Registrar tempo de início para garantir tempo mínimo
        start_time = datetime.now()

        # Realizar buscas complementares se necessário
        additional_context = ""
        if max_search_iterations > 0:
            # Extrair termos de busca do prompt
            search_queries = self._extract_search_terms(prompt)
            
            for i, query in enumerate(search_queries[:max_search_iterations]):
                logger.info(f"🔍 Busca {i+1}/{len(search_queries)}: {query}")
                search_results = await self._perform_smart_search(query, max_results=3)
                
                if search_results:
                    additional_context += f"\n\n=== DADOS DE BUSCA: {query} ===\n"
                    for result in search_results:
                        additional_context += f"- {result.get('title', 'Sem título')}: {result.get('snippet', result.get('description', ''))}\n"

        # Prepara prompt com instruções de busca e contexto
        enhanced_prompt = f"""
{prompt}

CONTEXTO PRINCIPAL:
{context}

{additional_context if additional_context else ""}

INSTRUÇÕES ESPECIAIS:
- Analise o contexto fornecido detalhadamente
- Use os dados de busca complementares para enriquecer a análise
- Procure por estatísticas, tendências e casos reais
- Forneça insights profundos baseados nos dados disponíveis
- Combine informações de múltiplas fontes para criar análise robusta

IMPORTANTE: Gere uma análise completa e profissional baseando-se em TODOS os dados fornecidos.
"""

        # Sistema prompt para busca ativa
        system_prompt = """Você é um especialista em análise de mercado e tendências digitais com acesso a dados em tempo real.
        Sua função é gerar análises profundas e insights valiosos baseados nos dados fornecidos.
        Sempre forneça informações precisas, atualizadas e acionáveis.
        Combine dados de múltiplas fontes para criar análises robustas e confiáveis."""

        try:
            # Usar modelo preferido ou hierarquia
            logger.info(f"🤖 Gerando com modelo: {preferred_model or 'hierarquia Gemini-2.0 Flash → Gemini Direct'}")
            
            # Gerar resposta usando hierarquia
            response = await self.generate_text(
                prompt=enhanced_prompt,
                system_prompt=system_prompt,
                max_tokens=4000,
                temperature=0.7,
                model_override=preferred_model
            )
            
            # Garantir tempo mínimo de processamento se especificado
            if min_processing_time > 0:
                elapsed_time = (datetime.now() - start_time).total_seconds()
                if elapsed_time < min_processing_time:
                    remaining_time = min_processing_time - elapsed_time
                    logger.info(f"⏱️ Aguardando {remaining_time:.1f}s para completar tempo mínimo")
                    await asyncio.sleep(remaining_time)
            
            logger.info("✅ Geração com busca ativa concluída")
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro na geração com busca ativa: {e}")
            # Fallback simples
            try:
                return await self.generate_text(enhanced_prompt, system_prompt)
            except Exception as e2:
                logger.error(f"❌ Erro no fallback: {e2}")
                raise
    
    def _extract_search_terms(self, prompt: str) -> List[str]:
        """Extrai termos de busca relevantes do prompt"""
        # Implementação básica - pode ser melhorada
        search_terms = []
        
        # Buscar por palavras-chave comuns
        keywords = ['mercado', 'brasil', 'tendências', 'estatísticas', 'dados', 'análise']
        
        for keyword in keywords:
            if keyword in prompt.lower():
                # Extrair contexto ao redor da palavra-chave
                words = prompt.lower().split()
                for i, word in enumerate(words):
                    if keyword in word:
                        # Pegar 2 palavras antes e depois
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        search_term = ' '.join(words[start:end])
                        search_terms.append(search_term)
                        break
        
        # Se não encontrou termos específicos, usar primeiras palavras
        if not search_terms:
            words = prompt.split()[:5]
            search_terms.append(' '.join(words))
        
        return search_terms[:3]  # Máximo 3 buscas

    async def generate_content(
        self,
        prompt: str,
        service_type: str = 'ai_generation',
        model: str = None,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: str = None,
        **kwargs
    ) -> str:
        """
        Método de compatibilidade para generate_content usado pelo enhanced_module_processor
        
        Args:
            prompt: Prompt do usuário
            service_type: Tipo de serviço (compatibilidade)
            model: Modelo específico
            max_tokens: Máximo de tokens
            temperature: Temperatura
            system_prompt: Prompt do sistema
            **kwargs: Argumentos adicionais
        
        Returns:
            String com a resposta da IA
        """
        try:
            logger.info(f"🔄 generate_content chamado - service_type: {service_type}, model: {model}")
            
            # Mapear service_type para modelo se necessário
            model_mapping = {
                'ai_generation': 'gpt-4o-mini',
                'qwen': 'qwen/qwen-2.5-72b-instruct',
                'gemini': 'google/gemini-2.0-flash-exp:free',
                'openrouter': 'google/gemini-2.0-flash-exp:free'
            }
            
            # Usar modelo específico ou mapear do service_type
            target_model = model or model_mapping.get(service_type, 'google/gemini-2.0-flash-exp:free')
            
            # Aplicar delay entre requisições para evitar rate limiting
            await self._apply_rate_limit_delay()
            
            # Gerar conteúdo usando hierarquia
            result = await self.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                model_override=target_model
            )
            
            if not result:
                raise Exception(f"Modelo {target_model} não retornou resultado")
            
            logger.info(f"✅ generate_content sucesso com {target_model}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro em generate_content: {e}")
            
            # Fallback para modelo local se disponível
            try:
                logger.info("🔄 Tentando fallback para modelo local...")
                from services.local_model_manager import local_model_manager
                
                if local_model_manager.is_model_loaded():
                    fallback_result = local_model_manager.generate_text(
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    
                    if fallback_result:
                        logger.info("✅ Fallback modelo local sucesso")
                        return fallback_result
                        
            except Exception as fallback_error:
                logger.error(f"❌ Fallback modelo local falhou: {fallback_error}")
            
            # Se tudo falhou, re-raise a exceção original
            raise Exception(f"generate_content falhou: {str(e)}")

    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "comprehensive",
        target_audience: str = "general",
        model_preference: str = None
    ) -> str:
        """
        Analisa conteúdo usando hierarquia OpenRouter com delay
        
        Args:
            content: Conteúdo para análise
            analysis_type: Tipo de análise (comprehensive, viral, market, etc.)
            target_audience: Público-alvo
            model_preference: Preferência de modelo
        
        Returns:
            Análise detalhada do conteúdo
        """
        system_prompt = f"""Você é um especialista em análise de conteúdo digital e marketing.
        Sua função é analisar conteúdo de forma {analysis_type} para o público {target_audience}.
        Forneça insights acionáveis, tendências identificadas e recomendações estratégicas."""
        
        analysis_prompt = f"""
Analise o seguinte conteúdo de forma {analysis_type}:

CONTEÚDO:
{content}

PÚBLICO-ALVO: {target_audience}

FORNEÇA:
1. Análise detalhada do conteúdo
2. Pontos fortes e fracos identificados
3. Potencial viral e engajamento
4. Recomendações de melhoria
5. Estratégias de distribuição
6. Insights de mercado relevantes

Seja específico, prático e acionável em suas recomendações.
"""
        
        try:
            return await self.generate_text(
                prompt=analysis_prompt,
                system_prompt=system_prompt,
                max_tokens=3000,
                temperature=0.7,
                model_override=model_preference
            )
        except Exception as e:
            logger.error(f"❌ Erro na análise de conteúdo: {e}")
            raise

    async def generate_insights(
        self,
        data: Dict[str, Any],
        insight_type: str = "market_trends",
        depth: str = "deep"
    ) -> str:
        """
        Gera insights baseados em dados usando hierarquia OpenRouter com delay
        
        Args:
            data: Dados para análise
            insight_type: Tipo de insight desejado
            depth: Profundidade da análise (shallow, medium, deep)
        
        Returns:
            Insights gerados
        """
        system_prompt = f"""Você é um analista de dados especializado em {insight_type}.
        Sua função é gerar insights {depth} baseados nos dados fornecidos.
        Sempre forneça análises precisas, tendências identificadas e recomendações acionáveis."""
        
        data_str = json.dumps(data, indent=2, ensure_ascii=False)
        
        insights_prompt = f"""
Analise os seguintes dados e gere insights {depth} sobre {insight_type}:

DADOS:
{data_str}

FORNEÇA:
1. Principais tendências identificadas
2. Padrões e correlações importantes
3. Oportunidades de mercado
4. Riscos e desafios
5. Recomendações estratégicas
6. Previsões baseadas nos dados

Seja específico, use números quando relevante e forneça insights acionáveis.
"""
        
        try:
            return await self.generate_text(
                prompt=insights_prompt,
                system_prompt=system_prompt,
                max_tokens=4000,
                temperature=0.6
            )
        except Exception as e:
            logger.error(f"❌ Erro na geração de insights: {e}")
            raise

    async def _generate_with_local_model(
        self,
        prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        system_prompt: str = None,
        context_data: Dict[str, Any] = None
    ) -> str:
        """
        PRIORIDADE 2: Gera texto personalizado usando modelo local CUDA
        com análise específica dos dados das etapas anteriores
        """
        try:
            logger.info("🚀 Tentando modelo local com geração personalizada")
            
            # Importar o gerenciador de API rotation que tem acesso ao modelo local
            try:
                from services.enhanced_api_rotation_manager import enhanced_api_rotation_manager
                
                # Construir prompt completo
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                
                # Usar o método de fallback local APRIMORADO com contexto
                result = await enhanced_api_rotation_manager.generate_with_local_fallback(
                    prompt=full_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    context_data=context_data  # NOVO: Passar contexto para personalização
                )
                
                if result:
                    logger.info("✅ Modelo local gerou resposta personalizada com sucesso")
                    return result
                else:
                    logger.warning("⚠️ Modelo local não retornou resultado")
                    return None
                    
            except ImportError:
                logger.error("❌ Enhanced API Rotation Manager não disponível")
                return None
            except AttributeError as e:
                logger.error(f"❌ Método generate_with_local_fallback não encontrado: {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro no modelo local: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Retorna status do gerenciador"""
        return {
            "openrouter_keys_count": len(self.openrouter_keys),
            "gemini_keys_count": len(self.gemini_keys),
            "current_openrouter_key_index": self.current_key_index,
            "current_gemini_key_index": self.current_gemini_key_index,
            "request_delay_seconds": self.request_delay,
            "last_request_time": self.last_request_time,
            "search_orchestrator_available": self.search_orchestrator is not None,
            "model_hierarchy": [m['name'] for m in self.model_hierarchy],
            "timestamp": datetime.now().isoformat()
        }

    def reset_failed_models(self):
        """Reseta índices de rotação de chaves"""
        self.current_key_index = 0
        self.current_gemini_key_index = 0
        self.last_request_time = 0
        logger.info("✅ Índices de rotação resetados")

# Instância global para uso em todo o projeto
enhanced_ai_manager = EnhancedAIManager()

# Funções de conveniência para uso direto
async def generate_ai_text(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    model_override: Optional[str] = None
) -> str:
    """Função de conveniência para geração de texto"""
    return await enhanced_ai_manager.generate_text(
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        model_override=model_override
    )

def generate_ai_text_sync(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    model_override: Optional[str] = None
) -> str:
    """Função de conveniência síncrona para geração de texto"""
    return enhanced_ai_manager.generate_text_sync(
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        model_override=model_override
    )

if __name__ == "__main__":
    # Teste básico
    async def test():
        try:
            manager = EnhancedAIManager()
            
            print("🧪 Testando geração de texto com delay e rotação de APIs...")
            print(f"⏱️ Delay configurado: {manager.request_delay}s entre requisições")
            print(f"🔑 Chaves OpenRouter disponíveis: {len(manager.openrouter_keys)}")
            print(f"🔑 Chaves Gemini disponíveis: {len(manager.gemini_keys)}")
            print()
            
            # Teste 1: Geração simples
            print("📝 Teste 1: Geração de texto simples")
            response1 = await manager.generate_text(
                prompt="Explique brevemente o que é inteligência artificial",
                system_prompt="Você é um especialista em tecnologia"
            )
            print(f"✅ Resposta 1 (primeiros 200 chars): {response1[:200]}...")
            print()
            
            # Teste 2: Segunda requisição (deve aguardar 10s)
            print("📝 Teste 2: Segunda requisição (testando delay)")
            response2 = await manager.generate_text(
                prompt="O que é machine learning?",
                system_prompt="Você é um especialista em IA"
            )
            print(f"✅ Resposta 2 (primeiros 200 chars): {response2[:200]}...")
            print()
            
            # Teste 3: Status do gerenciador
            print("📊 Status do gerenciador:")
            status = manager.get_status()
            print(json.dumps(status, indent=2, default=str, ensure_ascii=False))
            print()
            
            print("✅ Todos os testes concluídos com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(test())
