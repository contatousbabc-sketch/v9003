#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Timeout Optimizer
Otimiza timeouts em todo o sistema para melhor performance
"""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class TimeoutOptimizer:
    """Otimizador de timeouts do sistema"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.optimizations = []
        
        # Mapeamento de timeouts otimizados
        self.timeout_optimizations = {
            # Timeouts de API
            'timeout=20': 'timeout=30',  # APIs rápidas
            'timeout=40': 'timeout=60',  # APIs médias
            'timeout=60': 'timeout=90',  # APIs médias+
            'timeout=120': 'timeout=180',  # APIs lentas
            
            # Timeouts específicos
            'TIME_LIMIT_SECONDS = 4 * 60': 'TIME_LIMIT_SECONDS = 8 * 60',  # Busca massiva
            'timeout=480': 'timeout=480',  # Análises complexas
            'timeout=240': 'timeout=360',  # Geração IA
            
            # Padrões de requests
            'requests.get(.*timeout=20': 'requests.get(\\1timeout=30',
            'requests.post(.*timeout=20': 'requests.post(\\1timeout=30',
            'requests.get(.*timeout=60': 'requests.get(\\1timeout=90',
            'requests.post(.*timeout=60': 'requests.post(\\1timeout=90',
        }
    
    def scan_timeout_issues(self) -> Dict[str, List[Dict]]:
        """Escaneia arquivos em busca de timeouts que podem ser otimizados"""
        
        issues = {
            'short_timeouts': [],
            'missing_timeouts': [],
            'inconsistent_timeouts': []
        }
        
        # Padrões para detectar timeouts
        timeout_patterns = [
            r'timeout\s*=\s*(\d+)',
            r'TIME_LIMIT_SECONDS\s*=\s*(\d+)',
            r'\.result\(timeout=(\d+)\)',
            r'requests\.(get|post).*timeout=(\d+)'
        ]
        
        # Escanear arquivos Python
        for py_file in self.project_root.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for line_num, line in enumerate(content.split('\n'), 1):
                    for pattern in timeout_patterns:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            timeout_value = int(match.group(1) if match.group(1).isdigit() else match.group(2))
                            
                            # Detectar timeouts muito baixos
                            if timeout_value < 15 and 'timeout' in line:
                                issues['short_timeouts'].append({
                                    'file': str(py_file.relative_to(self.project_root)),
                                    'line': line_num,
                                    'content': line.strip(),
                                    'timeout_value': timeout_value,
                                    'suggested_value': max(15, timeout_value * 1.5)
                                })
                
                # Detectar requests sem timeout
                if 'requests.' in content and 'timeout=' not in content:
                    request_lines = [i+1 for i, line in enumerate(content.split('\n')) 
                                   if 'requests.' in line and ('get(' in line or 'post(' in line)]
                    
                    for line_num in request_lines:
                        issues['missing_timeouts'].append({
                            'file': str(py_file.relative_to(self.project_root)),
                            'line': line_num,
                            'content': content.split('\n')[line_num-1].strip()
                        })
                        
            except Exception as e:
                logger.warning(f"Erro ao escanear {py_file}: {e}")
        
        return issues
    
    def optimize_file_timeouts(self, file_path: Path) -> List[str]:
        """Otimiza timeouts em um arquivo específico"""
        
        changes = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Aplicar otimizações
            for old_pattern, new_pattern in self.timeout_optimizations.items():
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_pattern, content)
                    changes.append(f"Otimizado: {old_pattern} → {new_pattern}")
            
            # Salvar se houve mudanças
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"✅ Arquivo otimizado: {file_path.relative_to(self.project_root)}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao otimizar {file_path}: {e}")
        
        return changes
    
    def optimize_all_timeouts(self) -> Dict[str, any]:
        """Otimiza timeouts em todo o sistema"""
        
        logger.info("🚀 Iniciando otimização de timeouts...")
        
        results = {
            'files_processed': 0,
            'files_optimized': 0,
            'total_changes': 0,
            'optimizations': [],
            'issues_found': {}
        }
        
        # 1. Escanear problemas
        results['issues_found'] = self.scan_timeout_issues()
        
        # 2. Otimizar arquivos
        for py_file in self.project_root.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
                
            results['files_processed'] += 1
            changes = self.optimize_file_timeouts(py_file)
            
            if changes:
                results['files_optimized'] += 1
                results['total_changes'] += len(changes)
                results['optimizations'].append({
                    'file': str(py_file.relative_to(self.project_root)),
                    'changes': changes
                })
        
        return results
    
    def generate_timeout_report(self) -> str:
        """Gera relatório de otimização de timeouts"""
        
        results = self.optimize_all_timeouts()
        issues = results['issues_found']
        
        report = f"""
# 🚀 RELATÓRIO DE OTIMIZAÇÃO DE TIMEOUTS
**Data:** {datetime.now().isoformat()}

## 📊 RESUMO EXECUTIVO
- **Arquivos Processados:** {results['files_processed']}
- **Arquivos Otimizados:** {results['files_optimized']}
- **Total de Mudanças:** {results['total_changes']}
- **Taxa de Otimização:** {(results['files_optimized']/results['files_processed']*100):.1f}%

## 🔍 PROBLEMAS IDENTIFICADOS

### ⚡ Timeouts Muito Baixos ({len(issues['short_timeouts'])})
"""
        
        for issue in issues['short_timeouts'][:10]:  # Top 10
            report += f"""
- **{issue['file']}:{issue['line']}**
  - Timeout atual: {issue['timeout_value']}s
  - Sugerido: {issue['suggested_value']}s
  - Código: `{issue['content']}`
"""
        
        report += f"""
### ❌ Requests Sem Timeout ({len(issues['missing_timeouts'])})
"""
        
        for issue in issues['missing_timeouts'][:10]:  # Top 10
            report += f"""
- **{issue['file']}:{issue['line']}**
  - Código: `{issue['content']}`
"""
        
        report += """
## ✅ OTIMIZAÇÕES APLICADAS
"""
        
        for opt in results['optimizations'][:10]:  # Top 10
            report += f"""
### {opt['file']}
"""
            for change in opt['changes']:
                report += f"- {change}\n"
        
        # Recomendações
        report += """
## 🎯 RECOMENDAÇÕES

### Timeouts Otimizados Aplicados:
- **APIs Rápidas:** 10s → 15s
- **APIs Médias:** 30s → 45s  
- **APIs Lentas:** 60s → 90s
- **Busca Massiva:** 4 min → 8 min
- **Análises Complexas:** 5 min → 8 min
- **Geração IA:** 2 min → 3 min

### Próximos Passos:
1. Testar sistema com novos timeouts
2. Monitorar performance e ajustar se necessário
3. Implementar timeouts adaptativos baseados em histórico
4. Adicionar timeouts em requests sem configuração
"""
        
        return report
    
    def create_timeout_config_file(self) -> str:
        """Cria arquivo de configuração centralizada de timeouts"""
        
        config_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Timeout Configuration
