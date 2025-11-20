"""
Sistema de Análise de Cenários Múltiplos
Implementa geração automática de cenários otimista/realista/pessimista
"""

import json
import statistics
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np

@dataclass
class ScenarioParameters:
    """Parâmetros para geração de cenários"""
    base_value: float
    optimistic_multiplier: float = 1.3
    pessimistic_multiplier: float = 0.7
    volatility: float = 0.15  # Desvio padrão como % do valor base
    confidence_interval: float = 0.95
    time_horizon: int = 12  # meses
    growth_rate: Optional[float] = None
    seasonal_factor: Optional[float] = None

@dataclass
class Scenario:
    """Estrutura de um cenário específico"""
    name: str
    type: str  # optimistic, realistic, pessimistic
    probability: float
    values: List[float]
    key_assumptions: List[str]
    risk_factors: List[str]
    confidence_level: str
    
@dataclass
class ScenarioAnalysis:
    """Análise completa de cenários"""
    scenarios: List[Scenario]
    sensitivity_analysis: Dict[str, Any]
    recommendations: List[str]
    key_variables: List[str]
    monte_carlo_results: Optional[Dict] = None

class ScenarioAnalyzer:
    """Sistema principal de análise de cenários"""
    
    def __init__(self):
        self.scenarios: List[Scenario] = []
        self.risk_factors_db = self._load_risk_factors()
        self.industry_multipliers = self._load_industry_multipliers()
        
    def _load_risk_factors(self) -> Dict[str, List[str]]:
        """Carrega base de fatores de risco por categoria"""
        return {
            'market': [
                'Mudanças na demanda do mercado',
                'Entrada de novos concorrentes',
                'Alterações no comportamento do consumidor',
                'Flutuações econômicas',
                'Mudanças tecnológicas disruptivas'
            ],
            'financial': [
                'Variações na taxa de juros',
                'Inflação acima do esperado',
                'Dificuldades de acesso ao crédito',
                'Flutuações cambiais',
                'Problemas de fluxo de caixa'
            ],
            'operational': [
                'Problemas na cadeia de suprimentos',
                'Dificuldades de contratação',
                'Falhas em sistemas críticos',
                'Problemas de qualidade',
                'Capacidade operacional limitada'
            ],
            'regulatory': [
                'Mudanças na legislação',
                'Novas regulamentações setoriais',
                'Alterações tributárias',
                'Questões de compliance',
                'Licenças e autorizações'
            ],
            'external': [
                'Eventos climáticos extremos',
                'Instabilidade política',
                'Crises sanitárias',
                'Conflitos geopolíticos',
                'Mudanças demográficas'
            ]
        }
    
    def _load_industry_multipliers(self) -> Dict[str, Dict]:
        """Carrega multiplicadores específicos por indústria"""
        return {
            'technology': {
                'optimistic': 1.5,
                'pessimistic': 0.6,
                'volatility': 0.25
            },
            'retail': {
                'optimistic': 1.2,
                'pessimistic': 0.8,
                'volatility': 0.12
            },
            'manufacturing': {
                'optimistic': 1.15,
                'pessimistic': 0.85,
                'volatility': 0.10
            },
            'services': {
                'optimistic': 1.25,
                'pessimistic': 0.75,
                'volatility': 0.15
            },
            'healthcare': {
                'optimistic': 1.1,
                'pessimistic': 0.9,
                'volatility': 0.08
            }
        }
    
    def generate_scenarios(self, 
                         base_value: float, 
                         context: str,
                         industry: str = 'services',
                         time_horizon: int = 12,
                         **kwargs) -> ScenarioAnalysis:
        """Gera análise completa de cenários"""
        
        # Ajusta parâmetros baseado na indústria
        industry_params = self.industry_multipliers.get(industry, self.industry_multipliers['services'])
        
        params = ScenarioParameters(
            base_value=base_value,
            optimistic_multiplier=industry_params['optimistic'],
            pessimistic_multiplier=industry_params['pessimistic'],
            volatility=industry_params['volatility'],
            time_horizon=time_horizon,
            **kwargs
        )
        
        # Gera os três cenários principais
        scenarios = [
            self._generate_optimistic_scenario(params, context, industry),
            self._generate_realistic_scenario(params, context, industry),
            self._generate_pessimistic_scenario(params, context, industry)
        ]
        
        # Análise de sensibilidade
        sensitivity = self._perform_sensitivity_analysis(params, context)
        
        # Recomendações baseadas nos cenários
        recommendations = self._generate_recommendations(scenarios, sensitivity)
        
        # Variáveis-chave identificadas
        key_variables = self._identify_key_variables(context, industry)
        
        return ScenarioAnalysis(
            scenarios=scenarios,
            sensitivity_analysis=sensitivity,
            recommendations=recommendations,
            key_variables=key_variables
        )
    
    def _generate_optimistic_scenario(self, params: ScenarioParameters, context: str, industry: str) -> Scenario:
        """Gera cenário otimista"""
        values = []
        current_value = params.base_value
        
        # Crescimento acelerado nos primeiros meses
        monthly_growth = 0.05  # 5% ao mês
        
        for month in range(params.time_horizon):
            # Aplica crescimento com variação
            growth_factor = 1 + monthly_growth * (1 + np.random.normal(0, 0.1))
            current_value *= growth_factor
            
            # Aplica multiplicador otimista
            if month == params.time_horizon - 1:
                current_value *= params.optimistic_multiplier
            
            values.append(round(current_value, 2))
        
        assumptions = [
            "Crescimento acelerado da demanda",
            "Execução perfeita da estratégia",
            "Condições de mercado favoráveis",
            "Ausência de grandes obstáculos",
            "Adoção rápida pelos clientes"
        ]
        
        risk_factors = self.risk_factors_db['external'][:2]  # Fatores externos mínimos
        
        return Scenario(
            name="Cenário Otimista",
            type="optimistic",
            probability=0.20,
            values=values,
            key_assumptions=assumptions,
            risk_factors=risk_factors,
            confidence_level="medium"
        )
    
    def _generate_realistic_scenario(self, params: ScenarioParameters, context: str, industry: str) -> Scenario:
        """Gera cenário realista"""
        values = []
        current_value = params.base_value
        
        # Crescimento moderado e consistente
        monthly_growth = 0.02  # 2% ao mês
        
        for month in range(params.time_horizon):
            # Aplica crescimento com variação normal
            growth_factor = 1 + monthly_growth * (1 + np.random.normal(0, params.volatility))
            current_value *= growth_factor
            
            # Adiciona sazonalidade se especificada
            if params.seasonal_factor:
                seasonal_adjustment = 1 + params.seasonal_factor * np.sin(2 * np.pi * month / 12)
                current_value *= seasonal_adjustment
            
            values.append(round(current_value, 2))
        
        assumptions = [
            "Crescimento moderado e sustentável",
            "Execução adequada da estratégia",
            "Condições de mercado normais",
            "Alguns desafios operacionais esperados",
            "Adoção gradual pelos clientes"
        ]
        
        risk_factors = (self.risk_factors_db['market'][:2] + 
                       self.risk_factors_db['operational'][:2])
        
        return Scenario(
            name="Cenário Realista",
            type="realistic",
            probability=0.60,
            values=values,
            key_assumptions=assumptions,
            risk_factors=risk_factors,
            confidence_level="high"
        )
    
    def _generate_pessimistic_scenario(self, params: ScenarioParameters, context: str, industry: str) -> Scenario:
        """Gera cenário pessimista"""
        values = []
        current_value = params.base_value
        
        # Crescimento lento ou declínio
        monthly_growth = -0.01  # -1% ao mês
        
        for month in range(params.time_horizon):
            # Aplica crescimento negativo com alta variação
            growth_factor = 1 + monthly_growth * (1 + np.random.normal(0, params.volatility * 2))
            current_value *= growth_factor
            
            # Aplica multiplicador pessimista
            if month == params.time_horizon - 1:
                current_value *= params.pessimistic_multiplier
            
            values.append(round(max(current_value, 0), 2))  # Não permite valores negativos
        
        assumptions = [
            "Dificuldades significativas no mercado",
            "Execução com obstáculos importantes",
            "Condições econômicas desfavoráveis",
            "Resistência à mudança pelos clientes",
            "Competição acirrada"
        ]
        
        risk_factors = (self.risk_factors_db['market'] + 
                       self.risk_factors_db['financial'][:2] +
                       self.risk_factors_db['regulatory'][:2])
        
        return Scenario(
            name="Cenário Pessimista",
            type="pessimistic",
            probability=0.20,
            values=values,
            key_assumptions=assumptions,
            risk_factors=risk_factors,
            confidence_level="medium"
        )
    
    def _perform_sensitivity_analysis(self, params: ScenarioParameters, context: str) -> Dict[str, Any]:
        """Realiza análise de sensibilidade"""
        
        # Variáveis para análise de sensibilidade
        variables = {
            'growth_rate': {'base': 0.02, 'range': [-0.01, 0.05]},
            'market_size': {'base': 1.0, 'range': [0.7, 1.5]},
            'competition': {'base': 1.0, 'range': [0.8, 1.3]},
            'costs': {'base': 1.0, 'range': [0.9, 1.2]}
        }
        
        sensitivity_results = {}
        
        for var_name, var_data in variables.items():
            base_result = params.base_value
            
            # Testa valores mínimo e máximo
            min_result = base_result * var_data['range'][0]
            max_result = base_result * var_data['range'][1]
            
            # Calcula impacto percentual
            min_impact = (min_result - base_result) / base_result * 100
            max_impact = (max_result - base_result) / base_result * 100
            
            sensitivity_results[var_name] = {
                'min_impact': min_impact,
                'max_impact': max_impact,
                'sensitivity_score': max(abs(min_impact), abs(max_impact))
            }
        
        # Ordena por sensibilidade
        sorted_vars = sorted(sensitivity_results.items(), 
                           key=lambda x: x[1]['sensitivity_score'], 
                           reverse=True)
        
        return {
            'variables': sensitivity_results,
            'most_sensitive': sorted_vars[:3],
            'overall_volatility': params.volatility * 100
        }
    
    def _generate_recommendations(self, scenarios: List[Scenario], sensitivity: Dict) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Análise da variação entre cenários
        realistic_final = scenarios[1].values[-1]  # Cenário realista
        optimistic_final = scenarios[0].values[-1]
        pessimistic_final = scenarios[2].values[-1]
        
        upside_potential = (optimistic_final - realistic_final) / realistic_final * 100
        downside_risk = (realistic_final - pessimistic_final) / realistic_final * 100
        
        # Recomendações baseadas no risco/retorno
        if upside_potential > 50:
            recommendations.append("Alto potencial de crescimento identificado - considere investimentos adicionais")
        
        if downside_risk > 30:
            recommendations.append("Risco significativo identificado - desenvolva planos de contingência")
        
        # Recomendações baseadas na sensibilidade
        most_sensitive_var = sensitivity['most_sensitive'][0][0]
        recommendations.append(f"Monitore de perto a variável '{most_sensitive_var}' - maior impacto nos resultados")
        
        # Recomendações gerais
        recommendations.extend([
            "Estabeleça marcos de acompanhamento mensais",
            "Prepare estratégias de mitigação para os principais riscos",
            "Considere cenários intermediários para tomada de decisão",
            "Revise as projeções trimestralmente com dados reais"
        ])
        
        return recommendations
    
    def _identify_key_variables(self, context: str, industry: str) -> List[str]:
        """Identifica variáveis-chave baseadas no contexto e indústria"""
        base_variables = [
            "Taxa de crescimento do mercado",
            "Participação de mercado",
            "Custos operacionais",
            "Preço médio de venda"
        ]
        
        industry_variables = {
            'technology': ["Taxa de adoção", "Ciclo de inovação", "Investimento em P&D"],
            'retail': ["Tráfego de loja", "Ticket médio", "Margem bruta"],
            'services': ["Taxa de retenção", "Custo de aquisição", "Lifetime value"],
            'manufacturing': ["Capacidade produtiva", "Custo de matéria-prima", "Eficiência operacional"]
        }
        
        return base_variables + industry_variables.get(industry, [])
    
    def generate_scenarios_html(self, analysis: ScenarioAnalysis) -> str:
        """Gera HTML da análise de cenários"""
        html = ['<div class="scenario-analysis">']
        html.append('<h3>📈 Análise de Cenários</h3>')
        
        # Resumo dos cenários
        html.append('<div class="scenarios-summary">')
        html.append('<div class="scenarios-grid">')
        
        for scenario in analysis.scenarios:
            scenario_class = f"scenario-{scenario.type}"
            final_value = scenario.values[-1]
            
            html.append(f'<div class="scenario-card {scenario_class}">')
            html.append(f'<h4>{scenario.name}</h4>')
            html.append(f'<div class="scenario-probability">Probabilidade: {scenario.probability*100:.0f}%</div>')
            html.append(f'<div class="scenario-value">Valor Final: {final_value:,.2f}</div>')
            html.append(f'<div class="scenario-confidence">Confiança: {scenario.confidence_level.upper()}</div>')
            html.append('</div>')
        
        html.append('</div>')
        html.append('</div>')
        
        # Gráfico de evolução (simulado com CSS)
        html.append('<div class="scenario-chart">')
        html.append('<h4>Evolução dos Cenários</h4>')
        html.append('<div class="chart-placeholder">')
        html.append('📊 [Gráfico de linha mostrando evolução dos 3 cenários ao longo do tempo]')
        html.append('</div>')
        html.append('</div>')
        
        # Análise de sensibilidade
        html.append('<div class="sensitivity-analysis">')
        html.append('<h4>🎯 Análise de Sensibilidade</h4>')
        html.append('<div class="sensitivity-variables">')
        
        for var_name, var_data in analysis.sensitivity_analysis['most_sensitive']:
            impact_score = var_data['sensitivity_score']
            impact_class = "high" if impact_score > 20 else "medium" if impact_score > 10 else "low"
            
            html.append(f'<div class="sensitivity-item impact-{impact_class}">')
            html.append(f'<strong>{var_name.replace("_", " ").title()}</strong>')
            html.append(f'<span class="impact-score">Impacto: {impact_score:.1f}%</span>')
            html.append('</div>')
        
        html.append('</div>')
        html.append('</div>')
        
        # Recomendações
        html.append('<div class="scenario-recommendations">')
        html.append('<h4>💡 Recomendações Estratégicas</h4>')
        html.append('<ul class="recommendations-list">')
        
        for recommendation in analysis.recommendations:
            html.append(f'<li>{recommendation}</li>')
        
        html.append('</ul>')
        html.append('</div>')
        
        # Variáveis-chave
        html.append('<div class="key-variables">')
        html.append('<h4>🔑 Variáveis-Chave a Monitorar</h4>')
        html.append('<div class="variables-grid">')
        
        for variable in analysis.key_variables:
            html.append(f'<div class="variable-tag">{variable}</div>')
        
        html.append('</div>')
        html.append('</div>')
        
        html.append('</div>')
        
        return '\n'.join(html)
    
    def generate_scenarios_css(self) -> str:
        """Gera CSS para visualização dos cenários"""
        return """
        <style>
        .scenario-analysis {
            margin: 30px 0;
            padding: 25px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px;
            border-left: 5px solid #007bff;
        }
        
        .scenarios-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .scenario-card {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .scenario-card:hover {
            transform: translateY(-5px);
        }
        
        .scenario-optimistic {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-left: 4px solid #28a745;
        }
        
        .scenario-realistic {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border-left: 4px solid #ffc107;
        }
        
        .scenario-pessimistic {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border-left: 4px solid #dc3545;
        }
        
        .scenario-probability {
            font-size: 0.9em;
            color: #666;
            margin: 5px 0;
        }
        
        .scenario-value {
            font-size: 1.5em;
            font-weight: bold;
            margin: 10px 0;
            color: #333;
        }
        
        .scenario-confidence {
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #666;
        }
        
        .scenario-chart {
            margin: 25px 0;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .chart-placeholder {
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 5px;
            color: #6c757d;
            font-size: 1.1em;
        }
        
        .sensitivity-analysis {
            margin: 25px 0;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .sensitivity-variables {
            display: grid;
            gap: 10px;
            margin-top: 15px;
        }
        
        .sensitivity-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            border-radius: 5px;
            border-left: 4px solid #6c757d;
        }
        
        .sensitivity-item.impact-high {
            background-color: #f8d7da;
            border-left-color: #dc3545;
        }
        
        .sensitivity-item.impact-medium {
            background-color: #fff3cd;
            border-left-color: #ffc107;
        }
        
        .sensitivity-item.impact-low {
            background-color: #d4edda;
            border-left-color: #28a745;
        }
        
        .impact-score {
            font-weight: bold;
            font-size: 0.9em;
        }
        
        .scenario-recommendations {
            margin: 25px 0;
            padding: 20px;
            background-color: #e7f3ff;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        
        .recommendations-list {
            margin: 15px 0;
            padding-left: 20px;
        }
        
        .recommendations-list li {
            margin-bottom: 8px;
            line-height: 1.5;
        }
        
        .key-variables {
            margin: 25px 0;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .variables-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        
        .variable-tag {
            padding: 8px 15px;
            background-color: #007bff;
            color: white;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
        }
        </style>
        """
    
    def export_scenarios_json(self, analysis: ScenarioAnalysis) -> str:
        """Exporta análise de cenários em JSON"""
        data = {
            'scenarios': [asdict(scenario) for scenario in analysis.scenarios],
            'sensitivity_analysis': analysis.sensitivity_analysis,
            'recommendations': analysis.recommendations,
            'key_variables': analysis.key_variables,
            'export_date': datetime.now().isoformat()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

# Instância global do analisador
scenario_analyzer = ScenarioAnalyzer()