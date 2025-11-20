#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Verificação de Integridade de Arquivos
Detecta e corrige arquivos corrompidos ou problemáticos
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import magic
import chardet

logger = logging.getLogger(__name__)

class FileIntegrityChecker:
    """Sistema de verificação de integridade de arquivos"""
    
    def __init__(self, data_dir: str = "analyses_data"):
        self.data_dir = data_dir
        self.integrity_log = os.path.join(data_dir, "integrity_log.json")
        self.quarantine_dir = os.path.join(data_dir, "quarantine")
        
        # Criar diretórios necessários
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(self.quarantine_dir, exist_ok=True)
        
        # Configurações
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.supported_encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        logger.info("🔍 Sistema de Verificação de Integridade inicializado")
    
    def check_directory_integrity(self, directory: str) -> Dict[str, Any]:
        """Verifica integridade de todos os arquivos em um diretório"""
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "directory": directory,
            "total_files": 0,
            "healthy_files": 0,
            "corrupted_files": 0,
            "suspicious_files": 0,
            "issues": [],
            "recommendations": []
        }
        
        if not os.path.exists(directory):
            results["issues"].append(f"Diretório não encontrado: {directory}")
            return results
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    results["total_files"] += 1
                    
                    # Verificar arquivo individual
                    file_result = self.check_file_integrity(file_path)
                    
                    if file_result["status"] == "healthy":
                        results["healthy_files"] += 1
                    elif file_result["status"] == "corrupted":
                        results["corrupted_files"] += 1
                        results["issues"].append({
                            "file": file_path,
                            "type": "corruption",
                            "details": file_result["issues"]
                        })
                    elif file_result["status"] == "suspicious":
                        results["suspicious_files"] += 1
                        results["issues"].append({
                            "file": file_path,
                            "type": "suspicious",
                            "details": file_result["issues"]
                        })
            
            # Gerar recomendações
            results["recommendations"] = self._generate_recommendations(results)
            
            # Salvar log
            self._save_integrity_log(results)
            
            logger.info(f"✅ Verificação concluída: {results['healthy_files']}/{results['total_files']} arquivos saudáveis")
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de integridade: {e}")
            results["issues"].append(f"Erro na verificação: {str(e)}")
        
        return results
    
    def check_file_integrity(self, file_path: str) -> Dict[str, Any]:
        """Verifica integridade de um arquivo específico"""
        
        result = {
            "file": file_path,
            "status": "healthy",
            "issues": [],
            "metadata": {},
            "recommendations": []
        }
        
        try:
            if not os.path.exists(file_path):
                result["status"] = "corrupted"
                result["issues"].append("Arquivo não encontrado")
                return result
            
            # Verificações básicas
            file_stats = os.stat(file_path)
            result["metadata"] = {
                "size": file_stats.st_size,
                "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "permissions": oct(file_stats.st_mode)[-3:]
            }
            
            # Verificar tamanho
            if file_stats.st_size == 0:
                result["status"] = "corrupted"
                result["issues"].append("Arquivo vazio")
                result["recommendations"].append("Regenerar arquivo")
                return result
            
            if file_stats.st_size > self.max_file_size:
                result["status"] = "suspicious"
                result["issues"].append(f"Arquivo muito grande: {file_stats.st_size / 1024 / 1024:.1f}MB")
            
            # Verificar tipo de arquivo
            try:
                file_type = magic.from_file(file_path, mime=True)
                result["metadata"]["mime_type"] = file_type
            except:
                result["metadata"]["mime_type"] = "unknown"
            
            # Verificações específicas por extensão
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.json':
                json_result = self._check_json_integrity(file_path)
                result["issues"].extend(json_result["issues"])
                result["metadata"].update(json_result["metadata"])
                if json_result["corrupted"]:
                    result["status"] = "corrupted"
            
            elif file_ext in ['.txt', '.md', '.py', '.html', '.css', '.js']:
                text_result = self._check_text_integrity(file_path)
                result["issues"].extend(text_result["issues"])
                result["metadata"].update(text_result["metadata"])
                if text_result["corrupted"]:
                    result["status"] = "corrupted"
            
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                image_result = self._check_image_integrity(file_path)
                result["issues"].extend(image_result["issues"])
                result["metadata"].update(image_result["metadata"])
                if image_result["corrupted"]:
                    result["status"] = "corrupted"
            
            # Verificar hash para detectar mudanças
            result["metadata"]["md5_hash"] = self._calculate_file_hash(file_path)
            
            # Determinar status final
            if result["issues"] and result["status"] == "healthy":
                result["status"] = "suspicious"
            
        except Exception as e:
            result["status"] = "corrupted"
            result["issues"].append(f"Erro na verificação: {str(e)}")
            logger.error(f"❌ Erro ao verificar {file_path}: {e}")
        
        return result
    
    def _check_json_integrity(self, file_path: str) -> Dict[str, Any]:
        """Verifica integridade de arquivo JSON"""
        
        result = {
            "issues": [],
            "metadata": {},
            "corrupted": False
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar se é JSON válido
            try:
                data = json.loads(content)
                result["metadata"]["json_valid"] = True
                result["metadata"]["json_keys"] = len(data) if isinstance(data, dict) else 0
                result["metadata"]["json_type"] = type(data).__name__
                
                # Verificar estrutura esperada para arquivos do sistema
                if "fallback_mode" in str(data):
                    if isinstance(data, dict) and data.get("fallback_mode") is True:
                        result["issues"].append("Arquivo em modo fallback - pode conter dados simulados")
                
                if "confidence_level" in str(data):
                    if isinstance(data, dict) and data.get("confidence_level", 1.0) < 0.5:
                        result["issues"].append("Baixo nível de confiança nos dados")
                
            except json.JSONDecodeError as e:
                result["corrupted"] = True
                result["issues"].append(f"JSON inválido: {str(e)}")
                result["metadata"]["json_valid"] = False
            
            # Verificar encoding
            encoding_result = self._detect_encoding(file_path)
            result["metadata"]["encoding"] = encoding_result["encoding"]
            if encoding_result["confidence"] < 0.8:
                result["issues"].append(f"Encoding incerto: {encoding_result['encoding']} ({encoding_result['confidence']:.2f})")
            
        except Exception as e:
            result["corrupted"] = True
            result["issues"].append(f"Erro ao ler arquivo JSON: {str(e)}")
        
        return result
    
    def _check_text_integrity(self, file_path: str) -> Dict[str, Any]:
        """Verifica integridade de arquivo de texto"""
        
        result = {
            "issues": [],
            "metadata": {},
            "corrupted": False
        }
        
        try:
            # Detectar encoding
            encoding_result = self._detect_encoding(file_path)
            result["metadata"]["encoding"] = encoding_result["encoding"]
            result["metadata"]["encoding_confidence"] = encoding_result["confidence"]
            
            if encoding_result["confidence"] < 0.7:
                result["issues"].append(f"Encoding incerto: {encoding_result['encoding']}")
            
            # Tentar ler o arquivo
            try:
                with open(file_path, 'r', encoding=encoding_result["encoding"]) as f:
                    content = f.read()
                    
                result["metadata"]["line_count"] = content.count('\n')
                result["metadata"]["char_count"] = len(content)
                
                # Verificar caracteres problemáticos
                null_chars = content.count('\x00')
                if null_chars > 0:
                    result["issues"].append(f"Contém {null_chars} caracteres nulos")
                
                # Verificar se há muito conteúdo binário
                try:
                    content.encode('utf-8')
                except UnicodeEncodeError:
                    result["issues"].append("Contém caracteres não-UTF8")
                
            except UnicodeDecodeError as e:
                result["corrupted"] = True
                result["issues"].append(f"Erro de decodificação: {str(e)}")
            
        except Exception as e:
            result["corrupted"] = True
            result["issues"].append(f"Erro ao verificar arquivo de texto: {str(e)}")
        
        return result
    
    def _check_image_integrity(self, file_path: str) -> Dict[str, Any]:
        """Verifica integridade de arquivo de imagem"""
        
        result = {
            "issues": [],
            "metadata": {},
            "corrupted": False
        }
        
        try:
            from PIL import Image
            
            try:
                with Image.open(file_path) as img:
                    result["metadata"]["format"] = img.format
                    result["metadata"]["size"] = img.size
                    result["metadata"]["mode"] = img.mode
                    
                    # Verificar se a imagem pode ser processada
                    img.verify()
                    
            except Exception as e:
                result["corrupted"] = True
                result["issues"].append(f"Imagem corrompida: {str(e)}")
                
        except ImportError:
            result["issues"].append("PIL não disponível para verificação de imagem")
        except Exception as e:
            result["corrupted"] = True
            result["issues"].append(f"Erro ao verificar imagem: {str(e)}")
        
        return result
    
    def _detect_encoding(self, file_path: str) -> Dict[str, Any]:
        """Detecta encoding de um arquivo"""
        
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Ler primeiros 10KB
                
            result = chardet.detect(raw_data)
            return {
                "encoding": result.get("encoding", "utf-8"),
                "confidence": result.get("confidence", 0.0)
            }
        except:
            return {"encoding": "utf-8", "confidence": 0.5}
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula hash MD5 do arquivo"""
        
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return "unknown"
    
    def quarantine_file(self, file_path: str, reason: str) -> bool:
        """Move arquivo corrompido para quarentena"""
        
        try:
            if not os.path.exists(file_path):
                return False
            
            # Criar nome único na quarentena
            file_name = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_name = f"{timestamp}_{file_name}"
            quarantine_path = os.path.join(self.quarantine_dir, quarantine_name)
            
            # Mover arquivo
            os.rename(file_path, quarantine_path)
            
            # Registrar quarentena
            quarantine_info = {
                "original_path": file_path,
                "quarantine_path": quarantine_path,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            }
            
            quarantine_log = os.path.join(self.quarantine_dir, "quarantine_log.json")
            if os.path.exists(quarantine_log):
                with open(quarantine_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = []
            
            log_data.append(quarantine_info)
            
            with open(quarantine_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"🚨 Arquivo em quarentena: {file_path} -> {quarantine_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao colocar arquivo em quarentena: {e}")
            return False
    
    def repair_json_file(self, file_path: str) -> bool:
        """Tenta reparar arquivo JSON corrompido"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Tentar reparos comuns
            repaired_content = content
            
            # Remover caracteres nulos
            repaired_content = repaired_content.replace('\x00', '')
            
            # Tentar fechar chaves/colchetes não fechados
            open_braces = repaired_content.count('{') - repaired_content.count('}')
            open_brackets = repaired_content.count('[') - repaired_content.count(']')
            
            if open_braces > 0:
                repaired_content += '}' * open_braces
            if open_brackets > 0:
                repaired_content += ']' * open_brackets
            
            # Verificar se o reparo funcionou
            try:
                json.loads(repaired_content)
                
                # Fazer backup do original
                backup_path = file_path + '.backup'
                os.rename(file_path, backup_path)
                
                # Salvar versão reparada
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(repaired_content)
                
                logger.info(f"✅ Arquivo JSON reparado: {file_path}")
                return True
                
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Não foi possível reparar: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao reparar JSON: {e}")
            return False
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        
        recommendations = []
        
        corruption_rate = results["corrupted_files"] / results["total_files"] if results["total_files"] > 0 else 0
        
        if corruption_rate > 0.1:
            recommendations.append("Taxa alta de corrupção - verificar sistema de arquivos")
        
        if results["corrupted_files"] > 0:
            recommendations.append("Mover arquivos corrompidos para quarentena")
            recommendations.append("Regenerar arquivos corrompidos se possível")
        
        if results["suspicious_files"] > 0:
            recommendations.append("Investigar arquivos suspeitos")
        
        # Recomendações específicas baseadas nos problemas
        for issue in results["issues"]:
            if isinstance(issue, dict):
                if "fallback" in str(issue.get("details", "")):
                    recommendations.append("Reprocessar dados para evitar modo fallback")
                if "encoding" in str(issue.get("details", "")):
                    recommendations.append("Padronizar encoding para UTF-8")
        
        return list(set(recommendations))  # Remover duplicatas
    
    def _save_integrity_log(self, results: Dict[str, Any]):
        """Salva log de verificação de integridade"""
        
        try:
            if os.path.exists(self.integrity_log):
                with open(self.integrity_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = []
            
            log_data.append(results)
            
            # Manter apenas os últimos 50 logs
            if len(log_data) > 50:
                log_data = log_data[-50:]
            
            with open(self.integrity_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar log de integridade: {e}")
    
    def get_integrity_report(self) -> Dict[str, Any]:
        """Retorna relatório de integridade histórico"""
        
        try:
            if os.path.exists(self.integrity_log):
                with open(self.integrity_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                
                if log_data:
                    latest = log_data[-1]
                    return {
                        "latest_check": latest,
                        "total_checks": len(log_data),
                        "trend": self._analyze_integrity_trend(log_data)
                    }
            
            return {"error": "Nenhum log de integridade encontrado"}
            
        except Exception as e:
            return {"error": f"Erro ao ler log: {str(e)}"}
    
    def _analyze_integrity_trend(self, log_data: List[Dict]) -> Dict[str, Any]:
        """Analisa tendência de integridade"""
        
        if len(log_data) < 2:
            return {"trend": "insufficient_data"}
        
        recent = log_data[-5:]  # Últimas 5 verificações
        
        corruption_rates = []
        for entry in recent:
            total = entry.get("total_files", 1)
            corrupted = entry.get("corrupted_files", 0)
            rate = corrupted / total if total > 0 else 0
            corruption_rates.append(rate)
        
        if len(corruption_rates) >= 2:
            if corruption_rates[-1] > corruption_rates[0]:
                trend = "worsening"
            elif corruption_rates[-1] < corruption_rates[0]:
                trend = "improving"
            else:
                trend = "stable"
        else:
            trend = "unknown"
        
        return {
            "trend": trend,
            "avg_corruption_rate": sum(corruption_rates) / len(corruption_rates),
            "latest_corruption_rate": corruption_rates[-1] if corruption_rates else 0
        }

# Instância global
file_integrity_checker = FileIntegrityChecker()