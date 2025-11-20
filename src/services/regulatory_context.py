"""
Sistema de Contexto Regulatório e Compliance
Implementa base de dados de regulamentações e alertas de compliance
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import re

@dataclass
class Regulation:
    """Estrutura de uma regulamentação"""
    id: str
    name: str
    authority: str  # Órgão regulador
    sector: str
    description: str
    key_requirements: List[str]
    penalties: List[str]
    compliance_checklist: List[str]
    last_updated: str
    url: Optional[str] = None
    status: str = "active"  # active, proposed, revoked
    
@dataclass
class ComplianceAlert:
    """Alerta de compliance"""
    regulation_id: str
    alert_type: str  # mandatory, recommended, warning
    message: str
    action_required: str
    deadline: Optional[str] = None
    priority: str = "medium"  # low, medium, high, critical

@dataclass
class RegulatoryContext:
    """Contexto regulatório completo"""
    applicable_regulations: List[Regulation]
    compliance_alerts: List[ComplianceAlert]
    sector_overview: Dict[str, Any]
    compliance_score: float
    recommendations: List[str]

class RegulatoryContextManager:
    """Sistema principal de contexto regulatório"""
    
    def __init__(self):
        self.regulations_database = self._load_regulations_database()
        self.sector_mappings = self._load_sector_mappings()
        self.compliance_templates = self._load_compliance_templates()
        
    def _load_regulations_database(self) -> Dict[str, Dict]:
        """Carrega base de dados de regulamentações por setor"""
        return {
            'financial_services': {
                'cvm_539': {
                    'name': 'Instrução CVM 539/2013',
                    'authority': 'CVM - Comissão de Valores Mobiliários',
                    'description': 'Dispõe sobre o dever de verificação da adequação dos produtos, serviços e operações ao perfil do cliente',
                    'key_requirements': [
                        'Verificação do perfil de risco do investidor',
                        'Adequação de produtos ao perfil',
                        'Documentação das recomendações',
                        'Treinamento de funcionários'
                    ],
                    'penalties': [
                        'Multa de R$ 1.000 a R$ 500.000',
                        'Suspensão de atividades',
                        'Inabilitação temporária'
                    ],
                    'compliance_checklist': [
                        'Implementar questionário de suitability',
                        'Treinar equipe comercial',
                        'Documentar todas as recomendações',
                        'Revisar produtos oferecidos'
                    ],
                    'url': 'https://conteudo.cvm.gov.br/legislacao/instrucoes/inst539.html'
                },
                'lei_6385': {
                    'name': 'Lei 6.385/1976 - Lei do Mercado de Capitais',
                    'authority': 'CVM - Comissão de Valores Mobiliários',
                    'description': 'Dispõe sobre o mercado de valores mobiliários e cria a CVM',
                    'key_requirements': [
                        'Registro de ofertas públicas',
                        'Divulgação de informações',
                        'Proteção aos investidores',
                        'Transparência nas operações'
                    ],
                    'penalties': [
                        'Multa até R$ 50 milhões',
                        'Proibição de exercer atividades',
                        'Responsabilização civil e criminal'
                    ],
                    'compliance_checklist': [
                        'Registrar ofertas na CVM',
                        'Publicar demonstrações financeiras',
                        'Manter controles internos',
                        'Reportar fatos relevantes'
                    ],
                    'url': 'http://www.planalto.gov.br/ccivil_03/leis/l6385.htm'
                }
            },
            'healthcare': {
                'rdc_96_2008': {
                    'name': 'RDC 96/2008 - Propaganda de Medicamentos',
                    'authority': 'ANVISA - Agência Nacional de Vigilância Sanitária',
                    'description': 'Dispõe sobre a propaganda, publicidade, informação e outras práticas cujo objetivo seja a divulgação ou promoção comercial de medicamentos',
                    'key_requirements': [
                        'Aprovação prévia da propaganda',
                        'Informações obrigatórias',
                        'Restrições de conteúdo',
                        'Identificação clara do produto'
                    ],
                    'penalties': [
                        'Advertência',
                        'Multa de R$ 2.000 a R$ 1.500.000',
                        'Suspensão da propaganda',
                        'Cancelamento do registro'
                    ],
                    'compliance_checklist': [
                        'Submeter propaganda à ANVISA',
                        'Incluir informações obrigatórias',
                        'Evitar claims não comprovados',
                        'Manter documentação técnica'
                    ],
                    'url': 'https://bvsms.saude.gov.br/bvs/saudelegis/anvisa/2008/rdc0096_17_12_2008.html'
                },
                'lei_9782': {
                    'name': 'Lei 9.782/1999 - Lei da ANVISA',
                    'authority': 'ANVISA - Agência Nacional de Vigilância Sanitária',
                    'description': 'Define o Sistema Nacional de Vigilância Sanitária e cria a ANVISA',
                    'key_requirements': [
                        'Registro de produtos',
                        'Boas práticas de fabricação',
                        'Controle de qualidade',
                        'Farmacovigilância'
                    ],
                    'penalties': [
                        'Advertência',
                        'Multa até R$ 15 milhões',
                        'Interdição de estabelecimento',
                        'Cancelamento de licença'
                    ],
                    'compliance_checklist': [
                        'Registrar produtos na ANVISA',
                        'Implementar BPF',
                        'Manter controle de qualidade',
                        'Reportar eventos adversos'
                    ],
                    'url': 'http://www.planalto.gov.br/ccivil_03/leis/l9782.htm'
                }
            },
            'food_supplements': {
                'rdc_243_2018': {
                    'name': 'RDC 243/2018 - Suplementos Alimentares',
                    'authority': 'ANVISA - Agência Nacional de Vigilância Sanitária',
                    'description': 'Dispõe sobre os requisitos sanitários dos suplementos alimentares',
                    'key_requirements': [
                        'Registro ou notificação',
                        'Rotulagem específica',
                        'Limites de nutrientes',
                        'Claims permitidos'
                    ],
                    'penalties': [
                        'Advertência',
                        'Multa de R$ 2.000 a R$ 1.500.000',
                        'Apreensão do produto',
                        'Interdição do estabelecimento'
                    ],
                    'compliance_checklist': [
                        'Notificar produto na ANVISA',
                        'Adequar rotulagem',
                        'Respeitar limites nutricionais',
                        'Validar claims de saúde'
                    ],
                    'url': 'https://bvsms.saude.gov.br/bvs/saudelegis/anvisa/2018/rdc0243_26_07_2018.pdf'
                }
            },
            'digital_marketing': {
                'lgpd': {
                    'name': 'LGPD - Lei Geral de Proteção de Dados',
                    'authority': 'ANPD - Autoridade Nacional de Proteção de Dados',
                    'description': 'Dispõe sobre o tratamento de dados pessoais',
                    'key_requirements': [
                        'Consentimento para coleta de dados',
                        'Finalidade específica',
                        'Direitos do titular',
                        'Segurança dos dados'
                    ],
                    'penalties': [
                        'Advertência',
                        'Multa até R$ 50 milhões',
                        'Bloqueio dos dados',
                        'Eliminação dos dados'
                    ],
                    'compliance_checklist': [
                        'Implementar política de privacidade',
                        'Obter consentimento explícito',
                        'Nomear DPO se necessário',
                        'Implementar medidas de segurança'
                    ],
                    'url': 'http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm'
                },
                'cdc': {
                    'name': 'CDC - Código de Defesa do Consumidor',
                    'authority': 'SENACON - Secretaria Nacional do Consumidor',
                    'description': 'Dispõe sobre a proteção do consumidor',
                    'key_requirements': [
                        'Informação clara e adequada',
                        'Publicidade não enganosa',
                        'Direito de arrependimento',
                        'Garantia de produtos'
                    ],
                    'penalties': [
                        'Multa de R$ 200 a R$ 3 milhões',
                        'Apreensão do produto',
                        'Suspensão de atividades',
                        'Revogação de licença'
                    ],
                    'compliance_checklist': [
                        'Fornecer informações claras',
                        'Evitar publicidade enganosa',
                        'Respeitar direito de arrependimento',
                        'Oferecer garantia adequada'
                    ],
                    'url': 'http://www.planalto.gov.br/ccivil_03/leis/l8078.htm'
                }
            },
            'e_commerce': {
                'decreto_7962': {
                    'name': 'Decreto 7.962/2013 - Comércio Eletrônico',
                    'authority': 'SENACON - Secretaria Nacional do Consumidor',
                    'description': 'Regulamenta o CDC para dispor sobre a contratação no comércio eletrônico',
                    'key_requirements': [
                        'Informações claras sobre produto',
                        'Dados do fornecedor',
                        'Condições de compra',
                        'Atendimento ao consumidor'
                    ],
                    'penalties': [
                        'Aplicação das penalidades do CDC',
                        'Multa até R$ 11 milhões',
                        'Suspensão de atividades'
                    ],
                    'compliance_checklist': [
                        'Disponibilizar informações do fornecedor',
                        'Detalhar características do produto',
                        'Informar condições de entrega',
                        'Manter canal de atendimento'
                    ],
                    'url': 'http://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/decreto/d7962.htm'
                }
            },
            'general_business': {
                'lei_complementar_123': {
                    'name': 'Lei Complementar 123/2006 - Simples Nacional',
                    'authority': 'Receita Federal do Brasil',
                    'description': 'Institui o Estatuto Nacional da Microempresa e da Empresa de Pequeno Porte',
                    'key_requirements': [
                        'Enquadramento correto',
                        'Limite de faturamento',
                        'Obrigações acessórias',
                        'Recolhimento unificado'
                    ],
                    'penalties': [
                        'Exclusão do Simples Nacional',
                        'Multa por desenquadramento',
                        'Cobrança retroativa de impostos'
                    ],
                    'compliance_checklist': [
                        'Verificar enquadramento anual',
                        'Controlar limite de faturamento',
                        'Cumprir obrigações acessórias',
                        'Recolher impostos em dia'
                    ],
                    'url': 'http://www.planalto.gov.br/ccivil_03/leis/lcp/lcp123.htm'
                }
            }
        }
    
    def _load_sector_mappings(self) -> Dict[str, List[str]]:
        """Carrega mapeamento de palavras-chave para setores"""
        return {
            'financial_services': [
                'investimento', 'financeiro', 'banco', 'crédito', 'empréstimo',
                'financiamento', 'seguro', 'previdência', 'corretora', 'cvm'
            ],
            'healthcare': [
                'saúde', 'medicamento', 'farmácia', 'hospital', 'clínica',
                'médico', 'tratamento', 'terapia', 'diagnóstico', 'anvisa'
            ],
            'food_supplements': [
                'suplemento', 'vitamina', 'nutricional', 'alimentar',
                'proteína', 'whey', 'creatina', 'suplementação'
            ],
            'digital_marketing': [
                'marketing digital', 'publicidade online', 'dados pessoais',
                'cookies', 'newsletter', 'email marketing', 'redes sociais'
            ],
            'e_commerce': [
                'loja virtual', 'e-commerce', 'venda online', 'marketplace',
                'entrega', 'frete', 'pagamento online', 'carrinho'
            ],
            'general_business': [
                'empresa', 'negócio', 'empreendimento', 'startup',
                'mei', 'microempresa', 'pequena empresa'
            ]
        }
    
    def _load_compliance_templates(self) -> Dict[str, Dict]:
        """Carrega templates de compliance por setor"""
        return {
            'financial_services': {
                'mandatory_documents': [
                    'Política de Suitability',
                    'Manual de Compliance',
                    'Código de Ética',
                    'Política de Prevenção à Lavagem de Dinheiro'
                ],
                'required_training': [
                    'Certificação ANBIMA',
                    'Treinamento em Suitability',
                    'Prevenção à Lavagem de Dinheiro',
                    'Código de Ética'
                ],
                'periodic_obligations': [
                    'Relatório de Compliance (mensal)',
                    'Auditoria interna (anual)',
                    'Atualização de políticas (anual)',
                    'Treinamento de funcionários (semestral)'
                ]
            },
            'healthcare': {
                'mandatory_documents': [
                    'Autorização de Funcionamento',
                    'Licença Sanitária',
                    'Manual de Boas Práticas',
                    'Plano de Gerenciamento de Resíduos'
                ],
                'required_training': [
                    'Boas Práticas de Fabricação',
                    'Farmacovigilância',
                    'Controle de Qualidade',
                    'Segurança do Trabalho'
                ],
                'periodic_obligations': [
                    'Renovação de licenças (anual)',
                    'Relatório de farmacovigilância (trimestral)',
                    'Auditoria de qualidade (semestral)',
                    'Atualização de procedimentos (anual)'
                ]
            }
        }
    
    def analyze_regulatory_context(self, content: str, industry: str = None) -> RegulatoryContext:
        """Analisa contexto regulatório baseado no conteúdo"""
        content_lower = content.lower()
        
        # Identifica setores aplicáveis
        applicable_sectors = self._identify_sectors(content_lower, industry)
        
        # Coleta regulamentações aplicáveis
        applicable_regulations = []
        for sector in applicable_sectors:
            if sector in self.regulations_database:
                for reg_id, reg_data in self.regulations_database[sector].items():
                    regulation = Regulation(
                        id=reg_id,
                        name=reg_data['name'],
                        authority=reg_data['authority'],
                        sector=sector,
                        description=reg_data['description'],
                        key_requirements=reg_data['key_requirements'],
                        penalties=reg_data['penalties'],
                        compliance_checklist=reg_data['compliance_checklist'],
                        last_updated=datetime.now().strftime('%Y-%m-%d'),
                        url=reg_data.get('url')
                    )
                    applicable_regulations.append(regulation)
        
        # Gera alertas de compliance
        compliance_alerts = self._generate_compliance_alerts(content_lower, applicable_regulations)
        
        # Cria overview do setor
        sector_overview = self._create_sector_overview(applicable_sectors)
        
        # Calcula score de compliance
        compliance_score = self._calculate_compliance_score(compliance_alerts)
        
        # Gera recomendações
        recommendations = self._generate_regulatory_recommendations(
            applicable_regulations, compliance_alerts, applicable_sectors
        )
        
        return RegulatoryContext(
            applicable_regulations=applicable_regulations,
            compliance_alerts=compliance_alerts,
            sector_overview=sector_overview,
            compliance_score=compliance_score,
            recommendations=recommendations
        )
    
    def _identify_sectors(self, content: str, industry: str = None) -> List[str]:
        """Identifica setores aplicáveis baseado no conteúdo"""
        sectors = []
        
        # Se indústria foi especificada, adiciona diretamente
        if industry and industry in self.sector_mappings:
            sectors.append(industry)
        
        # Identifica setores baseado em palavras-chave
        for sector, keywords in self.sector_mappings.items():
            if sector not in sectors:  # Evita duplicatas
                if any(keyword in content for keyword in keywords):
                    sectors.append(sector)
        
        # Sempre inclui contexto geral de negócios
        if 'general_business' not in sectors:
            sectors.append('general_business')
        
        return sectors
    
    def _generate_compliance_alerts(self, content: str, regulations: List[Regulation]) -> List[ComplianceAlert]:
        """Gera alertas de compliance baseado no conteúdo"""
        alerts = []
        
        # Palavras-chave que geram alertas específicos
        alert_triggers = {
            'investimento': {
                'regulation_id': 'cvm_539',
                'message': 'Conteúdo sobre investimentos detectado - verificar adequação ao perfil do investidor',
                'action_required': 'Implementar processo de suitability',
                'priority': 'high'
            },
            'medicamento': {
                'regulation_id': 'rdc_96_2008',
                'message': 'Propaganda de medicamentos detectada - aprovação prévia necessária',
                'action_required': 'Submeter propaganda à ANVISA',
                'priority': 'critical'
            },
            'suplemento': {
                'regulation_id': 'rdc_243_2018',
                'message': 'Conteúdo sobre suplementos - verificar claims de saúde',
                'action_required': 'Validar alegações com base científica',
                'priority': 'high'
            },
            'dados pessoais': {
                'regulation_id': 'lgpd',
                'message': 'Tratamento de dados pessoais identificado - verificar conformidade LGPD',
                'action_required': 'Implementar política de privacidade',
                'priority': 'high'
            },
            'venda online': {
                'regulation_id': 'decreto_7962',
                'message': 'Comércio eletrônico detectado - verificar informações obrigatórias',
                'action_required': 'Adequar informações do e-commerce',
                'priority': 'medium'
            }
        }
        
        for trigger, alert_data in alert_triggers.items():
            if trigger in content:
                # Verifica se a regulamentação está nas aplicáveis
                if any(reg.id == alert_data['regulation_id'] for reg in regulations):
                    alert = ComplianceAlert(
                        regulation_id=alert_data['regulation_id'],
                        alert_type='mandatory',
                        message=alert_data['message'],
                        action_required=alert_data['action_required'],
                        priority=alert_data['priority']
                    )
                    alerts.append(alert)
        
        # Alertas gerais para todas as regulamentações aplicáveis
        for regulation in regulations:
            if regulation.sector == 'financial_services':
                alerts.append(ComplianceAlert(
                    regulation_id=regulation.id,
                    alert_type='recommended',
                    message=f'Verificar conformidade com {regulation.name}',
                    action_required='Revisar checklist de compliance',
                    priority='medium'
                ))
        
        return alerts
    
    def _create_sector_overview(self, sectors: List[str]) -> Dict[str, Any]:
        """Cria overview dos setores identificados"""
        overview = {
            'identified_sectors': sectors,
            'regulatory_complexity': self._assess_regulatory_complexity(sectors),
            'main_authorities': self._get_main_authorities(sectors),
            'compliance_priority': self._assess_compliance_priority(sectors)
        }
        return overview
    
    def _assess_regulatory_complexity(self, sectors: List[str]) -> str:
        """Avalia complexidade regulatória"""
        high_complexity_sectors = ['financial_services', 'healthcare', 'food_supplements']
        
        if any(sector in high_complexity_sectors for sector in sectors):
            return 'high'
        elif len(sectors) > 2:
            return 'medium'
        else:
            return 'low'
    
    def _get_main_authorities(self, sectors: List[str]) -> List[str]:
        """Identifica principais autoridades reguladoras"""
        authorities = set()
        
        for sector in sectors:
            if sector in self.regulations_database:
                for reg_data in self.regulations_database[sector].values():
                    authorities.add(reg_data['authority'])
        
        return list(authorities)
    
    def _assess_compliance_priority(self, sectors: List[str]) -> str:
        """Avalia prioridade de compliance"""
        critical_sectors = ['financial_services', 'healthcare']
        high_priority_sectors = ['food_supplements', 'digital_marketing']
        
        if any(sector in critical_sectors for sector in sectors):
            return 'critical'
        elif any(sector in high_priority_sectors for sector in sectors):
            return 'high'
        else:
            return 'medium'
    
    def _calculate_compliance_score(self, alerts: List[ComplianceAlert]) -> float:
        """Calcula score de compliance (0-1, onde 1 é melhor)"""
        if not alerts:
            return 1.0
        
        # Pontuação baseada na prioridade dos alertas
        priority_weights = {'critical': 0.4, 'high': 0.3, 'medium': 0.2, 'low': 0.1}
        
        total_weight = 0
        penalty = 0
        
        for alert in alerts:
            weight = priority_weights.get(alert.priority, 0.1)
            total_weight += weight
            penalty += weight
        
        # Score inversamente proporcional aos alertas
        score = max(0.0, 1.0 - (penalty / max(total_weight, 1.0)))
        return score
    
    def _generate_regulatory_recommendations(self, regulations: List[Regulation], 
                                           alerts: List[ComplianceAlert], 
                                           sectors: List[str]) -> List[str]:
        """Gera recomendações regulatórias"""
        recommendations = []
        
        # Recomendações baseadas em alertas críticos
        critical_alerts = [a for a in alerts if a.priority == 'critical']
        if critical_alerts:
            recommendations.append("🚨 AÇÃO IMEDIATA: Resolver alertas críticos de compliance")
            recommendations.append("Consultar advogado especializado imediatamente")
        
        # Recomendações por setor
        if 'financial_services' in sectors:
            recommendations.extend([
                "Implementar política de suitability para produtos financeiros",
                "Estabelecer controles internos rigorosos",
                "Manter documentação de todas as recomendações"
            ])
        
        if 'healthcare' in sectors:
            recommendations.extend([
                "Validar todas as alegações de saúde com base científica",
                "Submeter propaganda à aprovação da ANVISA",
                "Implementar sistema de farmacovigilância"
            ])
        
        if 'digital_marketing' in sectors:
            recommendations.extend([
                "Implementar política de privacidade conforme LGPD",
                "Obter consentimento explícito para coleta de dados",
                "Estabelecer procedimentos de segurança de dados"
            ])
        
        # Recomendações gerais
        recommendations.extend([
            "Estabelecer programa de compliance estruturado",
            "Realizar treinamentos regulares da equipe",
            "Manter monitoramento contínuo de mudanças regulatórias",
            "Documentar todos os processos de compliance",
            "Realizar auditorias internas periódicas"
        ])
        
        return recommendations
    
    def generate_regulatory_html(self, context: RegulatoryContext) -> str:
        """Gera HTML do contexto regulatório"""
        html = ['<div class="regulatory-context">']
        html.append('<h3>📋 Contexto Regulatório e Compliance</h3>')
        
        # Score de compliance
        score_class = self._get_compliance_score_class(context.compliance_score)
        html.append(f'<div class="compliance-score {score_class}">')
        html.append(f'<h4>Score de Compliance: {context.compliance_score:.2f}</h4>')
        html.append(f'<p>Nível: {self._get_compliance_level_text(context.compliance_score)}</p>')
        html.append('</div>')
        
        # Overview do setor
        html.append('<div class="sector-overview">')
        html.append('<h4>📊 Overview Regulatório</h4>')
        html.append(f'<p><strong>Setores Identificados:</strong> {", ".join(context.sector_overview["identified_sectors"])}</p>')
        html.append(f'<p><strong>Complexidade Regulatória:</strong> {context.sector_overview["regulatory_complexity"].upper()}</p>')
        html.append(f'<p><strong>Prioridade de Compliance:</strong> {context.sector_overview["compliance_priority"].upper()}</p>')
        html.append('</div>')
        
        # Alertas de compliance
        if context.compliance_alerts:
            html.append('<div class="compliance-alerts">')
            html.append('<h4>⚠️ Alertas de Compliance</h4>')
            
            for alert in context.compliance_alerts:
                priority_class = f"alert-{alert.priority}"
                html.append(f'<div class="compliance-alert {priority_class}">')
                html.append(f'<h5>{alert.message}</h5>')
                html.append(f'<p><strong>Ação Necessária:</strong> {alert.action_required}</p>')
                html.append(f'<p><strong>Prioridade:</strong> {alert.priority.upper()}</p>')
                html.append('</div>')
            
            html.append('</div>')
        
        # Regulamentações aplicáveis
        if context.applicable_regulations:
            html.append('<div class="applicable-regulations">')
            html.append('<h4>📜 Regulamentações Aplicáveis</h4>')
            
            for regulation in context.applicable_regulations[:5]:  # Top 5
                html.append('<div class="regulation-item">')
                html.append(f'<h5>{regulation.name}</h5>')
                html.append(f'<p><strong>Órgão:</strong> {regulation.authority}</p>')
                html.append(f'<p><strong>Setor:</strong> {regulation.sector.replace("_", " ").title()}</p>')
                html.append(f'<p>{regulation.description}</p>')
                
                if regulation.url:
                    html.append(f'<p><a href="{regulation.url}" target="_blank">🔗 Acessar regulamentação</a></p>')
                
                # Checklist de compliance
                if regulation.compliance_checklist:
                    html.append('<div class="compliance-checklist">')
                    html.append('<strong>Checklist de Compliance:</strong>')
                    html.append('<ul>')
                    for item in regulation.compliance_checklist[:3]:
                        html.append(f'<li>{item}</li>')
                    html.append('</ul>')
                    html.append('</div>')
                
                html.append('</div>')
            
            html.append('</div>')
        
        # Principais autoridades
        if context.sector_overview['main_authorities']:
            html.append('<div class="main-authorities">')
            html.append('<h4>🏛️ Principais Órgãos Reguladores</h4>')
            html.append('<div class="authorities-grid">')
            
            for authority in context.sector_overview['main_authorities']:
                html.append(f'<div class="authority-tag">{authority}</div>')
            
            html.append('</div>')
            html.append('</div>')
        
        # Recomendações
        html.append('<div class="regulatory-recommendations">')
        html.append('<h4>💡 Recomendações de Compliance</h4>')
        html.append('<ul class="recommendations-list">')
        
        for recommendation in context.recommendations:
            html.append(f'<li>{recommendation}</li>')
        
        html.append('</ul>')
        html.append('</div>')
        
        html.append('</div>')
        
        return '\n'.join(html)
    
    def _get_compliance_score_class(self, score: float) -> str:
        """Retorna classe CSS baseada no score de compliance"""
        if score >= 0.8:
            return 'compliance-excellent'
        elif score >= 0.6:
            return 'compliance-good'
        elif score >= 0.4:
            return 'compliance-fair'
        else:
            return 'compliance-poor'
    
    def _get_compliance_level_text(self, score: float) -> str:
        """Retorna texto do nível de compliance"""
        if score >= 0.8:
            return 'EXCELENTE'
        elif score >= 0.6:
            return 'BOM'
        elif score >= 0.4:
            return 'REGULAR'
        else:
            return 'INADEQUADO'
    
    def generate_regulatory_css(self) -> str:
        """Gera CSS para visualização do contexto regulatório"""
        return """
        <style>
        .regulatory-context {
            margin: 30px 0;
            padding: 25px;
            background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
            border-radius: 12px;
            border-left: 5px solid #007bff;
        }
        
        .compliance-score {
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 25px;
            font-weight: bold;
        }
        
        .compliance-excellent {
            background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
            border: 2px solid #38a169;
            color: #22543d;
        }
        
        .compliance-good {
            background: linear-gradient(135deg, #fefcbf 0%, #f6e05e 100%);
            border: 2px solid #d69e2e;
            color: #744210;
        }
        
        .compliance-fair {
            background: linear-gradient(135deg, #feebc8 0%, #fbd38d 100%);
            border: 2px solid #dd6b20;
            color: #7b341e;
        }
        
        .compliance-poor {
            background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
            border: 2px solid #e53e3e;
            color: #742a2a;
        }
        
        .sector-overview {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .compliance-alerts {
            margin-bottom: 25px;
        }
        
        .compliance-alert {
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 5px solid;
        }
        
        .compliance-alert.alert-critical {
            background-color: #fed7d7;
            border-left-color: #e53e3e;
        }
        
        .compliance-alert.alert-high {
            background-color: #feebc8;
            border-left-color: #dd6b20;
        }
        
        .compliance-alert.alert-medium {
            background-color: #fefcbf;
            border-left-color: #d69e2e;
        }
        
        .compliance-alert.alert-low {
            background-color: #c6f6d5;
            border-left-color: #38a169;
        }
        
        .applicable-regulations {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .regulation-item {
            padding: 15px;
            margin-bottom: 20px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            background-color: #f8f9fa;
        }
        
        .regulation-item h5 {
            color: #2d3748;
            margin-bottom: 10px;
        }
        
        .compliance-checklist {
            margin-top: 15px;
            padding: 10px;
            background-color: rgba(0,123,255,0.1);
            border-radius: 5px;
        }
        
        .compliance-checklist ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        
        .main-authorities {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .authorities-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        
        .authority-tag {
            padding: 8px 15px;
            background-color: #007bff;
            color: white;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 500;
        }
        
        .regulatory-recommendations {
            background-color: #e7f3ff;
            padding: 20px;
            border-left: 4px solid #007bff;
            border-radius: 8px;
        }
        
        .recommendations-list {
            margin: 15px 0;
            padding-left: 20px;
        }
        
        .recommendations-list li {
            margin-bottom: 8px;
            line-height: 1.5;
        }
        
        .regulation-item a {
            color: #007bff;
            text-decoration: none;
        }
        
        .regulation-item a:hover {
            text-decoration: underline;
        }
        </style>
        """
    
    def export_regulatory_context_json(self, context: RegulatoryContext) -> str:
        """Exporta contexto regulatório em JSON"""
        data = {
            'applicable_regulations': [asdict(reg) for reg in context.applicable_regulations],
            'compliance_alerts': [asdict(alert) for alert in context.compliance_alerts],
            'sector_overview': context.sector_overview,
            'compliance_score': context.compliance_score,
            'recommendations': context.recommendations,
            'export_date': datetime.now().isoformat()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

# Instância global do gerenciador
regulatory_context_manager = RegulatoryContextManager()