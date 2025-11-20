#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Contexto Compartilhado
Garante coerência entre módulos através de contexto unificado
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import threading

logger = logging.getLogger(__name__)

@dataclass
class SessionContext:
    """Contexto de sessão compartilhado entre módulos"""
    session_id: str
    produto: str
    publico_alvo: str
    timestamp: str
    
    # Dados coletados
    search_results: Dict[str, Any]
    competitor_data: Dict[str, Any]
    market_insights: Dict[str, Any]
    viral_content: Dict[str, Any]
    
    # Configurações
    tone: str = "profissional"
    language: str = "pt-BR"
    target_audience_details: Dict[str, Any] = None
    
    # Metadados
    modules_executed: List[str] = None
    quality_scores: Dict[str, float] = None
    
    def __post_init__(self):
        if self.modules_executed is None:
            self.modules_executed = []
        if self.quality_scores is None:
            self.quality_scores = {}
        if self.target_audience_details is None:
            self.target_audience_details = {}

class SharedContextManager:
    """Gerenciador de contexto compartilhado entre módulos"""
    
    def __init__(self, data_dir: str = "analyses_data"):
        self.data_dir = data_dir
        self.contexts: Dict[str, SessionContext] = {}
        self.lock = threading.Lock()
        
        os.makedirs(data_dir, exist_ok=True)
        
        logger.info("🔗 Sistema de Contexto Compartilhado inicializado")
    
    def create_session_context(self, session_id: str, produto: str, publico_alvo: str) -> SessionContext:
        """Cria novo contexto de sessão"""
        
        with self.lock:
            context = SessionContext(
                session_id=session_id,
                produto=produto,
                publico_alvo=publico_alvo,
                timestamp=datetime.now().isoformat(),
                search_results={},
                competitor_data={},
                market_insights={},
                viral_content={}
            )
            
            self.contexts[session_id] = context
            self._save_context(context)
            
            logger.info(f"✅ Contexto criado para sessão: {session_id}")
            return context
    
    def get_context(self, session_id: str) -> Optional[SessionContext]:
        """Recupera contexto de sessão"""
        
        with self.lock:
            if session_id in self.contexts:
                return self.contexts[session_id]
            
            # Tentar carregar do disco
            context = self._load_context(session_id)
            if context:
                self.contexts[session_id] = context
                return context
            
            return None
    
    def update_context(self, session_id: str, module_name: str, data: Dict[str, Any], quality_score: float = 0.0):
        """Atualiza contexto com dados de um módulo"""
        
        with self.lock:
            context = self.get_context(session_id)
            if not context:
                logger.error(f"❌ Contexto não encontrado: {session_id}")
                return
            
            # Atualizar dados baseado no módulo
            if module_name == "search":
                context.search_results.update(data)
            elif module_name == "competitor":
                context.competitor_data.update(data)
            elif module_name == "market":
                context.market_insights.update(data)
            elif module_name == "viral":
                context.viral_content.update(data)
            
            # Registrar execução do módulo
            if module_name not in context.modules_executed:
                context.modules_executed.append(module_name)
            
            # Atualizar score de qualidade
            context.quality_scores[module_name] = quality_score
            
            # Salvar contexto atualizado
            self._save_context(context)
            
            logger.debug(f"🔄 Contexto atualizado - Módulo: {module_name}, Sessão: {session_id}")
    
    def get_unified_context_for_module(self, session_id: str, requesting_module: str) -> Dict[str, Any]:
        """Retorna contexto unificado para um módulo específico"""
        
        context = self.get_context(session_id)
        if not context:
            return {}
        
        # Contexto base sempre disponível
        unified_context = {
            "session_id": context.session_id,
            "produto": context.produto,
            "publico_alvo": context.publico_alvo,
            "tone": context.tone,
            "language": context.language,
            "target_audience_details": context.target_audience_details,
            "modules_executed": context.modules_executed
        }
        
        # Adicionar dados relevantes baseado no módulo solicitante
        if requesting_module == "synthesis":
            # Módulo de síntese precisa de todos os dados
            unified_context.update({
                "search_results": context.search_results,
                "competitor_data": context.competitor_data,
                "market_insights": context.market_insights,
                "viral_content": context.viral_content,
                "quality_scores": context.quality_scores
            })
        
        elif requesting_module == "competitor":
            # Análise de concorrência precisa de dados de mercado
            unified_context.update({
                "search_results": context.search_results,
                "market_insights": context.market_insights
            })
        
        elif requesting_module == "viral":
            # Conteúdo viral precisa de dados de concorrência e mercado
            unified_context.update({
                "competitor_data": context.competitor_data,
                "market_insights": context.market_insights,
                "search_results": context.search_results
            })
        
        elif requesting_module == "report":
            # Relatório precisa de todos os dados
            unified_context.update({
                "search_results": context.search_results,
                "competitor_data": context.competitor_data,
                "market_insights": context.market_insights,
                "viral_content": context.viral_content,
                "quality_scores": context.quality_scores
            })
        
        return unified_context
    
    def analyze_context_coherence(self, session_id: str) -> Dict[str, Any]:
        """Analisa coerência do contexto entre módulos"""
        
        context = self.get_context(session_id)
        if not context:
            return {"coherence_score": 0.0, "issues": ["Contexto não encontrado"]}
        
        issues = []
        coherence_factors = []
        
        # Verificar se produto é consistente
        produto_mentions = []
        for module_data in [context.search_results, context.competitor_data, 
                           context.market_insights, context.viral_content]:
            if isinstance(module_data, dict):
                produto_text = json.dumps(module_data, ensure_ascii=False).lower()
                if context.produto.lower() in produto_text:
                    produto_mentions.append(True)
                else:
                    produto_mentions.append(False)
        
        produto_coherence = sum(produto_mentions) / len(produto_mentions) if produto_mentions else 0
        coherence_factors.append(produto_coherence)
        
        if produto_coherence < 0.5:
            issues.append("Produto não mencionado consistentemente entre módulos")
        
        # Verificar se público-alvo é consistente
        publico_mentions = []
        for module_data in [context.search_results, context.competitor_data, 
                           context.market_insights, context.viral_content]:
            if isinstance(module_data, dict):
                publico_text = json.dumps(module_data, ensure_ascii=False).lower()
                publico_words = context.publico_alvo.lower().split()
                mentions = sum(1 for word in publico_words if word in publico_text)
                publico_mentions.append(mentions > 0)
        
        publico_coherence = sum(publico_mentions) / len(publico_mentions) if publico_mentions else 0
        coherence_factors.append(publico_coherence)
        
        if publico_coherence < 0.3:
            issues.append("Público-alvo não considerado consistentemente entre módulos")
        
        # Verificar qualidade dos módulos
        avg_quality = sum(context.quality_scores.values()) / len(context.quality_scores) if context.quality_scores else 0
        coherence_factors.append(avg_quality)
        
        if avg_quality < 0.6:
            issues.append("Qualidade média dos módulos abaixo do esperado")
        
        # Calcular score final
        final_coherence = sum(coherence_factors) / len(coherence_factors) if coherence_factors else 0
        
        return {
            "coherence_score": final_coherence,
            "issues": issues,
            "produto_coherence": produto_coherence,
            "publico_coherence": publico_coherence,
            "avg_quality": avg_quality,
            "modules_executed": len(context.modules_executed),
            "recommendations": self._generate_coherence_recommendations(issues, final_coherence)
        }
    
    def _generate_coherence_recommendations(self, issues: List[str], coherence_score: float) -> List[str]:
        """Gera recomendações para melhorar coerência"""
        
        recommendations = []
        
        if coherence_score < 0.4:
            recommendations.append("Reiniciar análise com parâmetros mais específicos")
        elif coherence_score < 0.7:
            recommendations.append("Revisar dados coletados e ajustar consultas")
        
        if "Produto não mencionado" in str(issues):
            recommendations.append("Incluir nome do produto em todas as consultas de busca")
        
        if "Público-alvo não considerado" in str(issues):
            recommendations.append("Especificar melhor o público-alvo nas análises")
        
        if "Qualidade média" in str(issues):
            recommendations.append("Verificar configuração das APIs e modelos de IA")
        
        return recommendations
    
    def _save_context(self, context: SessionContext):
        """Salva contexto no disco"""
        try:
            context_file = os.path.join(self.data_dir, f"context_{context.session_id}.json")
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(context), f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar contexto: {e}")
    
    def _load_context(self, session_id: str) -> Optional[SessionContext]:
        """Carrega contexto do disco"""
        try:
            context_file = os.path.join(self.data_dir, f"context_{session_id}.json")
            if os.path.exists(context_file):
                with open(context_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return SessionContext(**data)
        except Exception as e:
            logger.error(f"❌ Erro ao carregar contexto: {e}")
        
        return None
    
    def cleanup_old_contexts(self, days_old: int = 7):
        """Remove contextos antigos"""
        
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        removed_count = 0
        for session_id in list(self.contexts.keys()):
            context = self.contexts[session_id]
            try:
                context_date = datetime.fromisoformat(context.timestamp)
                if context_date < cutoff_date:
                    # Remove da memória
                    del self.contexts[session_id]
                    
                    # Remove do disco
                    context_file = os.path.join(self.data_dir, f"context_{session_id}.json")
                    if os.path.exists(context_file):
                        os.remove(context_file)
                    
                    removed_count += 1
            except:
                # Se não conseguir parsear a data, remove
                if session_id in self.contexts:
                    del self.contexts[session_id]
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"🧹 Removidos {removed_count} contextos antigos")

# Instância global
shared_context_manager = SharedContextManager()