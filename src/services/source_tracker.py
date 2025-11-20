"""
Sistema de Rastreamento e Citação de Fontes
Implementa tracking completo de origem de dados com metadados
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import re

@dataclass
class SourceMetadata:
    """Estrutura de dados para metadados de fonte"""
    url: str
    title: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None
    access_date: str = None
    domain: str = None
    content_type: str = "web"  # web, pdf, api, database
    reliability_score: float = 0.5  # 0.0 a 1.0
    verification_status: str = "pending"  # verified, pending, unverified
    source_hash: str = None
    
    def __post_init__(self):
        if not self.access_date:
            self.access_date = datetime.now().isoformat()
        if not self.domain and self.url:
            self.domain = urlparse(self.url).netloc
        if not self.source_hash:
            self.source_hash = hashlib.md5(self.url.encode()).hexdigest()[:8]

@dataclass
class CitationData:
    """Dados de citação para uma informação específica"""
    content: str
    source_metadata: SourceMetadata
    confidence_level: str = "medium"  # high, medium, low
    data_type: str = "general"  # numerical, textual, statistical, projection
    footnote_id: int = None
    tags: List[str] = None
    
    def __post_init__(self):
        if not self.tags:
            self.tags = []

class SourceTracker:
    """Sistema principal de rastreamento de fontes"""
    
    def __init__(self):
        self.sources: Dict[str, SourceMetadata] = {}
        self.citations: List[CitationData] = []
        self.footnote_counter = 0
        self.reliability_thresholds = {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.3
        }
        
        # Domínios confiáveis com scores pré-definidos
        self.trusted_domains = {
            'gov.br': 0.95,
            'ibge.gov.br': 0.95,
            'bcb.gov.br': 0.95,
            'sebrae.com.br': 0.85,
            'estadao.com.br': 0.75,
            'folha.uol.com.br': 0.75,
            'g1.globo.com': 0.75,
            'reuters.com': 0.90,
            'bloomberg.com': 0.90,
            'forbes.com': 0.80,
            'harvard.edu': 0.95,
            'mit.edu': 0.95,
            'wikipedia.org': 0.60,
            'linkedin.com': 0.50,
            'medium.com': 0.40,
            'blog': 0.30
        }
    
    def add_source(self, url: str, **kwargs) -> str:
        """Adiciona uma nova fonte ao sistema"""
        metadata = SourceMetadata(url=url, **kwargs)
        
        # Calcula score de confiabilidade baseado no domínio
        metadata.reliability_score = self._calculate_reliability_score(metadata.domain)
        
        # Armazena a fonte
        self.sources[metadata.source_hash] = metadata
        
        return metadata.source_hash
    
    def add_citation(self, content: str, source_hash: str, **kwargs) -> int:
        """Adiciona uma citação vinculada a uma fonte"""
        if source_hash not in self.sources:
            raise ValueError(f"Fonte {source_hash} não encontrada")
        
        self.footnote_counter += 1
        
        citation = CitationData(
            content=content,
            source_metadata=self.sources[source_hash],
            footnote_id=self.footnote_counter,
            **kwargs
        )
        
        self.citations.append(citation)
        return self.footnote_counter
    
    def _calculate_reliability_score(self, domain: str) -> float:
        """Calcula score de confiabilidade baseado no domínio"""
        if not domain:
            return 0.3
        
        domain_lower = domain.lower()
        
        # Verifica domínios exatos
        for trusted_domain, score in self.trusted_domains.items():
            if trusted_domain in domain_lower:
                return score
        
        # Verifica padrões
        if any(pattern in domain_lower for pattern in ['.gov', '.edu', '.org']):
            return 0.85
        elif any(pattern in domain_lower for pattern in ['blog', 'wordpress', 'blogspot']):
            return 0.30
        elif any(pattern in domain_lower for pattern in ['news', 'jornal', 'revista']):
            return 0.70
        else:
            return 0.50
    
    def get_confidence_level(self, reliability_score: float) -> str:
        """Determina nível de confiança baseado no score"""
        if reliability_score >= self.reliability_thresholds['high']:
            return 'high'
        elif reliability_score >= self.reliability_thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    def generate_footnotes_html(self) -> str:
        """Gera HTML das notas de rodapé"""
        if not self.citations:
            return ""
        
        html = ['<div class="footnotes-section">']
        html.append('<h3>📚 Referências e Fontes</h3>')
        html.append('<ol class="footnotes-list">')
        
        for citation in sorted(self.citations, key=lambda x: x.footnote_id):
            source = citation.source_metadata
            confidence_class = f"confidence-{citation.confidence_level}"
            
            html.append(f'<li id="footnote-{citation.footnote_id}" class="footnote-item {confidence_class}">')
            
            # Título e link
            if source.title:
                html.append(f'<strong>{source.title}</strong>')
            else:
                html.append(f'<strong>{source.domain}</strong>')
            
            # Autor se disponível
            if source.author:
                html.append(f' - {source.author}')
            
            # Data de publicação
            if source.publication_date:
                html.append(f' ({source.publication_date})')
            
            # Link clicável
            html.append(f' <a href="{source.url}" target="_blank" class="source-link">🔗 Acessar fonte</a>')
            
            # Indicador de confiabilidade
            reliability_icon = self._get_reliability_icon(source.reliability_score)
            html.append(f' <span class="reliability-indicator">{reliability_icon}</span>')
            
            # Data de acesso
            access_date = datetime.fromisoformat(source.access_date).strftime('%d/%m/%Y')
            html.append(f' <small class="access-date">Acessado em: {access_date}</small>')
            
            html.append('</li>')
        
        html.append('</ol>')
        html.append('</div>')
        
        return '\n'.join(html)
    
    def _get_reliability_icon(self, score: float) -> str:
        """Retorna ícone baseado no score de confiabilidade"""
        if score >= 0.8:
            return '🟢 Alta confiabilidade'
        elif score >= 0.5:
            return '🟡 Média confiabilidade'
        else:
            return '🔴 Baixa confiabilidade'
    
    def generate_inline_citation(self, footnote_id: int) -> str:
        """Gera citação inline para inserir no texto"""
        return f'<sup><a href="#footnote-{footnote_id}" class="footnote-link">[{footnote_id}]</a></sup>'
    
    def get_sources_summary(self) -> Dict[str, Any]:
        """Retorna resumo das fontes utilizadas"""
        if not self.sources:
            return {}
        
        total_sources = len(self.sources)
        reliability_distribution = {'high': 0, 'medium': 0, 'low': 0}
        
        for source in self.sources.values():
            confidence = self.get_confidence_level(source.reliability_score)
            reliability_distribution[confidence] += 1
        
        return {
            'total_sources': total_sources,
            'reliability_distribution': reliability_distribution,
            'average_reliability': sum(s.reliability_score for s in self.sources.values()) / total_sources,
            'domains_used': list(set(s.domain for s in self.sources.values() if s.domain))
        }
    
    def generate_sources_css(self) -> str:
        """Gera CSS para estilização das fontes"""
        return """
        <style>
        .footnotes-section {
            margin-top: 40px;
            padding: 20px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 5px;
        }
        
        .footnotes-section h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .footnotes-list {
            list-style-type: decimal;
            padding-left: 20px;
        }
        
        .footnote-item {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 3px;
            line-height: 1.4;
        }
        
        .footnote-item.confidence-high {
            background-color: #d4edda;
            border-left: 3px solid #28a745;
        }
        
        .footnote-item.confidence-medium {
            background-color: #fff3cd;
            border-left: 3px solid #ffc107;
        }
        
        .footnote-item.confidence-low {
            background-color: #f8d7da;
            border-left: 3px solid #dc3545;
        }
        
        .source-link {
            color: #007bff;
            text-decoration: none;
            font-size: 0.9em;
        }
        
        .source-link:hover {
            text-decoration: underline;
        }
        
        .reliability-indicator {
            font-size: 0.8em;
            margin-left: 10px;
        }
        
        .access-date {
            color: #666;
            font-size: 0.8em;
            display: block;
            margin-top: 3px;
        }
        
        .footnote-link {
            color: #007bff;
            text-decoration: none;
            font-weight: bold;
        }
        
        .footnote-link:hover {
            text-decoration: underline;
        }
        
        .sources-summary {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .reliability-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin: 2px;
        }
        
        .reliability-high { background-color: #28a745; color: white; }
        .reliability-medium { background-color: #ffc107; color: black; }
        .reliability-low { background-color: #dc3545; color: white; }
        </style>
        """
    
    def export_sources_json(self) -> str:
        """Exporta todas as fontes em formato JSON"""
        data = {
            'sources': {k: asdict(v) for k, v in self.sources.items()},
            'citations': [asdict(c) for c in self.citations],
            'summary': self.get_sources_summary(),
            'export_date': datetime.now().isoformat()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def validate_sources(self) -> List[Dict[str, Any]]:
        """Valida todas as fontes e retorna problemas encontrados"""
        issues = []
        
        for source_hash, source in self.sources.items():
            # Verifica URL válida
            if not source.url or not source.url.startswith(('http://', 'https://')):
                issues.append({
                    'type': 'invalid_url',
                    'source_hash': source_hash,
                    'message': f'URL inválida: {source.url}'
                })
            
            # Verifica confiabilidade muito baixa
            if source.reliability_score < 0.3:
                issues.append({
                    'type': 'low_reliability',
                    'source_hash': source_hash,
                    'message': f'Fonte com confiabilidade muito baixa: {source.reliability_score}'
                })
            
            # Verifica fontes sem título
            if not source.title:
                issues.append({
                    'type': 'missing_title',
                    'source_hash': source_hash,
                    'message': 'Fonte sem título definido'
                })
        
        return issues

# Instância global do rastreador
source_tracker = SourceTracker()