#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Instagram Bypass Tester
Testa e monitora a eficácia do sistema de bypass do Instagram
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
import json

from instagram_bypass import instagram_bypass

logger = logging.getLogger(__name__)

class InstagramBypassTester:
    """Testa diferentes estratégias de bypass do Instagram"""
    
    def __init__(self):
        self.test_urls = [
            "https://www.instagram.com/p/DDXnzJdSBlK/",
            "https://www.instagram.com/p/DLQ2yAwtVHG/",
            "https://www.instagram.com/reel/DBeY6OLuiSv/",
            "https://www.instagram.com/patchworkdesign.oficial/reel/DA_QH_lOiTx/?hl=en"
        ]
        
    def test_single_url(self, url: str) -> Dict[str, Any]:
        """Testa uma URL específica com todas as estratégias"""
        
        logger.info(f"🧪 Testando: {url}")
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'strategies': {},
            'success': False,
            'best_method': None,
            'extracted_data': None
        }
        
        # Estratégia 1: Requisição direta
        try:
            response = instagram_bypass.safe_request(url, max_retries=1)
            if response and response.status_code == 200:
                result['strategies']['direct'] = {
                    'success': True,
                    'status_code': response.status_code,
                    'content_length': len(response.text)
                }
                if not result['success']:
                    result['success'] = True
                    result['best_method'] = 'direct'
            else:
                result['strategies']['direct'] = {
                    'success': False,
                    'status_code': response.status_code if response else None,
                    'error': 'No response or non-200 status'
                }
        except Exception as e:
            result['strategies']['direct'] = {
                'success': False,
                'error': str(e)
            }
        
        # Estratégia 2: Embed
        try:
            embed_data = instagram_bypass.extract_from_embed(url)
            if embed_data:
                result['strategies']['embed'] = {
                    'success': True,
                    'data_fields': list(embed_data.keys()),
                    'data_quality': len(embed_data)
                }
                if not result['success']:
                    result['success'] = True
                    result['best_method'] = 'embed'
                    result['extracted_data'] = embed_data
            else:
                result['strategies']['embed'] = {
                    'success': False,
                    'error': 'No data extracted'
                }
        except Exception as e:
            result['strategies']['embed'] = {
                'success': False,
                'error': str(e)
            }
        
        # Estratégia 3: APIs externas
        try:
            api_data = instagram_bypass.try_external_apis(url)
            if api_data:
                result['strategies']['external_apis'] = {
                    'success': True,
                    'data_fields': list(api_data.keys()),
                    'provider': api_data.get('provider', 'unknown')
                }
                if not result['success']:
                    result['success'] = True
                    result['best_method'] = 'external_apis'
                    result['extracted_data'] = api_data
            else:
                result['strategies']['external_apis'] = {
                    'success': False,
                    'error': 'No data from external APIs'
                }
        except Exception as e:
            result['strategies']['external_apis'] = {
                'success': False,
                'error': str(e)
            }
        
        # Estratégia 4: Método abrangente
        try:
            comprehensive_data = instagram_bypass.comprehensive_extract(url)
            if comprehensive_data:
                result['strategies']['comprehensive'] = {
                    'success': True,
                    'data_fields': list(comprehensive_data.keys()),
                    'extraction_method': comprehensive_data.get('extraction_method', 'unknown')
                }
                if not result['success']:
                    result['success'] = True
                    result['best_method'] = 'comprehensive'
                    result['extracted_data'] = comprehensive_data
            else:
                result['strategies']['comprehensive'] = {
                    'success': False,
                    'error': 'Comprehensive extraction failed'
                }
        except Exception as e:
            result['strategies']['comprehensive'] = {
                'success': False,
                'error': str(e)
            }
        
        # Log resultado
        if result['success']:
            logger.info(f"✅ Sucesso com {url} usando método: {result['best_method']}")
        else:
            logger.warning(f"❌ Falha total para {url}")
        
        return result
    
    def test_all_urls(self) -> Dict[str, Any]:
        """Testa todas as URLs de exemplo"""
        
        logger.info("🧪 Iniciando teste abrangente do sistema de bypass Instagram")
        
        results = []
        for url in self.test_urls:
            result = self.test_single_url(url)
            results.append(result)
            
            # Pequeno delay entre testes
            import time
            time.sleep(2)
        
        # Análise dos resultados
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['success'])
        
        strategy_success = {
            'direct': sum(1 for r in results if r['strategies'].get('direct', {}).get('success', False)),
            'embed': sum(1 for r in results if r['strategies'].get('embed', {}).get('success', False)),
            'external_apis': sum(1 for r in results if r['strategies'].get('external_apis', {}).get('success', False)),
            'comprehensive': sum(1 for r in results if r['strategies'].get('comprehensive', {}).get('success', False))
        }
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'strategy_success_rates': {
                strategy: count / total_tests if total_tests > 0 else 0
                for strategy, count in strategy_success.items()
            },
            'best_strategy': max(strategy_success.items(), key=lambda x: x[1])[0] if strategy_success else None,
            'detailed_results': results,
            'recommendations': []
        }
        
        # Gerar recomendações
        if summary['success_rate'] == 0:
            summary['recommendations'].append("🚨 CRÍTICO: Nenhuma estratégia funcionou - Instagram pode ter bloqueado completamente")
            summary['recommendations'].append("🔄 Considerar usar proxies ou serviços de terceiros")
        elif summary['success_rate'] < 0.5:
            summary['recommendations'].append("⚠️ Taxa de sucesso baixa - melhorar estratégias de bypass")
            summary['recommendations'].append("🔧 Implementar mais métodos alternativos")
        else:
            summary['recommendations'].append("✅ Sistema funcionando adequadamente")
        
        if strategy_success['embed'] > strategy_success['direct']:
            summary['recommendations'].append("💡 URLs embed são mais eficazes - priorizar este método")
        
        if strategy_success['external_apis'] > 0:
            summary['recommendations'].append("🌐 APIs externas funcionando - manter como fallback")
        
        return summary
    
    def generate_report(self, save_to_file: bool = True) -> str:
        """Gera relatório completo dos testes"""
        
        test_results = self.test_all_urls()
        
        report = f"""
# 📊 RELATÓRIO DE TESTE - INSTAGRAM BYPASS SYSTEM
**Data:** {test_results['timestamp']}

## 📈 RESUMO EXECUTIVO
- **Total de testes:** {test_results['total_tests']}
- **Testes bem-sucedidos:** {test_results['successful_tests']}
- **Taxa de sucesso:** {test_results['success_rate']:.1%}
- **Melhor estratégia:** {test_results['best_strategy']}

## 🎯 EFICÁCIA POR ESTRATÉGIA
"""
        
        for strategy, rate in test_results['strategy_success_rates'].items():
            report += f"- **{strategy.title()}:** {rate:.1%}\n"
        
        report += "\n## 💡 RECOMENDAÇÕES\n"
        for rec in test_results['recommendations']:
            report += f"- {rec}\n"
        
        report += "\n## 📋 DETALHES DOS TESTES\n"
        for i, result in enumerate(test_results['detailed_results'], 1):
            status = "✅ SUCESSO" if result['success'] else "❌ FALHA"
            method = result['best_method'] or "N/A"
            report += f"\n### Teste {i}: {status}\n"
            report += f"- **URL:** {result['url']}\n"
            report += f"- **Método eficaz:** {method}\n"
            
            for strategy, data in result['strategies'].items():
                success_icon = "✅" if data.get('success', False) else "❌"
                report += f"  - {success_icon} {strategy}: {data.get('error', 'OK')}\n"
        
        if save_to_file:
            filename = f"instagram_bypass_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📄 Relatório salvo em: {filename}")
        
        return report

# Instância global
instagram_tester = InstagramBypassTester()

if __name__ == "__main__":
    # Teste rápido
    tester = InstagramBypassTester()
    report = tester.generate_report()
    print(report)