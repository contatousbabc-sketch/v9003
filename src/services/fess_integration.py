"""
Fess Integration Service - Fallback para Google CSE
Integra o Fess como sistema de busca local quando Google CSE falha
Compatível com Fess 14.x
"""

import os
import requests
import json
import logging
import time
from typing import Dict, List, Optional, Any
from urllib.parse import quote_plus, urljoin

class FessIntegration:
    def __init__(self, fess_url: str = "http://localhost:8080"):
        """
        Inicializa a integração com Fess
        
        Args:
            fess_url: URL base do servidor Fess
        """
        self.fess_url = fess_url.rstrip('/')
        # Para Fess 14.x, o endpoint correto é /json
        self.search_endpoint = f"{self.fess_url}/json"
        self.admin_endpoint = f"{self.fess_url}/admin"
        self.logger = logging.getLogger(__name__)
        
        # Carregar configuração se existir
        self._load_config()
        
        # Configurações padrão
        self.default_params = {
            'num': getattr(self, 'max_results', 10),
            'start': 0,
            'q': '',
        }
    
    def _load_config(self):
        """Carrega configuração do arquivo fess_config.json"""
        
        try:
            # Procurar arquivo de configuração na raiz do projeto
            current_dir = os.path.dirname(__file__)
            config_paths = [
                os.path.join(current_dir, "..", "..", "fess_config.json"),
                os.path.join(os.getcwd(), "fess_config.json"),
                "fess_config.json"
            ]
            
            config_loaded = False
            for config_file in config_paths:
                config_file = os.path.abspath(config_file)
                if os.path.exists(config_file):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    self.fess_url = config.get('fess_url', self.fess_url).rstrip('/')
                    self.search_endpoint = config.get('fess_api_url', f"{self.fess_url}/json").rstrip('/')
                    self.admin_endpoint = config.get('fess_admin_url', f"{self.fess_url}/admin").rstrip('/')
                    
                    self.timeout = config.get('timeout', 15)
                    self.max_results = config.get('max_results', 10)
                    self.auto_start = config.get('auto_start', True)
                    self.fess_version = config.get('fess_version', 'unknown')
                    
                    self.logger.info(f"✅ Configuração Fess carregada: {config_file}")
                    self.logger.info(f"📡 Endpoint API: {self.search_endpoint}")
                    self.logger.info(f"🔢 Versão Fess: {self.fess_version}")
                    config_loaded = True
                    break
            
            if not config_loaded:
                self.logger.debug("⚠️ Arquivo fess_config.json não encontrado, usando configuração padrão")
                self.timeout = 15
                self.max_results = 10
                self.auto_start = True
                self.fess_version = 'unknown'
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar configuração Fess: {e}")
            self.timeout = 15
            self.max_results = 10
            self.auto_start = True
            self.fess_version = 'unknown'
    
    def is_available(self) -> bool:
        """
        Verifica se o Fess está disponível
        
        Returns:
            bool: True se Fess estiver disponível
        """
        try:
            # Testa o endpoint principal
            response = requests.get(self.fess_url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.debug(f"Fess não disponível: {e}")
            return False
    
    def search(self, query: str, num_results: int = 10, start: int = 0) -> Dict[str, Any]:
        """
        Realiza busca no Fess com tratamento completo de erros
        """
        try:
            # Verifica se o Fess está disponível
            if not self.is_available():
                self.logger.warning("🔴 Fess não está disponível")
                return self._create_fallback_results(query)
            
            # Parâmetros para Fess 14.x endpoint /json
            params = {
                'q': query,
                'num': min(num_results, 100),
                'start': start,
            }
            
            # CRÍTICO: Para endpoint /json do Fess 14.x, NÃO use application/json
            # Use form data ou deixe o requests usar o padrão
            headers = {
                'Accept': '*/*',  # Aceita qualquer resposta
            }
            
            self.logger.debug(f"🔍 Fess request: {self.search_endpoint}")
            self.logger.debug(f"📋 Params: {params}")
            
            # Requisição GET com params na URL
            response = requests.get(
                self.search_endpoint, 
                params=params, 
                headers=headers,
                timeout=self.timeout
            )
            
            self.logger.debug(f"📥 Fess status: {response.status_code}")
            self.logger.debug(f"📄 Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            
            # Verifica se a resposta está vazia
            if not response.text.strip():
                self.logger.warning("⚠️ Fess retornou resposta vazia")
                return self._create_fallback_results(query)
            
            # Verifica status HTTP
            if response.status_code != 200:
                self.logger.warning(f"⚠️ Fess retornou status {response.status_code}")
                self.logger.debug(f"Response: {response.text[:500]}")
                return self._create_fallback_results(query)
            
            # Detecta se é HTML (página de erro)
            if response.text.strip().startswith('<!DOCTYPE') or response.text.strip().startswith('<html'):
                self.logger.error("❌ Fess retornou HTML em vez de JSON")
                self.logger.error("💡 Possíveis causas:")
                self.logger.error("   1. Nenhum documento indexado no Fess")
                self.logger.error("   2. Índice não criado ou crawler não executado")
                self.logger.error("   3. Serviço Elasticsearch não está rodando")
                self.logger.error(f"🔧 Acesse: {self.admin_endpoint} e verifique o status")
                return self._create_fallback_results(query, "No documents indexed")
            
            # Tenta parsear o JSON
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.logger.error(f"❌ Fess retornou JSON inválido: {str(e)}")
                self.logger.debug(f"📄 Response text: {response.text[:500]}")
                return self._create_fallback_results(query)
            
            # Verifica estrutura da resposta
            if not isinstance(data, dict):
                self.logger.warning(f"⚠️ Estrutura inesperada: não é um dict")
                return self._create_fallback_results(query)
            
            # Fess 14.x pode retornar estruturas diferentes
            # Estrutura 1: {response: {status: 0, result: [...]}}
            # Estrutura 2: {data: [...], recordCount: N}
            # Estrutura 3: Direto array de resultados
            
            has_results = False
            if 'response' in data:
                response_data = data['response']
                if isinstance(response_data, dict):
                    status = response_data.get('status', -1)
                    if status == 0:
                        has_results = True
                    else:
                        self.logger.warning(f"⚠️ Fess status: {status}")
            elif 'data' in data or 'result' in data or isinstance(data, list):
                has_results = True
            
            if not has_results:
                self.logger.info(f"ℹ️ Nenhum resultado encontrado para: {query}")
                return self._create_fallback_results(query, "No results found")
            
            # Formatar resultados
            formatted_results = self._format_search_results(data, query)
            
            result_count = len(formatted_results.get('items', []))
            self.logger.info(f"✅ Fess search successful: {result_count} results")
            
            return formatted_results
            
        except requests.exceptions.Timeout:
            self.logger.error("⏱️ Timeout na conexão com Fess")
            return self._create_fallback_results(query)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"🔌 Erro de conexão com Fess: {e}")
            return self._create_fallback_results(query)
        except Exception as e:
            self.logger.error(f"💥 Erro inesperado na busca Fess: {e}", exc_info=True)
            return self._create_fallback_results(query)
    
    def _format_search_results(self, fess_data: Dict, query: str) -> Dict[str, Any]:
        """
        Formata resultados do Fess 14.x para compatibilidade com Google CSE
        """
        items = []
        total_results = 0
        exec_time = 0.1
        
        # Detecta estrutura da resposta
        results = []
        
        # Estrutura 1: {response: {status: 0, result: [...], record_count: N}}
        if 'response' in fess_data:
            response_data = fess_data['response']
            if isinstance(response_data, dict):
                results = response_data.get('result', [])
                total_results = response_data.get('record_count', len(results))
                exec_time = response_data.get('exec_time', 0.1)
        
        # Estrutura 2: {data: [...], recordCount: N}
        elif 'data' in fess_data:
            results = fess_data.get('data', [])
            total_results = fess_data.get('recordCount', len(results))
        
        # Estrutura 3: {result: [...]}
        elif 'result' in fess_data:
            results = fess_data.get('result', [])
            total_results = fess_data.get('record_count', len(results))
        
        # Estrutura 4: Array direto
        elif isinstance(fess_data, list):
            results = fess_data
            total_results = len(results)
        
        self.logger.debug(f"📊 Processando {len(results)} resultados do Fess")
        
        for idx, result in enumerate(results):
            if not isinstance(result, dict):
                continue
            
            # Extrai campos do resultado
            title = (
                result.get('title') or 
                result.get('doc_title') or 
                result.get('name') or
                f'Documento {idx + 1}'
            )
            
            url = (
                result.get('url') or 
                result.get('doc_id') or 
                result.get('link') or
                ''
            )
            
            # Snippet: tenta vários campos possíveis
            snippet = (
                result.get('content_description') or
                result.get('description') or 
                result.get('content') or
                result.get('digest') or
                result.get('body') or
                ''
            )
            
            # Limita tamanho do snippet
            if len(snippet) > 300:
                snippet = snippet[:297] + '...'
            
            # Host/domain
            display_link = result.get('site') or result.get('host') or ''
            if not display_link and url:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(url)
                    display_link = parsed.netloc or parsed.path.split('/')[0]
                except:
                    pass
            
            item = {
                'title': title,
                'link': url,
                'snippet': snippet,
                'displayLink': display_link,
                'formattedUrl': url,
                'htmlTitle': title,
                'htmlSnippet': snippet,
                'cacheId': result.get('doc_id', result.get('id', str(idx))),
                'fileFormat': result.get('mimetype', result.get('filetype', 'text/html')),
                'source': 'fess',
                'score': result.get('score', 0),
                'last_modified': result.get('last_modified', result.get('timestamp', ''))
            }
            
            items.append(item)
        
        return {
            'kind': 'customsearch#search',
            'url': {
                'type': 'application/json',
                'template': f'{self.search_endpoint}?q={quote_plus(query)}'
            },
            'queries': {
                'request': [{
                    'title': 'Fess Search',
                    'totalResults': str(total_results),
                    'searchTerms': query,
                    'count': len(items),
                    'startIndex': 1,
                    'inputEncoding': 'utf8',
                    'outputEncoding': 'utf8'
                }]
            },
            'searchInformation': {
                'searchTime': exec_time,
                'formattedSearchTime': f"{exec_time:.2f}",
                'totalResults': str(total_results),
                'formattedTotalResults': str(total_results)
            },
            'items': items,
            'provider': 'fess',
            'fallback_mode': False
        }
    
    def _create_fallback_results(self, query: str, reason: str = 'Service unavailable') -> Dict[str, Any]:
        """
        Cria resultados de fallback quando Fess falha
        """
        return {
            'kind': 'customsearch#search',
            'queries': {
                'request': [{
                    'title': 'Fess Search (Fallback)',
                    'totalResults': '0',
                    'searchTerms': query,
                    'count': 0,
                    'startIndex': 1
                }]
            },
            'searchInformation': {
                'searchTime': 0.1,
                'formattedSearchTime': '0.10',
                'totalResults': '0',
                'formattedTotalResults': '0'
            },
            'items': [],
            'provider': 'fess_fallback',
            'fallback_mode': True,
            'error': reason
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtém status do Fess
        """
        try:
            if not self.is_available():
                return {
                    'status': 'offline',
                    'message': 'Fess service is not available',
                    'fess_url': self.fess_url,
                    'check': f'Verifique se o Fess está rodando em {self.fess_url}'
                }
            
            # Fazer uma busca de teste
            headers = {'Accept': '*/*'}
            
            test_response = requests.get(
                self.search_endpoint, 
                params={'q': '*', 'num': 1}, 
                headers=headers,
                timeout=10
            )
            
            if test_response.status_code == 200:
                # Verifica se retornou HTML ou JSON
                if test_response.text.strip().startswith('<!DOCTYPE') or test_response.text.strip().startswith('<html'):
                    return {
                        'status': 'online_no_index',
                        'message': 'Fess está rodando mas nenhum documento indexado',
                        'search_endpoint': self.search_endpoint,
                        'admin_endpoint': self.admin_endpoint,
                        'action': f'Acesse {self.admin_endpoint} para configurar crawlers e indexar documentos'
                    }
                
                try:
                    data = test_response.json()
                    
                    # Tenta contar documentos
                    total_docs = 0
                    if 'response' in data and isinstance(data['response'], dict):
                        total_docs = data['response'].get('record_count', 0)
                    elif 'recordCount' in data:
                        total_docs = data.get('recordCount', 0)
                    
                    return {
                        'status': 'online',
                        'message': 'Fess service is running',
                        'total_documents': total_docs,
                        'search_endpoint': self.search_endpoint,
                        'admin_endpoint': self.admin_endpoint,
                        'version': self.fess_version
                    }
                except json.JSONDecodeError:
                    return {
                        'status': 'online_unknown',
                        'message': 'Fess está rodando mas retornou resposta inesperada',
                        'search_endpoint': self.search_endpoint
                    }
            else:
                return {
                    'status': 'api_error',
                    'message': f'API returned status: {test_response.status_code}',
                    'search_endpoint': self.search_endpoint,
                    'response_preview': test_response.text[:200]
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error checking Fess status: {str(e)}',
                'search_endpoint': self.search_endpoint,
                'fess_url': self.fess_url
            }

# Instância global para uso em outros módulos
fess_client = FessIntegration()

def search_with_fess_fallback(query: str, num_results: int = 10) -> Dict[str, Any]:
    """
    Função utilitária para busca com Fess como fallback
    """
    return fess_client.search(query, num_results)

def is_fess_available() -> bool:
    """
    Função utilitária para verificar disponibilidade do Fess
    """
    return fess_client.is_available()
