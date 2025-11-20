#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Quality Monitor
Sistema avançado de monitoramento de qualidade com alertas e recuperação automática
"""

import time
import logging
import json
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class QualityMetric:
    """Métrica de qualidade"""
    service_name: str
    metric_type: str
    value: float
    timestamp: datetime
    session_id: str
    details: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class QualityThresholds:
    """Thresholds de qualidade para diferentes serviços"""
    
    # Success rates mínimos
    SUCCESS_RATE_CRITICAL = 0.1    # Abaixo disso é crítico
    SUCCESS_RATE_WARNING = 0.5     # Abaixo disso é warning
    SUCCESS_RATE_GOOD = 0.8        # Acima disso é bom
    
    # Response times máximos (segundos)
    RESPONSE_TIME_FAST = 5.0       # Resposta rápida
    RESPONSE_TIME_ACCEPTABLE = 15.0 # Resposta aceitável
    RESPONSE_TIME_SLOW = 30.0      # Resposta lenta
    
    # Error rates máximos
    ERROR_RATE_LOW = 0.05          # Taxa de erro baixa
    ERROR_RATE_MEDIUM = 0.15       # Taxa de erro média
    ERROR_RATE_HIGH = 0.30         # Taxa de erro alta

class QualityMonitor:
    """Monitor avançado de qualidade com alertas e recuperação"""
    
    def __init__(self, window_size: int = 100, alert_threshold: int = 5):
        self.window_size = window_size
        self.alert_threshold = alert_threshold
        
        # Armazenamento de métricas por serviço
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.service_status: Dict[str, str] = {}  # healthy, warning, critical
        self.alert_counts: Dict[str, int] = defaultdict(int)
        
        # Callbacks para alertas
        self.alert_callbacks: List[Callable] = []
        self.recovery_callbacks: Dict[str, Callable] = {}
        
        # Thread para monitoramento contínuo
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Lock para thread safety
        self.lock = threading.Lock()
        
        logger.info("✅ Quality Monitor inicializado")
    
    def record_metric(self, service_name: str, metric_type: str, value: float, 
                     session_id: str = None, details: Dict[str, Any] = None):
        """Registra uma métrica de qualidade"""
        
        metric = QualityMetric(
            service_name=service_name,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            session_id=session_id or f"session_{int(time.time())}",
            details=details or {}
        )
        
        with self.lock:
            self.metrics[service_name].append(metric)
            self._evaluate_service_health(service_name)
        
        logger.debug(f"📊 Métrica registrada: {service_name}.{metric_type} = {value}")
    
    def _evaluate_service_health(self, service_name: str):
        """Avalia a saúde de um serviço baseado nas métricas recentes"""
        
        if service_name not in self.metrics or len(self.metrics[service_name]) < 5:
            return
        
        recent_metrics = list(self.metrics[service_name])[-20:]  # Últimas 20 métricas
        
        # Calcula estatísticas
        success_rates = [m.value for m in recent_metrics if m.metric_type == 'success_rate']
        response_times = [m.value for m in recent_metrics if m.metric_type == 'response_time']
        error_rates = [m.value for m in recent_metrics if m.metric_type == 'error_rate']
        
        # Determina status baseado nas métricas
        status = 'healthy'
        issues = []
        
        # Avalia success rate
        if success_rates:
            avg_success = statistics.mean(success_rates)
            if avg_success < QualityThresholds.SUCCESS_RATE_CRITICAL:
                status = 'critical'
                issues.append(f"Success rate crítico: {avg_success:.1%}")
            elif avg_success < QualityThresholds.SUCCESS_RATE_WARNING:
                status = 'warning' if status != 'critical' else status
                issues.append(f"Success rate baixo: {avg_success:.1%}")
        
        # Avalia response time
        if response_times:
            avg_response = statistics.mean(response_times)
            if avg_response > QualityThresholds.RESPONSE_TIME_SLOW:
                status = 'warning' if status == 'healthy' else status
                issues.append(f"Response time alto: {avg_response:.1f}s")
        
        # Avalia error rate
        if error_rates:
            avg_errors = statistics.mean(error_rates)
            if avg_errors > QualityThresholds.ERROR_RATE_HIGH:
                status = 'critical'
                issues.append(f"Error rate alto: {avg_errors:.1%}")
            elif avg_errors > QualityThresholds.ERROR_RATE_MEDIUM:
                status = 'warning' if status != 'critical' else status
                issues.append(f"Error rate elevado: {avg_errors:.1%}")
        
        # Atualiza status e dispara alertas se necessário
        old_status = self.service_status.get(service_name, 'healthy')
        self.service_status[service_name] = status
        
        if status != 'healthy' and status != old_status:
            self._trigger_alert(service_name, status, issues)
        elif status == 'healthy' and old_status != 'healthy':
            self._trigger_recovery(service_name)
    
    def _trigger_alert(self, service_name: str, status: str, issues: List[str]):
        """Dispara alerta para um serviço"""
        
        self.alert_counts[service_name] += 1
        
        alert_data = {
            'service': service_name,
            'status': status,
            'issues': issues,
            'timestamp': datetime.now().isoformat(),
            'alert_count': self.alert_counts[service_name]
        }
        
        logger.warning(f"🚨 ALERTA {status.upper()}: {service_name} - {', '.join(issues)}")
        
        # Chama callbacks de alerta
        for callback in self.alert_callbacks:
            try:
                callback(alert_data)
            except Exception as e:
                logger.error(f"Erro no callback de alerta: {e}")
        
        # Tenta recuperação automática se configurada
        if service_name in self.recovery_callbacks and self.alert_counts[service_name] >= self.alert_threshold:
            self._attempt_recovery(service_name)
    
    def _trigger_recovery(self, service_name: str):
        """Dispara evento de recuperação"""
        
        self.alert_counts[service_name] = 0
        
        logger.info(f"✅ RECUPERAÇÃO: {service_name} voltou ao normal")
        
        recovery_data = {
            'service': service_name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Notifica callbacks sobre recuperação
        for callback in self.alert_callbacks:
            try:
                callback(recovery_data)
            except Exception as e:
                logger.error(f"Erro no callback de recuperação: {e}")
    
    def _attempt_recovery(self, service_name: str):
        """Tenta recuperação automática de um serviço"""
        
        if service_name not in self.recovery_callbacks:
            return
        
        logger.info(f"🔧 Tentando recuperação automática para {service_name}")
        
        try:
            recovery_func = self.recovery_callbacks[service_name]
            success = recovery_func()
            
            if success:
                logger.info(f"✅ Recuperação automática bem-sucedida para {service_name}")
                self.alert_counts[service_name] = 0
            else:
                logger.warning(f"⚠️ Recuperação automática falhou para {service_name}")
                
        except Exception as e:
            logger.error(f"❌ Erro na recuperação automática de {service_name}: {e}")
    
    def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Retorna informações de saúde de um serviço"""
        
        with self.lock:
            if service_name not in self.metrics:
                return {'status': 'unknown', 'message': 'Nenhuma métrica disponível'}
            
            recent_metrics = list(self.metrics[service_name])[-10:]
            
            # Calcula estatísticas recentes
            stats = {}
            for metric_type in ['success_rate', 'response_time', 'error_rate']:
                values = [m.value for m in recent_metrics if m.metric_type == metric_type]
                if values:
                    stats[metric_type] = {
                        'current': values[-1],
                        'average': statistics.mean(values),
                        'min': min(values),
                        'max': max(values)
                    }
            
            return {
                'service': service_name,
                'status': self.service_status.get(service_name, 'healthy'),
                'alert_count': self.alert_counts[service_name],
                'metrics_count': len(self.metrics[service_name]),
                'statistics': stats,
                'last_update': recent_metrics[-1].timestamp.isoformat() if recent_metrics else None
            }
    
    def get_all_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Retorna saúde de todos os serviços"""
        
        result = {}
        for service_name in self.metrics.keys():
            result[service_name] = self.get_service_health(service_name)
        
        return result
    
    def register_alert_callback(self, callback: Callable):
        """Registra callback para alertas"""
        self.alert_callbacks.append(callback)
    
    def register_recovery_callback(self, service_name: str, callback: Callable):
        """Registra callback para recuperação automática"""
        self.recovery_callbacks[service_name] = callback
    
    def start_monitoring(self, interval: int = 60):
        """Inicia monitoramento contínuo"""
        
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info(f"🔄 Monitoramento contínuo iniciado (intervalo: {interval}s)")
    
    def stop_monitoring(self):
        """Para monitoramento contínuo"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        logger.info("⏹️ Monitoramento contínuo parado")
    
    def _monitoring_loop(self, interval: int):
        """Loop de monitoramento contínuo"""
        
        while self.monitoring_active:
            try:
                # Avalia saúde de todos os serviços
                with self.lock:
                    for service_name in list(self.metrics.keys()):
                        self._evaluate_service_health(service_name)
                
                # Limpa métricas antigas (mais de 24h)
                self._cleanup_old_metrics()
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(interval)
    
    def _cleanup_old_metrics(self):
        """Remove métricas antigas para economizar memória"""
        
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        with self.lock:
            for service_name in list(self.metrics.keys()):
                metrics_queue = self.metrics[service_name]
                
                # Remove métricas antigas
                while metrics_queue and metrics_queue[0].timestamp < cutoff_time:
                    metrics_queue.popleft()
                
                # Remove serviços sem métricas
                if not metrics_queue:
                    del self.metrics[service_name]
                    if service_name in self.service_status:
                        del self.service_status[service_name]
                    if service_name in self.alert_counts:
                        del self.alert_counts[service_name]

