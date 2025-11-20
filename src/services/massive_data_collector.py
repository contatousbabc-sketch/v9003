#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Massive Data Collector
Coletor massivo de dados com integração robusta
"""

import os
import logging
import time
import json
import asyncio
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher

# Importa serviços existentes
from services.real_search_orchestrator import real_search_orchestrator
from services.social_media_extractor import SocialMediaExtractor
social_media_extractor = SocialMediaExtractor()
from services.auto_save_manager import salvar_etapa, salvar_erro

# Importa novos serviços da Etapa 1
# from services.search_api_manager import search_api_manager  # REMOVIDO - não existe
from services.trendfinder_client import trendfinder_client
from services.supadata_mcp_client import supadata_client
from services.visual_content_capture import visual_content_capture

logger = logging.getLogger(__name__)

class ContentDeduplicator:
    """✅ NOVO: Sistema avançado de eliminação de redundância de conteúdo"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Inicializa o deduplicador
        
        Args:
            similarity_threshold: Limiar de similaridade (0.0-1.0) para considerar conteúdo duplicado
        """
        self.similarity_threshold = similarity_threshold
        self.content_hashes: Set[str] = set()
        self.content_fingerprints: Dict[str, str] = {}
        self.url_seen: Set[str] = set()
        self.title_seen: Set[str] = set()
        self.duplicate_count = 0
        self.processed_count = 0
        
        logger.info(f"🔍 ContentDeduplicator inicializado (threshold: {similarity_threshold})")
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para comparação"""
        if not text:
            return ""
        
        # Remove caracteres especiais, espaços extras e converte para minúsculas
        normalized = re.sub(r'[^\w\s]', ' ', text.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def _generate_content_hash(self, content: str) -> str:
        """Gera hash MD5 do conteúdo normalizado"""
        normalized = self._normalize_text(content)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def _generate_content_fingerprint(self, content: str, length: int = 100) -> str:
        """Gera fingerprint do conteúdo (primeiros N caracteres normalizados)"""
        normalized = self._normalize_text(content)
        return normalized[:length] if len(normalized) > length else normalized
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos usando SequenceMatcher"""
        if not text1 or not text2:
            return 0.0
        
        norm1 = self._normalize_text(text1)
        norm2 = self._normalize_text(text2)
        
        if not norm1 or not norm2:
            return 0.0
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def is_duplicate_content(self, content: str, url: str = "", title: str = "") -> Tuple[bool, str]:
        """
        Verifica se o conteúdo é duplicado
        
        Returns:
            Tuple[bool, str]: (is_duplicate, reason)
        """
        self.processed_count += 1
        
        if not content or len(content.strip()) < 50:
            return True, "content_too_short"
        
        # 1. Verifica URL duplicada
        if url and url in self.url_seen:
            self.duplicate_count += 1
            return True, "duplicate_url"
        
        # 2. Verifica título duplicado
        if title:
            normalized_title = self._normalize_text(title)
            if normalized_title in self.title_seen:
                self.duplicate_count += 1
                return True, "duplicate_title"
        
        # 3. Verifica hash exato do conteúdo
        content_hash = self._generate_content_hash(content)
        if content_hash in self.content_hashes:
            self.duplicate_count += 1
            return True, "exact_duplicate"
        
        # 4. Verifica similaridade com conteúdos existentes
        fingerprint = self._generate_content_fingerprint(content)
        
        for existing_fingerprint in self.content_fingerprints.values():
            similarity = self._calculate_similarity(fingerprint, existing_fingerprint)
            if similarity >= self.similarity_threshold:
                self.duplicate_count += 1
                return True, f"similar_content_{similarity:.2f}"
        
        # Não é duplicado - adiciona aos registros
        self.content_hashes.add(content_hash)
        self.content_fingerprints[content_hash] = fingerprint
        
        if url:
            self.url_seen.add(url)
        if title:
            self.title_seen.add(self._normalize_text(title))
        
        return False, "unique_content"
    
    def deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicatas de uma lista de resultados
        
        Args:
            results: Lista de dicionários com conteúdo
            
        Returns:
            Lista filtrada sem duplicatas
        """
        if not results:
            return results
        
        unique_results = []
        duplicates_removed = 0
        
        logger.info(f"🔍 Iniciando deduplicação de {len(results)} itens...")
        
        for i, result in enumerate(results):
            if not isinstance(result, dict):
                continue
            
            # Extrai conteúdo do resultado
            content = ""
            url = result.get('url', result.get('page_url', ''))
            title = result.get('title', result.get('titulo', ''))
            
            # Tenta diferentes campos de conteúdo
            content_fields = ['content', 'conteudo', 'text', 'texto', 'description', 'descricao', 'snippet']
            for field in content_fields:
                if result.get(field):
                    content += str(result[field]) + " "
            
            # Verifica se é duplicado
            is_duplicate, reason = self.is_duplicate_content(content.strip(), url, title)
            
            if not is_duplicate:
                unique_results.append(result)
                logger.debug(f"✅ Item {i+1} mantido: {title[:50]}...")
            else:
                duplicates_removed += 1
                logger.debug(f"🗑️ Item {i+1} removido ({reason}): {title[:50]}...")
        
        logger.info(f"✅ Deduplicação concluída: {len(unique_results)} únicos, {duplicates_removed} duplicatas removidas")
        
        return unique_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da deduplicação"""
        return {
            'processed_items': self.processed_count,
            'duplicate_items': self.duplicate_count,
            'unique_items': self.processed_count - self.duplicate_count,
            'duplicate_rate': (self.duplicate_count / max(self.processed_count, 1)) * 100,
            'similarity_threshold': self.similarity_threshold,
            'unique_urls': len(self.url_seen),
            'unique_titles': len(self.title_seen),
            'unique_content_hashes': len(self.content_hashes)
        }

class MassiveDataCollector:
    """Coletor de dados massivo para criar JSON gigante"""

    def __init__(self):
        """✅ MELHORADO: Inicializa o coletor massivo com sistema de deduplicação"""
        self.collected_data = {}
        self.total_content_length = 0
        self.sources_count = 0
        
        # ✅ NOVO: Sistema de deduplicação integrado
        self.deduplicator = ContentDeduplicator(similarity_threshold=0.85)

        logger.info("🚀 Massive Data Collector inicializado com sistema de deduplicação")

    def collect_comprehensive_data(
        self,
        produto: str,
        nicho: str,
        publico: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Método de compatibilidade para coleta de dados"""
        try:
            # Constrói query a partir dos parâmetros
            query_parts = []
            if produto:
                query_parts.append(produto)
            if nicho:
                query_parts.append(nicho)
            if publico:
                query_parts.append(publico)
            
            query = " ".join(query_parts) if query_parts else "análise de mercado"
            
            # Contexto da análise
            context = {
                "produto": produto,
                "nicho": nicho,
                "publico": publico,
                "session_id": session_id
            }
            
            # Chama o método assíncrono de forma síncrona
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.execute_massive_collection(query, context, session_id)
                )
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Erro na coleta de dados: {e}")
            return {"error": str(e), "success": False}

    async def execute_massive_collection(
        self,
        query: str,
        context: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """Executa coleta massiva de dados com novos serviços"""

        logger.info(f"🚀 INICIANDO COLETA MASSIVA APRIMORADA - Sessão: {session_id}")
        start_time = time.time()

        # Estrutura de dados consolidados
        massive_data = {
            "session_id": session_id,
            "query": query,
            "context": context,
            "collection_started": datetime.now().isoformat(),
            "web_search_data": {},
            "social_media_data": {},
            "trends_data": {},
            "supadata_results": {},
            "visual_content": {},
            "extracted_content": [],
            "statistics": {
                "total_sources": 0,
                "total_content_length": 0,
                "collection_time": 0,
                "sources_by_type": {},
                "screenshot_count": 0,
                "api_rotations": {}
            }
        }

        try:
            # FASE 1: Busca Web Intercalada com Rotação de APIs
            logger.info("🔍 FASE 1: Executando busca web intercalada...")
            # web_results = await search_api_manager.interleaved_search(query)  # REMOVIDO
            web_results = []  # Placeholder
            massive_data["web_search_data"] = web_results

            # FASE 2: Coleta de Tendências via TrendFinder MCP
            logger.info("📈 FASE 2: Coletando tendências via TrendFinder...")
            if trendfinder_client.is_available():
                trends_results = await trendfinder_client.search(query)
                massive_data["trends_data"] = trends_results
            else:
                logger.warning("⚠️ TrendFinder não disponível")
                massive_data["trends_data"] = {"success": False, "error": "TrendFinder não configurado"}

            # FASE 3: Dados Sociais via Supadata MCP
            logger.info("📊 FASE 3: Coletando dados sociais via Supadata...")
            if supadata_client.is_available():
                supadata_results = await supadata_client.search(query, "all")
                massive_data["supadata_results"] = supadata_results
            else:
                logger.warning("⚠️ Supadata não disponível")
                massive_data["supadata_results"] = {"success": False, "error": "Supadata não configurado"}

            # FASE 4: Extração de Redes Sociais (método existente como fallback)
            logger.info("📱 FASE 4: Extraindo dados de redes sociais (fallback)...")
            try:
                # Usa método existente do social_media_extractor
                social_results = social_media_extractor.search_all_platforms(query, 15)
                
                # Adapta formato para compatibilidade
                if social_results.get("success"):
                    social_results = {
                        "success": True,
                        "all_platforms_data": social_results,
                        "total_posts": social_results.get("total_results", 0),
                        "platforms_analyzed": len(social_results.get("platforms", [])),
                        "extracted_at": datetime.now().isoformat()
                    }
                else:
                    social_results = {
                        "success": False,
                        "error": "Falha na extração de redes sociais",
                        "all_platforms_data": {"platforms": {}},
                        "total_posts": 0
                    }
            except Exception as social_error:
                logger.error(f"❌ Erro na extração social: {social_error}")
                social_results = {
                    "success": False,
                    "error": str(social_error),
                    "all_platforms_data": {"platforms": {}},
                    "total_posts": 0
                }
                
            massive_data["social_media_data"] = social_results

            # FASE 5: Seleção de URLs Relevantes
            logger.info("🎯 FASE 5: Selecionando URLs mais relevantes...")
            selected_urls = visual_content_capture.select_top_urls(web_results, max_urls=8)

            # FASE 6: Extração de Imagens Virais (PRIORITÁRIO)
            logger.info("🔥 FASE 6: Extraindo imagens virais reais...")
            try:
                from .viral_integration_service import viral_image_finder
                viral_images, results_file = await viral_image_finder.find_viral_images(query)
                
                massive_data["viral_images"] = {
                    "success": True,
                    "total_images": len(viral_images),
                    "images": [
                        {
                            "image_url": img.image_url,
                            "post_url": img.post_url,
                            "platform": img.platform,
                            "title": img.title,
                            "viral_score": img.engagement_score,
                            "local_path": img.image_path
                        } for img in viral_images
                    ]
                }
                massive_data["statistics"]["viral_images_count"] = len(viral_images)
                logger.info(f"✅ {len(viral_images)} imagens virais extraídas com sucesso")
                
            except Exception as viral_error:
                logger.error(f"❌ Erro na extração de imagens virais: {viral_error}")
                massive_data["viral_images"] = {"success": False, "error": str(viral_error)}
                massive_data["statistics"]["viral_images_count"] = 0

            # FASE 7: Captura de Screenshots (FALLBACK)
            logger.info("📸 FASE 7: Capturando screenshots das URLs selecionadas...")
            if selected_urls:
                try:
                    screenshot_results = await visual_content_capture.capture_screenshots(
                        selected_urls, session_id
                    )
                    massive_data["visual_content"] = screenshot_results
                    massive_data["statistics"]["screenshot_count"] = screenshot_results.get("successful_captures", 0)
                except Exception as capture_error:
                    logger.error(f"❌ Erro na captura de screenshots: {capture_error}")
                    massive_data["visual_content"] = {"success": False, "error": str(capture_error)}
                    massive_data["statistics"]["screenshot_count"] = 0
            else:
                logger.warning("⚠️ Nenhuma URL selecionada para screenshots")
                massive_data["visual_content"] = {"success": False, "error": "Nenhuma URL disponível"}

            # FASE 7: Consolidação e Processamento
            logger.info("🔗 FASE 7: Consolidando dados coletados...")

            # Extrai e processa conteúdo
            all_results = []

            # Processa resultados web - Handle both dict and list formats
            if isinstance(web_results, dict) and web_results.get("all_results"):
                for provider_result in web_results["all_results"]:
                    if provider_result.get("success") and provider_result.get("results"):
                        all_results.extend(provider_result["results"])
            elif isinstance(web_results, list):
                all_results.extend(web_results)

            # Processa resultados sociais existentes - CORRIGIDO
            if isinstance(social_results, dict) and social_results.get("all_platforms_data"):
                platforms = social_results["all_platforms_data"].get("platforms", {})
                
                # Verifica se platforms é um dict ou list
                if isinstance(platforms, dict):
                    # Se é dict, itera pelos items
                    for platform, data in platforms.items():
                        if isinstance(data, dict) and "results" in data:
                            all_results.extend(data["results"])
                elif isinstance(platforms, list):
                    # Se é list, itera diretamente
                    for platform_data in platforms:
                        if isinstance(platform_data, dict) and "results" in platform_data:
                            all_results.extend(platform_data["results"])
                        elif isinstance(platform_data, dict) and "platform" in platform_data:
                            # Se o item da lista tem estrutura diferente
                            platform_results = platform_data.get("data", {}).get("results", [])
                            all_results.extend(platform_results)

            # Processa tendências do TrendFinder
            if massive_data["trends_data"].get("success"):
                trends = massive_data["trends_data"].get("trends", [])
                all_results.extend([{"source": "TrendFinder", "content": trend} for trend in trends])

            # Processa dados do Supadata
            if massive_data["supadata_results"].get("success"):
                posts = massive_data["supadata_results"].get("posts", [])
                all_results.extend([{"source": "Supadata", "content": post} for post in posts])

            # ✅ NOVO: Aplica deduplicação nos resultados consolidados
            logger.info(f"🔍 Aplicando deduplicação em {len(all_results)} itens coletados...")
            
            # Deduplicação antes de salvar
            unique_results = self.deduplicator.deduplicate_results(all_results)
            dedup_stats = self.deduplicator.get_stats()
            
            logger.info(f"✅ Deduplicação concluída: {len(unique_results)} únicos de {len(all_results)} originais")
            logger.info(f"📊 Taxa de duplicação: {dedup_stats['duplicate_rate']:.1f}%")
            
            massive_data["extracted_content"] = unique_results
            massive_data["deduplication_stats"] = dedup_stats

            # Calcula estatísticas finais (com dados deduplicados)
            collection_time = time.time() - start_time
            total_sources = len(unique_results)  # Usa resultados únicos
            total_content = sum(len(str(item)) for item in unique_results)  # Usa resultados únicos

            # Atualiza estatísticas com informações dos novos serviços
            sources_by_type = {
                "web_search_intercalado": web_results.get("successful_searches", 0) if isinstance(web_results, dict) else len(web_results) if isinstance(web_results, list) else 0,
                "social_media_fallback": self._count_social_results(social_results),
                "trendfinder_mcp": len(massive_data["trends_data"].get("trends", [])),
                "supadata_mcp": massive_data["supadata_results"].get("total_results", 0),
                "screenshots": massive_data["statistics"]["screenshot_count"]
            }

            massive_data["statistics"].update({
                "total_sources": total_sources,
                "total_content_length": total_content,
                "collection_time": collection_time,
                "sources_by_type": sources_by_type,
                # "api_rotations": search_api_manager.get_provider_stats()  # REMOVIDO
                "api_rotations": {}  # Placeholder
            })

            # Gera relatório de coleta com referências às imagens
            collection_report = await self._generate_collection_report(massive_data, session_id)

            # Salva dados coletados
            salvar_etapa("massive_data_collected", massive_data, categoria="coleta_massiva")

            logger.info(f"✅ COLETA MASSIVA APRIMORADA CONCLUÍDA")
            logger.info(f"📊 {total_sources} fontes únicas coletadas em {collection_time:.2f}s")
            logger.info(f"📝 {total_content:,} caracteres de conteúdo único")
            logger.info(f"📸 {massive_data['statistics']['screenshot_count']} screenshots capturados")
            logger.info(f"🔍 Deduplicação: {dedup_stats['duplicate_items']} duplicatas removidas ({dedup_stats['duplicate_rate']:.1f}%)")

            return massive_data

        except Exception as e:
            logger.error(f"❌ Erro durante a coleta massiva: {e}", exc_info=True)
            salvar_erro("massive_data_collection", e, contexto={"query": query, "session_id": session_id})
            return {"error": "Falha na coleta massiva de dados", "details": str(e)}

    def _count_social_results(self, social_results: Dict[str, Any]) -> int:
        """Conta resultados sociais de forma segura"""
        try:
            platforms = social_results.get("all_platforms_data", {}).get("platforms", {})
            total_count = 0
            
            if isinstance(platforms, dict):
                for data in platforms.values():
                    if isinstance(data, dict) and "results" in data:
                        total_count += len(data["results"])
            elif isinstance(platforms, list):
                for platform_data in platforms:
                    if isinstance(platform_data, dict):
                        if "results" in platform_data:
                            total_count += len(platform_data["results"])
                        elif "data" in platform_data and isinstance(platform_data["data"], dict):
                            results = platform_data["data"].get("results", [])
                            total_count += len(results)
            
            return total_count
        except Exception as e:
            logger.error(f"Erro ao contar resultados sociais: {e}")
            return 0

    def _collect_urls_from_web_search(self, web_data: Dict[str, Any], all_urls: set):
        """Coleta URLs dos dados de busca web"""
        try:
            # Enhanced search results
            enhanced_results = web_data.get("enhanced_search_results", {})
            for provider_results in ["exa_results", "google_results", "other_results"]:
                results = enhanced_results.get(provider_results, [])
                for result in results:
                    if result.get("url"):
                        all_urls.add(result["url"])

            # Production search results
            production_results = web_data.get("production_search_results", {}).get("results", [])
            for result in production_results:
                if result.get("url"):
                    all_urls.add(result["url"])

            # Additional queries results
            additional_results = web_data.get("additional_queries_results", {})
            for query_results in additional_results.values():
                if isinstance(query_results, dict) and query_results.get("results"):
                    for result in query_results["results"]:
                        if result.get("url"):
                            all_urls.add(result["url"])
        except Exception as e:
            logger.error(f"❌ Erro ao coletar URLs web: {e}")

    def _collect_urls_from_social_data(self, social_data: Dict[str, Any], all_urls: set):
        """Coleta URLs dos dados de redes sociais"""
        try:
            platforms_data = social_data.get("all_platforms_data", {}).get("platforms", {})
            
            # Trata tanto dict quanto list
            if isinstance(platforms_data, dict):
                for platform_data in platforms_data.values():
                    if platform_data.get("results"):
                        for post in platform_data["results"]:
                            if post.get("url"):
                                all_urls.add(post["url"])
            elif isinstance(platforms_data, list):
                for platform_data in platforms_data:
                    if isinstance(platform_data, dict):
                        results = platform_data.get("results", [])
                        if not results and "data" in platform_data:
                            results = platform_data["data"].get("results", [])
                        
                        for post in results:
                            if post.get("url"):
                                all_urls.add(post["url"])
        except Exception as e:
            logger.error(f"❌ Erro ao coletar URLs sociais: {e}")

    def _collect_urls_from_deep_navigation(self, deep_data: Dict[str, Any], all_urls: set):
        """Coleta URLs da navegação profunda"""
        try:
            websailor_data = deep_data.get("websailor_navigation", {})
            conteudo_consolidado = websailor_data.get("conteudo_consolidado", {})
            fontes_detalhadas = conteudo_consolidado.get("fontes_detalhadas", [])

            for fonte in fontes_detalhadas:
                if fonte.get("url"):
                    all_urls.add(fonte["url"])
        except Exception as e:
            logger.error(f"❌ Erro ao coletar URLs navegação: {e}")

    def _generate_additional_queries(self, base_query: str, context: Dict[str, Any]) -> List[str]:
        """Gera queries adicionais baseadas no contexto"""
        additional_queries = []

        segmento = context.get("segmento", "")
        produto = context.get("produto", "")

        if segmento and produto:
            additional_queries.extend([
                f"{segmento} {produto} mercado brasileiro 2025",
                f"{segmento} {produto} concorrentes Brasil",
                f"{segmento} {produto} tendências futuro",
                f"como vender {produto} {segmento}",
                f"estratégias marketing {segmento} {produto}",
                f"público-alvo {segmento} {produto}",
                f"preços {produto} {segmento} Brasil",
                f"cases sucesso {segmento} {produto}"
            ])

        return additional_queries[:5]  # Limita a 5 queries adicionais

    def _analyze_social_engagement(self, platforms_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa métricas de engajamento das redes sociais"""
        engagement_metrics = {
            "total_posts": 0,
            "platforms_active": 0,
            "avg_engagement_score": 0,
            "top_performing_platforms": []
        }

        try:
            platforms = platforms_data.get("platforms", {})
            platform_scores = []

            # Trata tanto dict quanto list
            if isinstance(platforms, dict):
                for platform_name, platform_data in platforms.items():
                    posts = platform_data.get("results", [])
                    if posts:
                        engagement_metrics["total_posts"] += len(posts)
                        engagement_metrics["platforms_active"] += 1

                        # Calcula score básico da plataforma
                        platform_score = len(posts) * 10  # Score simples baseado no número de posts
                        platform_scores.append({
                            "platform": platform_name,
                            "score": platform_score,
                            "posts_count": len(posts)
                        })
            elif isinstance(platforms, list):
                for i, platform_data in enumerate(platforms):
                    if isinstance(platform_data, dict):
                        platform_name = platform_data.get("platform", f"Platform_{i}")
                        results = platform_data.get("results", [])
                        if not results and "data" in platform_data:
                            results = platform_data["data"].get("results", [])
                        
                        if results:
                            engagement_metrics["total_posts"] += len(results)
                            engagement_metrics["platforms_active"] += 1

                            platform_score = len(results) * 10
                            platform_scores.append({
                                "platform": platform_name,
                                "score": platform_score,
                                "posts_count": len(results)
                            })

            # Ordena plataformas por score
            platform_scores.sort(key=lambda x: x["score"], reverse=True)
            engagement_metrics["top_performing_platforms"] = platform_scores[:3]

            if platform_scores:
                engagement_metrics["avg_engagement_score"] = sum(p["score"] for p in platform_scores) / len(platform_scores)

        except Exception as e:
            logger.error(f"❌ Erro na análise de engajamento: {e}")
            engagement_metrics["error"] = str(e)

        return engagement_metrics

    def _extract_trending_topics(self, all_posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrai tópicos trending dos posts coletados"""
        trending_topics = {
            "keywords_frequency": {},
            "hashtags_found": [],
            "common_themes": []
        }

        try:
            all_text = []
            hashtags = []

            for post in all_posts:
                # Coleta texto dos posts
                post_text = ""
                if post.get("content"):
                    post_text += post["content"] + " "
                if post.get("title"):
                    post_text += post["title"] + " "
                if post.get("text"):
                    post_text += post["text"] + " "
                if post.get("caption"):
                    post_text += post["caption"] + " "

                if post_text.strip():
                    all_text.append(post_text.lower())

                # Coleta hashtags
                hashtags.extend(post.get("hashtags_detected", []))

            # Análise básica de palavras-chave
            if all_text:
                combined_text = " ".join(all_text)
                words = combined_text.split()
                word_freq = {}

                for word in words:
                    if len(word) > 3:  # Ignora palavras muito curtas
                        word_freq[word] = word_freq.get(word, 0) + 1

                # Top 20 palavras mais frequentes
                sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
                trending_topics["keywords_frequency"] = dict(sorted_words[:20])

            # Hashtags únicas
            trending_topics["hashtags_found"] = list(set(hashtags))[:10]

            # Temas comuns (básico)
            common_themes = []
            if trending_topics["keywords_frequency"]:
                top_words = list(trending_topics["keywords_frequency"].keys())[:10]
                for i in range(0, len(top_words), 2):
                    if i + 1 < len(top_words):
                        theme = f"{top_words[i]} + {top_words[i+1]}"
                        common_themes.append(theme)

            trending_topics["common_themes"] = common_themes[:5]

        except Exception as e:
            logger.error(f"❌ Erro na extração de trending topics: {e}")
            trending_topics["error"] = str(e)

        return trending_topics

    def _analyze_content_quality(self, websailor_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa qualidade do conteúdo navegado"""
        quality_metrics = {
            "content_depth_score": 0,
            "source_reliability_score": 0,
            "information_richness": 0,
            "total_insights": 0
        }

        try:
            conteudo_consolidado = websailor_results.get("conteudo_consolidado", {})

            # Score de profundidade baseado em insights
            insights = conteudo_consolidado.get("insights_principais", [])
            quality_metrics["total_insights"] = len(insights)
            quality_metrics["content_depth_score"] = min(len(insights) * 10, 100)

            # Score de confiabilidade baseado nas fontes
            fontes = conteudo_consolidado.get("fontes_detalhadas", [])
            if fontes:
                avg_quality = sum(fonte.get("quality_score", 0) for fonte in fontes) / len(fontes)
                quality_metrics["source_reliability_score"] = avg_quality

            # Score de riqueza de informação baseado no tamanho do conteúdo
            navegacao_profunda = websailor_results.get("navegacao_profunda", {})
            total_chars = navegacao_profunda.get("total_caracteres_analisados", 0)
            quality_metrics["information_richness"] = min(total_chars / 1000, 100)  # Normaliza para 0-100

        except Exception as e:
            logger.error(f"❌ Erro na análise de qualidade: {e}")
            quality_metrics["error"] = str(e)

        return quality_metrics

    def _calculate_final_statistics(self, massive_data: Dict[str, Any], collection_time: float):
        """Calcula estatísticas finais da coleta"""
        pass

    async def _generate_collection_report(self, massive_data: Dict[str, Any], session_id: str):
        """Gera um relatório de coleta com referências às imagens capturadas."""
        logger.info(f"📝 Gerando relatório de coleta para sessão: {session_id}")
        
        # Cria diretório da sessão
        session_dir = f"analyses_data/{session_id}"
        os.makedirs(session_dir, exist_ok=True)

        report_data = {
            "session_id": session_id,
            "query": massive_data["query"],
            "collection_timestamp": massive_data["collection_started"],
            "summary": {
                "total_sources": massive_data["statistics"]["total_sources"],
                "total_content_length": massive_data["statistics"]["total_content_length"],
                "collection_duration": f"{massive_data['statistics']['collection_time']:.2f}s",
                "screenshot_count": massive_data["statistics"]["screenshot_count"],
                "api_rotations": massive_data["statistics"]["api_rotations"],
                "sources_by_type": massive_data["statistics"]["sources_by_type"]
            },
            "visual_references": [],
            "errors": []
        }
        
        # Gera relatório em Markdown
        markdown_report = self._generate_markdown_report(massive_data, session_id)
        
        # Salva relatório de coleta
        report_path = f"{session_dir}/relatorio_coleta.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        logger.info(f"✅ Relatório de coleta salvo: {report_path}")

        if massive_data["visual_content"] and massive_data["visual_content"].get("success"):
            report_data["visual_references"] = massive_data["visual_content"].get("screenshots", [])
            logger.info(f"🖼️ {len(report_data['visual_references'])} referências visuais incluídas no relatório.")
        else:
            report_data["errors"].append({
                "source": "Visual Content Capture",
                "message": massive_data["visual_content"].get("error", "Nenhum dado de visual disponível.")
            })
            logger.warning("🖼️ Nenhum dado visual para incluir no relatório.")

        # Adicionar erros de outras fontes, se houver
        if massive_data.get("web_search_data", {}).get("error"):
            report_data["errors"].append({"source": "Web Search", "message": massive_data["web_search_data"]["error"]})
        if massive_data.get("trends_data", {}).get("error"):
            report_data["errors"].append({"source": "TrendFinder", "message": massive_data["trends_data"]["error"]})
        if massive_data.get("supadata_results", {}).get("error"):
            report_data["errors"].append({"source": "Supadata", "message": massive_data["supadata_results"]["error"]})
        if massive_data.get("social_media_data", {}).get("error"):
             report_data["errors"].append({"source": "Social Media Extractor", "message": massive_data["social_media_data"]["error"]})

        try:
            salvar_etapa("collection_report", report_data, categoria="relatorios")
            logger.info("✅ Relatório de coleta gerado com sucesso.")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório de coleta: {e}")
            
        return report_data
    
    def _generate_markdown_report(self, massive_data: Dict[str, Any], session_id: str) -> str:
        """Gera relatório em formato Markdown"""
        
        report = f"""# RELATÓRIO DE COLETA DE DADOS - ARQV18 Enhanced v18.0

**Sessão:** {session_id}  
**Query:** {massive_data.get('query', 'N/A')}  
**Iniciado em:** {massive_data.get('collection_started', 'N/A')}  
**Duração:** {massive_data.get('statistics', {}).get('collection_time', 0):.2f} segundos

---

## RESUMO DA COLETA

### Estatísticas Gerais:
- **Total de Fontes:** {massive_data.get('statistics', {}).get('total_sources', 0)}
- **Conteúdo Coletado:** {massive_data.get('statistics', {}).get('total_content_length', 0):,} caracteres
- **Screenshots:** {massive_data.get('statistics', {}).get('screenshot_count', 0)}
- **APIs Utilizadas:** {len(massive_data.get('statistics', {}).get('api_rotations', {}))}

### Fontes por Tipo:
"""
        
        # Adiciona estatísticas por tipo
        sources_by_type = massive_data.get('statistics', {}).get('sources_by_type', {})
        # Corrigido: Verifica se sources_by_type é um dicionário antes de iterar
        if isinstance(sources_by_type, dict):
            for source_type, count in sources_by_type.items():
                report += f"- **{source_type.replace('_', ' ').title()}:** {count}\n"
        else:
            # Se não for um dicionário, tenta tratá-lo como lista ou outro tipo
            report += f"- **Dados de fontes:** {sources_by_type}\n"
        
        report += "\n---\n\n"
        
        # Adiciona dados de busca web
        web_data = massive_data.get('web_search_data', {})
        if web_data.get('all_results'):
            report += "## DADOS DE BUSCA WEB\n\n"
            for i, provider_result in enumerate(web_data['all_results'], 1):
                if provider_result.get('success'):
                    provider = provider_result.get('provider', 'Unknown')
                    results_count = len(provider_result.get('results', []))
                    report += f"### {provider} ({results_count} resultados)\n\n"
                    
                    for j, result in enumerate(provider_result.get('results', [])[:5], 1):
                        report += f"**{j}. {result.get('title', 'Sem título')}**  \n"
                        report += f"URL: {result.get('url', 'N/A')}  \n"
                        report += f"Resumo: {result.get('snippet', 'N/A')[:200]}...\n\n"
        
        # Adiciona dados sociais
        social_data = massive_data.get('social_media_data', {})
        if social_data.get('success'):
            report += "## DADOS DE REDES SOCIAIS\n\n"
            platforms = social_data.get('all_platforms_data', {}).get('platforms', {})
            
            # Corrigido: Verifica o tipo de platforms antes de iterar
            if isinstance(platforms, dict):
                for platform, data in platforms.items():
                    results = data.get('results', [])
                    if results:
                        report += f"### {platform.title()} ({len(results)} posts)\n\n"
                        for i, post in enumerate(results[:3], 1):
                            title = post.get('title', post.get('text', post.get('caption', 'Post sem título')))
                            report += f"**{i}.** {title[:100]}...\n\n"
            elif isinstance(platforms, list):
                # Se for uma lista, processa cada item
                for i, platform_data in enumerate(platforms):
                    if isinstance(platform_data, dict):
                        platform_name = platform_data.get('platform', f'Platform_{i}')
                        results = platform_data.get('results', [])
                        if results:
                            report += f"### {platform_name.title()} ({len(results)} posts)\n\n"
                            for j, post in enumerate(results[:3], 1):
                                title = post.get('title', post.get('text', post.get('caption', 'Post sem título')))
                                report += f"**{j}.** {title[:100]}...\n\n"
        
        # Adiciona screenshots
        visual_content = massive_data.get('visual_content', {})
        if visual_content.get('success'):
            screenshots = visual_content.get('screenshots', [])
            if screenshots:
                report += "## EVIDÊNCIAS VISUAIS\n\n"
                for i, screenshot in enumerate(screenshots, 1):
                    report += f"### Screenshot {i}\n"
                    report += f"**URL:** {screenshot.get('url', 'N/A')}  \n"
                    report += f"**Título:** {screenshot.get('title', 'N/A')}  \n"
                    report += f"![Screenshot {i}]({screenshot.get('filepath', '')})  \n\n"
        
        # Adiciona contexto da análise
        context = massive_data.get('context', {})
        if context:
            report += "## CONTEXTO DA ANÁLISE\n\n"
            for key, value in context.items():
                if value:
                    report += f"**{key.replace('_', ' ').title()}:** {value}  \n"
        
        report += f"\n---\n\n*Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*"
        
        return report

    def _save_massive_json(self, massive_data: Dict[str, Any], session_id: str):
        """Salva o JSON gigante"""
        # Esta função foi substituída pela lógica dentro de execute_massive_collection
        pass

# Instância global
massive_data_collector = MassiveDataCollector()
