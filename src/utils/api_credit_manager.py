# -*- coding: utf-8 -*-
"""
ARQ-ALPHA-V12 - API Credit Manager
Sistema inteligente de monitoramento e gestão de créditos de API
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# Importar sistema de logging otimizado
try:
    from enhanced_logging_system import get_logger, log_performance
except ImportError:
    import logging
    def get_logger(name, level=None):
        return logging.getLogger(name)
    def log_performance(operation, duration, details=None):
        pass

@dataclass
class APIStatus:
    """Status de uma API"""
    name: str
    key_id: str
    is_active: bool = True
    credits_remaining: Optional[int] = None
    daily_limit: Optional[int] = None
    requests_made: int = 0
    last_request_time: Optional[datetime] = None
    last_error: Optional[str] = None
    error_count: int = 0
    success_count: int = 0
    rate_limit_reset: Optional[datetime] = None
    cost_per_request: float = 0.0
    total_cost: float = 0.0

@dataclass
class APILimits:
    """Limites conhecidos das APIs"""
    name: str
    free_tier_daily: int
    free_tier_monthly: int
    paid_tier_daily: Optional[int] = None
    cost_per_1k_requests: float = 0.0
    rate_limit_per_minute: int = 60

class APICreditManager:
    """Gerenciador inteligente de créditos de API - V2.0 ULTRA-ROBUSTO"""
    
    def __init__(self, data_dir: str = "data"):
        self.logger = get_logger(__name__)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.status_file = self.data_dir / "api_status.json"
        self.alerts_file = self.data_dir / "api_alerts.json"
        self.api_statuses: Dict[str, APIStatus] = {}
        
        # Limites conhecidos das APIs - ATUALIZADOS COM DADOS REAIS
        self.api_limits = {
            'serper': APILimits('serper', 100, 2500, cost_per_1k_requests=5.0, rate_limit_per_minute=30),
            'exa': APILimits('exa', 1000, 1000, cost_per_1k_requests=1.0, rate_limit_per_minute=60),
            'firecrawl': APILimits('firecrawl', 500, 500, cost_per_1k_requests=3.0, rate_limit_per_minute=20),
            'apify': APILimits('apify', 1000, 10000, cost_per_1k_requests=2.0, rate_limit_per_minute=30),
            'jina': APILimits('jina', 1000, 1000, cost_per_1k_requests=0.2, rate_limit_per_minute=100),
            'openrouter': APILimits('openrouter', 200, 200, cost_per_1k_requests=0.0, rate_limit_per_minute=20),
            'supadata': APILimits('supadata', 100, 1000, cost_per_1k_requests=1.0, rate_limit_per_minute=60),
            'tavily': APILimits('tavily', 1000, 1000, cost_per_1k_requests=1.0, rate_limit_per_minute=60),
            'gemini': APILimits('gemini', 1500, 1500, cost_per_1k_requests=0.0, rate_limit_per_minute=15),
            'fireworks': APILimits('fireworks', 1000, 1000, cost_per_1k_requests=0.2, rate_limit_per_minute=60),
            'groq': APILimits('groq', 14400, 14400, cost_per_1k_requests=0.0, rate_limit_per_minute=30),
        }
        
        # Sistema de alertas preventivos
        self.alert_thresholds = {
            'credits_low': 0.1,  # 10% dos créditos restantes
            'rate_limit_approaching': 0.8,  # 80% do rate limit
            'error_rate_high': 0.3,  # 30% de taxa de erro
            'consecutive_failures': 3  # 3 falhas consecutivas
        }
        
        self.load_status()
        
    def load_status(self):
        """Carrega status das APIs do arquivo"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for key, status_data in data.items():
                    # Converter strings de data de volta para datetime
                    if status_data.get('last_request_time'):
                        status_data['last_request_time'] = datetime.fromisoformat(status_data['last_request_time'])
                    if status_data.get('rate_limit_reset'):
                        status_data['rate_limit_reset'] = datetime.fromisoformat(status_data['rate_limit_reset'])
                    
                    self.api_statuses[key] = APIStatus(**status_data)
                    
                self.logger.info(f"✅ Status de {len(self.api_statuses)} APIs carregado")
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar status das APIs: {e}")
            
    def save_status(self):
        """Salva status das APIs no arquivo"""
        try:
            data = {}
            for key, status in self.api_statuses.items():
                status_dict = asdict(status)
                # Converter datetime para string
                if status_dict.get('last_request_time'):
                    status_dict['last_request_time'] = status_dict['last_request_time'].isoformat()
                if status_dict.get('rate_limit_reset'):
                    status_dict['rate_limit_reset'] = status_dict['rate_limit_reset'].isoformat()
                data[key] = status_dict
                
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar status das APIs: {e}")
            
    def register_api(self, api_name: str, key_id: str, daily_limit: Optional[int] = None):
        """Registra uma nova API"""
        api_key = f"{api_name}_{key_id}"
        
        if api_key not in self.api_statuses:
            # Usar limites conhecidos se disponível
            limits = self.api_limits.get(api_name)
            default_limit = limits.free_tier_daily if limits else 1000
            
            self.api_statuses[api_key] = APIStatus(
                name=api_name,
                key_id=key_id,
                daily_limit=daily_limit or default_limit
            )
            self.logger.info(f"📝 API registrada: {api_key} (limite: {daily_limit or default_limit})")
            
    def record_request(self, api_name: str, key_id: str, success: bool = True, 
                      cost: float = 0.0, error_message: str = None):
        """Registra uma requisição feita à API"""
        api_key = f"{api_name}_{key_id}"
        
        if api_key not in self.api_statuses:
            self.register_api(api_name, key_id)
            
        status = self.api_statuses[api_key]
        status.requests_made += 1
        status.last_request_time = datetime.now()
        status.total_cost += cost
        
        if success:
            status.success_count += 1
            status.error_count = max(0, status.error_count - 1)  # Reduz contador de erro
        else:
            status.error_count += 1
            status.last_error = error_message
            
            # Desativar API se muitos erros consecutivos
            if status.error_count >= 5:
                status.is_active = False
                self.logger.warning(f"⚠️ API {api_key} desativada por muitos erros: {error_message}")
                
        self.save_status()
        
    def record_rate_limit(self, api_name: str, key_id: str, reset_time: Optional[datetime] = None):
        """Registra rate limiting de uma API"""
        api_key = f"{api_name}_{key_id}"
        
        if api_key not in self.api_statuses:
            self.register_api(api_name, key_id)
            
        status = self.api_statuses[api_key]
        status.rate_limit_reset = reset_time or (datetime.now() + timedelta(minutes=60))
        status.is_active = False
        
        self.logger.warning(f"⏱️ Rate limit atingido para {api_key}, reset em: {status.rate_limit_reset}")
        self.save_status()
        
    def record_credit_exhaustion(self, api_name: str, key_id: str, credits_remaining: int = 0):
        """Registra esgotamento de créditos"""
        api_key = f"{api_name}_{key_id}"
        
        if api_key not in self.api_statuses:
            self.register_api(api_name, key_id)
            
        status = self.api_statuses[api_key]
        status.credits_remaining = credits_remaining
        status.is_active = credits_remaining > 0
        
        if credits_remaining <= 0:
            self.logger.warning(f"💳 Créditos esgotados para {api_key}")
        else:
            self.logger.info(f"💳 {api_key}: {credits_remaining} créditos restantes")
            
        self.save_status()
        
    def get_best_api(self, api_name: str) -> Optional[str]:
        """Retorna a melhor API disponível para um serviço"""
        available_apis = []
        
        for key, status in self.api_statuses.items():
            if status.name == api_name and self.is_api_available(key):
                # Score baseado em sucesso, créditos e tempo desde último uso
                success_rate = status.success_count / max(1, status.success_count + status.error_count)
                
                # Penalizar APIs usadas recentemente para distribuir carga
                time_penalty = 0
                if status.last_request_time:
                    minutes_since_last = (datetime.now() - status.last_request_time).total_seconds() / 60
                    time_penalty = max(0, 10 - minutes_since_last) / 10  # Penalidade de 0-1
                
                # Score final (maior é melhor)
                score = success_rate - time_penalty
                
                available_apis.append((key, score, status))
                
        if available_apis:
            # Ordenar por score (maior primeiro)
            available_apis.sort(key=lambda x: x[1], reverse=True)
            best_api = available_apis[0][0]
            
            self.logger.info(f"🎯 Melhor API para {api_name}: {best_api}")
            return best_api
            
        self.logger.warning(f"⚠️ Nenhuma API disponível para {api_name}")
        return None
        
    def is_api_available(self, api_key: str) -> bool:
        """Verifica se uma API está disponível para uso"""
        if api_key not in self.api_statuses:
            return False
            
        status = self.api_statuses[api_key]
        
        # Verificar se está ativa
        if not status.is_active:
            # Verificar se rate limit expirou
            if status.rate_limit_reset and datetime.now() > status.rate_limit_reset:
                status.is_active = True
                status.rate_limit_reset = None
                self.logger.info(f"✅ Rate limit expirado, reativando {api_key}")
                self.save_status()
            else:
                return False
                
        # Verificar créditos
        if status.credits_remaining is not None and status.credits_remaining <= 0:
            return False
            
        # Verificar limite diário
        if status.daily_limit and status.requests_made >= status.daily_limit:
            # Reset diário às 00:00
            if status.last_request_time and status.last_request_time.date() < datetime.now().date():
                status.requests_made = 0
                self.logger.info(f"🔄 Reset diário para {api_key}")
                self.save_status()
            else:
                return False
                
        return True
        
    def get_api_statistics(self) -> Dict:
        """Retorna estatísticas das APIs"""
        stats = {
            'total_apis': len(self.api_statuses),
            'active_apis': 0,
            'total_requests': 0,
            'total_cost': 0.0,
            'by_service': {},
            'top_performers': [],
            'problematic_apis': []
        }
        
        for api_key, status in self.api_statuses.items():
            if status.is_active:
                stats['active_apis'] += 1
                
            stats['total_requests'] += status.requests_made
            stats['total_cost'] += status.total_cost
            
            # Estatísticas por serviço
            service = status.name
            if service not in stats['by_service']:
                stats['by_service'][service] = {
                    'total_apis': 0,
                    'active_apis': 0,
                    'total_requests': 0,
                    'success_rate': 0.0
                }
                
            service_stats = stats['by_service'][service]
            service_stats['total_apis'] += 1
            if status.is_active:
                service_stats['active_apis'] += 1
            service_stats['total_requests'] += status.requests_made
            
            # Taxa de sucesso
            total_ops = status.success_count + status.error_count
            if total_ops > 0:
                success_rate = status.success_count / total_ops
                service_stats['success_rate'] = (service_stats['success_rate'] + success_rate) / 2
                
                # Top performers (>90% sucesso, >10 requests)
                if success_rate > 0.9 and total_ops > 10:
                    stats['top_performers'].append({
                        'api': api_key,
                        'success_rate': success_rate,
                        'requests': total_ops
                    })
                    
                # APIs problemáticas (<50% sucesso, >5 requests)
                elif success_rate < 0.5 and total_ops > 5:
                    stats['problematic_apis'].append({
                        'api': api_key,
                        'success_rate': success_rate,
                        'error_count': status.error_count,
                        'last_error': status.last_error
                    })
                    
        return stats
        
    def cleanup_old_data(self, days: int = 30):
        """Remove dados antigos"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for api_key in list(self.api_statuses.keys()):
            status = self.api_statuses[api_key]
            
            # Remove APIs que não foram usadas há muito tempo
            if (status.last_request_time and 
                status.last_request_time < cutoff_date and 
                status.requests_made == 0):
                
                del self.api_statuses[api_key]
                self.logger.info(f"🗑️ Removida API inativa: {api_key}")
                
        self.save_status()
        
    def reset_daily_limits(self):
        """Reset manual dos limites diários"""
        for status in self.api_statuses.values():
            status.requests_made = 0
            
        self.save_status()
        self.logger.info("🔄 Limites diários resetados manualmente")
        
    def reactivate_api(self, api_key: str):
        """Reativa uma API manualmente"""
        if api_key in self.api_statuses:
            status = self.api_statuses[api_key]
            status.is_active = True
            status.error_count = 0
            status.rate_limit_reset = None
            
            self.save_status()
            self.logger.info(f"✅ API reativada manualmente: {api_key}")
            return True
            
        return False
    
    def detect_credit_error(self, error_response: Any, status_code: int = None) -> bool:
        """Detecta se o erro é relacionado a créditos/quota - ULTRA-ROBUSTO"""
        # Códigos HTTP que indicam problemas de crédito
        credit_status_codes = [400, 402, 429, 403]
        
        if status_code in credit_status_codes:
            return True
        
        # Análise de texto da resposta
        if isinstance(error_response, (str, dict)):
            error_text = str(error_response).lower()
            
            # Indicadores de falta de créditos
            credit_indicators = [
                'not enough credits', 'credits', 'quota', 'exceeded', 'limit',
                'billing', 'payment', 'subscription', 'plan', 'usage',
                'rate limit', 'too many requests', 'throttled',
                'insufficient funds', 'account suspended', 'upgrade',
                'no more credits', 'credit limit', 'daily limit',
                'monthly limit', 'api limit', 'request limit'
            ]
            
            return any(indicator in error_text for indicator in credit_indicators)
        
        return False
    
    def handle_api_error(self, api_name: str, key_id: str, error_response: Any, 
                        status_code: int = None) -> Dict[str, Any]:
        """Trata erros de API de forma inteligente"""
        api_key = f"{api_name}_{key_id}"
        
        # Detectar tipo de erro
        is_credit_error = self.detect_credit_error(error_response, status_code)
        is_rate_limit = status_code == 429 or 'rate limit' in str(error_response).lower()
        is_auth_error = status_code in [401, 403] and not is_credit_error
        
        # Registrar erro
        self.record_request(api_name, key_id, success=False, 
                          error_message=str(error_response))
        
        result = {
            'api_key': api_key,
            'error_type': 'unknown',
            'should_retry': False,
            'retry_after': 0,
            'switch_api': False,
            'disable_api': False
        }
        
        if is_credit_error:
            result['error_type'] = 'credits'
            result['disable_api'] = True
            result['switch_api'] = True
            
            # Registra esgotamento de créditos com detalhes
            self.record_credit_exhaustion(api_name, key_id, 0)
            
            # Atualiza status da API
            if api_key in self.api_statuses:
                self.api_statuses[api_key].is_active = False
                self.api_statuses[api_key].credits_remaining = 0
                self.api_statuses[api_key].last_error = f"CREDITS_EXHAUSTED_{status_code}: {str(error_response)[:100]}"
                
            # Log detalhado do esgotamento de créditos
            credit_details = {
                'api_name': api_name,
                'key_id': key_id,
                'status_code': status_code,
                'error_response': str(error_response)[:200],
                'timestamp': datetime.now().isoformat(),
                'requests_made_today': self.api_statuses.get(api_key, APIStatus('', '')).requests_made
            }
            
            self.logger.error(f"💳 {api_key}: Créditos esgotados (HTTP {status_code}) - API DESABILITADA")
            self.logger.error(f"   Detalhes: {credit_details}")
            
            # Verifica se há APIs alternativas disponíveis
            alternative_apis = self.get_available_apis_for_service(api_name)
            if alternative_apis:
                self.logger.info(f"🔄 APIs alternativas disponíveis para {api_name}: {len(alternative_apis)}")
            else:
                self.logger.critical(f"🚨 CRÍTICO: Nenhuma API alternativa disponível para {api_name}!")
                
            # Salva o status atualizado
            self.save_status()
            
        elif is_rate_limit:
            result['error_type'] = 'rate_limit'
            result['should_retry'] = True
            result['switch_api'] = True
            
            # Detecção inteligente do tempo de retry
            retry_after = self._extract_retry_after_time(error_response, api_name)
            result['retry_after'] = retry_after
            
            # Atualiza status da API
            reset_time = datetime.now() + timedelta(seconds=retry_after)
            self.record_rate_limit(api_name, key_id, reset_time)
            
            if api_key in self.api_statuses:
                self.api_statuses[api_key].rate_limit_reset = reset_time
                self.api_statuses[api_key].last_error = f"RATE_LIMITED_{status_code}: retry_after={retry_after}s"
            
            # Log detalhado do rate limiting
            rate_limit_details = {
                'api_name': api_name,
                'key_id': key_id,
                'status_code': status_code,
                'retry_after': retry_after,
                'reset_time': reset_time.isoformat(),
                'requests_made_today': self.api_statuses.get(api_key, APIStatus('', '')).requests_made
            }
            
            self.logger.warning(f"⏱️ {api_key}: Rate limit (HTTP {status_code}) - retry em {retry_after}s")
            self.logger.info(f"   Detalhes: {rate_limit_details}")
            
            # Verifica se há APIs alternativas disponíveis
            alternative_apis = self.get_available_apis_for_service(api_name)
            if alternative_apis:
                self.logger.info(f"🔄 {len(alternative_apis)} APIs alternativas disponíveis para {api_name}")
            
            # Salva o status atualizado
            self.save_status()
            
        elif is_auth_error:
            result['error_type'] = 'authentication'
            result['disable_api'] = True
            result['switch_api'] = True
            
            # Desabilita permanentemente a API com erro de autenticação
            if api_key in self.api_statuses:
                self.api_statuses[api_key].is_active = False
                self.api_statuses[api_key].last_error = f"AUTH_ERROR_{status_code}: {str(error_response)[:100]}"
                self.api_statuses[api_key].error_count += 1
                
            # Log detalhado do erro de autenticação
            error_details = {
                'api_name': api_name,
                'key_id': key_id,
                'status_code': status_code,
                'error_response': str(error_response)[:200],
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.error(f"🔒 {api_key}: Erro de autenticação (HTTP {status_code}) - API DESABILITADA")
            self.logger.error(f"   Detalhes: {error_details}")
            
            # Salva o status atualizado
            self.save_status()
            
        else:
            result['error_type'] = 'generic'
            result['should_retry'] = True
            result['retry_after'] = 5
            result['switch_api'] = True
            
        return result
    
    def get_next_available_api(self, api_name: str, exclude_keys: List[str] = None) -> Optional[str]:
        """Retorna próxima API disponível, excluindo as especificadas"""
        exclude_keys = exclude_keys or []
        
        available_apis = []
        for key, status in self.api_statuses.items():
            if (status.name == api_name and 
                key not in exclude_keys and 
                self.is_api_available(key)):
                
                # Score baseado em múltiplos fatores
                success_rate = status.success_count / max(1, status.success_count + status.error_count)
                
                # Penalizar APIs usadas recentemente
                time_penalty = 0
                if status.last_request_time:
                    minutes_since_last = (datetime.now() - status.last_request_time).total_seconds() / 60
                    time_penalty = max(0, 5 - minutes_since_last) / 5
                
                # Bonus para APIs com mais créditos
                credit_bonus = 0
                if status.credits_remaining:
                    credit_bonus = min(0.2, status.credits_remaining / 1000)
                
                score = success_rate - time_penalty + credit_bonus
                available_apis.append((key, score, status))
        
        if available_apis:
            available_apis.sort(key=lambda x: x[1], reverse=True)
            best_api = available_apis[0][0]
            self.logger.info(f"🎯 Próxima API para {api_name}: {best_api}")
            return best_api
        
        self.logger.warning(f"⚠️ Nenhuma API disponível para {api_name}")
        return None
    
    def generate_credit_report(self) -> Dict[str, Any]:
        """Gera relatório detalhado de créditos"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_apis': len(self.api_statuses),
                'active_apis': 0,
                'apis_with_credits': 0,
                'apis_rate_limited': 0,
                'total_requests_today': 0,
                'total_cost_today': 0.0
            },
            'by_service': {},
            'alerts': [],
            'recommendations': []
        }
        
        today = datetime.now().date()
        
        for api_key, status in self.api_statuses.items():
            service = status.name
            
            # Inicializar serviço se não existir
            if service not in report['by_service']:
                report['by_service'][service] = {
                    'total_apis': 0,
                    'active_apis': 0,
                    'total_requests': 0,
                    'success_rate': 0.0,
                    'apis': []
                }
            
            service_data = report['by_service'][service]
            service_data['total_apis'] += 1
            
            # Status da API
            api_info = {
                'key_id': status.key_id,
                'is_active': status.is_active,
                'credits_remaining': status.credits_remaining,
                'requests_made': status.requests_made,
                'success_rate': 0.0,
                'last_used': status.last_request_time.isoformat() if status.last_request_time else None
            }
            
            # Calcular taxa de sucesso
            total_ops = status.success_count + status.error_count
            if total_ops > 0:
                api_info['success_rate'] = status.success_count / total_ops
            
            service_data['apis'].append(api_info)
            
            # Atualizar contadores
            if status.is_active:
                report['summary']['active_apis'] += 1
                service_data['active_apis'] += 1
            
            if status.credits_remaining and status.credits_remaining > 0:
                report['summary']['apis_with_credits'] += 1
            
            if status.rate_limit_reset and status.rate_limit_reset > datetime.now():
                report['summary']['apis_rate_limited'] += 1
            
            # Requests de hoje
            if (status.last_request_time and 
                status.last_request_time.date() == today):
                report['summary']['total_requests_today'] += status.requests_made
                report['summary']['total_cost_today'] += status.total_cost
            
            # Gerar alertas
            self._generate_alerts_for_api(api_key, status, report['alerts'])
        
        # Gerar recomendações
        self._generate_recommendations(report)
        
        return report
    
    def _generate_alerts_for_api(self, api_key: str, status: APIStatus, alerts: List[Dict]):
        """Gera alertas para uma API específica"""
        # Alerta de créditos baixos
        if (status.credits_remaining is not None and 
            status.daily_limit and
            status.credits_remaining < (status.daily_limit * self.alert_thresholds['credits_low'])):
            alerts.append({
                'type': 'credits_low',
                'api': api_key,
                'message': f"Créditos baixos: {status.credits_remaining} restantes",
                'severity': 'warning'
            })
        
        # Alerta de taxa de erro alta
        total_ops = status.success_count + status.error_count
        if total_ops > 10:
            error_rate = status.error_count / total_ops
            if error_rate > self.alert_thresholds['error_rate_high']:
                alerts.append({
                    'type': 'high_error_rate',
                    'api': api_key,
                    'message': f"Taxa de erro alta: {error_rate:.1%}",
                    'severity': 'error'
                })
        
        # Alerta de API inativa
        if not status.is_active:
            alerts.append({
                'type': 'api_inactive',
                'api': api_key,
                'message': f"API inativa: {status.last_error}",
                'severity': 'critical'
            })
    
    def _generate_recommendations(self, report: Dict):
        """Gera recomendações baseadas no relatório"""
        recommendations = report['recommendations']
        
        # Recomendação para serviços sem APIs ativas
        for service, data in report['by_service'].items():
            if data['active_apis'] == 0:
                recommendations.append({
                    'type': 'no_active_apis',
                    'service': service,
                    'message': f"Serviço {service} sem APIs ativas - verificar chaves",
                    'priority': 'high'
                })
            elif data['active_apis'] == 1:
                recommendations.append({
                    'type': 'single_api',
                    'service': service,
                    'message': f"Serviço {service} com apenas 1 API ativa - considerar backup",
                    'priority': 'medium'
                })
        
        # Recomendação geral de créditos
        if report['summary']['apis_with_credits'] < report['summary']['total_apis'] * 0.5:
            recommendations.append({
                'type': 'low_credits_overall',
                'message': "Mais de 50% das APIs sem créditos - considerar recarga",
                'priority': 'high'
            })
    
    def get_authentication_issues_report(self) -> Dict[str, Any]:
        """Gera relatório específico de problemas de autenticação"""
        auth_issues = []
        
        for api_key, status in self.api_statuses.items():
            if not status.is_active and status.last_error and 'AUTH_ERROR' in status.last_error:
                auth_issues.append({
                    'api_key': api_key,
                    'api_name': status.name,
                    'key_id': status.key_id,
                    'error_message': status.last_error,
                    'error_count': status.error_count,
                    'last_request_time': status.last_request_time.isoformat() if status.last_request_time else None
                })
        
        return {
            'total_auth_issues': len(auth_issues),
            'affected_apis': auth_issues,
            'recommendations': [
                "Verificar se as chaves de API estão corretas no arquivo .env",
                "Confirmar se as chaves não expiraram",
                "Verificar se as contas têm as permissões necessárias",
                "Considerar regenerar chaves com problemas persistentes"
            ]
        }
    
    def disable_problematic_apis(self) -> Dict[str, int]:
        """Desabilita APIs com muitos erros de autenticação"""
        disabled_count = 0
        disabled_apis = []
        
        for api_key, status in self.api_statuses.items():
            # Desabilita APIs com mais de 3 erros de autenticação
            if (status.error_count >= 3 and 
                status.last_error and 
                'AUTH_ERROR' in status.last_error and 
                status.is_active):
                
                status.is_active = False
                disabled_count += 1
                disabled_apis.append(api_key)
                self.logger.warning(f"🚫 API {api_key} desabilitada automaticamente após {status.error_count} erros de autenticação")
        
        if disabled_count > 0:
            self.save_status()
            
        return {
            'disabled_count': disabled_count,
            'disabled_apis': disabled_apis
        }
    
    def get_available_apis_for_service(self, service_name: str) -> List[str]:
        """Retorna lista de APIs disponíveis para um serviço específico"""
        available_apis = []
        
        for api_key, status in self.api_statuses.items():
            if (status.name == service_name and 
                status.is_active and 
                self.is_api_available(api_key)):
                available_apis.append(api_key)
                
        return available_apis
    
    def get_available_apis(self, service_name: str) -> List[str]:
        """Alias para get_available_apis_for_service - mantém compatibilidade"""
        return self.get_available_apis_for_service(service_name)
    
    def get_credit_exhaustion_report(self) -> Dict[str, Any]:
        """Gera relatório específico de APIs com créditos esgotados"""
        exhausted_apis = []
        
        for api_key, status in self.api_statuses.items():
            if (not status.is_active and 
                status.last_error and 
                'CREDITS_EXHAUSTED' in status.last_error):
                exhausted_apis.append({
                    'api_key': api_key,
                    'api_name': status.name,
                    'key_id': status.key_id,
                    'error_message': status.last_error,
                    'requests_made': status.requests_made,
                    'last_request_time': status.last_request_time.isoformat() if status.last_request_time else None
                })
        
        # Agrupa por serviço
        by_service = {}
        for api in exhausted_apis:
            service = api['api_name']
            if service not in by_service:
                by_service[service] = {
                    'exhausted_count': 0,
                    'available_count': len(self.get_available_apis_for_service(service)),
                    'apis': []
                }
            by_service[service]['exhausted_count'] += 1
            by_service[service]['apis'].append(api)
        
        return {
            'total_exhausted': len(exhausted_apis),
            'exhausted_apis': exhausted_apis,
            'by_service': by_service,
            'critical_services': [
                service for service, data in by_service.items() 
                if data['available_count'] == 0
            ],
            'recommendations': [
                "Verificar saldo das contas de API",
                "Considerar upgrade para planos pagos",
                "Implementar cache mais agressivo para reduzir uso",
                "Distribuir carga entre mais chaves de API"
            ]
        }
    
    def _extract_retry_after_time(self, error_response: Any, api_name: str) -> int:
        """Extrai tempo de retry inteligentemente baseado na API e resposta"""
        
        # Tempos padrão por API (baseado em documentação real)
        default_retry_times = {
            'openrouter': 60,    # OpenRouter: 1 minuto
            'gemini': 60,        # Gemini: 1 minuto  
            'openai': 60,        # OpenAI: 1 minuto
            'serper': 60,        # Serper: 1 minuto
            'exa': 60,           # Exa: 1 minuto
            'jina': 30,          # Jina: 30 segundos
            'firecrawl': 60,     # Firecrawl: 1 minuto
            'apify': 60,         # Apify: 1 minuto
            'supadata': 60,      # Supadata: 1 minuto
            'tavily': 60,        # Tavily: 1 minuto
        }
        
        # 1. Tenta extrair da resposta HTTP
        if isinstance(error_response, dict):
            # Verifica headers comuns de rate limiting
            retry_after = error_response.get('retry_after')
            if retry_after:
                try:
                    return int(retry_after)
                except (ValueError, TypeError):
                    pass
            
            # Verifica outros campos comuns
            for field in ['retry-after', 'Retry-After', 'x-ratelimit-reset', 'X-RateLimit-Reset']:
                value = error_response.get(field)
                if value:
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        pass
        
        # 2. Analisa texto da resposta para pistas
        if isinstance(error_response, (str, dict)):
            error_text = str(error_response).lower()
            
            # Procura por padrões de tempo na mensagem
            import re
            
            # Padrões como "try again in 60 seconds", "wait 2 minutes"
            time_patterns = [
                r'try again in (\d+) seconds?',
                r'wait (\d+) seconds?',
                r'retry after (\d+) seconds?',
                r'wait (\d+) minutes?',
                r'try again in (\d+) minutes?'
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, error_text)
                if match:
                    time_value = int(match.group(1))
                    # Se menciona minutos, converte para segundos
                    if 'minute' in pattern:
                        time_value *= 60
                    return min(time_value, 300)  # Máximo 5 minutos
        
        # 3. Usa tempo padrão baseado na API
        default_time = default_retry_times.get(api_name, 60)
        
        # 4. Aplica backoff exponencial se a API tem muitos rate limits recentes
        api_key = f"{api_name}_1"  # Assume key padrão para estatísticas
        if api_key in self.api_statuses:
            status = self.api_statuses[api_key]
            
            # Se teve rate limit recente, aumenta o tempo
            if (status.rate_limit_reset and 
                status.rate_limit_reset > datetime.now() - timedelta(minutes=10)):
                default_time = min(default_time * 2, 300)  # Dobra até máximo de 5 minutos
        
        return default_time
    
    def get_rate_limit_report(self) -> Dict[str, Any]:
        """Gera relatório específico de rate limiting"""
        rate_limited_apis = []
        
        for api_key, status in self.api_statuses.items():
            if (status.rate_limit_reset and 
                status.rate_limit_reset > datetime.now()):
                
                time_remaining = (status.rate_limit_reset - datetime.now()).total_seconds()
                rate_limited_apis.append({
                    'api_key': api_key,
                    'api_name': status.name,
                    'key_id': status.key_id,
                    'reset_time': status.rate_limit_reset.isoformat(),
                    'time_remaining_seconds': int(time_remaining),
                    'last_error': status.last_error
                })
        
        # Agrupa por serviço
        by_service = {}
        for api in rate_limited_apis:
            service = api['api_name']
            if service not in by_service:
                by_service[service] = {
                    'rate_limited_count': 0,
                    'available_count': len(self.get_available_apis_for_service(service)),
                    'apis': []
                }
            by_service[service]['rate_limited_count'] += 1
            by_service[service]['apis'].append(api)
        
        return {
            'total_rate_limited': len(rate_limited_apis),
            'rate_limited_apis': rate_limited_apis,
            'by_service': by_service,
            'services_affected': list(by_service.keys()),
            'recommendations': [
                "Implementar delays entre requisições",
                "Usar mais chaves de API para distribuir carga",
                "Implementar cache mais agressivo",
                "Considerar upgrade para planos com rate limits maiores"
            ]
        }