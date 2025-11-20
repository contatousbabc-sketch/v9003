#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Cache Monitor
Sistema de monitoramento e relatórios do cache
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# Importar sistema de cache
try:
    from intelligent_cache_system import get_cache, cache_stats
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

# Importar sistema de logging
try:
    from enhanced_logging_system import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class CacheMonitor:
    """Monitor de performance e status do cache"""
    
    def __init__(self, report_dir: str = "reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
        
        self.cache_available = CACHE_AVAILABLE
        
        if self.cache_available:
            self.cache = get_cache()
        
        logger.info("📊 Cache Monitor inicializado")
    
    def get_detailed_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas detalhadas do cache"""
        if not self.cache_available:
            return {'error': 'Cache não disponível'}
        
        stats = cache_stats()
        
        # Adicionar informações extras
        detailed_stats = {
            'timestamp': datetime.now().isoformat(),
            'cache_status': 'active' if self.cache_available else 'inactive',
            'basic_stats': stats,
            'performance_metrics': self._calculate_performance_metrics(stats),
            'recommendations': self._generate_recommendations(stats)
        }
        
        return detailed_stats
    
    def _calculate_performance_metrics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas de performance"""
        metrics = {}
        
        # Taxa de hit
        if stats['total_requests'] > 0:
            metrics['hit_rate_percentage'] = round(stats['hit_rate'] * 100, 2)
            metrics['miss_rate_percentage'] = round((1 - stats['hit_rate']) * 100, 2)
        else:
            metrics['hit_rate_percentage'] = 0
            metrics['miss_rate_percentage'] = 0
        
        # Eficiência de memória
        memory_mb = stats['memory_size_mb']
        if memory_mb > 0:
            entries_per_mb = stats['memory_entries'] / memory_mb
            metrics['memory_efficiency'] = round(entries_per_mb, 2)
        else:
            metrics['memory_efficiency'] = 0
        
        # Status geral
        if stats['hit_rate'] >= 0.7:
            metrics['performance_status'] = 'excellent'
        elif stats['hit_rate'] >= 0.5:
            metrics['performance_status'] = 'good'
        elif stats['hit_rate'] >= 0.3:
            metrics['performance_status'] = 'fair'
        else:
            metrics['performance_status'] = 'poor'
        
        return metrics
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nas estatísticas"""
        recommendations = []
        
        # Recomendações baseadas na taxa de hit
        if stats['hit_rate'] < 0.3:
            recommendations.append("Taxa de hit baixa - considere aumentar TTL para dados estáveis")
        
        if stats['evictions'] > stats['hits']:
            recommendations.append("Muitas evicções - considere aumentar limite de memória")
        
        if stats['memory_size_mb'] > 80:  # 80MB de 100MB
            recommendations.append("Uso de memória alto - considere limpeza ou aumento de limite")
        
        if stats['disk_entries'] > stats['memory_entries'] * 2:
            recommendations.append("Muitos dados em disco - considere otimizar padrões de acesso")
        
        if stats['total_requests'] > 1000 and stats['hit_rate'] > 0.8:
            recommendations.append("Excelente performance de cache - sistema otimizado")
        
        if not recommendations:
            recommendations.append("Sistema de cache funcionando adequadamente")
        
        return recommendations
    
    def generate_report(self, format: str = 'json') -> str:
        """Gera relatório do cache"""
        stats = self.get_detailed_stats()
        
        if format.lower() == 'json':
            return self._generate_json_report(stats)
        elif format.lower() == 'markdown':
            return self._generate_markdown_report(stats)
        else:
            return self._generate_text_report(stats)
    
    def _generate_json_report(self, stats: Dict[str, Any]) -> str:
        """Gera relatório em formato JSON"""
        report_file = self.report_dir / f"cache_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório JSON salvo: {report_file}")
        return str(report_file)
    
    def _generate_markdown_report(self, stats: Dict[str, Any]) -> str:
        """Gera relatório em formato Markdown"""
        report_file = self.report_dir / f"cache_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        if not self.cache_available:
            content = "# Relatório de Cache\n\n❌ **Sistema de cache não disponível**\n"
        else:
            basic = stats['basic_stats']
            metrics = stats['performance_metrics']
            
            content = f"""# Relatório de Cache - {stats['timestamp']}

## 📊 Estatísticas Básicas

- **Status**: {stats['cache_status']}
- **Entradas em Memória**: {basic['memory_entries']}
- **Entradas em Disco**: {basic['disk_entries']}
- **Uso de Memória**: {basic['memory_size_mb']:.2f} MB
- **Total de Requisições**: {basic['total_requests']}

## 🎯 Performance

- **Taxa de Hit**: {metrics['hit_rate_percentage']}%
- **Taxa de Miss**: {metrics['miss_rate_percentage']}%
- **Eficiência de Memória**: {metrics['memory_efficiency']} entradas/MB
- **Status de Performance**: {metrics['performance_status']}

## 📈 Métricas Detalhadas

- **Hits**: {basic['hits']}
- **Misses**: {basic['misses']}
- **Evicções**: {basic['evictions']}

## 💡 Recomendações

"""
            for i, rec in enumerate(stats['recommendations'], 1):
                content += f"{i}. {rec}\n"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"📄 Relatório Markdown salvo: {report_file}")
        return str(report_file)
    
    def _generate_text_report(self, stats: Dict[str, Any]) -> str:
        """Gera relatório em formato texto"""
        if not self.cache_available:
            return "Sistema de cache não disponível"
        
        basic = stats['basic_stats']
        metrics = stats['performance_metrics']
        
        report = f"""
=== RELATÓRIO DE CACHE ===
Timestamp: {stats['timestamp']}

ESTATÍSTICAS BÁSICAS:
- Status: {stats['cache_status']}
- Entradas em Memória: {basic['memory_entries']}
- Entradas em Disco: {basic['disk_entries']}
- Uso de Memória: {basic['memory_size_mb']:.2f} MB
- Total de Requisições: {basic['total_requests']}

PERFORMANCE:
- Taxa de Hit: {metrics['hit_rate_percentage']}%
- Taxa de Miss: {metrics['miss_rate_percentage']}%
- Status: {metrics['performance_status']}

MÉTRICAS:
- Hits: {basic['hits']}
- Misses: {basic['misses']}
- Evicções: {basic['evictions']}

RECOMENDAÇÕES:
"""
        for i, rec in enumerate(stats['recommendations'], 1):
            report += f"{i}. {rec}\n"
        
        return report
    
    def save_report(self, format: str = 'markdown') -> str:
        """Salva relatório em arquivo"""
        return self.generate_report(format)
    
    def print_status(self):
        """Imprime status atual do cache"""
        print(self._generate_text_report(self.get_detailed_stats()))
    
    def cleanup_old_reports(self, days: int = 7):
        """Remove relatórios antigos"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        removed_count = 0
        for report_file in self.report_dir.glob("cache_report_*"):
            if report_file.stat().st_mtime < cutoff_date.timestamp():
                report_file.unlink()
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"🧹 Removidos {removed_count} relatórios antigos")
        
        return removed_count

# Instância global do monitor
_monitor_instance = None

def get_cache_monitor() -> CacheMonitor:
    """Obtém instância global do monitor"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = CacheMonitor()
    return _monitor_instance

# Funções de conveniência
def print_cache_status():
    """Imprime status atual do cache"""
    get_cache_monitor().print_status()

def save_cache_report(format: str = 'markdown') -> str:
    """Salva relatório de cache"""
    return get_cache_monitor().save_report(format)

def get_cache_stats_detailed() -> Dict[str, Any]:
    """Obtém estatísticas detalhadas"""
    return get_cache_monitor().get_detailed_stats()