#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Serper Credit Monitor
Monitor específico para créditos da API Serper com alertas preventivos
"""

import os
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class SerperCreditMonitor:
    """Monitor específico para créditos da API Serper"""
    
    def __init__(self):
        self.serper_keys = self._load_serper_keys()
        self.credit_status = {}
        self.last_check = {}
        self.check_interval = 300  # 5 minutos
        
    def _load_serper_keys(self) -> List[str]:
        """Carrega todas as chaves Serper disponíveis"""
        keys = []
        
        # Chave principal
        main_key = os.getenv('SERPER_API_KEY')
        if main_key and main_key.strip():
            keys.append(main_key.strip())
        
        # Chaves adicionais (1-4)
        for i in range(1, 5):
            key = os.getenv(f'SERPER_API_KEY_{i}')
            if key and key.strip():
                keys.append(key.strip())
        
        logger.info(f"📊 Serper Monitor: {len(keys)} chaves carregadas")
        return keys
    
    async def check_single_key_credits(self, api_key: str) -> Dict[str, Any]:
        """Verifica créditos de uma chave específica"""
        try:
            # Serper não tem endpoint específico para créditos, então fazemos uma busca teste
            test_query = "test"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-API-KEY': api_key,
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'q': test_query,
                    'num': 1  # Mínimo possível para economizar créditos
                }
                
                start_time = datetime.now()
                
                async with session.post(
                    'https://google.serper.dev/search',
                    json=payload,
                    headers=headers,
                    timeout=20
                ) as response:
                    
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    if response.status == 200:
                        # Chave funcionando
                        return {
                            'key_masked': f"{api_key[:8]}...{api_key[-4:]}",
                            'status': 'active',
                            'credits_available': True,
                            'response_time': response_time,
                            'last_check': datetime.now().isoformat(),
                            'error': None
                        }
                    
                    elif response.status == 400:
                        error_text = await response.text()
                        if 'not enough credits' in error_text.lower():
                            return {
                                'key_masked': f"{api_key[:8]}...{api_key[-4:]}",
                                'status': 'no_credits',
                                'credits_available': False,
                                'response_time': response_time,
                                'last_check': datetime.now().isoformat(),
                                'error': 'Créditos esgotados'
                            }
                        else:
                            return {
                                'key_masked': f"{api_key[:8]}...{api_key[-4:]}",
                                'status': 'error',
                                'credits_available': False,
                                'response_time': response_time,
                                'last_check': datetime.now().isoformat(),
                                'error': f'Erro 400: {error_text}'
                            }
                    
                    elif response.status == 401:
                        return {
                            'key_masked': f"{api_key[:8]}...{api_key[-4:]}",
                            'status': 'invalid',
                            'credits_available': False,
                            'response_time': response_time,
                            'last_check': datetime.now().isoformat(),
                            'error': 'Chave inválida'
                        }
                    
                    else:
                        error_text = await response.text()
                        return {
                            'key_masked': f"{api_key[:8]}...{api_key[-4:]}",
                            'status': 'error',
                            'credits_available': False,
                            'response_time': response_time,
                            'last_check': datetime.now().isoformat(),
                            'error': f'HTTP {response.status}: {error_text}'
                        }
                        
        except asyncio.TimeoutError:
            return {
                'key_masked': f"{api_key[:8]}...{api_key[-4:]}",
                'status': 'timeout',
                'credits_available': False,
                'response_time': 10.0,
                'last_check': datetime.now().isoformat(),
                'error': 'Timeout na verificação'
            }
        except Exception as e:
            return {
                'key_masked': f"{api_key[:8]}...{api_key[-4:]}",
                'status': 'error',
                'credits_available': False,
                'response_time': 0,
                'last_check': datetime.now().isoformat(),
                'error': str(e)
            }
    
    async def check_all_keys(self) -> Dict[str, Any]:
        """Verifica todas as chaves Serper"""
        results = []
        
        logger.info("🔍 Verificando créditos de todas as chaves Serper...")
        
        for i, api_key in enumerate(self.serper_keys):
            logger.info(f"   Verificando chave {i+1}/{len(self.serper_keys)}...")
            result = await self.check_single_key_credits(api_key)
            results.append(result)
            
            # Pequeno delay entre verificações
            await asyncio.sleep(1)
        
        # Análise dos resultados
        active_keys = [r for r in results if r['credits_available']]
        exhausted_keys = [r for r in results if r['status'] == 'no_credits']
        invalid_keys = [r for r in results if r['status'] == 'invalid']
        error_keys = [r for r in results if r['status'] == 'error']
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_keys': len(self.serper_keys),
            'active_keys': len(active_keys),
            'exhausted_keys': len(exhausted_keys),
            'invalid_keys': len(invalid_keys),
            'error_keys': len(error_keys),
            'keys_detail': results,
            'recommendations': []
        }
        
        # Gerar recomendações
        if len(active_keys) == 0:
            summary['recommendations'].append("🚨 CRÍTICO: Nenhuma chave Serper com créditos disponíveis!")
            summary['recommendations'].append("💳 Recarregar créditos ou adicionar novas chaves")
        elif len(active_keys) <= 1:
            summary['recommendations'].append("⚠️ ATENÇÃO: Apenas 1 chave Serper ativa")
            summary['recommendations'].append("🔄 Considerar recarregar outras chaves para redundância")
        
        if len(exhausted_keys) > 0:
            summary['recommendations'].append(f"💸 {len(exhausted_keys)} chave(s) sem créditos - recarregar")
        
        if len(invalid_keys) > 0:
            summary['recommendations'].append(f"🔑 {len(invalid_keys)} chave(s) inválida(s) - verificar configuração")
        
        return summary
    
    def should_check_now(self) -> bool:
        """Verifica se é hora de fazer nova verificação"""
        last_check = self.last_check.get('all_keys')
        if not last_check:
            return True
        
        time_since_check = (datetime.now() - last_check).total_seconds()
        return time_since_check >= self.check_interval
    
    async def get_status_report(self, force_check: bool = False) -> Dict[str, Any]:
        """Retorna relatório de status das chaves Serper"""
        if force_check or self.should_check_now():
            logger.info("🔄 Atualizando status das chaves Serper...")
            self.credit_status = await self.check_all_keys()
            self.last_check['all_keys'] = datetime.now()
        
        return self.credit_status
    
    def get_available_keys(self) -> List[str]:
        """Retorna lista de chaves com créditos disponíveis"""
        if not self.credit_status:
            return self.serper_keys  # Se não verificou ainda, assume todas disponíveis
        
        available = []
        for i, key_status in enumerate(self.credit_status.get('keys_detail', [])):
            if key_status.get('credits_available', False):
                available.append(self.serper_keys[i])
        
        return available
    
    def log_status_summary(self):
        """Loga resumo do status atual"""
        if not self.credit_status:
            logger.info("📊 Serper Status: Não verificado ainda")
            return
        
        status = self.credit_status
        logger.info(f"📊 Serper Status: {status['active_keys']}/{status['total_keys']} chaves ativas")
        
        if status['exhausted_keys'] > 0:
            logger.warning(f"💸 {status['exhausted_keys']} chave(s) sem créditos")
        
        if status['invalid_keys'] > 0:
            logger.error(f"🔑 {status['invalid_keys']} chave(s) inválida(s)")
        
        for rec in status.get('recommendations', []):
            logger.info(f"💡 {rec}")

# Instância global
serper_credit_monitor = SerperCreditMonitor()