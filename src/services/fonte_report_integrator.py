#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV40 Enhanced - Integrador de Relatório de Fontes
Integra os serviços de coleta e verificação de fontes no relatório final
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from .fonte_collection_service import FonteCollectionService, FonteColetada
from .fonte_verification_service import FonteVerificationService, FonteAnalise

logger = logging.getLogger(__name__)

class FonteReportIntegrator:
    """Integrador de relatórios de fontes para o relatório final"""
    
    def __init__(self):
        """Inicializa o integrador"""
        self.fonte_collector = FonteCollectionService()
        self.fonte_verifier = FonteVerificationService()
        
    def generate_resumo_ia_verificacao_module(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera módulo de Resumo da IA - Verificação de Fontes
        
        Args:
            session_data: Dados da sessão de análise
            
        Returns:
            Dados do módulo formatados para o relatório
        """
        try:
            # Coleta estatísticas de verificação
            fontes_aprovadas = self.fonte_verifier.fontes_aprovadas
            fontes_rejeitadas = self.fonte_verifier.fontes_rejeitadas
            fontes_pendentes = self.fonte_verifier.fontes_pendentes
            
            total_fontes = len(fontes_aprovadas) + len(fontes_rejeitadas) + len(fontes_pendentes)
            
            # Calcula métricas
            taxa_aprovacao = (len(fontes_aprovadas) / total_fontes * 100) if total_fontes > 0 else 0
            taxa_rejeicao = (len(fontes_rejeitadas) / total_fontes * 100) if total_fontes > 0 else 0
            
            # Análise por categoria
            categorias_aprovadas = {}
            categorias_rejeitadas = {}
            
            for fonte in fontes_aprovadas:
                categoria = fonte.categoria
                if categoria not in categorias_aprovadas:
                    categorias_aprovadas[categoria] = 0
                categorias_aprovadas[categoria] += 1
            
            for fonte in fontes_rejeitadas:
                categoria = fonte.categoria
                if categoria not in categorias_rejeitadas:
                    categorias_rejeitadas[categoria] = 0
                categorias_rejeitadas[categoria] += 1
            
            # Principais motivos de rejeição
            motivos_rejeicao = {}
            for fonte in fontes_rejeitadas:
                motivo = fonte.motivo_status
                if motivo not in motivos_rejeicao:
                    motivos_rejeicao[motivo] = 0
                motivos_rejeicao[motivo] += 1
            
            # Gera conteúdo HTML
            content = self._generate_verificacao_html(
                total_fontes, taxa_aprovacao, taxa_rejeicao,
                categorias_aprovadas, categorias_rejeitadas, motivos_rejeicao,
                fontes_aprovadas[:10], fontes_rejeitadas[:5]  # Top 10 aprovadas, top 5 rejeitadas
            )
            
            return {
                'title': 'Resumo da IA - Verificação de Fontes',
                'content': content,
                'metadata': {
                    'total_fontes': total_fontes,
                    'fontes_aprovadas': len(fontes_aprovadas),
                    'fontes_rejeitadas': len(fontes_rejeitadas),
                    'fontes_pendentes': len(fontes_pendentes),
                    'taxa_aprovacao': round(taxa_aprovacao, 2),
                    'taxa_rejeicao': round(taxa_rejeicao, 2),
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar módulo de verificação: {e}")
            return {
                'title': 'Resumo da IA - Verificação de Fontes',
                'content': f'<div class="error">Erro ao gerar relatório de verificação: {str(e)}</div>',
                'metadata': {'error': str(e)}
            }
    
    def generate_fontes_coletadas_module(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera módulo de Fontes Coletadas e Analisadas
        
        Args:
            session_data: Dados da sessão de análise
            
        Returns:
            Dados do módulo formatados para o relatório
        """
        try:
            fontes_coletadas = self.fonte_collector.fontes_coletadas
            
            # Organiza fontes por categoria
            fontes_por_categoria = {}
            for fonte in fontes_coletadas:
                categoria = fonte.categoria
                if categoria not in fontes_por_categoria:
                    fontes_por_categoria[categoria] = []
                fontes_por_categoria[categoria].append(fonte)
            
            # Organiza fontes por tipo
            fontes_por_tipo = {}
            for fonte in fontes_coletadas:
                tipo = fonte.tipo
                if tipo not in fontes_por_tipo:
                    fontes_por_tipo[tipo] = []
                fontes_por_tipo[tipo].append(fonte)
            
            # Estatísticas de relevância
            relevancia_stats = {'alta': 0, 'media': 0, 'baixa': 0}
            for fonte in fontes_coletadas:
                if fonte.relevancia in relevancia_stats:
                    relevancia_stats[fonte.relevancia] += 1
            
            # Gera conteúdo HTML
            content = self._generate_fontes_coletadas_html(
                fontes_coletadas, fontes_por_categoria, fontes_por_tipo, relevancia_stats
            )
            
            return {
                'title': 'Fontes Coletadas e Analisadas',
                'content': content,
                'metadata': {
                    'total_fontes': len(fontes_coletadas),
                    'categorias': list(fontes_por_categoria.keys()),
                    'tipos': list(fontes_por_tipo.keys()),
                    'relevancia_stats': relevancia_stats,
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar módulo de fontes coletadas: {e}")
            return {
                'title': 'Fontes Coletadas e Analisadas',
                'content': f'<div class="error">Erro ao gerar relatório de fontes: {str(e)}</div>',
                'metadata': {'error': str(e)}
            }
    
    def _generate_verificacao_html(self, total_fontes: int, taxa_aprovacao: float, taxa_rejeicao: float,
                                 categorias_aprovadas: Dict, categorias_rejeitadas: Dict, 
                                 motivos_rejeicao: Dict, top_aprovadas: List, top_rejeitadas: List) -> str:
        """Gera HTML para o módulo de verificação"""
        
        html = f"""
        <div class="fonte-verification-module">
            <div class="verification-summary">
                <h3>📊 Resumo da Verificação Automática</h3>
                <div class="stats-grid">
                    <div class="stat-card approved">
                        <div class="stat-number">{total_fontes}</div>
                        <div class="stat-label">Total de Fontes Analisadas</div>
                    </div>
                    <div class="stat-card success">
                        <div class="stat-number">{taxa_aprovacao:.1f}%</div>
                        <div class="stat-label">Taxa de Aprovação</div>
                    </div>
                    <div class="stat-card warning">
                        <div class="stat-number">{taxa_rejeicao:.1f}%</div>
                        <div class="stat-label">Taxa de Rejeição</div>
                    </div>
                </div>
            </div>
            
            <div class="verification-details">
                <div class="row">
                    <div class="col-md-6">
                        <h4>✅ Fontes Aprovadas por Categoria</h4>
                        <div class="category-list">
        """
        
        for categoria, count in sorted(categorias_aprovadas.items(), key=lambda x: x[1], reverse=True):
            html += f"""
                            <div class="category-item approved">
                                <span class="category-name">{categoria.title()}</span>
                                <span class="category-count">{count}</span>
                            </div>
            """
        
        html += """
                        </div>
                    </div>
                    <div class="col-md-6">
                        <h4>❌ Fontes Rejeitadas por Categoria</h4>
                        <div class="category-list">
        """
        
        for categoria, count in sorted(categorias_rejeitadas.items(), key=lambda x: x[1], reverse=True):
            html += f"""
                            <div class="category-item rejected">
                                <span class="category-name">{categoria.title()}</span>
                                <span class="category-count">{count}</span>
                            </div>
            """
        
        html += """
                        </div>
                    </div>
                </div>
                
                <div class="rejection-reasons">
                    <h4>🔍 Principais Motivos de Rejeição</h4>
                    <div class="reasons-list">
        """
        
        for motivo, count in sorted(motivos_rejeicao.items(), key=lambda x: x[1], reverse=True)[:5]:
            html += f"""
                        <div class="reason-item">
                            <span class="reason-text">{motivo}</span>
                            <span class="reason-count">{count} fontes</span>
                        </div>
            """
        
        html += """
                    </div>
                </div>
                
                <div class="top-sources">
                    <h4>🏆 Top Fontes Aprovadas</h4>
                    <div class="sources-list">
        """
        
        for fonte in top_aprovadas:
            html += f"""
                        <div class="source-item approved">
                            <div class="source-header">
                                <span class="source-title">{fonte.titulo}</span>
                                <span class="source-relevance relevance-{fonte.relevancia}">{fonte.relevancia.upper()}</span>
                            </div>
                            <div class="source-details">
                                <span class="source-type">{fonte.tipo}</span>
                                <span class="source-category">{fonte.categoria}</span>
                                <a href="{fonte.url}" target="_blank" class="source-link">Ver Fonte</a>
                            </div>
                        </div>
            """
        
        html += """
                    </div>
                </div>
            </div>
        </div>
        
        <style>
        .fonte-verification-module {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 24px;
            margin: 20px 0;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 8px;
        }
        
        .stat-card.approved .stat-number { color: #007bff; }
        .stat-card.success .stat-number { color: #28a745; }
        .stat-card.warning .stat-number { color: #ffc107; }
        
        .category-item, .reason-item, .source-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            margin: 8px 0;
            border-radius: 6px;
            background: white;
        }
        
        .category-item.approved { border-left: 4px solid #28a745; }
        .category-item.rejected { border-left: 4px solid #dc3545; }
        
        .source-item {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .source-header {
            display: flex;
            justify-content: space-between;
            width: 100%;
            margin-bottom: 8px;
        }
        
        .source-relevance {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .relevance-alta { background: #28a745; color: white; }
        .relevance-media { background: #ffc107; color: black; }
        .relevance-baixa { background: #6c757d; color: white; }
        
        .source-details {
            display: flex;
            gap: 16px;
            font-size: 0.9rem;
            color: #6c757d;
        }
        
        .source-link {
            color: #007bff;
            text-decoration: none;
        }
        </style>
        """
        
        return html
    
    def _generate_fontes_coletadas_html(self, fontes: List[FonteColetada], 
                                      por_categoria: Dict, por_tipo: Dict, 
                                      relevancia_stats: Dict) -> str:
        """Gera HTML para o módulo de fontes coletadas"""
        
        html = f"""
        <div class="fontes-coletadas-module">
            <div class="collection-summary">
                <h3>📚 Fontes Coletadas Durante a Análise</h3>
                <div class="summary-stats">
                    <div class="stat-item">
                        <span class="stat-value">{len(fontes)}</span>
                        <span class="stat-label">Total de Fontes</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{len(por_categoria)}</span>
                        <span class="stat-label">Categorias</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">{len(por_tipo)}</span>
                        <span class="stat-label">Tipos de Fonte</span>
                    </div>
                </div>
            </div>
            
            <div class="relevance-distribution">
                <h4>📈 Distribuição por Relevância</h4>
                <div class="relevance-bars">
                    <div class="relevance-bar">
                        <span class="relevance-label">Alta Relevância</span>
                        <div class="bar-container">
                            <div class="bar alta" style="width: {(relevancia_stats['alta']/len(fontes)*100) if fontes else 0}%"></div>
                            <span class="bar-value">{relevancia_stats['alta']}</span>
                        </div>
                    </div>
                    <div class="relevance-bar">
                        <span class="relevance-label">Média Relevância</span>
                        <div class="bar-container">
                            <div class="bar media" style="width: {(relevancia_stats['media']/len(fontes)*100) if fontes else 0}%"></div>
                            <span class="bar-value">{relevancia_stats['media']}</span>
                        </div>
                    </div>
                    <div class="relevance-bar">
                        <span class="relevance-label">Baixa Relevância</span>
                        <div class="bar-container">
                            <div class="bar baixa" style="width: {(relevancia_stats['baixa']/len(fontes)*100) if fontes else 0}%"></div>
                            <span class="bar-value">{relevancia_stats['baixa']}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="sources-by-category">
                <h4>🏷️ Fontes por Categoria</h4>
                <div class="category-tabs">
        """
        
        for categoria, fontes_categoria in por_categoria.items():
            html += f"""
                    <div class="category-section">
                        <h5>{categoria.title()} ({len(fontes_categoria)} fontes)</h5>
                        <div class="sources-grid">
            """
            
            for fonte in fontes_categoria[:10]:  # Máximo 10 por categoria
                html += f"""
                            <div class="source-card">
                                <div class="source-header">
                                    <span class="source-type-badge {fonte.tipo}">{fonte.tipo.upper()}</span>
                                    <span class="relevance-badge {fonte.relevancia}">{fonte.relevancia.upper()}</span>
                                </div>
                                <h6 class="source-title">{fonte.titulo[:60]}{'...' if len(fonte.titulo) > 60 else ''}</h6>
                                <p class="source-description">{fonte.descricao[:100]}{'...' if len(fonte.descricao) > 100 else ''}</p>
                                <div class="source-footer">
                                    <a href="{fonte.url}" target="_blank" class="source-link">
                                        <i class="fas fa-external-link-alt"></i> Ver Fonte
                                    </a>
                                    <span class="source-date">{fonte.data_coleta[:10]}</span>
                                </div>
                            </div>
                """
            
            html += """
                        </div>
                    </div>
            """
        
        html += """
                </div>
            </div>
            
            <div class="collection-insights">
                <h4>💡 Insights da Coleta</h4>
                <div class="insights-grid">
        """
        
        # Insights automáticos
        total_fontes = len(fontes)
        if total_fontes > 0:
            # Tipo mais comum
            tipo_mais_comum = max(por_tipo.items(), key=lambda x: len(x[1]))
            categoria_mais_comum = max(por_categoria.items(), key=lambda x: len(x[1]))
            
            html += f"""
                    <div class="insight-card">
                        <h6>📊 Tipo de Fonte Predominante</h6>
                        <p><strong>{tipo_mais_comum[0].title()}</strong> representa {len(tipo_mais_comum[1])/total_fontes*100:.1f}% das fontes coletadas</p>
                    </div>
                    <div class="insight-card">
                        <h6>🎯 Categoria Mais Relevante</h6>
                        <p><strong>{categoria_mais_comum[0].title()}</strong> com {len(categoria_mais_comum[1])} fontes identificadas</p>
                    </div>
                    <div class="insight-card">
                        <h6>⭐ Qualidade das Fontes</h6>
                        <p>{relevancia_stats['alta']} fontes de alta relevância ({relevancia_stats['alta']/total_fontes*100:.1f}%)</p>
                    </div>
            """
        
        html += """
                </div>
            </div>
        </div>
        
        <style>
        .fontes-coletadas-module {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 24px;
            margin: 20px 0;
        }
        
        .summary-stats {
            display: flex;
            gap: 24px;
            margin: 20px 0;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            display: block;
            font-size: 2rem;
            font-weight: bold;
            color: #007bff;
        }
        
        .relevance-bars {
            margin: 16px 0;
        }
        
        .relevance-bar {
            display: flex;
            align-items: center;
            margin: 12px 0;
            gap: 16px;
        }
        
        .relevance-label {
            min-width: 120px;
            font-weight: 500;
        }
        
        .bar-container {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .bar {
            height: 20px;
            border-radius: 10px;
            min-width: 4px;
        }
        
        .bar.alta { background: #28a745; }
        .bar.media { background: #ffc107; }
        .bar.baixa { background: #6c757d; }
        
        .sources-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
            margin: 16px 0;
        }
        
        .source-card {
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .source-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 12px;
        }
        
        .source-type-badge, .relevance-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
        }
        
        .source-type-badge.youtube { background: #ff0000; color: white; }
        .source-type-badge.instagram { background: #e4405f; color: white; }
        .source-type-badge.linkedin { background: #0077b5; color: white; }
        .source-type-badge.website { background: #6c757d; color: white; }
        
        .source-title {
            font-size: 1rem;
            font-weight: 600;
            margin: 8px 0;
            color: #333;
        }
        
        .source-description {
            font-size: 0.9rem;
            color: #666;
            margin: 8px 0;
        }
        
        .source-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #eee;
        }
        
        .source-link {
            color: #007bff;
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .source-date {
            font-size: 0.8rem;
            color: #999;
        }
        
        .insights-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 16px;
            margin: 16px 0;
        }
        
        .insight-card {
            background: white;
            border-radius: 8px;
            padding: 16px;
            border-left: 4px solid #007bff;
        }
        
        .insight-card h6 {
            margin: 0 0 8px 0;
            color: #007bff;
        }
        
        .insight-card p {
            margin: 0;
            font-size: 0.9rem;
        }
        </style>
        """
        
        return html

# Instância global
fonte_report_integrator = FonteReportIntegrator()