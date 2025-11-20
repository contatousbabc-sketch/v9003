#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Integridade de Dados de Sessão
Garante que dados de sessão não sejam corrompidos ou perdidos durante processamento
"""

import os
import json
import hashlib
import logging
import threading
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import pickle
import gzip

logger = logging.getLogger(__name__)

@dataclass
class SessionSnapshot:
    """Snapshot de dados de sessão para backup"""
    session_id: str
    timestamp: str
    data_hash: str
    data_size: int
    module_states: Dict[str, Any]
    checkpoint_name: str

class SessionDataIntegrity:
    """Sistema de integridade de dados de sessão"""
    
    def __init__(self, data_dir: str = "analyses_data"):
        self.data_dir = data_dir
        self.sessions_dir = os.path.join(data_dir, "sessions")
        self.backups_dir = os.path.join(data_dir, "session_backups")
        self.integrity_log = os.path.join(data_dir, "session_integrity.json")
        
        # Criar diretórios
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.backups_dir, exist_ok=True)
        
        # Cache de sessões ativas
        self.active_sessions = {}
        self.session_locks = {}
        self.global_lock = threading.Lock()
        
        # Configurações
        self.backup_interval = 300  # 5 minutos
        self.max_backups_per_session = 10
        self.integrity_check_interval = 60  # 1 minuto
        
        # Iniciar monitoramento
        self._start_integrity_monitoring()
        
        logger.info("🔒 Sistema de Integridade de Dados de Sessão inicializado")
    
    def create_session(self, session_id: str, initial_data: Dict[str, Any]) -> bool:
        """Cria nova sessão com dados iniciais"""
        
        try:
            with self.global_lock:
                if session_id in self.active_sessions:
                    logger.warning(f"⚠️ Sessão {session_id} já existe")
                    return False
                
                # Criar lock específico para a sessão
                self.session_locks[session_id] = threading.Lock()
            
            with self.session_locks[session_id]:
                # Preparar dados da sessão
                session_data = {
                    'session_id': session_id,
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'data': initial_data,
                    'integrity_hash': self._calculate_data_hash(initial_data),
                    'version': 1,
                    'module_states': {},
                    'checkpoints': []
                }
                
                # Salvar sessão
                session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)
                
                # Adicionar ao cache
                self.active_sessions[session_id] = session_data
                
                # Criar backup inicial
                self._create_backup(session_id, "initial")
                
                logger.info(f"✅ Sessão {session_id} criada com integridade")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar sessão {session_id}: {e}")
            return False
    
    def update_session_data(self, session_id: str, module_name: str, 
                           data_update: Dict[str, Any], create_checkpoint: bool = False) -> bool:
        """Atualiza dados da sessão de forma segura"""
        
        try:
            # Verificar se sessão existe
            if session_id not in self.session_locks:
                logger.error(f"❌ Sessão {session_id} não encontrada")
                return False
            
            with self.session_locks[session_id]:
                # Carregar dados atuais se não estiver em cache
                if session_id not in self.active_sessions:
                    self.active_sessions[session_id] = self._load_session_from_disk(session_id)
                    if not self.active_sessions[session_id]:
                        return False
                
                session_data = self.active_sessions[session_id]
                
                # Verificar integridade antes da atualização
                current_hash = self._calculate_data_hash(session_data['data'])
                if current_hash != session_data['integrity_hash']:
                    logger.error(f"❌ Integridade comprometida na sessão {session_id}")
                    self._handle_integrity_violation(session_id)
                    return False
                
                # Criar checkpoint se solicitado
                if create_checkpoint:
                    checkpoint_name = f"{module_name}_{int(time.time())}"
                    self._create_backup(session_id, checkpoint_name)
                
                # Atualizar dados
                if 'data' not in session_data:
                    session_data['data'] = {}
                
                session_data['data'].update(data_update)
                session_data['last_updated'] = datetime.now().isoformat()
                session_data['version'] += 1
                session_data['integrity_hash'] = self._calculate_data_hash(session_data['data'])
                
                # Atualizar estado do módulo
                session_data['module_states'][module_name] = {
                    'last_update': datetime.now().isoformat(),
                    'data_keys': list(data_update.keys()),
                    'status': 'updated'
                }
                
                # Salvar no disco
                self._save_session_to_disk(session_id, session_data)
                
                logger.debug(f"🔄 Sessão {session_id} atualizada pelo módulo {module_name}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar sessão {session_id}: {e}")
            return False
    
    def get_session_data(self, session_id: str, verify_integrity: bool = True) -> Optional[Dict[str, Any]]:
        """Recupera dados da sessão com verificação de integridade"""
        
        try:
            if session_id not in self.session_locks:
                logger.error(f"❌ Sessão {session_id} não encontrada")
                return None
            
            with self.session_locks[session_id]:
                # Carregar do cache ou disco
                if session_id not in self.active_sessions:
                    self.active_sessions[session_id] = self._load_session_from_disk(session_id)
                
                session_data = self.active_sessions[session_id]
                if not session_data:
                    return None
                
                # Verificar integridade se solicitado
                if verify_integrity:
                    current_hash = self._calculate_data_hash(session_data['data'])
                    if current_hash != session_data['integrity_hash']:
                        logger.error(f"❌ Integridade comprometida na sessão {session_id}")
                        
                        # Tentar recuperar do backup mais recente
                        recovered_data = self._recover_from_backup(session_id)
                        if recovered_data:
                            self.active_sessions[session_id] = recovered_data
                            return recovered_data['data']
                        
                        return None
                
                return session_data['data']
                
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar sessão {session_id}: {e}")
            return None
    
    def _calculate_data_hash(self, data: Any) -> str:
        """Calcula hash dos dados para verificação de integridade"""
        
        try:
            # Serializar dados de forma determinística
            json_str = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
            return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
        except:
            return "unknown"
    
    def _create_backup(self, session_id: str, checkpoint_name: str) -> bool:
        """Cria backup comprimido da sessão"""
        
        try:
            if session_id not in self.active_sessions:
                return False
            
            session_data = self.active_sessions[session_id]
            
            # Criar snapshot
            snapshot = SessionSnapshot(
                session_id=session_id,
                timestamp=datetime.now().isoformat(),
                data_hash=session_data['integrity_hash'],
                data_size=len(json.dumps(session_data, default=str)),
                module_states=session_data.get('module_states', {}),
                checkpoint_name=checkpoint_name
            )
            
            # Salvar backup comprimido
            backup_filename = f"{session_id}_{checkpoint_name}_{int(time.time())}.backup.gz"
            backup_path = os.path.join(self.backups_dir, backup_filename)
            
            backup_data = {
                'snapshot': asdict(snapshot),
                'session_data': session_data
            }
            
            with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Atualizar lista de checkpoints na sessão
            if 'checkpoints' not in session_data:
                session_data['checkpoints'] = []
            
            session_data['checkpoints'].append({
                'name': checkpoint_name,
                'timestamp': snapshot.timestamp,
                'backup_file': backup_filename,
                'data_hash': snapshot.data_hash
            })
            
            # Limitar número de backups
            self._cleanup_old_backups(session_id)
            
            logger.debug(f"💾 Backup criado para sessão {session_id}: {checkpoint_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup da sessão {session_id}: {e}")
            return False
    
    def _recover_from_backup(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Recupera sessão do backup mais recente"""
        
        try:
            # Encontrar backup mais recente
            backup_files = []
            for filename in os.listdir(self.backups_dir):
                if filename.startswith(f"{session_id}_") and filename.endswith('.backup.gz'):
                    backup_path = os.path.join(self.backups_dir, filename)
                    backup_files.append((backup_path, os.path.getmtime(backup_path)))
            
            if not backup_files:
                logger.error(f"❌ Nenhum backup encontrado para sessão {session_id}")
                return None
            
            # Ordenar por data de modificação (mais recente primeiro)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            latest_backup = backup_files[0][0]
            
            # Carregar backup
            with gzip.open(latest_backup, 'rt', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            recovered_session = backup_data['session_data']
            
            # Verificar integridade do backup
            backup_hash = self._calculate_data_hash(recovered_session['data'])
            if backup_hash == backup_data['snapshot']['data_hash']:
                logger.info(f"✅ Sessão {session_id} recuperada do backup")
                return recovered_session
            else:
                logger.error(f"❌ Backup corrompido para sessão {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao recuperar backup da sessão {session_id}: {e}")
            return None
    
    def _load_session_from_disk(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Carrega sessão do disco"""
        
        try:
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            if not os.path.exists(session_file):
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar sessão {session_id} do disco: {e}")
            return None
    
    def _save_session_to_disk(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Salva sessão no disco"""
        
        try:
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            
            # Salvar em arquivo temporário primeiro
            temp_file = session_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Mover arquivo temporário para final (operação atômica)
            os.replace(temp_file, session_file)
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar sessão {session_id}: {e}")
            return False
    
    def _handle_integrity_violation(self, session_id: str):
        """Trata violação de integridade"""
        
        logger.error(f"🚨 VIOLAÇÃO DE INTEGRIDADE detectada na sessão {session_id}")
        
        # Registrar violação
        violation_record = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'integrity_violation',
            'action_taken': 'backup_recovery_attempted'
        }
        
        self._log_integrity_event(violation_record)
        
        # Tentar recuperar do backup
        recovered_data = self._recover_from_backup(session_id)
        if recovered_data:
            self.active_sessions[session_id] = recovered_data
            self._save_session_to_disk(session_id, recovered_data)
            logger.info(f"✅ Sessão {session_id} recuperada após violação de integridade")
        else:
            logger.error(f"❌ Não foi possível recuperar sessão {session_id}")
    
    def _cleanup_old_backups(self, session_id: str):
        """Remove backups antigos para economizar espaço"""
        
        try:
            # Encontrar todos os backups da sessão
            backup_files = []
            for filename in os.listdir(self.backups_dir):
                if filename.startswith(f"{session_id}_") and filename.endswith('.backup.gz'):
                    backup_path = os.path.join(self.backups_dir, filename)
                    backup_files.append((backup_path, os.path.getmtime(backup_path)))
            
            # Se há mais backups que o limite, remover os mais antigos
            if len(backup_files) > self.max_backups_per_session:
                backup_files.sort(key=lambda x: x[1])  # Ordenar por data
                
                # Remover os mais antigos
                for backup_path, _ in backup_files[:-self.max_backups_per_session]:
                    os.remove(backup_path)
                    logger.debug(f"🗑️ Backup antigo removido: {backup_path}")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao limpar backups antigos: {e}")
    
    def _start_integrity_monitoring(self):
        """Inicia monitoramento contínuo de integridade"""
        
        def monitor_integrity():
            while True:
                try:
                    time.sleep(self.integrity_check_interval)
                    self._check_all_sessions_integrity()
                except Exception as e:
                    logger.error(f"❌ Erro no monitoramento de integridade: {e}")
        
        monitor_thread = threading.Thread(target=monitor_integrity, daemon=True)
        monitor_thread.start()
    
    def _check_all_sessions_integrity(self):
        """Verifica integridade de todas as sessões ativas"""
        
        for session_id in list(self.active_sessions.keys()):
            try:
                if session_id in self.session_locks:
                    with self.session_locks[session_id]:
                        session_data = self.active_sessions[session_id]
                        current_hash = self._calculate_data_hash(session_data['data'])
                        
                        if current_hash != session_data['integrity_hash']:
                            self._handle_integrity_violation(session_id)
                            
            except Exception as e:
                logger.error(f"❌ Erro ao verificar integridade da sessão {session_id}: {e}")
    
    def _log_integrity_event(self, event: Dict[str, Any]):
        """Registra evento de integridade"""
        
        try:
            if os.path.exists(self.integrity_log):
                with open(self.integrity_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = []
            
            log_data.append(event)
            
            # Manter apenas os últimos 1000 eventos
            if len(log_data) > 1000:
                log_data = log_data[-1000:]
            
            with open(self.integrity_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            logger.error(f"❌ Erro ao registrar evento de integridade: {e}")
    
    def get_session_integrity_report(self, session_id: str) -> Dict[str, Any]:
        """Retorna relatório de integridade de uma sessão"""
        
        try:
            if session_id not in self.active_sessions:
                return {"error": "Sessão não encontrada"}
            
            session_data = self.active_sessions[session_id]
            current_hash = self._calculate_data_hash(session_data['data'])
            
            return {
                'session_id': session_id,
                'integrity_status': 'valid' if current_hash == session_data['integrity_hash'] else 'compromised',
                'current_hash': current_hash,
                'expected_hash': session_data['integrity_hash'],
                'version': session_data.get('version', 1),
                'last_updated': session_data.get('last_updated'),
                'module_states': session_data.get('module_states', {}),
                'checkpoints_count': len(session_data.get('checkpoints', [])),
                'data_size': len(json.dumps(session_data['data'], default=str))
            }
            
        except Exception as e:
            return {"error": f"Erro ao gerar relatório: {str(e)}"}
    
    def cleanup_session(self, session_id: str):
        """Remove sessão e seus backups"""
        
        try:
            # Remover do cache
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Remover lock
            if session_id in self.session_locks:
                del self.session_locks[session_id]
            
            # Remover arquivo da sessão
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            if os.path.exists(session_file):
                os.remove(session_file)
            
            # Remover backups
            for filename in os.listdir(self.backups_dir):
                if filename.startswith(f"{session_id}_"):
                    backup_path = os.path.join(self.backups_dir, filename)
                    os.remove(backup_path)
            
            logger.info(f"🗑️ Sessão {session_id} removida completamente")
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar sessão {session_id}: {e}")

# Instância global
session_data_integrity = SessionDataIntegrity()