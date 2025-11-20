#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - LLM Provider Tester
Testa e diagnostica problemas com providers LLM
"""

import os
import logging
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMProviderTester:
    """Testa conectividade e funcionalidade dos providers LLM"""
    
    def __init__(self):
        self.providers = {
            'fireworks': {
                'base_url': 'https://api.fireworks.ai/inference/v1/chat/completions',
                'model': 'accounts/fireworks/models/gemma-3-27b-it',
                'env_keys': ['FIREWORKS_API_KEY', 'FIREWORKS_API_KEY_1', 'FIREWORKS_API_KEY_2']
            },
            'groq': {
                'base_url': 'https://api.groq.com/openai/v1/chat/completions',
                'model': 'qwen/qwen3-32b',
                'env_keys': ['GROQ_API_KEY', 'GROQ_API_KEY_1', 'GROQ_API_KEY_2']
            },
            'openai': {
                'base_url': 'https://api.openai.com/v1/chat/completions',
                'model': 'gpt-3.5-turbo',
                'env_keys': ['OPENAI_API_KEY', 'OPENAI_API_KEY_1', 'OPENAI_API_KEY_2']
            }
        }
        
        self.test_prompt = "Responda apenas 'OK' se você conseguir processar esta mensagem."
    
    def get_api_keys(self, provider: str) -> List[str]:
        """Obtém chaves API do ambiente"""
        keys = []
        if provider in self.providers:
            for env_key in self.providers[provider]['env_keys']:
                key = os.getenv(env_key)
                if key and key.strip():
                    keys.append(key.strip())
        return keys
    
    def test_api_key(self, provider: str, api_key: str) -> Dict[str, Any]:
        """Testa uma chave API específica"""
        
        if provider not in self.providers:
            return {
                'success': False,
                'error': f'Provider {provider} não suportado'
            }
        
        config = self.providers[provider]
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': config['model'],
            'messages': [{'role': 'user', 'content': self.test_prompt}],
            'max_tokens': 10,
            'temperature': 0.1
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                config['base_url'],
                json=payload,
                headers=headers,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                    
                    return {
                        'success': True,
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'content': content,
                        'model_used': config['model']
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'status_code': response.status_code,
                        'error': f'Erro ao parsear resposta: {e}',
                        'response_time': response_time
                    }
            else:
                error_msg = response.text[:200] if response.text else 'Sem mensagem de erro'
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': error_msg,
                    'response_time': response_time
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Timeout na requisição (30s)',
                'response_time': 30.0
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Erro de conexão'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro inesperado: {e}'
            }
    
    def test_provider(self, provider: str) -> Dict[str, Any]:
        """Testa todas as chaves de um provider"""
        
        keys = self.get_api_keys(provider)
        
        if not keys:
            return {
                'provider': provider,
                'success': False,
                'error': 'Nenhuma chave API encontrada',
                'keys_found': 0,
                'keys_tested': 0,
                'keys_working': 0
            }
        
        results = []
        working_keys = 0
        
        for i, key in enumerate(keys):
            logger.info(f"🧪 Testando {provider} chave #{i+1}...")
            
            # Mascara a chave para log
            masked_key = key[:8] + '...' + key[-4:] if len(key) > 12 else key[:4] + '...'
            
            result = self.test_api_key(provider, key)
            result['key_index'] = i + 1
            result['key_masked'] = masked_key
            
            if result['success']:
                working_keys += 1
                logger.info(f"✅ {provider} chave #{i+1}: OK ({result.get('response_time', 0):.2f}s)")
            else:
                status = result.get('status_code', 'N/A')
                error = result.get('error', 'Erro desconhecido')
                logger.warning(f"❌ {provider} chave #{i+1}: {status} - {error}")
            
            results.append(result)
            
            # Pequeno delay entre testes
            time.sleep(1)
        
        return {
            'provider': provider,
            'success': working_keys > 0,
            'keys_found': len(keys),
            'keys_tested': len(results),
            'keys_working': working_keys,
            'success_rate': working_keys / len(keys) if keys else 0,
            'results': results
        }
    
    def test_all_providers(self) -> Dict[str, Any]:
        """Testa todos os providers disponíveis"""
        
        logger.info("🚀 Iniciando teste de todos os providers LLM...")
        
        all_results = {}
        total_providers = 0
        working_providers = 0
        total_keys = 0
        working_keys = 0
        
        for provider in self.providers.keys():
            logger.info(f"🔍 Testando provider: {provider}")
            
            result = self.test_provider(provider)
            all_results[provider] = result
            
            total_providers += 1
            if result['success']:
                working_providers += 1
            
            total_keys += result['keys_found']
            working_keys += result['keys_working']
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_providers': total_providers,
                'working_providers': working_providers,
                'provider_success_rate': working_providers / total_providers if total_providers else 0,
                'total_keys': total_keys,
                'working_keys': working_keys,
                'key_success_rate': working_keys / total_keys if total_keys else 0
            },
            'providers': all_results
        }
    
    def diagnose_fireworks_issues(self) -> Dict[str, Any]:
        """Diagnóstico específico para problemas do Fireworks"""
        
        logger.info("🔥 Diagnosticando problemas específicos do Fireworks...")
        
        keys = self.get_api_keys('fireworks')
        
        if not keys:
            return {
                'diagnosis': 'no_keys',
                'message': 'Nenhuma chave Fireworks encontrada no ambiente',
                'recommendations': [
                    'Verificar se FIREWORKS_API_KEY está definida',
                    'Verificar se as chaves adicionais (FIREWORKS_API_KEY_1, etc.) estão definidas',
                    'Confirmar se as chaves são válidas no dashboard do Fireworks'
                ]
            }
        
        # Testa conectividade básica
        try:
            response = requests.get('https://api.fireworks.ai', timeout=20)
            api_reachable = True
        except:
            api_reachable = False
        
        # Testa cada chave
        key_results = []
        for i, key in enumerate(keys):
            result = self.test_api_key('fireworks', key)
            key_results.append({
                'index': i + 1,
                'success': result['success'],
                'status_code': result.get('status_code'),
                'error': result.get('error')
            })
        
        # Análise dos resultados
        forbidden_keys = sum(1 for r in key_results if r.get('status_code') == 403)
        working_keys = sum(1 for r in key_results if r['success'])
        
        if not api_reachable:
            diagnosis = 'connectivity_issue'
            message = 'Não foi possível conectar à API do Fireworks'
            recommendations = [
                'Verificar conexão com internet',
                'Verificar se o firewall não está bloqueando api.fireworks.ai',
                'Tentar novamente em alguns minutos'
            ]
        elif forbidden_keys == len(keys):
            diagnosis = 'all_keys_forbidden'
            message = 'Todas as chaves retornam erro 403 (Forbidden)'
            recommendations = [
                'Verificar se as chaves são válidas no dashboard do Fireworks',
                'Confirmar se a conta tem créditos disponíveis',
                'Verificar se o modelo especificado está disponível para sua conta',
                'Considerar gerar novas chaves API'
            ]
        elif forbidden_keys > 0:
            diagnosis = 'some_keys_forbidden'
            message = f'{forbidden_keys}/{len(keys)} chaves com erro 403'
            recommendations = [
                'Remover ou substituir chaves inválidas',
                'Verificar créditos das contas associadas às chaves',
                'Usar apenas as chaves que funcionam'
            ]
        elif working_keys == 0:
            diagnosis = 'all_keys_failed'
            message = 'Todas as chaves falharam por motivos diversos'
            recommendations = [
                'Verificar logs detalhados dos erros',
                'Confirmar se o modelo está disponível',
                'Verificar se há problemas temporários na API'
            ]
        else:
            diagnosis = 'partial_success'
            message = f'{working_keys}/{len(keys)} chaves funcionando'
            recommendations = [
                'Sistema funcionando parcialmente',
                'Considerar adicionar mais chaves válidas',
                'Monitorar chaves que falharam'
            ]
        
        return {
            'diagnosis': diagnosis,
            'message': message,
            'api_reachable': api_reachable,
            'total_keys': len(keys),
            'working_keys': working_keys,
            'forbidden_keys': forbidden_keys,
            'key_results': key_results,
            'recommendations': recommendations
        }
    
    def generate_health_report(self) -> str:
        """Gera relatório de saúde dos providers LLM"""
        
        test_results = self.test_all_providers()
        fireworks_diagnosis = self.diagnose_fireworks_issues()
        
        report = f"""
