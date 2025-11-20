#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Local Atual - Sistema de Log em Tempo Real para Windows
Cria e atualiza arquivo de log específico por sessão na raiz do app
Monitora e salva todos os logs de execução em tempo real
OTIMIZADO PARA WINDOWS LOCAL
"""

import os
import sys
import json
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
import time
import queue
import traceback
import platform
from enum import Enum
import hashlib

class LogLevel(Enum):
    """✅ NOVO: Níveis de log estruturados"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(Enum):
    """✅ NOVO: Categorias específicas de log"""
    SYSTEM = "SYSTEM"
    API_ROTATION = "API_ROTATION"
    LLM_PROCESSING = "LLM_PROCESSING"
    CONTENT_EXTRACTION = "CONTENT_EXTRACTION"
    DEDUPLICATION = "DEDUPLICATION"
    EXTERNAL_AI = "EXTERNAL_AI"
    RULE_ENGINE = "RULE_ENGINE"
    DATA_COLLECTION = "DATA_COLLECTION"
    ERROR_HANDLING = "ERROR_HANDLING"
    PERFORMANCE = "PERFORMANCE"

class StructuredLogEntry:
    """✅ NOVO: Entrada de log estruturada"""
    
    def __init__(self, 
                 level: LogLevel,
                 category: LogCategory,
                 message: str,
                 session_id: str = None,
                 component: str = None,
                 operation: str = None,
                 data: Dict[str, Any] = None,
                 error: Exception = None,
                 duration_ms: float = None,
                 metadata: Dict[str, Any] = None):
        
        self.timestamp = datetime.now().isoformat()
        self.level = level
        self.category = category
        self.message = message
        self.session_id = session_id
        self.component = component
        self.operation = operation
        self.data = data or {}
        self.error = error
        self.duration_ms = duration_ms
        self.metadata = metadata or {}
        
        # Gera ID único para o log
        self.log_id = hashlib.md5(
            f"{self.timestamp}{self.message}{self.component}".encode()
        ).hexdigest()[:8]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        result = {
            'log_id': self.log_id,
            'timestamp': self.timestamp,
            'level': self.level.value,
            'category': self.category.value,
            'message': self.message,
            'session_id': self.session_id,
            'component': self.component,
            'operation': self.operation,
            'data': self.data,
            'duration_ms': self.duration_ms,
            'metadata': self.metadata
        }
        
        if self.error:
            result['error'] = {
                'type': type(self.error).__name__,
                'message': str(self.error),
                'traceback': traceback.format_exc() if self.error else None
            }
        
        return result

