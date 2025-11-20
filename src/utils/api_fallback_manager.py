#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - API Fallback Manager
Sistema inteligente de fallback para APIs com créditos esgotados
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from .api_credit_manager import APICreditManager

logger = logging.getLogger(__name__)

@dataclass
class FallbackStrategy:
    """Estratégia de fallback para um serviço"""
    service_name: str
    primary_apis: List[str]
    fallback_apis: List[str]
    cache_enabled: bool = True
    reduced_functionality: bool = False
    alternative_services: List[str] = None

class APIFallbackManager:
    """Gerenciador inteligente de fallback para APIs"""
    
    def __init__(self):
        self.credit_manager = APICreditManager()
        
        # Estratégias de fallback por serviço
        self.fallback_strategies = {
            'search': FallbackStrategy(
                service_name='search',
                primary_apis=['serper', 'exa'],
                fallback_apis=['jina', 'tavily'],
                alternative_services=['google_cse', 'fess']
            ),
            'content_extraction': FallbackStrategy(
                service_name='content_extraction',
                primary_apis=['firecrawl', 'jina'],
                fallback_apis=['apify'],
                reduced_functionality=True
            ),
            'ai_generation': FallbackStrategy(
                service_name='ai_generation',
                primary_apis=['openrouter', 'gemini'],
                fallback_apis=['openai', 'deepseek'],
                alternative_services=['groq']
            ),
            'social_media': FallbackStrategy(
                service_name='social_media',
                primary_apis=['apify', 'supadata'],
                fallback_apis=['phantombuster'],
                reduced_functionality=True
            )
        }
        
    def get_best_available_api(self, service_type: str, exclude_apis: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Retorna a melhor API disponível para um tipo de serviço
        
        Args:
            service_type: Tipo de serviço ('search', 'content_extraction', etc.)
            exclude_apis: Lista de APIs para excluir
            
        Returns:
            Dict com informações da API ou None se nenhuma disponível
        """
        exclude_apis = exclude_apis or []
        
        if service_type not in self.fallback_strategies:
            logger.warning(f"⚠️ Tipo de serviço desconhecido: {service_type}")
            return None
            
        strategy = self.fallback_strategies[service_type]
        
        # 1. Tenta APIs primárias primeiro
        for api_name in strategy.primary_apis:
            if api_name in exclude_apis:
                continue
                
            available_keys = self.credit_manager.get_available_apis_for_service(api_name)
            if available_keys:
                best_key = self._select_best_api_key(available_keys)
                return {
                    'api_name': api_name,
                    'api_key': best_key,
                    'tier': 'primary',
                    'reduced_functionality': False
                }
        
        # 2. Tenta APIs de fallback
        for api_name in strategy.fallback_apis:
            if api_name in exclude_apis:
                continue
                
            available_keys = self.credit_manager.get_available_apis_for_service(api_name)
            if available_keys:
                best_key = self._select_best_api_key(available_keys)
                return {
                    'api_name': api_name,
                    'api_key': best_key,
                    'tier': 'fallback',
                    'reduced_functionality': strategy.reduced_functionality
                }
        
        # 3. Tenta serviços alternativos
        if strategy.alternative_services:
            for alt_service in strategy.alternative_services:
                available_keys = self.credit_manager.get_available_apis_for_service(alt_service)
                if available_keys:
                    best_key = self._select_best_api_key(available_keys)
                    return {
                        'api_name': alt_service,
                        'api_key': best_key,
                        'tier': 'alternative',
                        'reduced_functionality': True
                    }
        
        logger.error(f"❌ Nenhuma API disponível para {service_type}")
        return None
    
    def _select_best_api_key(self, available_keys: List[str]) -> str:
        """Seleciona a melhor chave de API baseada em métricas"""
        if not available_keys:
            return None
            
        if len(available_keys) == 1:
            return available_keys[0]
        
        # Seleciona baseado em taxa de sucesso e uso recente
        best_key = available_keys[0]
        best_score = 0
        
        for key in available_keys:
            status = self.credit_manager.api_statuses.get(key)
            if not status:
                continue
                
            # Calcula score baseado em taxa de sucesso e uso
            total_requests = status.success_count + status.error_count
            if total_requests > 0:
                success_rate = status.success_count / total_requests
            else:
                success_rate = 1.0  # Nova API, assume sucesso
                
            # Penaliza APIs muito usadas recentemente
            time_penalty = 0
            if status.last_request_time:
                minutes_since_last = (datetime.now() - status.last_request_time).total_seconds() / 60
                time_penalty = max(0, 1 - (minutes_since_last / 60))  # Penalidade decresce em 1 hora
            
            score = success_rate * (1 - time_penalty * 0.3)
            
            if score > best_score:
                best_score = score
                best_key = key
        
        return best_key
    
    def handle_api_failure(self, failed_api: str, service_type: str, error_details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Lida com falha de API e retorna alternativa
        
        Args:
            failed_api: Nome da API que falhou
            service_type: Tipo de serviço
            error_details: Detalhes do erro
            
        Returns:
            Dict com API alternativa ou None
        """
        logger.warning(f"🔄 Buscando alternativa para {failed_api} ({service_type})")
        
        # Registra a falha no credit manager
        if error_details.get('status_code') in [402, 429]:
            self.credit_manager.handle_api_error(
                failed_api.split('_')[0],  # Nome da API
                failed_api.split('_')[-1] if '_' in failed_api else '1',  # Key ID
                error_details.get('error_response', ''),
                error_details.get('status_code')
            )
        
        # Busca alternativa excluindo a API que falhou
        alternative = self.get_best_available_api(service_type, exclude_apis=[failed_api.split('_')[0]])
        
        if alternative:
            logger.info(f"✅ Alternativa encontrada: {alternative['api_name']} (tier: {alternative['tier']})")
            if alternative['reduced_functionality']:
                logger.warning("⚠️ Funcionalidade reduzida na API alternativa")
        else:
            logger.error(f"❌ Nenhuma alternativa disponível para {service_type}")
            
        return alternative
    
    def get_service_health_report(self) -> Dict[str, Any]:
        """Gera relatório de saúde dos serviços"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'critical_services': [],
            'warnings': []
        }
        
        for service_name, strategy in self.fallback_strategies.items():
            service_health = {
                'primary_apis_available': 0,
                'fallback_apis_available': 0,
                'alternative_apis_available': 0,
                'total_available': 0,
                'status': 'unknown'
            }
            
            # Conta APIs primárias disponíveis
            for api_name in strategy.primary_apis:
                available = len(self.credit_manager.get_available_apis_for_service(api_name))
                service_health['primary_apis_available'] += available
                service_health['total_available'] += available
            
            # Conta APIs de fallback disponíveis
            for api_name in strategy.fallback_apis:
                available = len(self.credit_manager.get_available_apis_for_service(api_name))
                service_health['fallback_apis_available'] += available
                service_health['total_available'] += available
            
            # Conta APIs alternativas disponíveis
            if strategy.alternative_services:
                for api_name in strategy.alternative_services:
                    available = len(self.credit_manager.get_available_apis_for_service(api_name))
                    service_health['alternative_apis_available'] += available
                    service_health['total_available'] += available
            
            # Determina status do serviço
            if service_health['primary_apis_available'] > 0:
                service_health['status'] = 'healthy'
            elif service_health['fallback_apis_available'] > 0:
                service_health['status'] = 'degraded'
                report['warnings'].append(f"Serviço {service_name} usando APIs de fallback")
            elif service_health['alternative_apis_available'] > 0:
                service_health['status'] = 'limited'
                report['warnings'].append(f"Serviço {service_name} com funcionalidade limitada")
            else:
                service_health['status'] = 'critical'
                report['critical_services'].append(service_name)
            
            report['services'][service_name] = service_health
        
        return report
    
    def optimize_api_usage(self) -> Dict[str, Any]:
        """Otimiza o uso de APIs baseado no status atual"""
        optimization_actions = []
        
        # Desabilita APIs com muitos erros de crédito
        disabled_result = self.credit_manager.disable_problematic_apis()
        if disabled_result['disabled_count'] > 0:
            optimization_actions.append(f"Desabilitadas {disabled_result['disabled_count']} APIs problemáticas")
        
        # Gera recomendações baseadas no relatório de saúde
        health_report = self.get_service_health_report()
        
        for service_name, health in health_report['services'].items():
            if health['status'] == 'critical':
                optimization_actions.append(f"CRÍTICO: Serviço {service_name} sem APIs disponíveis")
            elif health['status'] == 'limited':
                optimization_actions.append(f"ATENÇÃO: Serviço {service_name} com funcionalidade limitada")
        
        return {
            'actions_taken': optimization_actions,
            'health_report': health_report,
            'timestamp': datetime.now().isoformat()
        }

# Instância global
api_fallback_manager = APIFallbackManager()