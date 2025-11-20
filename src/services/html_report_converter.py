#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - HTML Report Converter
Conversor profissional de relatórios MD para HTML
Layout responsivo, cores corporativas, hierarquia visual
ZERO SIMULAÇÃO - Apenas conversões reais e funcionais
"""

import os
import logging
import json
import re
import html
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import markdown
from markdown.extensions import codehilite, tables, toc

logger = logging.getLogger(__name__)

class HTMLReportConverter:
    """
    Conversor profissional de relatórios MD para HTML
    Implementa design corporativo com layout responsivo
    """
    
    def __init__(self):
        """Inicializa o conversor HTML"""
        self.nome_modulo = "HTML Report Converter"
        self.versao = "3.0 Enhanced"
        
        # Configurações de design
        self.cores = {
            'primaria': '#0056b3',
            'secundaria': '#d9534f', 
            'fundo_claro': '#f8f9fa',
            'texto_principal': '#333333',
            'texto_secundario': '#666666',
            'borda': '#e0e0e0',
            'sucesso': '#28a745',
            'alerta': '#ffc107',
            'perigo': '#dc3545'
        }
        
        self.fontes = {
            'principal': "'Segoe UI', 'Open Sans', 'Helvetica Neue', sans-serif",
            'codigo': "'Consolas', 'Monaco', 'Courier New', monospace"
        }
    
    def _escape_html(self, text: str) -> str:
        """Escapa caracteres especiais HTML"""
        if not text:
            return ""
        return html.escape(str(text), quote=True)
    
    def _format_json_data(self, data: Any, max_depth: int = 3, current_depth: int = 0) -> str:
        """Formata dados JSON para exibição HTML estruturada"""
        
        if current_depth > max_depth:
            return "<span class='text-muted'>...</span>"
        
        if data is None:
            return "<span class='text-muted'>null</span>"
        
        if isinstance(data, bool):
            return f"<span class='text-{'success' if data else 'danger'}'>{str(data).lower()}</span>"
        
        if isinstance(data, (int, float)):
            return f"<span class='text-info'>{data}</span>"
        
        if isinstance(data, str):
            # Truncar strings muito longas
            if len(data) > 200:
                truncated = data[:197] + "..."
                return f"<span class='text-dark'>"{self._escape_html(truncated)}"</span>"
            return f"<span class='text-dark'>"{self._escape_html(data)}"</span>"
        
        if isinstance(data, list):
            if not data:
                return "<span class='text-muted'>[]</span>"
            
            items = []
            for i, item in enumerate(data[:10]):  # Limitar a 10 itens
                formatted_item = self._format_json_data(item, max_depth, current_depth + 1)
                items.append(f"<li class='list-group-item border-0 py-1'>{formatted_item}</li>")
            
            if len(data) > 10:
                items.append(f"<li class='list-group-item border-0 py-1 text-muted'>... e mais {len(data) - 10} itens</li>")
            
            return f"""
            <div class="json-array">
                <ul class="list-group list-group-flush">
                    {''.join(items)}
                </ul>
            </div>
            """
        
        if isinstance(data, dict):
            if not data:
                return "<span class='text-muted'>{}</span>"
            
            rows = []
            for key, value in list(data.items())[:15]:  # Limitar a 15 chaves
                formatted_value = self._format_json_data(value, max_depth, current_depth + 1)
                rows.append(f"""
                <tr>
                    <td class="fw-bold text-primary" style="width: 30%;">{self._escape_html(str(key))}</td>
                    <td>{formatted_value}</td>
                </tr>
                """)
            
            if len(data) > 15:
                rows.append(f"""
                <tr>
                    <td colspan="2" class="text-muted text-center">... e mais {len(data) - 15} propriedades</td>
                </tr>
                """)
            
            return f"""
            <div class="json-object">
                <table class="table table-sm table-borderless">
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </div>
            """
        
        # Fallback para outros tipos
        return f"<span class='text-secondary'>{self._escape_html(str(data))}</span>"
    
    def _render_json_section(self, title: str, data: Any, icon: str = "📊") -> str:
        """Renderiza uma seção com dados JSON formatados"""
        
        if not data:
            return f"""
            <div class="card mb-4">
                <div class="card-header bg-light">
                    <h5 class="mb-0">
                        <i class="me-2">{icon}</i>
                        {self._escape_html(title)}
                    </h5>
                </div>
                <div class="card-body">
                    <p class="text-muted">Nenhum dado disponível</p>
                </div>
            </div>
            """
        
        formatted_data = self._format_json_data(data)
        
        return f"""
        <div class="card mb-4">
            <div class="card-header bg-light">
                <h5 class="mb-0">
                    <i class="me-2">{icon}</i>
                    {self._escape_html(title)}
                </h5>
            </div>
            <div class="card-body">
                <div class="json-content">
                    {formatted_data}
                </div>
            </div>
        </div>
        """
        
        logger.info("🎨 HTML Report Converter inicializado")
    
    async def converter_relatorio_para_html(
        self,
        session_id: str,
        arquivo_md: str,
        configuracoes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Converte relatório MD para HTML profissional
        
        Args:
            session_id: ID da sessão
            arquivo_md: Caminho do arquivo MD ou conteúdo MD
            configuracoes: Configurações específicas de conversão
        """
        logger.info(f"🎨 Iniciando conversão HTML para sessão {session_id}")
        
        try:
            # Carregar conteúdo MD
            conteudo_md = await self._carregar_conteudo_md(arquivo_md)
            
            # Processar configurações
            config = configuracoes or {}
            titulo = config.get('titulo', 'Relatório de Análise')
            subtitulo = config.get('subtitulo', 'Análise Completa de Dados')
            
            # Gerar HTML completo
            html_completo = await self._gerar_html_completo(
                session_id, conteudo_md, titulo, subtitulo, config
            )
            
            # Salvar arquivo HTML
            arquivo_html = await self._salvar_arquivo_html(
                session_id, html_completo, config.get('nome_arquivo', 'relatorio')
            )
            
            logger.info(f"✅ Conversão HTML concluída para sessão {session_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'arquivo_html': arquivo_html,
                'tamanho_arquivo': len(html_completo),
                'timestamp': datetime.now().isoformat(),
                'configuracoes_aplicadas': config
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na conversão HTML: {e}")
            raise
    
    async def _carregar_conteudo_md(self, arquivo_md: str) -> str:
        """Carrega conteúdo do arquivo MD"""
        
        try:
            # Verificar se é caminho de arquivo ou conteúdo direto
            if os.path.exists(arquivo_md):
                with open(arquivo_md, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # Assumir que é conteúdo direto
                return arquivo_md
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar conteúdo MD: {e}")
            raise
    
    async def _gerar_html_completo(
        self,
        session_id: str,
        conteudo_md: str,
        titulo: str,
        subtitulo: str,
        config: Dict[str, Any]
    ) -> str:
        """Gera HTML completo com design profissional"""
        
        # Converter MD para HTML
        html_conteudo = self._converter_markdown_para_html(conteudo_md)
        
        # Processar conteúdo para melhorar visualização
        html_processado = await self._processar_conteudo_html(html_conteudo, session_id)
        
        # Gerar CSS personalizado
        css_personalizado = self._gerar_css_profissional()
        
        # Gerar JavaScript para interatividade
        js_interativo = self._gerar_javascript_interativo()
        
        # Montar HTML completo
        html_completo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{self._escape_html(titulo)}</title>
    <meta name="description" content="{self._escape_html(subtitulo)}">
    <meta name="generator" content="ARQV18 Enhanced v18.0">
    <meta name="robots" content="noindex, nofollow">
    <meta name="format-detection" content="telephone=no">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- CSS Personalizado -->
    <style>
        {css_personalizado}
    </style>
</head>
<body>
    <!-- Cabeçalho -->
    {self._gerar_cabecalho(titulo, subtitulo, session_id)}
    
    <!-- Conteúdo Principal -->
    <main class="container-fluid">
        <div class="row">
            <!-- Sidebar de Navegação -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar">
                {self._gerar_sidebar_navegacao(html_conteudo)}
            </nav>
            
            <!-- Conteúdo do Relatório -->
            <div class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                {html_processado}
            </div>
        </div>
    </main>
    
    <!-- Rodapé -->
    {self._gerar_rodape()}
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Chart.js para gráficos -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- JavaScript Personalizado -->
    <script>
        {js_interativo}
    </script>
</body>
</html>"""
        
        return html_completo
    
    def _converter_markdown_para_html(self, conteudo_md: str) -> str:
        """Converte Markdown para HTML usando extensões"""
        
        # Configurar extensões do Markdown
        extensoes = [
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.tables',
            'markdown.extensions.attr_list',
            'markdown.extensions.def_list'
        ]
        
        # Configurações das extensões
        config_extensoes = {
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True
            },
            'toc': {
                'permalink': True,
                'permalink_class': 'toc-link'
            }
        }
        
        # Converter
        md = markdown.Markdown(
            extensions=extensoes,
            extension_configs=config_extensoes
        )
        
        return md.convert(conteudo_md)
    
    async def _processar_conteudo_html(self, html_conteudo: str, session_id: str) -> str:
        """Processa HTML para melhorar visualização"""
        
        # Adicionar classes Bootstrap às tabelas
        html_conteudo = re.sub(
            r'<table>',
            '<table class="table table-striped table-hover">',
            html_conteudo
        )
        
        # Adicionar classes aos alertas/blocos especiais
        html_conteudo = re.sub(
            r'<blockquote>',
            '<blockquote class="blockquote alert alert-info">',
            html_conteudo
        )
        
        # Processar listas para melhor visualização
        html_conteudo = re.sub(
            r'<ul>',
            '<ul class="list-group list-group-flush">',
            html_conteudo
        )
        
        html_conteudo = re.sub(
            r'<li>',
            '<li class="list-group-item">',
            html_conteudo
        )
        
        # Adicionar cards para seções principais
        html_conteudo = self._adicionar_cards_secoes(html_conteudo)
        
        # Processar estatísticas e números
        html_conteudo = self._processar_estatisticas(html_conteudo)
        
        # Adicionar seção de imagens 1080x1080 se disponível
        html_conteudo = await self._adicionar_secao_imagens(html_conteudo, session_id)
        
        return html_conteudo
    
    def _adicionar_cards_secoes(self, html_conteudo: str) -> str:
        """Adiciona cards para seções principais"""
        
        # Padrão para identificar seções H2
        padrao_h2 = r'<h2[^>]*>(.*?)</h2>'
        
        def substituir_secao(match):
            titulo_secao = match.group(1)
            icone = self._obter_icone_secao(titulo_secao)
            
            return f'''
            <div class="card section-card mb-4">
                <div class="card-header bg-primary text-white">
                    <h2 class="card-title mb-0">
                        <i class="{icone}"></i> {titulo_secao}
                    </h2>
                </div>
                <div class="card-body">
            '''
        
        # Substituir H2 por início de card
        html_processado = re.sub(padrao_h2, substituir_secao, html_conteudo)
        
        # Fechar cards antes de próximo H2 ou no final
        # Implementação simplificada - pode ser melhorada
        
        return html_processado
    
    def _obter_icone_secao(self, titulo_secao: str) -> str:
        """Obtém ícone apropriado para seção"""
        
        titulo_lower = titulo_secao.lower()
        
        icones_map = {
            'sumário': 'fas fa-clipboard-list',
            'executivo': 'fas fa-chart-line',
            'análise': 'fas fa-search',
            'dados': 'fas fa-database',
            'insights': 'fas fa-lightbulb',
            'drivers': 'fas fa-brain',
            'mental': 'fas fa-brain',
            'preditivo': 'fas fa-crystal-ball',
            'futuro': 'fas fa-crystal-ball',
            'oportunidades': 'fas fa-bullseye',
            'recomendações': 'fas fa-tasks',
            'conclusão': 'fas fa-flag-checkered',
            'viral': 'fas fa-fire',
            'tendências': 'fas fa-trending-up',
            'mercado': 'fas fa-store',
            'competitivo': 'fas fa-chess',
            'swot': 'fas fa-balance-scale'
        }
        
        for palavra, icone in icones_map.items():
            if palavra in titulo_lower:
                return icone
        
        return 'fas fa-file-alt'  # Ícone padrão
    
    def _processar_estatisticas(self, html_conteudo: str) -> str:
        """Processa números e estatísticas para destaque visual"""
        
        # Padrão para números com % ou valores monetários
        padrao_stats = r'(\d+(?:\.\d+)?)\s*([%$R\$€£¥]|\w+)'
        
        def destacar_estatistica(match):
            numero = match.group(1)
            unidade = match.group(2)
            
            return f'''
            <span class="stat-highlight">
                <span class="stat-number">{numero}</span>
                <span class="stat-unit">{unidade}</span>
            </span>
            '''
        
        return re.sub(padrao_stats, destacar_estatistica, html_conteudo)
    
    async def _adicionar_secao_imagens(self, html_conteudo: str, session_id: str) -> str:
        """
        Adiciona seção de imagens 1080x1080 extraídas na primeira etapa
        
        Args:
            html_conteudo: Conteúdo HTML atual
            session_id: ID da sessão para localizar imagens
            
        Returns:
            HTML com seção de imagens adicionada
        """
        try:
            # Diretório de imagens da sessão
            images_dir = f"analyses_data/files/{session_id}"
            
            # Procurar por imagens 1080x1080
            imagens_1080 = []
            
            if os.path.exists(images_dir):
                for arquivo in os.listdir(images_dir):
                    if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                        caminho_completo = os.path.join(images_dir, arquivo)
                        
                        # Verificar se é uma imagem 1080x1080
                        try:
                            from PIL import Image
                            with Image.open(caminho_completo) as img:
                                width, height = img.size
                                if width == 1080 and height == 1080:
                                    imagens_1080.append({
                                        'arquivo': arquivo,
                                        'caminho': caminho_completo,
                                        'tamanho': os.path.getsize(caminho_completo),
                                        'formato': img.format
                                    })
                        except Exception as img_error:
                            logger.warning(f"⚠️ Erro ao processar imagem {arquivo}: {img_error}")
                            continue
            
            # Se não há imagens 1080x1080, retorna o HTML original
            if not imagens_1080:
                logger.info(f"ℹ️ Nenhuma imagem 1080x1080 encontrada para sessão {session_id}")
                return html_conteudo
            
            logger.info(f"🖼️ Encontradas {len(imagens_1080)} imagens 1080x1080 para sessão {session_id}")
            
            # Gerar HTML da seção de imagens
            secao_imagens_html = self._gerar_html_secao_imagens(imagens_1080, session_id)
            
            # Inserir seção antes do final do conteúdo
            # Procurar por um bom local para inserir (antes de conclusões ou no final)
            pontos_insercao = [
                r'(<h2[^>]*>.*?conclus[ãa]o.*?</h2>)',
                r'(<h2[^>]*>.*?considera[çc][õo]es.*?finais.*?</h2>)',
                r'(<h2[^>]*>.*?resumo.*?executivo.*?</h2>)',
                r'(</div>\s*$)'  # Final do conteúdo
            ]
            
            inserido = False
            for padrao in pontos_insercao:
                if re.search(padrao, html_conteudo, re.IGNORECASE):
                    html_conteudo = re.sub(
                        padrao,
                        f'{secao_imagens_html}\\1',
                        html_conteudo,
                        flags=re.IGNORECASE
                    )
                    inserido = True
                    break
            
            # Se não encontrou um ponto específico, adiciona no final
            if not inserido:
                html_conteudo += secao_imagens_html
            
            logger.info(f"✅ Seção de imagens 1080x1080 adicionada ao relatório HTML")
            
            return html_conteudo
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar seção de imagens: {e}")
            return html_conteudo
    
    def _gerar_html_secao_imagens(self, imagens_1080: List[Dict], session_id: str) -> str:
        """
        Gera HTML da seção de imagens 1080x1080
        
        Args:
            imagens_1080: Lista de imagens 1080x1080 encontradas
            session_id: ID da sessão
            
        Returns:
            HTML da seção de imagens
        """
        # Cabeçalho da seção
        html_secao = f'''
        <div class="card mb-4 images-section">
            <div class="card-header bg-primary text-white">
                <h2 class="card-title mb-0">
                    <i class="fas fa-images me-2"></i>
                    Imagens Extraídas (1080x1080)
                </h2>
                <p class="card-subtitle mb-0 mt-2 opacity-75">
                    {len(imagens_1080)} imagens de alta qualidade extraídas durante a primeira etapa da análise
                </p>
            </div>
            <div class="card-body">
                <div class="row g-3">
        '''
        
        # Adicionar cada imagem
        for i, imagem in enumerate(imagens_1080):
            # Converter tamanho para formato legível
            tamanho_mb = imagem['tamanho'] / (1024 * 1024)
            tamanho_str = f"{tamanho_mb:.2f} MB" if tamanho_mb >= 1 else f"{imagem['tamanho'] / 1024:.1f} KB"
            
            # Caminho relativo para o HTML
            caminho_relativo = f"files/{session_id}/{imagem['arquivo']}"
            
            html_secao += f'''
                    <div class="col-md-6 col-lg-4">
                        <div class="card image-card h-100">
                            <div class="image-container">
                                <img src="{caminho_relativo}" 
                                     class="card-img-top image-1080" 
                                     alt="Imagem extraída {i+1}"
                                     loading="lazy"
                                     onclick="openImageModal('{caminho_relativo}', 'Imagem {i+1}')">
                                <div class="image-overlay">
                                    <i class="fas fa-expand-alt"></i>
                                </div>
                            </div>
                            <div class="card-body">
                                <h6 class="card-title">Imagem {i+1}</h6>
                                <div class="image-info">
                                    <small class="text-muted">
                                        <i class="fas fa-file-image me-1"></i>
                                        {imagem['formato']} • 1080×1080 • {tamanho_str}
                                    </small>
                                </div>
                                <div class="mt-2">
                                    <a href="{caminho_relativo}" 
                                       class="btn btn-sm btn-outline-primary" 
                                       download="{imagem['arquivo']}"
                                       title="Baixar imagem">
                                        <i class="fas fa-download me-1"></i>
                                        Download
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
            '''
        
        # Fechar seção
        html_secao += '''
                </div>
            </div>
        </div>
        
        <!-- Modal para visualização de imagens -->
        <div class="modal fade" id="imageModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="imageModalLabel">Visualizar Imagem</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img id="modalImage" src="" class="img-fluid" alt="Imagem ampliada">
                    </div>
                </div>
            </div>
        </div>
        '''
        
        return html_secao
    
    def _gerar_css_profissional(self) -> str:
        """Gera CSS profissional personalizado"""
        
        return f"""
        /* Variáveis CSS */
        :root {{
            --primary-color: {self.cores['primaria']};
            --secondary-color: {self.cores['secundaria']};
            --light-bg: {self.cores['fundo_claro']};
            --text-primary: {self.cores['texto_principal']};
            --text-secondary: {self.cores['texto_secundario']};
            --border-color: {self.cores['borda']};
            --font-family: {self.fontes['principal']};
        }}
        
        /* Reset e Base */
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: var(--font-family);
            line-height: 1.6;
            color: var(--text-primary);
            background-color: #ffffff;
        }}
        
        /* Cabeçalho */
        .header-section {{
            background: linear-gradient(135deg, var(--primary-color), #004494);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .header-subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 1rem;
        }}
        
        .header-meta {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        /* Header Melhorado */
        .bg-gradient-primary {{
            background: linear-gradient(135deg, var(--primary-color) 0%, #0056b3 50%, #004085 100%);
            position: relative;
            overflow: hidden;
        }}
        
        .header-section::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            pointer-events: none;
        }}
        
        .header-content {{
            position: relative;
            z-index: 2;
        }}
        
        .meta-item {{
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
        }}
        
        .meta-item:hover {{
            background-color: rgba(255,255,255,0.2) !important;
            transform: translateY(-2px);
        }}
        
        .pulse-animation {{
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.1); opacity: 0.7; }}
            100% {{ transform: scale(1); opacity: 1; }}
        }}
        
        .pulse-dot {{
            width: 12px;
            height: 12px;
            animation: pulse-dot 1.5s infinite;
        }}
        
        @keyframes pulse-dot {{
            0% {{ transform: scale(0.8); opacity: 0.5; }}
            50% {{ transform: scale(1.2); opacity: 1; }}
            100% {{ transform: scale(0.8); opacity: 0.5; }}
        }}
        
        .header-wave {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            overflow: hidden;
            line-height: 0;
        }}
        
        .header-wave svg {{
            position: relative;
            display: block;
            width: calc(100% + 1.3px);
            height: 60px;
        }}
        
        .header-wave path {{
            fill: #ffffff;
        }}
        
        .stat-item {{
            transition: transform 0.3s ease;
        }}
        
        .stat-item:hover {{
            transform: scale(1.1);
        }}
        
        /* Sidebar */
        .sidebar {{
            background-color: var(--light-bg);
            min-height: calc(100vh - 200px);
            padding: 1.5rem 1rem;
            border-right: 1px solid var(--border-color);
        }}
        
        .sidebar-nav {{
            position: sticky;
            top: 2rem;
        }}
        
        .nav-link {{
            color: var(--text-primary);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        
        .nav-link:hover {{
            background-color: var(--primary-color);
            color: white;
            transform: translateX(5px);
        }}
        
        /* Conteúdo Principal */
        .main-content {{
            padding: 2rem;
        }}
        
        /* Cards de Seção */
        .section-card {{
            border: none;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .section-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        .section-card .card-header {{
            border-radius: 12px 12px 0 0 !important;
            padding: 1.5rem;
        }}
        
        .section-card .card-body {{
            padding: 2rem;
        }}
        
        /* Tipografia */
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 1.5rem;
        }}
        
        h2 {{
            font-size: 2rem;
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 1rem;
        }}
        
        h3 {{
            font-size: 1.5rem;
            font-weight: 500;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
        }}
        
        /* Estatísticas em Destaque */
        .stat-highlight {{
            display: inline-block;
            background: linear-gradient(135deg, var(--primary-color), #0066cc);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            margin: 0.25rem;
            font-weight: 600;
            box-shadow: 0 3px 10px rgba(0,86,179,0.3);
        }}
        
        .stat-number {{
            font-size: 1.2em;
            font-weight: 700;
        }}
        
        .stat-unit {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        /* Seção de Imagens 1080x1080 */
        .images-section {{
            border: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-radius: 12px;
            overflow: hidden;
        }}
        
        .images-section .card-header {{
            background: linear-gradient(135deg, var(--primary-color), #0066cc) !important;
            border: none;
            padding: 1.5rem;
        }}
        
        .image-card {{
            border: none;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
            transition: all 0.3s ease;
            overflow: hidden;
        }}
        
        .image-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        
        .image-container {{
            position: relative;
            overflow: hidden;
            aspect-ratio: 1;
        }}
        
        .image-1080 {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
            cursor: pointer;
        }}
        
        .image-1080:hover {{
            transform: scale(1.05);
        }}
        
        .image-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
            color: white;
            font-size: 1.5rem;
        }}
        
        .image-container:hover .image-overlay {{
            opacity: 1;
        }}
        
        .image-info {{
            font-size: 0.85rem;
        }}
        
        /* Modal de imagens */
        #imageModal .modal-dialog {{
            max-width: 90vw;
        }}
        
        #modalImage {{
            max-height: 80vh;
            border-radius: 8px;
        }}
        
        /* Tabelas */
        .table {{
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }}
        
        .table thead th {{
            background-color: var(--primary-color);
            color: white;
            border: none;
            font-weight: 600;
        }}
        
        /* Listas */
        .list-group-item {{
            border: none;
            border-left: 3px solid transparent;
            transition: all 0.3s ease;
        }}
        
        .list-group-item:hover {{
            border-left-color: var(--primary-color);
            background-color: var(--light-bg);
        }}
        
        /* Blockquotes */
        .blockquote {{
            border-left: 4px solid var(--primary-color);
            padding-left: 1.5rem;
            font-style: italic;
        }}
        
        /* Botões e Links */
        .btn-primary {{
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            border-radius: 25px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .btn-primary:hover {{
            background-color: #004494;
            border-color: #004494;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,86,179,0.4);
        }}
        
        /* Animações */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .section-card {{
            animation: fadeInUp 0.6s ease-out;
        }}
        
        /* Responsividade */
        @media (max-width: 768px) {{
            .header-title {{
                font-size: 2rem;
            }}
            
            .main-content {{
                padding: 1rem;
            }}
            
            .section-card .card-body {{
                padding: 1.5rem;
            }}
        }}
        
        /* Rodapé */
        .footer-section {{
            background-color: var(--text-primary);
            color: white;
            padding: 2rem 0;
            margin-top: 3rem;
        }}
        
        .footer-section a {{
            color: #ccc;
            text-decoration: none;
        }}
        
        .footer-section a:hover {{
            color: white;
        }}
        
        /* Scroll suave */
        html {{
            scroll-behavior: smooth;
        }}
        
        /* Loading spinner */
        .loading-spinner {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        """
    
    def _gerar_cabecalho(self, titulo: str, subtitulo: str, session_id: str) -> str:
        """Gera cabeçalho profissional com melhor formatação"""
        
        timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M")
        
        return f"""
        <header class="header-section bg-gradient-primary text-white py-5 mb-4">
            <div class="container">
                <div class="row align-items-center">
                    <div class="col-lg-8 col-md-7">
                        <div class="header-content">
                            <h1 class="header-title display-4 fw-bold mb-3">
                                <i class="fas fa-chart-line me-3 text-warning"></i>
                                {self._escape_html(titulo)}
                            </h1>
                            <p class="header-subtitle lead mb-4 text-light">
                                {self._escape_html(subtitulo)}
                            </p>
                            <div class="header-meta d-flex flex-wrap gap-3">
                                <div class="meta-item bg-white bg-opacity-10 px-3 py-2 rounded">
                                    <i class="fas fa-calendar-alt me-2"></i>
                                    <span class="fw-medium">Gerado em {timestamp}</span>
                                </div>
                                <div class="meta-item bg-white bg-opacity-10 px-3 py-2 rounded">
                                    <i class="fas fa-cog me-2"></i>
                                    <span class="fw-medium">ARQV18 Enhanced v18.0</span>
                                </div>
                                <div class="meta-item bg-white bg-opacity-10 px-3 py-2 rounded">
                                    <i class="fas fa-robot me-2"></i>
                                    <span class="fw-medium">Powered by AI</span>
                                </div>
                            </div>
                            <div class="session-info mt-3">
                                <small class="text-light opacity-75">
                                    <i class="fas fa-fingerprint me-1"></i>
                                    Sessão: {session_id[:8]}...
                                </small>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4 col-md-5 text-center text-md-end">
                        <div class="header-visual">
                            <div class="logo-container position-relative">
                                <i class="fas fa-brain fa-5x text-warning opacity-75 mb-3"></i>
                                <div class="pulse-animation position-absolute top-0 start-50 translate-middle-x">
                                    <div class="pulse-dot bg-warning rounded-circle"></div>
                                </div>
                            </div>
                            <div class="stats-preview mt-3">
                                <div class="row text-center">
                                    <div class="col-4">
                                        <div class="stat-item">
                                            <i class="fas fa-search text-info"></i>
                                            <small class="d-block text-light">Busca</small>
                                        </div>
                                    </div>
                                    <div class="col-4">
                                        <div class="stat-item">
                                            <i class="fas fa-users text-success"></i>
                                            <small class="d-block text-light">Análise</small>
                                        </div>
                                    </div>
                                    <div class="col-4">
                                        <div class="stat-item">
                                            <i class="fas fa-chart-bar text-warning"></i>
                                            <small class="d-block text-light">Relatório</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Decorative wave -->
            <div class="header-wave">
                <svg viewBox="0 0 1200 120" preserveAspectRatio="none" class="w-100" style="height: 60px;">
                    <path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" fill="currentColor"></path>
                    <path d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" opacity=".5" fill="currentColor"></path>
                    <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" fill="currentColor"></path>
                </svg>
            </div>
        </header>
        """
    
    def _gerar_sidebar_navegacao(self, html_conteudo: str) -> str:
        """Gera sidebar de navegação baseada nos cabeçalhos"""
        
        # Extrair cabeçalhos H2 e H3 com melhor regex
        padrao_h2 = r'<h2[^>]*>(.*?)</h2>'
        padrao_h3 = r'<h3[^>]*>(.*?)</h3>'
        
        h2_matches = re.findall(padrao_h2, html_conteudo, re.DOTALL)
        h3_matches = re.findall(padrao_h3, html_conteudo, re.DOTALL)
        
        nav_items = []
        
        # Adicionar navegação para seções principais
        main_sections = [
            ("resumo-executivo", "📊 Resumo Executivo"),
            ("analise-mercado", "🎯 Análise de Mercado"),
            ("concorrencia", "🏆 Análise de Concorrência"),
            ("estrategias", "💡 Estratégias Recomendadas"),
            ("viral-content", "🚀 Conteúdo Viral"),
            ("dados-tecnicos", "📈 Dados Técnicos")
        ]
        
        for anchor, titulo in main_sections:
            nav_items.append(f'''
                <li class="nav-item">
                    <a class="nav-link sidebar-link" href="#{anchor}" onclick="scrollToSection('{anchor}')">
                        <i class="fas fa-chevron-right me-2"></i>
                        {titulo}
                    </a>
                </li>
            ''')
        
        # Adicionar cabeçalhos H2 encontrados no conteúdo
        for i, h2 in enumerate(h2_matches[:5]):  # Limitar a 5 itens
            # Limpar HTML tags do título
            titulo_limpo = re.sub(r'<[^>]+>', '', h2).strip()
            if len(titulo_limpo) > 50:
                titulo_limpo = titulo_limpo[:47] + "..."
            
            anchor = re.sub(r'[^\w\s-]', '', titulo_limpo).strip().replace(' ', '-').lower()
            anchor = re.sub(r'-+', '-', anchor)  # Remove múltiplos hífens
            
            if titulo_limpo and anchor:
                nav_items.append(f'''
                    <li class="nav-item">
                        <a class="nav-link sidebar-link" href="#{anchor}" onclick="scrollToSection('{anchor}')">
                            <i class="fas fa-angle-right me-2"></i>
                            {titulo_limpo}
                        </a>
                    </li>
                ''')
        
        return f"""
        <div class="sidebar-nav">
            <h5 class="mb-3">
                <i class="fas fa-list me-2"></i>
                Navegação
            </h5>
            <ul class="nav flex-column">
                {' '.join(nav_items)}
            </ul>
            
            <div class="mt-4">
                <button class="btn btn-outline-primary btn-sm w-100" onclick="scrollToTop()">
                    <i class="fas fa-arrow-up me-2"></i>
                    Voltar ao Topo
                </button>
            </div>
        </div>
        """
    
    def _gerar_rodape(self) -> str:
        """Gera rodapé profissional"""
        
        return f"""
        <footer class="footer-section">
            <div class="container">
                <div class="row">
                    <div class="col-md-6">
                        <h5>ARQV18 Enhanced v18.0</h5>
                        <p class="mb-0">Sistema avançado de análise e relatórios inteligentes</p>
                    </div>
                    <div class="col-md-6 text-end">
                        <p class="mb-0">
                            <i class="fas fa-robot me-2"></i>
                            Powered by Artificial Intelligence
                        </p>
                        <small class="text-muted">
                            Gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}
                        </small>
                    </div>
                </div>
            </div>
        </footer>
        """
    
    def _gerar_javascript_interativo(self) -> str:
        """Gera JavaScript para interatividade"""
        
        return """
        // Função para scroll suave para seções
        function scrollToSection(sectionId) {
            const target = document.getElementById(sectionId);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Atualizar link ativo
                document.querySelectorAll('.sidebar-link').forEach(link => {
                    link.classList.remove('active');
                });
                document.querySelector(`a[href="#${sectionId}"]`)?.classList.add('active');
            }
        }
        
        // Função para voltar ao topo
        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }
        
        // Smooth scrolling para todos os links de navegação
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    scrollToSection(targetId);
                });
            });
        });
        
        // Highlight da seção ativa na navegação
        window.addEventListener('scroll', function() {
            const sections = document.querySelectorAll('h2[id], h3[id], section[id]');
            const navLinks = document.querySelectorAll('.sidebar-link');
            
            let current = '';
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                if (window.scrollY >= (sectionTop - 200)) {
                    current = section.getAttribute('id');
                }
            });
            
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {
                    link.classList.add('active');
                }
            });
        });
        
        // Animação de entrada para cards
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);
        
        document.querySelectorAll('.section-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
        
        // Tooltip para estatísticas
        document.querySelectorAll('.stat-highlight').forEach(stat => {
            stat.setAttribute('data-bs-toggle', 'tooltip');
            stat.setAttribute('data-bs-placement', 'top');
            stat.setAttribute('title', 'Estatística destacada');
        });
        
        // Inicializar tooltips do Bootstrap
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // Print functionality
        function printReport() {
            window.print();
        }
        
        // Export functionality (placeholder)
        function exportReport(format) {
            alert('Funcionalidade de exportação em ' + format + ' será implementada em breve.');
        }
        
        // Modal de imagens 1080x1080
        function openImageModal(imageSrc, imageTitle) {
            const modal = new bootstrap.Modal(document.getElementById('imageModal'));
            const modalImage = document.getElementById('modalImage');
            const modalTitle = document.getElementById('imageModalLabel');
            
            modalImage.src = imageSrc;
            modalTitle.textContent = imageTitle;
            modal.show();
        }
        
        // Lazy loading para imagens
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src || img.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            document.querySelectorAll('img[loading="lazy"]').forEach(img => {
                imageObserver.observe(img);
            });
        }
        
        // Animação para cards de imagem
        document.querySelectorAll('.image-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
        
        console.log('📊 Relatório HTML carregado com sucesso!');
        """
    
    async def _salvar_arquivo_html(
        self,
        session_id: str,
        html_completo: str,
        nome_arquivo: str
    ) -> str:
        """Salva arquivo HTML no diretório da sessão"""
        
        try:
            # Criar diretório da sessão
            session_dir = Path(f"sessions/{session_id}/reports")
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # Definir caminho do arquivo
            arquivo_path = session_dir / f"{nome_arquivo}.html"
            
            # Salvar arquivo
            with open(arquivo_path, 'w', encoding='utf-8') as f:
                f.write(html_completo)
            
            logger.info(f"✅ Arquivo HTML salvo: {arquivo_path}")
            
            return str(arquivo_path)
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar arquivo HTML: {e}")
            raise
    
    def get_info_modulo(self) -> Dict[str, Any]:
        """Retorna informações do módulo"""
        return {
            'nome': self.nome_modulo,
            'versao': self.versao,
            'funcionalidades': [
                'Conversão MD para HTML profissional',
                'Layout responsivo e moderno',
                'Design corporativo personalizado',
                'Navegação interativa',
                'Destaque de estatísticas',
                'Animações e transições',
                'Compatibilidade mobile'
            ],
            'tecnologias': ['HTML5', 'CSS3', 'Bootstrap 5', 'JavaScript', 'Font Awesome'],
            'cores_suportadas': self.cores,
            'fontes_suportadas': self.fontes
        }

# Instância global do conversor
html_report_converter = HTMLReportConverter()