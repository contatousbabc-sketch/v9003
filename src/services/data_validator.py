"""
Sistema de Validação de Dados Numéricos
Implementa verificação cruzada e scoring de confiabilidade
"""

import re
import statistics
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime
import json

@dataclass
class NumericalData:
    """Estrutura para dados numéricos com metadados"""
    value: float
    unit: Optional[str] = None
    context: Optional[str] = None
    source_hash: Optional[str] = None
    data_type: str = "absolute"  # absolute, percentage, ratio, currency
    confidence_score: float = 0.5
    validation_status: str = "pending"  # verified, cross_verified, outlier, invalid
    historical_comparison: Optional[Dict] = None
    
@dataclass
class ValidationResult:
    """Resultado da validação de dados"""
    is_valid: bool
    confidence_level: str  # high, medium, low
    issues: List[str]
    recommendations: List[str]
    cross_verification_count: int = 0
    outlier_score: float = 0.0
    benchmark_comparison: Optional[Dict] = None

class DataValidator:
    """Sistema principal de validação de dados"""
    
    def __init__(self):
        self.numerical_data: List[NumericalData] = []
        self.benchmarks: Dict[str, Dict] = {}
        self.historical_data: Dict[str, List[float]] = {}
        self.outlier_threshold = 2.0  # Desvios padrão
        
        # Carrega benchmarks padrão
        self._load_default_benchmarks()
    
    def _load_default_benchmarks(self):
        """Carrega benchmarks padrão da indústria"""
        self.benchmarks = {
            'ecommerce': {
                'conversion_rate': {'min': 1.0, 'max': 5.0, 'average': 2.5, 'unit': '%'},
                'cart_abandonment': {'min': 60.0, 'max': 80.0, 'average': 70.0, 'unit': '%'},
                'customer_acquisition_cost': {'min': 50.0, 'max': 500.0, 'average': 150.0, 'unit': 'BRL'},
                'lifetime_value': {'min': 200.0, 'max': 2000.0, 'average': 600.0, 'unit': 'BRL'}
            },
            'saas': {
                'churn_rate': {'min': 2.0, 'max': 15.0, 'average': 7.0, 'unit': '%'},
                'mrr_growth': {'min': 5.0, 'max': 30.0, 'average': 15.0, 'unit': '%'},
                'customer_acquisition_cost': {'min': 100.0, 'max': 1000.0, 'average': 300.0, 'unit': 'BRL'},
                'ltv_cac_ratio': {'min': 3.0, 'max': 10.0, 'average': 5.0, 'unit': 'ratio'}
            },
            'retail': {
                'gross_margin': {'min': 20.0, 'max': 60.0, 'average': 40.0, 'unit': '%'},
                'inventory_turnover': {'min': 4.0, 'max': 12.0, 'average': 8.0, 'unit': 'times/year'},
                'foot_traffic_conversion': {'min': 15.0, 'max': 40.0, 'average': 25.0, 'unit': '%'}
            },
            'marketing': {
                'cpm': {'min': 5.0, 'max': 50.0, 'average': 20.0, 'unit': 'BRL'},
                'cpc': {'min': 0.50, 'max': 10.0, 'average': 2.0, 'unit': 'BRL'},
                'ctr': {'min': 0.5, 'max': 5.0, 'average': 2.0, 'unit': '%'},
                'roas': {'min': 2.0, 'max': 8.0, 'average': 4.0, 'unit': 'ratio'}
            }
        }
    
    def add_numerical_data(self, value: float, context: str, **kwargs) -> str:
        """Adiciona dados numéricos para validação"""
        data = NumericalData(value=value, context=context, **kwargs)
        self.numerical_data.append(data)
        return f"data_{len(self.numerical_data)}"
    
    def validate_data_point(self, data: NumericalData, industry: str = None) -> ValidationResult:
        """Valida um ponto de dados específico"""
        issues = []
        recommendations = []
        confidence_level = "medium"
        
        # Validação básica
        if data.value < 0 and data.data_type not in ['ratio', 'percentage']:
            issues.append("Valor negativo em contexto onde não é esperado")
        
        # Validação contra benchmarks
        benchmark_comparison = None
        if industry and industry in self.benchmarks:
            benchmark_comparison = self._compare_with_benchmark(data, industry)
            if benchmark_comparison['is_outlier']:
                issues.append(f"Valor fora do range típico da indústria: {benchmark_comparison['message']}")
        
        # Validação de outliers estatísticos
        outlier_score = self._calculate_outlier_score(data)
        if outlier_score > self.outlier_threshold:
            issues.append(f"Possível outlier estatístico (score: {outlier_score:.2f})")
        
        # Validação de consistência
        consistency_issues = self._check_consistency(data)
        issues.extend(consistency_issues)
        
        # Determina nível de confiança
        if len(issues) == 0:
            confidence_level = "high"
        elif len(issues) > 2:
            confidence_level = "low"
        
        # Gera recomendações
        if issues:
            recommendations.append("Verificar fonte dos dados e metodologia de coleta")
            recommendations.append("Buscar validação cruzada com outras fontes")
        
        if benchmark_comparison and benchmark_comparison['is_outlier']:
            recommendations.append("Investigar fatores que podem explicar a discrepância")
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            confidence_level=confidence_level,
            issues=issues,
            recommendations=recommendations,
            outlier_score=outlier_score,
            benchmark_comparison=benchmark_comparison
        )
    
    def _compare_with_benchmark(self, data: NumericalData, industry: str) -> Dict:
        """Compara dados com benchmarks da indústria"""
        if industry not in self.benchmarks:
            return {'is_outlier': False, 'message': 'Benchmark não disponível'}
        
        # Tenta encontrar benchmark relevante baseado no contexto
        context_lower = data.context.lower() if data.context else ""
        relevant_benchmark = None
        
        for metric, benchmark in self.benchmarks[industry].items():
            if any(keyword in context_lower for keyword in metric.split('_')):
                relevant_benchmark = benchmark
                break
        
        if not relevant_benchmark:
            return {'is_outlier': False, 'message': 'Benchmark específico não encontrado'}
        
        # Compara com o benchmark
        min_val = relevant_benchmark['min']
        max_val = relevant_benchmark['max']
        avg_val = relevant_benchmark['average']
        
        is_outlier = data.value < min_val or data.value > max_val
        
        if data.value < min_val:
            message = f"Valor {data.value} abaixo do mínimo típico ({min_val})"
        elif data.value > max_val:
            message = f"Valor {data.value} acima do máximo típico ({max_val})"
        else:
            deviation = abs(data.value - avg_val) / avg_val * 100
            message = f"Valor dentro do range esperado (desvio de {deviation:.1f}% da média)"
        
        return {
            'is_outlier': is_outlier,
            'message': message,
            'benchmark': relevant_benchmark,
            'deviation_from_average': abs(data.value - avg_val) / avg_val
        }
    
    def _calculate_outlier_score(self, data: NumericalData) -> float:
        """Calcula score de outlier baseado em dados históricos"""
        if not data.context or data.context not in self.historical_data:
            return 0.0
        
        historical_values = self.historical_data[data.context]
        if len(historical_values) < 3:
            return 0.0
        
        mean = statistics.mean(historical_values)
        stdev = statistics.stdev(historical_values)
        
        if stdev == 0:
            return 0.0
        
        z_score = abs(data.value - mean) / stdev
        return z_score
    
    def _check_consistency(self, data: NumericalData) -> List[str]:
        """Verifica consistência dos dados"""
        issues = []
        
        # Verifica consistência de unidades
        if data.data_type == "percentage" and (data.value < 0 or data.value > 100):
            issues.append("Percentual fora do range válido (0-100%)")
        
        # Verifica valores extremos por tipo
        if data.data_type == "currency" and data.value > 1000000:
            issues.append("Valor monetário extremamente alto - verificar se está correto")
        
        if data.data_type == "ratio" and data.value > 100:
            issues.append("Ratio muito alto - verificar cálculo")
        
        return issues
    
    def cross_validate_data(self, values: List[float], context: str) -> Dict:
        """Realiza validação cruzada de múltiplos valores"""
        if len(values) < 2:
            return {'status': 'insufficient_data', 'message': 'Dados insuficientes para validação cruzada'}
        
        # Estatísticas básicas
        mean_val = statistics.mean(values)
        median_val = statistics.median(values)
        stdev_val = statistics.stdev(values) if len(values) > 1 else 0
        
        # Identifica outliers
        outliers = []
        if stdev_val > 0:
            for i, value in enumerate(values):
                z_score = abs(value - mean_val) / stdev_val
                if z_score > self.outlier_threshold:
                    outliers.append({'index': i, 'value': value, 'z_score': z_score})
        
        # Calcula coeficiente de variação
        cv = (stdev_val / mean_val) * 100 if mean_val != 0 else 0
        
        # Determina confiabilidade
        if cv < 10:
            reliability = "high"
        elif cv < 25:
            reliability = "medium"
        else:
            reliability = "low"
        
        return {
            'status': 'completed',
            'count': len(values),
            'mean': mean_val,
            'median': median_val,
            'standard_deviation': stdev_val,
            'coefficient_of_variation': cv,
            'reliability': reliability,
            'outliers': outliers,
            'recommended_value': median_val if outliers else mean_val
        }
    
    def generate_validation_report(self, data_list: List[NumericalData], industry: str = None) -> str:
        """Gera relatório de validação em HTML"""
        html = ['<div class="validation-report">']
        html.append('<h3>📊 Relatório de Validação de Dados</h3>')
        
        # Resumo geral
        total_data = len(data_list)
        valid_data = sum(1 for data in data_list if self.validate_data_point(data, industry).is_valid)
        
        html.append(f'<div class="validation-summary">')
        html.append(f'<p><strong>Total de dados analisados:</strong> {total_data}</p>')
        html.append(f'<p><strong>Dados válidos:</strong> {valid_data} ({valid_data/total_data*100:.1f}%)</p>')
        html.append('</div>')
        
        # Detalhes por item
        html.append('<div class="validation-details">')
        for i, data in enumerate(data_list):
            validation = self.validate_data_point(data, industry)
            
            status_class = "valid" if validation.is_valid else "invalid"
            confidence_class = f"confidence-{validation.confidence_level}"
            
            html.append(f'<div class="validation-item {status_class} {confidence_class}">')
            html.append(f'<h4>Dado #{i+1}: {data.context or "Sem contexto"}</h4>')
            html.append(f'<p><strong>Valor:</strong> {data.value} {data.unit or ""}</p>')
            html.append(f'<p><strong>Confiabilidade:</strong> {validation.confidence_level.upper()}</p>')
            
            if validation.issues:
                html.append('<div class="issues">')
                html.append('<strong>⚠️ Problemas identificados:</strong>')
                html.append('<ul>')
                for issue in validation.issues:
                    html.append(f'<li>{issue}</li>')
                html.append('</ul>')
                html.append('</div>')
            
            if validation.recommendations:
                html.append('<div class="recommendations">')
                html.append('<strong>💡 Recomendações:</strong>')
                html.append('<ul>')
                for rec in validation.recommendations:
                    html.append(f'<li>{rec}</li>')
                html.append('</ul>')
                html.append('</div>')
            
            html.append('</div>')
        
        html.append('</div>')
        html.append('</div>')
        
        return '\n'.join(html)
    
    def generate_validation_css(self) -> str:
        """Gera CSS para o relatório de validação"""
        return """
        <style>
        .validation-report {
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #17a2b8;
        }
        
        .validation-summary {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .validation-item {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #6c757d;
        }
        
        .validation-item.valid {
            background-color: #d4edda;
            border-left-color: #28a745;
        }
        
        .validation-item.invalid {
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }
        
        .validation-item.confidence-high {
            box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);
        }
        
        .validation-item.confidence-medium {
            box-shadow: 0 2px 4px rgba(255, 193, 7, 0.2);
        }
        
        .validation-item.confidence-low {
            box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2);
        }
        
        .issues {
            background-color: rgba(220, 53, 69, 0.1);
            padding: 10px;
            border-radius: 3px;
            margin: 10px 0;
        }
        
        .recommendations {
            background-color: rgba(23, 162, 184, 0.1);
            padding: 10px;
            border-radius: 3px;
            margin: 10px 0;
        }
        
        .issues ul, .recommendations ul {
            margin: 5px 0;
            padding-left: 20px;
        }
        </style>
        """
    
    def add_historical_data(self, context: str, values: List[float]):
        """Adiciona dados históricos para comparação"""
        self.historical_data[context] = values
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Retorna resumo da validação"""
        if not self.numerical_data:
            return {}
        
        validations = [self.validate_data_point(data) for data in self.numerical_data]
        
        return {
            'total_data_points': len(self.numerical_data),
            'valid_count': sum(1 for v in validations if v.is_valid),
            'confidence_distribution': {
                'high': sum(1 for v in validations if v.confidence_level == 'high'),
                'medium': sum(1 for v in validations if v.confidence_level == 'medium'),
                'low': sum(1 for v in validations if v.confidence_level == 'low')
            },
            'common_issues': self._get_common_issues(validations)
        }
    
    def _get_common_issues(self, validations: List[ValidationResult]) -> List[str]:
        """Identifica problemas mais comuns"""
        all_issues = []
        for validation in validations:
            all_issues.extend(validation.issues)
        
        # Conta frequência dos problemas
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # Retorna os 5 mais comuns
        return sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]

# Instância global do validador
data_validator = DataValidator()