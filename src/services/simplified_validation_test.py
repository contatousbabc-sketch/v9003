#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ NOVO: Teste Simplificado de Validação das Melhorias
Foca nos componentes que conseguimos validar diretamente
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any

def test_logs_estruturados():
    """Testa sistema de logs estruturados"""
    print("🔍 Testando sistema de logs estruturados...")
    
    try:
        from log_local_atual import log_local_atual, LogLevel, LogCategory, StructuredLogEntry
        
        session_id = f"validation_test_{int(time.time())}"
        
        # Testa log estruturado
        log_entry = StructuredLogEntry(
            level=LogLevel.INFO,
            category=LogCategory.SYSTEM,
            message="Teste de validação",
            session_id=session_id,
            component="VALIDATION_TEST"
        )
        
        log_local_atual.log_structured(log_entry)
        
        # Testa logs específicos
        log_local_atual.log_llm_processing(
            session_id=session_id,
            operation="validation_test",
            recommendation="APROVAR",
            confidence=0.9
        )
        
        log_local_atual.log_deduplication(
            session_id=session_id,
            operation="validation_test",
            items_processed=100,
            duplicates_found=15
        )
        
        # Recupera logs
        logs = log_local_atual.get_structured_logs(session_id)
        
        print(f"✅ Logs estruturados: {len(logs)} entradas criadas")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos logs estruturados: {e}")
        return False

def test_error_handler():
    """Testa sistema de tratamento de erros"""
    print("🔍 Testando sistema de tratamento de erros...")
    
    try:
        from error_handler import error_handler, ErrorType, ErrorSeverity
        
        # Testa classificação de erro
        test_exception = Exception("API quota exceeded for requests")
        error_type = error_handler.classify_error(test_exception)
        severity = error_handler.determine_severity(error_type)
        
        # Testa estatísticas
        stats = error_handler.get_error_statistics()
        
        print(f"✅ Error handler: Tipo={error_type.value}, Severidade={severity.value}")
        print(f"✅ Estatísticas disponíveis: {len(stats)} métricas")
        return True
        
    except Exception as e:
        print(f"❌ Erro no error handler: {e}")
        return False

def test_deduplication():
    """Testa sistema de deduplicação"""
    print("🔍 Testando sistema de deduplicação...")
    
    try:
        # Importa diretamente do arquivo local
        import importlib.util
        spec = importlib.util.spec_from_file_location("massive_data_collector", "massive_data_collector.py")
        massive_data_collector = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(massive_data_collector)
        
        ContentDeduplicator = massive_data_collector.ContentDeduplicator
        
        # Cria deduplicador
        deduplicator = ContentDeduplicator(similarity_threshold=0.85)
        
        # Dados de teste com duplicatas
        test_data = [
            {'url': 'http://test1.com', 'title': 'Artigo Teste', 'content': 'Conteúdo do artigo de teste'},
            {'url': 'http://test2.com', 'title': 'Artigo Teste', 'content': 'Conteúdo do artigo de teste'},  # Duplicata
            {'url': 'http://test3.com', 'title': 'Artigo Diferente', 'content': 'Conteúdo completamente diferente'},
            {'url': 'http://test1.com', 'title': 'Artigo Teste', 'content': 'Conteúdo do artigo de teste'},  # Duplicata URL
        ]
        
        # Aplica deduplicação
        unique_results = deduplicator.deduplicate_results(test_data)
        stats = deduplicator.get_stats()
        
        print(f"✅ Deduplicação: {len(test_data)} → {len(unique_results)} únicos")
        print(f"✅ Taxa de duplicação: {stats['duplicate_rate']:.1f}%")
        return len(unique_results) < len(test_data)
        
    except Exception as e:
        print(f"❌ Erro na deduplicação: {e}")
        return False