class LogLocalAtual:
    """
    ✅ MELHORADO: Sistema de log local estruturado em tempo real
    
    Cria arquivos de log específicos por sessão com logs estruturados
    para rastreamento detalhado de problemas
    """
    
    def __init__(self, app_root_path: str = None):
        """
        Inicializa o sistema de log local para Windows
        
        Args:
            app_root_path: Caminho raiz do app (se None, detecta automaticamente)
        """
        # Detecta automaticamente o caminho raiz do app
        if app_root_path is None:
            current_dir = os.path.abspath(__file__)
            # Sobe até encontrar a pasta ARQ-ALPHA-V9 ou similar
            while True:
                parent_dir = os.path.dirname(current_dir)
                if parent_dir == current_dir:  # Chegou na raiz
                    # Se não encontrou, usa o diretório atual
                    self.app_root = os.getcwd()
                    break
                if any(name in os.path.basename(parent_dir).upper() for name in ['ARQ-ALPHA', 'ARQ_ALPHA']):
                    self.app_root = parent_dir
                    break
                current_dir = parent_dir
        else:
            self.app_root = os.path.abspath(app_root_path)
        
        # Configurações
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.log_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        self.lock = threading.Lock()
        self.is_windows = platform.system().lower() == 'windows'
        
        # Logger interno
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Inicia o worker thread
        self.start_worker()
        
        print(f"✅ Log Local Atual inicializado para {platform.system()}")
        print(f"📁 Diretório raiz: {self.app_root}")
        
        # Cria diretório se não existir
        if not os.path.exists(self.app_root):
            os.makedirs(self.app_root, exist_ok=True)
    
    def start_worker(self):
        """Inicia o thread worker para processar logs"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            print("🔄 Worker thread de log iniciado")
    
    def stop_worker(self):
        """Para o worker thread"""
        self.is_running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=4)
            print("⏹️ Worker thread de log parado")
    
    def _worker_loop(self):
        """Loop principal do worker thread"""
        while self.is_running:
            try:
                # Processa logs na fila
                try:
                    log_entry = self.log_queue.get(timeout=0.5)
                    self._write_log_entry(log_entry)
                    self.log_queue.task_done()
                except queue.Empty:
                    continue
                    
            except Exception as e:
                print(f"❌ Erro no worker loop: {e}")
                time.sleep(1)
    
    def create_session_log(self, session_id: str, session_info: Dict[str, Any] = None) -> str:
        """
        Cria um novo arquivo de log para uma sessão
        
        Args:
            session_id: ID da sessão
            session_info: Informações adicionais da sessão
            
        Returns:
            Caminho do arquivo de log criado
        """
        try:
            # Nome do arquivo de log
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"log_{session_id}_{timestamp}.txt"
            log_path = os.path.join(self.app_root, log_filename)
            
            # Informações da sessão
            session_data = {
                'session_id': session_id,
                'log_file': log_path,
                'created_at': datetime.now().isoformat(),
                'info': session_info or {},
                'entries_count': 0
            }
            
            with self.lock:
                self.active_sessions[session_id] = session_data
            
            # Cria arquivo inicial
            header = self._create_log_header(session_id, session_info)
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(header)
            
            print(f"📝 Log criado para sessão {session_id}: {log_filename}")
            
            # Log inicial
            self.add_log_entry(session_id, "SISTEMA", "INFO", f"Log iniciado para sessão {session_id}")
            
            return log_path
            
        except Exception as e:
            print(f"❌ Erro ao criar log para sessão {session_id}: {e}")
            return ""
    
    def _create_log_header(self, session_id: str, session_info: Dict[str, Any] = None) -> str:
        """Cria o cabeçalho do arquivo de log"""
        header = f"""
{'='*80}
                    ARQ-ALPHA-V9 - LOG DE EXECUÇÃO EM TEMPO REAL
{'='*80}
SESSÃO: {session_id}
INICIADO EM: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
ARQUIVO: {self.active_sessions.get(session_id, {}).get('log_file', 'N/A')}
{'='*80}

"""
        
        if session_info:
            header += "INFORMAÇÕES DA SESSÃO:\n"
            for key, value in session_info.items():
                header += f"  {key}: {value}\n"
            header += f"{'='*80}\n\n"
        
        return header
    
    def add_log_entry(self, session_id: str, component: str, level: str, message: str, 
                     code_executed: str = None, extra_data: Dict[str, Any] = None):
        """
        Adiciona uma entrada de log para uma sessão específica
        
        Args:
            session_id: ID da sessão
            component: Componente que gerou o log (ex: "ETAPA1", "SYNTHESIS", "AI_VERIFIER")
            level: Nível do log (INFO, WARNING, ERROR, DEBUG)
            message: Mensagem do log
            code_executed: Código que foi executado (opcional)
            extra_data: Dados extras (opcional)
        """
        if session_id not in self.active_sessions:
            print(f"⚠️ Sessão {session_id} não encontrada. Criando automaticamente...")
            self.create_session_log(session_id)
        
        log_entry = {
            'session_id': session_id,
            'timestamp': datetime.now(),
            'component': component,
            'level': level,
            'message': message,
            'code_executed': code_executed,
            'extra_data': extra_data or {}
        }
        
        # Adiciona à fila para processamento assíncrono
        self.log_queue.put(log_entry)
    
    def _write_log_entry(self, log_entry: Dict[str, Any]):
        """Escreve uma entrada de log no arquivo"""
        try:
            session_id = log_entry['session_id']
            
            if session_id not in self.active_sessions:
                return
            
            session_data = self.active_sessions[session_id]
            log_path = session_data['log_file']
            
            # Formata a entrada
            timestamp_str = log_entry['timestamp'].strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]
            
            # Linha principal
            log_line = f"[{timestamp_str}] [{log_entry['level']:7}] [{log_entry['component']:15}] {log_entry['message']}\n"
            
            # Código executado (se houver)
            code_section = ""
            if log_entry['code_executed']:
                code_section = f"""
{'─'*60}
CÓDIGO EXECUTADO:
{log_entry['code_executed']}
{'─'*60}
"""
            
            # Dados extras (se houver)
            extra_section = ""
            if log_entry['extra_data']:
                extra_section = f"""
