#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Logging Otimizado V2.0
Sistema centralizado de logging com níveis apropriados, formatação melhorada e rotação
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import threading

class EnhancedLoggingSystem:
    """Sistema de logging otimizado e centralizado"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.loggers = {}
        self.log_dir = Path(__file__).parent.parent.parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Configuração global de logging
        self._setup_root_logger()
        
    def _setup_root_logger(self):
        """Configura o logger raiz com formatação otimizada"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Limpar handlers existentes
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Formatter otimizado
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para console com cores
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        
        # Handler para arquivo principal com rotação
        main_log_file = self.log_dir / "arqv18_main.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Handler para erros críticos
        error_log_file = self.log_dir / "arqv18_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Adicionar handlers
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(error_handler)
        
    def get_logger(self, name: str, level: Optional[str] = None) -> logging.Logger:
        """Obtém um logger otimizado para um módulo específico"""
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        
        # Configurar nível se especificado
        if level:
            level_map = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
            }
            logger.setLevel(level_map.get(level.upper(), logging.INFO))
        
        self.loggers[name] = logger
        return logger
    
    def create_module_logger(self, module_name: str, log_file: Optional[str] = None) -> logging.Logger:
        """Cria um logger específico para um módulo com arquivo próprio"""
        logger = self.get_logger(module_name)
        
        if log_file:
            # Handler específico para o módulo
            module_log_file = self.log_dir / log_file
            module_handler = logging.handlers.RotatingFileHandler(
                module_log_file,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=2,
                encoding='utf-8'
            )
            module_handler.setLevel(logging.DEBUG)
            
            formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(funcName)-20s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            module_handler.setFormatter(formatter)
            
            logger.addHandler(module_handler)
        
        return logger
    
    def log_system_info(self):
        """Log de informações do sistema na inicialização"""
        logger = self.get_logger('system')
        logger.info("🚀 Sistema de Logging Otimizado V2.0 inicializado")
        logger.info(f"📁 Diretório de logs: {self.log_dir}")
        logger.info(f"🐍 Python: {sys.version}")
        logger.info(f"💻 Sistema: {os.name}")
        
    def set_debug_mode(self, enabled: bool = True):
        """Ativa/desativa modo debug globalmente"""
        level = logging.DEBUG if enabled else logging.INFO
        logging.getLogger().setLevel(level)
        
        logger = self.get_logger('system')
        if enabled:
            logger.info("🔍 Modo DEBUG ativado")
        else:
            logger.info("ℹ️ Modo DEBUG desativado")
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
        """Log otimizado para métricas de performance"""
        logger = self.get_logger('performance')
        
        if duration > 5.0:  # Operações lentas
            logger.warning(f"⚠️ Operação lenta: {operation} ({duration:.2f}s)")
        elif duration > 1.0:
            logger.info(f"⏱️ {operation}: {duration:.2f}s")
        else:
            logger.debug(f"✅ {operation}: {duration:.3f}s")
        
        if details:
            logger.debug(f"   Detalhes: {details}")
    
    def log_api_call(self, api_name: str, endpoint: str, status: str, duration: float):
        """Log específico para chamadas de API"""
        logger = self.get_logger('api_calls')
        
        if status == 'success':
            logger.info(f"✅ {api_name} | {endpoint} | {duration:.2f}s")
        elif status == 'error':
            logger.error(f"❌ {api_name} | {endpoint} | {duration:.2f}s")
        elif status == 'timeout':
            logger.warning(f"⏰ {api_name} | {endpoint} | TIMEOUT após {duration:.2f}s")
        else:
            logger.warning(f"⚠️ {api_name} | {endpoint} | {status} | {duration:.2f}s")

class ColoredFormatter(logging.Formatter):
    """Formatter com cores para console"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Aplicar cor baseada no nível
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formato com cor
        formatter = logging.Formatter(
            fmt=f'{color}%(asctime)s | %(levelname)-8s{reset} | %(name)-25s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        return formatter.format(record)

# Instância global do sistema de logging
logging_system = EnhancedLoggingSystem()

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Função de conveniência para obter um logger otimizado"""
    return logging_system.get_logger(name, level)

def setup_module_logging(module_name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Função de conveniência para configurar logging de um módulo"""
    return logging_system.create_module_logger(module_name, log_file)

def log_performance(operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
    """Função de conveniência para log de performance"""
    logging_system.log_performance(operation, duration, details)

def log_api_call(api_name: str, endpoint: str, status: str, duration: float):
    """Função de conveniência para log de API"""
    logging_system.log_api_call(api_name, endpoint, status, duration)

def set_debug_mode(enabled: bool = True):
    """Função de conveniência para ativar modo debug"""
    logging_system.set_debug_mode(enabled)

# Inicializar sistema na importação
logging_system.log_system_info()