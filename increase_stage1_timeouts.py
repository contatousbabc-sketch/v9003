#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aumentar timeouts da Etapa 1
Dobra todos os timeouts relacionados à coleta de dados
"""

import os
import re
import glob
from pathlib import Path

def increase_timeouts_in_file(file_path: Path) -> int:
    """Aumenta timeouts em um arquivo específico"""
    changes_made = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Padrões para aumentar timeouts
        timeout_patterns = [
            # aiohttp timeouts
            (r'aiohttp\.ClientTimeout\(total=(\d+)\)', lambda m: f'aiohttp.ClientTimeout(total={int(m.group(1)) * 2})'),
            # timeout= parameters simples
            (r'timeout=(\d+)(?!\d)', lambda m: f'timeout={int(m.group(1)) * 2}'),
            # future.result timeouts
            (r'\.result\(timeout=(\d+)\)', lambda m: f'.result(timeout={int(m.group(1)) * 2})'),
        ]
        
        for pattern, replacement_func in timeout_patterns:
            matches = list(re.finditer(pattern, content))
            for match in reversed(matches):  # Reverse para não afetar posições
                old_value = int(match.group(1))
                # Só aumenta se for menor que 300 (5 minutos) para evitar timeouts excessivos
                if old_value < 300:
                    new_text = replacement_func(match)
                    content = content[:match.start()] + new_text + content[match.end():]
                    changes_made += 1
        
        # Salva apenas se houve mudanças
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {file_path.name}: {changes_made} timeouts aumentados")
        
        return changes_made
        
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return 0

def main():
    """Função principal"""
    print("🚀 Aumentando timeouts da Etapa 1...")
    
    # Diretórios para processar
    directories = [
        "src/services",
        "src/routes", 
        "src/utils"
    ]
    
    total_changes = 0
    files_processed = 0
    
    for directory in directories:
        if os.path.exists(directory):
            for py_file in glob.glob(f"{directory}/*.py"):
                file_path = Path(py_file)
                changes = increase_timeouts_in_file(file_path)
                total_changes += changes
                if changes > 0:
                    files_processed += 1
    
    print(f"\n📊 Resumo:")
    print(f"   Arquivos processados: {files_processed}")
    print(f"   Total de timeouts aumentados: {total_changes}")
    print(f"   Status: {'✅ Concluído' if total_changes > 0 else '⚠️ Nenhuma alteração necessária'}")

if __name__ == "__main__":
    main()