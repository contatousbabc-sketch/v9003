#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Credit Manager Compatibility Wrapper
Wrapper para manter compatibilidade com código existente
"""

import logging
from typing import Dict, Any, Optional, List
from utils.advanced_credit_manager import advanced_credit_manager

logger = logging.getLogger(__name__)

class APICreditManagerWrapper:
    """Wrapper para manter compatibilidade com APICreditManager antigo"""
    
    def __init__(self):
        self.manager = advanced_credit_manager
    
    def get_next_api_key(self, provider: str) -> Optional[str]:
        """Compatibilidade: retorna próxima chave de API"""
        api_key = self.manager.get_best_api_key(provider)
        return api_key.key if api_key else None
    
    def disable_api_key(self, provider: str, key: str, reason: str = ""):
        """Compatibilidade: desabilita chave de API"""
        self.manager.handle_api_error(provider, key, 403, reason)
    
    def record_success(self, provider: str, key: str):
        """Compatibilidade: registra sucesso"""
        self.manager.record_api_usage(provider, key, True)
    
    def record_failure(self, provider: str, key: str, error: str = ""):
        """Compatibilidade: registra falha"""
        self.manager.record_api_usage(provider, key, False, error_message=error)
    
    def get_api_status(self, provider: str) -> Dict[str, Any]:
        """Compatibilidade: retorna status da API"""
        return self.manager.get_provider_status(provider)

# Instância global para compatibilidade
api_credit_manager = APICreditManagerWrapper()

# Aliases para compatibilidade total
credit_manager = api_credit_manager
fallback_manager = api_credit_manager
