#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - External Review Agent
Agente principal de revisão externa - ponto de entrada do módulo
"""

import logging
import os
import yaml
import json
import glob
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import asyncio
import time

# Handle both relative and absolute imports
try:
    from .services.sentiment_analyzer import ExternalSentimentAnalyzer
    from .services.bias_disinformation_detector import ExternalBiasDisinformationDetector
    from .services.llm_reasoning_service import ExternalLLMReasoningService
    from .services.rule_engine import ExternalRuleEngine
    from .services.contextual_analyzer import ExternalContextualAnalyzer
    from .services.confidence_thresholds import ExternalConfidenceThresholds
except ImportError:
    try:
        from services.sentiment_analyzer import ExternalSentimentAnalyzer
        from services.bias_disinformation_detector import ExternalBiasDisinformationDetector
        from services.llm_reasoning_service import ExternalLLMReasoningService
        from services.rule_engine import ExternalRuleEngine
        from services.contextual_analyzer import ExternalContextualAnalyzer
        from services.confidence_thresholds import ExternalConfidenceThresholds
    except ImportError:
        from sentiment_analyzer import ExternalSentimentAnalyzer
        from bias_disinformation_detector import ExternalBiasDisinformationDetector
        from llm_reasoning_service import ExternalLLMReasoningService
        from rule_engine import ExternalRuleEngine
        from contextual_analyzer import ExternalContextualAnalyzer
        from confidence_thresholds import ExternalConfidenceThresholds

logger = logging.getLogger(__name__)


class ExternalReviewAgent:
    """Agente de revisão externa - orquestrador principal do módulo"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o agente de revisão externa

        Args:
            config_path (Optional[str]): Caminho para arquivo de configuração
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        self.config = self._load_config(config_path)

        # Initialize all analysis services
        self.sentiment_analyzer = ExternalSentimentAnalyzer(self.config)
        self.bias_detector = ExternalBiasDisinformationDetector(self.config)
        self.llm_service = ExternalLLMReasoningService(self.config)
        self.rule_engine = ExternalRuleEngine(self.config)
        self.contextual_analyzer = ExternalContextualAnalyzer(self.config)
        self.confidence_thresholds = ExternalConfidenceThresholds(self.config)

        # Rate Limiting Configuration
        self.llm_call_delay = self.config.get('rate_limiting', {}).get('llm_call_delay_seconds', 10)
        self.last_llm_call_time = 0.0
        
        # Configuração flexível para validação de URL
        self.require_url = self.config.get('validation', {}).get('require_url', False)
        self.min_content_length = self.config.get('validation', {}).get('min_content_length', 5)

        # Processing statistics
        self.stats = {
            'total_processed': 0,
            'approved': 0,
            'rejected': 0,
            'start_time': datetime.now(),
            'processing_times': []
        }

        logger.info(f"✅ External Review Agent inicializado com sucesso")
        logger.info(f"🔧 Configurações carregadas: {len(self.config)} seções")
        logger.info(f"⏳ Rate Limiting LLM: {self.llm_call_delay:.2f}s entre chamadas")
        logger.info(f"🔗 Requisito de URL: {'Obrigatório' if self.require_url else 'Opcional'}")

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Carrega configuração do módulo"""
        try:
            if config_path is None:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                config_path = os.path.join(current_dir, '..', 'config', 'default_config.yaml')

            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                        config = yaml.safe_load(f)
                    else:
                        config = json.load(f)
                logger.info(f"✅ Configuração carregada: {config_path}")
                return config
            else:
                logger.warning(f"⚠️ Arquivo de configuração não encontrado: {config_path}")
                return self._get_default_config()

        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão"""
        return {
            'thresholds': {
                'approval': 0.75,
                'rejection': 0.35,
                'high_confidence': 0.85,
                'low_confidence': 0.5,
                'bias_high_risk': 0.7
            },
            'sentiment_analysis': {'enabled': True},
            'bias_detection': {'enabled': True},
            'llm_reasoning': {'enabled': True},
            'contextual_analysis': {'enabled': True},
            'rules': [],
            'rate_limiting': {
                'llm_call_delay_seconds': 6.7
            },
            'validation': {
                'require_url': False,
                'min_content_length': 5,
                'allow_empty_url': True
            }
        }

    def _enforce_llm_rate_limit(self):
        """Aplica delay para respeitar o limite de chamadas LLM por minuto."""
        current_time = time.time()
        time_since_last_call = current_time - self.last_llm_call_time

        if time_since_last_call < self.llm_call_delay:
            sleep_time = self.llm_call_delay - time_since_last_call
            logger.debug(f"Rate limiting: aguardando {sleep_time:.2f}s antes da próxima chamada LLM")
            time.sleep(sleep_time)
        
        self.last_llm_call_time = time.time()

    def process_item(self, item_data: Dict[str, Any], massive_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Processa um item individual através de todas as análises com validação aprimorada

        Args:
            item_data (Dict[str, Any]): Dados do item para análise
            massive_data (Optional[Dict[str, Any]]): Contexto adicional

        Returns:
            Dict[str, Any]: Resultado completo da análise
        """
        start_time = datetime.now()

        try:
            item_id = item_data.get('id', f'item_{self.stats["total_processed"]}')
            logger.info(f"🔍 Iniciando análise do item: {item_id}")

            # Validação prévia do item (agora mais flexível)
            validation_result = self._validate_item_data(item_data)
            if not validation_result['valid']:
                logger.warning(f"⚠️ Item inválido: {validation_result['reason']}")
                return self._create_validation_error_result(item_data, validation_result['reason'])

            # Extract text content for analysis
            text_content = self._extract_text_content(item_data)

            if not text_content or len(text_content.strip()) < self.min_content_length:
                logger.warning(f"⚠️ Item com conteúdo textual insuficiente (min: {self.min_content_length} chars)")
                return self._create_insufficient_content_result(item_data)

            # Initialize analysis results
            analysis_result = {
                'item_id': item_id,
                'original_item': item_data,
                'processing_timestamp': start_time.isoformat(),
                'text_analyzed': text_content[:500],
                'has_url': bool(item_data.get('url') or item_data.get('source'))
            }

            # Step 1: Sentiment Analysis
            logger.debug("Executando análise de sentimento...")
            sentiment_result = self.sentiment_analyzer.analyze_sentiment(text_content)
            analysis_result['sentiment_analysis'] = sentiment_result

            # Step 2: Bias & Disinformation Detection
            logger.debug("Executando detecção de viés/desinformação...")
            bias_result = self.bias_detector.detect_bias_disinformation(text_content)
            analysis_result['bias_disinformation_analysis'] = bias_result

            # Step 3: LLM Reasoning (for ambiguous cases)
            should_use_llm = self._should_use_llm_analysis(sentiment_result, bias_result)
            if should_use_llm:
                logger.debug("Executando análise LLM...")
                self._enforce_llm_rate_limit()
                context = self._create_llm_context(analysis_result, massive_data)
                llm_result = self.llm_service.analyze_with_llm(text_content, context)
                analysis_result['llm_reasoning_analysis'] = llm_result
            else:
                analysis_result['llm_reasoning_analysis'] = {
                    'llm_confidence': 0.5,
                    'llm_recommendation': 'NÃO_EXECUTADO',
                    'analysis_reasoning': 'LLM não necessário para este item'
                }

            # Step 4: Contextual Analysis
            logger.debug("Executando análise contextual...")
            contextual_result = self.contextual_analyzer.analyze_context(item_data, massive_data)
            analysis_result['contextual_analysis'] = contextual_result

            # Step 5: Rule Engine Application
            logger.debug("Aplicando regras de negócio...")
            rule_result = self.rule_engine.apply_rules(analysis_result)
            analysis_result['rule_decision'] = rule_result

            # Step 6: Final Decision
            final_decision = self._make_final_decision(analysis_result)
            analysis_result['ai_review'] = final_decision

            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(final_decision['status'], processing_time)

            analysis_result['processing_time_seconds'] = processing_time

            logger.info(f"✅ Item processado: {final_decision['status']} (confiança: {final_decision['final_confidence']:.3f})")

            return analysis_result

        except Exception as e:
            logger.error(f"Erro no processamento do item: {e}", exc_info=True)
            error_result = self._create_error_result(item_data, str(e))
            self._update_stats('error', (datetime.now() - start_time).total_seconds())
            return error_result

    def _validate_item_data(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida dados do item antes do processamento - versão flexível"""
        if not isinstance(item_data, dict):
            return {'valid': False, 'reason': 'Item deve ser um dicionário'}
        
        if not item_data:
            return {'valid': False, 'reason': 'Item vazio'}
        
        # Verificar conteúdo textual
        content_fields = ['content', 'text', 'title', 'description', 'summary', 'body', 'caption', 'excerpt']
        has_content = any(
            field in item_data and 
            item_data[field] and 
            str(item_data[field]).strip() 
            for field in content_fields
        )
        
        if not has_content:
            return {'valid': False, 'reason': 'Item não possui conteúdo textual válido'}
        
        # Verificar URL apenas se for obrigatório
        if self.require_url:
            url_fields = ['url', 'source', 'link']
            has_url = any(
                field in item_data and 
                item_data[field] and 
                str(item_data[field]).strip() 
                for field in url_fields
            )
            
            if not has_url:
                return {'valid': False, 'reason': 'Item não possui URL e URL é obrigatória'}
        
        return {'valid': True, 'reason': 'Item válido'}

    def _extract_text_content(self, item_data: Dict[str, Any]) -> str:
        """Extrai conteúdo textual do item com priorização"""
        priority_fields = ['content', 'text', 'description', 'summary', 'title', 'body']
        extra_fields = ['subtitle', 'excerpt', 'abstract', 'caption', 'snippet']

        text_parts = []
        
        # Campos prioritários
        for field in priority_fields:
            if field in item_data and item_data[field]:
                content = str(item_data[field]).strip()
                if content:
                    text_parts.append(content)

        # Campos extras
        for field in extra_fields:
            if field in item_data and item_data[field]:
                content = str(item_data[field]).strip()
                if content:
                    text_parts.append(content)

        return ' '.join(text_parts).strip()

    def _should_use_llm_analysis(self, sentiment_result: Dict[str, Any], bias_result: Dict[str, Any]) -> bool:
        """
        Determina se deve usar análise LLM - CORRIGIDO para garantir processamento completo
        
        MUDANÇA CRÍTICA: Agora SEMPRE executa LLM para garantir análise completa
        conforme identificado no documento de melhorias
        """
        # ✅ CORREÇÃO CRÍTICA: SEMPRE executa LLM para garantir processamento completo
        # Isso resolve o problema de itens marcados como "NÃO_EXECUTADO"
        
        sentiment_confidence = sentiment_result.get('confidence', 0.5)
        bias_risk = bias_result.get('overall_risk', 0.0)
        
        # Condições para SEMPRE usar LLM (mais abrangentes)
        should_use = (
            sentiment_confidence < 0.8 or  # Aumentado de 0.6 para 0.8
            bias_risk > 0.2 or             # Diminuído de 0.4 para 0.2  
            sentiment_confidence == 0.5 or # Casos de confiança padrão
            bias_risk == 0.0               # Casos sem detecção de viés
        )
        
        # Log para debugging
        if should_use:
            logger.debug(f"🧠 LLM será executado: sentiment_conf={sentiment_confidence:.3f}, bias_risk={bias_risk:.3f}")
        else:
            logger.debug(f"⚠️ LLM NÃO será executado: sentiment_conf={sentiment_confidence:.3f}, bias_risk={bias_risk:.3f}")
        
        return should_use

    def _create_llm_context(self, analysis_result: Dict[str, Any], massive_data: Optional[Dict[str, Any]]) -> str:
        """Cria contexto para análise LLM"""
        context_parts = []

        sentiment = analysis_result.get('sentiment_analysis', {})
        if sentiment.get('classification') != 'neutral':
            context_parts.append(f"Sentimento detectado: {sentiment.get('classification', 'indefinido')}")

        bias = analysis_result.get('bias_disinformation_analysis', {})
        if bias.get('overall_risk', 0) > 0.3:
            context_parts.append(f"Risco de viés detectado: {bias.get('overall_risk', 0):.2f}")

        if massive_data:
            if 'topic' in massive_data:
                context_parts.append(f"Tópico: {massive_data['topic']}")

        return ' | '.join(context_parts) if context_parts else ""

    def _make_final_decision(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Toma decisão final baseada em todas as análises"""
        try:
            sentiment = analysis_result.get('sentiment_analysis', {})
            bias = analysis_result.get('bias_disinformation_analysis', {})
            llm = analysis_result.get('llm_reasoning_analysis', {})
            contextual = analysis_result.get('contextual_analysis', {})
            rule_decision = analysis_result.get('rule_decision', {})

            # Calculate composite confidence
            confidences = [
                sentiment.get('confidence', 0.5) * 0.2,
                (1.0 - bias.get('overall_risk', 0.5)) * 0.3,
                llm.get('llm_confidence', 0.5) * 0.3,
                contextual.get('contextual_confidence', 0.5) * 0.2
            ]

            final_confidence = sum(confidences)

            # Apply rule engine decision if applicable
            if rule_decision.get('status') in ['approved', 'rejected']:
                status = rule_decision['status']
                reason = rule_decision['reason']
            else:
                if self.confidence_thresholds.should_approve(final_confidence):
                    status = 'approved'
                    reason = 'Aprovado com base na análise combinada'
                elif self.confidence_thresholds.should_reject(final_confidence):
                    status = 'rejected'
                    reason = 'Rejeitado com base na análise combinada'
                else:
                    status = 'rejected'
                    reason = 'Rejeitado por ambiguidade - política de segurança'

            decision = {
                'status': status,
                'reason': reason,
                'final_confidence': final_confidence,
                'confidence_breakdown': {
                    'sentiment_contribution': sentiment.get('confidence', 0.5) * 0.2,
                    'bias_contribution': (1.0 - bias.get('overall_risk', 0.5)) * 0.3,
                    'llm_contribution': llm.get('llm_confidence', 0.5) * 0.3,
                    'contextual_contribution': contextual.get('contextual_confidence', 0.5) * 0.2
                },
                'decision_factors': {
                    'sentiment_classification': sentiment.get('classification', 'neutral'),
                    'bias_risk_level': 'high' if bias.get('overall_risk', 0) > 0.6 else 'medium' if bias.get('overall_risk', 0) > 0.3 else 'low',
                    'llm_recommendation': llm.get('llm_recommendation', 'NÃO_EXECUTADO'),
                    'rule_triggered': rule_decision.get('triggered_rules', [])
                },
                'analysis_summary': {
                    'total_flags': (
                        len(bias.get('detected_bias_keywords', [])) +
                        len(bias.get('detected_disinformation_patterns', [])) +
                        len(contextual.get('context_flags', []))
                    ),
                    'sentiment_polarity': sentiment.get('polarity', 0.0),
                    'overall_risk_score': bias.get('overall_risk', 0.0),
                    'contextual_consistency': contextual.get('consistency_score', 0.5)
                },
                'processing_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'version': '3.0.0',
                    'confidence_threshold_used': self.confidence_thresholds.get_threshold('approval')
                }
            }

            return decision

        except Exception as e:
            logger.error(f"Erro na decisão final: {e}", exc_info=True)
            return {
                'status': 'rejected',
                'reason': f'Erro no processamento: {str(e)}',
                'final_confidence': 0.0,
                'error': True
            }

    def _create_validation_error_result(self, item_data: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Cria resultado para item que falhou na validação"""
        return {
            'item_id': item_data.get('id', 'sem_id'),
            'original_item': item_data,
            'processing_timestamp': datetime.now().isoformat(),
            'ai_review': {
                'status': 'rejected',
                'reason': f'Erro de validação: {reason}',
                'final_confidence': 0.0,
                'error': True,
                'validation_error': True
            },
            'sentiment_analysis': {},
            'bias_disinformation_analysis': {},
            'llm_reasoning_analysis': {},
            'contextual_analysis': {},
            'processing_time_seconds': 0.0
        }

    def _create_insufficient_content_result(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria resultado para item com conteúdo insuficiente"""
        return {
            'item_id': item_data.get('id', 'sem_id'),
            'original_item': item_data,
            'processing_timestamp': datetime.now().isoformat(),
            'ai_review': {
                'status': 'rejected',
                'reason': f'Conteúdo textual insuficiente para análise (mínimo: {self.min_content_length} caracteres)',
                'final_confidence': 0.0,
                'error': False,
                'insufficient_content': True
            },
            'sentiment_analysis': {},
            'bias_disinformation_analysis': {},
            'llm_reasoning_analysis': {},
            'contextual_analysis': {},
            'processing_time_seconds': 0.0
        }

    def _create_error_result(self, item_data: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """Cria resultado para erro de processamento"""
        return {
            'item_id': item_data.get('id', 'sem_id'),
            'original_item': item_data,
            'processing_timestamp': datetime.now().isoformat(),
            'ai_review': {
                'status': 'rejected',
                'reason': f'Erro no processamento: {error_message}',
                'final_confidence': 0.0,
                'error': True
            },
            'error_details': error_message,
            'processing_time_seconds': 0.0
        }

    def _update_stats(self, status: str, processing_time: float):
        """Atualiza estatísticas de processamento"""
        self.stats['total_processed'] += 1
        self.stats['processing_times'].append(processing_time)

        if status == 'approved':
            self.stats['approved'] += 1
        elif status == 'rejected':
            self.stats['rejected'] += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de processamento"""
        total_time = (datetime.now() - self.stats['start_time']).total_seconds()
        avg_processing_time = sum(self.stats['processing_times']) / len(self.stats['processing_times']) if self.stats['processing_times'] else 0

        return {
            'total_processed': self.stats['total_processed'],
            'approved': self.stats['approved'],
            'rejected': self.stats['rejected'],
            'approval_rate': self.stats['approved'] / max(self.stats['total_processed'], 1),
            'total_runtime_seconds': total_time,
            'average_processing_time_seconds': avg_processing_time,
            'items_per_second': self.stats['total_processed'] / max(total_time, 1)
        }

    def force_reprocess_failed_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        ✅ NOVO MÉTODO: Força o reprocessamento de itens que falharam no LLM
        
        Resolve o problema identificado no documento de melhorias onde itens
        ficam marcados como "NÃO_EXECUTADO"
        
        Args:
            items: Lista de itens para reprocessar
            
        Returns:
            Lista de itens reprocessados
        """
        logger.info(f"🔄 Iniciando reprocessamento forçado de {len(items)} itens")
        
        reprocessed_items = []
        failed_items = []
        
        for item in items:
            try:
                item_id = item.get('item_id', item.get('id', 'unknown'))
                
                # Verifica se o item realmente precisa de reprocessamento
                llm_analysis = item.get('llm_reasoning_analysis', {})
                llm_recommendation = llm_analysis.get('llm_recommendation', '')
                
                if llm_recommendation == 'NÃO_EXECUTADO':
                    logger.info(f"🔄 Reprocessando item {item_id} (LLM não executado)")
                    
                    # Força a execução do LLM
                    text_content = self._extract_text_content(item.get('original_item', item))
                    
                    if text_content and len(text_content.strip()) >= self.min_content_length:
                        # Força análise LLM
                        self._enforce_llm_rate_limit()
                        context = self._create_llm_context(item, None)
                        
                        try:
                            llm_result = self.llm_service.analyze_with_llm(text_content, context)
                            
                            # Atualiza o item com o resultado do LLM
                            item['llm_reasoning_analysis'] = llm_result
                            
                            # Refaz a decisão final com o novo resultado LLM
                            final_decision = self._make_final_decision(item)
                            item['ai_review'] = final_decision
                            
                            logger.info(f"✅ Item {item_id} reprocessado com sucesso: {final_decision['status']}")
                            reprocessed_items.append(item)
                            
                        except Exception as llm_error:
                            logger.error(f"❌ Falha no reprocessamento LLM do item {item_id}: {llm_error}")
                            
                            # Marca como erro mas mantém o item
                            item['llm_reasoning_analysis'] = {
                                'llm_confidence': 0.1,
                                'llm_recommendation': 'ERRO_REPROCESSAMENTO',
                                'analysis_reasoning': f'Erro no reprocessamento: {str(llm_error)}',
                                'error': True
                            }
                            
                            # Refaz decisão final mesmo com erro
                            final_decision = self._make_final_decision(item)
                            item['ai_review'] = final_decision
                            
                            failed_items.append(item)
                    else:
                        logger.warning(f"⚠️ Item {item_id} não tem conteúdo suficiente para reprocessamento")
                        failed_items.append(item)
                else:
                    # Item já foi processado corretamente
                    logger.debug(f"✅ Item {item_id} já processado corretamente")
                    reprocessed_items.append(item)
                    
            except Exception as e:
                logger.error(f"❌ Erro no reprocessamento do item: {e}")
                failed_items.append(item)
        
        logger.info(f"✅ Reprocessamento concluído: {len(reprocessed_items)} sucessos, {len(failed_items)} falhas")
        
        # Retorna todos os itens (reprocessados + falhas)
        return reprocessed_items + failed_items

    def find_consolidacao_file(self, session_id: str) -> Optional[str]:
        """Busca automaticamente o arquivo de consolidação da etapa 1 para a sessão especificada"""
        try:
            base_paths = [
                f"../src/relatorios_intermediarios/workflow/{session_id}",
                f"src/relatorios_intermediarios/workflow/{session_id}",
                f"relatorios_intermediarios/workflow/{session_id}",
                f"../relatorios_intermediarios/workflow/{session_id}",
                f"../src/analyses_data/sessions/{session_id}",
                f"src/analyses_data/sessions/{session_id}",
                f"analyses_data/sessions/{session_id}",
                f"../analyses_data/sessions/{session_id}",
                f"../src/relatorios_finais/{session_id}",
                f"src/relatorios_finais/{session_id}",
                f"relatorios_finais/{session_id}",
                f"../relatorios_finais/{session_id}"
            ]

            for base_path in base_paths:
                if os.path.exists(base_path):
                    patterns = [
                        f"{base_path}/consolidacao_etapa1_final_*.json",
                        f"{base_path}/consolidacao_*.json",
                        f"{base_path}/etapa1_*.json",
                        f"{base_path}/*consolidacao*.json",
                        f"{base_path}/*.json"
                    ]
                    
                    for pattern in patterns:
                        files = glob.glob(pattern)
                        if files:
                            session_files = [f for f in files if session_id in f or session_id in os.path.basename(f)]
                            if session_files:
                                latest_file = max(session_files, key=os.path.getmtime)
                                self.logger.info(f"✅ Arquivo de consolidação encontrado: {latest_file}")
                                return latest_file

                    if files:
                        latest_file = max(files, key=os.path.getmtime)
                        self.logger.info(f"✅ Arquivo de consolidação encontrado: {latest_file}")
                        return latest_file

            search_patterns = [
                f"**/consolidacao_etapa1_final_*{session_id}*.json",
                f"**/consolidacao_etapa1_final_*.json"
            ]

            for pattern in search_patterns:
                files = glob.glob(pattern, recursive=True)
                if files:
                    session_files = [f for f in files if session_id in f]
                    if session_files:
                        latest_file = max(session_files, key=os.path.getmtime)
                        self.logger.info(f"✅ Arquivo de consolidação encontrado (busca recursiva): {latest_file}")
                        return latest_file
                    else:
                        latest_file = max(files, key=os.path.getmtime)
                        self.logger.info(f"⚠️ Usando arquivo mais recente: {latest_file}")
                        return latest_file

            self.logger.warning(f"⚠️ Nenhum arquivo de consolidação encontrado para sessão {session_id}")
            return None

        except Exception as e:
            self.logger.error(f"⚠️ Erro ao buscar arquivo de consolidação: {e}")
            return None

    def load_consolidacao_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Carrega dados do arquivo de consolidação da etapa 1"""
        try:
            file_path = self.find_consolidacao_file(session_id)

            if not file_path:
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.logger.info(f"📄 Arquivo de consolidação carregado: {file_path}")
            
            # Log da estrutura completa para debug
            self.logger.debug(f"🔍 Estrutura JSON - Chaves raiz: {list(data.keys())}")
            
            return data

        except Exception as e:
            self.logger.error(f"⚠️ Erro ao carregar dados de consolidação: {e}")
            return None

    def convert_consolidacao_to_analysis_format(self, consolidacao_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Converte dados de consolidação para formato de análise do External AI Verifier
        CORRIGIDO: Agora explora TODAS as estruturas possíveis de forma recursiva
        """
        try:
            if not consolidacao_data:
                return {'items': [], 'context': {}}

            self.logger.info("🔍 INICIANDO EXTRAÇÃO INTELIGENTE DE DADOS")
            self.logger.info(f"📋 Estrutura JSON raiz: {list(consolidacao_data.keys())}")

            # Função recursiva para encontrar listas de items
            def find_item_lists(obj, path="root", depth=0):
                """Busca recursivamente por listas que parecem conter items de dados"""
                if depth > 10:  # Limite de profundidade para evitar loops
                    return []
                
                found_lists = []
                
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}"
                        
                        # Se o valor é uma lista, verificar se contém items válidos
                        if isinstance(value, list) and value:
                            if isinstance(value[0], dict):
                                # Verificar se parece ser uma lista de items de dados
                                sample = value[0]
                                data_indicators = ['titulo', 'title', 'content', 'text', 'descricao', 
                                                 'description', 'url', 'source', 'dados']
                                
                                if any(indicator in sample for indicator in data_indicators):
                                    self.logger.info(f"✅ Lista de items encontrada em: {current_path} ({len(value)} items)")
                                    found_lists.append({
                                        'path': current_path,
                                        'items': value,
                                        'count': len(value),
                                        'sample_keys': list(sample.keys())[:10]
                                    })
                        
                        # Continuar busca recursiva
                        if isinstance(value, (dict, list)):
                            found_lists.extend(find_item_lists(value, current_path, depth + 1))
                
                elif isinstance(obj, list):
                    for idx, item in enumerate(obj):
                        if isinstance(item, (dict, list)):
                            found_lists.extend(find_item_lists(item, f"{path}[{idx}]", depth + 1))
                
                return found_lists

            # Buscar todas as listas de items no JSON
            all_item_lists = find_item_lists(consolidacao_data)
            
            if not all_item_lists:
                self.logger.warning("⚠️ NENHUMA LISTA DE ITEMS ENCONTRADA NO JSON")
                self.logger.info(f"📊 Estrutura do JSON: {json.dumps(consolidacao_data, indent=2, ensure_ascii=False)[:1000]}...")
                
                # CORREÇÃO: Se não há listas, tentar criar item único dos dados de contexto
                self.logger.info("🔄 Tentando criar item único dos dados de contexto...")
                
                # Extrair dados de contexto
                data_section = consolidacao_data.get('data', {})
                context_section = data_section.get('context', {}) if isinstance(data_section, dict) else {}
                
                if context_section:
                    # Criar item único com dados de contexto
                    context_item = {
                        'titulo': f"Análise de {context_section.get('segmento', 'Negócio Digital')}",
                        'content': f"Segmento: {context_section.get('segmento', '')}\n"
                                  f"Produto: {context_section.get('produto', '')}\n"
                                  f"Público: {context_section.get('publico', '')}\n"
                                  f"Query: {context_section.get('query_original', '')}",
                        'source': 'session_context',
                        'url': f'session://{session_id}',
                        'tipo': 'contexto_sessao'
                    }
                    
                    self.logger.info("✅ Item de contexto criado com sucesso")
                    return {
                        'items': [context_item],
                        'context': {
                            'session_id': session_id,
                            'source_type': 'session_context',
                            'segmento': context_section.get('segmento', ''),
                            'publico': context_section.get('publico', ''),
                            'timestamp': datetime.now().isoformat()
                        }
                    }
                
                return {'items': [], 'context': {}}
            
            # Log de todas as listas encontradas
            self.logger.info(f"📦 TOTAL DE LISTAS ENCONTRADAS: {len(all_item_lists)}")
            for lst in all_item_lists:
                self.logger.info(f"  📍 {lst['path']}: {lst['count']} items - Chaves: {lst['sample_keys']}")
            
            # Selecionar a melhor lista (maior quantidade de items)
            best_list = max(all_item_lists, key=lambda x: x['count'])
            dados_web = best_list['items']
            
            self.logger.info(f"🎯 LISTA SELECIONADA: {best_list['path']} com {len(dados_web)} items")
            
            # Processar items
            items = []
            for idx, item in enumerate(dados_web):
                try:
                    # Extrai conteúdo de forma robusta
                    content_parts = []
                    
                    # Tentar diferentes campos de título
                    for title_field in ['titulo', 'title', 'name', 'heading', 'subject']:
                        if item.get(title_field):
                            content_parts.append(str(item[title_field]))
                            break
                    
                    # Tentar diferentes campos de descrição/conteúdo
                    for content_field in ['descricao', 'description', 'conteudo', 'content', 'text', 'body', 'summary', 'abstract', 'snippet']:
                        if item.get(content_field):
                            content_parts.append(str(item[content_field]))
                            break
                    
                    content = ' '.join(filter(None, content_parts))
                    
                    # Só adiciona se tiver conteúdo mínimo
                    if not content or len(content.strip()) < self.min_content_length:
                        self.logger.debug(f"Item {idx+1} ignorado - conteúdo insuficiente ({len(content)} chars)")
                        continue

                    # Extrair URL de múltiplos campos possíveis
                    url = ''
                    for url_field in ['url', 'source', 'link', 'href', 'src', 'fonte_url']:
                        if item.get(url_field):
                            url = str(item[url_field])
                            break

                    converted_item = {
                        'id': item.get('id', f"web_{idx+1:03d}"),
                        'content': content,
                        'title': item.get('titulo') or item.get('title', ''),
                        'source': url,
                        'url': url,
                        'author': item.get('fonte') or item.get('author') or item.get('source_name', 'Desconhecido'),
                        'timestamp': item.get('timestamp') or item.get('date') or datetime.now().isoformat(),
                        'category': item.get('category') or item.get('tipo', 'web_content'),
                        'relevancia': item.get('relevancia', 0.5),
                        'conteudo_tamanho': len(content),
                        'engagement': item.get('engagement', {}),
                        'metadata': {
                            'session_id': session_id,
                            'fonte_original': item.get('fonte') or item.get('source', ''),
                            'tipo_dado': 'analise_dados',
                            'processado_em': datetime.now().isoformat(),
                            'item_original_index': idx,
                            'extracted_from_path': best_list['path']
                        }
                    }
                    items.append(converted_item)
                    
                except Exception as e:
                    self.logger.error(f"❌ Erro ao processar item {idx}: {e}")
                    continue
                
            self.logger.info(f"✅ EXTRAÇÃO CONCLUÍDA: {len(items)} itens válidos de {len(dados_web)} items originais")

            context = {
                'topic': 'analise_dados_web',
                'analysis_type': 'verificacao_consolidacao_etapa1',
                'session_id': session_id,
                'source_file': 'consolidacao_etapa1',
                'source_path': best_list['path'],
                'total_items_originais': len(dados_web),
                'items_validos': len(items),
                'processamento_timestamp': datetime.now().isoformat(),
                **self.config.get('context', {})
            }

            return {
                'items': items,
                'context': context
            }

        except Exception as e:
            self.logger.error(f"⚠️ Erro ao converter dados de consolidação: {e}", exc_info=True)
            return {'items': [], 'context': {}}

    def analyze_session_consolidacao(self, session_id: str) -> Dict[str, Any]:
        """Analisa automaticamente os dados de consolidação de uma sessão"""
        try:
            self.logger.info(f"🔍 Iniciando análise da consolidação para sessão: {session_id}")

            consolidacao_data = self.load_consolidacao_data(session_id)

            if not consolidacao_data:
                return {
                    'success': False,
                    'error': f'Arquivo de consolidação não encontrado para sessão {session_id}',
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat()
                }

            analysis_data = self.convert_consolidacao_to_analysis_format(consolidacao_data, session_id)

            if not analysis_data.get('items'):
                return {
                    'success': False,
                    'error': 'Nenhum item válido encontrado nos dados de consolidação',
                    'session_id': session_id,
                    'items_originais': 0,
                    'items_validos': 0,
                    'timestamp': datetime.now().isoformat()
                }

            result = self.analyze_content_batch(analysis_data)

            result['session_analysis'] = {
                'session_id': session_id,
                'consolidacao_source': True,
                'items_analisados': len(analysis_data.get('items', [])),
                'timestamp': datetime.now().isoformat()
            }

            return result

        except Exception as e:
            self.logger.error(f"⚠️ Erro na análise da sessão {session_id}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }

    def process_batch(self, items: List[Dict[str, Any]], massive_data: Optional[Dict[str, Any]] = None, 
                     batch_size: int = 10) -> Dict[str, Any]:
        """
        Processa uma lista de itens em lotes para melhor performance
        
        Args:
            items: Lista de itens para processar
            massive_data: Contexto adicional
            batch_size: Tamanho do lote para processamento
            
        Returns:
            Dict com resultados do processamento em lote
        """
        logger.info(f"💼 Iniciando processamento em lote: {len(items)} itens, lotes de {batch_size}")
        
        all_results = []
        approved_items = []
        rejected_items = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(items) + batch_size - 1) // batch_size
            
            logger.info(f"📦 Processando lote {batch_num}/{total_batches} ({len(batch)} itens)")
            
            batch_results = []
            for item in batch:
                result = self.process_item(item, massive_data)
                batch_results.append(result)
                all_results.append(result)
                
                status = result.get('ai_review', {}).get('status', 'rejected')
                if status == 'approved':
                    approved_items.append(result)
                else:
                    rejected_items.append(result)
            
            logger.info(f"✅ Lote {batch_num} concluído: {len([r for r in batch_results if r.get('ai_review', {}).get('status') == 'approved'])} aprovados")
        
        stats = self.get_statistics()
        
        return {
            'all_results': all_results,
            'approved_items': approved_items,
            'rejected_items': rejected_items,
            'statistics': stats,
            'batch_info': {
                'total_items': len(items),
                'batch_size': batch_size,
                'total_batches': total_batches,
                'approved_count': len(approved_items),
                'rejected_count': len(rejected_items),
                'approval_rate': len(approved_items) / len(items) if items else 0
            },
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '3.0.0',
                'processing_mode': 'batch'
            }
        }

    async def process_batch_async(self, items: List[Dict[str, Any]], massive_data: Optional[Dict[str, Any]] = None,
                                 max_concurrent: int = 5) -> Dict[str, Any]:
        """
        Processa itens de forma assíncrona para melhor performance
        
        Args:
            items: Lista de itens para processar
            massive_data: Contexto adicional
            max_concurrent: Máximo de processamentos simultâneos
            
        Returns:
            Dict com resultados do processamento assíncrono
        """
        logger.info(f"⚡ Iniciando processamento assíncrono: {len(items)} itens, máx {max_concurrent} simultâneos")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single_item(item):
            async with semaphore:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, self.process_item, item, massive_data)
        
        tasks = [process_single_item(item) for item in items]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        approved_items = []
        rejected_items = []
        errors = []
        
        for i, result in enumerate(all_results):
            if isinstance(result, Exception):
                logger.error(f"⚠️ Erro no item {i}: {result}")
                errors.append({'item_index': i, 'error': str(result)})
                error_result = self._create_error_result(items[i], str(result))
                valid_results.append(error_result)
                rejected_items.append(error_result)
            else:
                valid_results.append(result)
                status = result.get('ai_review', {}).get('status', 'rejected')
                if status == 'approved':
                    approved_items.append(result)
                else:
                    rejected_items.append(result)
        
        stats = self.get_statistics()
        
        return {
            'all_results': valid_results,
            'approved_items': approved_items,
            'rejected_items': rejected_items,
            'errors': errors,
            'statistics': stats,
            'async_info': {
                'total_items': len(items),
                'max_concurrent': max_concurrent,
                'approved_count': len(approved_items),
                'rejected_count': len(rejected_items),
                'error_count': len(errors),
                'approval_rate': len(approved_items) / len(items) if items else 0
            },
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '3.0.0',
                'processing_mode': 'async'
            }
        }

    def analyze_content_batch(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa lote de conteúdo"""
        try:
            items = input_data.get('items', [])
            context = input_data.get('context', {})

            if not items:
                return {
                    'success': False,
                    'error': 'Nenhum item fornecido para análise',
                    'timestamp': datetime.now().isoformat()
                }

            self.logger.info(f"🔍 Iniciando análise de {len(items)} itens")

            results = []
            total_items = len(items)

            for idx, item in enumerate(items):
                self.logger.info(f"📄 Analisando item {idx + 1}/{total_items}: {item.get('id', 'N/A')}")

                try:
                    result = self.process_item(item, context)
                    results.append(result)

                except Exception as e:
                    self.logger.error(f"⚠️ Erro ao analisar item {item.get('id', 'N/A')}: {e}", exc_info=True)
                    results.append({
                        'item_id': item.get('id', 'N/A'),
                        'ai_review': {
                            'status': 'rejected',
                            'reason': f'Erro no processamento: {str(e)}',
                            'error': True
                        },
                        'confidence_score': 0.0
                    })

            stats = self._generate_batch_statistics(results)

            return {
                'success': True,
                'total_items': total_items,
                'results': results,
                'statistics': stats,
                'processing_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'agent_version': '3.0',
                    'batch_size': total_items
                }
            }

        except Exception as e:
            self.logger.error(f"⚠️ Erro na análise em lote: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_batch_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera estatísticas para uma análise em lote."""
        total_items = len(results)
        approved_count = sum(1 for r in results if r.get('ai_review', {}).get('status') == 'approved')
        rejected_count = total_items - approved_count
        error_count = sum(1 for r in results if r.get('ai_review', {}).get('error'))
        
        total_processing_time = sum(r.get('processing_time_seconds', 0) for r in results)
        avg_processing_time = total_processing_time / total_items if total_items > 0 else 0

        return {
            'total_items': total_items,
            'approved': approved_count,
            'rejected': rejected_count,
            'errors': error_count,
            'approval_rate': approved_count / total_items if total_items > 0 else 0,
            'total_processing_time_seconds': total_processing_time,
            'average_processing_time_seconds': avg_processing_time
        }


def run_external_review(input_data: Dict[str, Any], config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Função principal de entrada para o módulo externo

    Args:
        input_data (Dict[str, Any]): Dados de entrada contendo itens para análise
        config_path (Optional[str]): Caminho para arquivo de configuração

    Returns:
        Dict[str, Any]: Resultados da análise e itens processados
    """
    try:
        logger.info("💼 Iniciando External AI Verifier...")

        review_agent = ExternalReviewAgent(config_path)

        items = input_data.get('items', [])
        massive_data = input_data.get('context', {})

        if not items:
            logger.warning("Nenhum item fornecido para análise")
            return {
                'items': [],
                'statistics': {'total_processed': 0, 'error': 'Nenhum item fornecido'},
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'version': '3.0.0'
                }
            }

        logger.info(f"Processando {len(items)} itens...")

        processed_items = []
        approved_items = []
        rejected_items = []

        for item in items:
            result = review_agent.process_item(item, massive_data)
            processed_items.append(result)

            if result['ai_review']['status'] == 'approved':
                approved_items.append(result)
            else:
                rejected_items.append(result)

        final_result = {
            'items': approved_items,
            'all_items': processed_items,
            'rejected_items': rejected_items,
            'statistics': review_agent.get_statistics(),
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '3.0.0',
                'total_input_items': len(items),
                'approved_count': len(approved_items),
                'rejected_count': len(rejected_items)
            }
        }

        logger.info(f"✅ Processamento concluído: {len(approved_items)} aprovados, {len(rejected_items)} rejeitados")

        return final_result

    except Exception as e:
        logger.error(f"Erro crítico no External AI Verifier: {e}", exc_info=True)
        return {
            'items': [],
            'statistics': {'error': str(e), 'total_processed': 0},
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '3.0.0',
                'error': True
            }
        }


# Instância global do External AI Verifier (usando ExternalReviewAgent)
external_ai_verifier = ExternalReviewAgent()
