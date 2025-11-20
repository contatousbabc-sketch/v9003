"""
Sistema de Disclaimers Contextuais e Avisos
Implementa disclaimers automáticos baseados no conteúdo e contexto
"""

import re
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Disclaimer:
    """Estrutura de um disclaimer"""
    id: str
    title: str
    content: str
    severity: str  # critical, warning, info
    category: str
    triggers: List[str]  # Palavras-chave que ativam o disclaimer
    mandatory: bool = False
    
@dataclass
class DisclaimerContext:
    """Contexto para aplicação de disclaimers"""
    content_type: str  # financial, health, legal, marketing, general
    industry: str
    contains_projections: bool = False
    contains_financial_advice: bool = False
    contains_health_claims: bool = False
    contains_legal_advice: bool = False
    ai_generated: bool = True

class DisclaimerManager:
    """Sistema principal de gerenciamento de disclaimers"""
    
    def __init__(self):
        self.disclaimers = self._load_disclaimers()
        self.sensitive_keywords = self._load_sensitive_keywords()
        self.regulatory_requirements = self._load_regulatory_requirements()
    
    def _load_disclaimers(self) -> Dict[str, Disclaimer]:
        """Carrega biblioteca de disclaimers"""
        disclaimers = {}
        
        # Disclaimer geral de IA
        disclaimers['ai_generated'] = Disclaimer(
            id='ai_generated',
            title='⚠️ Conteúdo Gerado por Inteligência Artificial',
            content='''Este documento foi gerado por inteligência artificial com base em dados coletados da web. 
            As informações apresentadas devem ser validadas por profissionais qualificados antes de qualquer 
            tomada de decisão. A precisão e atualidade dos dados não podem ser garantidas.''',
            severity='warning',
            category='general',
            triggers=['*'],  # Sempre aplicado
            mandatory=True
        )
        
        # Disclaimers financeiros
        disclaimers['financial_projections'] = Disclaimer(
            id='financial_projections',
            title='💰 Projeções Financeiras - Aviso Importante',
            content='''As projeções financeiras apresentadas são estimativas baseadas em dados históricos e 
            premissas que podem não se concretizar. Resultados passados não garantem resultados futuros. 
            Consulte um contador ou consultor financeiro antes de tomar decisões de investimento.''',
            severity='critical',
            category='financial',
            triggers=['receita', 'lucro', 'investimento', 'roi', 'retorno', 'projeção', 'faturamento'],
            mandatory=True
        )
        
        disclaimers['investment_advice'] = Disclaimer(
            id='investment_advice',
            title='📊 Não Constitui Consultoria de Investimentos',
            content='''Este conteúdo não constitui consultoria de investimentos, recomendação de compra ou venda 
            de ativos, ou aconselhamento financeiro personalizado. Sempre consulte um consultor financeiro 
            certificado antes de fazer investimentos.''',
            severity='critical',
            category='financial',
            triggers=['investir', 'ações', 'fundos', 'renda fixa', 'criptomoedas', 'bolsa'],
            mandatory=True
        )
        
        # Disclaimers de saúde
        disclaimers['health_claims'] = Disclaimer(
            id='health_claims',
            title='🏥 Informações de Saúde - Consulte um Médico',
            content='''As informações sobre saúde apresentadas são apenas para fins educacionais e não substituem 
            o aconselhamento médico profissional. Sempre consulte um médico ou profissional de saúde qualificado 
            para questões relacionadas à sua saúde.''',
            severity='critical',
            category='health',
            triggers=['saúde', 'medicina', 'tratamento', 'diagnóstico', 'sintomas', 'doença'],
            mandatory=True
        )
        
        # Disclaimers legais
        disclaimers['legal_advice'] = Disclaimer(
            id='legal_advice',
            title='⚖️ Não Constitui Aconselhamento Jurídico',
            content='''Este conteúdo não constitui aconselhamento jurídico e não deve ser usado como substituto 
            para consulta com um advogado qualificado. As leis variam por jurisdição e podem ter mudado desde 
            a geração deste conteúdo.''',
            severity='critical',
            category='legal',
            triggers=['lei', 'legal', 'jurídico', 'contrato', 'direito', 'advogado', 'processo'],
            mandatory=True
        )
        
        # Disclaimers de dados
        disclaimers['data_accuracy'] = Disclaimer(
            id='data_accuracy',
            title='📈 Precisão dos Dados',
            content='''Os dados apresentados foram coletados de fontes públicas e podem conter imprecisões. 
            A data de coleta e as fontes estão indicadas nas referências. Recomenda-se verificação independente 
            dos dados críticos para sua decisão.''',
            severity='warning',
            category='data',
            triggers=['dados', 'estatística', 'pesquisa', 'estudo', 'análise'],
            mandatory=False
        )
        
        # Disclaimers de mercado
        disclaimers['market_volatility'] = Disclaimer(
            id='market_volatility',
            title='📊 Volatilidade do Mercado',
            content='''As condições de mercado são voláteis e podem mudar rapidamente. As análises apresentadas 
            refletem condições no momento da geração do conteúdo e podem não ser aplicáveis no futuro. 
            Monitore continuamente as condições de mercado.''',
            severity='warning',
            category='market',
            triggers=['mercado', 'concorrência', 'demanda', 'oferta', 'tendência'],
            mandatory=False
        )
        
        # Disclaimers regulatórios
        disclaimers['regulatory_compliance'] = Disclaimer(
            id='regulatory_compliance',
            title='📋 Conformidade Regulatória',
            content='''As informações sobre regulamentações podem estar desatualizadas ou incompletas. 
            Regulamentações variam por localização e podem ter mudado recentemente. Consulte sempre as 
            fontes oficiais e profissionais especializados para questões de compliance.''',
            severity='warning',
            category='regulatory',
            triggers=['regulamentação', 'compliance', 'licença', 'autorização', 'anvisa', 'cvm'],
            mandatory=False
        )
        
        # Disclaimers de estimativas
        disclaimers['estimates_projections'] = Disclaimer(
            id='estimates_projections',
            title='🔮 Estimativas e Projeções',
            content='''Todas as estimativas e projeções são baseadas em premissas que podem não se materializar. 
            Fatores externos imprevisíveis podem afetar significativamente os resultados. Use estas informações 
            como ponto de partida, não como garantia de resultados.''',
            severity='info',
            category='projections',
            triggers=['estimativa', 'projeção', 'previsão', 'expectativa', 'cenário'],
            mandatory=False
        )
        
        return disclaimers
    
    def _load_sensitive_keywords(self) -> Dict[str, List[str]]:
        """Carrega palavras-chave sensíveis por categoria"""
        return {
            'financial': [
                'investimento', 'lucro', 'receita', 'roi', 'retorno', 'ações', 'fundos',
                'renda fixa', 'criptomoedas', 'bolsa', 'financiamento', 'empréstimo',
                'juros', 'inflação', 'câmbio', 'dólar', 'euro', 'bitcoin'
            ],
            'health': [
                'saúde', 'medicina', 'tratamento', 'cura', 'diagnóstico', 'sintomas',
                'doença', 'medicamento', 'terapia', 'clínica', 'hospital', 'médico',
                'enfermagem', 'fisioterapia', 'psicologia', 'nutrição'
            ],
            'legal': [
                'lei', 'legal', 'jurídico', 'contrato', 'direito', 'advogado',
                'processo', 'tribunal', 'juiz', 'sentença', 'recurso', 'apelação',
                'constituição', 'código civil', 'trabalhista', 'tributário'
            ],
            'regulatory': [
                'anvisa', 'cvm', 'bacen', 'anatel', 'aneel', 'ans', 'susep',
                'regulamentação', 'norma', 'portaria', 'resolução', 'instrução',
                'compliance', 'auditoria', 'fiscalização', 'licença', 'autorização'
            ]
        }
    
    def _load_regulatory_requirements(self) -> Dict[str, Dict]:
        """Carrega requisitos regulatórios por setor"""
        return {
            'financial_services': {
                'required_disclaimers': ['financial_projections', 'investment_advice'],
                'regulatory_body': 'CVM - Comissão de Valores Mobiliários',
                'key_regulations': ['Instrução CVM 539/2013', 'Lei 6.385/1976']
            },
            'healthcare': {
                'required_disclaimers': ['health_claims'],
                'regulatory_body': 'ANVISA - Agência Nacional de Vigilância Sanitária',
                'key_regulations': ['RDC 96/2008', 'Lei 9.782/1999']
            },
            'food_supplements': {
                'required_disclaimers': ['health_claims', 'regulatory_compliance'],
                'regulatory_body': 'ANVISA',
                'key_regulations': ['RDC 243/2018', 'IN 28/2018']
            },
            'legal_services': {
                'required_disclaimers': ['legal_advice'],
                'regulatory_body': 'OAB - Ordem dos Advogados do Brasil',
                'key_regulations': ['Estatuto da Advocacia', 'Código de Ética']
            }
        }
    
    def analyze_content(self, content: str, context: DisclaimerContext) -> List[str]:
        """Analisa conteúdo e retorna disclaimers aplicáveis"""
        applicable_disclaimers = []
        content_lower = content.lower()
        
        # Sempre adiciona disclaimer de IA se aplicável
        if context.ai_generated:
            applicable_disclaimers.append('ai_generated')
        
        # Verifica cada disclaimer
        for disclaimer_id, disclaimer in self.disclaimers.items():
            if disclaimer_id == 'ai_generated':  # Já tratado acima
                continue
            
            # Verifica se algum trigger está presente
            if disclaimer.triggers == ['*']:  # Aplicar sempre
                applicable_disclaimers.append(disclaimer_id)
            else:
                for trigger in disclaimer.triggers:
                    if trigger in content_lower:
                        applicable_disclaimers.append(disclaimer_id)
                        break
        
        # Adiciona disclaimers obrigatórios baseados no contexto
        if context.contains_financial_advice:
            applicable_disclaimers.extend(['financial_projections', 'investment_advice'])
        
        if context.contains_health_claims:
            applicable_disclaimers.append('health_claims')
        
        if context.contains_legal_advice:
            applicable_disclaimers.append('legal_advice')
        
        if context.contains_projections:
            applicable_disclaimers.append('estimates_projections')
        
        # Remove duplicatas mantendo ordem
        return list(dict.fromkeys(applicable_disclaimers))
    
    def detect_sensitive_content(self, content: str) -> Dict[str, List[str]]:
        """Detecta conteúdo sensível no texto"""
        content_lower = content.lower()
        detected = {}
        
        for category, keywords in self.sensitive_keywords.items():
            found_keywords = []
            for keyword in keywords:
                if keyword in content_lower:
                    found_keywords.append(keyword)
            
            if found_keywords:
                detected[category] = found_keywords
        
        return detected
    
    def generate_disclaimer_section(self, disclaimer_ids: List[str]) -> str:
        """Gera seção HTML de disclaimers"""
        if not disclaimer_ids:
            return ""
        
        html = ['<div class="disclaimers-section">']
        html.append('<h3>⚠️ Avisos Importantes</h3>')
        
        # Agrupa por severidade
        critical_disclaimers = []
        warning_disclaimers = []
        info_disclaimers = []
        
        for disclaimer_id in disclaimer_ids:
            if disclaimer_id in self.disclaimers:
                disclaimer = self.disclaimers[disclaimer_id]
                if disclaimer.severity == 'critical':
                    critical_disclaimers.append(disclaimer)
                elif disclaimer.severity == 'warning':
                    warning_disclaimers.append(disclaimer)
                else:
                    info_disclaimers.append(disclaimer)
        
        # Renderiza por ordem de severidade
        for disclaimers_group in [critical_disclaimers, warning_disclaimers, info_disclaimers]:
            for disclaimer in disclaimers_group:
                severity_class = f"disclaimer-{disclaimer.severity}"
                html.append(f'<div class="disclaimer-item {severity_class}">')
                html.append(f'<h4>{disclaimer.title}</h4>')
                html.append(f'<p>{disclaimer.content}</p>')
                html.append('</div>')
        
        html.append('</div>')
        return '\n'.join(html)
    
    def generate_regulatory_notice(self, industry: str) -> str:
        """Gera aviso regulatório específico da indústria"""
        if industry not in self.regulatory_requirements:
            return ""
        
        req = self.regulatory_requirements[industry]
        
        html = ['<div class="regulatory-notice">']
        html.append('<h4>📋 Informações Regulatórias</h4>')
        html.append(f'<p><strong>Órgão Regulador:</strong> {req["regulatory_body"]}</p>')
        html.append('<p><strong>Principais Regulamentações:</strong></p>')
        html.append('<ul>')
        for regulation in req['key_regulations']:
            html.append(f'<li>{regulation}</li>')
        html.append('</ul>')
        html.append('<p><em>Consulte sempre as fontes oficiais para informações atualizadas.</em></p>')
        html.append('</div>')
        
        return '\n'.join(html)
    
    def generate_validation_checklist(self, content_type: str, industry: str) -> str:
        """Gera checklist de validação recomendado"""
        checklists = {
            'financial': [
                "Verificar dados financeiros com fontes oficiais",
                "Consultar contador ou consultor financeiro",
                "Validar projeções com dados históricos",
                "Considerar cenários de risco",
                "Revisar aspectos tributários"
            ],
            'health': [
                "Consultar profissional de saúde qualificado",
                "Verificar informações com fontes médicas confiáveis",
                "Considerar contraindicações e efeitos colaterais",
                "Validar com órgãos reguladores (ANVISA)",
                "Buscar segunda opinião médica se necessário"
            ],
            'legal': [
                "Consultar advogado especializado",
                "Verificar legislação atualizada",
                "Considerar jurisprudência relevante",
                "Validar com órgãos competentes",
                "Revisar contratos e documentos"
            ],
            'marketing': [
                "Verificar claims com dados reais",
                "Validar com equipe de compliance",
                "Considerar regulamentações de publicidade",
                "Testar mensagens com público-alvo",
                "Revisar aspectos éticos"
            ]
        }
        
        checklist_items = checklists.get(content_type, [
            "Verificar informações com fontes primárias",
            "Consultar especialistas da área",
            "Validar dados críticos independentemente",
            "Considerar riscos e limitações",
            "Revisar aspectos regulatórios"
        ])
        
        html = ['<div class="validation-checklist">']
        html.append('<h4>✅ Checklist de Validação Recomendado</h4>')
        html.append('<ul class="checklist">')
        
        for item in checklist_items:
            html.append(f'<li><input type="checkbox"> {item}</li>')
        
        html.append('</ul>')
        html.append('</div>')
        
        return '\n'.join(html)
    
    def generate_disclaimers_css(self) -> str:
        """Gera CSS para estilização dos disclaimers"""
        return """
        <style>
        .disclaimers-section {
            margin: 30px 0;
            padding: 25px;
            background-color: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .disclaimers-section h3 {
            color: #856404;
            margin-bottom: 20px;
            font-size: 1.3em;
            text-align: center;
        }
        
        .disclaimer-item {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 8px;
            border-left: 5px solid #6c757d;
        }
        
        .disclaimer-critical {
            background-color: #f8d7da;
            border-left-color: #dc3545;
            border: 2px solid #dc3545;
        }
        
        .disclaimer-warning {
            background-color: #fff3cd;
            border-left-color: #ffc107;
        }
        
        .disclaimer-info {
            background-color: #d1ecf1;
            border-left-color: #17a2b8;
        }
        
        .disclaimer-item h4 {
            margin-bottom: 10px;
            color: #333;
            font-size: 1.1em;
        }
        
        .disclaimer-item p {
            line-height: 1.6;
            margin-bottom: 0;
            color: #555;
        }
        
        .regulatory-notice {
            margin: 20px 0;
            padding: 20px;
            background-color: #e7f3ff;
            border-left: 4px solid #007bff;
            border-radius: 5px;
        }
        
        .regulatory-notice h4 {
            color: #0056b3;
            margin-bottom: 15px;
        }
        
        .regulatory-notice ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        
        .validation-checklist {
            margin: 20px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-left: 4px solid #28a745;
            border-radius: 5px;
        }
        
        .validation-checklist h4 {
            color: #155724;
            margin-bottom: 15px;
        }
        
        .checklist {
            list-style: none;
            padding-left: 0;
        }
        
        .checklist li {
            margin-bottom: 10px;
            padding: 8px;
            background-color: white;
            border-radius: 3px;
            border-left: 3px solid #28a745;
        }
        
        .checklist input[type="checkbox"] {
            margin-right: 10px;
            transform: scale(1.2);
        }
        
        .sensitive-content-alert {
            background-color: #f8d7da;
            border: 2px solid #dc3545;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(220, 53, 69, 0); }
            100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }
        }
        
        .disclaimer-mandatory {
            border: 3px solid #dc3545 !important;
            background-color: #f8d7da !important;
            font-weight: bold;
        }
        
        .disclaimer-timestamp {
            font-size: 0.8em;
            color: #666;
            text-align: right;
            margin-top: 10px;
            font-style: italic;
        }
        </style>
        """
    
    def create_context_from_content(self, content: str, industry: str = "general") -> DisclaimerContext:
        """Cria contexto automaticamente baseado no conteúdo"""
        content_lower = content.lower()
        
        # Detecta tipo de conteúdo
        content_type = "general"
        if any(kw in content_lower for kw in self.sensitive_keywords['financial']):
            content_type = "financial"
        elif any(kw in content_lower for kw in self.sensitive_keywords['health']):
            content_type = "health"
        elif any(kw in content_lower for kw in self.sensitive_keywords['legal']):
            content_type = "legal"
        
        # Detecta características específicas
        contains_projections = any(word in content_lower for word in 
                                 ['projeção', 'estimativa', 'previsão', 'cenário', 'expectativa'])
        
        contains_financial_advice = any(word in content_lower for word in 
                                      ['investir', 'comprar', 'vender', 'aplicar', 'recomendo'])
        
        contains_health_claims = any(word in content_lower for word in 
                                   ['cura', 'trata', 'previne', 'melhora', 'reduz'])
        
        contains_legal_advice = any(word in content_lower for word in 
                                  ['deve', 'obrigatório', 'ilegal', 'permitido', 'proibido'])
        
        return DisclaimerContext(
            content_type=content_type,
            industry=industry,
            contains_projections=contains_projections,
            contains_financial_advice=contains_financial_advice,
            contains_health_claims=contains_health_claims,
            contains_legal_advice=contains_legal_advice,
            ai_generated=True
        )
    
    def get_disclaimer_summary(self, disclaimer_ids: List[str]) -> Dict[str, Any]:
        """Retorna resumo dos disclaimers aplicados"""
        if not disclaimer_ids:
            return {}
        
        severity_count = {'critical': 0, 'warning': 0, 'info': 0}
        categories = set()
        mandatory_count = 0
        
        for disclaimer_id in disclaimer_ids:
            if disclaimer_id in self.disclaimers:
                disclaimer = self.disclaimers[disclaimer_id]
                severity_count[disclaimer.severity] += 1
                categories.add(disclaimer.category)
                if disclaimer.mandatory:
                    mandatory_count += 1
        
        return {
            'total_disclaimers': len(disclaimer_ids),
            'severity_distribution': severity_count,
            'categories': list(categories),
            'mandatory_disclaimers': mandatory_count,
            'risk_level': 'high' if severity_count['critical'] > 0 else 
                         'medium' if severity_count['warning'] > 0 else 'low'
        }

# Instância global do gerenciador
disclaimer_manager = DisclaimerManager()