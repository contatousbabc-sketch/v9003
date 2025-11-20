"""
Elasticsearch Integration - Fallback direto para Google CSE
Implementação mais simples e confiável que Fess
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
import time

class ElasticsearchIntegration:
    """Integração direta com Elasticsearch como fallback do Google CSE"""
    
    def __init__(self, host: str = "localhost", port: int = 9200):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.logger = logging.getLogger(__name__)
        
    def is_available(self) -> bool:
        """Verifica se o Elasticsearch está disponível"""
        try:
            response = requests.get(f"{self.base_url}/_cluster/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Elasticsearch não disponível: {e}")
            return False
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca no Elasticsearch
        
        Args:
            query: Termo de busca
            max_results: Número máximo de resultados
            
        Returns:
            Lista de resultados formatados
        """
        if not self.is_available():
            return []
            
        try:
            # Busca em todos os índices
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^2", "content", "url", "description"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                },
                "size": max_results,
                "highlight": {
                    "fields": {
                        "title": {},
                        "content": {"fragment_size": 150, "number_of_fragments": 3}
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/_search",
                json=search_body,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._format_results(data, query)
            else:
                self.logger.error(f"Erro na busca Elasticsearch: {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Erro na busca Elasticsearch: {e}")
            return []
    
    def _format_results(self, data: Dict, query: str) -> List[Dict[str, Any]]:
        """Formata os resultados do Elasticsearch para o formato padrão"""
        results = []
        
        hits = data.get("hits", {}).get("hits", [])
        
        for hit in hits:
            source = hit.get("_source", {})
            highlight = hit.get("highlight", {})
            
            # Extrai snippet do highlight ou do conteúdo
            snippet = ""
            if "content" in highlight:
                snippet = " ... ".join(highlight["content"])
            elif "content" in source:
                content = source["content"]
                if len(content) > 200:
                    snippet = content[:200] + "..."
                else:
                    snippet = content
            
            result = {
                "title": highlight.get("title", [source.get("title", "")])[0] if highlight.get("title") else source.get("title", ""),
                "link": source.get("url", ""),
                "snippet": snippet,
                "displayLink": source.get("domain", ""),
                "formattedUrl": source.get("url", ""),
                "score": hit.get("_score", 0),
                "source": "elasticsearch"
            }
            
            results.append(result)
        
        return results
    
    def index_document(self, index: str, doc_id: str, document: Dict[str, Any]) -> bool:
        """
        Indexa um documento no Elasticsearch
        
        Args:
            index: Nome do índice
            doc_id: ID do documento
            document: Documento a ser indexado
            
        Returns:
            True se indexado com sucesso
        """
        if not self.is_available():
            return False
            
        try:
            response = requests.put(
                f"{self.base_url}/{index}/_doc/{doc_id}",
                json=document,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            self.logger.error(f"Erro ao indexar documento: {e}")
            return False
    
    def create_web_index(self) -> bool:
        """Cria índice para páginas web se não existir"""
        if not self.is_available():
            return False
            
        try:
            # Verifica se o índice já existe
            response = requests.head(f"{self.base_url}/web_pages")
            if response.status_code == 200:
                return True
            
            # Cria o índice com mapping otimizado
            mapping = {
                "mappings": {
                    "properties": {
                        "title": {
                            "type": "text",
                            "analyzer": "standard",
                            "boost": 2.0
                        },
                        "content": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "url": {
                            "type": "keyword"
                        },
                        "domain": {
                            "type": "keyword"
                        },
                        "description": {
                            "type": "text"
                        },
                        "timestamp": {
                            "type": "date"
                        },
                        "keywords": {
                            "type": "keyword"
                        }
                    }
                }
            }
            
            response = requests.put(
                f"{self.base_url}/web_pages",
                json=mapping,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Erro ao criar índice: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do Elasticsearch"""
        if not self.is_available():
            return {}
            
        try:
            response = requests.get(f"{self.base_url}/_stats", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {}

# Instância global para uso em outros módulos
elasticsearch_client = ElasticsearchIntegration()