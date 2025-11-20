#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - External AI Verifier Integration
Integração do módulo External AI Verifier ao app principal
"""

import os
import sys
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ExternalAIVerifierIntegration:
    """Integração do External AI Verifier com o app principal"""

    def __init__(self):
        """Inicializa a integração"""
        # Adiciona o caminho do módulo externo ao Python path
        external_module_path = os.path.join(os.getcwd(), "external_ai_verifier", "src")
        external_services_path = os.path.join(external_module_path, "services")
        
        if external_module_path not in sys.path:
            sys.path.insert(0, external_module_path)
        if external_services_path not in sys.path:
            sys.path.insert(0, external_services_path)

        self.module_available = self._check_module_availability()

        if self.module_available:
            logger.info("✅ External AI Verifier integrado com sucesso")
        else:
            logger.warning("⚠️ External AI Verifier não disponível - executando em modo fallback")

    def _check_module_availability(self) -> bool:
        """Verifica se o módulo External AI Verifier está disponível"""
        try:
            from external_review_agent import ExternalReviewAgent
            return True
        except ImportError as e:
            logger.warning(f"External AI Verifier não encontrado: {e}")
            return False

    def verify_session_data(self, session_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa verificação dos dados de uma sessão específica

        Args:
            session_id (str): ID da sessão para verificar
            data (Dict): Dados opcionais para verificar diretamente

        Returns:
            Dict[str, Any]: Resultado da verificação
        """
        try:
            if not self.module_available:
                return self._fallback_verification_result(session_id)

            logger.info(f"🔍 Iniciando verificação AI para sessão: {session_id}")

            # Importa o agente de verificação
            from external_review_agent import ExternalReviewAgent

            # Cria instância do agente
            agent = ExternalReviewAgent()

            # Se dados foram fornecidos diretamente, usa eles
            if data:
                logger.info(f"📊 Usando dados fornecidos diretamente para sessão {session_id}")
                # Converte dados para formato de análise
                analysis_data = self._prepare_data_for_analysis(data, session_id)
                if analysis_data.get('items'):
                    result = agent.process_batch(analysis_data['items'])
                    result['session_id'] = session_id
                    result['data_source'] = 'direct_input'
                else:
                    result = {
                        'success': False,
                        'error': 'Nenhum item válido encontrado nos dados fornecidos',
                        'session_id': session_id
                    }
            else:
                # Tenta encontrar dados de consolidação, se não encontrar, usa fallback
                result = agent.analyze_session_consolidacao(session_id)
                
                # Se não encontrou dados de consolidação, cria dados de exemplo para teste
                if not result.get('success') and 'não encontrado' in result.get('error', ''):
                    logger.warning(f"⚠️ Dados de consolidação não encontrados para {session_id}, usando dados de exemplo")
                    example_data = self._create_example_data_for_testing(session_id)
                    analysis_data = self._prepare_data_for_analysis(example_data, session_id)
                    if analysis_data.get('items'):
                        result = agent.process_batch(analysis_data['items'])
                        result['session_id'] = session_id
                        result['data_source'] = 'example_data'
                        result['note'] = 'Dados de exemplo usados devido à ausência de dados de consolidação'

            # Verifica se foi bem-sucedido (se tem estatísticas, foi sucesso)
            if result.get('statistics') or result.get('batch_info'):
                result['success'] = True
                logger.info(f"✅ Verificação AI concluída para sessão {session_id}")
                logger.info(f"📊 Items processados: {result.get('statistics', {}).get('total_processed', 0)}")
                logger.info(f"✅ Aprovados: {result.get('statistics', {}).get('approved', 0)}")
                logger.info(f"❌ Rejeitados: {result.get('statistics', {}).get('rejected', 0)}")
            else:
                result['success'] = False
                logger.error(f"❌ Falha na verificação AI: {result.get('error', 'Erro desconhecido')}")

            return result

        except Exception as e:
            logger.error(f"❌ Erro durante verificação AI: {e}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'fallback_used': True
            }

    async def verify_batch_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa verificação de um lote de dados

        Args:
            input_data (Dict[str, Any]): Dados para verificação

        Returns:
            Dict[str, Any]: Resultado da verificação
        """
        try:
            if not self.module_available:
                return self._fallback_batch_result(input_data)

            logger.info(f"🔍 Iniciando verificação AI em lote: {len(input_data.get('items', []))} itens")

            # Importa o agente de verificação
            from external_review_agent import ExternalReviewAgent

            # Cria instância do agente
            agent = ExternalReviewAgent()

            # ✅ CORRIGIDO: analyze_content_batch NÃO é async, removido await
            result = agent.analyze_content_batch(input_data)

            if result.get('success', False):
                logger.info(f"✅ Verificação AI em lote concluída")
                logger.info(f"📊 Items processados: {result.get('total_items', 0)}")
                stats = result.get('statistics', {})
                logger.info(f"✅ Aprovados: {stats.get('approved', 0)}")
                logger.info(f"❌ Rejeitados: {stats.get('rejected', 0)}")
            else:
                logger.error(f"❌ Falha na verificação AI em lote")

            return result

        except Exception as e:
            logger.error(f"❌ Erro durante verificação AI em lote: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'fallback_used': True
            }

    def _prepare_data_for_analysis(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Prepara dados para análise, tratando diferentes estruturas de forma mais robusta
        
        Args:
            data: Dados de entrada em formato variado
            session_id: ID da sessão
            
        Returns:
            Dict com items formatados para análise
        """
        items = []
        raw_items = []
        
        try:
            logger.info(f"🔍 Analisando estrutura de dados para sessão {session_id}")
            logger.info(f"📋 Chaves principais encontradas: {list(data.keys())}")
            
            # Estratégia 1: data.dados_web (estrutura padrão do sistema)
            if 'data' in data and isinstance(data['data'], dict) and 'dados_web' in data['data']:
                raw_items = data['data']['dados_web']
                logger.info(f"📊 Estrutura 1 (data.dados_web): Encontrados {len(raw_items)} items")
            
            # Estratégia 2: dados_web direto
            elif 'dados_web' in data and isinstance(data['dados_web'], list):
                raw_items = data['dados_web']
                logger.info(f"📊 Estrutura 2 (dados_web direto): Encontrados {len(raw_items)} items")
            
            # Estratégia 3: items direto (formato external_ai_verifier)
            elif 'items' in data and isinstance(data['items'], list):
                raw_items = data['items']
                logger.info(f"📊 Estrutura 3 (items direto): Encontrados {len(raw_items)} items")
            
            # Estratégia 4: busca por qualquer array de objetos
            else:
                logger.info("🔍 Buscando arrays de dados em todas as chaves...")
                for key, value in data.items():
                    if isinstance(value, list) and value and len(value) > 0:
                        # Verifica se é uma lista de dicionários (dados válidos)
                        if isinstance(value[0], dict):
                            raw_items = value
                            logger.info(f"📊 Estrutura 4 (array em '{key}'): Encontrados {len(raw_items)} items")
                            break
                    elif isinstance(value, dict):
                        # Busca recursivamente em objetos aninhados
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, list) and sub_value and len(sub_value) > 0:
                                if isinstance(sub_value[0], dict):
                                    raw_items = sub_value
                                    logger.info(f"📊 Estrutura 4 (array aninhado em '{key}.{sub_key}'): Encontrados {len(raw_items)} items")
                                    break
                        if raw_items:
                            break
            
            if not raw_items:
                logger.warning("⚠️ Nenhum array de dados encontrado. Estrutura de dados:")
                logger.warning(f"📋 Dados recebidos: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
                return {
                    'items': [],
                    'total_items': 0,
                    'session_id': session_id,
                    'error': 'Nenhum array de dados válido encontrado na estrutura fornecida'
                }
            
            # Converte items para formato de análise
            logger.info(f"🔄 Convertendo {len(raw_items)} items para formato de análise...")
            
            for idx, item in enumerate(raw_items):
                if not item or not isinstance(item, dict):
                    logger.debug(f"⚠️ Item {idx} inválido (não é dict): {type(item)}")
                    continue
                
                # Extrai conteúdo textual com priorização inteligente
                content_parts = []
                
                # Campos de conteúdo principal (prioridade alta)
                primary_fields = ['conteudo', 'content', 'text', 'body']
                for field in primary_fields:
                    if field in item and item[field] and str(item[field]).strip():
                        content_parts.append(str(item[field]).strip())
                        break  # Usa apenas o primeiro campo de conteúdo encontrado
                
                # Campos de título/descrição (sempre incluir se disponível)
                secondary_fields = ['titulo', 'title', 'descricao', 'description', 'summary']
                for field in secondary_fields:
                    if field in item and item[field] and str(item[field]).strip():
                        title_content = str(item[field]).strip()
                        if title_content not in ' '.join(content_parts):  # Evita duplicação
                            content_parts.append(title_content)
                
                if not content_parts:
                    logger.debug(f"⚠️ Item {idx} sem conteúdo textual válido. Campos disponíveis: {list(item.keys())}")
                    continue
                
                # Cria item formatado para external_ai_verifier
                formatted_item = {
                    'id': f"{session_id}_item_{idx+1:03d}",
                    'content': ' | '.join(content_parts),  # Separa título do conteúdo
                    'title': item.get('titulo', item.get('title', f'Item {idx+1}')),
                    'url': item.get('url', item.get('link', '')),
                    'source': item.get('fonte', item.get('source', 'unknown')),
                    'author': item.get('autor', item.get('author', 'Desconhecido')),
                    'timestamp': item.get('timestamp', datetime.now().isoformat()),
                    'category': item.get('categoria', item.get('category', 'geral')),
                    'metadata': {
                        'original_data': item,
                        'session_id': session_id,
                        'index': idx,
                        'relevancia': item.get('relevancia', 0.5),
                        'conteudo_tamanho': item.get('conteudo_tamanho', len(' '.join(content_parts))),
                        'engagement': item.get('engagement', {}),
                        'processado_em': datetime.now().isoformat()
                    }
                }
                
                items.append(formatted_item)
                logger.debug(f"✅ Item {idx+1} convertido: {formatted_item['title'][:50]}...")
            
            logger.info(f"✅ Conversão concluída: {len(items)} items válidos preparados para análise")
            
            return {
                'items': items,
                'total_items': len(items),
                'session_id': session_id,
                'prepared_at': datetime.now().isoformat(),
                'source_structure': 'auto_detected',
                'original_count': len(raw_items)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao preparar dados para análise: {e}")
            logger.error(f"📋 Dados que causaram erro: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}...")
            return {
                'items': [],
                'total_items': 0,
                'session_id': session_id,
                'error': str(e),
                'error_details': {
                    'exception_type': type(e).__name__,
                    'data_keys': list(data.keys()) if isinstance(data, dict) else 'not_dict'
                }
            }

    def _fallback_verification_result(self, session_id: str) -> Dict[str, Any]:
        """Resultado fallback quando o módulo não está disponível"""
        return {
            'success': True,
            'session_id': session_id,
            'total_items': 0,
            'statistics': {
                'approved': 0,
                'rejected': 0,
                'total_processed': 0,
                'average_confidence': 0.0
            },
            'all_results': [],
            'approved_items': [],
            'rejected_items': [],
            'metadata': {
                'fallback_mode': True,
                'message': 'External AI Verifier não disponível - modo fallback ativo',
                'timestamp': datetime.now().isoformat()
            },
            'fallback_used': True
        }

    def _fallback_batch_result(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resultado fallback para verificação em lote"""
        items_count = len(input_data.get('items', []))
        return {
            'success': True,
            'total_items': items_count,
            'statistics': {
                'approved': items_count,
                'rejected': 0,
                'total_processed': items_count,
                'average_confidence': 1.0
            },
            'results': input_data.get('items', []),
            'approved_items': input_data.get('items', []),
            'rejected_items': [],
            'metadata': {
                'fallback_mode': True,
                'message': 'External AI Verifier não disponível - todos os itens aprovados por fallback',
                'timestamp': datetime.now().isoformat()
            },
            'fallback_used': True
        }

    def _create_example_data_for_testing(self, session_id: str) -> Dict[str, Any]:
        """Cria dados de exemplo para teste quando não há dados de consolidação"""
        return {
            'data': {
                'dados_web': [
                    {
                        'titulo': 'Exemplo de análise de mercado - Tendências 2025',
                        'url': 'https://example.com/market-analysis-2025',
                        'fonte': 'Market Research Institute',
                        'conteudo': 'Análise detalhada das principais tendências de mercado para 2025, incluindo tecnologia, sustentabilidade e comportamento do consumidor.',
                        'relevancia': 0.8,
                        'conteudo_tamanho': 1500,
                        'engagement': {'views': 1000, 'shares': 50}
                    },
                    {
                        'titulo': 'Inovações tecnológicas que transformarão o setor',
                        'url': 'https://example.com/tech-innovations',
                        'fonte': 'Tech Today',
                        'conteudo': 'Artigo sobre as principais inovações tecnológicas que estão moldando o futuro dos negócios e da sociedade.',
                        'relevancia': 0.9,
                        'conteudo_tamanho': 2000,
                        'engagement': {'views': 1500, 'shares': 75}
                    },
                    {
                        'titulo': 'Estratégias de marketing digital para pequenas empresas',
                        'url': 'https://example.com/digital-marketing-strategies',
                        'fonte': 'Business Weekly',
                        'conteudo': 'Guia completo com estratégias práticas de marketing digital especificamente desenvolvidas para pequenas e médias empresas.',
                        'relevancia': 0.7,
                        'conteudo_tamanho': 1200,
                        'engagement': {'views': 800, 'shares': 40}
                    }
                ],
                'tipo': 'analise_exemplo_teste'
            },
            'metadata': {
                'session_id': session_id,
                'created_for_testing': True,
                'timestamp': datetime.now().isoformat()
            }
        }

    def verify_and_reprocess_failed_items(self, session_id: str, verification_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        ✅ NOVO MÉTODO: Verifica e reprocessa itens que falharam no LLM
        
        Implementa a correção identificada no documento de melhorias para garantir
        que todos os itens passem pela análise LLM
        
        Args:
            session_id: ID da sessão
            verification_results: Resultados da verificação inicial
            
        Returns:
            Resultados atualizados após reprocessamento
        """
        try:
            if not self.module_available:
                logger.warning("⚠️ External AI Verifier não disponível para reprocessamento")
                return verification_results
            
            # Verifica se há resultados para processar
            all_results = verification_results.get('all_results', [])
            if not all_results:
                logger.info("ℹ️ Nenhum resultado encontrado para reprocessamento")
                return verification_results
            
            # Identifica itens que não foram processados pelo LLM
            failed_items = []
            for item in all_results:
                llm_analysis = item.get('llm_reasoning_analysis', {})
                llm_recommendation = llm_analysis.get('llm_recommendation', '')
                
                if llm_recommendation == 'NÃO_EXECUTADO':
                    failed_items.append(item)
            
            if not failed_items:
                logger.info("✅ Todos os itens foram processados corretamente pelo LLM")
                return verification_results
            
            logger.info(f"🔄 Encontrados {len(failed_items)} itens não processados pelo LLM - iniciando reprocessamento")
            
            # Importa o agente de verificação
            from external_review_agent import ExternalReviewAgent
            
            # Cria instância do agente
            agent = ExternalReviewAgent()
            
            # Força o reprocessamento dos itens falhos
            reprocessed_items = agent.force_reprocess_failed_items(failed_items)
            
            # Atualiza os resultados originais com os itens reprocessados
            updated_results = []
            failed_item_ids = {item.get('item_id', item.get('id', '')) for item in failed_items}
            
            for item in all_results:
                item_id = item.get('item_id', item.get('id', ''))
                
                if item_id in failed_item_ids:
                    # Encontra o item reprocessado correspondente
                    reprocessed_item = next(
                        (r_item for r_item in reprocessed_items 
                         if r_item.get('item_id', r_item.get('id', '')) == item_id),
                        item  # Fallback para o item original se não encontrar
                    )
                    updated_results.append(reprocessed_item)
                else:
                    updated_results.append(item)
            
            # Recalcula estatísticas
            approved_items = [item for item in updated_results 
                            if item.get('ai_review', {}).get('status') == 'approved']
            rejected_items = [item for item in updated_results 
                            if item.get('ai_review', {}).get('status') == 'rejected']
            
            # Atualiza os resultados da verificação
            verification_results.update({
                'all_results': updated_results,
                'approved_items': approved_items,
                'rejected_items': rejected_items,
                'statistics': {
                    'total_processed': len(updated_results),
                    'approved': len(approved_items),
                    'rejected': len(rejected_items),
                    'approval_rate': len(approved_items) / len(updated_results) if updated_results else 0,
                    'reprocessed_items': len(failed_items)
                },
                'reprocessing_info': {
                    'items_reprocessed': len(failed_items),
                    'reprocessing_successful': True,
                    'timestamp': datetime.now().isoformat()
                }
            })
            
            logger.info(f"✅ Reprocessamento concluído: {len(failed_items)} itens reprocessados")
            logger.info(f"📊 Estatísticas atualizadas: {len(approved_items)} aprovados, {len(rejected_items)} rejeitados")
            
            return verification_results
            
        except Exception as e:
            logger.error(f"❌ Erro durante reprocessamento de itens falhos: {e}")
            
            # Adiciona informação de erro mas retorna os resultados originais
            verification_results['reprocessing_info'] = {
                'items_reprocessed': 0,
                'reprocessing_successful': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            return verification_results

    def get_status(self) -> Dict[str, Any]:
        """Retorna status da integração"""
        return {
            'module_available': self.module_available,
            'integration_active': True,
            'timestamp': datetime.now().isoformat()
        }

# Alias para compatibilidade
ExternalAIIntegration = ExternalAIVerifierIntegration

# Instância global
external_ai_integration = ExternalAIVerifierIntegration()