DADOS EXTRAS:
{json.dumps(log_entry['extra_data'], indent=2, ensure_ascii=False)}
{'─'*40}
"""
            
            # Escreve no arquivo
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(log_line)
                if code_section:
                    f.write(code_section)
                if extra_section:
                    f.write(extra_section)
                f.write("\n")
            
            # Atualiza contador
            with self.lock:
                session_data['entries_count'] += 1
            
            # Também exibe no console para debug
            print(f"📝 [{session_id}] {log_entry['component']} - {log_entry['message']}")
            
        except Exception as e:
            print(f"❌ Erro ao escrever log: {e}")
    
    def log_etapa_iniciada(self, session_id: str, etapa_numero: int, etapa_nome: str, 
                          parametros: Dict[str, Any] = None):
        """Log específico para início de etapa"""
        message = f"🚀 ETAPA {etapa_numero} INICIADA: {etapa_nome}"
        self.add_log_entry(
            session_id=session_id,
            component=f"ETAPA{etapa_numero}",
            level="INFO",
            message=message,
            extra_data={
                'etapa_numero': etapa_numero,
                'etapa_nome': etapa_nome,
                'parametros': parametros or {},
                'status': 'iniciada'
            }
        )
    
    def log_etapa_concluida(self, session_id: str, etapa_numero: int, etapa_nome: str, 
                           resultado: Dict[str, Any] = None, tempo_execucao: float = None):
        """Log específico para conclusão de etapa"""
        tempo_str = f" em {tempo_execucao:.2f}s" if tempo_execucao else ""
        message = f"✅ ETAPA {etapa_numero} CONCLUÍDA: {etapa_nome}{tempo_str}"
        self.add_log_entry(
            session_id=session_id,
            component=f"ETAPA{etapa_numero}",
            level="INFO",
            message=message,
            extra_data={
                'etapa_numero': etapa_numero,
                'etapa_nome': etapa_nome,
                'resultado': resultado or {},
                'tempo_execucao': tempo_execucao,
                'status': 'concluida'
            }
        )
    
    def log_codigo_executado(self, session_id: str, component: str, codigo: str, 
                            resultado: Any = None, erro: str = None):
        """Log específico para código executado"""
        if erro:
            level = "ERROR"
            message = f"❌ Erro na execução de código em {component}: {erro}"
        else:
            level = "INFO"
            message = f"🔧 Código executado em {component}"
        
        self.add_log_entry(
            session_id=session_id,
            component=component,
            level=level,
            message=message,
            code_executed=codigo,
            extra_data={
                'resultado': str(resultado) if resultado else None,
                'erro': erro,
                'codigo_tamanho': len(codigo) if codigo else 0
            }
        )
    
    def log_api_call(self, session_id: str, component: str, api_name: str, 
                    parametros: Dict[str, Any] = None, resposta: Any = None, 
                    tempo_resposta: float = None, erro: str = None):
        """Log específico para chamadas de API"""
        if erro:
            level = "ERROR"
            message = f"❌ Erro na API {api_name}: {erro}"
        else:
            level = "INFO"
            tempo_str = f" ({tempo_resposta:.2f}s)" if tempo_resposta else ""
            message = f"🌐 Chamada API {api_name}{tempo_str}"
        
        self.add_log_entry(
            session_id=session_id,
            component=component,
            level=level,
            message=message,
            extra_data={
                'api_name': api_name,
                'parametros': parametros or {},
                'resposta_tamanho': len(str(resposta)) if resposta else 0,
                'tempo_resposta': tempo_resposta,
                'erro': erro
            }
        )
    
    def log_arquivo_processado(self, session_id: str, component: str, arquivo_path: str, 
                              operacao: str, resultado: Dict[str, Any] = None):
        """Log específico para processamento de arquivos"""
        message = f"📁 {operacao}: {os.path.basename(arquivo_path)}"
        self.add_log_entry(
            session_id=session_id,
            component=component,
            level="INFO",
            message=message,
            extra_data={
                'arquivo_path': arquivo_path,
                'operacao': operacao,
                'resultado': resultado or {}
            }
        )
    
    def finalize_session_log(self, session_id: str, resumo: Dict[str, Any] = None):
        """
        Finaliza o log de uma sessão
        
        Args:
            session_id: ID da sessão
            resumo: Resumo final da sessão
        """
        if session_id not in self.active_sessions:
            return
        
        try:
            session_data = self.active_sessions[session_id]
            log_path = session_data['log_file']
            
            # Resumo final
            fim_timestamp = datetime.now()
            inicio_timestamp = datetime.fromisoformat(session_data['created_at'])
            duracao_total = (fim_timestamp - inicio_timestamp).total_seconds()
            
            footer = f"""

