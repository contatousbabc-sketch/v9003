#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Monitor de Exceções
Sistema de monitoramento e análise de exceções
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from collections import defaultdict, Counter

# Importar sistema de tratamento de exceções
try:
    from enhanced_exception_handler import get_exception_handler, get_exception_stats
    EXCEPTION_HANDLER_AVAILABLE = True
except ImportError:
    EXCEPTION_HANDLER_AVAILABLE = False

# Importar sistema de logging
try:
    from enhanced_logging_system import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class ExceptionMonitor:
    """Monitor de Exceções V2.0 - Análise e relatórios"""
    
    def __init__(self, report_dir: str = "reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
        
        self.exception_handler_available = EXCEPTION_HANDLER_AVAILABLE
        
        if self.exception_handler_available:
            self.exception_handler = get_exception_handler()
        
        logger.info("📊 Monitor de Exceções V2.0 inicializado")
    
    def get_exception_analysis(self) -> Dict[str, Any]:
        """Análise detalhada das exceções"""
        if not self.exception_handler_available:
            return {'error': 'Sistema de tratamento de exceções não disponível'}
        
        # Carregar exceções do arquivo
        exceptions_data = self._load_exceptions_from_file()
        
        if not exceptions_data:
            return {
                'total_exceptions': 0,
                'analysis': 'Nenhuma exceção registrada',
                'recommendations': ['Sistema funcionando sem exceções registradas']
            }
        
        # Análise por categoria
        category_analysis = self._analyze_by_category(exceptions_data)
        
        # Análise por severidade
        severity_analysis = self._analyze_by_severity(exceptions_data)
        
        # Análise temporal
        temporal_analysis = self._analyze_temporal_patterns(exceptions_data)
        
        # Análise de funções mais problemáticas
        function_analysis = self._analyze_problematic_functions(exceptions_data)
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(
            category_analysis, severity_analysis, temporal_analysis, function_analysis
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_exceptions': len(exceptions_data),
            'category_analysis': category_analysis,
            'severity_analysis': severity_analysis,
            'temporal_analysis': temporal_analysis,
            'function_analysis': function_analysis,
            'recommendations': recommendations
        }
    
    def _load_exceptions_from_file(self) -> List[Dict]:
        """Carrega exceções do arquivo JSON"""
        try:
            exception_file = self.exception_handler.exception_log_file
            if exception_file.exists():
                with open(exception_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"❌ Erro ao carregar exceções: {e}")
        
        return []
    
    def _analyze_by_category(self, exceptions_data: List[Dict]) -> Dict[str, Any]:
        """Análise por categoria de exceção"""
        categories = Counter(exc.get('category', 'unknown') for exc in exceptions_data)
        
        total = len(exceptions_data)
        category_percentages = {
            cat: {'count': count, 'percentage': round((count / total) * 100, 2)}
            for cat, count in categories.items()
        }
        
        return {
            'categories': category_percentages,
            'most_common': categories.most_common(5),
            'total_categories': len(categories)
        }
    
    def _analyze_by_severity(self, exceptions_data: List[Dict]) -> Dict[str, Any]:
        """Análise por severidade"""
        severities = Counter(exc.get('severity', 'medium') for exc in exceptions_data)
        
        total = len(exceptions_data)
        severity_percentages = {
            sev: {'count': count, 'percentage': round((count / total) * 100, 2)}
            for sev, count in severities.items()
        }
        
        # Calcular score de risco
        risk_weights = {'critical': 10, 'high': 5, 'medium': 2, 'low': 1}
        risk_score = sum(
            severities.get(sev, 0) * weight 
            for sev, weight in risk_weights.items()
        )
        
        return {
            'severities': severity_percentages,
            'risk_score': risk_score,
            'risk_level': self._calculate_risk_level(risk_score, total)
        }
    
    def _analyze_temporal_patterns(self, exceptions_data: List[Dict]) -> Dict[str, Any]:
        """Análise de padrões temporais"""
        # Agrupar por hora
        hourly_counts = defaultdict(int)
        daily_counts = defaultdict(int)
        
        for exc in exceptions_data:
            try:
                timestamp = datetime.fromisoformat(exc.get('timestamp', ''))
                hour = timestamp.hour
                date = timestamp.date().isoformat()
                
                hourly_counts[hour] += 1
                daily_counts[date] += 1
            except Exception:
                continue
        
        # Encontrar picos
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1]) if hourly_counts else (0, 0)
        peak_day = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else ('', 0)
        
        return {
            'hourly_distribution': dict(hourly_counts),
            'daily_distribution': dict(daily_counts),
            'peak_hour': {'hour': peak_hour[0], 'count': peak_hour[1]},
            'peak_day': {'date': peak_day[0], 'count': peak_day[1]},
            'total_days': len(daily_counts)
        }
    
    def _analyze_problematic_functions(self, exceptions_data: List[Dict]) -> Dict[str, Any]:
        """Análise de funções mais problemáticas"""
        function_counts = Counter(exc.get('function_name', 'unknown') for exc in exceptions_data)
        
        # Agrupar por arquivo
        file_counts = Counter(
            Path(exc.get('file_name', 'unknown')).name 
            for exc in exceptions_data
        )
        
        return {
            'top_functions': function_counts.most_common(10),
            'top_files': file_counts.most_common(10),
            'total_functions': len(function_counts),
            'total_files': len(file_counts)
        }
    
    def _calculate_risk_level(self, risk_score: int, total_exceptions: int) -> str:
        """Calcula nível de risco baseado no score"""
        if total_exceptions == 0:
            return 'none'
        
        avg_risk = risk_score / total_exceptions
        
        if avg_risk >= 7:
            return 'critical'
        elif avg_risk >= 4:
            return 'high'
        elif avg_risk >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, 
                                category_analysis: Dict,
                                severity_analysis: Dict,
                                temporal_analysis: Dict,
                                function_analysis: Dict) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Recomendações baseadas em categoria
        categories = category_analysis['categories']
        if 'api_error' in categories and categories['api_error']['percentage'] > 30:
            recommendations.append("Alto número de erros de API - verificar conectividade e chaves")
        
        if 'network_error' in categories and categories['network_error']['percentage'] > 20:
            recommendations.append("Muitos erros de rede - implementar retry mais agressivo")
        
        if 'rate_limit_error' in categories and categories['rate_limit_error']['percentage'] > 15:
            recommendations.append("Rate limiting frequente - ajustar delays entre requisições")
        
        # Recomendações baseadas em severidade
        severities = severity_analysis['severities']
        if 'critical' in severities and severities['critical']['percentage'] > 5:
            recommendations.append("Exceções críticas detectadas - investigação urgente necessária")
        
        if 'high' in severities and severities['high']['percentage'] > 15:
            recommendations.append("Alto número de exceções de alta severidade - revisar código")
        
        # Recomendações baseadas em padrões temporais
        peak_hour = temporal_analysis['peak_hour']
        if peak_hour['count'] > 10:
            recommendations.append(f"Pico de exceções às {peak_hour['hour']}h - investigar carga do sistema")
        
        # Recomendações baseadas em funções
        top_functions = function_analysis['top_functions']
        if top_functions and top_functions[0][1] > 5:
            func_name = top_functions[0][0]
            count = top_functions[0][1]
            recommendations.append(f"Função '{func_name}' com {count} exceções - revisar implementação")
        
        # Recomendação geral
        if not recommendations:
            recommendations.append("Sistema de exceções funcionando adequadamente")
        
        return recommendations
    
    def generate_report(self, format: str = 'markdown') -> str:
        """Gera relatório de exceções"""
        analysis = self.get_exception_analysis()
        
        if format.lower() == 'json':
            return self._generate_json_report(analysis)
        elif format.lower() == 'markdown':
            return self._generate_markdown_report(analysis)
        else:
            return self._generate_text_report(analysis)
    
    def _generate_json_report(self, analysis: Dict[str, Any]) -> str:
        """Gera relatório em formato JSON"""
        report_file = self.report_dir / f"exception_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório de exceções JSON salvo: {report_file}")
        return str(report_file)
    
    def _generate_markdown_report(self, analysis: Dict[str, Any]) -> str:
        """Gera relatório em formato Markdown"""
        report_file = self.report_dir / f"exception_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        if not self.exception_handler_available:
            content = "# Relatório de Exceções\n\n❌ **Sistema de tratamento de exceções não disponível**\n"
        else:
            content = f"""# Relatório de Exceções - {analysis['timestamp']}

## 📊 Resumo Geral

- **Total de Exceções**: {analysis['total_exceptions']}
- **Nível de Risco**: {analysis.get('severity_analysis', {}).get('risk_level', 'unknown')}
- **Score de Risco**: {analysis.get('severity_analysis', {}).get('risk_score', 0)}

## 📈 Análise por Categoria

"""
            
            if 'category_analysis' in analysis:
                for category, data in analysis['category_analysis']['categories'].items():
                    content += f"- **{category}**: {data['count']} ({data['percentage']}%)\n"
            
            content += "\n## ⚠️ Análise por Severidade\n\n"
            
            if 'severity_analysis' in analysis:
                for severity, data in analysis['severity_analysis']['severities'].items():
                    content += f"- **{severity}**: {data['count']} ({data['percentage']}%)\n"
            
            content += "\n## 🕒 Padrões Temporais\n\n"
            
            if 'temporal_analysis' in analysis:
                temporal = analysis['temporal_analysis']
                content += f"- **Pico de Exceções**: {temporal['peak_hour']['hour']}h ({temporal['peak_hour']['count']} exceções)\n"
                content += f"- **Dia com Mais Exceções**: {temporal['peak_day']['date']} ({temporal['peak_day']['count']} exceções)\n"
                content += f"- **Total de Dias**: {temporal['total_days']}\n"
            
            content += "\n## 🎯 Funções Mais Problemáticas\n\n"
            
            if 'function_analysis' in analysis:
                for func_name, count in analysis['function_analysis']['top_functions'][:5]:
                    content += f"- **{func_name}**: {count} exceções\n"
            
            content += "\n## 💡 Recomendações\n\n"
            
            for i, rec in enumerate(analysis.get('recommendations', []), 1):
                content += f"{i}. {rec}\n"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"📄 Relatório de exceções Markdown salvo: {report_file}")
        return str(report_file)
    
    def _generate_text_report(self, analysis: Dict[str, Any]) -> str:
        """Gera relatório em formato texto"""
        if not self.exception_handler_available:
            return "Sistema de tratamento de exceções não disponível"
        
        report = f"""
=== RELATÓRIO DE EXCEÇÕES ===
Timestamp: {analysis['timestamp']}

RESUMO GERAL:
- Total de Exceções: {analysis['total_exceptions']}
- Nível de Risco: {analysis.get('severity_analysis', {}).get('risk_level', 'unknown')}
- Score de Risco: {analysis.get('severity_analysis', {}).get('risk_score', 0)}

CATEGORIAS PRINCIPAIS:
"""
        
        if 'category_analysis' in analysis:
            for category, data in list(analysis['category_analysis']['categories'].items())[:5]:
                report += f"- {category}: {data['count']} ({data['percentage']}%)\n"
        
        report += "\nSEVERIDADES:\n"
        
        if 'severity_analysis' in analysis:
            for severity, data in analysis['severity_analysis']['severities'].items():
                report += f"- {severity}: {data['count']} ({data['percentage']}%)\n"
        
        report += "\nRECOMENDAÇÕES:\n"
        
        for i, rec in enumerate(analysis.get('recommendations', []), 1):
            report += f"{i}. {rec}\n"
        
        return report
    
    def print_status(self):
        """Imprime status atual das exceções"""
        print(self._generate_text_report(self.get_exception_analysis()))
    
    def save_report(self, format: str = 'markdown') -> str:
        """Salva relatório em arquivo"""
        return self.generate_report(format)

# Instância global do monitor
_exception_monitor_instance = None

def get_exception_monitor() -> ExceptionMonitor:
    """Obtém instância global do monitor"""
    global _exception_monitor_instance
    if _exception_monitor_instance is None:
        _exception_monitor_instance = ExceptionMonitor()
    return _exception_monitor_instance

# Funções de conveniência
def print_exception_status():
    """Imprime status atual das exceções"""
    get_exception_monitor().print_status()

def save_exception_report(format: str = 'markdown') -> str:
    """Salva relatório de exceções"""
    return get_exception_monitor().save_report(format)

def get_exception_analysis() -> Dict[str, Any]:
    """Obtém análise detalhada das exceções"""
    return get_exception_monitor().get_exception_analysis()