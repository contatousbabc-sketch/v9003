#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração de Logging Centralizada
Facilita a configuração do sistema de logging em todo o projeto
"""

from enhanced_logging_system import (
    get_logger, 
    setup_module_logging, 
    log_performance, 
    log_api_call, 
    set_debug_mode,
    logging_system
)

def setup_project_logging(debug_mode: bool = False):
    """Configura o logging para todo o projeto"""
    
    # Configurar modo debug se solicitado
    if debug_mode:
        set_debug_mode(True)
    
    # Configurar loggers específicos para módulos principais
    api_logger = setup_module_logging('api_rotation_manager', 'api_rotation.log')
    cpl_logger = setup_module_logging('cpl_integration', 'cpl_integration.log')
    metadata_logger = setup_module_logging('image_metadata', 'image_metadata.log')
    
    # Log de inicialização
    system_logger = get_logger('project_setup')
    system_logger.info("🚀 Sistema de logging do projeto configurado")
    system_logger.info(f"🔍 Modo debug: {'ATIVADO' if debug_mode else 'DESATIVADO'}")
    
    return {
        'api': api_logger,
        'cpl': cpl_logger,
        'metadata': metadata_logger,
        'system': system_logger
    }

def get_project_logger(module_name: str):
    """Obtém um logger otimizado para um módulo do projeto"""
    return get_logger(f'arqv18.{module_name}')

# Configuração padrão para importação rápida
def quick_setup():
    """Configuração rápida de logging"""
    return setup_project_logging(debug_mode=False)

# Exportar funções principais
__all__ = [
    'get_logger',
    'setup_module_logging',
    'log_performance',
    'log_api_call',
    'set_debug_mode',
    'setup_project_logging',
    'get_project_logger',
    'quick_setup'
]