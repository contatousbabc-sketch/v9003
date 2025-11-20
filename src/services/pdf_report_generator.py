#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV40 Enhanced - Gerador de Relatório PDF
Gera relatórios profissionais em PDF com cabeçalho, rodapé e design moderno
"""

import logging
import os
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import re

# Importações para PDF
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import Color, HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
    from reportlab.platypus.frames import Frame
    from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """Gerador de relatórios PDF profissionais"""
    
    def __init__(self):
        """Inicializa o gerador de PDF"""
        if not REPORTLAB_AVAILABLE:
            logger.error("❌ ReportLab não está disponível. Instale com: pip install reportlab")
            raise ImportError("ReportLab é necessário para gerar PDFs")
        
        self.page_width, self.page_height = A4
        self.margin = 2*cm
        self.content_width = self.page_width - 2*self.margin
        
        # Cores do tema
        self.primary_color = HexColor('#2c3e50')
        self.secondary_color = HexColor('#3498db')
        self.accent_color = HexColor('#e74c3c')
        self.text_color = HexColor('#2c3e50')
        self.light_gray = HexColor('#ecf0f1')
        self.dark_gray = HexColor('#7f8c8d')
        
        # Estilos
        self.styles = self._create_styles()
        
        # Logo
        self.logo_path = self._get_logo_path()
        
    def _get_logo_path(self) -> Optional[str]:
        """Obtém caminho do logo"""
        try:
            project_root = Path(__file__).parent.parent.parent
            logo_path = project_root / "src" / "static" / "logo_USB.png"
            
            if logo_path.exists():
                return str(logo_path)
            
            # Tenta criar logo temporário do base64
            logo_base64_path = project_root / "src" / "static" / "logo_base64.txt"
            if logo_base64_path.exists():
                with open(logo_base64_path, 'r') as f:
                    base64_data = f.read().strip()
                
                # Decodifica e salva temporariamente
                temp_logo_path = project_root / "temp_logo.png"
                with open(temp_logo_path, 'wb') as f:
                    f.write(base64.b64decode(base64_data))
                
                return str(temp_logo_path)
                
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível carregar logo: {e}")
        
        return None
    
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Cria estilos personalizados para o PDF com design moderno"""
        base_styles = getSampleStyleSheet()
        
        styles = {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Title'],
                fontSize=28,
                spaceAfter=40,
                spaceBefore=20,
                textColor=self.primary_color,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                leading=32
            ),
            'Subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=base_styles['Normal'],
                fontSize=16,
                spaceAfter=30,
                textColor=self.secondary_color,
                alignment=TA_CENTER,
                fontName='Helvetica',
                leading=20
            ),
            'Heading1': ParagraphStyle(
                'CustomHeading1',
                parent=base_styles['Heading1'],
                fontSize=20,
                spaceAfter=25,
                spaceBefore=35,
                textColor=self.primary_color,
                fontName='Helvetica-Bold',
                borderWidth=2,
                borderColor=self.secondary_color,
                borderPadding=15,
                backColor=HexColor('#f8f9fa'),
                leading=24
            ),
            'Heading2': ParagraphStyle(
                'CustomHeading2',
                parent=base_styles['Heading2'],
                fontSize=16,
                spaceAfter=18,
                spaceBefore=25,
                textColor=self.secondary_color,
                fontName='Helvetica-Bold',
                borderWidth=1,
                borderColor=self.secondary_color,
                borderPadding=8,
                leftIndent=10,
                leading=20
            ),
            'Heading3': ParagraphStyle(
                'CustomHeading3',
                parent=base_styles['Heading3'],
                fontSize=14,
                spaceAfter=15,
                spaceBefore=20,
                textColor=self.text_color,
                fontName='Helvetica-Bold',
                leftIndent=5,
                leading=18
            ),
            'Normal': ParagraphStyle(
                'CustomNormal',
                parent=base_styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                textColor=self.text_color,
                fontName='Helvetica',
                alignment=TA_JUSTIFY,
                leading=16,
                firstLineIndent=20
            ),
            'Bullet': ParagraphStyle(
                'CustomBullet',
                parent=base_styles['Normal'],
                fontSize=11,
                spaceAfter=8,
                textColor=self.text_color,
                fontName='Helvetica',
                leftIndent=25,
                bulletIndent=15,
                leading=14
            ),
            'NumberedList': ParagraphStyle(
                'CustomNumberedList',
                parent=base_styles['Normal'],
                fontSize=11,
                spaceAfter=8,
                textColor=self.text_color,
                fontName='Helvetica',
                leftIndent=25,
                bulletIndent=15,
                leading=14
            ),
            'Quote': ParagraphStyle(
                'CustomQuote',
                parent=base_styles['Normal'],
                fontSize=12,
                spaceAfter=15,
                spaceBefore=15,
                textColor=self.dark_gray,
                fontName='Helvetica-Oblique',
                alignment=TA_JUSTIFY,
                leftIndent=30,
                rightIndent=30,
                borderWidth=1,
                borderColor=self.secondary_color,
                borderPadding=15,
                backColor=HexColor('#f8f9fa'),
                leading=16
            ),
            'Highlight': ParagraphStyle(
                'CustomHighlight',
                parent=base_styles['Normal'],
                fontSize=12,
                spaceAfter=15,
                spaceBefore=15,
                textColor=self.primary_color,
                fontName='Helvetica-Bold',
                alignment=TA_CENTER,
                borderWidth=2,
                borderColor=self.accent_color,
                borderPadding=12,
                backColor=HexColor('#fff3cd'),
                leading=16
            ),
            'Caption': ParagraphStyle(
                'CustomCaption',
                parent=base_styles['Normal'],
                fontSize=9,
                textColor=self.dark_gray,
                fontName='Helvetica-Oblique',
                alignment=TA_CENTER,
                spaceAfter=10
            ),
            'Footer': ParagraphStyle(
                'CustomFooter',
                parent=base_styles['Normal'],
                fontSize=9,
                textColor=self.dark_gray,
                fontName='Helvetica',
                alignment=TA_CENTER
            ),
            'TableHeader': ParagraphStyle(
                'CustomTableHeader',
                parent=base_styles['Normal'],
                fontSize=12,
                textColor=colors.white,
                fontName='Helvetica-Bold',
                alignment=TA_CENTER,
                leading=14
            ),
            'TableCell': ParagraphStyle(
                'CustomTableCell',
                parent=base_styles['Normal'],
                fontSize=10,
                textColor=self.text_color,
                fontName='Helvetica',
                alignment=TA_LEFT,
                leading=12
            )
        }
        
        return styles
    
    def generate_pdf_report(self, report_data: Dict[str, Any], output_path: str) -> bool:
        """
        Gera relatório PDF completo
        
        Args:
            report_data: Dados do relatório
            output_path: Caminho para salvar o PDF
            
        Returns:
            True se gerado com sucesso
        """
        try:
            logger.info(f"📄 Gerando relatório PDF: {output_path}")
            
            # Cria documento PDF
            doc = BaseDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin + 1*cm,  # Espaço extra para cabeçalho
                bottomMargin=self.margin + 1*cm  # Espaço extra para rodapé
            )
            
            # Define template de página
            frame = Frame(
                self.margin, self.margin + 1*cm,
                self.content_width, self.page_height - 2*self.margin - 2*cm,
                id='normal'
            )
            
            template = PageTemplate(
                id='main',
                frames=frame,
                onPage=self._draw_page_decoration
            )
            
            doc.addPageTemplates([template])
            
            # Gera conteúdo
            story = self._build_story(report_data)
            
            # Constrói PDF
            doc.build(story)
            
            logger.info(f"✅ PDF gerado com sucesso: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar PDF: {e}")
            return False
    
    def _draw_page_decoration(self, canvas_obj, doc):
        """Desenha cabeçalho e rodapé em cada página"""
        try:
            # Cabeçalho
            self._draw_header(canvas_obj)
            
            # Rodapé
            self._draw_footer(canvas_obj, doc)
            
        except Exception as e:
            logger.error(f"❌ Erro ao desenhar decoração da página: {e}")
    
    def _draw_header(self, canvas_obj):
        """Desenha cabeçalho da página"""
        try:
            # Linha superior
            canvas_obj.setStrokeColor(self.secondary_color)
            canvas_obj.setLineWidth(3)
            canvas_obj.line(self.margin, self.page_height - self.margin/2, 
                          self.page_width - self.margin, self.page_height - self.margin/2)
            
            # Logo (se disponível)
            if self.logo_path and os.path.exists(self.logo_path):
                try:
                    canvas_obj.drawImage(
                        self.logo_path,
                        self.margin, self.page_height - self.margin + 0.2*cm,
                        width=1.5*cm, height=1.5*cm,
                        preserveAspectRatio=True
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao inserir logo no cabeçalho: {e}")
            
            # Título do relatório
            canvas_obj.setFont('Helvetica-Bold', 14)
            canvas_obj.setFillColor(self.primary_color)
            canvas_obj.drawString(
                self.margin + 2*cm, self.page_height - self.margin + 0.8*cm,
                "ARQV40 Enhanced - Relatório de Análise de Mercado"
            )
            
            # Data de geração
            canvas_obj.setFont('Helvetica', 10)
            canvas_obj.setFillColor(self.dark_gray)
            canvas_obj.drawRightString(
                self.page_width - self.margin, self.page_height - self.margin + 0.5*cm,
                f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao desenhar cabeçalho: {e}")
    
    def _draw_footer(self, canvas_obj, doc):
        """Desenha rodapé da página"""
        try:
            # Linha inferior
            canvas_obj.setStrokeColor(self.secondary_color)
            canvas_obj.setLineWidth(1)
            canvas_obj.line(self.margin, self.margin/2, 
                          self.page_width - self.margin, self.margin/2)
            
            # Número da página
            canvas_obj.setFont('Helvetica', 10)
            canvas_obj.setFillColor(self.dark_gray)
            canvas_obj.drawCentredText(
                self.page_width/2, self.margin/4,
                f"Página {doc.page}"
            )
            
            # Informações da empresa (lado esquerdo)
            canvas_obj.drawString(
                self.margin, self.margin/4,
                "USB MKT AM - Análise de Mercado com IA"
            )
            
            # Website (lado direito)
            canvas_obj.drawRightString(
                self.page_width - self.margin, self.margin/4,
                "www.usbmktam.com"
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao desenhar rodapé: {e}")
    
    def _build_story(self, report_data: Dict[str, Any]) -> List:
        """Constrói o conteúdo do relatório"""
        story = []
        
        try:
            # Página de título
            story.extend(self._create_title_page(report_data))
            story.append(PageBreak())
            
            # Sumário executivo
            if 'sumario_executivo' in report_data:
                story.extend(self._create_executive_summary(report_data['sumario_executivo']))
                story.append(PageBreak())
            
            # Módulos do relatório
            if 'modules' in report_data:
                story.extend(self._create_modules_content(report_data['modules']))
            
            # Conclusões
            story.extend(self._create_conclusions(report_data))
            
        except Exception as e:
            logger.error(f"❌ Erro ao construir story do PDF: {e}")
            story.append(Paragraph(f"Erro ao gerar conteúdo: {str(e)}", self.styles['Normal']))
        
        return story
    
    def _create_title_page(self, report_data: Dict[str, Any]) -> List:
        """Cria página de título com design moderno"""
        elements = []
        
        try:
            # Espaço inicial menor
            elements.append(Spacer(1, 2*cm))
            
            # Logo grande centralizado (se disponível)
            if self.logo_path and os.path.exists(self.logo_path):
                try:
                    logo = Image(self.logo_path, width=5*cm, height=5*cm)
                    logo.hAlign = 'CENTER'
                    elements.append(logo)
                    elements.append(Spacer(1, 1.5*cm))
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao inserir logo na capa: {e}")
            else:
                # Se não há logo, adiciona espaço extra
                elements.append(Spacer(1, 2*cm))
            
            # Título principal com estilo aprimorado
            elements.append(Paragraph(
                "RELATÓRIO DE ANÁLISE DE MERCADO",
                self.styles['Title']
            ))
            
            # Subtítulo com estilo personalizado
            elements.append(Paragraph(
                "Análise Completa com Inteligência Artificial",
                self.styles['Subtitle']
            ))
            
            elements.append(Spacer(1, 1.5*cm))
            
            # Caixa de destaque com query
            if 'query' in report_data and report_data['query']:
                query_text = f"<b>Análise Focada em:</b><br/><i>{report_data['query']}</i>"
                elements.append(Paragraph(query_text, self.styles['Highlight']))
                elements.append(Spacer(1, 1*cm))
            
            # Informações do relatório em formato moderno
            current_time = datetime.now()
            info_data = [
                ['📊 Tipo de Análise:', 'Análise Completa de Mercado'],
                ['📅 Data de Geração:', current_time.strftime('%d/%m/%Y')],
                ['⏰ Hora de Geração:', current_time.strftime('%H:%M:%S')],
                ['🤖 Sistema:', 'ARQV40 Enhanced v1.0'],
                ['🔍 Módulos Incluídos:', str(len(report_data.get('modules', {}))) + ' módulos']
            ]
            
            info_table = Table(info_data, colWidths=[4.5*cm, 7.5*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.text_color),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, self.secondary_color),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f8f9fa')])
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 2*cm))
            
            # Disclaimer moderno com ícones
            disclaimer_text = """
            <b>⚠️ IMPORTANTE:</b> Este relatório foi gerado automaticamente utilizando 
            inteligência artificial avançada e análise de dados em tempo real. As informações 
            apresentadas devem ser utilizadas como base estratégica para tomada de decisões, 
            sempre considerando o contexto específico do seu negócio e validação adicional quando necessário.
            <br/><br/>
            <b>🎯 Objetivo:</b> Fornecer insights acionáveis para otimização de estratégias de marketing e vendas.
            """
            
            elements.append(Paragraph(disclaimer_text, ParagraphStyle(
                'ModernDisclaimer',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=self.text_color,
                alignment=TA_JUSTIFY,
                borderWidth=2,
                borderColor=self.secondary_color,
                borderPadding=15,
                backColor=HexColor('#f0f8ff'),
                leading=14
            )))
            
            # Rodapé da capa
            elements.append(Spacer(1, 1*cm))
            elements.append(Paragraph(
                "USB MKT AM - Análise de Mercado com IA | www.usbmktam.com",
                ParagraphStyle(
                    'CoverFooter',
                    parent=self.styles['Normal'],
                    fontSize=9,
                    textColor=self.dark_gray,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Oblique'
                )
            ))
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar página de título: {e}")
            elements.append(Paragraph(f"Erro na página de título: {str(e)}", self.styles['Normal']))
        
        return elements
    
    def _create_executive_summary(self, summary_content: str) -> List:
        """Cria seção de sumário executivo"""
        elements = []
        
        try:
            elements.append(Paragraph("SUMÁRIO EXECUTIVO", self.styles['Heading1']))
            elements.append(Spacer(1, 0.5*cm))
            
            # Converte conteúdo para PDF
            summary_elements = self._convert_content_to_pdf(summary_content)
            elements.extend(summary_elements)
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar sumário executivo: {e}")
            elements.append(Paragraph(f"Erro no sumário executivo: {str(e)}", self.styles['Normal']))
        
        return elements
    
    def _create_modules_content(self, modules: Dict[str, Any]) -> List:
        """Cria conteúdo dos módulos"""
        elements = []
        
        try:
            for module_name, module_data in modules.items():
                if isinstance(module_data, dict) and 'content' in module_data:
                    # Título do módulo
                    title = module_data.get('title', module_name.replace('_', ' ').title())
                    elements.append(Paragraph(title.upper(), self.styles['Heading1']))
                    elements.append(Spacer(1, 0.3*cm))
                    
                    # Conteúdo do módulo
                    module_elements = self._convert_content_to_pdf(module_data['content'])
                    elements.extend(module_elements)
                    
                    # Quebra de página entre módulos principais
                    elements.append(PageBreak())
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar conteúdo dos módulos: {e}")
            elements.append(Paragraph(f"Erro nos módulos: {str(e)}", self.styles['Normal']))
        
        return elements
    
    def _create_conclusions(self, report_data: Dict[str, Any]) -> List:
        """Cria seção de conclusões"""
        elements = []
        
        try:
            elements.append(Paragraph("CONCLUSÕES E RECOMENDAÇÕES", self.styles['Heading1']))
            elements.append(Spacer(1, 0.5*cm))
            
            # Conclusões automáticas baseadas nos dados
            conclusions = self._generate_automatic_conclusions(report_data)
            
            for conclusion in conclusions:
                elements.append(Paragraph(f"• {conclusion}", self.styles['Bullet']))
            
            elements.append(Spacer(1, 1*cm))
            
            # Próximos passos
            elements.append(Paragraph("Próximos Passos Recomendados:", self.styles['Heading3']))
            
            next_steps = [
                "Implementar as estratégias identificadas como de maior potencial",
                "Monitorar continuamente os concorrentes identificados",
                "Realizar testes A/B das abordagens sugeridas",
                "Acompanhar métricas de performance regularmente",
                "Atualizar a análise trimestralmente"
            ]
            
            for step in next_steps:
                elements.append(Paragraph(f"• {step}", self.styles['Bullet']))
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar conclusões: {e}")
            elements.append(Paragraph(f"Erro nas conclusões: {str(e)}", self.styles['Normal']))
        
        return elements
    
    def _convert_content_to_pdf(self, content: str) -> List:
        """Converte conteúdo HTML/Markdown para elementos PDF com formatação avançada"""
        elements = []
        
        try:
            # Detecta se é JSON e formata adequadamente
            if self._is_json_content(content):
                elements.extend(self._format_json_content(content))
                return elements
            
            # Remove tags HTML complexas e converte para texto simples
            clean_content = self._clean_html_content(content)
            
            # Divide em seções por quebras duplas
            sections = clean_content.split('\n\n')
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                # Identifica diferentes tipos de conteúdo
                if self._is_header(section):
                    elements.extend(self._format_header(section))
                elif self._is_list(section):
                    elements.extend(self._format_list(section))
                elif self._is_table(section):
                    elements.extend(self._format_table(section))
                elif self._is_quote(section):
                    elements.extend(self._format_quote(section))
                elif self._is_highlight(section):
                    elements.extend(self._format_highlight(section))
                else:
                    # Parágrafo normal com formatação avançada
                    elements.extend(self._format_paragraph(section))
                
                # Espaçamento entre seções
                elements.append(Spacer(1, 0.3*cm))
        
        except Exception as e:
            logger.error(f"❌ Erro ao converter conteúdo: {e}")
            elements.append(Paragraph(f"Erro na conversão: {str(e)}", self.styles['Normal']))
        
        return elements
    
    def _is_json_content(self, content: str) -> bool:
        """Verifica se o conteúdo é JSON"""
        try:
            import json
            json.loads(content.strip())
            return True
        except:
            return False
    
    def _format_json_content(self, content: str) -> List:
        """Formata conteúdo JSON de forma estruturada"""
        elements = []
        try:
            import json
            data = json.loads(content.strip())
            
            if isinstance(data, dict):
                for key, value in data.items():
                    # Título da seção
                    title = key.replace('_', ' ').title()
                    elements.append(Paragraph(title, self.styles['Heading3']))
                    
                    # Conteúdo da seção
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, str):
                                elements.append(Paragraph(f"• {item}", self.styles['Bullet']))
                            elif isinstance(item, dict):
                                elements.extend(self._format_dict_item(item))
                    elif isinstance(value, dict):
                        elements.extend(self._format_dict_item(value))
                    elif isinstance(value, str):
                        elements.append(Paragraph(value, self.styles['Normal']))
                    
                    elements.append(Spacer(1, 0.2*cm))
            
        except Exception as e:
            logger.error(f"❌ Erro ao formatar JSON: {e}")
            elements.append(Paragraph("Conteúdo JSON não pôde ser formatado", self.styles['Normal']))
        
        return elements
    
    def _format_dict_item(self, item: dict) -> List:
        """Formata item de dicionário"""
        elements = []
        for k, v in item.items():
            key_name = k.replace('_', ' ').title()
            if isinstance(v, list):
                elements.append(Paragraph(f"<b>{key_name}:</b>", self.styles['Normal']))
                for list_item in v:
                    elements.append(Paragraph(f"  • {list_item}", self.styles['Bullet']))
            else:
                elements.append(Paragraph(f"<b>{key_name}:</b> {v}", self.styles['Normal']))
        return elements
    
    def _is_header(self, text: str) -> bool:
        """Verifica se é um cabeçalho"""
        return text.startswith('#') or (text.isupper() and len(text.split()) <= 6)
    
    def _format_header(self, text: str) -> List:
        """Formata cabeçalhos"""
        elements = []
        if text.startswith('###'):
            header_text = text.replace('###', '').strip()
            elements.append(Paragraph(header_text, self.styles['Heading3']))
        elif text.startswith('##'):
            header_text = text.replace('##', '').strip()
            elements.append(Paragraph(header_text, self.styles['Heading2']))
        elif text.startswith('#'):
            header_text = text.replace('#', '').strip()
            elements.append(Paragraph(header_text, self.styles['Heading1']))
        elif text.isupper():
            elements.append(Paragraph(text, self.styles['Heading2']))
        return elements
    
    def _is_list(self, text: str) -> bool:
        """Verifica se é uma lista"""
        lines = text.split('\n')
        list_indicators = ['•', '-', '*', '1.', '2.', '3.']
        return any(line.strip().startswith(indicator) for line in lines for indicator in list_indicators)
    
    def _format_list(self, text: str) -> List:
        """Formata listas com numeração e bullets"""
        elements = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Lista numerada
            if re.match(r'^\d+\.', line):
                item_text = re.sub(r'^\d+\.\s*', '', line)
                elements.append(Paragraph(f"{line.split('.')[0]}. {item_text}", self.styles['NumberedList']))
            # Lista com bullets
            elif line.startswith(('•', '-', '*')):
                item_text = line[1:].strip()
                elements.append(Paragraph(f"• {item_text}", self.styles['Bullet']))
            else:
                elements.append(Paragraph(line, self.styles['Normal']))
        
        return elements
    
    def _is_table(self, text: str) -> bool:
        """Verifica se é uma tabela"""
        lines = text.split('\n')
        return len(lines) > 1 and any('|' in line for line in lines)
    
    def _format_table(self, text: str) -> List:
        """Formata tabelas"""
        elements = []
        try:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if not lines:
                return elements
            
            # Extrai dados da tabela
            table_data = []
            for line in lines:
                if '|' in line:
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    if cells:
                        table_data.append(cells)
            
            if table_data:
                # Cria tabela
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), self.secondary_color),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
        
        except Exception as e:
            logger.error(f"❌ Erro ao formatar tabela: {e}")
            elements.append(Paragraph(text, self.styles['Normal']))
        
        return elements
    
    def _is_quote(self, text: str) -> bool:
        """Verifica se é uma citação"""
        return text.startswith('>') or text.startswith('"') and text.endswith('"')
    
    def _format_quote(self, text: str) -> List:
        """Formata citações"""
        elements = []
        quote_text = text.lstrip('> ').strip('"')
        elements.append(Paragraph(f'"{quote_text}"', self.styles['Quote']))
        return elements
    
    def _is_highlight(self, text: str) -> bool:
        """Verifica se é um destaque"""
        highlight_keywords = ['IMPORTANTE', 'ATENÇÃO', 'DESTAQUE', 'NOTA', 'AVISO']
        return any(keyword in text.upper() for keyword in highlight_keywords)
    
    def _format_highlight(self, text: str) -> List:
        """Formata destaques"""
        elements = []
        elements.append(Paragraph(text, self.styles['Highlight']))
        return elements
    
    def _format_paragraph(self, text: str) -> List:
        """Formata parágrafo normal com formatação avançada"""
        elements = []
        formatted_text = self._apply_advanced_formatting(text)
        elements.append(Paragraph(formatted_text, self.styles['Normal']))
        return elements
    
    def _clean_html_content(self, content: str) -> str:
        """Remove tags HTML e limpa conteúdo"""
        try:
            # Remove tags HTML
            clean_content = re.sub(r'<[^>]+>', '', content)
            
            # Decodifica entidades HTML
            clean_content = clean_content.replace('&nbsp;', ' ')
            clean_content = clean_content.replace('&amp;', '&')
            clean_content = clean_content.replace('&lt;', '<')
            clean_content = clean_content.replace('&gt;', '>')
            clean_content = clean_content.replace('&quot;', '"')
            
            # Remove espaços extras
            clean_content = re.sub(r'\s+', ' ', clean_content)
            clean_content = re.sub(r'\n\s*\n', '\n\n', clean_content)
            
            return clean_content.strip()
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar HTML: {e}")
            return content
    
    def _apply_advanced_formatting(self, text: str) -> str:
        """Aplica formatação avançada ao texto"""
        try:
            # Bold (markdown e HTML)
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'<strong>(.*?)</strong>', r'<b>\1</b>', text)
            
            # Italic (markdown e HTML)
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            text = re.sub(r'<em>(.*?)</em>', r'<i>\1</i>', text)
            
            # Underline
            text = re.sub(r'<u>(.*?)</u>', r'<u>\1</u>', text)
            
            # Links (converte para texto simples com URL)
            text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', text)
            text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', r'\2 (\1)', text)
            
            # Código inline
            text = re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)
            
            # Destaque com cor
            text = re.sub(r'==([^=]+)==', r'<font color="#e74c3c"><b>\1</b></font>', text)
            
            return text
            
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar formatação avançada: {e}")
            return text
    
    def _apply_basic_formatting(self, text: str) -> str:
        """Aplica formatação básica ao texto (mantido para compatibilidade)"""
        return self._apply_advanced_formatting(text)
    
    def _generate_automatic_conclusions(self, report_data: Dict[str, Any]) -> List[str]:
        """Gera conclusões automáticas baseadas nos dados do relatório"""
        conclusions = []
        
        try:
            # Análise baseada nos módulos presentes
            if 'modules' in report_data:
                modules = report_data['modules']
                
                if 'concorrencia' in modules:
                    conclusions.append("Identificados concorrentes principais que devem ser monitorados continuamente")
                
                if 'palavras_chave' in modules:
                    conclusions.append("Estratégia de SEO deve focar nas palavras-chave de alta relevância identificadas")
                
                if 'avatars' in modules:
                    conclusions.append("Personas definidas fornecem direcionamento claro para campanhas de marketing")
                
                if 'funil_vendas' in modules:
                    conclusions.append("Funil de vendas otimizado pode aumentar significativamente as conversões")
                
                if 'insights_mercado' in modules:
                    conclusions.append("Insights de mercado revelam oportunidades de crescimento específicas")
            
            # Conclusões gerais
            conclusions.extend([
                "Implementação das recomendações deve ser priorizada por impacto e facilidade",
                "Monitoramento contínuo é essencial para manter vantagem competitiva",
                "Análises regulares permitirão ajustes estratégicos oportunos"
            ])
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar conclusões automáticas: {e}")
            conclusions.append("Análise completa dos dados fornece base sólida para decisões estratégicas")
        
        return conclusions

# Instância global
pdf_report_generator = PDFReportGenerator() if REPORTLAB_AVAILABLE else None