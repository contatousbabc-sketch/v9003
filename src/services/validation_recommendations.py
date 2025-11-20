"""
Sistema de Recomendações de Validação e Especialistas
Implementa sugestões de validação e indicação de profissionais por área
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Expert:
    """Estrutura de um especialista recomendado"""
    profession: str
    specialization: str
    description: str
    when_to_consult: List[str]
    typical_services: List[str]
    regulatory_bodies: List[str]
    cost_range: str
    urgency_level: str  # low, medium, high, critical

@dataclass
class ValidationStep:
    """Etapa de validação recomendada"""
    step_id: str
    title: str
    description: str
    priority: str  # low, medium, high, critical
    estimated_time: str
    required_resources: List[str]
    success_criteria: List[str]
    potential_issues: List[str]

@dataclass
class ValidationPlan:
    """Plano completo de validação"""
    context: str
    industry: str
    validation_steps: List[ValidationStep]
    recommended_experts: List[Expert]
    estimated_timeline: str
    estimated_cost: str
    critical_checkpoints: List[str]
    success_metrics: List[str]

class ValidationRecommendationSystem:
    """Sistema principal de recomendações de validação"""
    
    def __init__(self):
        self.experts_database = self._load_experts_database()
        self.validation_templates = self._load_validation_templates()
        self.industry_requirements = self._load_industry_requirements()
        
    def _load_experts_database(self) -> Dict[str, Expert]:
        """Carrega base de dados de especialistas por área"""
        experts = {}
        
        # Especialistas Financeiros
        experts['contador'] = Expert(
            profession='Contador',
            specialization='Contabilidade e Finanças',
            description='Profissional especializado em contabilidade, finanças e tributação',
            when_to_consult=[
                'Análise de demonstrações financeiras',
                'Planejamento tributário',
                'Estruturação de custos',
                'Projeções financeiras',
                'Compliance fiscal'
            ],
            typical_services=[
                'Auditoria de demonstrações financeiras',
                'Planejamento tributário',
                'Análise de viabilidade econômica',
                'Estruturação de custos',
                'Consultoria fiscal'
            ],
            regulatory_bodies=['CRC - Conselho Regional de Contabilidade'],
            cost_range='R$ 150 - R$ 500/hora',
            urgency_level='high'
        )
        
        experts['consultor_financeiro'] = Expert(
            profession='Consultor Financeiro',
            specialization='Investimentos e Planejamento Financeiro',
            description='Especialista em investimentos, planejamento financeiro e gestão de patrimônio',
            when_to_consult=[
                'Estratégias de investimento',
                'Análise de risco financeiro',
                'Planejamento de aposentadoria',
                'Diversificação de portfólio',
                'Produtos financeiros'
            ],
            typical_services=[
                'Análise de perfil de investidor',
                'Recomendação de produtos financeiros',
                'Planejamento financeiro pessoal',
                'Gestão de carteiras',
                'Educação financeira'
            ],
            regulatory_bodies=['ANBIMA', 'CVM'],
            cost_range='R$ 200 - R$ 800/hora',
            urgency_level='medium'
        )
        
        # Especialistas Jurídicos
        experts['advogado_empresarial'] = Expert(
            profession='Advogado Empresarial',
            specialization='Direito Empresarial e Societário',
            description='Advogado especializado em direito empresarial, contratos e questões societárias',
            when_to_consult=[
                'Estruturação de empresas',
                'Elaboração de contratos',
                'Questões societárias',
                'Compliance empresarial',
                'Fusões e aquisições'
            ],
            typical_services=[
                'Constituição de empresas',
                'Elaboração de contratos',
                'Due diligence jurídica',
                'Consultoria em compliance',
                'Reestruturação societária'
            ],
            regulatory_bodies=['OAB - Ordem dos Advogados do Brasil'],
            cost_range='R$ 300 - R$ 1.200/hora',
            urgency_level='high'
        )
        
        experts['advogado_tributario'] = Expert(
            profession='Advogado Tributário',
            specialization='Direito Tributário',
            description='Especialista em questões tributárias, fiscais e regulatórias',
            when_to_consult=[
                'Planejamento tributário',
                'Questões fiscais complexas',
                'Defesa em autuações',
                'Estruturação tributária',
                'Compliance fiscal'
            ],
            typical_services=[
                'Consultoria tributária',
                'Defesa administrativa',
                'Planejamento fiscal',
                'Revisão de tributos',
                'Estruturação tributária'
            ],
            regulatory_bodies=['OAB - Ordem dos Advogados do Brasil'],
            cost_range='R$ 400 - R$ 1.500/hora',
            urgency_level='critical'
        )
        
        # Especialistas de Marketing
        experts['especialista_marketing'] = Expert(
            profession='Especialista em Marketing',
            specialization='Marketing Digital e Estratégico',
            description='Profissional especializado em estratégias de marketing e comunicação',
            when_to_consult=[
                'Estratégias de marketing',
                'Análise de mercado',
                'Posicionamento de marca',
                'Campanhas publicitárias',
                'Marketing digital'
            ],
            typical_services=[
                'Planejamento estratégico de marketing',
                'Pesquisa de mercado',
                'Desenvolvimento de campanhas',
                'Análise de concorrência',
                'Consultoria em branding'
            ],
            regulatory_bodies=['CONAR - Conselho Nacional de Autorregulamentação Publicitária'],
            cost_range='R$ 150 - R$ 600/hora',
            urgency_level='medium'
        )
        
        # Especialistas Técnicos
        experts['engenheiro_producao'] = Expert(
            profession='Engenheiro de Produção',
            specialization='Processos e Operações',
            description='Especialista em otimização de processos, produção e operações',
            when_to_consult=[
                'Otimização de processos',
                'Análise de capacidade produtiva',
                'Gestão de qualidade',
                'Redução de custos operacionais',
                'Implementação de melhorias'
            ],
            typical_services=[
                'Mapeamento de processos',
                'Análise de capacidade',
                'Implementação de lean manufacturing',
                'Gestão da qualidade',
                'Otimização de layout'
            ],
            regulatory_bodies=['CREA - Conselho Regional de Engenharia'],
            cost_range='R$ 200 - R$ 700/hora',
            urgency_level='medium'
        )
        
        experts['consultor_ti'] = Expert(
            profession='Consultor de TI',
            specialization='Tecnologia da Informação',
            description='Especialista em sistemas, infraestrutura e soluções tecnológicas',
            when_to_consult=[
                'Implementação de sistemas',
                'Segurança da informação',
                'Infraestrutura de TI',
                'Transformação digital',
                'Análise de sistemas'
            ],
            typical_services=[
                'Consultoria em sistemas',
                'Auditoria de segurança',
                'Planejamento de infraestrutura',
                'Implementação de soluções',
                'Treinamento técnico'
            ],
            regulatory_bodies=['Certificações específicas (CISSP, PMP, etc.)'],
            cost_range='R$ 180 - R$ 800/hora',
            urgency_level='medium'
        )
        
        # Especialistas Regulatórios
        experts['especialista_regulatorio'] = Expert(
            profession='Especialista Regulatório',
            specialization='Compliance e Regulamentações',
            description='Profissional especializado em compliance e questões regulatórias setoriais',
            when_to_consult=[
                'Compliance regulatório',
                'Licenças e autorizações',
                'Adequação a normas',
                'Auditoria de compliance',
                'Relacionamento com órgãos'
            ],
            typical_services=[
                'Auditoria de compliance',
                'Implementação de políticas',
                'Treinamento em compliance',
                'Relacionamento institucional',
                'Monitoramento regulatório'
            ],
            regulatory_bodies=['Varia por setor (ANVISA, CVM, ANATEL, etc.)'],
            cost_range='R$ 250 - R$ 900/hora',
            urgency_level='high'
        )
        
        # Especialistas de Saúde
        experts['medico_especialista'] = Expert(
            profession='Médico Especialista',
            specialization='Medicina e Saúde',
            description='Profissional médico especializado em área específica da saúde',
            when_to_consult=[
                'Validação de informações médicas',
                'Análise de tratamentos',
                'Avaliação de produtos de saúde',
                'Pesquisa clínica',
                'Protocolos médicos'
            ],
            typical_services=[
                'Consultoria médica',
                'Revisão científica',
                'Desenvolvimento de protocolos',
                'Treinamento médico',
                'Pesquisa clínica'
            ],
            regulatory_bodies=['CRM - Conselho Regional de Medicina'],
            cost_range='R$ 300 - R$ 1.000/hora',
            urgency_level='critical'
        )
        
        return experts
    
    def _load_validation_templates(self) -> Dict[str, List[ValidationStep]]:
        """Carrega templates de validação por contexto"""
        return {
            'financial_analysis': [
                ValidationStep(
                    step_id='financial_data_verification',
                    title='Verificação de Dados Financeiros',
                    description='Validar dados financeiros com fontes oficiais e demonstrações auditadas',
                    priority='critical',
                    estimated_time='2-3 dias',
                    required_resources=['Demonstrações financeiras', 'Relatórios oficiais', 'Contador'],
                    success_criteria=['Dados confirmados em múltiplas fontes', 'Consistência temporal'],
                    potential_issues=['Dados desatualizados', 'Fontes não confiáveis', 'Inconsistências']
                ),
                ValidationStep(
                    step_id='market_data_validation',
                    title='Validação de Dados de Mercado',
                    description='Confirmar informações de mercado com pesquisas e relatórios setoriais',
                    priority='high',
                    estimated_time='3-5 dias',
                    required_resources=['Relatórios setoriais', 'Pesquisas de mercado', 'Especialista'],
                    success_criteria=['Dados alinhados com tendências', 'Fontes múltiplas confirmam'],
                    potential_issues=['Dados conflitantes', 'Amostras pequenas', 'Viés de seleção']
                ),
                ValidationStep(
                    step_id='projection_review',
                    title='Revisão de Projeções',
                    description='Avaliar metodologia e premissas das projeções financeiras',
                    priority='high',
                    estimated_time='1-2 dias',
                    required_resources=['Modelos financeiros', 'Dados históricos', 'Consultor financeiro'],
                    success_criteria=['Metodologia sólida', 'Premissas realistas', 'Cenários múltiplos'],
                    potential_issues=['Premissas otimistas', 'Metodologia inadequada', 'Falta de cenários']
                )
            ],
            'market_research': [
                ValidationStep(
                    step_id='sample_validation',
                    title='Validação da Amostra',
                    description='Verificar representatividade e tamanho da amostra da pesquisa',
                    priority='high',
                    estimated_time='1 dia',
                    required_resources=['Dados da pesquisa', 'Especialista em estatística'],
                    success_criteria=['Amostra representativa', 'Tamanho adequado', 'Metodologia clara'],
                    potential_issues=['Amostra pequena', 'Viés de seleção', 'Metodologia inadequada']
                ),
                ValidationStep(
                    step_id='competitor_analysis',
                    title='Análise Competitiva',
                    description='Validar informações sobre concorrentes e posicionamento',
                    priority='medium',
                    estimated_time='2-3 dias',
                    required_resources=['Dados públicos', 'Relatórios setoriais', 'Especialista de mercado'],
                    success_criteria=['Dados atualizados', 'Fontes confiáveis', 'Análise abrangente'],
                    potential_issues=['Dados desatualizados', 'Informações incompletas', 'Viés competitivo']
                )
            ],
            'regulatory_compliance': [
                ValidationStep(
                    step_id='regulation_review',
                    title='Revisão Regulatória',
                    description='Verificar conformidade com regulamentações atuais',
                    priority='critical',
                    estimated_time='3-5 dias',
                    required_resources=['Textos legais', 'Especialista regulatório', 'Advogado'],
                    success_criteria=['Conformidade total', 'Documentação adequada', 'Processos alinhados'],
                    potential_issues=['Regulamentações desatualizadas', 'Interpretação incorreta', 'Gaps de compliance']
                ),
                ValidationStep(
                    step_id='documentation_audit',
                    title='Auditoria de Documentação',
                    description='Verificar adequação e completude da documentação',
                    priority='high',
                    estimated_time='2-3 dias',
                    required_resources=['Documentos existentes', 'Checklist regulatório', 'Auditor'],
                    success_criteria=['Documentação completa', 'Processos documentados', 'Rastreabilidade'],
                    potential_issues=['Documentação incompleta', 'Processos não documentados', 'Falta de controle']
                )
            ],
            'product_development': [
                ValidationStep(
                    step_id='technical_feasibility',
                    title='Viabilidade Técnica',
                    description='Avaliar viabilidade técnica e recursos necessários',
                    priority='critical',
                    estimated_time='5-7 dias',
                    required_resources=['Especificações técnicas', 'Engenheiro especialista', 'Protótipos'],
                    success_criteria=['Viabilidade confirmada', 'Recursos identificados', 'Riscos mapeados'],
                    potential_issues=['Limitações técnicas', 'Recursos insuficientes', 'Complexidade subestimada']
                ),
                ValidationStep(
                    step_id='market_validation',
                    title='Validação de Mercado',
                    description='Confirmar demanda e aceitação do produto no mercado',
                    priority='high',
                    estimated_time='7-10 dias',
                    required_resources=['Pesquisa de mercado', 'Testes com usuários', 'Especialista de marketing'],
                    success_criteria=['Demanda confirmada', 'Feedback positivo', 'Mercado identificado'],
                    potential_issues=['Demanda insuficiente', 'Feedback negativo', 'Mercado saturado']
                )
            ]
        }
    
    def _load_industry_requirements(self) -> Dict[str, Dict]:
        """Carrega requisitos específicos por indústria"""
        return {
            'financial_services': {
                'mandatory_experts': ['contador', 'advogado_tributario', 'consultor_financeiro'],
                'critical_validations': ['financial_data_verification', 'regulatory_compliance'],
                'regulatory_focus': ['CVM', 'BACEN', 'SUSEP'],
                'typical_timeline': '2-4 semanas',
                'estimated_cost': 'R$ 15.000 - R$ 50.000'
            },
            'healthcare': {
                'mandatory_experts': ['medico_especialista', 'especialista_regulatorio'],
                'critical_validations': ['regulatory_compliance', 'technical_feasibility'],
                'regulatory_focus': ['ANVISA', 'CFM', 'ANS'],
                'typical_timeline': '4-8 semanas',
                'estimated_cost': 'R$ 20.000 - R$ 80.000'
            },
            'technology': {
                'mandatory_experts': ['consultor_ti', 'engenheiro_producao'],
                'critical_validations': ['technical_feasibility', 'market_validation'],
                'regulatory_focus': ['ANATEL', 'LGPD'],
                'typical_timeline': '3-6 semanas',
                'estimated_cost': 'R$ 10.000 - R$ 40.000'
            },
            'retail': {
                'mandatory_experts': ['especialista_marketing', 'contador'],
                'critical_validations': ['market_validation', 'financial_analysis'],
                'regulatory_focus': ['PROCON', 'INMETRO'],
                'typical_timeline': '2-4 semanas',
                'estimated_cost': 'R$ 8.000 - R$ 25.000'
            },
            'manufacturing': {
                'mandatory_experts': ['engenheiro_producao', 'especialista_regulatorio'],
                'critical_validations': ['technical_feasibility', 'regulatory_compliance'],
                'regulatory_focus': ['INMETRO', 'IBAMA', 'Ministério do Trabalho'],
                'typical_timeline': '4-8 semanas',
                'estimated_cost': 'R$ 15.000 - R$ 60.000'
            }
        }
    
    def generate_validation_plan(self, content: str, industry: str = 'general', 
                               context: str = 'general_analysis') -> ValidationPlan:
        """Gera plano de validação personalizado"""
        
        # Identifica validações necessárias
        validation_steps = self._identify_validation_steps(content, context, industry)
        
        # Identifica especialistas recomendados
        recommended_experts = self._identify_recommended_experts(content, industry, validation_steps)
        
        # Estima timeline e custos
        timeline_estimate = self._estimate_timeline(validation_steps, industry)
        cost_estimate = self._estimate_costs(recommended_experts, validation_steps, industry)
        
        # Identifica checkpoints críticos
        critical_checkpoints = self._identify_critical_checkpoints(validation_steps, industry)
        
        # Define métricas de sucesso
        success_metrics = self._define_success_metrics(context, industry)
        
        return ValidationPlan(
            context=context,
            industry=industry,
            validation_steps=validation_steps,
            recommended_experts=recommended_experts,
            estimated_timeline=timeline_estimate,
            estimated_cost=cost_estimate,
            critical_checkpoints=critical_checkpoints,
            success_metrics=success_metrics
        )
    
    def _identify_validation_steps(self, content: str, context: str, industry: str) -> List[ValidationStep]:
        """Identifica etapas de validação necessárias"""
        steps = []
        content_lower = content.lower()
        
        # Adiciona steps baseados no contexto
        if context in self.validation_templates:
            steps.extend(self.validation_templates[context])
        else:
            # Steps genéricos se contexto não encontrado
            steps.extend(self.validation_templates.get('market_research', []))
        
        # Adiciona steps baseados no conteúdo
        if any(word in content_lower for word in ['financeiro', 'investimento', 'receita', 'lucro']):
            financial_steps = self.validation_templates.get('financial_analysis', [])
            for step in financial_steps:
                if step not in steps:
                    steps.append(step)
        
        if any(word in content_lower for word in ['regulamentação', 'compliance', 'lei', 'norma']):
            regulatory_steps = self.validation_templates.get('regulatory_compliance', [])
            for step in regulatory_steps:
                if step not in steps:
                    steps.append(step)
        
        if any(word in content_lower for word in ['produto', 'desenvolvimento', 'inovação']):
            product_steps = self.validation_templates.get('product_development', [])
            for step in product_steps:
                if step not in steps:
                    steps.append(step)
        
        # Ordena por prioridade
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        steps.sort(key=lambda x: priority_order.get(x.priority, 3))
        
        return steps[:8]  # Máximo 8 steps para não sobrecarregar
    
    def _identify_recommended_experts(self, content: str, industry: str, 
                                    validation_steps: List[ValidationStep]) -> List[Expert]:
        """Identifica especialistas recomendados"""
        recommended = []
        content_lower = content.lower()
        
        # Especialistas obrigatórios por indústria
        if industry in self.industry_requirements:
            mandatory_experts = self.industry_requirements[industry]['mandatory_experts']
            for expert_id in mandatory_experts:
                if expert_id in self.experts_database:
                    recommended.append(self.experts_database[expert_id])
        
        # Especialistas baseados no conteúdo
        expert_triggers = {
            'contador': ['financeiro', 'contábil', 'tributário', 'fiscal', 'demonstração'],
            'advogado_empresarial': ['contrato', 'jurídico', 'legal', 'societário'],
            'especialista_marketing': ['marketing', 'mercado', 'cliente', 'campanha', 'branding'],
            'consultor_ti': ['sistema', 'tecnologia', 'software', 'digital', 'ti'],
            'medico_especialista': ['saúde', 'médico', 'tratamento', 'diagnóstico', 'clínico'],
            'especialista_regulatorio': ['regulamentação', 'compliance', 'norma', 'licença']
        }
        
        for expert_id, triggers in expert_triggers.items():
            if any(trigger in content_lower for trigger in triggers):
                if expert_id in self.experts_database:
                    expert = self.experts_database[expert_id]
                    if expert not in recommended:
                        recommended.append(expert)
        
        # Especialistas baseados nas etapas de validação
        step_expert_mapping = {
            'financial_data_verification': ['contador', 'consultor_financeiro'],
            'regulatory_compliance': ['especialista_regulatorio', 'advogado_empresarial'],
            'technical_feasibility': ['engenheiro_producao', 'consultor_ti'],
            'market_validation': ['especialista_marketing']
        }
        
        for step in validation_steps:
            if step.step_id in step_expert_mapping:
                for expert_id in step_expert_mapping[step.step_id]:
                    if expert_id in self.experts_database:
                        expert = self.experts_database[expert_id]
                        if expert not in recommended:
                            recommended.append(expert)
        
        # Ordena por urgência
        urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommended.sort(key=lambda x: urgency_order.get(x.urgency_level, 3))
        
        return recommended[:6]  # Máximo 6 especialistas
    
    def _estimate_timeline(self, validation_steps: List[ValidationStep], industry: str) -> str:
        """Estima timeline do projeto"""
        if industry in self.industry_requirements:
            return self.industry_requirements[industry]['typical_timeline']
        
        # Estimativa baseada nas etapas
        total_days = 0
        for step in validation_steps:
            # Extrai número de dias da estimativa
            time_str = step.estimated_time.lower()
            if 'dia' in time_str:
                days = int(time_str.split('-')[0]) if '-' in time_str else int(time_str.split()[0])
                total_days += days
        
        if total_days <= 7:
            return '1-2 semanas'
        elif total_days <= 21:
            return '2-4 semanas'
        elif total_days <= 42:
            return '4-8 semanas'
        else:
            return '8+ semanas'
    
    def _estimate_costs(self, experts: List[Expert], steps: List[ValidationStep], industry: str) -> str:
        """Estima custos do projeto"""
        if industry in self.industry_requirements:
            return self.industry_requirements[industry]['estimated_cost']
        
        # Estimativa baseada nos especialistas
        min_cost = 0
        max_cost = 0
        
        for expert in experts:
            # Extrai valores do range de custo
            cost_range = expert.cost_range.replace('R$', '').replace('/hora', '').strip()
            if '-' in cost_range:
                min_val = int(cost_range.split('-')[0].strip())
                max_val = int(cost_range.split('-')[1].strip())
                
                # Estima 10-20 horas por especialista
                min_cost += min_val * 10
                max_cost += max_val * 20
        
        if min_cost == 0:
            return 'R$ 5.000 - R$ 20.000'
        
        return f'R$ {min_cost:,.0f} - R$ {max_cost:,.0f}'
    
    def _identify_critical_checkpoints(self, steps: List[ValidationStep], industry: str) -> List[str]:
        """Identifica checkpoints críticos"""
        checkpoints = []
        
        # Checkpoints baseados em steps críticos
        critical_steps = [step for step in steps if step.priority == 'critical']
        for step in critical_steps:
            checkpoints.append(f"Conclusão: {step.title}")
        
        # Checkpoints padrão
        checkpoints.extend([
            "Validação de dados críticos concluída",
            "Aprovação de especialistas obtida",
            "Documentação de validação finalizada",
            "Relatório final de validação aprovado"
        ])
        
        return checkpoints[:6]  # Máximo 6 checkpoints
    
    def _define_success_metrics(self, context: str, industry: str) -> List[str]:
        """Define métricas de sucesso"""
        base_metrics = [
            "95% dos dados críticos validados",
            "Aprovação de todos os especialistas consultados",
            "Zero não-conformidades críticas identificadas",
            "Documentação completa e aprovada"
        ]
        
        context_metrics = {
            'financial_analysis': [
                "Dados financeiros confirmados em 3+ fontes",
                "Projeções validadas por especialista",
                "Compliance fiscal verificado"
            ],
            'market_research': [
                "Amostra representativa confirmada",
                "Dados de mercado atualizados",
                "Análise competitiva validada"
            ],
            'regulatory_compliance': [
                "100% conformidade regulatória",
                "Documentação aprovada por órgãos",
                "Processos auditados e aprovados"
            ]
        }
        
        metrics = base_metrics.copy()
        if context in context_metrics:
            metrics.extend(context_metrics[context])
        
        return metrics[:8]  # Máximo 8 métricas
    
    def generate_validation_html(self, plan: ValidationPlan) -> str:
        """Gera HTML do plano de validação"""
        html = ['<div class="validation-recommendations">']
        html.append('<h3>✅ Plano de Validação e Especialistas</h3>')
        
        # Resumo do plano
        html.append('<div class="validation-summary">')
        html.append('<h4>📋 Resumo do Plano</h4>')
        html.append(f'<p><strong>Contexto:</strong> {plan.context.replace("_", " ").title()}</p>')
        html.append(f'<p><strong>Indústria:</strong> {plan.industry.replace("_", " ").title()}</p>')
        html.append(f'<p><strong>Timeline Estimado:</strong> {plan.estimated_timeline}</p>')
        html.append(f'<p><strong>Custo Estimado:</strong> {plan.estimated_cost}</p>')
        html.append('</div>')
        
        # Especialistas recomendados
        if plan.recommended_experts:
            html.append('<div class="recommended-experts">')
            html.append('<h4>👥 Especialistas Recomendados</h4>')
            
            for expert in plan.recommended_experts:
                urgency_class = f"urgency-{expert.urgency_level}"
                html.append(f'<div class="expert-card {urgency_class}">')
                html.append(f'<h5>{expert.profession}</h5>')
                html.append(f'<p class="specialization">{expert.specialization}</p>')
                html.append(f'<p class="description">{expert.description}</p>')
                
                # Quando consultar
                html.append('<div class="when-consult">')
                html.append('<strong>Quando Consultar:</strong>')
                html.append('<ul>')
                for reason in expert.when_to_consult[:3]:
                    html.append(f'<li>{reason}</li>')
                html.append('</ul>')
                html.append('</div>')
                
                # Informações práticas
                html.append('<div class="expert-info">')
                html.append(f'<span class="cost-range">💰 {expert.cost_range}</span>')
                html.append(f'<span class="urgency">⚡ {expert.urgency_level.upper()}</span>')
                html.append('</div>')
                
                # Órgãos reguladores
                if expert.regulatory_bodies:
                    html.append('<div class="regulatory-bodies">')
                    html.append('<strong>Órgãos Reguladores:</strong>')
                    for body in expert.regulatory_bodies:
                        html.append(f'<span class="regulatory-tag">{body}</span>')
                    html.append('</div>')
                
                html.append('</div>')
            
            html.append('</div>')
        
        # Etapas de validação
        if plan.validation_steps:
            html.append('<div class="validation-steps">')
            html.append('<h4>🔍 Etapas de Validação</h4>')
            
            for i, step in enumerate(plan.validation_steps, 1):
                priority_class = f"priority-{step.priority}"
                html.append(f'<div class="validation-step {priority_class}">')
                html.append(f'<h5>Etapa {i}: {step.title}</h5>')
                html.append(f'<p class="step-description">{step.description}</p>')
                
                # Informações da etapa
                html.append('<div class="step-info">')
                html.append(f'<span class="priority">Prioridade: {step.priority.upper()}</span>')
                html.append(f'<span class="time">Tempo: {step.estimated_time}</span>')
                html.append('</div>')
                
                # Recursos necessários
                if step.required_resources:
                    html.append('<div class="required-resources">')
                    html.append('<strong>Recursos Necessários:</strong>')
                    html.append('<ul>')
                    for resource in step.required_resources:
                        html.append(f'<li>{resource}</li>')
                    html.append('</ul>')
                    html.append('</div>')
                
                # Critérios de sucesso
                if step.success_criteria:
                    html.append('<div class="success-criteria">')
                    html.append('<strong>Critérios de Sucesso:</strong>')
                    html.append('<ul>')
                    for criteria in step.success_criteria[:2]:
                        html.append(f'<li>✅ {criteria}</li>')
                    html.append('</ul>')
                    html.append('</div>')
                
                html.append('</div>')
            
            html.append('</div>')
        
        # Checkpoints críticos
        if plan.critical_checkpoints:
            html.append('<div class="critical-checkpoints">')
            html.append('<h4>🎯 Checkpoints Críticos</h4>')
            html.append('<div class="checkpoints-list">')
            
            for checkpoint in plan.critical_checkpoints:
                html.append(f'<div class="checkpoint-item">')
                html.append(f'<input type="checkbox" id="checkpoint-{hash(checkpoint)}">')
                html.append(f'<label for="checkpoint-{hash(checkpoint)}">{checkpoint}</label>')
                html.append('</div>')
            
            html.append('</div>')
            html.append('</div>')
        
        # Métricas de sucesso
        if plan.success_metrics:
            html.append('<div class="success-metrics">')
            html.append('<h4>📊 Métricas de Sucesso</h4>')
            html.append('<div class="metrics-grid">')
            
            for metric in plan.success_metrics:
                html.append(f'<div class="metric-card">{metric}</div>')
            
            html.append('</div>')
            html.append('</div>')
        
        html.append('</div>')
        
        return '\n'.join(html)
    
    def generate_validation_css(self) -> str:
        """Gera CSS para visualização das recomendações"""
        return """
        <style>
        .validation-recommendations {
            margin: 30px 0;
            padding: 25px;
            background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
            border-radius: 12px;
            border-left: 5px solid #38a169;
        }
        
        .validation-summary {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .recommended-experts {
            margin-bottom: 25px;
        }
        
        .expert-card {
            background-color: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 5px solid;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .expert-card.urgency-critical {
            border-left-color: #e53e3e;
        }
        
        .expert-card.urgency-high {
            border-left-color: #dd6b20;
        }
        
        .expert-card.urgency-medium {
            border-left-color: #d69e2e;
        }
        
        .expert-card.urgency-low {
            border-left-color: #38a169;
        }
        
        .expert-card h5 {
            color: #2d3748;
            margin-bottom: 5px;
        }
        
        .specialization {
            color: #4a5568;
            font-style: italic;
            margin-bottom: 10px;
        }
        
        .description {
            color: #718096;
            margin-bottom: 15px;
        }
        
        .when-consult {
            margin: 15px 0;
        }
        
        .when-consult ul {
            margin: 8px 0;
            padding-left: 20px;
        }
        
        .expert-info {
            display: flex;
            gap: 15px;
            margin: 15px 0;
        }
        
        .cost-range, .urgency {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }
        
        .cost-range {
            background-color: #e6fffa;
            color: #234e52;
        }
        
        .urgency {
            background-color: #fef5e7;
            color: #744210;
        }
        
        .regulatory-bodies {
            margin-top: 15px;
        }
        
        .regulatory-tag {
            display: inline-block;
            padding: 3px 8px;
            margin: 2px;
            background-color: #edf2f7;
            border-radius: 8px;
            font-size: 0.8em;
            color: #4a5568;
        }
        
        .validation-steps {
            margin-bottom: 25px;
        }
        
        .validation-step {
            background-color: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 5px solid;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .validation-step.priority-critical {
            border-left-color: #e53e3e;
        }
        
        .validation-step.priority-high {
            border-left-color: #dd6b20;
        }
        
        .validation-step.priority-medium {
            border-left-color: #d69e2e;
        }
        
        .validation-step.priority-low {
            border-left-color: #38a169;
        }
        
        .step-description {
            color: #4a5568;
            margin-bottom: 15px;
        }
        
        .step-info {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .priority, .time {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
            background-color: #edf2f7;
            color: #4a5568;
        }
        
        .required-resources, .success-criteria {
            margin: 15px 0;
        }
        
        .required-resources ul, .success-criteria ul {
            margin: 8px 0;
            padding-left: 20px;
        }
        
        .critical-checkpoints {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .checkpoints-list {
            margin-top: 15px;
        }
        
        .checkpoint-item {
            display: flex;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .checkpoint-item:last-child {
            border-bottom: none;
        }
        
        .checkpoint-item input[type="checkbox"] {
            margin-right: 10px;
            transform: scale(1.2);
        }
        
        .checkpoint-item label {
            cursor: pointer;
            color: #4a5568;
        }
        
        .success-metrics {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .metric-card {
            padding: 15px;
            background-color: #f7fafc;
            border-radius: 8px;
            border-left: 4px solid #38a169;
            font-size: 0.9em;
            color: #4a5568;
        }
        </style>
        """
    
    def export_validation_plan_json(self, plan: ValidationPlan) -> str:
        """Exporta plano de validação em JSON"""
        data = {
            'validation_plan': asdict(plan),
            'experts_database': {expert_id: asdict(expert) for expert_id, expert in self.experts_database.items()},
            'export_date': datetime.now().isoformat()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

# Instância global do sistema
validation_recommendation_system = ValidationRecommendationSystem()