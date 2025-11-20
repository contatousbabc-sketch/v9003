#!/usr/bin/env python3
"""
ARQV18 - Gerenciador de Modelos Locais
Sistema para gerenciar, trocar e otimizar modelos GGUF
"""

import os
import sys
from pathlib import Path
import shutil
from datetime import datetime

def get_model_info(filepath):
    """Obtém informações básicas do modelo"""
    try:
        size = filepath.stat().st_size
        size_gb = size / (1024**3)
        modified = datetime.fromtimestamp(filepath.stat().st_mtime)
        
        return {
            'size_bytes': size,
            'size_gb': size_gb,
            'modified': modified,
            'exists': True
        }
    except:
        return {'exists': False}

def list_available_models():
    """Lista todos os modelos disponíveis"""
    model_dir = Path("model")
    
    if not model_dir.exists():
        print("❌ Diretório 'model' não encontrado!")
        return []
    
    models = []
    current_model = None
    
    # Verificar modelo ativo
    main_model = model_dir / "model.gguf"
    if main_model.exists():
        info = get_model_info(main_model)
        current_model = {
            'filename': 'model.gguf',
            'path': main_model,
            'info': info,
            'is_active': True
        }
    
    # Listar todos os modelos .gguf
    for model_file in model_dir.glob("*.gguf"):
        if model_file.name != "model.gguf":
            info = get_model_info(model_file)
            models.append({
                'filename': model_file.name,
                'path': model_file,
                'info': info,
                'is_active': False
            })
    
    return current_model, models

def switch_model(new_model_path, model_dir):
    """Troca o modelo ativo"""
    main_model = model_dir / "model.gguf"
    backup_dir = model_dir / "backup"
    backup_dir.mkdir(exist_ok=True)
    
    try:
        # Fazer backup do modelo atual se existir
        if main_model.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"model_backup_{timestamp}.gguf"
            backup_path = backup_dir / backup_name
            
            print(f"📦 Fazendo backup do modelo atual...")
            shutil.move(str(main_model), str(backup_path))
            print(f"✅ Backup salvo: {backup_name}")
        
        # Copiar novo modelo
        print(f"🔄 Ativando novo modelo...")
        shutil.copy2(str(new_model_path), str(main_model))
        print(f"✅ Modelo ativado: {new_model_path.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao trocar modelo: {e}")
        return False

def delete_model(model_path):
    """Remove um modelo"""
    try:
        model_path.unlink()
        print(f"✅ Modelo removido: {model_path.name}")
        return True
    except Exception as e:
        print(f"❌ Erro ao remover modelo: {e}")
        return False

def show_model_stats():
    """Mostra estatísticas dos modelos"""
    model_dir = Path("model")
    
    if not model_dir.exists():
        print("❌ Diretório 'model' não encontrado!")
        return
    
    models = list(model_dir.glob("*.gguf"))
    backup_dir = model_dir / "backup"
    backups = list(backup_dir.glob("*.gguf")) if backup_dir.exists() else []
    
    total_size = sum(m.stat().st_size for m in models)
    backup_size = sum(b.stat().st_size for b in backups)
    
    print(f"\n📊 ESTATÍSTICAS DOS MODELOS")
    print("=" * 40)
    print(f"📁 Modelos ativos: {len(models)}")
    print(f"📦 Backups: {len(backups)}")
    print(f"💾 Espaço usado: {total_size / (1024**3):.2f}GB")
    print(f"🗃️ Espaço backups: {backup_size / (1024**3):.2f}GB")
    print(f"📊 Total: {(total_size + backup_size) / (1024**3):.2f}GB")

def cleanup_backups():
    """Limpa backups antigos"""
    model_dir = Path("model")
    backup_dir = model_dir / "backup"
    
    if not backup_dir.exists():
        print("📦 Nenhum backup encontrado")
        return
    
    backups = list(backup_dir.glob("*.gguf"))
    
    if not backups:
        print("📦 Nenhum backup encontrado")
        return
    
    print(f"\n🗃️ BACKUPS ENCONTRADOS:")
    print("─" * 40)
    
    for i, backup in enumerate(backups, 1):
        info = get_model_info(backup)
        print(f"{i}. {backup.name}")
        print(f"   📊 {info['size_gb']:.2f}GB")
        print(f"   📅 {info['modified'].strftime('%d/%m/%Y %H:%M')}")
        print()
    
    choice = input("Deseja remover todos os backups? (s/N): ").strip().lower()
    
    if choice in ['s', 'sim', 'y', 'yes']:
        removed = 0
        for backup in backups:
            try:
                backup.unlink()
                removed += 1
            except:
                pass
        
        print(f"✅ {removed} backups removidos")
        
        # Remover diretório se vazio
        try:
            backup_dir.rmdir()
        except:
            pass
    else:
        print("❌ Limpeza cancelada")