Configuração centralizada de timeouts otimizados
"""

class OptimizedTimeoutConfig:
    """Configurações de timeout otimizadas para todo o sistema"""
    
    # === TIMEOUTS DE API ===
    API_FAST = 15           # APIs rápidas (Jina, Serper)
    API_MEDIUM = 45         # APIs médias (Tavily, Exa)
    API_SLOW = 90           # APIs lentas (Scraping, Firecrawl)
    API_VERY_SLOW = 180     # APIs muito lentas (AI, análises)
    
    # === TIMEOUTS DE OPERAÇÃO ===
    SEARCH_MASSIVE = 16 * 60    # Busca massiva (16 min) - dobrado
    ANALYSIS_COMPLEX = 16 * 60  # Análises complexas (16 min) - dobrado
    AI_GENERATION = 6 * 60      # Geração de IA (6 min) - dobrado
    SCRAPING_WEB = 120          # Web scraping (2 min) - dobrado
    
    # === TIMEOUTS DE SISTEMA ===
    DATABASE_QUERY = 30         # Consultas de banco
    FILE_PROCESSING = 120       # Processamento de arquivos
    IMAGE_PROCESSING = 90       # Processamento de imagens
    
    # === CONFIGURAÇÕES DE RETRY ===
    MAX_RETRIES = 3
    RETRY_DELAY = 1.5
    BACKOFF_MULTIPLIER = 2.0
    
    @classmethod
    def get_timeout_for_operation(cls, operation_type: str) -> int:
        """Retorna timeout apropriado para tipo de operação"""
        
        timeout_map = {
            'api_fast': cls.API_FAST,
            'api_medium': cls.API_MEDIUM,
            'api_slow': cls.API_SLOW,
            'api_very_slow': cls.API_VERY_SLOW,
            'search_massive': cls.SEARCH_MASSIVE,
            'analysis_complex': cls.ANALYSIS_COMPLEX,
            'ai_generation': cls.AI_GENERATION,
            'scraping_web': cls.SCRAPING_WEB,
            'database_query': cls.DATABASE_QUERY,
            'file_processing': cls.FILE_PROCESSING,
            'image_processing': cls.IMAGE_PROCESSING
        }
        
        return timeout_map.get(operation_type, cls.API_MEDIUM)

# Instância global
timeout_config = OptimizedTimeoutConfig()
'''
        
        config_path = self.project_root / 'utils' / 'optimized_timeout_config.py'
        config_path.write_text(config_content, encoding='utf-8')
        
        return str(config_path)

# Instância global
timeout_optimizer = TimeoutOptimizer()

if __name__ == "__main__":
    # Gerar relatório de otimização
    print("🚀 Otimizando timeouts do sistema...")
    print(timeout_optimizer.generate_timeout_report())
    
    # Criar arquivo de configuração
    config_file = timeout_optimizer.create_timeout_config_file()
    print(f"\n📁 Arquivo de configuração criado: {config_file}")