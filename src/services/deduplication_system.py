#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Deduplicação Avançado
Evita conteúdo duplicado e inconsistente entre módulos
"""

import hashlib
import json
import logging
import os
import re
from typing import Dict, List, Any, Set, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import difflib

logger = logging.getLogger(__name__)

@dataclass
class ContentFingerprint:
    """Impressão digital de conteúdo para deduplicação"""
    content_hash: str
    title_hash: str
    url_hash: str
    text_similarity_hash: str
    timestamp: str
    source: str
    content_type: str

class DeduplicationSystem:
    """Sistema avançado de deduplicação de conteúdo"""
    
    def __init__(self, data_dir: str = "analyses_data"):
        self.data_dir = data_dir
        self.fingerprints_file = os.path.join(data_dir, "content_fingerprints.json")
        self.fingerprints: Dict[str, ContentFingerprint] = {}
        self.similarity_threshold = 0.85  # 85% de similaridade = duplicata
        
        os.makedirs(data_dir, exist_ok=True)
        self._load_fingerprints()
        
        logger.info("🔍 Sistema de Deduplicação inicializado")
    
    def _load_fingerprints(self):
        """Carrega fingerprints existentes"""
        try:
            if os.path.exists(self.fingerprints_file):
                with open(self.fingerprints_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        self.fingerprints[key] = ContentFingerprint(**value)
                logger.info(f"✅ Carregados {len(self.fingerprints)} fingerprints")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar fingerprints: {e}")
    
    def _save_fingerprints(self):
        """Salva fingerprints no disco"""
        try:
            data = {key: asdict(fp) for key, fp in self.fingerprints.items()}
            with open(self.fingerprints_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar fingerprints: {e}")
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para comparação"""
        if not text:
            return ""
        
        # Remove caracteres especiais, espaços extras, converte para minúsculas
        normalized = re.sub(r'[^\w\s]', ' ', text.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def _calculate_content_hash(self, content: Any) -> str:
        """Calcula hash do conteúdo completo"""
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _calculate_text_similarity_hash(self, text: str) -> str:
        """Calcula hash baseado em similaridade textual"""
        normalized = self._normalize_text(text)
        # Usa apenas as primeiras 500 palavras para similaridade
        words = normalized.split()[:500]
        similarity_text = ' '.join(sorted(set(words)))  # Remove duplicatas e ordena
        return hashlib.md5(similarity_text.encode()).hexdigest()
    
    def _calculate_url_hash(self, url: str) -> str:
        """Calcula hash da URL normalizada"""
        if not url:
            return ""
        
        # Remove parâmetros de tracking e normaliza
        normalized_url = re.sub(r'[?&](utm_|fbclid|gclid|ref=)', '', url.lower())
        normalized_url = re.sub(r'/$', '', normalized_url)  # Remove trailing slash
        return hashlib.md5(normalized_url.encode()).hexdigest()
    
    def create_fingerprint(self, content: Dict[str, Any], source: str, content_type: str = "general") -> ContentFingerprint:
        """Cria fingerprint de conteúdo"""
        
        # Extrai texto principal do conteúdo
        text_content = ""
        if isinstance(content, dict):
            # Tenta extrair texto de campos comuns
            for field in ['title', 'description', 'content', 'text', 'summary', 'snippet']:
                if field in content and content[field]:
                    text_content += str(content[field]) + " "
        else:
            text_content = str(content)
        
        # Extrai título
        title = ""
        if isinstance(content, dict):
            title = content.get('title', content.get('name', ''))
        
        # Extrai URL
        url = ""
        if isinstance(content, dict):
            url = content.get('url', content.get('link', content.get('page_url', '')))
        
        # Calcula hashes
        content_hash = self._calculate_content_hash(content)
        title_hash = hashlib.md5(self._normalize_text(title).encode()).hexdigest()
        url_hash = self._calculate_url_hash(url)
        text_similarity_hash = self._calculate_text_similarity_hash(text_content)
        
        return ContentFingerprint(
            content_hash=content_hash,
            title_hash=title_hash,
            url_hash=url_hash,
            text_similarity_hash=text_similarity_hash,
            timestamp=datetime.now().isoformat(),
            source=source,
            content_type=content_type
        )
    
    def is_duplicate(self, content: Dict[str, Any], source: str, content_type: str = "general") -> Tuple[bool, Optional[str]]:
        """Verifica se o conteúdo é duplicado"""
        
        fingerprint = self.create_fingerprint(content, source, content_type)
        
        # Verifica duplicatas exatas por hash de conteúdo
        for existing_key, existing_fp in self.fingerprints.items():
            if existing_fp.content_hash == fingerprint.content_hash:
                logger.debug(f"🔍 Duplicata exata encontrada: {existing_key}")
                return True, existing_key
        
        # Verifica duplicatas por URL
        if fingerprint.url_hash and fingerprint.url_hash != "":
            for existing_key, existing_fp in self.fingerprints.items():
                if existing_fp.url_hash == fingerprint.url_hash:
                    logger.debug(f"🔍 Duplicata por URL encontrada: {existing_key}")
                    return True, existing_key
        
        # Verifica similaridade textual
        if fingerprint.text_similarity_hash:
            for existing_key, existing_fp in self.fingerprints.items():
                if existing_fp.text_similarity_hash == fingerprint.text_similarity_hash:
                    logger.debug(f"🔍 Duplicata por similaridade encontrada: {existing_key}")
                    return True, existing_key
        
        return False, None
    
    def add_content(self, content: Dict[str, Any], source: str, content_type: str = "general") -> str:
        """Adiciona conteúdo ao sistema de deduplicação"""
        
        fingerprint = self.create_fingerprint(content, source, content_type)
        
        # Gera chave única
        key = f"{source}_{content_type}_{fingerprint.content_hash[:8]}"
        
        # Adiciona ao sistema
        self.fingerprints[key] = fingerprint
        self._save_fingerprints()
        
        logger.debug(f"✅ Conteúdo adicionado: {key}")
        return key
    
    def deduplicate_list(self, content_list: List[Dict[str, Any]], source: str, content_type: str = "general") -> List[Dict[str, Any]]:
        """Remove duplicatas de uma lista de conteúdo"""
        
        unique_content = []
        seen_hashes = set()
        
        for item in content_list:
            fingerprint = self.create_fingerprint(item, source, content_type)
            
            # Verifica se já foi visto nesta lista
            if fingerprint.content_hash in seen_hashes:
                logger.debug(f"🔍 Duplicata na lista removida")
                continue
            
            # Verifica se é duplicata global
            is_dup, existing_key = self.is_duplicate(item, source, content_type)
            if is_dup:
                logger.debug(f"🔍 Duplicata global removida: {existing_key}")
                continue
            
            # Adiciona ao resultado e marca como visto
            unique_content.append(item)
            seen_hashes.add(fingerprint.content_hash)
            
            # Adiciona ao sistema global
            self.add_content(item, source, content_type)
        
        logger.info(f"🔍 Deduplicação: {len(content_list)} → {len(unique_content)} itens únicos")
        return unique_content
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de deduplicação"""
        
        stats = {
            "total_fingerprints": len(self.fingerprints),
            "sources": {},
            "content_types": {},
            "oldest_entry": None,
            "newest_entry": None
        }
        
        for fp in self.fingerprints.values():
            # Conta por fonte
            if fp.source not in stats["sources"]:
                stats["sources"][fp.source] = 0
            stats["sources"][fp.source] += 1
            
            # Conta por tipo
            if fp.content_type not in stats["content_types"]:
                stats["content_types"][fp.content_type] = 0
            stats["content_types"][fp.content_type] += 1
            
            # Encontra mais antigo e mais novo
            if not stats["oldest_entry"] or fp.timestamp < stats["oldest_entry"]:
                stats["oldest_entry"] = fp.timestamp
            if not stats["newest_entry"] or fp.timestamp > stats["newest_entry"]:
                stats["newest_entry"] = fp.timestamp
        
        return stats
    
    def cleanup_old_entries(self, days_old: int = 30):
        """Remove entradas antigas do sistema"""
        
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        old_keys = []
        for key, fp in self.fingerprints.items():
            try:
                entry_date = datetime.fromisoformat(fp.timestamp)
                if entry_date < cutoff_date:
                    old_keys.append(key)
            except:
                # Se não conseguir parsear a data, considera como antiga
                old_keys.append(key)
        
        # Remove entradas antigas
        for key in old_keys:
            del self.fingerprints[key]
        
        if old_keys:
            self._save_fingerprints()
            logger.info(f"🧹 Removidas {len(old_keys)} entradas antigas")

# Instância global
deduplication_system = DeduplicationSystem()