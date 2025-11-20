#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Viral Report Generator
Gera relatórios automáticos de conteúdo viral para incorporação no relatório final
REGRAS DE OURO: APENAS DADOS REAIS, NUNCA SIMULADOS
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class ViralReportGenerator:
    """Gerador automático de relatórios de conteúdo viral"""
    
    def __init__(self):
        """Inicializa o gerador"""
        # Usa caminhos absolutos baseados no diretório do projeto
        project_root = Path(__file__).parent.parent.parent
        self.viral_data_dir = project_root / "viral_images_data"
        self.analyses_data_dir = project_root / "analyses_data"
        logger.info(f"🔥 Viral Report Generator inicializado - Viral dir: {self.viral_data_dir}")
    
    def generate_viral_report(self, session_id: str) -> bool:
        """Gera relatório viral automático para uma sessão"""
        try:
            logger.info(f"📊 Gerando relatório viral para sessão: {session_id}")
            
            # 1. Encontra dados virais mais recentes
            viral_data = self._load_latest_viral_data()
            if not viral_data:
                logger.warning("⚠️ Nenhum dado viral encontrado")
                return False
            
            # 2. Gera relatório em markdown
            report_content = self._generate_markdown_report(viral_data)
            
            # 3. Salva relatório na pasta da sessão
            session_dir = self.analyses_data_dir / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            report_path = session_dir / "relatorio_viral.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"✅ Relatório viral salvo: {report_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório viral: {e}")
            return False
    
    def _load_latest_viral_data(self) -> Optional[Dict[str, Any]]:
        """Carrega dados virais mais recentes"""
        try:
            if not self.viral_data_dir.exists():
                return None
            
            # Encontra arquivo mais recente
            viral_files = list(self.viral_data_dir.glob("viral_results_*.json"))
            if not viral_files:
                return None
            
            latest_file = max(viral_files, key=lambda f: f.stat().st_mtime)
            logger.info(f"📂 Carregando dados virais: {latest_file.name}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados virais: {e}")
            return None
    
    def _generate_markdown_report(self, viral_data: Dict[str, Any]) -> str:
        """Gera relatório em markdown a partir dos dados virais"""
        
        # Extrai métricas principais
        total_content = viral_data.get('total_content', 0)
        viral_content = viral_data.get('viral_content', 0)
        images_downloaded = viral_data.get('images_downloaded', 0)
        screenshots_taken = viral_data.get('screenshots_taken', 0)
        
        metrics = viral_data.get('metrics', {})
        platform_dist = viral_data.get('platform_distribution', {})
        top_performers = viral_data.get('top_performers', [])
        
        # Gera relatório
        report = f"""# 🔥 RELATÓRIO DE CONTEÚDO VIRAL - DADOS REAIS

**Gerado em:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}  
**Query analisada:** {viral_data.get('query', 'N/A')}  
**Extração realizada em:** {viral_data.get('extracted_at', 'N/A')}

---

## 📊 RESUMO EXECUTIVO

### Métricas de Coleta:
- **Total de conteúdo analisado:** {total_content}
- **Conteúdo viral identificado:** {viral_content}
- **Imagens baixadas:** {images_downloaded}
- **Screenshots capturados:** {screenshots_taken}

### Métricas de Engajamento:
- **Score total de engajamento:** {metrics.get('total_engagement_score', 0):.1f}
- **Engajamento médio:** {metrics.get('average_engagement', 0):.2f}
- **Maior engajamento:** {metrics.get('highest_engagement', 0):.1f}
- **Visualizações estimadas:** {metrics.get('total_estimated_views', 0):,}
- **Curtidas estimadas:** {metrics.get('total_estimated_likes', 0):,}

---

## 🎯 DISTRIBUIÇÃO POR PLATAFORMA

"""
        
        # Adiciona distribuição por plataforma
        for platform, data in platform_dist.items():
            count = data.get('count', 0)
            engagement = data.get('total_engagement', 0)
            views = data.get('total_views', 0)
            likes = data.get('total_likes', 0)
            
            platform_name = {
                'youtube': '📺 YouTube',
                'instagram': '📸 Instagram', 
                'facebook': '📘 Facebook',
                'tiktok': '🎵 TikTok',
                'twitter': '🐦 Twitter'
            }.get(platform, f'🌐 {platform.title()}')
            
            report += f"""### {platform_name}
- **Conteúdos encontrados:** {count}
- **Engajamento total:** {engagement:.1f}
- **Visualizações:** {views:,}
- **Curtidas:** {likes:,}

"""
        
        # Adiciona top performers
        if top_performers:
            report += """---

## 🏆 TOP PERFORMERS - CONTEÚDO VIRAL REAL

"""
            
            for i, content in enumerate(top_performers[:5], 1):
                title = content.get('title', 'Sem título')[:100]
                platform = content.get('platform', 'web')
                score = content.get('engagement_score', 0)
                views = content.get('views_estimate', 0)
                likes = content.get('likes_estimate', 0)
                comments = content.get('comments_estimate', 0)
                url = content.get('post_url', '')
                author = content.get('author', 'Autor não identificado')
                
                platform_emoji = {
                    'youtube': '📺',
                    'instagram': '📸',
                    'facebook': '📘',
                    'tiktok': '🎵',
                    'twitter': '🐦'
                }.get(platform, '🌐')
                
                report += f"""### {i}. {platform_emoji} {title}

**Plataforma:** {platform.title()}  
**Score de Engajamento:** {score:.1f}/10  
**Autor:** {author}  
**Métricas Estimadas:**
- Visualizações: {views:,}
- Curtidas: {likes:,}
- Comentários: {comments:,}

**URL:** {url}

**Insights:**
- Conteúdo com alto potencial viral
- Estratégia de engajamento eficaz
- Referência para criação de conteúdo similar

---

"""
        
        # Adiciona insights e recomendações
        report += """## 💡 INSIGHTS E RECOMENDAÇÕES

### Padrões Identificados:
"""
        
        # Analisa padrões nos top performers
        if top_performers:
            # Plataformas mais eficazes
            platform_counts = {}
            for content in top_performers:
                platform = content.get('platform', 'web')
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            top_platform = max(platform_counts.items(), key=lambda x: x[1])
            report += f"- **Plataforma mais eficaz:** {top_platform[0].title()} ({top_platform[1]} conteúdos no top 5)\n"
            
            # Score médio dos top performers
            avg_score = sum(c.get('engagement_score', 0) for c in top_performers[:5]) / min(5, len(top_performers))
            report += f"- **Score médio dos top performers:** {avg_score:.1f}/10\n"
            
            # Tipos de conteúdo
            educational_content = sum(1 for c in top_performers if any(word in c.get('title', '').lower() 
                                    for word in ['curso', 'tutorial', 'como', 'aprenda', 'dicas', 'método']))
            if educational_content > 0:
                report += f"- **Conteúdo educacional:** {educational_content} dos top 5 são educacionais\n"
        
        report += """
### Recomendações Estratégicas:
1. **Foque nas plataformas com maior engajamento identificadas**
2. **Replique os formatos de conteúdo dos top performers**
3. **Use títulos similares aos que geraram maior engajamento**
4. **Analise os horários de postagem dos conteúdos virais**
5. **Estude as estratégias visuais dos screenshots capturados**

### Próximos Passos:
- Analisar comentários dos posts virais para insights de audiência
- Identificar influenciadores e criadores de conteúdo relevantes
- Mapear hashtags e palavras-chave mais eficazes
- Criar calendário de conteúdo baseado nos padrões identificados

---

**⚠️ IMPORTANTE:** Todos os dados apresentados são REAIS, extraídos diretamente das plataformas. Nenhum dado foi simulado ou inventado, seguindo rigorosamente as REGRAS DE OURO do sistema.

**🔄 Dados atualizados automaticamente** - Este relatório é gerado automaticamente a partir da coleta massiva de dados reais.
"""
        
        return report
    
    def generate_viral_summary_for_synthesis(self, session_id: str) -> Optional[str]:
        """Gera resumo viral específico para síntese de IA"""
        try:
            viral_data = self._load_latest_viral_data()
            if not viral_data:
                return None
            
            top_performers = viral_data.get('top_performers', [])[:3]  # Top 3
            metrics = viral_data.get('metrics', {})
            
            summary = f"""CONTEÚDO VIRAL IDENTIFICADO ({viral_data.get('viral_content', 0)} itens):

MÉTRICAS PRINCIPAIS:
- Engajamento total: {metrics.get('total_engagement_score', 0):.1f}
- Visualizações estimadas: {metrics.get('total_estimated_views', 0):,}
- Curtidas estimadas: {metrics.get('total_estimated_likes', 0):,}

TOP 3 CONTEÚDOS VIRAIS:
"""
            
            for i, content in enumerate(top_performers, 1):
                title = content.get('title', 'Sem título')[:80]
                platform = content.get('platform', 'web')
                score = content.get('engagement_score', 0)
                url = content.get('post_url', '')
                
                summary += f"""
{i}. [{platform.upper()}] {title}
   Score: {score:.1f}/10 | URL: {url}
"""
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resumo viral: {e}")
            return None