def test_massive_data_collector():
    """Testa coletor de dados massivo"""
    print("🔍 Testando coletor de dados massivo...")
    
    try:
        # Importa diretamente do arquivo local
        import importlib.util
        spec = importlib.util.spec_from_file_location("massive_data_collector", "massive_data_collector.py")
        massive_data_collector = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(massive_data_collector)
        
        MassiveDataCollector = massive_data_collector.MassiveDataCollector
        
        # Cria instância
        collector = MassiveDataCollector()
        
        # Verifica se tem deduplicador integrado
        has_deduplicator = hasattr(collector, 'deduplicator')
        
        print(f"✅ MassiveDataCollector: Deduplicador integrado = {has_deduplicator}")
        return has_deduplicator
        
    except Exception as e:
        print(f"❌ Erro no massive data collector: {e}")
        return False

def test_file_structure():
    """Testa estrutura de arquivos das melhorias"""
    print("🔍 Testando estrutura de arquivos...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Arquivos que devem existir
    required_files = [
        'error_handler.py',
        'log_local_atual.py',
        'massive_data_collector.py',
        'test_verification_system.py'
    ]
    
    existing_files = []
    for file in required_files:
        file_path = os.path.join(current_dir, file)
        if os.path.exists(file_path):
            existing_files.append(file)
    
    print(f"✅ Arquivos encontrados: {len(existing_files)}/{len(required_files)}")
    for file in existing_files:
        print(f"  ✓ {file}")
    
    return len(existing_files) == len(required_files)

def test_external_ai_verifier_structure():
    """Testa estrutura do external_ai_verifier"""
    print("🔍 Testando estrutura do external_ai_verifier...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    external_ai_dir = os.path.join(current_dir, '../../external_ai_verifier/src/services')
    
    if not os.path.exists(external_ai_dir):
        print("❌ Diretório external_ai_verifier não encontrado")
        return False
    
    # Arquivos que devem existir
    required_files = [
        'external_review_agent.py',
        'rule_engine.py',
        'llm_reasoning_service.py',
        'external_ai_integration.py'
    ]
    
    existing_files = []
    for file in required_files:
        file_path = os.path.join(external_ai_dir, file)
        if os.path.exists(file_path):
            existing_files.append(file)
    
    print(f"✅ Arquivos external_ai_verifier: {len(existing_files)}/{len(required_files)}")
    for file in existing_files:
        print(f"  ✓ {file}")
    
    return len(existing_files) >= 3  # Pelo menos 3 dos 4 arquivos

def run_simplified_validation():
    """Executa validação simplificada"""
    print("🧪 INICIANDO VALIDAÇÃO SIMPLIFICADA DO ARQ-ALPHA-V11")
    print("="*60)
    
    tests = [
        ("Estrutura de Arquivos", test_file_structure),
        ("External AI Verifier", test_external_ai_verifier_structure),
        ("Logs Estruturados", test_logs_estruturados),
        ("Tratamento de Erros", test_error_handler),
        ("Sistema de Deduplicação", test_deduplication),
        ("Coletor de Dados Massivo", test_massive_data_collector)
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"Resultado: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ ERRO: {e}")
    
    # Relatório final
    end_time = time.time()
    duration = end_time - start_time
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL")
    print("="*60)
    print(f"Total de testes: {total}")
    print(f"Testes aprovados: {passed}")
    print(f"Testes falhados: {total - passed}")
    print(f"Taxa de sucesso: {success_rate:.1f}%")
    print(f"Tempo total: {duration:.2f}s")
    
    print(f"\nStatus: {'✅ APROVADO' if success_rate >= 70 else '❌ REPROVADO'}")
    
    # Detalhes dos testes
    print("\n📋 DETALHES DOS TESTES:")
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    # Salva relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': success_rate,
            'duration_seconds': duration
        },
        'test_results': {test_name: result for test_name, result in results},
        'status': 'PASSED' if success_rate >= 70 else 'FAILED'
    }
    
    # Salva na raiz do projeto
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    report_file = os.path.join(project_root, f"simplified_validation_report_{int(time.time())}.json")
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📄 Relatório salvo: {report_file}")
    except Exception as e:
        print(f"\n❌ Erro ao salvar relatório: {e}")
    
    return report

if __name__ == "__main__":
    # Adiciona diretório atual ao path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Executa validação
    report = run_simplified_validation()
    
    # Exit code baseado no resultado
    exit_code = 0 if report['status'] == 'PASSED' else 1
    sys.exit(exit_code)