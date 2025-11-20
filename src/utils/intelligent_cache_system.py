#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Sistema de Cache Inteligente
Sistema robusto de cache para otimizar performance das requisições
"""

import os
import json
import hashlib
import pickle
import time
from typing import Dict, Any, Optional, Union, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import threading
from collections import defaultdict

# Importar sistema de logging otimizado
try:
    from enhanced_logging_system import get_logger, log_performance
except ImportError:
    import logging
    def get_logger(name, level=None):
        return logging.getLogger(name)
    def log_performance(operation, duration, details=None):
        pass

logger = get_logger(__name__)

@dataclass
class CacheEntry:
    """Entrada do cache com metadados"""
    key: str
    data: Any
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0
    cache_type: str = 'default'

@dataclass
class CacheStats:
    """Estatísticas do cache"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    total_size_bytes: int = 0
    hit_rate: float = 0.0

class IntelligentCacheSystem:
    """Sistema de Cache Inteligente V2.0 - Ultra-robusto"""
    
    def __init__(self, 
                 cache_dir: str = "cache",
                 max_memory_size: int = 100 * 1024 * 1024,  # 100MB
                 max_disk_size: int = 1024 * 1024 * 1024,   # 1GB
                 default_ttl: int = 3600):  # 1 hora
        """
        Inicializa o sistema de cache inteligente
        
        Args:
            cache_dir: Diretório para cache em disco
            max_memory_size: Tamanho máximo do cache em memória (bytes)
            max_disk_size: Tamanho máximo do cache em disco (bytes)
            default_ttl: TTL padrão em segundos
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.max_memory_size = max_memory_size
        self.max_disk_size = max_disk_size
        self.default_ttl = default_ttl
        
        # Cache em memória
        self.memory_cache: Dict[str, CacheEntry] = {}
        
        # Cache em disco (índice)
        self.disk_cache_index: Dict[str, str] = {}  # key -> filepath
        
        # Estatísticas
        self.stats = CacheStats()
        
        # Lock para thread safety
        self._lock = threading.RLock()
        
        # Configurações de TTL por tipo
        self.ttl_config = {
            'api_response': 1800,      # 30 minutos
            'search_results': 3600,    # 1 hora
            'file_content': 7200,      # 2 horas
            'metadata': 86400,         # 24 horas
            'static_data': 604800,     # 7 dias
            'user_session': 1800,      # 30 minutos
            'temporary': 300,          # 5 minutos
            'permanent': 31536000      # 1 ano
        }
        
        # Arquivo de estatísticas
        self.stats_file = self.cache_dir / "cache_stats.json"
        
        # Carregar cache existente
        self._load_cache_index()
        self._load_stats()
        
        logger.info("🚀 Sistema de Cache Inteligente V2.0 inicializado")
        logger.info(f"📁 Diretório de cache: {self.cache_dir}")
        logger.info(f"💾 Limite memória: {self.max_memory_size // 1024 // 1024}MB")
        logger.info(f"💿 Limite disco: {self.max_disk_size // 1024 // 1024}MB")
    
    def _generate_cache_key(self, data: Union[str, Dict, List], prefix: str = "") -> str:
        """Gera chave única para o cache"""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        else:
            data_str = str(data)
        
        hash_obj = hashlib.sha256(data_str.encode('utf-8'))
        if prefix:
            hash_obj.update(prefix.encode('utf-8'))
        
        return hash_obj.hexdigest()[:32]  # 32 caracteres
    
    def _get_ttl(self, cache_type: str) -> int:
        """Obtém TTL baseado no tipo de cache"""
        return self.ttl_config.get(cache_type, self.default_ttl)
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Verifica se entrada está expirada"""
        return datetime.now() > entry.expires_at
    
    def _calculate_size(self, data: Any) -> int:
        """Calcula tamanho dos dados em bytes"""
        try:
            if isinstance(data, str):
                return len(data.encode('utf-8'))
            elif isinstance(data, (dict, list)):
                return len(json.dumps(data).encode('utf-8'))
            else:
                return len(pickle.dumps(data))
        except Exception:
            return 1024  # Estimativa padrão
    
    def _cleanup_expired(self):
        """Remove entradas expiradas"""
        with self._lock:
            expired_keys = []
            
            # Verificar cache em memória
            for key, entry in self.memory_cache.items():
                if self._is_expired(entry):
                    expired_keys.append(key)
            
            # Remover entradas expiradas
            for key in expired_keys:
                self._remove_from_memory(key)
                self.stats.evictions += 1
            
            if expired_keys:
                logger.debug(f"🧹 Removidas {len(expired_keys)} entradas expiradas do cache")
    
    def _remove_from_memory(self, key: str):
        """Remove entrada do cache em memória"""
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            self.stats.total_size_bytes -= entry.size_bytes
            del self.memory_cache[key]
    
    def _evict_lru(self, needed_space: int):
        """Remove entradas menos usadas para liberar espaço"""
        with self._lock:
            # Ordenar por último acesso
            entries = list(self.memory_cache.items())
            entries.sort(key=lambda x: x[1].last_accessed or x[1].created_at)
            
            freed_space = 0
            evicted_count = 0
            
            for key, entry in entries:
                if freed_space >= needed_space:
                    break
                
                freed_space += entry.size_bytes
                self._remove_from_memory(key)
                evicted_count += 1
                self.stats.evictions += 1
            
            if evicted_count > 0:
                logger.debug(f"🗑️ Removidas {evicted_count} entradas LRU ({freed_space} bytes)")
    
    def _save_to_disk(self, key: str, entry: CacheEntry) -> bool:
        """Salva entrada no cache em disco"""
        try:
            file_path = self.cache_dir / f"{key}.cache"
            
            # Salvar dados
            with open(file_path, 'wb') as f:
                pickle.dump({
                    'data': entry.data,
                    'metadata': asdict(entry)
                }, f)
            
            # Atualizar índice
            self.disk_cache_index[key] = str(file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar cache em disco: {e}")
            return False
    
    def _load_from_disk(self, key: str) -> Optional[CacheEntry]:
        """Carrega entrada do cache em disco"""
        try:
            if key not in self.disk_cache_index:
                return None
            
            file_path = Path(self.disk_cache_index[key])
            if not file_path.exists():
                # Remover do índice se arquivo não existe
                del self.disk_cache_index[key]
                return None
            
            with open(file_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Reconstruir entrada
            metadata = cached_data['metadata']
            entry = CacheEntry(
                key=metadata['key'],
                data=cached_data['data'],
                created_at=datetime.fromisoformat(metadata['created_at']),
                expires_at=datetime.fromisoformat(metadata['expires_at']),
                access_count=metadata['access_count'],
                last_accessed=datetime.fromisoformat(metadata['last_accessed']) if metadata['last_accessed'] else None,
                size_bytes=metadata['size_bytes'],
                cache_type=metadata['cache_type']
            )
            
            return entry
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar cache do disco: {e}")
            return None
    
    def _load_cache_index(self):
        """Carrega índice do cache em disco"""
        index_file = self.cache_dir / "cache_index.json"
        try:
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    self.disk_cache_index = json.load(f)
                logger.debug(f"📋 Índice de cache carregado: {len(self.disk_cache_index)} entradas")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar índice de cache: {e}")
            self.disk_cache_index = {}
    
    def _save_cache_index(self):
        """Salva índice do cache em disco"""
        index_file = self.cache_dir / "cache_index.json"
        try:
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self.disk_cache_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar índice de cache: {e}")
    
    def _load_stats(self):
        """Carrega estatísticas do cache"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    stats_data = json.load(f)
                    self.stats = CacheStats(**stats_data)
                logger.debug("📊 Estatísticas de cache carregadas")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar estatísticas: {e}")
    
    def _save_stats(self):
        """Salva estatísticas do cache"""
        try:
            # Calcular hit rate
            if self.stats.total_requests > 0:
                self.stats.hit_rate = self.stats.hits / self.stats.total_requests
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.stats), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar estatísticas: {e}")
    
    def put(self, 
            key_data: Union[str, Dict, List], 
            value: Any, 
            cache_type: str = 'default',
            ttl: Optional[int] = None,
            prefix: str = "") -> str:
        """
        Armazena dados no cache
        
        Args:
            key_data: Dados para gerar a chave
            value: Valor a ser armazenado
            cache_type: Tipo de cache para TTL apropriado
            ttl: TTL customizado em segundos
            prefix: Prefixo para a chave
            
        Returns:
            Chave gerada para o cache
        """
        start_time = time.time()
        
        with self._lock:
            # Gerar chave
            cache_key = self._generate_cache_key(key_data, prefix)
            
            # Determinar TTL
            if ttl is None:
                ttl = self._get_ttl(cache_type)
            
            # Calcular tamanho
            size_bytes = self._calculate_size(value)
            
            # Criar entrada
            now = datetime.now()
            entry = CacheEntry(
                key=cache_key,
                data=value,
                created_at=now,
                expires_at=now + timedelta(seconds=ttl),
                size_bytes=size_bytes,
                cache_type=cache_type
            )
            
            # Verificar se cabe na memória
            if self.stats.total_size_bytes + size_bytes > self.max_memory_size:
                # Tentar liberar espaço
                self._evict_lru(size_bytes)
            
            # Se ainda não cabe, salvar em disco
            if self.stats.total_size_bytes + size_bytes > self.max_memory_size:
                if self._save_to_disk(cache_key, entry):
                    logger.debug(f"💿 Cache salvo em disco: {cache_key}")
                else:
                    logger.warning(f"⚠️ Falha ao salvar cache: {cache_key}")
            else:
                # Salvar em memória
                self.memory_cache[cache_key] = entry
                self.stats.total_size_bytes += size_bytes
                logger.debug(f"💾 Cache salvo em memória: {cache_key}")
            
            # Limpeza periódica
            if len(self.memory_cache) % 100 == 0:
                self._cleanup_expired()
            
            duration = time.time() - start_time
            log_performance('cache_put', duration, {
                'key': cache_key[:8],
                'type': cache_type,
                'size': size_bytes,
                'ttl': ttl
            })
            
            return cache_key
    
    def get(self, 
            key_data: Union[str, Dict, List], 
            prefix: str = "",
            default: Any = None) -> Any:
        """
        Recupera dados do cache
        
        Args:
            key_data: Dados para gerar a chave
            prefix: Prefixo para a chave
            default: Valor padrão se não encontrado
            
        Returns:
            Dados armazenados ou valor padrão
        """
        start_time = time.time()
        
        with self._lock:
            self.stats.total_requests += 1
            
            # Gerar chave
            cache_key = self._generate_cache_key(key_data, prefix)
            
            # Verificar cache em memória primeiro
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]
                
                # Verificar se expirou
                if self._is_expired(entry):
                    self._remove_from_memory(cache_key)
                    self.stats.misses += 1
                    self.stats.evictions += 1
                    
                    duration = time.time() - start_time
                    log_performance('cache_get_miss', duration, {'key': cache_key[:8], 'reason': 'expired'})
                    
                    return default
                
                # Atualizar estatísticas de acesso
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                
                self.stats.hits += 1
                
                duration = time.time() - start_time
                log_performance('cache_get_hit', duration, {'key': cache_key[:8], 'source': 'memory'})
                
                return entry.data
            
            # Verificar cache em disco
            entry = self._load_from_disk(cache_key)
            if entry and not self._is_expired(entry):
                # Mover para memória se houver espaço
                if self.stats.total_size_bytes + entry.size_bytes <= self.max_memory_size:
                    entry.access_count += 1
                    entry.last_accessed = datetime.now()
                    self.memory_cache[cache_key] = entry
                    self.stats.total_size_bytes += entry.size_bytes
                
                self.stats.hits += 1
                
                duration = time.time() - start_time
                log_performance('cache_get_hit', duration, {'key': cache_key[:8], 'source': 'disk'})
                
                return entry.data
            
            # Cache miss
            self.stats.misses += 1
            
            duration = time.time() - start_time
            log_performance('cache_get_miss', duration, {'key': cache_key[:8], 'reason': 'not_found'})
            
            return default
    
    def invalidate(self, key_data: Union[str, Dict, List], prefix: str = "") -> bool:
        """
        Invalida entrada do cache
        
        Args:
            key_data: Dados para gerar a chave
            prefix: Prefixo para a chave
            
        Returns:
            True se entrada foi removida
        """
        with self._lock:
            cache_key = self._generate_cache_key(key_data, prefix)
            
            removed = False
            
            # Remover da memória
            if cache_key in self.memory_cache:
                self._remove_from_memory(cache_key)
                removed = True
            
            # Remover do disco
            if cache_key in self.disk_cache_index:
                try:
                    file_path = Path(self.disk_cache_index[cache_key])
                    if file_path.exists():
                        file_path.unlink()
                    del self.disk_cache_index[cache_key]
                    removed = True
                except Exception as e:
                    logger.error(f"❌ Erro ao remover cache do disco: {e}")
            
            if removed:
                logger.debug(f"🗑️ Cache invalidado: {cache_key}")
            
            return removed
    
    def clear(self, cache_type: Optional[str] = None):
        """
        Limpa cache (tudo ou por tipo)
        
        Args:
            cache_type: Tipo específico para limpar (None = tudo)
        """
        with self._lock:
            if cache_type is None:
                # Limpar tudo
                self.memory_cache.clear()
                self.stats.total_size_bytes = 0
                
                # Limpar disco
                for file_path in self.disk_cache_index.values():
                    try:
                        Path(file_path).unlink(missing_ok=True)
                    except Exception:
                        pass
                
                self.disk_cache_index.clear()
                logger.info("🧹 Cache completamente limpo")
                
            else:
                # Limpar por tipo
                keys_to_remove = []
                
                for key, entry in self.memory_cache.items():
                    if entry.cache_type == cache_type:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    self._remove_from_memory(key)
                
                logger.info(f"🧹 Cache limpo para tipo: {cache_type}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        with self._lock:
            # Atualizar hit rate
            if self.stats.total_requests > 0:
                self.stats.hit_rate = self.stats.hits / self.stats.total_requests
            
            return {
                'memory_entries': len(self.memory_cache),
                'disk_entries': len(self.disk_cache_index),
                'memory_size_mb': self.stats.total_size_bytes / 1024 / 1024,
                'hits': self.stats.hits,
                'misses': self.stats.misses,
                'hit_rate': self.stats.hit_rate,
                'evictions': self.stats.evictions,
                'total_requests': self.stats.total_requests
            }
    
    def cleanup_and_save(self):
        """Limpeza final e salvamento"""
        with self._lock:
            self._cleanup_expired()
            self._save_cache_index()
            self._save_stats()
            logger.info("💾 Cache salvo e limpo")

# Instância global do cache
_cache_instance = None

def get_cache() -> IntelligentCacheSystem:
    """Obtém instância global do cache"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = IntelligentCacheSystem()
    return _cache_instance

# Funções de conveniência
def cache_put(key_data: Union[str, Dict, List], 
              value: Any, 
              cache_type: str = 'default',
              ttl: Optional[int] = None,
              prefix: str = "") -> str:
    """Função de conveniência para armazenar no cache"""
    return get_cache().put(key_data, value, cache_type, ttl, prefix)

def cache_get(key_data: Union[str, Dict, List], 
              prefix: str = "",
              default: Any = None) -> Any:
    """Função de conveniência para recuperar do cache"""
    return get_cache().get(key_data, prefix, default)

def cache_invalidate(key_data: Union[str, Dict, List], prefix: str = "") -> bool:
    """Função de conveniência para invalidar cache"""
    return get_cache().invalidate(key_data, prefix)

def cache_stats() -> Dict[str, Any]:
    """Função de conveniência para obter estatísticas"""
    return get_cache().get_stats()