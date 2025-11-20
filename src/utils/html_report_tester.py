#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - HTML Report Tester
Testa a geração de relatórios HTML modernos
"""

import os
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Adicionar path do projeto
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

logger = logging.getLogger(__name__)

class HTMLReportTester:
    """Testa a geração de relatórios HTML"""
    
    def __init__(self):
        self.test_session_id = "test_html_report_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_data = self._create_test_data()
    
    def _create_test_data(self) -> Dict[str, Any]:
        """Cria dados de teste para o relatório"""
        return {
            'titulo': 'Relatório de Teste - HTML Moderno',
            'sumario_executivo': """
# Sumário Executivo

Este é um relatório de teste para validar a geração de HTML moderno.

## Principais Descobertas
- Sistema de geração HTML funcional
- Templates modernos aplicados
- Navegação por sidebar implementada

## Recomendações
- Continuar desenvolvimento
- Implementar melhorias visuais
- Adicionar mais interatividade
            """,
            'modules': {
                'anti_objecao': {
                    'titulo': 'Sistema Anti-Objeção',
                    'conteudo': """
# Sistema Anti-Objeção

## Principais Objeções Identificadas
1. **Preço muito alto**
   - Resposta: Demonstrar ROI
   - Scripts preparados
   
2. **Não tenho tempo**
   - Resposta: Automatização
   - Processo simplificado

## Scripts de Resposta
- Script 1: Objeção de preço
- Script 2: Objeção de tempo
- Script 3: Objeção de confiança
                    """
                },
                'avatars': {
                    'titulo': 'Avatares de Cliente',
                    'conteudo': """
# Avatares de Cliente

## Avatar Principal: João Empreendedor
- **Idade:** 35-45 anos
- **Renda:** R$ 10.000+
- **Dores:** Falta de tempo, necessidade de crescimento
- **Sonhos:** Liberdade financeira, impacto social

## Avatar Secundário: Maria Executiva
- **Idade:** 30-40 anos
- **Renda:** R$ 15.000+
- **Dores:** Estresse, falta de reconhecimento
- **Sonhos:** Carreira sólida, equilíbrio vida-trabalho
                    """
                },
                'insights_mercado': {
                    'titulo': 'Insights de Mercado',
                    'conteudo': """
# Insights de Mercado

## Tendências Identificadas
1. **Crescimento do mercado digital**
   - 25% ao ano
   - Oportunidade de R$ 2 bilhões
   
2. **Demanda por automação**
   - 80% das empresas buscam
   - Economia de 40% em custos

