#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ NOVO: Sistema Avançado de Monitoramento de Qualidade
Monitora qualidade, performance e confiabilidade do sistema ARQ-ALPHA-V11
"""

import os
import sys
import time
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class QualityMetricType(Enum):
    """Tipos de métricas de qualidade"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    CONFIDENCE = "confidence"
    PROCESSING_TIME = "processing_time"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    AVAILABILITY = "availability"
    RELIABILITY = "reliability"

class QualityLevel(Enum):
    """Níveis de qualidade"""
    EXCELLENT = "excellent"    # 90-100%
    GOOD = "good"             # 75-89%
    ACCEPTABLE = "acceptable"  # 60-74%
    POOR = "poor"             # 40-59%
    CRITICAL = "critical"     # 0-39%

@dataclass
class QualityMetric:
    """Métrica individual de qualidade"""
    metric_type: QualityMetricType
    value: float
    timestamp: datetime
    component: str
    session_id: str
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class QualityReport:
    """Relatório de qualidade"""
    session_id: str
    component: str
    timestamp: datetime
    overall_score: float
    quality_level: QualityLevel
    metrics: Dict[str, float]
    recommendations: List[str]
    issues_found: List[str]
    performance_data: Dict[str, Any]

class QualityThresholds:
    """Limites de qualidade para diferentes métricas"""
    
    THRESHOLDS = {
        QualityMetricType.ACCURACY: {
            QualityLevel.EXCELLENT: 0.95,
            QualityLevel.GOOD: 0.85,
            QualityLevel.ACCEPTABLE: 0.75,
            QualityLevel.POOR: 0.60
        },
        QualityMetricType.SUCCESS_RATE: {
            QualityLevel.EXCELLENT: 0.98,
            QualityLevel.GOOD: 0.90,
            QualityLevel.ACCEPTABLE: 0.80,
            QualityLevel.POOR: 0.70
        },
        QualityMetricType.ERROR_RATE: {
            QualityLevel.EXCELLENT: 0.02,
            QualityLevel.GOOD: 0.05,
            QualityLevel.ACCEPTABLE: 0.10,
            QualityLevel.POOR: 0.20
        },
        QualityMetricType.PROCESSING_TIME: {  # em segundos
            QualityLevel.EXCELLENT: 1.0,
            QualityLevel.GOOD: 3.0,
            QualityLevel.ACCEPTABLE: 5.0,
            QualityLevel.POOR: 10.0
        },
        QualityMetricType.CONFIDENCE: {
            QualityLevel.EXCELLENT: 0.90,
            QualityLevel.GOOD: 0.80,
            QualityLevel.ACCEPTABLE: 0.70,
            QualityLevel.POOR: 0.60
        }
    }
    
    @classmethod
    def get_quality_level(cls, metric_type: QualityMetricType, value: float) -> QualityLevel:
        """Determina nível de qualidade baseado no valor da métrica"""
        
        thresholds = cls.THRESHOLDS.get(metric_type, {})
        
        if not thresholds:
            # Padrão genérico para métricas não definidas
            if value >= 0.90:
                return QualityLevel.EXCELLENT
            elif value >= 0.75:
                return QualityLevel.GOOD
            elif value >= 0.60:
                return QualityLevel.ACCEPTABLE
            elif value >= 0.40:
                return QualityLevel.POOR
            else:
                return QualityLevel.CRITICAL
        
        # Para métricas onde menor é melhor (como error_rate, processing_time)
        if metric_type in [QualityMetricType.ERROR_RATE, QualityMetricType.PROCESSING_TIME]:
            if value <= thresholds[QualityLevel.EXCELLENT]:
                return QualityLevel.EXCELLENT
            elif value <= thresholds[QualityLevel.GOOD]:
                return QualityLevel.GOOD
            elif value <= thresholds[QualityLevel.ACCEPTABLE]:
                return QualityLevel.ACCEPTABLE
            elif value <= thresholds[QualityLevel.POOR]:
                return QualityLevel.POOR
            else:
                return QualityLevel.CRITICAL
        
        # Para métricas onde maior é melhor
        else:
            if value >= thresholds[QualityLevel.EXCELLENT]:
                return QualityLevel.EXCELLENT
            elif value >= thresholds[QualityLevel.GOOD]:
                return QualityLevel.GOOD
            elif value >= thresholds[QualityLevel.ACCEPTABLE]:
                return QualityLevel.ACCEPTABLE
            elif value >= thresholds[QualityLevel.POOR]:
                return QualityLevel.POOR
            else:
                return QualityLevel.CRITICAL

