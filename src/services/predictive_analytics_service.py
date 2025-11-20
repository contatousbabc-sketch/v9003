#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Predictive Analytics Service
Serviço Centralizado de Análise Preditiva Ultra-Avançado
"""

import os
import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Import do engine existente
from engine.predictive_analytics_engine import PredictiveAnalyticsEngine

logger = logging.getLogger(__name__)

class PredictiveAnalyticsService:
    """
    Serviço centralizado que encapsula o PredictiveAnalyticsEngine
    e expõe funcionalidades específicas para consumo por outros módulos.
    """

    def __init__(self):
        """Inicializa o serviço de análise preditiva"""
        try:
            self.engine = PredictiveAnalyticsEngine()
            self.available = True
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inicializar engine preditivo: {e}")
            self.engine = None
            self.available = False
        logger.info("🔮 Predictive Analytics Service inicializado")

    def is_available(self) -> bool:
        """Verifica se o serviço está disponível"""
        return self.available and self.engine is not None

    async def analyze_session(self, session_id: str) -> Dict[str, Any]:
        """
        Executa a análise completa de uma sessão.

        Args:
            session_id: ID da sessão para análise

        Returns:
            Dict com insights preditivos completos
        """
        try:
            logger.info(f"🔮 Iniciando análise preditiva completa para sessão: {session_id}")

            # Chama o método principal do engine
            insights = await self.engine.analyze_session_data(session_id)

            if insights.get("success", False):
                logger.info(f"✅ Análise preditiva concluída para sessão: {session_id}")
            else:
                logger.warning(f"⚠️ Análise preditiva com problemas para sessão: {session_id}")

            return insights

        except Exception as e:
            logger.error(f"❌ Erro na análise preditiva da sessão {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

    async def analyze_content_chunk(self, text_content: str) -> Dict[str, Any]:
        """
        Analisa um pequeno trecho de texto para insights rápidos.

        Args:
            text_content: Texto para análise

        Returns:
            Dict com insights do conteúdo
        """
        try:
            logger.info("🧠 Analisando chunk de conteúdo...")

            # Análise simplificada para chunks de texto
            insights = await self._analyze_text_chunk_simple(text_content)

            return {
                "success": True,
                "content_insights": insights,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro na análise de chunk: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _analyze_text_chunk_simple(self, text_content: str) -> Dict[str, Any]:
        """
        Análise simplificada de um chunk de texto.

        Args:
            text_content: Texto para análise

        Returns:
            Dict com insights básicos
        """
        insights = {
            "word_count": 0,
            "key_entities": [],
            "sentiment_score": 0.0,
            "topics": [],
            "quality_indicators": {}
        }

        if not text_content or not text_content.strip():
            return insights

        # Contagem básica
        words = text_content.split()
        insights["word_count"] = len(words)

        # Análise com SpaCy se disponível
        if hasattr(self.engine, 'nlp_model') and self.engine.nlp_model:
            try:
                doc = self.engine.nlp_model(text_content[:1000])  # Limita para performance

                # Extrai entidades
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                insights["key_entities"] = entities[:10]  # Top 10

                # Análise de qualidade
                insights["quality_indicators"] = {
                    "has_entities": len(entities) > 0,
                    "entity_diversity": len(set([ent[1] for ent in entities])),
                    "avg_sentence_length": len(text_content) / max(len(list(doc.sents)), 1)
                }

            except Exception as e:
                logger.warning(f"⚠️ Erro na análise NLP do chunk: {e}")

        # Análise de sentimento se disponível
        if hasattr(self.engine, 'sentiment_analyzer') and self.engine.sentiment_analyzer:
            try:
                sentiment = self.engine.sentiment_analyzer.polarity_scores(text_content)
                insights["sentiment_score"] = sentiment.get("compound", 0.0)
            except Exception as e:
                logger.warning(f"⚠️ Erro na análise de sentimento: {e}")

        return insights

    def get_content_quality_score(self, text_data: str) -> float:
        """
        Retorna um score numérico (0-100) representando a qualidade/relevância do conteúdo.

        Args:
            text_data: Texto para avaliação

        Returns:
            Score de qualidade (0-100)
        """
        try:
            if not text_data or not text_data.strip():
                return 0.0

            score = 0.0

            # Critério 1: Comprimento (20 pontos)
            length = len(text_data.strip())
            if length > 1000:
                score += 20
            elif length > 500:
                score += 15
            elif length > 200:
                score += 10
            elif length > 50:
                score += 5

            # Critério 2: Densidade de informações (30 pontos)
            words = text_data.split()
            if len(words) > 100:
                score += 30
            elif len(words) > 50:
                score += 20
            elif len(words) > 20:
                score += 10

            # Critério 3: Presença de entidades/dados estruturados (25 pontos)
            # Busca por padrões que indicam dados estruturados
            structured_patterns = [
                r'\d+%',  # Percentuais
                r'R\$\s*\d+',  # Valores monetários
                r'\d{4}',  # Anos
                r'@\w+',  # Menções
                r'#\w+',  # Hashtags
                r'www\.\w+',  # URLs
                r'\d+\s*(mil|milhão|bilhão)',  # Números grandes
            ]

            import re
            pattern_matches = 0
            for pattern in structured_patterns:
                if re.search(pattern, text_data, re.IGNORECASE):
                    pattern_matches += 1

            score += min(pattern_matches * 5, 25)

            # Critério 4: Diversidade lexical (15 pontos)
            unique_words = set(word.lower() for word in words if len(word) > 3)
            if len(words) > 0:
                diversity_ratio = len(unique_words) / len(words)
                score += diversity_ratio * 15

            # Critério 5: Ausência de spam/conteúdo irrelevante (10 pontos)
            spam_indicators = ['lorem ipsum', 'placeholder', 'exemplo', 'teste', 'sample']
            has_spam = any(indicator in text_data.lower() for indicator in spam_indicators)
            if not has_spam:
                score += 10

            # Normaliza para 0-100
            final_score = min(max(score, 0), 100)

            logger.debug(f"📊 Score de qualidade calculado: {final_score:.1f}")
            return final_score

        except Exception as e:
            logger.error(f"❌ Erro no cálculo de score de qualidade: {e}")
            return 0.0

    async def generate_recommendations(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera recomendações estratégicas a partir de um conjunto de insights.

        Args:
            insights_data: Dados de insights para gerar recomendações

        Returns:
            Dict com recomendações estratégicas
        """
        try:
            logger.info("💡 Gerando recomendações estratégicas...")

            recommendations = {
                "strategic_recommendations": [],
                "quick_wins": [],
                "content_strategy": [],
                "competitive_actions": [],
                "risk_mitigation": [],
                "timestamp": datetime.now().isoformat()
            }

            # Analisa insights para gerar recomendações específicas
            if "textual_insights" in insights_data:
                textual = insights_data["textual_insights"]

                # Recomendações baseadas em entidades encontradas
                if "entities_found" in textual:
                    entities = textual["entities_found"]
                    if entities:
                        recommendations["strategic_recommendations"].append({
                            "category": "Entidades Relevantes",
                            "action": f"Focar em {len(entities)} entidades-chave identificadas na análise",
                            "priority": "alta",
                            "entities": list(entities.keys())[:5]
                        })

                # Quick wins baseados em qualidade de conteúdo
                if "content_quality_scores" in textual:
                    scores = textual["content_quality_scores"]
                    high_quality = [k for k, v in scores.items() if v > 80]
                    if high_quality:
                        recommendations["quick_wins"].append({
                            "action": f"Replicar estratégias dos {len(high_quality)} conteúdos de alta qualidade identificados",
                            "impact": "médio",
                            "effort": "baixo"
                        })

            # Recomendações baseadas em tendências temporais
            if "temporal_trends" in insights_data:
                temporal = insights_data["temporal_trends"]
                if "growth_rates" in temporal and temporal["growth_rates"] != "Depende de timestamps coletados pelos crawlers.":
                    recommendations["content_strategy"].append({
                        "category": "Timing",
                        "action": "Otimizar horários de publicação baseado em tendências identificadas",
                        "data_source": "análise temporal"
                    })

            # Recomendações baseadas em análise visual
            if "visual_insights" in insights_data:
                visual = insights_data["visual_insights"]
                if visual.get("screenshots_processed", 0) > 0:
                    recommendations["competitive_actions"].append({
                        "category": "Análise Visual",
                        "action": f"Analisar {visual['screenshots_processed']} elementos visuais dos concorrentes",
                        "keywords_found": visual.get("keywords_from_images", [])[:10]
                    })

            logger.info("✅ Recomendações estratégicas geradas")
            return recommendations

        except Exception as e:
            logger.error(f"❌ Erro na geração de recomendações: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def refine_search_queries(self, current_context: str, existing_results: List[Dict]) -> List[str]:
        """
        Sugere novas queries de busca para aprimorar a coleta.

        Args:
            current_context: Contexto atual da busca
            existing_results: Resultados já obtidos

        Returns:
            Lista de queries refinadas
        """
        try:
            logger.info("🔍 Refinando queries de busca...")

            refined_queries = []

            # Analisa resultados existentes para identificar gaps
            if existing_results:
                # Extrai termos-chave dos resultados existentes
                all_text = " ".join([
                    result.get("title", "") + " " + result.get("snippet", "") + " " + result.get("description", "")
                    for result in existing_results
                ])

                # Identifica termos frequentes
                words = all_text.lower().split()
                from collections import Counter
                common_terms = [term for term, count in Counter(words).most_common(10) if len(term) > 3]

                # Gera queries refinadas baseadas no contexto
                base_context = current_context.lower()

                # Queries específicas por categoria
                if "marketing" in base_context or "publicidade" in base_context:
                    refined_queries.extend([
                        f"{current_context} estratégias digitais 2025",
                        f"{current_context} ROI campanhas",
                        f"{current_context} métricas engajamento"
                    ])

                if "concorrente" in base_context or "competidor" in base_context:
                    refined_queries.extend([
                        f"{current_context} análise SWOT",
                        f"{current_context} posicionamento mercado",
                        f"{current_context} diferenciais competitivos"
                    ])

                # Combina com termos encontrados
                for term in common_terms[:3]:
                    refined_queries.append(f"{current_context} {term} tendências")

            # Remove duplicatas e limita
            refined_queries = list(set(refined_queries))[:8]

            logger.info(f"✅ {len(refined_queries)} queries refinadas geradas")
            return refined_queries

        except Exception as e:
            logger.error(f"❌ Erro no refinamento de queries: {e}")
            return [current_context]  # Retorna query original em caso de erro

    async def analyze_initial_data(self, dados_coletados: List[Dict]) -> Dict[str, Any]:
        """
        Analisa dados iniciais coletados para fornecer insights preliminares.

        Args:
            dados_coletados: Lista de dados coletados na fase inicial

        Returns:
            Dict com insights iniciais
        """
        try:
            logger.info("📊 Analisando dados iniciais...")

            insights_iniciais = {
                "data_quality_assessment": {},
                "content_gaps": [],
                "priority_areas": [],
                "next_steps_suggestions": [],
                "timestamp": datetime.now().isoformat()
            }

            if not dados_coletados:
                insights_iniciais["content_gaps"].append("Nenhum dado coletado na fase inicial")
                return insights_iniciais

            # Avalia qualidade dos dados coletados
            total_content = 0
            quality_scores = []

            for item in dados_coletados:
                if isinstance(item, dict) and "data" in item:
                    content = str(item["data"])
                    score = self.get_content_quality_score(content)
                    quality_scores.append(score)
                    total_content += len(content)

            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                insights_iniciais["data_quality_assessment"] = {
                    "average_quality_score": avg_quality,
                    "total_items": len(dados_coletados),
                    "total_content_length": total_content,
                    "quality_distribution": {
                        "high_quality": len([s for s in quality_scores if s > 80]),
                        "medium_quality": len([s for s in quality_scores if 50 <= s <= 80]),
                        "low_quality": len([s for s in quality_scores if s < 50])
                    }
                }

                # Sugere próximos passos baseado na qualidade
                if avg_quality < 60:
                    insights_iniciais["next_steps_suggestions"].append({
                        "action": "Expandir coleta de dados",
                        "reason": "Qualidade média dos dados abaixo do ideal",
                        "priority": "alta"
                    })

                if avg_quality > 80:
                    insights_iniciais["next_steps_suggestions"].append({
                        "action": "Focar em análise profunda",
                        "reason": "Dados de alta qualidade disponíveis",
                        "priority": "média"
                    })

            # Identifica áreas prioritárias
            content_types = {}
            for item in dados_coletados:
                if isinstance(item, dict):
                    # Classifica tipo de conteúdo
                    content = str(item.get("data", ""))
                    if "instagram" in content.lower() or "facebook" in content.lower():
                        content_types["social_media"] = content_types.get("social_media", 0) + 1
                    elif "youtube" in content.lower():
                        content_types["video_content"] = content_types.get("video_content", 0) + 1
                    elif "site" in content.lower() or "website" in content.lower():
                        content_types["web_content"] = content_types.get("web_content", 0) + 1

            # Prioriza áreas com mais dados
            if content_types:
                sorted_types = sorted(content_types.items(), key=lambda x: x[1], reverse=True)
                insights_iniciais["priority_areas"] = [
                    {"area": area, "data_points": count, "priority": "alta" if i == 0 else "média"}
                    for i, (area, count) in enumerate(sorted_types[:3])
                ]

            logger.info("✅ Análise de dados iniciais concluída")
            return insights_iniciais

        except Exception as e:
            logger.error(f"❌ Erro na análise de dados iniciais: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Instância global do serviço
predictive_analytics_service = PredictiveAnalyticsService()