# 🧪 RELATÓRIO DE SAÚDE - PROVIDERS LLM
**Data:** {datetime.now().isoformat()}

## 📊 RESUMO EXECUTIVO
- **Providers Funcionando:** {test_results['summary']['working_providers']}/{test_results['summary']['total_providers']} ({test_results['summary']['provider_success_rate']:.1%})
- **Chaves Funcionando:** {test_results['summary']['working_keys']}/{test_results['summary']['total_keys']} ({test_results['summary']['key_success_rate']:.1%})

## 🔍 DETALHES POR PROVIDER
"""
        
        for provider, result in test_results['providers'].items():
            status = "✅" if result['success'] else "❌"
            report += f"\n### {status} {provider.upper()}\n"
            report += f"- **Status:** {'Funcionando' if result['success'] else 'Com problemas'}\n"
            report += f"- **Chaves:** {result['keys_working']}/{result['keys_found']} funcionando\n"
            
            if result.get('results'):
                for key_result in result['results']:
                    key_status = "✅" if key_result['success'] else "❌"
                    report += f"  - {key_status} Chave #{key_result['key_index']}: "
                    if key_result['success']:
                        report += f"OK ({key_result.get('response_time', 0):.2f}s)\n"
                    else:
                        report += f"{key_result.get('status_code', 'N/A')} - {key_result.get('error', 'Erro desconhecido')}\n"
        
        # Diagnóstico específico do Fireworks
        report += f"\n## 🔥 DIAGNÓSTICO FIREWORKS\n"
        report += f"**Diagnóstico:** {fireworks_diagnosis['message']}\n\n"
        report += f"**Recomendações:**\n"
        for rec in fireworks_diagnosis['recommendations']:
            report += f"- {rec}\n"
        
        # Conclusão geral
        overall_health = test_results['summary']['provider_success_rate']
        if overall_health >= 0.8:
            report += f"\n## ✅ CONCLUSÃO\nSistema LLM saudável ({overall_health:.1%} providers funcionando)"
        elif overall_health >= 0.5:
            report += f"\n## ⚠️ CONCLUSÃO\nSistema LLM com problemas ({overall_health:.1%} providers funcionando)"
        else:
            report += f"\n## ❌ CONCLUSÃO\nSistema LLM com problemas críticos ({overall_health:.1%} providers funcionando)"
        
        return report

# Instância global
llm_tester = LLMProviderTester()

if __name__ == "__main__":
    # Teste rápido
    print("🧪 Testando Providers LLM...")
    print(llm_tester.generate_health_report())