class QualityMonitoringSystem:
    """✅ NOVO: Sistema avançado de monitoramento de qualidade"""
    
    def __init__(self, max_metrics_history: int = 10000):
        self.metrics_history: List[QualityMetric] = []
        self.max_metrics_history = max_metrics_history
        self.component_metrics: Dict[str, List[QualityMetric]] = defaultdict(list)
        self.session_metrics: Dict[str, List[QualityMetric]] = defaultdict(list)
        self.real_time_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Configurações de monitoramento
        self.monitoring_active = True
        self.alert_thresholds = {
            QualityLevel.CRITICAL: True,
            QualityLevel.POOR: True,
            QualityLevel.ACCEPTABLE: False
        }
        
        # Thread para processamento assíncrono
        self.processing_thread = None
        self.processing_queue = deque()
        self.processing_lock = threading.Lock()
        
        self._start_background_processing()
        
        logger.info("✅ QualityMonitoringSystem inicializado")
    
    def _start_background_processing(self):
        """Inicia processamento em background"""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.processing_thread = threading.Thread(
                target=self._background_processor,
                daemon=True
            )
            self.processing_thread.start()
    
    def _background_processor(self):
        """Processador em background para métricas"""
        while self.monitoring_active:
            try:
                with self.processing_lock:
                    if self.processing_queue:
                        metric = self.processing_queue.popleft()
                        self._process_metric_background(metric)
                
                time.sleep(0.1)  # Pequena pausa para não sobrecarregar
                
            except Exception as e:
                logger.error(f"Erro no processamento em background: {e}")
    
    def _process_metric_background(self, metric: QualityMetric):
        """Processa métrica em background"""
        try:
            # Adiciona aos históricos
            self.metrics_history.append(metric)
            self.component_metrics[metric.component].append(metric)
            self.session_metrics[metric.session_id].append(metric)
            
            # Adiciona às métricas em tempo real
            self.real_time_metrics[f"{metric.component}_{metric.metric_type.value}"].append({
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat()
            })
            
            # Mantém tamanho do histórico
            if len(self.metrics_history) > self.max_metrics_history:
                self.metrics_history = self.metrics_history[-self.max_metrics_history:]
            
            # Verifica alertas
            self._check_quality_alerts(metric)
            
        except Exception as e:
            logger.error(f"Erro no processamento da métrica: {e}")
    
    def record_metric(self, 
                     metric_type: QualityMetricType,
                     value: float,
                     component: str,
                     session_id: str,
                     context: Dict[str, Any] = None):
        """
        ✅ PRINCIPAL: Registra uma métrica de qualidade
        
        Args:
            metric_type: Tipo da métrica
            value: Valor da métrica
            component: Componente que gerou a métrica
            session_id: ID da sessão
            context: Contexto adicional
        """
        
        if not self.monitoring_active:
            return
        
        metric = QualityMetric(
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            component=component,
            session_id=session_id,
            context=context or {}
        )
        
        # Adiciona à fila de processamento
        with self.processing_lock:
            self.processing_queue.append(metric)
        
        # Log da métrica
        quality_level = QualityThresholds.get_quality_level(metric_type, value)
        logger.debug(f"📊 Métrica registrada: {component} - {metric_type.value}={value:.3f} ({quality_level.value})")
    
    def _check_quality_alerts(self, metric: QualityMetric):
        """Verifica se a métrica requer alerta"""
        quality_level = QualityThresholds.get_quality_level(metric.metric_type, metric.value)
        
        if self.alert_thresholds.get(quality_level, False):
            self._trigger_quality_alert(metric, quality_level)
    
    def _trigger_quality_alert(self, metric: QualityMetric, quality_level: QualityLevel):
        """Dispara alerta de qualidade"""
        alert_message = (
            f"🚨 ALERTA DE QUALIDADE: {metric.component} - "
            f"{metric.metric_type.value}={metric.value:.3f} ({quality_level.value})"
        )
        
        logger.warning(alert_message)
        
        # Aqui poderia integrar com sistema de notificações
        # Por exemplo: enviar email, Slack, etc.
    
    def get_component_quality_report(self, component: str, hours_back: int = 24) -> QualityReport:
        """
        ✅ NOVO: Gera relatório de qualidade para um componente
        
        Args:
            component: Nome do componente
            hours_back: Horas para trás para análise
            
        Returns:
            QualityReport com análise completa
        """
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Filtra métricas do componente no período
        component_metrics = [
            m for m in self.component_metrics[component]
            if m.timestamp >= cutoff_time
        ]
        
        if not component_metrics:
            return QualityReport(
                session_id="N/A",
                component=component,
                timestamp=datetime.now(),
                overall_score=0.0,
                quality_level=QualityLevel.CRITICAL,
                metrics={},
                recommendations=["Nenhuma métrica disponível para análise"],
                issues_found=["Sem dados suficientes"],
                performance_data={}
            )
        
        # Calcula métricas agregadas
        metrics_by_type = defaultdict(list)
        for metric in component_metrics:
            metrics_by_type[metric.metric_type].append(metric.value)
        
        # Calcula estatísticas
        aggregated_metrics = {}
        quality_scores = []
        
        for metric_type, values in metrics_by_type.items():
            avg_value = statistics.mean(values)
            aggregated_metrics[metric_type.value] = {
                'average': avg_value,
                'min': min(values),
                'max': max(values),
                'count': len(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
            }
            
            # Converte para score de qualidade (0-100)
            quality_level = QualityThresholds.get_quality_level(metric_type, avg_value)
            quality_score = self._quality_level_to_score(quality_level)
            quality_scores.append(quality_score)
        
        # Score geral
        overall_score = statistics.mean(quality_scores) if quality_scores else 0.0
        overall_quality_level = self._score_to_quality_level(overall_score)
        
        # Gera recomendações e identifica problemas
        recommendations = self._generate_recommendations(component, aggregated_metrics, overall_quality_level)
        issues_found = self._identify_issues(component, aggregated_metrics, overall_quality_level)
        
        # Dados de performance
        performance_data = self._calculate_performance_data(component_metrics)
        
        return QualityReport(
            session_id=component_metrics[-1].session_id if component_metrics else "N/A",
            component=component,
            timestamp=datetime.now(),
            overall_score=overall_score,
            quality_level=overall_quality_level,
            metrics=aggregated_metrics,
            recommendations=recommendations,
            issues_found=issues_found,
            performance_data=performance_data
        )
    
    def get_session_quality_summary(self, session_id: str) -> Dict[str, Any]:
        """
        ✅ NOVO: Gera resumo de qualidade para uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Dict com resumo de qualidade da sessão
        """
        
        session_metrics = self.session_metrics.get(session_id, [])
        
        if not session_metrics:
            return {
                'session_id': session_id,
                'total_metrics': 0,
                'components': [],
                'overall_quality': 'unknown',
                'summary': 'Nenhuma métrica encontrada para esta sessão'
            }
        
        # Agrupa por componente
        components_data = defaultdict(list)
        for metric in session_metrics:
            components_data[metric.component].append(metric)
        
        # Calcula qualidade por componente
        component_qualities = {}
        all_scores = []
        
        for component, metrics in components_data.items():
            # Calcula score médio do componente
            scores = []
            for metric in metrics:
                quality_level = QualityThresholds.get_quality_level(metric.metric_type, metric.value)
                score = self._quality_level_to_score(quality_level)
                scores.append(score)
            
            avg_score = statistics.mean(scores) if scores else 0.0
            component_qualities[component] = {
                'score': avg_score,
                'quality_level': self._score_to_quality_level(avg_score).value,
                'metrics_count': len(metrics)
            }
            all_scores.append(avg_score)
        
        # Score geral da sessão
        overall_score = statistics.mean(all_scores) if all_scores else 0.0
        overall_quality = self._score_to_quality_level(overall_score)
        
        return {
            'session_id': session_id,
            'total_metrics': len(session_metrics),
            'components': list(components_data.keys()),
            'component_qualities': component_qualities,
            'overall_score': overall_score,
            'overall_quality': overall_quality.value,
            'duration': self._calculate_session_duration(session_metrics),
            'summary': f"Sessão com {len(session_metrics)} métricas em {len(components_data)} componentes"
        }
    
    def get_system_health_dashboard(self) -> Dict[str, Any]:
        """
        ✅ NOVO: Gera dashboard de saúde do sistema
        
        Returns:
            Dict com dados completos do dashboard
        """
        
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
        # Métricas da última hora
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= last_hour]
        daily_metrics = [m for m in self.metrics_history if m.timestamp >= last_24h]
        
        # Componentes ativos
        active_components = set(m.component for m in recent_metrics)
        
        # Calcula saúde por componente
        component_health = {}
        for component in active_components:
            component_metrics = [m for m in recent_metrics if m.component == component]
            
            if component_metrics:
                scores = []
                for metric in component_metrics:
                    quality_level = QualityThresholds.get_quality_level(metric.metric_type, metric.value)
                    score = self._quality_level_to_score(quality_level)
                    scores.append(score)
                
                avg_score = statistics.mean(scores)
                component_health[component] = {
                    'score': avg_score,
                    'status': self._score_to_quality_level(avg_score).value,
                    'metrics_count': len(component_metrics),
                    'last_update': max(m.timestamp for m in component_metrics).isoformat()
                }
        
        # Estatísticas gerais
        total_metrics_24h = len(daily_metrics)
        total_metrics_1h = len(recent_metrics)
        
        # Tendências
        trends = self._calculate_trends(daily_metrics)
        
        # Alertas ativos
        active_alerts = self._get_active_alerts()
        
        return {
            'timestamp': now.isoformat(),
            'system_status': self._determine_system_status(component_health),
            'active_components': len(active_components),
            'component_health': component_health,
            'metrics_summary': {
                'last_hour': total_metrics_1h,
                'last_24h': total_metrics_24h,
                'total_stored': len(self.metrics_history)
            },
            'trends': trends,
            'active_alerts': active_alerts,
            'recommendations': self._generate_system_recommendations(component_health, trends)
        }
    
    def _quality_level_to_score(self, quality_level: QualityLevel) -> float:
        """Converte nível de qualidade para score numérico"""
        score_map = {
            QualityLevel.EXCELLENT: 95.0,
            QualityLevel.GOOD: 82.0,
            QualityLevel.ACCEPTABLE: 67.0,
            QualityLevel.POOR: 50.0,
            QualityLevel.CRITICAL: 25.0
        }
        return score_map.get(quality_level, 0.0)
    
    def _score_to_quality_level(self, score: float) -> QualityLevel:
        """Converte score numérico para nível de qualidade"""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 75:
            return QualityLevel.GOOD
        elif score >= 60:
            return QualityLevel.ACCEPTABLE
        elif score >= 40:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL
    
    def _generate_recommendations(self, component: str, metrics: Dict[str, Any], quality_level: QualityLevel) -> List[str]:
        """Gera recomendações baseadas nas métricas"""
        recommendations = []
        
        if quality_level == QualityLevel.CRITICAL:
            recommendations.append(f"🚨 CRÍTICO: {component} requer atenção imediata")
            recommendations.append("Verificar logs de erro e investigar falhas")
        
        elif quality_level == QualityLevel.POOR:
            recommendations.append(f"⚠️ {component} apresenta problemas de qualidade")
            recommendations.append("Revisar configurações e otimizar performance")
        
        # Recomendações específicas por métrica
        for metric_name, data in metrics.items():
            avg_value = data['average']
            
            if metric_name == 'processing_time' and avg_value > 5.0:
                recommendations.append("🐌 Tempo de processamento alto - considerar otimizações")
            
            elif metric_name == 'error_rate' and avg_value > 0.1:
                recommendations.append("❌ Taxa de erro elevada - investigar causas")
            
            elif metric_name == 'confidence' and avg_value < 0.7:
                recommendations.append("🤔 Baixa confiança nas análises - revisar modelos")
        
        if not recommendations:
            recommendations.append("✅ Sistema operando dentro dos parâmetros esperados")
        
        return recommendations
    
    def _identify_issues(self, component: str, metrics: Dict[str, Any], quality_level: QualityLevel) -> List[str]:
        """Identifica problemas específicos"""
        issues = []
        
        for metric_name, data in metrics.items():
            avg_value = data['average']
            std_dev = data['std_dev']
            
            # Variabilidade alta
            if std_dev > avg_value * 0.5:
                issues.append(f"Alta variabilidade em {metric_name}")
            
            # Valores extremos
            if metric_name == 'error_rate' and avg_value > 0.2:
                issues.append("Taxa de erro crítica")
            
            elif metric_name == 'processing_time' and avg_value > 10.0:
                issues.append("Tempo de processamento excessivo")
            
            elif metric_name == 'success_rate' and avg_value < 0.8:
                issues.append("Taxa de sucesso baixa")
        
        return issues
    
    def _calculate_performance_data(self, metrics: List[QualityMetric]) -> Dict[str, Any]:
        """Calcula dados de performance"""
        if not metrics:
            return {}
        
        # Métricas de tempo
        processing_times = [m.value for m in metrics if m.metric_type == QualityMetricType.PROCESSING_TIME]
        
        # Throughput (métricas por minuto)
        duration = (max(m.timestamp for m in metrics) - min(m.timestamp for m in metrics)).total_seconds() / 60
        throughput = len(metrics) / duration if duration > 0 else 0
        
        return {
            'total_operations': len(metrics),
            'avg_processing_time': statistics.mean(processing_times) if processing_times else 0,
            'throughput_per_minute': throughput,
            'time_span_minutes': duration
        }
    
    def _calculate_session_duration(self, metrics: List[QualityMetric]) -> float:
        """Calcula duração da sessão em minutos"""
        if len(metrics) < 2:
            return 0.0
        
        start_time = min(m.timestamp for m in metrics)
        end_time = max(m.timestamp for m in metrics)
        
        return (end_time - start_time).total_seconds() / 60
    
    def _calculate_trends(self, metrics: List[QualityMetric]) -> Dict[str, str]:
        """Calcula tendências das métricas"""
        if len(metrics) < 10:
            return {'overall': 'insufficient_data'}
        
        # Divide em duas metades para comparar
        mid_point = len(metrics) // 2
        first_half = metrics[:mid_point]
        second_half = metrics[mid_point:]
        
        # Calcula scores médios
        first_scores = []
        second_scores = []
        
        for metric in first_half:
            quality_level = QualityThresholds.get_quality_level(metric.metric_type, metric.value)
            first_scores.append(self._quality_level_to_score(quality_level))
        
        for metric in second_half:
            quality_level = QualityThresholds.get_quality_level(metric.metric_type, metric.value)
            second_scores.append(self._quality_level_to_score(quality_level))
        
        first_avg = statistics.mean(first_scores)
        second_avg = statistics.mean(second_scores)
        
        diff = second_avg - first_avg
        
        if diff > 5:
            trend = 'improving'
        elif diff < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'overall': trend,
            'change_percentage': (diff / first_avg) * 100 if first_avg > 0 else 0
        }
    
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Retorna alertas ativos"""
        # Por simplicidade, retorna alertas baseados nas métricas recentes
        recent_time = datetime.now() - timedelta(minutes=30)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= recent_time]
        
        alerts = []
        for metric in recent_metrics:
            quality_level = QualityThresholds.get_quality_level(metric.metric_type, metric.value)
            
            if quality_level in [QualityLevel.CRITICAL, QualityLevel.POOR]:
                alerts.append({
                    'component': metric.component,
                    'metric_type': metric.metric_type.value,
                    'value': metric.value,
                    'severity': quality_level.value,
                    'timestamp': metric.timestamp.isoformat()
                })
        
        return alerts[-10:]  # Últimos 10 alertas
    
    def _determine_system_status(self, component_health: Dict[str, Any]) -> str:
        """Determina status geral do sistema"""
        if not component_health:
            return 'unknown'
        
        scores = [health['score'] for health in component_health.values()]
        avg_score = statistics.mean(scores)
        
        if avg_score >= 90:
            return 'excellent'
        elif avg_score >= 75:
            return 'good'
        elif avg_score >= 60:
            return 'acceptable'
        elif avg_score >= 40:
            return 'poor'
        else:
            return 'critical'
    
    def _generate_system_recommendations(self, component_health: Dict[str, Any], trends: Dict[str, str]) -> List[str]:
        """Gera recomendações para o sistema"""
        recommendations = []
        
        # Baseado no trend
        if trends.get('overall') == 'declining':
            recommendations.append("📉 Tendência de declínio detectada - investigar causas")
        elif trends.get('overall') == 'improving':
            recommendations.append("📈 Sistema melhorando - manter práticas atuais")
        
        # Baseado na saúde dos componentes
        poor_components = [comp for comp, health in component_health.items() 
                          if health['score'] < 60]
        
        if poor_components:
            recommendations.append(f"⚠️ Componentes com problemas: {', '.join(poor_components)}")
        
        if not recommendations:
            recommendations.append("✅ Sistema operando adequadamente")
        
        return recommendations
    
    def export_quality_data(self, filepath: str, hours_back: int = 24) -> bool:
        """
        ✅ NOVO: Exporta dados de qualidade para arquivo
        
        Args:
            filepath: Caminho do arquivo para exportar
            hours_back: Horas para trás para incluir
            
        Returns:
            bool: True se exportação foi bem-sucedida
        """
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            # Filtra métricas do período
            export_metrics = [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'component': m.component,
                    'session_id': m.session_id,
                    'metric_type': m.metric_type.value,
                    'value': m.value,
                    'context': m.context
                }
                for m in self.metrics_history
                if m.timestamp >= cutoff_time
            ]
            
            # Dados para exportação
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'period_hours': hours_back,
                'total_metrics': len(export_metrics),
                'metrics': export_metrics,
                'summary': self.get_system_health_dashboard()
            }
            
            # Salva arquivo
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 Dados de qualidade exportados: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na exportação: {e}")
            return False
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring_active = False
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=10)
        
        logger.info("🛑 Monitoramento de qualidade parado")


# ✅ INSTÂNCIA GLOBAL
quality_monitor = QualityMonitoringSystem()


# ✅ FUNÇÕES DE CONVENIÊNCIA PARA INTEGRAÇÃO

def record_llm_quality(session_id: str, component: str, accuracy: float, confidence: float, processing_time: float):
    """Registra métricas de qualidade do LLM"""
    quality_monitor.record_metric(QualityMetricType.ACCURACY, accuracy, component, session_id)
    quality_monitor.record_metric(QualityMetricType.CONFIDENCE, confidence, component, session_id)
    quality_monitor.record_metric(QualityMetricType.PROCESSING_TIME, processing_time, component, session_id)

def record_api_quality(session_id: str, component: str, success_rate: float, error_rate: float, latency: float):
    """Registra métricas de qualidade da API"""
    quality_monitor.record_metric(QualityMetricType.SUCCESS_RATE, success_rate, component, session_id)
    quality_monitor.record_metric(QualityMetricType.ERROR_RATE, error_rate, component, session_id)
    quality_monitor.record_metric(QualityMetricType.LATENCY, latency, component, session_id)

def record_extraction_quality(session_id: str, component: str, success_rate: float, processing_time: float):
    """Registra métricas de qualidade da extração"""
    quality_monitor.record_metric(QualityMetricType.SUCCESS_RATE, success_rate, component, session_id)
    quality_monitor.record_metric(QualityMetricType.PROCESSING_TIME, processing_time, component, session_id)

def get_component_health(component: str) -> Dict[str, Any]:
    """Retorna saúde de um componente específico"""
    report = quality_monitor.get_component_quality_report(component)
    return asdict(report)

def get_system_dashboard() -> Dict[str, Any]:
    """Retorna dashboard do sistema"""
    return quality_monitor.get_system_health_dashboard()


# ✅ EXEMPLO DE USO
if __name__ == "__main__":
    import random
    import time
    
    print("🧪 Testando Sistema de Monitoramento de Qualidade...")
    
    # Simula algumas métricas
    session_id = "test_session_quality"
    
    for i in range(20):
        # Simula métricas variadas
        accuracy = random.uniform(0.7, 0.98)
        confidence = random.uniform(0.6, 0.95)
        processing_time = random.uniform(0.5, 8.0)
        
        record_llm_quality(session_id, "LLM_SERVICE", accuracy, confidence, processing_time)
        
        success_rate = random.uniform(0.8, 1.0)
        error_rate = random.uniform(0.0, 0.15)
        latency = random.uniform(0.1, 2.0)
        
        record_api_quality(session_id, "API_SERVICE", success_rate, error_rate, latency)
        
        time.sleep(0.1)  # Pequena pausa
    
    # Gera relatórios
    print("\n📊 RELATÓRIO DE QUALIDADE LLM_SERVICE:")
    llm_report = quality_monitor.get_component_quality_report("LLM_SERVICE")
    print(f"Score geral: {llm_report.overall_score:.1f}")
    print(f"Nível de qualidade: {llm_report.quality_level.value}")
    print(f"Recomendações: {llm_report.recommendations}")
    
    print("\n📊 DASHBOARD DO SISTEMA:")
    dashboard = quality_monitor.get_system_health_dashboard()
    print(f"Status do sistema: {dashboard['system_status']}")
    print(f"Componentes ativos: {dashboard['active_components']}")
    print(f"Métricas na última hora: {dashboard['metrics_summary']['last_hour']}")
    
    print("\n📄 Exportando dados...")
    quality_monitor.export_quality_data("quality_export_test.json", hours_back=1)
    
    print("✅ Teste concluído!")
    
    # Para o monitoramento
    quality_monitor.stop_monitoring()