#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Quality System Fixer
Corrige problemas no sistema de monitoramento de qualidade
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class QualitySystemFixer:
    """Corrige e melhora o sistema de monitoramento de qualidade"""
    
    def __init__(self):
        self.component_stats = defaultdict(lambda: {
            'total_attempts': 0,
            'successful_attempts': 0,
            'failed_attempts': 0,
            'processing_times': deque(maxlen=100),
            'last_reset': datetime.now()
        })
        
    def record_extraction_attempt(self, session_id: str, component: str, success: bool, processing_time: float):
        """Registra tentativa de extração de forma mais inteligente"""
        
        stats = self.component_stats[component]
        
        # Atualiza contadores
        stats['total_attempts'] += 1
        if success:
            stats['successful_attempts'] += 1
        else:
            stats['failed_attempts'] += 1
        
        # Registra tempo de processamento
        stats['processing_times'].append(processing_time)
        
        # Calcula taxa de sucesso atual
        success_rate = stats['successful_attempts'] / stats['total_attempts']
        
        # Log inteligente baseado na tendência
        if stats['total_attempts'] % 10 == 0:  # A cada 10 tentativas
            self._log_component_status(component, success_rate, stats)
        
        # Reset periódico para evitar acúmulo de dados antigos
        if datetime.now() - stats['last_reset'] > timedelta(hours=1):
            self._reset_component_stats(component)
        
        return success_rate
    
    def _log_component_status(self, component: str, success_rate: float, stats: Dict):
        """Log inteligente do status do componente"""
        
        total = stats['total_attempts']
        successful = stats['successful_attempts']
        failed = stats['failed_attempts']
        
        avg_time = statistics.mean(stats['processing_times']) if stats['processing_times'] else 0
        
        if success_rate >= 0.8:
            logger.info(f"✅ {component}: {success_rate:.1%} sucesso ({successful}/{total}) - Tempo médio: {avg_time:.2f}s")
        elif success_rate >= 0.5:
            logger.warning(f"⚠️ {component}: {success_rate:.1%} sucesso ({successful}/{total}) - Precisa melhorar")
        else:
            logger.error(f"❌ {component}: {success_rate:.1%} sucesso ({successful}/{total}) - CRÍTICO!")
    
    def _reset_component_stats(self, component: str):
        """Reset periódico das estatísticas para manter dados frescos"""
        
        stats = self.component_stats[component]
        
        # Salva estatísticas antes do reset
        if stats['total_attempts'] > 0:
            final_rate = stats['successful_attempts'] / stats['total_attempts']
            logger.info(f"📊 {component} - Reset estatísticas: Taxa final {final_rate:.1%} ({stats['total_attempts']} tentativas)")
        
        # Reset mantendo uma base pequena para continuidade
        keep_successful = max(1, stats['successful_attempts'] // 10)
        keep_failed = max(1, stats['failed_attempts'] // 10)
        
        stats.update({
            'total_attempts': keep_successful + keep_failed,
            'successful_attempts': keep_successful,
            'failed_attempts': keep_failed,
            'last_reset': datetime.now()
        })
    
    def get_component_health(self, component: str) -> Dict[str, Any]:
        """Retorna saúde atual do componente"""
        
        stats = self.component_stats[component]
        
        if stats['total_attempts'] == 0:
            return {
                'component': component,
                'success_rate': 0.0,
                'status': 'no_data',
                'total_attempts': 0,
                'avg_processing_time': 0.0,
                'recommendation': 'Aguardando dados'
            }
        
        success_rate = stats['successful_attempts'] / stats['total_attempts']
        avg_time = statistics.mean(stats['processing_times']) if stats['processing_times'] else 0
        
        # Determina status
        if success_rate >= 0.9:
            status = 'excellent'
        elif success_rate >= 0.7:
            status = 'good'
        elif success_rate >= 0.5:
            status = 'acceptable'
        elif success_rate >= 0.3:
            status = 'poor'
        else:
            status = 'critical'
        
        # Gera recomendação
        recommendations = []
        if success_rate < 0.5:
            recommendations.append("Taxa de sucesso crítica - investigar causas")
        if avg_time > 10:
            recommendations.append("Tempo de processamento alto - otimizar")
        if stats['total_attempts'] < 10:
            recommendations.append("Poucos dados - aguardar mais amostras")
        
        return {
            'component': component,
            'success_rate': success_rate,
            'status': status,
            'total_attempts': stats['total_attempts'],
            'successful_attempts': stats['successful_attempts'],
            'failed_attempts': stats['failed_attempts'],
            'avg_processing_time': avg_time,
            'recommendations': recommendations or ['Sistema funcionando adequadamente']
        }
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Retorna visão geral do sistema"""
        
        components_health = {}
        all_rates = []
        
        for component in self.component_stats:
            health = self.get_component_health(component)
            components_health[component] = health
            if health['total_attempts'] > 0:
                all_rates.append(health['success_rate'])
        
        overall_rate = statistics.mean(all_rates) if all_rates else 0.0
        
        # Status geral
        if overall_rate >= 0.8:
            overall_status = 'healthy'
        elif overall_rate >= 0.6:
            overall_status = 'warning'
        else:
            overall_status = 'critical'
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_success_rate': overall_rate,
            'overall_status': overall_status,
            'total_components': len(self.component_stats),
            'active_components': len([c for c in components_health.values() if c['total_attempts'] > 0]),
            'components': components_health,
            'system_recommendations': self._generate_system_recommendations(components_health)
        }
    
    def _generate_system_recommendations(self, components_health: Dict) -> List[str]:
        """Gera recomendações para o sistema"""
        
        recommendations = []
        
        critical_components = [
            name for name, health in components_health.items()
            if health['status'] == 'critical'
        ]
        
        if critical_components:
            recommendations.append(f"🚨 Componentes críticos: {', '.join(critical_components)}")
        
        poor_components = [
            name for name, health in components_health.items()
            if health['status'] in ['poor', 'critical']
        ]
        
        if len(poor_components) > len(components_health) / 2:
            recommendations.append("⚠️ Mais de 50% dos componentes com problemas - revisão geral necessária")
        
        slow_components = [
            name for name, health in components_health.items()
            if health['avg_processing_time'] > 10
        ]
        
        if slow_components:
            recommendations.append(f"🐌 Componentes lentos: {', '.join(slow_components)}")
        
        if not recommendations:
            recommendations.append("✅ Sistema funcionando adequadamente")
        
        return recommendations

# Instância global
quality_fixer = QualitySystemFixer()

def record_smart_extraction_quality(session_id: str, component: str, success: bool, processing_time: float):
    """Versão melhorada do registro de qualidade de extração"""
    return quality_fixer.record_extraction_attempt(session_id, component, success, processing_time)

def get_smart_component_health(component: str) -> Dict[str, Any]:
    """Versão melhorada da saúde do componente"""
    return quality_fixer.get_component_health(component)

def get_smart_system_overview() -> Dict[str, Any]:
    """Versão melhorada da visão geral do sistema"""
    return quality_fixer.get_system_overview()