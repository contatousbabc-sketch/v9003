#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Advanced Credit Manager
Sistema robusto e inteligente de gerenciamento de créditos para todas as APIs
"""

import os
import json
import logging
import time
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

class APIStatus(Enum):
    """Status das APIs"""
    ACTIVE = "active"
    DISABLED = "disabled"
    RATE_LIMITED = "rate_limited"
    NO_CREDITS = "no_credits"
    ERROR = "error"
    UNKNOWN = "unknown"

@dataclass
class APIKey:
    """Informações de uma chave de API"""
    key: str
    provider: str
    status: APIStatus
    credits_remaining: Optional[int] = None
    credits_used: int = 0
    last_used: Optional[datetime] = None
    last_error: Optional[str] = None
    error_count: int = 0
    success_count: int = 0
    rate_limit_reset: Optional[datetime] = None
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None
    cost_per_request: float = 0.0
    priority: int = 1  # 1 = alta, 5 = baixa

@dataclass
class APIUsageStats:
    """Estatísticas de uso de API"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    last_24h_requests: int = 0
    success_rate: float = 0.0

class AdvancedCreditManager:
    """Gerenciador avançado de créditos com inteligência artificial"""
    
    def __init__(self):
        self.api_keys: Dict[str, List[APIKey]] = defaultdict(list)
        self.usage_stats: Dict[str, APIUsageStats] = defaultdict(APIUsageStats)
        self.config_file = Path("config/credit_manager_config.json")
        self.stats_file = Path("config/api_usage_stats.json")
        self.lock = threading.Lock()
        
        # Configurações padrão
        self.default_config = {
            "auto_disable_threshold": 5,  # Desabilitar após 5 erros consecutivos
            "rate_limit_cooldown": 300,   # 5 minutos de cooldown
            "credit_check_interval": 3600, # Verificar créditos a cada hora
            "fallback_enabled": True,
            "smart_rotation": True,
            "cost_optimization": True
        }
        
        self.load_configuration()
        self.load_api_keys()
        self.load_usage_stats()
        
        # Iniciar thread de monitoramento
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def load_configuration(self):
        """Carrega configuração do arquivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.default_config.copy()
                self.save_configuration()
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            self.config = self.default_config.copy()
    
    def save_configuration(self):
        """Salva configuração no arquivo"""
        try:
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
    
    def load_api_keys(self):
        """Carrega chaves de API do ambiente"""
        
        # Mapeamento de providers e suas chaves
        api_providers = {
            'openrouter': ['OPENROUTER_API_KEY', 'OPENROUTER_API_KEY_2', 'OPENROUTER_API_KEY_3', 
                          'OPENROUTER_API_KEY_4', 'OPENROUTER_API_KEY_5', 'OPENROUTER_API_KEY_6'],
            'serper': ['SERPER_API_KEY', 'SERPER_API_KEY_2', 'SERPER_API_KEY_3'],
            'tavily': ['TAVILY_API_KEY', 'TAVILY_API_KEY_2'],
            'exa': ['EXA_API_KEY', 'EXA_API_KEY_2'],
            'jina': ['JINA_API_KEY'],
            'firecrawl': ['FIRECRAWL_API_KEY'],
            'gemini': ['GEMINI_API_KEY', 'GEMINI_API_KEY_2'],
            'anthropic': ['ANTHROPIC_API_KEY'],
            'groq': ['GROQ_API_KEY']
        }
        
        for provider, env_vars in api_providers.items():
            for i, env_var in enumerate(env_vars, 1):
                key = os.getenv(env_var)
                if key:
                    api_key = APIKey(
                        key=key,
                        provider=provider,
                        status=APIStatus.ACTIVE,
                        priority=i  # Primeira chave tem prioridade mais alta
                    )
                    self.api_keys[provider].append(api_key)
        
        logger.info(f"✅ Carregadas {sum(len(keys) for keys in self.api_keys.values())} chaves de API")
    
    def load_usage_stats(self):
        """Carrega estatísticas de uso"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    for provider, stats_data in data.items():
                        self.usage_stats[provider] = APIUsageStats(**stats_data)
        except Exception as e:
            logger.error(f"Erro ao carregar estatísticas: {e}")
    
    def save_usage_stats(self):
        """Salva estatísticas de uso"""
        try:
            self.stats_file.parent.mkdir(exist_ok=True)
            data = {provider: asdict(stats) for provider, stats in self.usage_stats.items()}
            with open(self.stats_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Erro ao salvar estatísticas: {e}")
    
    def get_best_api_key(self, provider: str, operation_type: str = "default") -> Optional[APIKey]:
        """
        Seleciona a melhor chave de API baseada em inteligência artificial
        
        Args:
            provider: Nome do provider (openrouter, serper, etc)
            operation_type: Tipo de operação (search, generation, etc)
        
        Returns:
            Melhor chave disponível ou None
        """
        
        with self.lock:
            available_keys = [
                key for key in self.api_keys.get(provider, [])
                if key.status == APIStatus.ACTIVE
            ]
            
            if not available_keys:
                logger.warning(f"⚠️ Nenhuma chave ativa para {provider}")
                return None
            
            # Algoritmo de seleção inteligente
            if self.config.get('smart_rotation', True):
                return self._select_smart_key(available_keys, operation_type)
            else:
                return self._select_round_robin_key(available_keys)
    
    def _select_smart_key(self, keys: List[APIKey], operation_type: str) -> APIKey:
        """Seleção inteligente baseada em múltiplos fatores"""
        
        scored_keys = []
        
        for key in keys:
            score = 0
            
            # Fator 1: Taxa de sucesso (peso 40%)
            if key.success_count + key.error_count > 0:
                success_rate = key.success_count / (key.success_count + key.error_count)
                score += success_rate * 40
            else:
                score += 20  # Chave nova recebe pontuação média
            
            # Fator 2: Prioridade da chave (peso 20%)
            priority_score = (6 - key.priority) * 4  # Prioridade 1 = 20 pontos
            score += priority_score
            
            # Fator 3: Tempo desde último uso (peso 15%)
            if key.last_used:
                time_since_use = (datetime.now() - key.last_used).total_seconds()
                time_score = min(time_since_use / 3600, 1) * 15  # Max 15 pontos após 1h
                score += time_score
            else:
                score += 15  # Chave nunca usada recebe pontuação máxima
            
            # Fator 4: Créditos restantes (peso 15%)
            if key.credits_remaining:
                credit_score = min(key.credits_remaining / 1000, 1) * 15
                score += credit_score
            else:
                score += 7.5  # Pontuação média se créditos desconhecidos
            
            # Fator 5: Rate limiting (peso 10%)
            if key.rate_limit_reset and key.rate_limit_reset > datetime.now():
                score -= 10  # Penalizar chaves com rate limit ativo
            else:
                score += 10
            
            scored_keys.append((key, score))
        
        # Ordenar por pontuação e retornar a melhor
        scored_keys.sort(key=lambda x: x[1], reverse=True)
        best_key = scored_keys[0][0]
        
        logger.debug(f"🎯 Chave selecionada para {best_key.provider}: prioridade {best_key.priority}, score {scored_keys[0][1]:.1f}")
        return best_key
    
    def _select_round_robin_key(self, keys: List[APIKey]) -> APIKey:
        """Seleção round-robin simples"""
        # Ordenar por último uso e retornar a menos usada recentemente
        keys.sort(key=lambda k: k.last_used or datetime.min)
        return keys[0]
    
    def record_api_usage(self, provider: str, key: str, success: bool, 
                        response_time: float = 0, error_message: str = None,
                        cost: float = 0):
        """
        Registra uso de API e atualiza estatísticas
        
        Args:
            provider: Nome do provider
            key: Chave utilizada
            success: Se a requisição foi bem-sucedida
            response_time: Tempo de resposta em segundos
            error_message: Mensagem de erro se houver
            cost: Custo da requisição
        """
        
        with self.lock:
            # Encontrar a chave
            api_key = None
            for k in self.api_keys.get(provider, []):
                if k.key == key:
                    api_key = k
                    break
            
            if not api_key:
                logger.warning(f"⚠️ Chave não encontrada: {provider}")
                return
            
            # Atualizar estatísticas da chave
            api_key.last_used = datetime.now()
            
            if success:
                api_key.success_count += 1
            else:
                api_key.error_count += 1
                api_key.last_error = error_message
                
                # Auto-desabilitar se muitos erros
                if api_key.error_count >= self.config.get('auto_disable_threshold', 5):
                    api_key.status = APIStatus.DISABLED
                    logger.warning(f"🚫 Chave {provider} desabilitada por muitos erros")
            
            # Atualizar estatísticas globais
            stats = self.usage_stats[provider]
            stats.total_requests += 1
            
            if success:
                stats.successful_requests += 1
            else:
                stats.failed_requests += 1
            
            stats.total_cost += cost
            
            # Atualizar tempo médio de resposta
            if response_time > 0:
                total_time = stats.average_response_time * (stats.total_requests - 1)
                stats.average_response_time = (total_time + response_time) / stats.total_requests
            
            # Calcular taxa de sucesso
            if stats.total_requests > 0:
                stats.success_rate = stats.successful_requests / stats.total_requests
            
            # Salvar estatísticas periodicamente
            if stats.total_requests % 10 == 0:
                self.save_usage_stats()
    
    def handle_api_error(self, provider: str, key: str, error_code: int, 
                        error_message: str) -> Optional[APIKey]:
        """
        Trata erros de API e retorna chave alternativa se disponível
        
        Args:
            provider: Nome do provider
            key: Chave que falhou
            error_code: Código do erro HTTP
            error_message: Mensagem de erro
        
        Returns:
            Chave alternativa ou None
        """
        
        with self.lock:
            # Encontrar a chave que falhou
            failed_key = None
            for k in self.api_keys.get(provider, []):
                if k.key == key:
                    failed_key = k
                    break
            
            if not failed_key:
                return None
            
            # Tratar diferentes tipos de erro
            if error_code == 401 or error_code == 403:
                # Erro de autenticação - desabilitar chave
                failed_key.status = APIStatus.DISABLED
                failed_key.last_error = f"Auth error: {error_message}"
                logger.error(f"🚫 Chave {provider} desabilitada por erro de autenticação")
            
            elif error_code == 402 or "credits" in error_message.lower():
                # Sem créditos
                failed_key.status = APIStatus.NO_CREDITS
                failed_key.credits_remaining = 0
                failed_key.last_error = f"No credits: {error_message}"
                logger.warning(f"💳 Chave {provider} sem créditos")
            
            elif error_code == 429:
                # Rate limiting
                failed_key.status = APIStatus.RATE_LIMITED
                failed_key.rate_limit_reset = datetime.now() + timedelta(
                    seconds=self.config.get('rate_limit_cooldown', 300)
                )
                failed_key.last_error = f"Rate limited: {error_message}"
                logger.warning(f"⏱️ Chave {provider} com rate limit")
            
            else:
                # Outros erros
                failed_key.error_count += 1
                failed_key.last_error = f"Error {error_code}: {error_message}"
            
            # Registrar uso com falha
            self.record_api_usage(provider, key, False, error_message=error_message)
            
            # Tentar encontrar chave alternativa
            return self.get_best_api_key(provider)
    
    def check_api_health(self, provider: str, key: str) -> bool:
        """
        Verifica saúde de uma API específica
        
        Args:
            provider: Nome do provider
            key: Chave a verificar
        
        Returns:
            True se API está saudável
        """
        
        # URLs de teste para cada provider
        test_urls = {
            'openrouter': 'https://openrouter.ai/api/v1/models',
            'serper': 'https://google.serper.dev/search',
            'tavily': 'https://api.tavily.com/search',
            'exa': 'https://api.exa.ai/search',
            'jina': 'https://r.jina.ai/',
            'firecrawl': 'https://api.firecrawl.dev/v0/scrape',
            'gemini': 'https://generativelanguage.googleapis.com/v1/models'
        }
        
        test_url = test_urls.get(provider)
        if not test_url:
            return True  # Assumir saudável se não temos teste
        
        try:
            headers = {'Authorization': f'Bearer {key}'}
            response = requests.get(test_url, headers=headers, timeout=20)
            
            # Considerar saudável se não for erro de auth/credits
            return response.status_code not in [401, 402, 403]
            
        except Exception as e:
            logger.debug(f"Health check failed for {provider}: {e}")
            return False
    
    def get_provider_status(self, provider: str) -> Dict[str, Any]:
        """Retorna status detalhado de um provider"""
        
        keys = self.api_keys.get(provider, [])
        stats = self.usage_stats.get(provider, APIUsageStats())
        
        active_keys = len([k for k in keys if k.status == APIStatus.ACTIVE])
        total_keys = len(keys)
        
        return {
            'provider': provider,
            'total_keys': total_keys,
            'active_keys': active_keys,
            'disabled_keys': len([k for k in keys if k.status == APIStatus.DISABLED]),
            'rate_limited_keys': len([k for k in keys if k.status == APIStatus.RATE_LIMITED]),
            'no_credit_keys': len([k for k in keys if k.status == APIStatus.NO_CREDITS]),
            'success_rate': stats.success_rate,
            'total_requests': stats.total_requests,
            'total_cost': stats.total_cost,
            'average_response_time': stats.average_response_time,
            'health_status': 'healthy' if active_keys > 0 else 'critical'
        }
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Retorna visão geral do sistema de créditos"""
        
        overview = {
            'timestamp': datetime.now().isoformat(),
            'providers': {},
            'total_keys': 0,
            'active_keys': 0,
            'total_requests': 0,
            'total_cost': 0.0,
            'overall_success_rate': 0.0
        }
        
        total_requests = 0
        successful_requests = 0
        
        for provider in self.api_keys.keys():
            provider_status = self.get_provider_status(provider)
            overview['providers'][provider] = provider_status
            overview['total_keys'] += provider_status['total_keys']
            overview['active_keys'] += provider_status['active_keys']
            overview['total_requests'] += provider_status['total_requests']
            overview['total_cost'] += provider_status['total_cost']
            
            stats = self.usage_stats.get(provider, APIUsageStats())
            total_requests += stats.total_requests
            successful_requests += stats.successful_requests
        
        if total_requests > 0:
            overview['overall_success_rate'] = successful_requests / total_requests
        
        return overview
    
    def _monitoring_loop(self):
        """Loop de monitoramento em background"""
        
        while True:
            try:
                # Verificar chaves com rate limit
                current_time = datetime.now()
                
                with self.lock:
                    for provider_keys in self.api_keys.values():
                        for key in provider_keys:
                            if (key.status == APIStatus.RATE_LIMITED and 
                                key.rate_limit_reset and 
                                current_time >= key.rate_limit_reset):
                                
                                key.status = APIStatus.ACTIVE
                                key.rate_limit_reset = None
                                logger.info(f"✅ Chave {key.provider} reativada após rate limit")
                
                # Salvar estatísticas
                self.save_usage_stats()
                
                # Aguardar próxima verificação
                time.sleep(60)  # Verificar a cada minuto
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(60)
    
    def optimize_costs(self) -> Dict[str, Any]:
        """Otimiza custos sugerindo melhor uso das APIs"""
        
        suggestions = {
            'timestamp': datetime.now().isoformat(),
            'total_cost': sum(stats.total_cost for stats in self.usage_stats.values()),
            'suggestions': []
        }
        
        for provider, stats in self.usage_stats.items():
            if stats.total_cost > 0:
                cost_per_request = stats.total_cost / stats.total_requests
                
                if cost_per_request > 0.01:  # Mais de 1 centavo por request
                    suggestions['suggestions'].append({
                        'provider': provider,
                        'issue': 'high_cost_per_request',
                        'cost_per_request': cost_per_request,
                        'recommendation': f'Considere usar {provider} apenas para operações críticas'
                    })
                
                if stats.success_rate < 0.8:  # Taxa de sucesso baixa
                    suggestions['suggestions'].append({
                        'provider': provider,
                        'issue': 'low_success_rate',
                        'success_rate': stats.success_rate,
                        'recommendation': f'Revisar configuração ou substituir chaves de {provider}'
                    })
        
        return suggestions

# Instância global
advanced_credit_manager = AdvancedCreditManager()

if __name__ == "__main__":
    # Teste do sistema
    manager = AdvancedCreditManager()
    overview = manager.get_system_overview()
    
    print("🔍 SISTEMA DE GERENCIAMENTO DE CRÉDITOS")
    print(f"Total de chaves: {overview['total_keys']}")
    print(f"Chaves ativas: {overview['active_keys']}")
    print(f"Taxa de sucesso geral: {overview['overall_success_rate']:.1%}")
    
    for provider, status in overview['providers'].items():
        print(f"\n📊 {provider.upper()}:")
        print(f"  Chaves: {status['active_keys']}/{status['total_keys']}")
        print(f"  Requests: {status['total_requests']}")
        print(f"  Sucesso: {status['success_rate']:.1%}")
        print(f"  Status: {status['health_status']}")