def main():
    """Função principal"""
    
    print("🤖 ARQV18 - Gerenciador de Modelos Locais")
    print("=" * 50)
    
    while True:
        print("\n📋 OPÇÕES DISPONÍVEIS:")
        print("─" * 30)
        print("1. 📋 Listar modelos")
        print("2. 🔄 Trocar modelo ativo")
        print("3. 🗑️ Remover modelo")
        print("4. 📊 Estatísticas")
        print("5. 🧹 Limpar backups")
        print("6. 📥 Baixar novos modelos")
        print("0. 👋 Sair")
        print()
        
        choice = input("Escolha uma opção (0-6): ").strip()
        
        if choice == "0":
            print("👋 Saindo...")
            break
        
        elif choice == "1":
            current_model, models = list_available_models()
            
            print(f"\n📋 MODELOS DISPONÍVEIS:")
            print("=" * 50)
            
            if current_model:
                info = current_model['info']
                print(f"🟢 ATIVO: {current_model['filename']}")
                print(f"   📊 {info['size_gb']:.2f}GB")
                print(f"   📅 {info['modified'].strftime('%d/%m/%Y %H:%M')}")
                print()
            else:
                print("❌ Nenhum modelo ativo (model.gguf não encontrado)")
                print()
            
            if models:
                print("📁 OUTROS MODELOS:")
                print("─" * 30)
                for i, model in enumerate(models, 1):
                    info = model['info']
                    print(f"{i}. {model['filename']}")
                    print(f"   📊 {info['size_gb']:.2f}GB")
                    print(f"   📅 {info['modified'].strftime('%d/%m/%Y %H:%M')}")
                    print()
            else:
                print("📁 Nenhum outro modelo encontrado")
        
        elif choice == "2":
            current_model, models = list_available_models()
            
            if not models:
                print("❌ Nenhum modelo alternativo encontrado")
                continue
            
            print(f"\n🔄 TROCAR MODELO ATIVO:")
            print("─" * 30)
            
            for i, model in enumerate(models, 1):
                info = model['info']
                print(f"{i}. {model['filename']}")
                print(f"   📊 {info['size_gb']:.2f}GB")
                print()
            
            try:
                model_choice = int(input("Escolha o modelo (número): ")) - 1
                
                if 0 <= model_choice < len(models):
                    selected_model = models[model_choice]
                    
                    confirm = input(f"Confirma troca para '{selected_model['filename']}'? (s/N): ").strip().lower()
                    
                    if confirm in ['s', 'sim', 'y', 'yes']:
                        model_dir = Path("model")
                        if switch_model(selected_model['path'], model_dir):
                            print(f"🎉 Modelo trocado com sucesso!")
                            print(f"🔄 Reinicie o ARQV18 para usar o novo modelo")
                    else:
                        print("❌ Troca cancelada")
                else:
                    print("❌ Opção inválida")
            except ValueError:
                print("❌ Digite um número válido")
        
        elif choice == "3":
            current_model, models = list_available_models()
            
            if not models:
                print("❌ Nenhum modelo encontrado para remover")
                continue
            
            print(f"\n🗑️ REMOVER MODELO:")
            print("─" * 30)
            
            for i, model in enumerate(models, 1):
                info = model['info']
                print(f"{i}. {model['filename']}")
                print(f"   📊 {info['size_gb']:.2f}GB")
                print()
            
            try:
                model_choice = int(input("Escolha o modelo para remover (número): ")) - 1
                
                if 0 <= model_choice < len(models):
                    selected_model = models[model_choice]
                    
                    print(f"⚠️ ATENÇÃO: Esta ação não pode ser desfeita!")
                    confirm = input(f"Confirma remoção de '{selected_model['filename']}'? (s/N): ").strip().lower()
                    
                    if confirm in ['s', 'sim', 'y', 'yes']:
                        delete_model(selected_model['path'])
                    else:
                        print("❌ Remoção cancelada")
                else:
                    print("❌ Opção inválida")
            except ValueError:
                print("❌ Digite um número válido")
        
        elif choice == "4":
            show_model_stats()
        
        elif choice == "5":
            cleanup_backups()
        
        elif choice == "6":
            print(f"\n📥 Para baixar novos modelos, execute:")
            print(f"python download_model.py")
            print(f"\nOu use o script de download integrado")
        
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Gerenciador interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