# Instância global
quality_monitor = QualityMonitor()

# Funções de conveniência
def record_success_rate(service_name: str, success_rate: float, session_id: str = None):
    """Registra taxa de sucesso"""
    quality_monitor.record_metric(service_name, 'success_rate', success_rate, session_id)

def record_response_time(service_name: str, response_time: float, session_id: str = None):
    """Registra tempo de resposta"""
    quality_monitor.record_metric(service_name, 'response_time', response_time, session_id)

def record_error_rate(service_name: str, error_rate: float, session_id: str = None):
    """Registra taxa de erro"""
    quality_monitor.record_metric(service_name, 'error_rate', error_rate, session_id)

def get_service_status(service_name: str) -> str:
    """Retorna status de um serviço"""
    health = quality_monitor.get_service_health(service_name)
    return health.get('status', 'unknown')

# Callback padrão para alertas
def default_alert_callback(alert_data: Dict[str, Any]):
    """Callback padrão para alertas"""
    service = alert_data['service']
    status = alert_data['status']
    issues = alert_data.get('issues', [])
    
    if status == 'critical':
        logger.critical(f"🚨 CRÍTICO: {service} - {', '.join(issues)}")
    elif status == 'warning':
        logger.warning(f"⚠️ AVISO: {service} - {', '.join(issues)}")
    else:
        logger.info(f"✅ RECUPERAÇÃO: {service}")

# Registra callback padrão
quality_monitor.register_alert_callback(default_alert_callback)