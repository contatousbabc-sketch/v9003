import os
import logging
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

class RealCompetitorAnalyzer:
    """
    Sistema genérico de análise de concorrentes reais do mercado
    Capaz de identificar concorrentes para qualquer segmento através de busca web
    """
    def __init__(self):
        self.competitor_cache = {}
        self.search_patterns = {
            'empresa': ['empresa', 'company', 'startup', 'corporação', 'negócio'],
            'influencer': ['influencer', 'influenciador', 'criador de conteúdo', 'youtuber', 'expert'],
            'produto': ['produto', 'serviço', 'solução', 'plataforma', 'ferramenta'],
            'mercado': ['mercado', 'setor', 'segmento', 'indústria', 'nicho']
        }
        
    async def analyze_competitors_for_query(
        self, 
        query: str, 
        max_competitors: int = 10,
        include_influencers: bool = True,
        country: str = "brasil"
    ) -> Dict[str, Any]:
        """
        Analisa concorrentes reais baseado em qualquer query do usuário
        
        Args:
            query: Query do usuário (ex: "marketing digital", "e-commerce de moda", "educação financeira")
            max_competitors: Número máximo de concorrentes a retornar
            include_influencers: Se deve incluir influencers e experts
            country: País para focar a busca (default: brasil)
        """
        logger.info(f"🔍 Iniciando análise de concorrentes para: {query}")
        
        # Normaliza a query
        normalized_query = self._normalize_query(query)
        
        # Gera variações de busca
        search_queries = self._generate_search_queries(normalized_query, country, include_influencers)
        
        # Executa buscas paralelas
        all_competitors = []
        for search_query in search_queries:
            competitors = await self._search_and_extract_competitors(search_query, country)
            all_competitors.extend(competitors)
        
        # Remove duplicatas e processa
        unique_competitors = self._deduplicate_competitors(all_competitors)
        
        # Enriquece dados dos concorrentes
        enriched_competitors = await self._enrich_competitors_data(unique_competitors[:max_competitors])
        
        # Gera análise do mercado
        market_analysis = self._analyze_market_landscape(enriched_competitors, normalized_query)
        
        result = {
            'query': query,
            'normalized_query': normalized_query,
            'total_competitors_found': len(enriched_competitors),
            'analysis_date': datetime.now().isoformat(),
            'country': country,
            'competitors': enriched_competitors,
            'market_analysis': market_analysis,
            'search_queries_used': search_queries
        }
        
        # Cache o resultado
        cache_key = f"{normalized_query}_{country}"
        self.competitor_cache[cache_key] = result
        
        logger.info(f"✅ Análise concluída: {len(enriched_competitors)} concorrentes identificados")
        return result
    
    def _normalize_query(self, query: str) -> str:
        """Normaliza a query removendo caracteres especiais e padronizando"""
        normalized = query.lower().strip()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    def _generate_search_queries(
        self, 
        normalized_query: str, 
        country: str,
        include_influencers: bool
    ) -> List[str]:
        """Gera múltiplas queries de busca otimizadas"""
        queries = []
        country_term = country if country.lower() != "brasil" else "Brasil"
        
        # Query principal - empresas líderes
        queries.append(f"principais empresas {normalized_query} {country_term}")
        queries.append(f"líderes de mercado {normalized_query} {country_term}")
        queries.append(f"top empresas {normalized_query} {country_term}")
        
        # Startups e scale-ups
        queries.append(f"startups {normalized_query} {country_term}")
        queries.append(f"unicórnios {normalized_query} {country_term}")
        
        # Plataformas e ferramentas
        queries.append(f"melhores plataformas {normalized_query} {country_term}")
        queries.append(f"ferramentas {normalized_query} {country_term}")
        
        if include_influencers:
            # Influencers e experts
            queries.append(f"principais influencers {normalized_query} {country_term}")
            queries.append(f"experts {normalized_query} {country_term}")
            queries.append(f"youtubers {normalized_query} {country_term}")
            queries.append(f"criadores de conteúdo {normalized_query} {country_term}")
        
        return queries
    
    async def _search_and_extract_competitors(
        self, 
        search_query: str, 
        country: str
    ) -> List[Dict[str, Any]]:
        """
        Executa busca web e extrai informações de concorrentes
        IMPORTANTE: Esta função deve ser integrada com o serviço de busca web do app
        """
        competitors = []
        
        try:
            # INTEGRAÇÃO NECESSÁRIA: Substituir por chamada ao serviço de busca web do app
            # Exemplo: search_results = await app_web_search_service.search(search_query)
            
            # Mock de resultados (substituir pela integração real)
            search_results = await self._mock_web_search(search_query)
            
            for result in search_results:
                competitor = self._extract_competitor_from_result(result)
                if competitor:
                    competitors.append(competitor)
                    
        except Exception as e:
            logger.error(f"Erro ao buscar concorrentes para '{search_query}': {str(e)}")
        
        return competitors
    
    async def _mock_web_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Mock temporário - DEVE SER SUBSTITUÍDO pela integração com busca web real
        """
        # Este é apenas um exemplo - remover quando integrar com busca real
        return [
            {
                'title': f'Resultado para {query}',
                'url': 'https://example.com',
                'snippet': 'Descrição do resultado...',
                'domain': 'example.com'
            }
        ]
    
    def _extract_competitor_from_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrai informações estruturadas de um resultado de busca"""
        try:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            url = result.get('url', '')
            domain = result.get('domain', '')
            
            # Extrai nome da empresa/influencer
            name = self._extract_name_from_title(title)
            if not name:
                return None
            
            # Determina o tipo (empresa, influencer, produto)
            entity_type = self._determine_entity_type(title, snippet)
            
            # Extrai website principal
            website = self._extract_main_website(url, domain)
            
            competitor = {
                'name': name,
                'type': entity_type,
                'website': website,
                'description': snippet[:200] if snippet else '',
                'source_url': url,
                'domain': domain,
                'raw_data': {
                    'title': title,
                    'snippet': snippet
                }
            }
            
            return competitor
            
        except Exception as e:
            logger.error(f"Erro ao extrair concorrente: {str(e)}")
            return None
    
    def _extract_name_from_title(self, title: str) -> Optional[str]:
        """Extrai o nome da empresa/influencer do título"""
        # Remove ruído comum
        title = re.sub(r'\s*[-|:]\s*.*$', '', title)
        title = title.strip()
        
        # Remove palavras-chave comuns
        noise_words = ['site oficial', 'página inicial', 'home', 'brasil']
        for word in noise_words:
            title = re.sub(f'\\b{word}\\b', '', title, flags=re.IGNORECASE)
        
        title = title.strip()
        return title if len(title) > 2 else None
    
    def _determine_entity_type(self, title: str, snippet: str) -> str:
        """Determina se é empresa, influencer ou produto"""
        text = f"{title} {snippet}".lower()
        
        influencer_keywords = ['influencer', 'youtuber', 'criador', 'expert', 'especialista', 'mentor', 'coach']
        company_keywords = ['empresa', 'company', 'startup', 'corporação', 'plataforma', 'serviço']
        
        if any(keyword in text for keyword in influencer_keywords):
            return 'influencer'
        elif any(keyword in text for keyword in company_keywords):
            return 'empresa'
        else:
            return 'produto'
    
    def _extract_main_website(self, url: str, domain: str) -> str:
        """Extrai o website principal do domínio"""
        if not url:
            return ''
        
        # Remove subpaths, mantém apenas domínio principal
        if domain:
            return f"https://{domain}"
        
        # Fallback: extrai do URL completo
        match = re.match(r'https?://([^/]+)', url)
        if match:
            return f"https://{match.group(1)}"
        
        return url
    
    def _deduplicate_competitors(self, competitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove concorrentes duplicados baseado em nome e domínio"""
        seen = set()
        unique = []
        
        for competitor in competitors:
            # Cria identificador único
            name = competitor.get('name', '').lower().strip()
            domain = competitor.get('domain', '').lower().strip()
            identifier = f"{name}|{domain}"
            
            if identifier not in seen and name:
                seen.add(identifier)
                unique.append(competitor)
        
        return unique
    
    async def _enrich_competitors_data(
        self, 
        competitors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enriquece dados dos concorrentes com informações adicionais"""
        enriched = []
        
        for competitor in competitors:
            enriched_competitor = competitor.copy()
            
            # Busca redes sociais
            enriched_competitor['social_media'] = await self._find_social_media(competitor)
            
            # Estima tamanho e alcance
            enriched_competitor['estimated_reach'] = self._estimate_reach(competitor)
            
            # Identifica produtos/serviços principais
            enriched_competitor['key_offerings'] = self._extract_key_offerings(competitor)
            
            # Score de relevância
            enriched_competitor['relevance_score'] = self._calculate_relevance_score(competitor)
            
            enriched.append(enriched_competitor)
        
        # Ordena por relevância
        enriched.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return enriched
    
    async def _find_social_media(self, competitor: Dict[str, Any]) -> Dict[str, str]:
        """
        Tenta identificar redes sociais do concorrente
        INTEGRAÇÃO NECESSÁRIA: Usar serviço de busca web do app
        """
        social_media = {}
        name = competitor.get('name', '')
        
        # Padrões comuns de redes sociais
        social_patterns = {
            'linkedin': f"site:linkedin.com {name}",
            'instagram': f"site:instagram.com {name}",
            'youtube': f"site:youtube.com {name}",
            'twitter': f"site:twitter.com {name}",
            'facebook': f"site:facebook.com {name}"
        }
        
        # Mock - substituir por busca real
        # Para cada rede social, buscar e extrair URL
        for platform, query in social_patterns.items():
            # social_media[platform] = await self._search_for_social_profile(query)
            social_media[platform] = f"@{name.lower().replace(' ', '')}"
        
        return social_media
    
    def _estimate_reach(self, competitor: Dict[str, Any]) -> Dict[str, str]:
        """Estima alcance e tamanho do concorrente"""
        # Baseado em sinais no snippet e tipo
        snippet = competitor.get('description', '').lower()
        entity_type = competitor.get('type', '')
        
        reach = {
            'size': 'Médio',
            'market_position': 'Competidor relevante',
            'confidence': 'Média'
        }
        
        # Indicadores de tamanho
        if any(term in snippet for term in ['líder', 'maior', 'principal', 'top']):
            reach['size'] = 'Grande'
            reach['market_position'] = 'Líder de mercado'
            reach['confidence'] = 'Alta'
        elif any(term in snippet for term in ['startup', 'emergente', 'nova']):
            reach['size'] = 'Pequeno'
            reach['market_position'] = 'Emergente'
            reach['confidence'] = 'Média'
        
        if entity_type == 'influencer':
            reach['market_position'] = 'Influenciador/Expert'
        
        return reach
    
    def _extract_key_offerings(self, competitor: Dict[str, Any]) -> List[str]:
        """Extrai produtos/serviços principais do snippet"""
        snippet = competitor.get('description', '')
        
        # Palavras-chave que indicam ofertas
        offering_keywords = [
            'plataforma', 'ferramenta', 'solução', 'serviço', 'produto',
            'sistema', 'software', 'aplicativo', 'consultoria', 'curso',
            'treinamento', 'mentoria', 'automação', 'gestão'
        ]
        
        offerings = []
        words = snippet.lower().split()
        
        for i, word in enumerate(words):
            if any(keyword in word for keyword in offering_keywords):
                # Captura contexto ao redor
                context_start = max(0, i - 2)
                context_end = min(len(words), i + 3)
                context = ' '.join(words[context_start:context_end])
                offerings.append(context)
        
        # Remove duplicatas e limita
        offerings = list(set(offerings))[:3]
        
        return offerings if offerings else ['Serviços não especificados']
    
    def _calculate_relevance_score(self, competitor: Dict[str, Any]) -> float:
        """Calcula score de relevância do concorrente"""
        score = 5.0  # Base score
        
        # Bônus por ter website
        if competitor.get('website'):
            score += 1.0
        
        # Bônus por descrição detalhada
        description = competitor.get('description', '')
        if len(description) > 100:
            score += 1.0
        if len(description) > 200:
            score += 0.5
        
        # Bônus por tipo
        if competitor.get('type') == 'empresa':
            score += 0.5
        
        # Bônus por indicadores de tamanho
        reach = competitor.get('estimated_reach', {})
        if reach.get('size') == 'Grande':
            score += 2.0
        elif reach.get('size') == 'Médio':
            score += 1.0
        
        return round(score, 2)
    
    def _analyze_market_landscape(
        self, 
        competitors: List[Dict[str, Any]], 
        query: str
    ) -> Dict[str, Any]:
        """Analisa o panorama do mercado baseado nos concorrentes encontrados"""
        analysis = {
            'market_maturity': self._assess_market_maturity(competitors),
            'competitive_intensity': self._assess_competitive_intensity(competitors),
            'key_players': self._identify_key_players(competitors),
            'market_trends': self._identify_market_trends(competitors, query),
            'entry_barriers': self._assess_entry_barriers(competitors),
            'opportunities': self._identify_opportunities(competitors)
        }
        
        return analysis
    
    def _assess_market_maturity(self, competitors: List[Dict[str, Any]]) -> Dict[str, str]:
        """Avalia maturidade do mercado"""
        total = len(competitors)
        
        if total == 0:
            return {'level': 'Nascente', 'description': 'Mercado com poucos players identificados'}
        
        # Conta grandes players
        large_players = sum(1 for c in competitors 
                          if c.get('estimated_reach', {}).get('size') == 'Grande')
        
        maturity_ratio = large_players / total if total > 0 else 0
        
        if maturity_ratio > 0.5:
            return {
                'level': 'Maduro',
                'description': 'Mercado estabelecido com múltiplos líderes consolidados'
            }
        elif maturity_ratio > 0.2:
            return {
                'level': 'Em crescimento',
                'description': 'Mercado em expansão com mix de players estabelecidos e emergentes'
            }
        else:
            return {
                'level': 'Emergente',
                'description': 'Mercado jovem com predominância de startups e novos entrantes'
            }
    
    def _assess_competitive_intensity(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Avalia intensidade competitiva"""
        total = len(competitors)
        
        if total < 5:
            intensity = 'Baixa'
            description = 'Poucos concorrentes diretos identificados'
        elif total < 15:
            intensity = 'Média'
            description = 'Número moderado de concorrentes'
        else:
            intensity = 'Alta'
            description = 'Mercado altamente competitivo com muitos players'
        
        return {
            'level': intensity,
            'total_competitors': total,
            'description': description
        }
    
    def _identify_key_players(self, competitors: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identifica os principais players do mercado"""
        # Pega os top 5 por relevance score
        top_competitors = sorted(
            competitors, 
            key=lambda x: x.get('relevance_score', 0), 
            reverse=True
        )[:5]
        
        key_players = []
        for comp in top_competitors:
            key_players.append({
                'name': comp.get('name', ''),
                'type': comp.get('type', ''),
                'position': comp.get('estimated_reach', {}).get('market_position', ''),
                'website': comp.get('website', '')
            })
        
        return key_players
    
    def _identify_market_trends(
        self, 
        competitors: List[Dict[str, Any]], 
        query: str
    ) -> List[str]:
        """Identifica tendências do mercado baseado nos concorrentes"""
        trends = []
        
        # Analisa tipos de players
        types = [c.get('type', '') for c in competitors]
        if types.count('influencer') > len(types) * 0.3:
            trends.append('Forte presença de influencers e criadores de conteúdo')
        
        # Analisa descrições para palavras-chave emergentes
        all_text = ' '.join([c.get('description', '') for c in competitors]).lower()
        
        trend_keywords = {
            'digital': 'Digitalização acelerada',
            'automação': 'Foco em automação e eficiência',
            'ia': 'Adoção de inteligência artificial',
            'sustentável': 'Preocupação com sustentabilidade',
            'personalizado': 'Customização e personalização',
            'mobile': 'Prioridade mobile-first'
        }
        
        for keyword, trend in trend_keywords.items():
            if keyword in all_text and trend not in trends:
                trends.append(trend)
        
        return trends if trends else ['Tendências não claramente identificadas']
    
    def _assess_entry_barriers(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Avalia barreiras de entrada no mercado"""
        large_players = sum(1 for c in competitors 
                          if c.get('estimated_reach', {}).get('size') == 'Grande')
        
        total = len(competitors)
        
        if large_players > total * 0.5:
            return {
                'level': 'Alta',
                'factors': [
                    'Mercado dominado por grandes players',
                    'Alta necessidade de capital',
                    'Marcas estabelecidas com forte reconhecimento'
                ]
            }
        elif large_players > total * 0.2:
            return {
                'level': 'Média',
                'factors': [
                    'Mix de grandes e pequenos players',
                    'Possibilidade de nichos não atendidos',
                    'Necessidade de diferenciação clara'
                ]
            }
        else:
            return {
                'level': 'Baixa',
                'factors': [
                    'Mercado fragmentado',
                    'Oportunidades para novos entrantes',
                    'Foco em inovação e agilidade'
                ]
            }
    
    def _identify_opportunities(self, competitors: List[Dict[str, Any]]) -> List[str]:
        """Identifica oportunidades no mercado"""
        opportunities = []
        
        # Analisa gaps baseado nos tipos de concorrentes
        types = [c.get('type', '') for c in competitors]
        
        if types.count('influencer') < len(types) * 0.2:
            opportunities.append('Baixa presença de influencers - oportunidade para marketing de conteúdo')
        
        if types.count('empresa') < 3:
            opportunities.append('Poucos players corporativos - mercado aberto para soluções B2B')
        
        # Analisa ofertas
        all_offerings = []
        for comp in competitors:
            all_offerings.extend(comp.get('key_offerings', []))
        
        offerings_text = ' '.join(all_offerings).lower()
        
        if 'mobile' not in offerings_text:
            opportunities.append('Ausência de soluções mobile - oportunidade para apps')
        
        if 'automação' not in offerings_text:
            opportunities.append('Falta de automação - oportunidade para eficiência operacional')
        
        return opportunities if opportunities else [
            'Mercado estabelecido - foco em diferenciação e inovação incremental'
        ]
    
    def generate_executive_summary(self, analysis_result: Dict[str, Any]) -> str:
        """Gera sumário executivo da análise"""
        query = analysis_result.get('query', '')
        total = analysis_result.get('total_competitors_found', 0)
        market_analysis = analysis_result.get('market_analysis', {})
        
        summary = f"""
ANÁLISE DE CONCORRENTES - {query.upper()}
{'=' * 60}

PANORAMA GERAL:
- Total de concorrentes identificados: {total}
- Maturidade do mercado: {market_analysis.get('market_maturity', {}).get('level', 'N/A')}
- Intensidade competitiva: {market_analysis.get('competitive_intensity', {}).get('level', 'N/A')}

PRINCIPAIS PLAYERS:
"""
        
        key_players = market_analysis.get('key_players', [])
        for i, player in enumerate(key_players[:5], 1):
            summary += f"{i}. {player.get('name', 'N/A')} - {player.get('position', 'N/A')}\n"
        
        summary += f"\nTENDÊNCIAS DO MERCADO:\n"
        trends = market_analysis.get('market_trends', [])
        for trend in trends[:3]:
            summary += f"• {trend}\n"
        
        summary += f"\nOPORTUNIDADES IDENTIFICADAS:\n"
        opportunities = market_analysis.get('opportunities', [])
        for opp in opportunities[:3]:
            summary += f"• {opp}\n"
        
        summary += f"\n{'=' * 60}\n"
        summary += f"Análise gerada em: {analysis_result.get('analysis_date', '')}\n"
        
        return summary


# Função auxiliar para integração com o app
async def analyze_competitors_from_query(
    query: str,
    max_results: int = 10,
    include_influencers: bool = True,
    country: str = "brasil"
) -> Dict[str, Any]:
    """
    Função wrapper para fácil integração com o app
    
    Usage:
        result = await analyze_competitors_from_query("marketing digital")
        print(result['market_analysis'])
    """
    analyzer = RealCompetitorAnalyzer()
    result = await analyzer.analyze_competitors_for_query(
        query=query,
        max_competitors=max_results,
        include_influencers=include_influencers,
        country=country
    )
    return result


# Exemplo de uso standalone
if __name__ == "__main__":
    async def main():
        analyzer = RealCompetitorAnalyzer()
        
        # Exemplos de queries diversas
        test_queries = [
            "marketing digital",
            "e-commerce de moda",
            "educação financeira",
            "delivery de comida",
            "consultoria empresarial"
        ]
        
        for query in test_queries:
            print(f"\n{'=' * 60}")
            print(f"Analisando: {query}")
            print('=' * 60)
            
            result = await analyzer.analyze_competitors_for_query(query, max_competitors=5)
            
            # Gera e imprime sumário
            summary = analyzer.generate_executive_summary(result)
            print(summary)
            
            # Aguarda um pouco entre requisições
            await asyncio.sleep(1)
    
    asyncio.run(main())
