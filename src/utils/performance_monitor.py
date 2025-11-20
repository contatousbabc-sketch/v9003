#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Monitor de Performance
Sistema de monitoramento em tempo real de performance
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from collections import defaultdict, deque
import threading
import asyncio

# Importar sistema de performance
try:
    from performance_optimizer import get_performance_optimizer, get_performance_stats
    PERFORMANCE_OPTIMIZER_AVAILABLE = True
except ImportError:
    PERFORMANCE_OPTIMIZER_AVAILABLE = False

# Importar sistema de logging
try:
    from enhanced_logging_system import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor de Performance em Tempo Real V2.0"""
    
    def __init__(self, report_dir: str = "reports", monitoring_interval: int = 60):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
        
        self.monitoring_interval = monitoring_interval
        self.performance_optimizer_available = PERFORMANCE_OPTIMIZER_AVAILABLE
        
        # Histórico de métricas
        self.metrics_history = deque(maxlen=1440)  # 24 horas de dados (1 por minuto)
        
        # Alertas de performance
        self.alert_thresholds = {
            'avg_duration': 5.0,  # 5 segundos
            'error_rate': 10.0,   # 10%
            'success_rate': 90.0, # 90%
            'cache_hit_rate': 20.0 # 20%
        }
        
        # Estado do monitoramento
        self.monitoring_active = False
        self.monitoring_thread = None
        
        logger.info("📊 Monitor de Performance em Tempo Real V2.0 inicializado")
    
    def start_monitoring(self):
        """Inicia monitoramento em tempo real"""
        if self.monitoring_active:
            logger.warning("⚠️ Monitoramento já está ativo")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info(f"🚀 Monitoramento de performance iniciado (intervalo: {self.monitoring_interval}s)")
    
    def stop_monitoring(self):
        """Para monitoramento em tempo real"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        
        logger.info("🛑 Monitoramento de performance parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring_active:
            try:
                # Coletar métricas
                metrics = self._collect_metrics()
                
                if metrics:
                    # Armazenar no histórico
                    self.metrics_history.append(metrics)
                    
                    # Verificar alertas
                    alerts = self._check_alerts(metrics)
                    
                    if alerts:
                        self._handle_alerts(alerts)
                    
                    # Log de status
                    self._log_status(metrics)
                
                # Aguardar próximo ciclo
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_metrics(self) -> Optional[Dict[str, Any]]:
        """Coleta métricas de performance"""
        if not self.performance_optimizer_available:
            return None
        
        try:
            stats = get_performance_stats()
            
            if stats.get('total_requests', 0) == 0:
                return None
            
            # Adicionar timestamp
            stats['collection_timestamp'] = datetime.now().isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas: {e}")
            return None
    
    def _check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verifica se há alertas de performance"""
        alerts = []
        
        # Verificar duração média
        avg_duration = metrics.get('avg_duration', 0)
        if avg_duration > self.alert_thresholds['avg_duration']:
            alerts.append({
                'type': 'high_latency',
                'severity': 'warning',
                'message': f"Latência alta: {avg_duration:.2f}s (limite: {self.alert_thresholds['avg_duration']}s)",
                'value': avg_duration,
                'threshold': self.alert_thresholds['avg_duration']
            })
        
        # Verificar taxa de erro
        error_rate = metrics.get('error_rate', 0)
        if error_rate > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'critical' if error_rate > 20 else 'warning',
                'message': f"Taxa de erro alta: {error_rate:.1f}% (limite: {self.alert_thresholds['error_rate']}%)",
                'value': error_rate,
                'threshold': self.alert_thresholds['error_rate']
            })
        
        # Verificar taxa de sucesso
        success_rate = metrics.get('success_rate', 100)
        if success_rate < self.alert_thresholds['success_rate']:
            alerts.append({
                'type': 'low_success_rate',
                'severity': 'critical' if success_rate < 80 else 'warning',
                'message': f"Taxa de sucesso baixa: {success_rate:.1f}% (limite: {self.alert_thresholds['success_rate']}%)",
                'value': success_rate,
                'threshold': self.alert_thresholds['success_rate']
            })
        
        # Verificar taxa de cache hit
        cache_hit_rate = metrics.get('cache_hit_rate', 0)
        if cache_hit_rate < self.alert_thresholds['cache_hit_rate']:
            alerts.append({
                'type': 'low_cache_hit_rate',
                'severity': 'info',
                'message': f"Taxa de cache baixa: {cache_hit_rate:.1f}% (limite: {self.alert_thresholds['cache_hit_rate']}%)",
                'value': cache_hit_rate,
                'threshold': self.alert_thresholds['cache_hit_rate']
            })
        
        return alerts
    
    def _handle_alerts(self, alerts: List[Dict[str, Any]]):
        """Trata alertas de performance"""
        for alert in alerts:
            severity = alert['severity']
            message = alert['message']
            
            if severity == 'critical':
                logger.error(f"🚨 CRÍTICO: {message}")
            elif severity == 'warning':
                logger.warning(f"⚠️ AVISO: {message}")
            else:
                logger.info(f"ℹ️ INFO: {message}")
    
    def _log_status(self, metrics: Dict[str, Any]):
        """Log de status de performance"""
        total_requests = metrics.get('total_requests', 0)
        success_rate = metrics.get('success_rate', 0)
        avg_duration = metrics.get('avg_duration', 0)
        cache_hit_rate = metrics.get('cache_hit_rate', 0)
        
        logger.info(f"📊 Performance: {total_requests} req, {success_rate:.1f}% sucesso, {avg_duration:.2f}s média, {cache_hit_rate:.1f}% cache")
    
    def get_performance_trends(self, hours: int = 1) -> Dict[str, Any]:
        """Obtém tendências de performance"""
        if not self.metrics_history:
            return {'message': 'Nenhum dado histórico disponível'}
        
        # Filtrar dados por período
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m['collection_timestamp']) > cutoff_time
        ]
        
        if not recent_metrics:
            return {'message': f'Nenhum dado dos últimos {hours} hora(s)'}
        
        # Calcular tendências
        durations = [m.get('avg_duration', 0) for m in recent_metrics]
        success_rates = [m.get('success_rate', 0) for m in recent_metrics]
        error_rates = [m.get('error_rate', 0) for m in recent_metrics]
        cache_rates = [m.get('cache_hit_rate', 0) for m in recent_metrics]
        
        # Calcular médias e tendências
        def calculate_trend(values):
            if len(values) < 2:
                return 'stable'
            
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            
            change_percent = ((avg_second - avg_first) / avg_first * 100) if avg_first > 0 else 0
            
            if change_percent > 10:
                return 'increasing'
            elif change_percent < -10:
                return 'decreasing'
            else:
                return 'stable'
        
        return {
            'period_hours': hours,
            'data_points': len(recent_metrics),
            'avg_duration': {
                'current': durations[-1] if durations else 0,
                'average': sum(durations) / len(durations) if durations else 0,
                'trend': calculate_trend(durations)
            },
            'success_rate': {
                'current': success_rates[-1] if success_rates else 0,
                'average': sum(success_rates) / len(success_rates) if success_rates else 0,
                'trend': calculate_trend(success_rates)
            },
            'error_rate': {
                'current': error_rates[-1] if error_rates else 0,
                'average': sum(error_rates) / len(error_rates) if error_rates else 0,
                'trend': calculate_trend(error_rates)
            },
            'cache_hit_rate': {
                'current': cache_rates[-1] if cache_rates else 0,
                'average': sum(cache_rates) / len(cache_rates) if cache_rates else 0,
                'trend': calculate_trend(cache_rates)
            }
        }
    
    def generate_performance_dashboard(self) -> str:
        """Gera dashboard de performance"""
        current_stats = get_performance_stats() if self.performance_optimizer_available else {}
        trends = self.get_performance_trends(1)  # Última hora
        
        dashboard = f"""# Dashboard de Performance - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Status Atual

- **Total de Requisições**: {current_stats.get('total_requests', 0)}
- **Taxa de Sucesso**: {current_stats.get('success_rate', 0):.2f}%
- **Duração Média**: {current_stats.get('avg_duration', 0):.3f}s
- **Taxa de Cache Hit**: {current_stats.get('cache_hit_rate', 0):.2f}%
- **Taxa de Erro**: {current_stats.get('error_rate', 0):.2f}%

## 📈 Tendências (Última Hora)

"""
        
        if 'data_points' in trends:
            dashboard += f"**Pontos de Dados**: {trends['data_points']}\n\n"
            
            # Duração
            duration_trend = trends['avg_duration']
            trend_icon = {'increasing': '📈', 'decreasing': '📉', 'stable': '➡️'}
            dashboard += f"### ⏱️ Duração\n"
            dashboard += f"- **Atual**: {duration_trend['current']:.3f}s\n"
            dashboard += f"- **Média**: {duration_trend['average']:.3f}s\n"
            dashboard += f"- **Tendência**: {trend_icon.get(duration_trend['trend'], '➡️')} {duration_trend['trend']}\n\n"
            
            # Taxa de sucesso
            success_trend = trends['success_rate']
            dashboard += f"### ✅ Taxa de Sucesso\n"
            dashboard += f"- **Atual**: {success_trend['current']:.2f}%\n"
            dashboard += f"- **Média**: {success_trend['average']:.2f}%\n"
            dashboard += f"- **Tendência**: {trend_icon.get(success_trend['trend'], '➡️')} {success_trend['trend']}\n\n"
            
            # Taxa de erro
            error_trend = trends['error_rate']
            dashboard += f"### ❌ Taxa de Erro\n"
            dashboard += f"- **Atual**: {error_trend['current']:.2f}%\n"
            dashboard += f"- **Média**: {error_trend['average']:.2f}%\n"
            dashboard += f"- **Tendência**: {trend_icon.get(error_trend['trend'], '➡️')} {error_trend['trend']}\n\n"
        
        # Performance por host
        host_stats = current_stats.get('host_stats', {})
        if host_stats:
            dashboard += "## 🌐 Performance por Host\n\n"
            for host, stats in list(host_stats.items())[:5]:  # Top 5 hosts
                dashboard += f"### {host}\n"
                dashboard += f"- **Requisições**: {stats['requests']}\n"
                dashboard += f"- **Duração Média**: {stats['avg_duration']:.3f}s\n"
                dashboard += f"- **Taxa de Sucesso**: {stats['success_rate']:.2f}%\n"
                dashboard += f"- **Timeout Adaptativo**: {stats['adaptive_timeout']:.1f}s\n\n"
        
        # Status do monitoramento
        dashboard += f"## 🔍 Status do Monitoramento\n\n"
        dashboard += f"- **Monitoramento Ativo**: {'✅ Sim' if self.monitoring_active else '❌ Não'}\n"
        dashboard += f"- **Intervalo**: {self.monitoring_interval}s\n"
        dashboard += f"- **Histórico**: {len(self.metrics_history)} pontos de dados\n"
        dashboard += f"- **Otimizador Disponível**: {'✅ Sim' if self.performance_optimizer_available else '❌ Não'}\n"
        
        return dashboard
    
    def save_dashboard(self) -> str:
        """Salva dashboard em arquivo"""
        dashboard_content = self.generate_performance_dashboard()
        
        dashboard_file = self.report_dir / f"performance_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)
        
        logger.info(f"📄 Dashboard de performance salvo: {dashboard_file}")
        return str(dashboard_file)
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Obtém resumo de alertas"""
        if not self.performance_optimizer_available:
            return {'message': 'Sistema de performance não disponível'}
        
        current_metrics = get_performance_stats()
        alerts = self._check_alerts(current_metrics)
        
        alert_counts = defaultdict(int)
        for alert in alerts:
            alert_counts[alert['severity']] += 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_alerts': len(alerts),
            'critical': alert_counts['critical'],
            'warning': alert_counts['warning'],
            'info': alert_counts['info'],
            'alerts': alerts
        }

# Instância global do monitor
_performance_monitor_instance = None

def get_performance_monitor() -> PerformanceMonitor:
    """Obtém instância global do monitor"""
    global _performance_monitor_instance
    if _performance_monitor_instance is None:
        _performance_monitor_instance = PerformanceMonitor()
    return _performance_monitor_instance

# Funções de conveniência
def start_performance_monitoring():
    """Inicia monitoramento de performance"""
    get_performance_monitor().start_monitoring()

def stop_performance_monitoring():
    """Para monitoramento de performance"""
    get_performance_monitor().stop_monitoring()

def get_performance_trends(hours: int = 1) -> Dict[str, Any]:
    """Obtém tendências de performance"""
    return get_performance_monitor().get_performance_trends(hours)

def save_performance_dashboard() -> str:
    """Salva dashboard de performance"""
    return get_performance_monitor().save_dashboard()

def get_alert_summary() -> Dict[str, Any]:
    """Obtém resumo de alertas"""
    return get_performance_monitor().get_alert_summary()