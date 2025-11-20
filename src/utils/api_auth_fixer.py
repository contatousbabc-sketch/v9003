#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - API Authentication Fixer
Script para identificar e corrigir problemas de autenticação de APIs
"""

import os
import sys
import logging
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.api_credit_manager import APICreditManager

logger = logging.getLogger(__name__)

class APIAuthenticationFixer:
    """Corretor automático de problemas de autenticação de APIs"""
    
    def __init__(self):
        self.credit_manager = APICreditManager()
        
    def diagnose_authentication_issues(self):
        """Diagnostica problemas de autenticação"""
        logger.info("🔍 Diagnosticando problemas de autenticação...")
        
        # Gera relatório de problemas de autenticação
        auth_report = self.credit_manager.get_authentication_issues_report()
        
        if auth_report['total_auth_issues'] == 0:
            logger.info("✅ Nenhum problema de autenticação detectado")
            return auth_report
            
        logger.error(f"❌ {auth_report['total_auth_issues']} APIs com problemas de autenticação:")
        
        for issue in auth_report['affected_apis']:
            logger.error(f"   🔒 {issue['api_key']}: {issue['error_message']}")
            
        return auth_report
    
    def fix_authentication_issues(self):
        """Corrige problemas de autenticação automaticamente"""
        logger.info("🔧 Iniciando correção automática de problemas de autenticação...")
        
        # Desabilita APIs problemáticas
        disabled_result = self.credit_manager.disable_problematic_apis()
        
        if disabled_result['disabled_count'] > 0:
            logger.warning(f"🚫 {disabled_result['disabled_count']} APIs desabilitadas automaticamente:")
            for api in disabled_result['disabled_apis']:
                logger.warning(f"   - {api}")
        else:
            logger.info("✅ Nenhuma API precisou ser desabilitada")
            
        return disabled_result
    
    def generate_env_recommendations(self):
        """Gera recomendações para o arquivo .env"""
        logger.info("📝 Gerando recomendações para arquivo .env...")
        
        auth_report = self.credit_manager.get_authentication_issues_report()
        
        if auth_report['total_auth_issues'] == 0:
            return []
            
        recommendations = []
        
        for issue in auth_report['affected_apis']:
            api_name = issue['api_name'].upper()
            key_id = issue['key_id']
            
            # Gera nome da variável de ambiente
            if key_id == '1' or key_id == 'main':
                env_var = f"{api_name}_API_KEY"
            else:
                env_var = f"{api_name}_API_KEY_{key_id}"
                
            recommendations.append({
                'env_var': env_var,
                'api_name': issue['api_name'],
                'key_id': key_id,
                'current_error': issue['error_message'],
                'suggestion': f"Verificar e atualizar {env_var} no arquivo .env"
            })
            
        return recommendations
    
    def run_full_diagnosis_and_fix(self):
        """Executa diagnóstico completo e correções"""
        logger.info("🚀 Iniciando diagnóstico e correção completa de APIs...")
        
        # 1. Diagnostica problemas
        auth_report = self.diagnose_authentication_issues()
        
        # 2. Corrige problemas automaticamente
        fix_result = self.fix_authentication_issues()
        
        # 3. Gera recomendações
        env_recommendations = self.generate_env_recommendations()
        
        # 4. Relatório final
        logger.info("📊 RELATÓRIO FINAL:")
        logger.info(f"   🔍 APIs com problemas de autenticação: {auth_report['total_auth_issues']}")
        logger.info(f"   🚫 APIs desabilitadas automaticamente: {fix_result['disabled_count']}")
        logger.info(f"   📝 Recomendações de .env: {len(env_recommendations)}")
        
        if env_recommendations:
            logger.info("📋 AÇÕES RECOMENDADAS:")
            for rec in env_recommendations:
                logger.info(f"   - {rec['suggestion']}")
                
        return {
            'auth_issues': auth_report,
            'disabled_apis': fix_result,
            'env_recommendations': env_recommendations
        }

def main():
    """Função principal"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )
    
    fixer = APIAuthenticationFixer()
    result = fixer.run_full_diagnosis_and_fix()
    
    return result

if __name__ == "__main__":
    main()