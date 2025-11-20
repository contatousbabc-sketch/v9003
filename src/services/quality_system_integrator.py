"""
Sistema Integrador de Qualidade
Combina todos os componentes do sistema de qualidade em uma interface unificada
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Importa todos os sistemas de qualidade
from .source_tracker import source_tracker, SourceMetadata, CitationData
from .data_validator import data_validator, NumericalData, ValidationResult
from .scenario_analyzer import scenario_analyzer, ScenarioParameters, ScenarioAnalysis
from .disclaimer_manager import disclaimer_manager, DisclaimerContext
from .risk_analyzer import risk_analyzer, RiskMatrix
from .regulatory_context import regulatory_context_manager, RegulatoryContext
from .information_qualifier import information_qualifier, QualifiedInformation, QualificationSummary
from .validation_recommendations import validation_recommendation_system, ValidationPlan

@dataclass
class QualityReport:
    """Relatório completo de qualidade"""
    session_id: str
    content_analyzed: str
    industry: str
    generation_date: str
    
    # Componentes do sistema de qualidade
    source_summary: Dict[str, Any]
    validation_summary: Dict[str, Any]
    scenario_analysis: Optional[ScenarioAnalysis]
    disclaimer_ids: List[str]
    risk_analysis: Optional[RiskMatrix]
    regulatory_context: Optional[RegulatoryContext]
    qualification_summary: Optional[QualificationSummary]
    validation_plan: Optional[ValidationPlan]
    
    # Métricas gerais
    overall_quality_score: float
    credibility_level: str
    recommendations: List[str]
    critical_issues: List[str]

class QualitySystemIntegrator:
    """Sistema principal que integra todos os componentes de qualidade"""
    
    def __init__(self):
        self.quality_thresholds = {
            'excellent': 0.85,
            'good': 0.70,
            'fair': 0.55,
            'poor': 0.40
        }
        
    def analyze_content_quality(self, content: str, industry: str = 'general', 
                              session_id: str = None, context: Dict = None) -> QualityReport:
        """Análise completa de qualidade do conteúdo"""
        
        if not session_id:
            session_id = f"quality_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 1. Análise de fontes e citações
        print("🔍 Analisando fontes e citações...")
        source_summary = source_tracker.get_sources_summary()
        
        # 2. Validação de dados numéricos
        print("📊 Validando dados numéricos...")
        validation_summary = data_validator.get_validation_summary()
        
        # 3. Análise de cenários (se aplicável)
        print("📈 Gerando análise de cenários...")
        scenario_analysis = None
        if self._has_numerical_projections(content):
            try:
                # Extrai valor base para análise de cenários
                base_value = self._extract_base_value(content)
                if base_value:
                    scenario_analysis = scenario_analyzer.generate_scenarios(
                        base_value=base_value,
                        context="market_analysis",
                        industry=industry
                    )
            except Exception as e:
                print(f"Erro na análise de cenários: {e}")
        
        # 4. Análise de disclaimers
        print("⚠️ Analisando disclaimers necessários...")
        disclaimer_context = disclaimer_manager.create_context_from_content(content, industry)
        disclaimer_ids = disclaimer_manager.analyze_content(content, disclaimer_context)
        
        # 5. Análise de riscos
        print("⚠️ Analisando riscos...")
        risk_analysis = None
        try:
            risk_analysis = risk_analyzer.analyze_risks(content, industry)
        except Exception as e:
            print(f"Erro na análise de riscos: {e}")
        
        # 6. Contexto regulatório
        print("📋 Analisando contexto regulatório...")
        regulatory_context = None
        try:
            regulatory_context = regulatory_context_manager.analyze_regulatory_context(content, industry)
        except Exception as e:
            print(f"Erro na análise regulatória: {e}")
        
        # 7. Qualificação de informações
        print("🏷️ Qualificando informações...")
        qualification_summary = None
        try:
            # Simula itens de conteúdo para qualificação
            content_items = self._extract_content_items(content)
            qualified_items = information_qualifier.qualify_content_batch(content_items)
            qualification_summary = information_qualifier.generate_qualification_summary(qualified_items)
        except Exception as e:
            print(f"Erro na qualificação: {e}")
        
        # 8. Plano de validação
        print("✅ Gerando plano de validação...")
        validation_plan = None
        try:
            validation_plan = validation_recommendation_system.generate_validation_plan(
                content=content,
                industry=industry,
                context="general_analysis"
            )
        except Exception as e:
            print(f"Erro no plano de validação: {e}")
        
        # 9. Calcula métricas gerais
        print("📊 Calculando métricas de qualidade...")
        overall_quality_score = self._calculate_overall_quality_score(
            source_summary, validation_summary, disclaimer_ids, 
            risk_analysis, regulatory_context, qualification_summary
        )
        
        credibility_level = self._determine_credibility_level(overall_quality_score)
        
        # 10. Gera recomendações e identifica problemas críticos
        recommendations = self._generate_integrated_recommendations(
            source_summary, validation_summary, disclaimer_ids,
            risk_analysis, regulatory_context, qualification_summary
        )
        
        critical_issues = self._identify_critical_issues(
            disclaimer_ids, risk_analysis, regulatory_context, qualification_summary
        )
        
        return QualityReport(
            session_id=session_id,
            content_analyzed=content[:500] + "..." if len(content) > 500 else content,
            industry=industry,
            generation_date=datetime.now().isoformat(),
            source_summary=source_summary,
            validation_summary=validation_summary,
            scenario_analysis=scenario_analysis,
            disclaimer_ids=disclaimer_ids,
            risk_analysis=risk_analysis,
            regulatory_context=regulatory_context,
            qualification_summary=qualification_summary,
            validation_plan=validation_plan,
            overall_quality_score=overall_quality_score,
            credibility_level=credibility_level,
            recommendations=recommendations,
            critical_issues=critical_issues
        )
    
    def _has_numerical_projections(self, content: str) -> bool:
        """Verifica se o conteúdo tem projeções numéricas"""
        projection_keywords = ['projeção', 'estimativa', 'previsão', 'expectativa', 'cenário']
        numerical_patterns = [r'\d+%', r'R\$\s*\d+', r'\d+\.\d+']
        
        content_lower = content.lower()
        has_keywords = any(keyword in content_lower for keyword in projection_keywords)
        
        import re
        has_numbers = any(re.search(pattern, content) for pattern in numerical_patterns)
        
        return has_keywords and has_numbers
    
    def _extract_base_value(self, content: str) -> Optional[float]:
        """Extrai valor base para análise de cenários"""
        import re
        
        # Procura por valores monetários
        money_pattern = r'R\$\s*(\d+(?:\.\d{3})*(?:,\d{2})?)'
        money_matches = re.findall(money_pattern, content)
        
        if money_matches:
            # Converte primeiro valor encontrado
            value_str = money_matches[0].replace('.', '').replace(',', '.')
            try:
                return float(value_str)
            except:
                pass
        
        # Procura por percentuais
        percent_pattern = r'(\d+(?:,\d+)?)\s*%'
        percent_matches = re.findall(percent_pattern, content)
        
        if percent_matches:
            try:
                value_str = percent_matches[0].replace(',', '.')
                return float(value_str)
            except:
                pass
        
        # Valor padrão se não encontrar nada
        return 100000.0  # R$ 100.000 como base
    
    def _extract_content_items(self, content: str) -> List[Dict]:
        """Extrai itens de conteúdo para qualificação"""
        # Divide o conteúdo em sentenças
        sentences = content.split('.')
        items = []
        
        for i, sentence in enumerate(sentences[:10]):  # Máximo 10 sentenças
            if len(sentence.strip()) > 20:  # Ignora sentenças muito curtas
                items.append({
                    'content': sentence.strip(),
                    'source_url': f'https://example.com/source_{i}',
                    'publication_date': datetime.now().isoformat(),
                    'source_reliability': 0.6
                })
        
        return items
    
    def _calculate_overall_quality_score(self, source_summary: Dict, validation_summary: Dict,
                                       disclaimer_ids: List[str], risk_analysis: Optional[RiskMatrix],
                                       regulatory_context: Optional[RegulatoryContext],
                                       qualification_summary: Optional[QualificationSummary]) -> float:
        """Calcula score geral de qualidade"""
        scores = []
        weights = []
        
        # Score de fontes (peso 20%)
        if source_summary and source_summary.get('total_sources', 0) > 0:
            source_score = source_summary.get('average_reliability', 0.5)
            scores.append(source_score)
            weights.append(0.20)
        
        # Score de validação de dados (peso 15%)
        if validation_summary and validation_summary.get('total_data_points', 0) > 0:
            valid_ratio = validation_summary.get('valid_count', 0) / validation_summary.get('total_data_points', 1)
            scores.append(valid_ratio)
            weights.append(0.15)
        
        # Score de disclaimers (peso 10% - inverso, menos disclaimers = melhor)
        disclaimer_score = max(0.0, 1.0 - (len(disclaimer_ids) * 0.1))
        scores.append(disclaimer_score)
        weights.append(0.10)
        
        # Score de riscos (peso 20%)
        if risk_analysis:
            risk_score = max(0.0, 1.0 - risk_analysis.overall_risk_score)
            scores.append(risk_score)
            weights.append(0.20)
        
        # Score regulatório (peso 15%)
        if regulatory_context:
            reg_score = regulatory_context.compliance_score
            scores.append(reg_score)
            weights.append(0.15)
        
        # Score de qualificação (peso 20%)
        if qualification_summary:
            qual_score = qualification_summary.overall_quality_score
            scores.append(qual_score)
            weights.append(0.20)
        
        # Calcula média ponderada
        if scores and weights:
            total_weight = sum(weights)
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            return weighted_sum / total_weight
        
        return 0.5  # Score neutro se não há dados
    
    def _determine_credibility_level(self, score: float) -> str:
        """Determina nível de credibilidade baseado no score"""
        if score >= self.quality_thresholds['excellent']:
            return 'EXCELENTE'
        elif score >= self.quality_thresholds['good']:
            return 'BOM'
        elif score >= self.quality_thresholds['fair']:
            return 'REGULAR'
        else:
            return 'INADEQUADO'
    
    def _generate_integrated_recommendations(self, source_summary: Dict, validation_summary: Dict,
                                           disclaimer_ids: List[str], risk_analysis: Optional[RiskMatrix],
                                           regulatory_context: Optional[RegulatoryContext],
                                           qualification_summary: Optional[QualificationSummary]) -> List[str]:
        """Gera recomendações integradas"""
        recommendations = []
        
        # Recomendações de fontes
        if source_summary and source_summary.get('total_sources', 0) < 3:
            recommendations.append("🔍 Adicionar mais fontes para aumentar credibilidade (mínimo 3 fontes)")
        
        if source_summary and source_summary.get('average_reliability', 0) < 0.7:
            recommendations.append("📚 Buscar fontes mais confiáveis (governamentais, acadêmicas)")
        
        # Recomendações de validação
        if validation_summary and validation_summary.get('total_data_points', 0) > 0:
            valid_ratio = validation_summary.get('valid_count', 0) / validation_summary.get('total_data_points', 1)
            if valid_ratio < 0.8:
                recommendations.append("📊 Validar dados numéricos com fontes adicionais")
        
        # Recomendações de disclaimers
        critical_disclaimers = [d for d in disclaimer_ids if 'critical' in d or 'financial' in d or 'health' in d]
        if critical_disclaimers:
            recommendations.append("⚠️ Revisar disclaimers críticos - consulta profissional necessária")
        
        # Recomendações de riscos
        if risk_analysis and risk_analysis.overall_risk_score > 0.6:
            recommendations.append("🚨 Implementar estratégias de mitigação para riscos identificados")
        
        # Recomendações regulatórias
        if regulatory_context and regulatory_context.compliance_score < 0.7:
            recommendations.append("📋 Revisar conformidade regulatória - possíveis gaps identificados")
        
        # Recomendações de qualificação
        if qualification_summary and qualification_summary.overall_quality_score < 0.6:
            recommendations.append("🏷️ Melhorar qualidade das informações - muitos dados não verificados")
        
        # Recomendações gerais
        recommendations.extend([
            "✅ Implementar processo sistemático de validação",
            "📝 Documentar todas as fontes e metodologias utilizadas",
            "🔄 Estabelecer revisão periódica das informações",
            "👥 Consultar especialistas para validação final"
        ])
        
        return recommendations[:10]  # Máximo 10 recomendações
    
    def _identify_critical_issues(self, disclaimer_ids: List[str], risk_analysis: Optional[RiskMatrix],
                                regulatory_context: Optional[RegulatoryContext],
                                qualification_summary: Optional[QualificationSummary]) -> List[str]:
        """Identifica problemas críticos"""
        critical_issues = []
        
        # Issues de disclaimers
        critical_disclaimer_types = ['financial_projections', 'investment_advice', 'health_claims', 'legal_advice']
        if any(d_id in critical_disclaimer_types for d_id in disclaimer_ids):
            critical_issues.append("🚨 CRÍTICO: Conteúdo requer disclaimers obrigatórios - risco legal")
        
        # Issues de riscos
        if risk_analysis:
            critical_risks = [r for r in risk_analysis.risks if r.severity_level == 'critical']
            if critical_risks:
                critical_issues.append(f"⚠️ CRÍTICO: {len(critical_risks)} riscos críticos identificados")
        
        # Issues regulatórias
        if regulatory_context:
            critical_alerts = [a for a in regulatory_context.compliance_alerts if a.priority == 'critical']
            if critical_alerts:
                critical_issues.append("📋 CRÍTICO: Alertas críticos de compliance identificados")
        
        # Issues de qualificação
        if qualification_summary:
            low_confidence_pct = (qualification_summary.confidence_distribution.get('low', 0) / 
                                 max(qualification_summary.total_items, 1)) * 100
            if low_confidence_pct > 50:
                critical_issues.append("🔍 CRÍTICO: Mais de 50% das informações têm baixa confiança")
        
        return critical_issues
    
    def generate_integrated_html_report(self, quality_report: QualityReport) -> str:
        """Gera relatório HTML integrado"""
        html = ['<div class="quality-system-report">']
        html.append('<h2>📋 Relatório Completo de Qualidade</h2>')
        
        # Cabeçalho do relatório
        html.append('<div class="report-header">')
        html.append(f'<p><strong>Sessão:</strong> {quality_report.session_id}</p>')
        html.append(f'<p><strong>Indústria:</strong> {quality_report.industry.replace("_", " ").title()}</p>')
        html.append(f'<p><strong>Data de Geração:</strong> {datetime.fromisoformat(quality_report.generation_date).strftime("%d/%m/%Y %H:%M")}</p>')
        html.append('</div>')
        
        # Score geral de qualidade
        credibility_class = f"credibility-{quality_report.credibility_level.lower()}"
        html.append(f'<div class="overall-quality {credibility_class}">')
        html.append('<h3>🎯 Avaliação Geral de Qualidade</h3>')
        html.append(f'<div class="quality-score">{quality_report.overall_quality_score:.2f}</div>')
        html.append(f'<div class="credibility-level">{quality_report.credibility_level}</div>')
        html.append('</div>')
        
        # Problemas críticos
        if quality_report.critical_issues:
            html.append('<div class="critical-issues">')
            html.append('<h3>🚨 Problemas Críticos</h3>')
            html.append('<ul class="critical-list">')
            for issue in quality_report.critical_issues:
                html.append(f'<li>{issue}</li>')
            html.append('</ul>')
            html.append('</div>')
        
        # Seções dos componentes
        components = [
            ('Fontes e Citações', source_tracker.generate_footnotes_html()),
            ('Validação de Dados', self._generate_validation_section(quality_report.validation_summary)),
            ('Análise de Cenários', scenario_analyzer.generate_scenarios_html(quality_report.scenario_analysis) if quality_report.scenario_analysis else ''),
            ('Disclaimers', disclaimer_manager.generate_disclaimer_section(quality_report.disclaimer_ids)),
            ('Análise de Riscos', risk_analyzer.generate_risk_matrix_html(quality_report.risk_analysis) if quality_report.risk_analysis else ''),
            ('Contexto Regulatório', regulatory_context_manager.generate_regulatory_html(quality_report.regulatory_context) if quality_report.regulatory_context else ''),
            ('Qualificação de Informações', self._generate_qualification_section(quality_report.qualification_summary)),
            ('Plano de Validação', validation_recommendation_system.generate_validation_html(quality_report.validation_plan) if quality_report.validation_plan else '')
        ]
        
        for title, content in components:
            if content:
                html.append(f'<div class="component-section">')
                html.append(f'<h3>{title}</h3>')
                html.append(content)
                html.append('</div>')
        
        # Recomendações finais
        html.append('<div class="final-recommendations">')
        html.append('<h3>💡 Recomendações Finais</h3>')
        html.append('<ul class="recommendations-list">')
        for recommendation in quality_report.recommendations:
            html.append(f'<li>{recommendation}</li>')
        html.append('</ul>')
        html.append('</div>')
        
        html.append('</div>')
        
        # Adiciona CSS de todos os componentes
        css_components = [
            source_tracker.generate_sources_css(),
            data_validator.generate_validation_css(),
            scenario_analyzer.generate_scenarios_css(),
            disclaimer_manager.generate_disclaimers_css(),
            risk_analyzer.generate_risk_css(),
            regulatory_context_manager.generate_regulatory_css(),
            information_qualifier.generate_qualification_css(),
            validation_recommendation_system.generate_validation_css(),
            self._generate_integrated_css()
        ]
        
        html.append('\n'.join(css_components))
        
        return '\n'.join(html)
    
    def _generate_validation_section(self, validation_summary: Dict) -> str:
        """Gera seção de validação"""
        if not validation_summary:
            return '<p>Nenhum dado numérico para validação encontrado.</p>'
        
        html = ['<div class="validation-summary">']
        html.append(f'<p><strong>Total de dados analisados:</strong> {validation_summary.get("total_data_points", 0)}</p>')
        html.append(f'<p><strong>Dados válidos:</strong> {validation_summary.get("valid_count", 0)}</p>')
        
        confidence_dist = validation_summary.get('confidence_distribution', {})
        html.append('<div class="confidence-breakdown">')
        for level, count in confidence_dist.items():
            html.append(f'<span class="confidence-badge {level}">{level.upper()}: {count}</span>')
        html.append('</div>')
        
        html.append('</div>')
        return '\n'.join(html)
    
    def _generate_qualification_section(self, qualification_summary: Optional[QualificationSummary]) -> str:
        """Gera seção de qualificação"""
        if not qualification_summary:
            return '<p>Qualificação de informações não disponível.</p>'
        
        html = ['<div class="qualification-summary">']
        html.append(f'<p><strong>Total de informações:</strong> {qualification_summary.total_items}</p>')
        html.append(f'<p><strong>Score de qualidade:</strong> {qualification_summary.overall_quality_score:.2f}</p>')
        
        # Top tags
        if qualification_summary.tag_distribution:
            html.append('<div class="top-tags">')
            html.append('<strong>Tags principais:</strong>')
            sorted_tags = sorted(qualification_summary.tag_distribution.items(), key=lambda x: x[1], reverse=True)
            for tag, count in sorted_tags[:5]:
                html.append(f'<span class="tag-badge">{tag} ({count})</span>')
            html.append('</div>')
        
        html.append('</div>')
        return '\n'.join(html)
    
    def _generate_integrated_css(self) -> str:
        """Gera CSS específico do sistema integrado"""
        return """
        <style>
        .quality-system-report {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .report-header {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border-left: 4px solid #007bff;
        }
        
        .overall-quality {
            text-align: center;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .credibility-excelente {
            background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
            border: 3px solid #38a169;
        }
        
        .credibility-bom {
            background: linear-gradient(135deg, #fefcbf 0%, #f6e05e 100%);
            border: 3px solid #d69e2e;
        }
        
        .credibility-regular {
            background: linear-gradient(135deg, #feebc8 0%, #fbd38d 100%);
            border: 3px solid #dd6b20;
        }
        
        .credibility-inadequado {
            background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
            border: 3px solid #e53e3e;
        }
        
        .quality-score {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .credibility-level {
            font-size: 1.5em;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .critical-issues {
            background-color: #fed7d7;
            border: 2px solid #e53e3e;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }
        
        .critical-list {
            margin: 15px 0;
            padding-left: 20px;
        }
        
        .critical-list li {
            margin-bottom: 10px;
            font-weight: 500;
            color: #742a2a;
        }
        
        .component-section {
            margin-bottom: 40px;
            padding: 25px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .component-section h3 {
            color: #2d3748;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        .final-recommendations {
            background: linear-gradient(135deg, #e6fffa 0%, #b2f5ea 100%);
            border-left: 4px solid #319795;
            border-radius: 8px;
            padding: 25px;
            margin-top: 30px;
        }
        
        .recommendations-list {
            margin: 15px 0;
            padding-left: 20px;
        }
        
        .recommendations-list li {
            margin-bottom: 10px;
            line-height: 1.6;
        }
        
        .confidence-badge {
            display: inline-block;
            padding: 4px 8px;
            margin: 2px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }
        
        .confidence-badge.high {
            background-color: #c6f6d5;
            color: #22543d;
        }
        
        .confidence-badge.medium {
            background-color: #fefcbf;
            color: #744210;
        }
        
        .confidence-badge.low {
            background-color: #fed7d7;
            color: #742a2a;
        }
        
        .tag-badge {
            display: inline-block;
            padding: 4px 8px;
            margin: 2px;
            background-color: #edf2f7;
            border-radius: 12px;
            font-size: 0.8em;
            color: #4a5568;
        }
        
        .validation-summary, .qualification-summary {
            background-color: #f7fafc;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        
        .confidence-breakdown, .top-tags {
            margin-top: 10px;
        }
        </style>
        """
    
    def export_quality_report_json(self, quality_report: QualityReport) -> str:
        """Exporta relatório completo em JSON"""
        # Converte objetos complexos para dicionários
        report_dict = asdict(quality_report)
        
        # Adiciona metadados do sistema
        report_dict['system_metadata'] = {
            'version': '1.0.0',
            'components_used': [
                'source_tracker',
                'data_validator', 
                'scenario_analyzer',
                'disclaimer_manager',
                'risk_analyzer',
                'regulatory_context_manager',
                'information_qualifier',
                'validation_recommendation_system'
            ],
            'export_date': datetime.now().isoformat()
        }
        
        return json.dumps(report_dict, indent=2, ensure_ascii=False)

# Instância global do sistema integrador
quality_system = QualitySystemIntegrator()