{'='*80}
                            SESSÃO FINALIZADA
{'='*80}
SESSÃO: {session_id}
FINALIZADA EM: {fim_timestamp.strftime("%d/%m/%Y %H:%M:%S")}
DURAÇÃO TOTAL: {duracao_total:.2f} segundos
TOTAL DE LOGS: {session_data['entries_count']}
{'='*80}

"""
            
            if resumo:
                footer += "RESUMO DA SESSÃO:\n"
                for key, value in resumo.items():
                    footer += f"  {key}: {value}\n"
                footer += f"{'='*80}\n"
            
            # Escreve footer
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(footer)
            
            # Remove da lista de sessões ativas
            with self.lock:
                del self.active_sessions[session_id]
            
            print(f"🏁 Log finalizado para sessão {session_id}")
            print(f"📊 Total de {session_data['entries_count']} entradas em {duracao_total:.2f}s")
            
        except Exception as e:
            print(f"❌ Erro ao finalizar log da sessão {session_id}: {e}")
    
    def get_active_sessions(self) -> List[str]:
        """Retorna lista de sessões ativas"""
        with self.lock:
            return list(self.active_sessions.keys())
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retorna informações de uma sessão"""
        with self.lock:
            return self.active_sessions.get(session_id)
    
    # ✅ NOVOS MÉTODOS ESTRUTURADOS PARA RASTREAMENTO ESPECÍFICO
    
    def log_structured(self, entry: StructuredLogEntry):
        """
        ✅ NOVO: Log estruturado para rastreamento detalhado
        
        Args:
            entry: Entrada de log estruturada
        """
        if not entry.session_id:
            print("⚠️ Session ID não fornecido para log estruturado")
            return
        
        # Converte para formato legível
        formatted_message = self._format_structured_entry(entry)
        
        # Adiciona ao log tradicional
        self.add_log_entry(
            session_id=entry.session_id,
            component=entry.component or entry.category.value,
            level=entry.level.value,
            message=formatted_message,
            extra_data=entry.to_dict()
        )
        
        # Salva também em formato JSON estruturado
        self._save_structured_log(entry)
    
    def _format_structured_entry(self, entry: StructuredLogEntry) -> str:
        """Formata entrada estruturada para exibição legível"""
        parts = [entry.message]
        
        if entry.operation:
            parts.append(f"[{entry.operation}]")
        
        if entry.duration_ms:
            parts.append(f"({entry.duration_ms:.1f}ms)")
        
        if entry.data:
            key_data = []
            for key, value in entry.data.items():
                if isinstance(value, (int, float, str, bool)):
                    key_data.append(f"{key}={value}")
            if key_data:
                parts.append(f"({', '.join(key_data)})")
        
        return " ".join(parts)
    
    def _save_structured_log(self, entry: StructuredLogEntry):
        """Salva log estruturado em arquivo JSON separado"""
        try:
            if not entry.session_id:
                return
            
            # Arquivo JSON estruturado por sessão
            json_filename = f"structured_log_{entry.session_id}.jsonl"
            json_path = os.path.join(self.app_root, json_filename)
            
            # Adiciona linha JSON
            with open(json_path, 'a', encoding='utf-8') as f:
                json.dump(entry.to_dict(), f, ensure_ascii=False)
                f.write('\n')
                
        except Exception as e:
            print(f"❌ Erro ao salvar log estruturado: {e}")
    
    def log_llm_processing(self, session_id: str, operation: str, 
                          item_id: str = None, recommendation: str = None,
                          confidence: float = None, duration_ms: float = None,
                          error: Exception = None):
        """✅ NOVO: Log específico para processamento LLM"""
        
        data = {}
        if item_id:
            data['item_id'] = item_id
        if recommendation:
            data['recommendation'] = recommendation
        if confidence is not None:
            data['confidence'] = confidence
        
        level = LogLevel.ERROR if error else LogLevel.INFO
        message = f"LLM {operation}"
        if error:
            message += f" FALHOU: {str(error)}"
        elif recommendation:
            message += f" → {recommendation}"
        
        entry = StructuredLogEntry(
            level=level,
            category=LogCategory.LLM_PROCESSING,
            message=message,
            session_id=session_id,
            component="LLM_SERVICE",
            operation=operation,
            data=data,
            error=error,
            duration_ms=duration_ms
        )
        
        self.log_structured(entry)
    
    def log_api_rotation(self, session_id: str, operation: str,
                        key_index: int = None, success_rate: float = None,
                        cooldown_remaining: float = None, error: Exception = None):
        """✅ NOVO: Log específico para rotação de API keys"""
        
        data = {}
        if key_index is not None:
            data['key_index'] = key_index
        if success_rate is not None:
            data['success_rate'] = success_rate
        if cooldown_remaining is not None:
            data['cooldown_remaining'] = cooldown_remaining
        
        level = LogLevel.ERROR if error else LogLevel.INFO
        message = f"API Key {operation}"
        if error:
            message += f" FALHOU: {str(error)}"
        elif key_index is not None:
            message += f" (key #{key_index + 1})"
        
        entry = StructuredLogEntry(
            level=level,
            category=LogCategory.API_ROTATION,
            message=message,
            session_id=session_id,
            component="API_ROTATION",
            operation=operation,
            data=data,
            error=error
        )
        
        self.log_structured(entry)
    
    def log_content_extraction(self, session_id: str, url: str, 
                              method: str = None, content_length: int = None,
                              success: bool = True, duration_ms: float = None,
                              error: Exception = None, component: str = None,
                              operation: str = None, data: Dict[str, Any] = None):
        """✅ NOVO: Log específico para extração de conteúdo"""
        
        # Mescla dados básicos com dados extras passados
        log_data = {
            'url': url,
            'method': method,
            'content_length': content_length,
            'success': success
        }
        
        # Adiciona dados extras se fornecidos
        if data:
            log_data.update(data)
        
        level = LogLevel.ERROR if error else LogLevel.INFO
        message = f"Extração de conteúdo"
        if error:
            message += f" FALHOU: {str(error)}"
        elif success and content_length:
            message += f" OK ({content_length} chars via {method})"
        
        entry = StructuredLogEntry(
            level=level,
            category=LogCategory.CONTENT_EXTRACTION,
            message=message,
            session_id=session_id,
            component=component or "CONTENT_EXTRACTOR",
            operation=operation or "extract_content",
            data=log_data,
            error=error,
            duration_ms=duration_ms
        )
        
        self.log_structured(entry)
    
    def log_deduplication(self, session_id: str, operation: str,
                         items_processed: int = None, duplicates_found: int = None,
                         duplicate_rate: float = None, duration_ms: float = None):
        """✅ NOVO: Log específico para deduplicação"""
        
        data = {}
        if items_processed is not None:
            data['items_processed'] = items_processed
        if duplicates_found is not None:
            data['duplicates_found'] = duplicates_found
        if duplicate_rate is not None:
            data['duplicate_rate'] = duplicate_rate
        
        message = f"Deduplicação {operation}"
        if duplicates_found is not None:
            message += f" ({duplicates_found} duplicatas de {items_processed} itens)"
        
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            category=LogCategory.DEDUPLICATION,
            message=message,
            session_id=session_id,
            component="DEDUPLICATOR",
            operation=operation,
            data=data,
            duration_ms=duration_ms
        )
        
        self.log_structured(entry)
    
    def log_rule_engine(self, session_id: str, operation: str,
                       rule_triggered: str = None, item_id: str = None,
                       decision: str = None, confidence_adjustment: float = None,
                       llm_override: bool = None):
        """✅ NOVO: Log específico para rule engine"""
        
        data = {}
        if rule_triggered:
            data['rule_triggered'] = rule_triggered
        if item_id:
            data['item_id'] = item_id
        if decision:
            data['decision'] = decision
        if confidence_adjustment is not None:
            data['confidence_adjustment'] = confidence_adjustment
        if llm_override is not None:
            data['llm_override'] = llm_override
        
        message = f"Rule Engine {operation}"
        if decision:
            message += f" → {decision}"
        if rule_triggered:
            message += f" (regra: {rule_triggered})"
        
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            category=LogCategory.RULE_ENGINE,
            message=message,
            session_id=session_id,
            component="RULE_ENGINE",
            operation=operation,
            data=data
        )
        
        self.log_structured(entry)
    
    def log_performance_metric(self, session_id: str, metric_name: str,
                              value: Union[int, float], unit: str = None,
                              component: str = None, operation: str = None):
        """✅ NOVO: Log específico para métricas de performance"""
        
        data = {
            'metric_name': metric_name,
            'value': value,
            'unit': unit
        }
        
        message = f"Métrica {metric_name}: {value}"
        if unit:
            message += f" {unit}"
        
        entry = StructuredLogEntry(
            level=LogLevel.INFO,
            category=LogCategory.PERFORMANCE,
            message=message,
            session_id=session_id,
            component=component or "PERFORMANCE",
            operation=operation or "metric",
            data=data
        )
        
        self.log_structured(entry)
    
    def get_structured_logs(self, session_id: str, 
                           category: LogCategory = None,
                           level: LogLevel = None) -> List[Dict[str, Any]]:
        """✅ NOVO: Recupera logs estruturados com filtros"""
        try:
            json_filename = f"structured_log_{session_id}.jsonl"
            json_path = os.path.join(self.app_root, json_filename)
            
            if not os.path.exists(json_path):
                return []
            
            logs = []
            with open(json_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        
                        # Aplica filtros
                        if category and log_entry.get('category') != category.value:
                            continue
                        if level and log_entry.get('level') != level.value:
                            continue
                        
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
            
            return logs
            
        except Exception as e:
            print(f"❌ Erro ao recuperar logs estruturados: {e}")
            return []
    
    def cleanup_old_logs(self, days_old: int = 7):
        """
        ✅ NOVO: Remove logs antigos para economizar espaço
        
        Args:
            days_old: Remove logs mais antigos que N dias
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            removed_count = 0
            
            for filename in os.listdir(self.app_root):
                if filename.startswith(('log_', 'structured_log_')):
                    file_path = os.path.join(self.app_root, filename)
                    
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        removed_count += 1
            
            if removed_count > 0:
                print(f"🧹 {removed_count} logs antigos removidos (>{days_old} dias)")
            
        except Exception as e:
            print(f"❌ Erro na limpeza de logs: {e}")


# ✅ INSTÂNCIA GLOBAL PARA USO EM TODO O SISTEMA
log_local_atual = LogLocalAtual()

# --- FUNÇÕES ADICIONADAS PARA RESOLVER OS ERROS DE IMPORTAÇÃO ---
def get_log_local():
    """
    Retorna a instância global do logger LogLocalAtual.
    
    Esta função é necessária para resolver o erro de importação:
    "cannot import name 'get_log_local'"
    """
    return log_local_atual

def log_info(session_id: str, component: str, message: str, **kwargs):
    """
    Função de atalho para adicionar um log INFO.
    
    Args:
        session_id: ID da sessão.
        component: Componente que gerou o log.
        message: Mensagem do log.
        **kwargs: Argumentos adicionais para extra_data.
    """
    log_local_atual.add_log_entry(session_id, component, "INFO", message, **kwargs)

def log_warning(session_id: str, component: str, message: str, **kwargs):
    """
    Função de atalho para adicionar um log WARNING.
    
    Args:
        session_id: ID da sessão.
        component: Componente que gerou o log.
        message: Mensagem do log.
        **kwargs: Argumentos adicionais para extra_data.
    """
    log_local_atual.add_log_entry(session_id, component, "WARNING", message, **kwargs)

def log_error(session_id: str, component: str, message: str, **kwargs):
    """
    Função de atalho para adicionar um log ERROR.
    
    Args:
        session_id: ID da sessão.
        component: Componente que gerou o log.
        message: Mensagem do log.
        **kwargs: Argumentos adicionais para extra_data.
    """
    log_local_atual.add_log_entry(session_id, component, "ERROR", message, **kwargs)

def log_debug(session_id: str, component: str, message: str, **kwargs):
    """
    Função de atalho para adicionar um log DEBUG.
    
    Args:
        session_id: ID da sessão.
        component: Componente que gerou o log.
        message: Mensagem do log.
        **kwargs: Argumentos adicionais para extra_data.
    """
    log_local_atual.add_log_entry(session_id, component, "DEBUG", message, **kwargs)

def log_critical(session_id: str, component: str, message: str, **kwargs):
    """
    Função de atalho para adicionar um log CRITICAL.
    
    Args:
        session_id: ID da sessão.
        component: Componente que gerou o log.
        message: Mensagem do log.
        **kwargs: Argumentos adicionais para extra_data.
    """
    log_local_atual.add_log_entry(session_id, component, "CRITICAL", message, **kwargs)
