#!/usr/bin/env python3
"""
ARQV18 - Otimizador de Modelos
Sistema para otimizar configurações baseado no modelo ativo
"""

import os
import json
from pathlib import Path
import psutil

def detect_system_specs():
    """Detecta especificações do sistema"""
    try:
        # RAM total
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        # CPU cores
        cpu_cores = psutil.cpu_count()
        
        # Verificar GPU (básico)
        gpu_available = False
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            gpu_available = len(gpus) > 0
        except:
            pass
        
        return {
            'ram_gb': ram_gb,
            'cpu_cores': cpu_cores,
            'gpu_available': gpu_available
        }
    except:
        return {
            'ram_gb': 8.0,  # Padrão
            'cpu_cores': 4,
            'gpu_available': False
        }

def get_model_size():
    """Obtém tamanho do modelo ativo"""
    model_path = Path("model/model.gguf")
    
    if not model_path.exists():
        return None
    
    try:
        size_gb = model_path.stat().st_size / (1024**3)
        return size_gb
    except:
        return None

def recommend_settings(model_size_gb, system_specs):
    """Recomenda configurações otimizadas"""
    ram_gb = system_specs['ram_gb']
    cpu_cores = system_specs['cpu_cores']
    gpu_available = system_specs['gpu_available']
    
    settings = {}
    
    # Configurações baseadas no tamanho do modelo
    if model_size_gb <= 1.0:  # Modelos pequenos (< 1GB)
        settings.update({
            'max_tokens': 4096,
            'context_length': 4096,
            'batch_size': 512,
            'threads': min(cpu_cores, 8),
            'gpu_layers': 35 if gpu_available else 0,
            'memory_map': True,
            'use_mlock': ram_gb >= 8,
            'low_vram': False
        })
    
    elif model_size_gb <= 2.5:  # Modelos médios (1-2.5GB)
        settings.update({
            'max_tokens': 4096,
            'context_length': 4096,
            'batch_size': 256,
            'threads': min(cpu_cores, 6),
            'gpu_layers': 30 if gpu_available else 0,
            'memory_map': True,
            'use_mlock': ram_gb >= 12,
            'low_vram': ram_gb < 8
        })
    
    elif model_size_gb <= 5.0:  # Modelos grandes (2.5-5GB)
        settings.update({
            'max_tokens': 4096,
            'context_length': 4096,
            'batch_size': 128,
            'threads': min(cpu_cores, 4),
            'gpu_layers': 25 if gpu_available and ram_gb >= 8 else 0,
            'memory_map': True,
            'use_mlock': ram_gb >= 16,
            'low_vram': ram_gb < 12
        })
    
    else:  # Modelos muito grandes (> 5GB)
        settings.update({
            'max_tokens': 4096,
            'context_length': 2048,
            'batch_size': 64,
            'threads': min(cpu_cores, 4),
            'gpu_layers': 20 if gpu_available and ram_gb >= 16 else 0,
            'memory_map': True,
            'use_mlock': ram_gb >= 24,
            'low_vram': ram_gb < 16
        })
    
    # Ajustes baseados na RAM disponível
    if ram_gb < 8:
        settings.update({
            'max_tokens': min(settings['max_tokens'], 2048),
            'context_length': min(settings['context_length'], 2048),
            'batch_size': min(settings['batch_size'], 64),
            'gpu_layers': 0,
            'low_vram': True
        })
    
    return settings

def update_local_model_config(settings):
    """Atualiza configuração do modelo local"""
    config_files = [
        "src/services/local_model_manager.py",
        "src/config/model_config.py"
    ]
    
    updated_files = []
    
    for config_file in config_files:
        config_path = Path(config_file)
        
        if config_path.exists():
            try:
                # Ler arquivo
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Atualizar configurações
                if 'max_tokens' in content:
                    content = content.replace(
                        'max_tokens=1024',
                        f'max_tokens={settings["max_tokens"]}'
                    )
                    content = content.replace(
                        'max_tokens=2048',
                        f'max_tokens={settings["max_tokens"]}'
                    )
                
                if 'n_ctx' in content:
                    content = content.replace(
                        'n_ctx=2048',
                        f'n_ctx={settings["context_length"]}'
                    )
                    content = content.replace(
                        'n_ctx=4096',
                        f'n_ctx={settings["context_length"]}'
                    )
                
                if 'n_batch' in content:
                    content = content.replace(
                        'n_batch=512',
                        f'n_batch={settings["batch_size"]}'
                    )
                
                if 'n_threads' in content:
                    content = content.replace(
                        'n_threads=4',
                        f'n_threads={settings["threads"]}'
                    )
                
                if 'n_gpu_layers' in content:
                    content = content.replace(
                        'n_gpu_layers=0',
                        f'n_gpu_layers={settings["gpu_layers"]}'
                    )
                
                # Salvar arquivo
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                updated_files.append(config_file)
                
            except Exception as e:
                print(f"⚠️ Erro ao atualizar {config_file}: {e}")
    
    return updated_files

