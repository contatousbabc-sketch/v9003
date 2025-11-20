#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v2.0 - Enhanced Progress Tracker
Sistema de progresso aprimorado com timing realista e detalhes precisos
"""

import time
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from services.auto_save_manager import salvar_etapa

logger = logging.getLogger(__name__)

class EnhancedProgressTracker:
    """Rastreador de progresso aprimorado com timing realista"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_step = 0
        self.total_steps = 14  # Aumentado para incluir WebSailor
        self.start_time = time.time()
        
        # Etapas com timing realista baseado no log
        self.steps = [
            {
                "name": "🔍 Validando dados de entrada e preparando análise",
                "estimated_duration": 2,
                "description": "Verificação de campos obrigatórios e preparação do ambiente"
            },
            {
                "name": "🌐 Iniciando WebSailor para navegação inteligente",
                "estimated_duration": 5,
                "description": "Ativação do agente de navegação web profunda"
            },
            {
                "name": "🔍 Executando pesquisa web massiva multi-engine",
                "estimated_duration": 45,
                "description": "Google + Serper + Bing + DuckDuckGo + Yahoo"
            },
            {
                "name": "📄 Extraindo conteúdo de fontes preferenciais",
                "estimated_duration": 120,
                "description": "Extração robusta com Trafilatura + Readability + Newspaper"
            },
            {
                "name": "🤖 Analisando com Gemini 2.5 Pro (modelo primário)",
                "estimated_duration": 30,
                "description": "Análise arqueológica ultra-detalhada com IA avançada"
            },
            {
                "name": "👤 Criando avatar arqueológico ultra-detalhado",
                "estimated_duration": 25,
                "description": "Perfil demográfico + psicográfico + dores + desejos"
            },
            {
                "name": "🧠 Gerando drivers mentais customizados (19 universais)",
                "estimated_duration": 20,
                "description": "Gatilhos psicológicos personalizados para o segmento"
            },
            {
                "name": "🎭 Desenvolvendo provas visuais instantâneas (PROVIs)",
                "estimated_duration": 25,
                "description": "Experimentos visuais para conceitos abstratos"
            },
            {
                "name": "🛡️ Construindo sistema anti-objeção psicológico",
                "estimated_duration": 18,
                "description": "Arsenal contra objeções universais + ocultas"
            },
            {
                "name": "🎯 Arquitetando pré-pitch invisível completo",
                "estimated_duration": 22,
                "description": "Orquestração emocional + roteiro de ativação"
            },
            {
                "name": "⚔️ Mapeando concorrência e posicionamento estratégico",
                "estimated_duration": 15,
                "description": "Análise SWOT + gaps de oportunidade"
            },
            {
                "name": "📈 Calculando métricas forenses e projeções",
                "estimated_duration": 12,
                "description": "KPIs + ROI + cenários conservador/realista/otimista"
            },
            {
                "name": "🔮 Predizendo futuro do mercado (36 meses)",
                "estimated_duration": 15,
                "description": "Tendências + cenários + pontos de inflexão"
            },
            {
                "name": "✨ Consolidando análise arqueológica final",
                "estimated_duration": 8,
                "description": "Validação + limpeza + metadados + relatório"
            }
        ]
        
        self.detailed_logs = []
        self.step_start_times = {}
        
        logger.info(f"Enhanced Progress Tracker inicializado para {session_id}")
    
    def update_progress(
        self, 
        step: int, 
        message: str, 
        details: str = None,
        force_timing: bool = False
    ) -> Dict[str, Any]:
        """Atualiza progresso com timing realista"""
        
        # Registra início da etapa se for nova
        if step != self.current_step:
            self.step_start_times[step] = time.time()
            
            # Calcula duração da etapa anterior
            if self.current_step > 0 and self.current_step in self.step_start_times:
                prev_duration = time.time() - self.step_start_times[self.current_step]
                logger.info(f"⏱️ Etapa {self.current_step} concluída em {prev_duration:.1f}s")
        
        self.current_step = step
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # Calcula tempo estimado baseado nas etapas
        total_estimated_duration = sum(step_info['estimated_duration'] for step_info in self.steps)
        completed_duration = sum(
            self.steps[i]['estimated_duration'] 
            for i in range(min(step, len(self.steps)))
        )
        
        if step > 0 and not force_timing:
            # Usa timing realista baseado no progresso
            progress_ratio = completed_duration / total_estimated_duration
            estimated_total = elapsed / progress_ratio if progress_ratio > 0 else total_estimated_duration
            remaining = max(0, estimated_total - elapsed)
        else:
            remaining = total_estimated_duration - completed_duration
        
        # Informações da etapa atual
        current_step_info = self.steps[min(step - 1, len(self.steps) - 1)] if step > 0 else self.steps[0]
        
        progress_data = {
            "session_id": self.session_id,
            "current_step": step,
            "total_steps": self.total_steps,
            "percentage": (step / self.total_steps) * 100,
            "current_message": message,
            "detailed_message": details or message,
            "step_description": current_step_info.get('description', ''),
            "elapsed_time": elapsed,
            "estimated_remaining": remaining,
            "estimated_total": elapsed + remaining,
            "current_step_duration": current_step_info.get('estimated_duration', 0),
            "timing_realistic": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log detalhado
        log_entry = {
            "step": step,
            "message": message,
            "details": details,
            "description": current_step_info.get('description', ''),
            "timestamp": datetime.now().isoformat(),
            "elapsed": elapsed,
            "estimated_remaining": remaining
        }
        self.detailed_logs.append(log_entry)
        
        # Salva progresso
        salvar_etapa("progresso_detalhado", progress_data, categoria="logs")
        
        logger.info(f"📊 Progresso {self.session_id}: {step}/{self.total_steps} ({progress_data['percentage']:.1f}%) - {message}")
        
        return progress_data
    
    def complete(self):
        """Marca análise como completa"""
        
        final_duration = time.time() - self.start_time
        
        completion_data = self.update_progress(
            self.total_steps, 
            "🎉 Análise arqueológica concluída com sucesso!",
            f"Análise ultra-detalhada finalizada em {final_duration:.1f} segundos",
            force_timing=True
        )
        
        # Salva estatísticas finais
        final_stats = {
            "session_id": self.session_id,
            "total_duration": final_duration,
            "total_steps_completed": self.total_steps,
            "average_step_duration": final_duration / self.total_steps,
            "detailed_logs": self.detailed_logs,
            "completion_timestamp": datetime.now().isoformat()
        }
        
        salvar_etapa("progresso_final", final_stats, categoria="logs")
        
        logger.info(f"🏁 Progresso finalizado para {self.session_id} em {final_duration:.1f}s")
        
        return completion_data
    
    def get_current_status(self) -> Dict[str, Any]:
        """Retorna status atual detalhado"""
        
        elapsed = time.time() - self.start_time
        current_step_info = self.steps[min(self.current_step - 1, len(self.steps) - 1)] if self.current_step > 0 else self.steps[0]
        
        # Calcula estimativas realistas
        total_estimated = sum(step['estimated_duration'] for step in self.steps)
        completed_estimated = sum(
            self.steps[i]['estimated_duration'] 
            for i in range(min(self.current_step, len(self.steps)))
        )
        
        progress_ratio = completed_estimated / total_estimated if total_estimated > 0 else 0
        estimated_total = elapsed / progress_ratio if progress_ratio > 0 else total_estimated
        remaining = max(0, estimated_total - elapsed)
        
        return {
            "session_id": self.session_id,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "percentage": (self.current_step / self.total_steps) * 100,
            "current_message": current_step_info['name'],
            "current_description": current_step_info['description'],
            "elapsed_time": elapsed,
            "estimated_remaining": remaining,
            "estimated_total": estimated_total,
            "detailed_logs": self.detailed_logs[-10:],  # Últimos 10 logs
            "is_complete": self.current_step >= self.total_steps,
            "timing_realistic": True,
            "next_step": self.steps[self.current_step]['name'] if self.current_step < len(self.steps) else None
        }
    
    def get_step_breakdown(self) -> List[Dict[str, Any]]:
        """Retorna breakdown detalhado das etapas"""
        
        breakdown = []
        
        for i, step_info in enumerate(self.steps):
            status = "completed" if i < self.current_step else "pending"
            if i == self.current_step:
                status = "in_progress"
            
            breakdown.append({
                "step_number": i + 1,
                "name": step_info['name'],
                "description": step_info['description'],
                "estimated_duration": step_info['estimated_duration'],
                "status": status,
                "actual_duration": self._get_actual_step_duration(i + 1) if status == "completed" else None
            })
        
        return breakdown
    
    def _get_actual_step_duration(self, step: int) -> Optional[float]:
        """Calcula duração real de uma etapa"""
        
        if step in self.step_start_times and step + 1 in self.step_start_times:
            return self.step_start_times[step + 1] - self.step_start_times[step]
        
        return None

# Função helper para criar tracker
def create_enhanced_progress_tracker(session_id: str) -> EnhancedProgressTracker:
    """Cria tracker de progresso aprimorado"""
    return EnhancedProgressTracker(session_id)

# Instância global para compatibilidade com imports existentes
class ProgressTrackerManager:
    """Gerenciador global de progress trackers"""
    
    def __init__(self):
        self.sessions = {}
        self.logger = logging.getLogger(__name__)
    
    def start_session(self, session_id: str, total_steps: int = 14):
        """Inicia uma nova sessão de progresso"""
        tracker = EnhancedProgressTracker(session_id)
        tracker.total_steps = total_steps
        self.sessions[session_id] = tracker
        self.logger.info(f"🎯 Sessão de progresso iniciada: {session_id}")
        return tracker
    
    def update_progress(self, session_id: str, step: int, message: str, details: str = None):
        """Atualiza progresso de uma sessão"""
        if session_id in self.sessions:
            return self.sessions[session_id].update_progress(step, message, details)
        else:
            self.logger.warning(f"⚠️ Sessão não encontrada: {session_id}")
            return None
    
    def complete_session(self, session_id: str):
        """Completa uma sessão"""
        if session_id in self.sessions:
            self.sessions[session_id].complete()
            self.logger.info(f"✅ Sessão completada: {session_id}")
        else:
            self.logger.warning(f"⚠️ Sessão não encontrada para completar: {session_id}")
    
    def get_session_progress(self, session_id: str):
        """Obtém progresso de uma sessão"""
        if session_id in self.sessions:
            return self.sessions[session_id].get_current_status()
        else:
            return {"error": f"Sessão {session_id} não encontrada"}
    
    def get_progress(self, session_id: str):
        """Obtém progresso de uma sessão (método alternativo)"""
        return self.get_session_progress(session_id)
    
    def reset(self):
        """Reseta todas as sessões"""
        self.sessions.clear()
        self.logger.info("🔄 Todas as sessões resetadas")

# Instância global para compatibilidade
progress_tracker = ProgressTrackerManager()