## Oportunidades
- Nicho pouco explorado
- Concorrência limitada
- Alta demanda reprimida
                    """
                }
            }
        }
    
    def test_enhanced_html_generator(self) -> Dict[str, Any]:
        """Testa o EnhancedHTMLReportGenerator"""
        
        try:
            from services.enhanced_html_report_generator import EnhancedHTMLReportGenerator
            
            generator = EnhancedHTMLReportGenerator()
            logger.info("✅ EnhancedHTMLReportGenerator importado com sucesso")
            
            # Criar diretório de teste
            test_dir = Path(f"analyses_data/{self.test_session_id}")
            test_dir.mkdir(parents=True, exist_ok=True)
            
            # Gerar relatório HTML
            output_path = str(test_dir / "relatorio_teste_moderno.html")
            
            html_path = generator.generate_html_report(
                self.test_session_id,
                self.test_data,
                output_path
            )
            
            # Verificar se arquivo foi criado
            if Path(html_path).exists():
                file_size = Path(html_path).stat().st_size
                return {
                    'success': True,
                    'html_path': html_path,
                    'file_size': file_size,
                    'file_size_mb': file_size / (1024 * 1024),
                    'message': 'HTML moderno gerado com sucesso'
                }
            else:
                return {
                    'success': False,
                    'error': 'Arquivo HTML não foi criado'
                }
                
        except ImportError as e:
            return {
                'success': False,
                'error': f'Erro ao importar EnhancedHTMLReportGenerator: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro na geração HTML: {e}'
            }
    
    def test_comprehensive_report_generator(self) -> Dict[str, Any]:
        """Testa o ComprehensiveReportGeneratorV3"""
        
        try:
            from services.comprehensive_report_generator_v3 import ComprehensiveReportGeneratorV3
            
            generator = ComprehensiveReportGeneratorV3()
            logger.info("✅ ComprehensiveReportGeneratorV3 importado com sucesso")
            
            # Criar estrutura de teste
            test_dir = Path(f"analyses_data/{self.test_session_id}")
            modules_dir = test_dir / "modules"
            modules_dir.mkdir(parents=True, exist_ok=True)
            
            # Criar alguns módulos de teste
            for module_name, module_data in self.test_data['modules'].items():
                module_file = modules_dir / f"{module_name}.md"
                module_file.write_text(module_data['conteudo'], encoding='utf-8')
            
            # Gerar relatório
            result = generator.compile_final_markdown_report(self.test_session_id)
            
            return {
                'success': result.get('success', False),
                'markdown_path': result.get('markdown_path'),
                'html_path': result.get('html_path'),
                'html_modern_path': result.get('html_modern_path'),
                'statistics': result.get('statistics', {}),
                'message': 'Relatório compilado com sucesso' if result.get('success') else 'Falha na compilação'
            }
            
        except ImportError as e:
            return {
                'success': False,
                'error': f'Erro ao importar ComprehensiveReportGeneratorV3: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro na compilação: {e}'
            }
    
    def test_html_template_structure(self) -> Dict[str, Any]:
        """Testa a estrutura do template HTML"""
        
        try:
            from services.enhanced_html_report_generator import EnhancedHTMLReportGenerator
            
            generator = EnhancedHTMLReportGenerator()
            
            # Verificar se métodos essenciais existem
            methods_to_check = [
                'generate_html_report',
                '_generate_html_template',
                '_generate_sidebar_navigation',
                '_process_module_content'
            ]
            
            missing_methods = []
            for method in methods_to_check:
                if not hasattr(generator, method):
                    missing_methods.append(method)
            
            if missing_methods:
                return {
                    'success': False,
                    'error': f'Métodos ausentes: {missing_methods}'
                }
            
            # Verificar estrutura de módulos
            modules_count = len(generator.modules_order)
            modules_titles = len(generator.modules_titles)
            
            return {
                'success': True,
                'modules_count': modules_count,
                'modules_titles': modules_titles,
                'modules_match': modules_count == modules_titles,
                'message': 'Estrutura do template validada'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro na validação: {e}'
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes"""
        
        logger.info("🧪 Iniciando testes de geração HTML...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'test_session_id': self.test_session_id,
            'tests': {}
        }
        
        # Teste 1: Template Structure
        logger.info("🔍 Testando estrutura do template...")
        results['tests']['template_structure'] = self.test_html_template_structure()
        
        # Teste 2: Enhanced HTML Generator
        logger.info("🎨 Testando EnhancedHTMLReportGenerator...")
        results['tests']['enhanced_html'] = self.test_enhanced_html_generator()
        
        # Teste 3: Comprehensive Report Generator
        logger.info("📋 Testando ComprehensiveReportGeneratorV3...")
        results['tests']['comprehensive_report'] = self.test_comprehensive_report_generator()
        
        # Calcular estatísticas gerais
        total_tests = len(results['tests'])
        successful_tests = sum(1 for test in results['tests'].values() if test.get('success', False))
        
        results['summary'] = {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
            'overall_success': successful_tests == total_tests
        }
        
        return results
    
    def generate_test_report(self) -> str:
        """Gera relatório dos testes"""
        
        results = self.run_all_tests()
        
        report = f"""
# 🧪 RELATÓRIO DE TESTE - GERAÇÃO HTML
**Data:** {datetime.now().isoformat()}
**Sessão de Teste:** {self.test_session_id}

## 📊 RESUMO EXECUTIVO
- **Total de Testes:** {results['summary']['total_tests']}
- **Testes Bem-sucedidos:** {results['summary']['successful_tests']}
- **Taxa de Sucesso:** {results['summary']['success_rate']:.1%}
- **Status Geral:** {'✅ SUCESSO' if results['summary']['overall_success'] else '❌ FALHAS DETECTADAS'}

## 🔍 DETALHES DOS TESTES

### 1. Estrutura do Template
"""
        
        template_test = results['tests']['template_structure']
        if template_test['success']:
            report += f"""✅ **SUCESSO**
- Módulos configurados: {template_test.get('modules_count', 0)}
- Títulos configurados: {template_test.get('modules_titles', 0)}
- Estrutura consistente: {'Sim' if template_test.get('modules_match', False) else 'Não'}
"""
        else:
            report += f"❌ **FALHA:** {template_test.get('error', 'Erro desconhecido')}\n"
        
        report += "\n### 2. Enhanced HTML Generator\n"
        enhanced_test = results['tests']['enhanced_html']
        if enhanced_test['success']:
            report += f"""✅ **SUCESSO**
- Arquivo gerado: {enhanced_test.get('html_path', 'N/A')}
- Tamanho: {enhanced_test.get('file_size_mb', 0):.2f} MB
"""
        else:
            report += f"❌ **FALHA:** {enhanced_test.get('error', 'Erro desconhecido')}\n"
        
        report += "\n### 3. Comprehensive Report Generator\n"
        comprehensive_test = results['tests']['comprehensive_report']
        if comprehensive_test['success']:
            report += f"""✅ **SUCESSO**
- Markdown: {comprehensive_test.get('markdown_path', 'N/A')}
- HTML Simples: {comprehensive_test.get('html_path', 'N/A')}
- HTML Moderno: {comprehensive_test.get('html_modern_path', 'N/A')}
"""
        else:
            report += f"❌ **FALHA:** {comprehensive_test.get('error', 'Erro desconhecido')}\n"
        
        # Conclusão
        if results['summary']['overall_success']:
            report += "\n## ✅ CONCLUSÃO\nSistema de geração HTML funcionando corretamente!"
        else:
            report += "\n## ❌ CONCLUSÃO\nProblemas detectados no sistema de geração HTML. Verificar logs para detalhes."
        
        return report
    
    def cleanup_test_files(self):
        """Remove arquivos de teste"""
        try:
            test_dir = Path(f"analyses_data/{self.test_session_id}")
            if test_dir.exists():
                import shutil
                shutil.rmtree(test_dir)
                logger.info(f"🗑️ Arquivos de teste removidos: {test_dir}")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao limpar arquivos de teste: {e}")

# Instância global
html_tester = HTMLReportTester()

if __name__ == "__main__":
    # Teste rápido
    print("🧪 Testando Geração HTML...")
    print(html_tester.generate_test_report())
    
    # Limpar arquivos de teste
    html_tester.cleanup_test_files()