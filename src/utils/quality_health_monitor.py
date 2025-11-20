#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Quality Health Monitor
Monitor em tempo real da saúde do sistema de qualidade
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
import json
import time

try:
    from quality_system_fixer import quality_fixer, get_smart_system_overview
    SMART_QUALITY_AVAILABLE = True
except ImportError:
    SMART_QUALITY_AVAILABLE = False

logger = logging.getLogger(__name__)

class QualityHealthMonitor:
    """Monitor de saúde do sistema de qualidade"""
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.monitoring_active = False
        self.last_report = None
        self.alert_history = []
        
    async def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        
        if not SMART_QUALITY_AVAILABLE:
            logger.error("❌ Sistema inteligente de qualidade não disponível")
            return
        
        self.monitoring_active = True
        logger.info(f"🔍 Iniciando monitoramento de saúde (intervalo: {self.check_interval}s)")
        
        while self.monitoring_active:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento de saúde: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring_active = False
        logger.info("⏹️ Monitoramento de saúde parado")
    
    async def _perform_health_check(self):
        """Executa verificação de saúde"""
        
        try:
            # Obtém visão geral do sistema
            overview = get_smart_system_overview()
            self.last_report = overview
            
            # Verifica se há alertas necessários
            await self._check_for_alerts(overview)
            
            # Log periódico do status
            self._log_system_status(overview)
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de saúde: {e}")
    
    async def _check_for_alerts(self, overview: Dict[str, Any]):
        """Verifica se há necessidade de alertas"""
        
        current_time = datetime.now()
        
        # Alerta para taxa de sucesso geral baixa
        overall_rate = overview.get('overall_success_rate', 0)
        if overall_rate < 0.3:
            alert = {
                'timestamp': current_time.isoformat(),
                'type': 'critical_success_rate',
                'message': f"Taxa de sucesso geral crítica: {overall_rate:.1%}",
                'overall_rate': overall_rate
            }
            await self._trigger_alert(alert)
        
        # Alerta para componentes críticos
        critical_components = [
            name for name, health in overview.get('components', {}).items()
            if health.get('status') == 'critical'
        ]
        
        if critical_components:
            alert = {
                'timestamp': current_time.isoformat(),
                'type': 'critical_components',
                'message': f"Componentes críticos: {', '.join(critical_components)}",
                'components': critical_components
            }
            await self._trigger_alert(alert)
        
        # Alerta para sistema inativo
        active_components = overview.get('active_components', 0)
        if active_components == 0:
            alert = {
                'timestamp': current_time.isoformat(),
                'type': 'system_inactive',
                'message': "Sistema aparenta estar inativo - nenhum componente ativo",
                'active_components': active_components
            }
            await self._trigger_alert(alert)
    
    async def _trigger_alert(self, alert: Dict[str, Any]):
        """Dispara alerta se não foi disparado recentemente"""
        
        # Evita spam de alertas do mesmo tipo
        recent_alerts = [
            a for a in self.alert_history[-10:]  # Últimos 10 alertas
            if a.get('type') == alert['type']
            and (datetime.now() - datetime.fromisoformat(a['timestamp'])).total_seconds() < 300  # 5 minutos
        ]
        
        if not recent_alerts:
            logger.warning(f"🚨 ALERTA DE SAÚDE: {alert['message']}")
            self.alert_history.append(alert)
            
            # Mantém histórico limitado
            if len(self.alert_history) > 100:
                self.alert_history = self.alert_history[-50:]
    
    def _log_system_status(self, overview: Dict[str, Any]):
        """Log periódico do status do sistema"""
        
        overall_rate = overview.get('overall_success_rate', 0)
        overall_status = overview.get('overall_status', 'unknown')
        active_components = overview.get('active_components', 0)
        total_components = overview.get('total_components', 0)
        
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '❌',
            'unknown': '❓'
        }.get(overall_status, '❓')
        
        logger.info(
            f"{status_emoji} Sistema: {overall_rate:.1%} sucesso | "
            f"{active_components}/{total_components} componentes ativos | "
            f"Status: {overall_status}"
        )
        
        # Log detalhado a cada 5 minutos
        if hasattr(self, '_last_detailed_log'):
            if (datetime.now() - self._last_detailed_log).total_seconds() < 300:
                return
        
        self._last_detailed_log = datetime.now()
        
        # Log detalhado dos componentes
        for component, health in overview.get('components', {}).items():
            if health.get('total_attempts', 0) > 0:
                rate = health.get('success_rate', 0)
                status = health.get('status', 'unknown')
                attempts = health.get('total_attempts', 0)
                
                component_emoji = {
                    'excellent': '🟢',
                    'good': '🟡',
                    'acceptable': '🟠',
                    'poor': '🔴',
                    'critical': '⚫'
                }.get(status, '❓')
                
                logger.info(f"  {component_emoji} {component}: {rate:.1%} ({attempts} tentativas)")
    
    def get_current_status(self) -> Dict[str, Any]:
        """Retorna status atual do sistema"""
        
        if not SMART_QUALITY_AVAILABLE:
            return {
                'error': 'Sistema inteligente de qualidade não disponível',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            overview = get_smart_system_overview()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'monitoring_active': self.monitoring_active,
                'system_overview': overview,
                'recent_alerts': self.alert_history[-5:] if self.alert_history else [],
                'health_summary': self._generate_health_summary(overview)
            }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_health_summary(self, overview: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resumo de saúde"""
        
        overall_rate = overview.get('overall_success_rate', 0)
        components = overview.get('components', {})
        
        # Conta componentes por status
        status_counts = {}
        for health in components.values():
            status = health.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Identifica componentes problemáticos
        problematic = [
            name for name, health in components.items()
            if health.get('status') in ['poor', 'critical']
        ]
        
        return {
            'overall_health': 'healthy' if overall_rate >= 0.8 else 'warning' if overall_rate >= 0.5 else 'critical',
            'success_rate': overall_rate,
            'status_distribution': status_counts,
            'problematic_components': problematic,
            'total_components': len(components),
            'active_components': len([c for c in components.values() if c.get('total_attempts', 0) > 0])
        }
    
    def generate_health_report(self) -> str:
        """Gera relatório de saúde em texto"""
        
        status = self.get_current_status()
        
        if 'error' in status:
            return f"❌ Erro ao gerar relatório: {status['error']}"
        
        overview = status['system_overview']
        summary = status['health_summary']
        
        report = f"""
# 🏥 RELATÓRIO DE SAÚDE DO SISTEMA
**Data:** {status['timestamp']}

## 📊 RESUMO EXECUTIVO
- **Saúde Geral:** {summary['overall_health'].upper()}
- **Taxa de Sucesso:** {summary['success_rate']:.1%}
- **Componentes Ativos:** {summary['active_components']}/{summary['total_components']}

## 🎯 STATUS DOS COMPONENTES
"""
        
        for status_type, count in summary['status_distribution'].items():
            emoji = {
                'excellent': '🟢',
                'good': '🟡', 
                'acceptable': '🟠',
                'poor': '🔴',
                'critical': '⚫'
            }.get(status_type, '❓')
            
            report += f"- {emoji} **{status_type.title()}:** {count} componente(s)\n"
        
        if summary['problematic_components']:
            report += f"\n## ⚠️ COMPONENTES PROBLEMÁTICOS\n"
            for component in summary['problematic_components']:
                health = overview['components'][component]
                rate = health.get('success_rate', 0)
                report += f"- **{component}:** {rate:.1%} sucesso\n"
        
        # Recomendações do sistema
        recommendations = overview.get('system_recommendations', [])
        if recommendations:
            report += f"\n## 💡 RECOMENDAÇÕES\n"
            for rec in recommendations:
                report += f"- {rec}\n"
        
        return report

# Instância global
health_monitor = QualityHealthMonitor()

# Funções de conveniência
def start_health_monitoring(interval: int = 60):
    """Inicia monitoramento de saúde"""
    health_monitor.check_interval = interval
    return asyncio.create_task(health_monitor.start_monitoring())

def stop_health_monitoring():
    """Para monitoramento de saúde"""
    health_monitor.stop_monitoring()

def get_health_status():
    """Retorna status atual de saúde"""
    return health_monitor.get_current_status()

def get_health_report():
    """Retorna relatório de saúde"""
    return health_monitor.generate_health_report()

if __name__ == "__main__":
    # Teste rápido
    print("🧪 Testando monitor de saúde...")
    print(get_health_report())