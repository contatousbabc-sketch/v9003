#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV40 Enhanced - Analisador de Concorrência Aprimorado
Sistema de análise de concorrentes reais com base de dados pré-definida
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class EnhancedCompetitorAnalyzer:
    """Analisador de concorrência com base de dados de empresas reais"""
    
    def __init__(self):
        """Inicializa o analisador com base de dados de concorrentes"""
        self.competitor_database = self._initialize_competitor_database()
        self.industry_keywords = self._initialize_industry_keywords()
        
    def _initialize_competitor_database(self) -> Dict[str, List[Dict]]:
        """Inicializa base de dados com concorrentes reais por setor"""
        return {
            'marketing_digital': [
                {
                    'name': 'RD Station',
                    'type': 'empresa',
                    'website': 'https://www.rdstation.com',
                    'description': 'Plataforma de automação de marketing e vendas líder no Brasil',
                    'size': 'grande',
                    'location': 'Brasil',
                    'specialties': ['automação de marketing', 'CRM', 'lead generation'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/rd-station',
                        'youtube': 'https://youtube.com/c/RDStation',
                        'instagram': 'https://instagram.com/rdstation'
                    },
                    'metrics': {
                        'employees': '1000+',
                        'funding': 'Series C',
                        'market_share': 'Alto'
                    }
                },
                {
                    'name': 'Hotmart',
                    'type': 'empresa',
                    'website': 'https://www.hotmart.com',
                    'description': 'Plataforma global de produtos digitais e educação online',
                    'size': 'grande',
                    'location': 'Brasil/Global',
                    'specialties': ['produtos digitais', 'educação online', 'afiliados'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/hotmart',
                        'youtube': 'https://youtube.com/c/HotmartOficial',
                        'instagram': 'https://instagram.com/hotmart'
                    },
                    'metrics': {
                        'employees': '2000+',
                        'funding': 'Unicórnio',
                        'market_share': 'Muito Alto'
                    }
                },
                {
                    'name': 'Erico Rocha',
                    'type': 'influencer',
                    'website': 'https://www.ericorocha.com.br',
                    'description': 'Expert em marketing digital e empreendedorismo online',
                    'size': 'individual',
                    'location': 'Brasil',
                    'specialties': ['marketing digital', 'vendas online', 'mentorias'],
                    'social_media': {
                        'youtube': 'https://youtube.com/c/EricoRocha',
                        'instagram': 'https://instagram.com/ericorocha',
                        'linkedin': 'https://linkedin.com/in/ericorocha'
                    },
                    'metrics': {
                        'followers': '1M+',
                        'engagement': 'Alto',
                        'influence': 'Nacional'
                    }
                },
                {
                    'name': 'Alex Vargas',
                    'type': 'influencer',
                    'website': 'https://www.alexvargas.com.br',
                    'description': 'Especialista em copywriting e vendas online',
                    'size': 'individual',
                    'location': 'Brasil',
                    'specialties': ['copywriting', 'vendas', 'persuasão'],
                    'social_media': {
                        'youtube': 'https://youtube.com/c/AlexVargas',
                        'instagram': 'https://instagram.com/alexvargas',
                        'facebook': 'https://facebook.com/alexvargasoficial'
                    },
                    'metrics': {
                        'followers': '800K+',
                        'engagement': 'Muito Alto',
                        'influence': 'Nacional'
                    }
                },
                {
                    'name': 'Klickpages',
                    'type': 'empresa',
                    'website': 'https://www.klickpages.com.br',
                    'description': 'Plataforma de criação de landing pages e funis de vendas',
                    'size': 'média',
                    'location': 'Brasil',
                    'specialties': ['landing pages', 'funis de vendas', 'conversão'],
                    'social_media': {
                        'youtube': 'https://youtube.com/c/Klickpages',
                        'instagram': 'https://instagram.com/klickpages',
                        'linkedin': 'https://linkedin.com/company/klickpages'
                    },
                    'metrics': {
                        'employees': '100+',
                        'clients': '50K+',
                        'market_share': 'Médio'
                    }
                }
            ],
            'ecommerce': [
                {
                    'name': 'Mercado Livre',
                    'type': 'empresa',
                    'website': 'https://www.mercadolivre.com.br',
                    'description': 'Maior marketplace da América Latina',
                    'size': 'gigante',
                    'location': 'América Latina',
                    'specialties': ['marketplace', 'pagamentos', 'logística'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/mercadolibre',
                        'youtube': 'https://youtube.com/c/MercadoLivre',
                        'instagram': 'https://instagram.com/mercadolivre'
                    },
                    'metrics': {
                        'employees': '40K+',
                        'gmv': '$28B+',
                        'market_share': 'Dominante'
                    }
                },
                {
                    'name': 'Magazine Luiza',
                    'type': 'empresa',
                    'website': 'https://www.magazineluiza.com.br',
                    'description': 'Varejista omnichannel líder no Brasil',
                    'size': 'gigante',
                    'location': 'Brasil',
                    'specialties': ['varejo', 'omnichannel', 'marketplace'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/magazine-luiza',
                        'youtube': 'https://youtube.com/c/MagazineLuiza',
                        'instagram': 'https://instagram.com/magazineluiza'
                    },
                    'metrics': {
                        'employees': '50K+',
                        'revenue': 'R$50B+',
                        'market_share': 'Alto'
                    }
                },
                {
                    'name': 'Shopify',
                    'type': 'empresa',
                    'website': 'https://www.shopify.com',
                    'description': 'Plataforma global de e-commerce',
                    'size': 'gigante',
                    'location': 'Global',
                    'specialties': ['plataforma e-commerce', 'SaaS', 'pagamentos'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/shopify',
                        'youtube': 'https://youtube.com/c/shopify',
                        'twitter': 'https://twitter.com/shopify'
                    },
                    'metrics': {
                        'employees': '10K+',
                        'merchants': '2M+',
                        'market_share': 'Global Leader'
                    }
                },
                {
                    'name': 'Nuvemshop',
                    'type': 'empresa',
                    'website': 'https://www.nuvemshop.com.br',
                    'description': 'Plataforma de e-commerce para pequenas e médias empresas',
                    'size': 'grande',
                    'location': 'América Latina',
                    'specialties': ['e-commerce', 'SaaS', 'PMEs'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/nuvemshop',
                        'youtube': 'https://youtube.com/c/Nuvemshop',
                        'instagram': 'https://instagram.com/nuvemshop'
                    },
                    'metrics': {
                        'employees': '1K+',
                        'stores': '100K+',
                        'market_share': 'Alto'
                    }
                },
                {
                    'name': 'Bruno Ávila',
                    'type': 'influencer',
                    'website': 'https://www.brunoavila.com.br',
                    'description': 'Expert em e-commerce e dropshipping',
                    'size': 'individual',
                    'location': 'Brasil',
                    'specialties': ['e-commerce', 'dropshipping', 'vendas online'],
                    'social_media': {
                        'youtube': 'https://youtube.com/c/BrunoAvila',
                        'instagram': 'https://instagram.com/brunoavilaoficial',
                        'linkedin': 'https://linkedin.com/in/brunoavila'
                    },
                    'metrics': {
                        'followers': '500K+',
                        'engagement': 'Alto',
                        'influence': 'Nacional'
                    }
                }
            ],
            'educacao_online': [
                {
                    'name': 'Alura',
                    'type': 'empresa',
                    'website': 'https://www.alura.com.br',
                    'description': 'Plataforma de cursos online de tecnologia',
                    'size': 'grande',
                    'location': 'Brasil',
                    'specialties': ['educação tech', 'programação', 'design'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/alura',
                        'youtube': 'https://youtube.com/c/AluraCursosOnline',
                        'instagram': 'https://instagram.com/aluraonline'
                    },
                    'metrics': {
                        'employees': '500+',
                        'students': '1M+',
                        'market_share': 'Alto'
                    }
                },
                {
                    'name': 'Coursera',
                    'type': 'empresa',
                    'website': 'https://www.coursera.org',
                    'description': 'Plataforma global de educação online',
                    'size': 'gigante',
                    'location': 'Global',
                    'specialties': ['educação superior', 'certificações', 'universidades'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/coursera',
                        'youtube': 'https://youtube.com/c/coursera',
                        'twitter': 'https://twitter.com/coursera'
                    },
                    'metrics': {
                        'employees': '3K+',
                        'learners': '100M+',
                        'market_share': 'Global Leader'
                    }
                },
                {
                    'name': 'Udemy',
                    'type': 'empresa',
                    'website': 'https://www.udemy.com',
                    'description': 'Marketplace global de cursos online',
                    'size': 'gigante',
                    'location': 'Global',
                    'specialties': ['marketplace educacional', 'skills', 'profissional'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/udemy',
                        'youtube': 'https://youtube.com/c/udemy',
                        'twitter': 'https://twitter.com/udemy'
                    },
                    'metrics': {
                        'employees': '2K+',
                        'students': '50M+',
                        'market_share': 'Global Top 3'
                    }
                },
                {
                    'name': 'Filipe Deschamps',
                    'type': 'influencer',
                    'website': 'https://filipedeschamps.com.br',
                    'description': 'Educador em programação e tecnologia',
                    'size': 'individual',
                    'location': 'Brasil',
                    'specialties': ['programação', 'JavaScript', 'carreira tech'],
                    'social_media': {
                        'youtube': 'https://youtube.com/c/FilipeDeschamps',
                        'instagram': 'https://instagram.com/filipedeschamps',
                        'linkedin': 'https://linkedin.com/in/filipedeschamps'
                    },
                    'metrics': {
                        'followers': '1M+',
                        'engagement': 'Muito Alto',
                        'influence': 'Nacional'
                    }
                },
                {
                    'name': 'Rocketseat',
                    'type': 'empresa',
                    'website': 'https://www.rocketseat.com.br',
                    'description': 'Plataforma de educação em programação',
                    'size': 'média',
                    'location': 'Brasil',
                    'specialties': ['programação', 'JavaScript', 'React', 'Node.js'],
                    'social_media': {
                        'youtube': 'https://youtube.com/c/RocketSeat',
                        'instagram': 'https://instagram.com/rocketseat',
                        'linkedin': 'https://linkedin.com/company/rocketseat'
                    },
                    'metrics': {
                        'employees': '200+',
                        'students': '500K+',
                        'market_share': 'Alto'
                    }
                }
            ],
            'fintech': [
                {
                    'name': 'Nubank',
                    'type': 'empresa',
                    'website': 'https://www.nubank.com.br',
                    'description': 'Maior fintech da América Latina',
                    'size': 'gigante',
                    'location': 'Brasil/América Latina',
                    'specialties': ['banco digital', 'cartão de crédito', 'investimentos'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/nubank',
                        'youtube': 'https://youtube.com/c/nubank',
                        'instagram': 'https://instagram.com/nubank'
                    },
                    'metrics': {
                        'employees': '5K+',
                        'customers': '70M+',
                        'market_share': 'Dominante'
                    }
                },
                {
                    'name': 'PicPay',
                    'type': 'empresa',
                    'website': 'https://www.picpay.com',
                    'description': 'Super app financeiro brasileiro',
                    'size': 'grande',
                    'location': 'Brasil',
                    'specialties': ['pagamentos', 'carteira digital', 'marketplace'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/picpay',
                        'youtube': 'https://youtube.com/c/PicPay',
                        'instagram': 'https://instagram.com/picpay'
                    },
                    'metrics': {
                        'employees': '3K+',
                        'users': '30M+',
                        'market_share': 'Alto'
                    }
                },
                {
                    'name': 'Inter',
                    'type': 'empresa',
                    'website': 'https://www.bancointer.com.br',
                    'description': 'Banco digital completo',
                    'size': 'grande',
                    'location': 'Brasil',
                    'specialties': ['banco digital', 'investimentos', 'seguros'],
                    'social_media': {
                        'linkedin': 'https://linkedin.com/company/banco-inter',
                        'youtube': 'https://youtube.com/c/BancoInter',
                        'instagram': 'https://instagram.com/bancointer'
                    },
                    'metrics': {
                        'employees': '8K+',
                        'customers': '20M+',
                        'market_share': 'Alto'
                    }
                },
                {
                    'name': 'Thiago Nigro (Primo Rico)',
                    'type': 'influencer',
                    'website': 'https://www.primorico.com.br',
                    'description': 'Educador financeiro e empreendedor',
                    'size': 'individual',
                    'location': 'Brasil',
                    'specialties': ['educação financeira', 'investimentos', 'empreendedorismo'],
                    'social_media': {
                        'youtube': 'https://youtube.com/c/ThiagoNigro',
                        'instagram': 'https://instagram.com/thiago.nigro',
                        'linkedin': 'https://linkedin.com/in/thiago-nigro'
                    },
                    'metrics': {
                        'followers': '5M+',
                        'engagement': 'Muito Alto',
                        'influence': 'Nacional'
                    }
                },
                {
                    'name': 'Nathalia Arcuri (Me Poupe!)',
                    'type': 'influencer',
                    'website': 'https://www.mepoupe.com',
                    'description': 'Educadora financeira e empresária',
                    'size': 'individual',
                    'location': 'Brasil',
                    'specialties': ['educação financeira', 'investimentos', 'economia doméstica'],
                    'social_media': {
                        'youtube': 'https://youtube.com/c/MePoupeOficial',
                        'instagram': 'https://instagram.com/nath.arcuri',
                        'linkedin': 'https://linkedin.com/in/nathaliaarcuri'
                    },
                    'metrics': {
                        'followers': '8M+',
                        'engagement': 'Muito Alto',
                        'influence': 'Nacional'
                    }
                }
            ]
        }
    
    def _initialize_industry_keywords(self) -> Dict[str, List[str]]:
        """Inicializa palavras-chave por setor"""
        return {
            'marketing_digital': [
                'marketing', 'digital', 'automação', 'leads', 'conversão', 'funil',
                'copywriting', 'vendas', 'CRM', 'email marketing', 'social media'
            ],
            'ecommerce': [
                'ecommerce', 'e-commerce', 'loja virtual', 'marketplace', 'vendas online',
                'dropshipping', 'varejo', 'omnichannel', 'pagamentos', 'logística'
            ],
            'educacao_online': [
                'educação', 'cursos', 'online', 'EAD', 'treinamento', 'capacitação',
                'programação', 'tecnologia', 'skills', 'certificação'
            ],
            'fintech': [
                'fintech', 'banco', 'digital', 'pagamentos', 'investimentos', 'cartão',
                'crédito', 'financeiro', 'pix', 'carteira digital'
            ]
        }
    
    def analyze_competitors_for_query(self, query: str, max_competitors: int = 10) -> Dict[str, Any]:
        """
        Analisa concorrentes baseado na query do usuário
        
        Args:
            query: Query de busca do usuário
            max_competitors: Número máximo de concorrentes a retornar
            
        Returns:
            Análise completa de concorrentes
        """
        try:
            logger.info(f"🔍 Analisando concorrentes para: {query}")
            
            # Identifica setor baseado na query
            identified_sectors = self._identify_sectors(query)
            
            # Coleta concorrentes relevantes
            relevant_competitors = []
            for sector in identified_sectors:
                if sector in self.competitor_database:
                    sector_competitors = self.competitor_database[sector]
                    # Filtra por relevância à query
                    filtered_competitors = self._filter_competitors_by_relevance(
                        sector_competitors, query
                    )
                    relevant_competitors.extend(filtered_competitors)
            
            # Remove duplicatas e limita quantidade
            unique_competitors = self._deduplicate_competitors(relevant_competitors)
            final_competitors = unique_competitors[:max_competitors]
            
            # Enriquece dados dos concorrentes
            enriched_competitors = self._enrich_competitor_data(final_competitors, query)
            
            # Gera análise do mercado
            market_analysis = self._generate_market_analysis(enriched_competitors, identified_sectors)
            
            # Gera insights competitivos
            competitive_insights = self._generate_competitive_insights(enriched_competitors)
            
            result = {
                'query': query,
                'identified_sectors': identified_sectors,
                'total_competitors_found': len(enriched_competitors),
                'analysis_date': datetime.now().isoformat(),
                'competitors': enriched_competitors,
                'market_analysis': market_analysis,
                'competitive_insights': competitive_insights,
                'recommendations': self._generate_recommendations(enriched_competitors, query)
            }
            
            logger.info(f"✅ Análise concluída: {len(enriched_competitors)} concorrentes identificados")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de concorrentes: {e}")
            return {
                'query': query,
                'error': str(e),
                'competitors': [],
                'analysis_date': datetime.now().isoformat()
            }
    
    def _identify_sectors(self, query: str) -> List[str]:
        """Identifica setores relevantes baseado na query"""
        query_lower = query.lower()
        identified_sectors = []
        
        for sector, keywords in self.industry_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
            
            if score > 0:
                identified_sectors.append((sector, score))
        
        # Ordena por relevância e retorna os setores
        identified_sectors.sort(key=lambda x: x[1], reverse=True)
        return [sector for sector, _ in identified_sectors[:3]]  # Top 3 setores
    
    def _filter_competitors_by_relevance(self, competitors: List[Dict], query: str) -> List[Dict]:
        """Filtra concorrentes por relevância à query"""
        query_lower = query.lower()
        relevant_competitors = []
        
        for competitor in competitors:
            relevance_score = 0
            
            # Verifica nome
            if any(word in competitor['name'].lower() for word in query_lower.split()):
                relevance_score += 3
            
            # Verifica descrição
            if any(word in competitor['description'].lower() for word in query_lower.split()):
                relevance_score += 2
            
            # Verifica especialidades
            for specialty in competitor.get('specialties', []):
                if any(word in specialty.lower() for word in query_lower.split()):
                    relevance_score += 1
            
            if relevance_score > 0:
                competitor['relevance_score'] = relevance_score
                relevant_competitors.append(competitor)
        
        # Ordena por relevância
        relevant_competitors.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return relevant_competitors
    
    def _deduplicate_competitors(self, competitors: List[Dict]) -> List[Dict]:
        """Remove duplicatas baseado no nome"""
        seen_names = set()
        unique_competitors = []
        
        for competitor in competitors:
            name = competitor['name'].lower()
            if name not in seen_names:
                seen_names.add(name)
                unique_competitors.append(competitor)
        
        return unique_competitors
    
    def _enrich_competitor_data(self, competitors: List[Dict], query: str) -> List[Dict]:
        """Enriquece dados dos concorrentes com análises adicionais"""
        enriched = []
        
        for competitor in competitors:
            # Calcula força competitiva
            competitive_strength = self._calculate_competitive_strength(competitor)
            
            # Identifica pontos fortes e fracos
            strengths, weaknesses = self._analyze_strengths_weaknesses(competitor, query)
            
            # Gera recomendações específicas
            recommendations = self._generate_competitor_recommendations(competitor, query)
            
            enriched_competitor = {
                **competitor,
                'competitive_strength': competitive_strength,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'recommendations': recommendations,
                'threat_level': self._calculate_threat_level(competitor, competitive_strength)
            }
            
            enriched.append(enriched_competitor)
        
        return enriched
    
    def _calculate_competitive_strength(self, competitor: Dict) -> str:
        """Calcula força competitiva do concorrente"""
        score = 0
        
        # Tamanho da empresa
        size = competitor.get('size', '')
        if size == 'gigante':
            score += 5
        elif size == 'grande':
            score += 4
        elif size == 'média':
            score += 3
        elif size == 'pequena':
            score += 2
        else:
            score += 1
        
        # Presença em redes sociais
        social_media = competitor.get('social_media', {})
        score += len(social_media)
        
        # Métricas específicas
        metrics = competitor.get('metrics', {})
        if 'market_share' in metrics:
            market_share = metrics['market_share'].lower()
            if 'dominante' in market_share or 'leader' in market_share:
                score += 3
            elif 'alto' in market_share or 'high' in market_share:
                score += 2
            elif 'médio' in market_share or 'medium' in market_share:
                score += 1
        
        # Classificação
        if score >= 10:
            return 'Muito Alta'
        elif score >= 7:
            return 'Alta'
        elif score >= 5:
            return 'Média'
        else:
            return 'Baixa'
    
    def _analyze_strengths_weaknesses(self, competitor: Dict, query: str) -> tuple:
        """Analisa pontos fortes e fracos do concorrente"""
        strengths = []
        weaknesses = []
        
        # Análise baseada no tipo
        if competitor['type'] == 'empresa':
            if competitor.get('size') in ['gigante', 'grande']:
                strengths.append('Grande porte e recursos financeiros')
                strengths.append('Marca estabelecida no mercado')
            else:
                strengths.append('Agilidade e flexibilidade')
                weaknesses.append('Recursos limitados comparado aos grandes players')
            
            # Presença digital
            social_count = len(competitor.get('social_media', {}))
            if social_count >= 3:
                strengths.append('Forte presença em múltiplas redes sociais')
            elif social_count <= 1:
                weaknesses.append('Presença digital limitada')
        
        elif competitor['type'] == 'influencer':
            strengths.append('Conexão direta com audiência')
            strengths.append('Agilidade na criação de conteúdo')
            strengths.append('Autenticidade e confiança do público')
            weaknesses.append('Dependência da pessoa física')
            weaknesses.append('Recursos limitados para escalar')
        
        # Análise de especialidades
        specialties = competitor.get('specialties', [])
        if len(specialties) > 3:
            strengths.append('Diversificação de especialidades')
        elif len(specialties) == 1:
            strengths.append('Foco especializado em nicho')
        
        return strengths, weaknesses
    
    def _generate_competitor_recommendations(self, competitor: Dict, query: str) -> List[str]:
        """Gera recomendações específicas para cada concorrente"""
        recommendations = []
        
        # Recomendações baseadas no tipo
        if competitor['type'] == 'empresa':
            recommendations.append(f"Analisar estratégias de conteúdo da {competitor['name']}")
            recommendations.append(f"Monitorar lançamentos de produtos/serviços")
            recommendations.append(f"Estudar modelo de precificação")
        
        elif competitor['type'] == 'influencer':
            recommendations.append(f"Analisar formato e frequência de conteúdo")
            recommendations.append(f"Estudar estratégias de engajamento")
            recommendations.append(f"Identificar parcerias e colaborações")
        
        # Recomendações baseadas na força competitiva
        strength = competitor.get('competitive_strength', '')
        if strength in ['Muito Alta', 'Alta']:
            recommendations.append("Identificar gaps não atendidos por este player")
            recommendations.append("Considerar estratégia de diferenciação")
        else:
            recommendations.append("Avaliar oportunidades de competição direta")
            recommendations.append("Analisar possibilidades de parceria")
        
        return recommendations
    
    def _calculate_threat_level(self, competitor: Dict, strength: str) -> str:
        """Calcula nível de ameaça do concorrente"""
        if strength == 'Muito Alta':
            return 'Crítico'
        elif strength == 'Alta':
            return 'Alto'
        elif strength == 'Média':
            return 'Moderado'
        else:
            return 'Baixo'
    
    def _generate_market_analysis(self, competitors: List[Dict], sectors: List[str]) -> Dict[str, Any]:
        """Gera análise do mercado baseada nos concorrentes"""
        analysis = {
            'dominant_sectors': sectors,
            'market_concentration': self._calculate_market_concentration(competitors),
            'player_types': self._analyze_player_types(competitors),
            'geographic_distribution': self._analyze_geographic_distribution(competitors),
            'competitive_landscape': self._analyze_competitive_landscape(competitors)
        }
        
        return analysis
    
    def _calculate_market_concentration(self, competitors: List[Dict]) -> str:
        """Calcula concentração do mercado"""
        large_players = sum(1 for c in competitors if c.get('size') in ['gigante', 'grande'])
        total_players = len(competitors)
        
        if total_players == 0:
            return 'Indefinido'
        
        concentration_ratio = large_players / total_players
        
        if concentration_ratio >= 0.7:
            return 'Alta concentração - Mercado dominado por grandes players'
        elif concentration_ratio >= 0.4:
            return 'Concentração moderada - Mix de grandes e médios players'
        else:
            return 'Baixa concentração - Mercado fragmentado'
    
    def _analyze_player_types(self, competitors: List[Dict]) -> Dict[str, int]:
        """Analisa tipos de players no mercado"""
        types = {}
        for competitor in competitors:
            player_type = competitor.get('type', 'unknown')
            types[player_type] = types.get(player_type, 0) + 1
        
        return types
    
    def _analyze_geographic_distribution(self, competitors: List[Dict]) -> Dict[str, int]:
        """Analisa distribuição geográfica dos concorrentes"""
        locations = {}
        for competitor in competitors:
            location = competitor.get('location', 'unknown')
            locations[location] = locations.get(location, 0) + 1
        
        return locations
    
    def _analyze_competitive_landscape(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analisa panorama competitivo"""
        strengths = [c.get('competitive_strength', 'Baixa') for c in competitors]
        
        landscape = {
            'total_competitors': len(competitors),
            'high_threat_competitors': sum(1 for s in strengths if s in ['Muito Alta', 'Alta']),
            'moderate_threat_competitors': sum(1 for s in strengths if s == 'Média'),
            'low_threat_competitors': sum(1 for s in strengths if s == 'Baixa'),
            'market_maturity': self._assess_market_maturity(competitors)
        }
        
        return landscape
    
    def _assess_market_maturity(self, competitors: List[Dict]) -> str:
        """Avalia maturidade do mercado"""
        established_players = sum(1 for c in competitors if c.get('size') in ['gigante', 'grande'])
        total_players = len(competitors)
        
        if total_players == 0:
            return 'Indefinido'
        
        maturity_ratio = established_players / total_players
        
        if maturity_ratio >= 0.6:
            return 'Mercado maduro - Dominado por players estabelecidos'
        elif maturity_ratio >= 0.3:
            return 'Mercado em crescimento - Mix de players estabelecidos e emergentes'
        else:
            return 'Mercado emergente - Muitas oportunidades para novos players'
    
    def _generate_competitive_insights(self, competitors: List[Dict]) -> List[str]:
        """Gera insights competitivos"""
        insights = []
        
        if not competitors:
            return ['Nenhum concorrente identificado para análise']
        
        # Insight sobre concentração
        large_players = [c for c in competitors if c.get('size') in ['gigante', 'grande']]
        if len(large_players) > len(competitors) * 0.5:
            insights.append(f"Mercado dominado por grandes players ({len(large_players)} de {len(competitors)})")
        
        # Insight sobre tipos de player
        influencers = [c for c in competitors if c.get('type') == 'influencer']
        if len(influencers) > 0:
            insights.append(f"Presença significativa de influencers ({len(influencers)} identificados)")
        
        # Insight sobre ameaças
        high_threat = [c for c in competitors if c.get('threat_level') in ['Crítico', 'Alto']]
        if len(high_threat) > 0:
            insights.append(f"Identificados {len(high_threat)} concorrentes de alta ameaça")
        
        # Insight sobre especialização
        all_specialties = []
        for c in competitors:
            all_specialties.extend(c.get('specialties', []))
        
        if all_specialties:
            from collections import Counter
            common_specialties = Counter(all_specialties).most_common(3)
            top_specialty = common_specialties[0][0]
            insights.append(f"Especialidade mais comum no mercado: {top_specialty}")
        
        return insights
    
    def _generate_recommendations(self, competitors: List[Dict], query: str) -> List[str]:
        """Gera recomendações estratégicas"""
        recommendations = []
        
        if not competitors:
            recommendations.append("Realizar pesquisa mais ampla para identificar concorrentes")
            return recommendations
        
        # Recomendações baseadas na análise
        high_threat = [c for c in competitors if c.get('threat_level') in ['Crítico', 'Alto']]
        
        if len(high_threat) > 0:
            recommendations.append("Priorizar diferenciação para competir com players dominantes")
            recommendations.append("Identificar nichos não atendidos pelos líderes de mercado")
        
        # Recomendações sobre influencers
        influencers = [c for c in competitors if c.get('type') == 'influencer']
        if len(influencers) > 0:
            recommendations.append("Considerar estratégias de marketing de influência")
            recommendations.append("Avaliar parcerias com criadores de conteúdo relevantes")
        
        # Recomendações sobre presença digital
        strong_digital = [c for c in competitors if len(c.get('social_media', {})) >= 3]
        if len(strong_digital) > len(competitors) * 0.5:
            recommendations.append("Investir fortemente em presença digital multi-canal")
            recommendations.append("Desenvolver estratégia de conteúdo consistente")
        
        recommendations.append("Monitorar continuamente movimentos dos principais concorrentes")
        recommendations.append("Realizar análise SWOT detalhada dos top 3 concorrentes")
        
        return recommendations

# Instância global
enhanced_competitor_analyzer = EnhancedCompetitorAnalyzer()