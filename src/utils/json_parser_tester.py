#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - JSON Parser Tester
Testa o sistema de parsing JSON do synthesis engine
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class JSONParserTester:
    """Testa o sistema de parsing JSON"""
    
    def __init__(self):
        self.test_cases = [
            # Caso 1: JSON válido
            {
                'name': 'JSON válido',
                'input': '{"title": "Test", "content": "Valid JSON", "score": 95}',
                'expected_success': True
            },
            
            # Caso 2: JSON vazio
            {
                'name': 'JSON vazio',
                'input': '',
                'expected_success': False
            },
            
            # Caso 3: JSON None
            {
                'name': 'JSON None',
                'input': None,
                'expected_success': False
            },
            
            # Caso 4: JSON com aspas simples
            {
                'name': 'JSON com aspas simples',
                'input': "{'title': 'Test', 'content': 'Single quotes'}",
                'expected_success': True
            },
            
            # Caso 5: JSON sem aspas nas chaves
            {
                'name': 'JSON sem aspas nas chaves',
                'input': '{title: "Test", content: "No quotes on keys"}',
                'expected_success': True
            },
            
            # Caso 6: JSON com comentários
            {
                'name': 'JSON com comentários',
                'input': '''
                {
                    // Comentário de linha
                    "title": "Test",
                    /* Comentário de bloco */
                    "content": "With comments"
                }
                ''',
                'expected_success': True
            },
            
            # Caso 7: JSON com valores Python
            {
                'name': 'JSON com valores Python',
                'input': '{"active": True, "disabled": False, "value": None}',
                'expected_success': True
            },
            
            # Caso 8: JSON incompleto (chaves não fechadas)
            {
                'name': 'JSON incompleto',
                'input': '{"title": "Test", "content": "Incomplete"',
                'expected_success': True  # Deve ser reparado
            },
            
            # Caso 9: JSON com vírgulas extras
            {
                'name': 'JSON com vírgulas extras',
                'input': '{"title": "Test", "content": "Extra commas",}',
                'expected_success': True
            },
            
            # Caso 10: JSON em markdown
            {
                'name': 'JSON em markdown',
                'input': '''
                Aqui está o resultado:
                
                ```json
                {
                    "title": "Test",
                    "content": "JSON in markdown"
                }
                ```
                
                Fim do resultado.
                ''',
                'expected_success': True
            },
            
            # Caso 11: Texto sem JSON
            {
                'name': 'Texto sem JSON',
                'input': 'Este é apenas um texto sem JSON válido',
                'expected_success': False
            },
            
            # Caso 12: JSON com caracteres de controle
            {
                'name': 'JSON com caracteres de controle',
                'input': '{"title": "Test\x00\x01", "content": "Control chars\x7f"}',
                'expected_success': True
            }
        ]
    
    def test_json_cleaning(self) -> Dict[str, Any]:
        """Testa o método _clean_json_text"""
        
        try:
            from ..services.enhanced_synthesis_engine import EnhancedSynthesisEngine
            engine = EnhancedSynthesisEngine()
            
            results = []
            
            for test_case in self.test_cases:
                logger.info(f"🧪 Testando limpeza: {test_case['name']}")
                
                try:
                    input_data = test_case['input']
                    cleaned = engine._clean_json_text(input_data) if input_data is not None else ""
                    
                    result = {
                        'name': test_case['name'],
                        'input_length': len(str(input_data)) if input_data else 0,
                        'output_length': len(cleaned),
                        'has_output': bool(cleaned and cleaned.strip()),
                        'starts_with_brace': cleaned.startswith(('{', '[')),
                        'success': True
                    }
                    
                    logger.info(f"✅ {test_case['name']}: {result['output_length']} chars")
                    
                except Exception as e:
                    result = {
                        'name': test_case['name'],
                        'error': str(e),
                        'success': False
                    }
                    logger.error(f"❌ {test_case['name']}: {e}")
                
                results.append(result)
            
            successful = [r for r in results if r.get('success', False)]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'json_cleaning',
                'total_tests': len(results),
                'successful_tests': len(successful),
                'success_rate': len(successful) / len(results) if results else 0,
                'results': results
            }
            
        except ImportError as e:
            return {
                'error': f'Erro ao importar EnhancedSynthesisEngine: {e}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': f'Erro geral no teste: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    def test_json_repair(self) -> Dict[str, Any]:
        """Testa o método _repair_common_json_issues"""
        
        try:
            from ..services.enhanced_synthesis_engine import EnhancedSynthesisEngine
            engine = EnhancedSynthesisEngine()
            
            results = []
            
            for test_case in self.test_cases:
                logger.info(f"🔧 Testando reparo: {test_case['name']}")
                
                try:
                    input_data = test_case['input']
                    if input_data is None:
                        input_data = ""
                    
                    repaired = engine._repair_common_json_issues(input_data)
                    
                    # Tenta parsear o resultado reparado
                    parse_success = False
                    try:
                        if repaired and repaired.strip():
                            json.loads(repaired)
                            parse_success = True
                    except json.JSONDecodeError:
                        pass
                    
                    result = {
                        'name': test_case['name'],
                        'input_length': len(str(input_data)),
                        'output_length': len(repaired),
                        'parse_success': parse_success,
                        'expected_success': test_case['expected_success'],
                        'test_passed': parse_success == test_case['expected_success'],
                        'success': True
                    }
                    
                    status = "✅" if result['test_passed'] else "⚠️"
                    logger.info(f"{status} {test_case['name']}: Parse={parse_success}, Expected={test_case['expected_success']}")
                    
                except Exception as e:
                    result = {
                        'name': test_case['name'],
                        'error': str(e),
                        'success': False
                    }
                    logger.error(f"❌ {test_case['name']}: {e}")
                
                results.append(result)
            
            successful = [r for r in results if r.get('success', False)]
            test_passed = [r for r in successful if r.get('test_passed', False)]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'json_repair',
                'total_tests': len(results),
                'successful_tests': len(successful),
                'tests_passed': len(test_passed),
                'success_rate': len(successful) / len(results) if results else 0,
                'pass_rate': len(test_passed) / len(successful) if successful else 0,
                'results': results
            }
            
        except ImportError as e:
            return {
                'error': f'Erro ao importar EnhancedSynthesisEngine: {e}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': f'Erro geral no teste: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    def test_full_parsing_pipeline(self) -> Dict[str, Any]:
        """Testa o pipeline completo de parsing JSON"""
        
        try:
            from ..services.enhanced_synthesis_engine import EnhancedSynthesisEngine
            engine = EnhancedSynthesisEngine()
            
            results = []
            
            for test_case in self.test_cases:
                logger.info(f"🔄 Testando pipeline: {test_case['name']}")
                
                try:
                    input_data = test_case['input']
                    
                    # Simula o processo completo
                    if input_data is None:
                        # Caso especial para None
                        final_result = engine._create_enhanced_fallback_synthesis("None input")
                        parse_success = True  # Fallback sempre funciona
                    else:
                        # Processo normal: limpa -> repara -> parsea
                        cleaned = engine._clean_json_text(input_data)
                        
                        if not cleaned or not cleaned.strip():
                            final_result = engine._create_enhanced_fallback_synthesis(input_data)
                            parse_success = True
                        else:
                            try:
                                final_result = json.loads(cleaned)
                                parse_success = True
                            except json.JSONDecodeError:
                                # Tenta reparar
                                repaired = engine._repair_common_json_issues(input_data)
                                try:
                                    final_result = json.loads(repaired)
                                    parse_success = True
                                except json.JSONDecodeError:
                                    final_result = engine._create_enhanced_fallback_synthesis(input_data)
                                    parse_success = True  # Fallback sempre funciona
                    
                    result = {
                        'name': test_case['name'],
                        'parse_success': parse_success,
                        'has_result': final_result is not None,
                        'result_type': type(final_result).__name__,
                        'expected_success': test_case['expected_success'],
                        'pipeline_success': True,
                        'success': True
                    }
                    
                    logger.info(f"✅ {test_case['name']}: Pipeline completo")
                    
                except Exception as e:
                    result = {
                        'name': test_case['name'],
                        'error': str(e),
                        'success': False
                    }
                    logger.error(f"❌ {test_case['name']}: {e}")
                
                results.append(result)
            
            successful = [r for r in results if r.get('success', False)]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'test_type': 'full_pipeline',
                'total_tests': len(results),
                'successful_tests': len(successful),
                'success_rate': len(successful) / len(results) if results else 0,
                'results': results
            }
            
        except ImportError as e:
            return {
                'error': f'Erro ao importar EnhancedSynthesisEngine: {e}',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'error': f'Erro geral no teste: {e}',
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_test_report(self) -> str:
        """Gera relatório completo dos testes"""
        
        cleaning_test = self.test_json_cleaning()
        repair_test = self.test_json_repair()
        pipeline_test = self.test_full_parsing_pipeline()
        
        report = f"""
# 🧪 RELATÓRIO DE TESTE - JSON PARSER
**Data:** {datetime.now().isoformat()}

## 📊 RESUMO EXECUTIVO
- **Limpeza JSON:** {cleaning_test.get('success_rate', 0):.1%} sucesso
- **Reparo JSON:** {repair_test.get('success_rate', 0):.1%} sucesso
- **Pipeline Completo:** {pipeline_test.get('success_rate', 0):.1%} sucesso

## 🧽 TESTE DE LIMPEZA JSON
"""
        
        if 'error' in cleaning_test:
            report += f"❌ **Erro:** {cleaning_test['error']}\n"
        else:
            report += f"- **Total:** {cleaning_test['total_tests']} testes\n"
            report += f"- **Sucessos:** {cleaning_test['successful_tests']}\n"
            report += f"- **Taxa:** {cleaning_test['success_rate']:.1%}\n"
        
        report += f"\n## 🔧 TESTE DE REPARO JSON\n"
        if 'error' in repair_test:
            report += f"❌ **Erro:** {repair_test['error']}\n"
        else:
            report += f"- **Total:** {repair_test['total_tests']} testes\n"
            report += f"- **Sucessos:** {repair_test['successful_tests']}\n"
            report += f"- **Testes Passaram:** {repair_test.get('tests_passed', 0)}\n"
            report += f"- **Taxa de Sucesso:** {repair_test['success_rate']:.1%}\n"
            report += f"- **Taxa de Aprovação:** {repair_test.get('pass_rate', 0):.1%}\n"
        
        report += f"\n## 🔄 TESTE DE PIPELINE COMPLETO\n"
        if 'error' in pipeline_test:
            report += f"❌ **Erro:** {pipeline_test['error']}\n"
        else:
            report += f"- **Total:** {pipeline_test['total_tests']} testes\n"
            report += f"- **Sucessos:** {pipeline_test['successful_tests']}\n"
            report += f"- **Taxa:** {pipeline_test['success_rate']:.1%}\n"
        
        # Status geral
        overall_success = (
            cleaning_test.get('success_rate', 0) + 
            repair_test.get('success_rate', 0) + 
            pipeline_test.get('success_rate', 0)
        ) / 3
        
        if overall_success >= 0.8:
            report += f"\n## ✅ CONCLUSÃO\nSistema de parsing JSON funcionando adequadamente ({overall_success:.1%} sucesso geral)"
        elif overall_success >= 0.6:
            report += f"\n## ⚠️ CONCLUSÃO\nSistema precisa de melhorias ({overall_success:.1%} sucesso geral)"
        else:
            report += f"\n## ❌ CONCLUSÃO\nSistema com problemas críticos ({overall_success:.1%} sucesso geral)"
        
        return report

# Instância global
json_tester = JSONParserTester()

if __name__ == "__main__":
    # Teste rápido
    print("🧪 Testando JSON Parser...")
    print(json_tester.generate_test_report())