def create_optimization_report(model_size_gb, system_specs, settings):
    """Cria relatório de otimização"""
    report = f"""
🤖 RELATÓRIO DE OTIMIZAÇÃO ARQV18
{'=' * 50}

📊 SISTEMA DETECTADO:
• RAM: {system_specs['ram_gb']:.1f}GB
• CPU Cores: {system_specs['cpu_cores']}
• GPU: {'Disponível' if system_specs['gpu_available'] else 'Não detectada'}

📁 MODELO ATIVO:
• Tamanho: {model_size_gb:.2f}GB
• Categoria: {'Pequeno' if model_size_gb <= 1 else 'Médio' if model_size_gb <= 2.5 else 'Grande' if model_size_gb <= 5 else 'Muito Grande'}

⚙️ CONFIGURAÇÕES OTIMIZADAS:
• Max Tokens: {settings['max_tokens']}
• Context Length: {settings['context_length']}
• Batch Size: {settings['batch_size']}
• CPU Threads: {settings['threads']}
• GPU Layers: {settings['gpu_layers']}
• Memory Map: {'Sim' if settings['memory_map'] else 'Não'}
• Use MLock: {'Sim' if settings['use_mlock'] else 'Não'}
• Low VRAM Mode: {'Sim' if settings['low_vram'] else 'Não'}

💡 RECOMENDAÇÕES:
"""
    
    # Adicionar recomendações específicas
    if system_specs['ram_gb'] < 8:
        report += "• ⚠️ RAM limitada - considere usar modelos menores\n"
    
    if not system_specs['gpu_available']:
        report += "• 🔧 GPU não detectada - usando apenas CPU\n"
    
    if model_size_gb > system_specs['ram_gb'] * 0.5:
        report += "• 📊 Modelo grande para sua RAM - pode haver lentidão\n"
    
    if settings['gpu_layers'] > 0:
        report += "• 🚀 GPU configurada - performance otimizada\n"
    
    report += f"\n📅 Relatório gerado em: {Path().cwd()}/optimization_report.txt"
    
    return report

def main():
    """Função principal"""
    
    print("🤖 ARQV18 - Otimizador de Modelos")
    print("=" * 50)
    
    # Detectar especificações do sistema
    print("🔍 Detectando especificações do sistema...")
    system_specs = detect_system_specs()
    
    print(f"✅ Sistema detectado:")
    print(f"   💾 RAM: {system_specs['ram_gb']:.1f}GB")
    print(f"   🖥️ CPU: {system_specs['cpu_cores']} cores")
    print(f"   🎮 GPU: {'Disponível' if system_specs['gpu_available'] else 'Não detectada'}")
    
    # Verificar modelo ativo
    print(f"\n🔍 Verificando modelo ativo...")
    model_size = get_model_size()
    
    if model_size is None:
        print("❌ Nenhum modelo ativo encontrado (src/model/model.gguf)")
        print("💡 Execute 'python download_model.py' para baixar um modelo")
        return
    
    print(f"✅ Modelo encontrado: {model_size:.2f}GB")
    
    # Gerar recomendações
    print(f"\n⚙️ Gerando configurações otimizadas...")
    settings = recommend_settings(model_size, system_specs)
    
    # Mostrar configurações
    print(f"\n📋 CONFIGURAÇÕES RECOMENDADAS:")
    print("─" * 40)
    print(f"🎯 Max Tokens: {settings['max_tokens']}")
    print(f"📝 Context Length: {settings['context_length']}")
    print(f"📦 Batch Size: {settings['batch_size']}")
    print(f"🧵 CPU Threads: {settings['threads']}")
    print(f"🎮 GPU Layers: {settings['gpu_layers']}")
    print(f"💾 Memory Map: {'Sim' if settings['memory_map'] else 'Não'}")
    print(f"🔒 Use MLock: {'Sim' if settings['use_mlock'] else 'Não'}")
    print(f"⚡ Low VRAM: {'Sim' if settings['low_vram'] else 'Não'}")
    
    # Perguntar se quer aplicar
    print(f"\n❓ Deseja aplicar essas configurações?")
    confirm = input("(s/N): ").strip().lower()
    
    if confirm in ['s', 'sim', 'y', 'yes']:
        print(f"\n🔧 Aplicando configurações...")
        
        updated_files = update_local_model_config(settings)
        
        if updated_files:
            print(f"✅ Configurações aplicadas em:")
            for file in updated_files:
                print(f"   • {file}")
        else:
            print(f"⚠️ Nenhum arquivo de configuração encontrado")
        
        # Gerar relatório
        report = create_optimization_report(model_size, system_specs, settings)
        
        try:
            with open("optimization_report.txt", "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Relatório salvo: optimization_report.txt")
        except:
            pass
        
        print(f"\n🎉 OTIMIZAÇÃO CONCLUÍDA!")
        print(f"🔄 Reinicie o ARQV18 para aplicar as mudanças")
        
    else:
        print(f"❌ Otimização cancelada")
    
    # Mostrar relatório na tela
    print(f"\n📊 RELATÓRIO COMPLETO:")
    report = create_optimization_report(model_size, system_specs, settings)
    print(report)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Otimização interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
