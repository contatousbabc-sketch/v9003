#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Sessões - ARQV18 Enhanced v18.0
Sistema para salvar e continuar análises de onde pararam
"""

import os
import json
import pickle
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

class SessionManager:
    """Gerenciador de sessões para continuar análises"""
    
    def __init__(self, session_dir: str = "sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        self.current_session_id = None
        self.current_session_data = {}
        
    def create_session(self, analysis_data: Dict[str, Any]) -> str:
        """Cria nova sessão"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_session_id = session_id
        
        # Dados iniciais da sessão
        self.current_session_data = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'iniciada',
            'analysis_data': analysis_data,
            'completed_modules': [],
            'current_module': None,
            'progress': {
                'total_modules': 12,  # Total de módulos
                'completed': 0,
                'current_step': 0,
                'percentage': 0.0
            },
            'results': {},
            'errors': []
        }
        
        self.save_session()
        return session_id
    
    def load_session(self, session_id: str) -> bool:
        """Carrega sessão existente"""
        session_file = self.session_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return False
            
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                self.current_session_data = json.load(f)
            
            self.current_session_id = session_id
            return True
        except Exception as e:
            print(f"Erro ao carregar sessão {session_id}: {e}")
            return False
    
    def save_session(self):
        """Salva sessão atual"""
        if not self.current_session_id:
            return False
            
        session_file = self.session_dir / f"{self.current_session_id}.json"
        
        try:
            self.current_session_data['updated_at'] = datetime.now().isoformat()
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_session_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar sessão: {e}")
            return False
    
    def mark_module_completed(self, module_name: str, result: Any = None):
        """Marca módulo como concluído"""
        if module_name not in self.current_session_data['completed_modules']:
            self.current_session_data['completed_modules'].append(module_name)
        
        if result:
            self.current_session_data['results'][module_name] = result
        
        # Atualiza progresso
        completed = len(self.current_session_data['completed_modules'])
        total = self.current_session_data['progress']['total_modules']
        
        self.current_session_data['progress']['completed'] = completed
        self.current_session_data['progress']['percentage'] = (completed / total) * 100
        
        self.save_session()
    
    def set_current_module(self, module_name: str, step: int = 0):
        """Define módulo atual"""
        self.current_session_data['current_module'] = module_name
        self.current_session_data['progress']['current_step'] = step
        self.save_session()
    
    def is_module_completed(self, module_name: str) -> bool:
        """Verifica se módulo foi concluído"""
        return module_name in self.current_session_data['completed_modules']
    
    def get_next_module(self) -> Optional[str]:
        """Retorna próximo módulo a ser executado"""
        all_modules = [
            'avatar_generation',
            'competitor_analysis', 
            'funnel_generation',
            'keyword_research',
            'content_strategy',
            'market_analysis',
            'persona_development',
            'pricing_strategy',
            'distribution_channels',
            'risk_assessment',
            'financial_projections',
            'final_report'
        ]
        
        for module in all_modules:
            if not self.is_module_completed(module):
                return module
        
        return None
    
    def get_progress(self) -> Dict[str, Any]:
        """Retorna progresso atual"""
        return self.current_session_data.get('progress', {})
    
    def get_completed_modules(self) -> List[str]:
        """Retorna lista de módulos concluídos"""
        return self.current_session_data.get('completed_modules', [])
    
    def get_session_data(self) -> Dict[str, Any]:
        """Retorna dados da sessão"""
        return self.current_session_data
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """Lista todas as sessões"""
        sessions = []
        
        for session_file in self.session_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                sessions.append({
                    'session_id': session_data.get('session_id'),
                    'created_at': session_data.get('created_at'),
                    'updated_at': session_data.get('updated_at'),
                    'status': session_data.get('status'),
                    'progress': session_data.get('progress', {}),
                    'completed_modules': len(session_data.get('completed_modules', [])),
                    'total_modules': session_data.get('progress', {}).get('total_modules', 12)
                })
            except Exception as e:
                print(f"Erro ao ler sessão {session_file}: {e}")
        
        return sorted(sessions, key=lambda x: x['updated_at'], reverse=True)
    
    def delete_session(self, session_id: str) -> bool:
        """Deleta sessão"""
        session_file = self.session_dir / f"{session_id}.json"
        
        try:
            if session_file.exists():
                session_file.unlink()
                return True
        except Exception as e:
            print(f"Erro ao deletar sessão {session_id}: {e}")
        
        return False
    
    def add_error(self, error_message: str, module_name: str = None):
        """Adiciona erro à sessão"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'message': error_message,
            'module': module_name
        }
        
        self.current_session_data['errors'].append(error_data)
        self.save_session()
    
    def update_status(self, status: str):
        """Atualiza status da sessão"""
        self.current_session_data['status'] = status
        self.save_session()
    
    def get_module_result(self, module_name: str) -> Any:
        """Retorna resultado de um módulo específico"""
        return self.current_session_data.get('results', {}).get(module_name)
    
    def calculate_detailed_progress(self, current_module: str, module_step: int, total_steps: int) -> float:
        """Calcula progresso detalhado incluindo passos do módulo atual"""
        completed_modules = len(self.current_session_data['completed_modules'])
        total_modules = self.current_session_data['progress']['total_modules']
        
        # Progresso dos módulos completos
        base_progress = (completed_modules / total_modules) * 100
        
        # Progresso do módulo atual
        if total_steps > 0:
            current_module_progress = (module_step / total_steps) * (100 / total_modules)
        else:
            current_module_progress = 0
        
        return min(base_progress + current_module_progress, 100.0)

# Instância global do gerenciador de sessões
session_manager = SessionManager()