"""
Serviço de Coleta de Fontes
Gerencia e organiza todas as fontes coletadas durante a análise
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse
from dataclasses import dataclass, asdict
import requests

logger = logging.getLogger(__name__)

@dataclass
class FonteColetada:
    """Estrutura para fonte coletada"""
    url: str
    titulo: str
    descricao: str
    tipo: str  # 'website', 'youtube', 'instagram', 'linkedin', 'facebook', 'twitter', 'empresa', 'blog'
    categoria: str  # 'concorrente', 'influencer', 'marca', 'canal', 'empresa', 'fornecedor', 'cliente'
    relevancia: str  # 'alta', 'media', 'baixa'
    status: str  # 'ativa', 'inativa', 'verificando'
    seguidores: Optional[int]
    engajamento: Optional[float]
    data_coleta: str
    tags: List[str]
    metricas: Dict[str, any]
    conteudo_sample: str
    contato_info: Dict[str, str]

class FonteCollectionService:
    """Serviço para coleta e organização de fontes"""
    
    def __init__(self):
        self.fontes_coletadas: List[FonteColetada] = []
        self.urls_processadas: Set[str] = set()
        self.categorias_config = self._definir_categorias()
        
    def _definir_categorias(self) -> Dict:
        """Define configurações de categorias"""
        return {
            'concorrente': {
                'palavras_chave': ['competitor', 'rival', 'similar', 'alternative', 'versus', 'concorrente'],
                'dominios_comuns': ['.com', '.com.br', '.net', '.org'],
                'indicadores': ['empresa', 'negócio', 'produto', 'serviço']
            },
            'influencer': {
                'palavras_chave': ['influencer', 'creator', 'youtuber', 'blogger', 'personalidade'],
                'dominios_comuns': ['youtube.com', 'instagram.com', 'tiktok.com', 'twitter.com'],
                'indicadores': ['seguidores', 'subscribers', 'followers', 'views']
            },
            'marca': {
                'palavras_chave': ['brand', 'marca', 'company', 'corporation', 'enterprise'],
                'dominios_comuns': ['.com', '.com.br', '.net'],
                'indicadores': ['produtos', 'services', 'about', 'empresa']
            },
            'canal': {
                'palavras_chave': ['channel', 'canal', 'tv', 'media', 'broadcast'],
                'dominios_comuns': ['youtube.com', 'twitch.tv', 'vimeo.com'],
                'indicadores': ['videos', 'episodes', 'shows', 'content']
            }
        }
    
    def coletar_fonte(self, url: str, titulo: str = "", descricao: str = "", contexto: str = "") -> FonteColetada:
        """Coleta e processa uma nova fonte"""
        try:
            # Evita duplicatas
            if url in self.urls_processadas:
                logger.info(f"⚠️ URL já processada: {url}")
                return self._encontrar_fonte_por_url(url)
            
            # Extrai informações básicas
            dominio = self._extrair_dominio(url)
            tipo = self._identificar_tipo(url, dominio)
            categoria = self._identificar_categoria(url, titulo, descricao, contexto)
            
            # Coleta métricas e informações adicionais
            metricas = self._coletar_metricas_fonte(url, tipo)
            contato_info = self._extrair_contato_info(url, titulo, descricao)
            
            # Determina relevância
            relevancia = self._calcular_relevancia(url, titulo, descricao, metricas)
            
            # Extrai tags
            tags = self._extrair_tags(url, titulo, descricao, contexto)
            
            # Coleta sample de conteúdo
            conteudo_sample = self._coletar_conteudo_sample(url, titulo, descricao)
            
            fonte = FonteColetada(
                url=url,
                titulo=titulo or self._extrair_titulo_url(url),
                descricao=descricao or "Descrição não disponível",
                tipo=tipo,
                categoria=categoria,
                relevancia=relevancia,
                status='verificando',
                seguidores=metricas.get('seguidores'),
                engajamento=metricas.get('engajamento'),
                data_coleta=datetime.now().isoformat(),
                tags=tags,
                metricas=metricas,
                conteudo_sample=conteudo_sample,
                contato_info=contato_info
            )
            
            self.fontes_coletadas.append(fonte)
            self.urls_processadas.add(url)
            
            logger.info(f"✅ Fonte coletada: {dominio} - Tipo: {tipo} - Categoria: {categoria}")
            return fonte
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar fonte {url}: {e}")
            return self._criar_fonte_erro(url, str(e))
    
    def _extrair_dominio(self, url: str) -> str:
        """Extrai domínio da URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return "dominio_invalido"
    
    def _identificar_tipo(self, url: str, dominio: str) -> str:
        """Identifica tipo da fonte baseado na URL e domínio"""
        url_lower = url.lower()
        dominio_lower = dominio.lower()
        
        tipos_mapeamento = {
            'youtube.com': 'youtube',
            'youtu.be': 'youtube',
            'instagram.com': 'instagram',
            'facebook.com': 'facebook',
            'twitter.com': 'twitter',
            'linkedin.com': 'linkedin',
            'tiktok.com': 'tiktok',
            'twitch.tv': 'twitch',
            'medium.com': 'blog',
            'blogspot.com': 'blog',
            'wordpress.com': 'blog'
        }
        
        for dominio_key, tipo in tipos_mapeamento.items():
            if dominio_key in dominio_lower:
                return tipo
        
        # Verifica padrões na URL
        if any(blog_indicator in url_lower for blog_indicator in ['blog', '/post/', '/article/']):
            return 'blog'
        elif any(empresa_indicator in url_lower for empresa_indicator in ['/about', '/empresa', '/company']):
            return 'empresa'
        else:
            return 'website'
    
    def _identificar_categoria(self, url: str, titulo: str, descricao: str, contexto: str) -> str:
        """Identifica categoria da fonte"""
        texto_completo = f"{titulo} {descricao} {contexto} {url}".lower()
        
        scores = {}
        for categoria, config in self.categorias_config.items():
            score = 0
            
            # Pontuação por palavras-chave
            for palavra in config['palavras_chave']:
                if palavra in texto_completo:
                    score += 2
            
            # Pontuação por indicadores
            for indicador in config['indicadores']:
                if indicador in texto_completo:
                    score += 1
            
            # Pontuação por domínio
            dominio = self._extrair_dominio(url)
            for dominio_comum in config['dominios_comuns']:
                if dominio_comum in dominio:
                    score += 1
            
            scores[categoria] = score
        
        # Retorna categoria com maior score
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'geral'
    
    def _coletar_metricas_fonte(self, url: str, tipo: str) -> Dict:
        """Coleta métricas específicas por tipo de fonte"""
        metricas = {
            'data_coleta': datetime.now().isoformat(),
            'tipo_fonte': tipo,
            'url_length': len(url),
            'https_enabled': url.startswith('https://')
        }
        
        try:
            if tipo == 'youtube':
                metricas.update(self._coletar_metricas_youtube(url))
            elif tipo == 'instagram':
                metricas.update(self._coletar_metricas_instagram(url))
            elif tipo == 'linkedin':
                metricas.update(self._coletar_metricas_linkedin(url))
            elif tipo in ['website', 'empresa']:
                metricas.update(self._coletar_metricas_website(url))
                
        except Exception as e:
            logger.warning(f"⚠️ Erro ao coletar métricas para {url}: {e}")
            metricas['erro_metricas'] = str(e)
        
        return metricas
    
    def _coletar_metricas_youtube(self, url: str) -> Dict:
        """Coleta métricas específicas do YouTube"""
        metricas = {}
        
        try:
            # Extrai ID do canal/vídeo
            if '/channel/' in url:
                channel_id = url.split('/channel/')[-1].split('/')[0]
                metricas['channel_id'] = channel_id
            elif '/c/' in url:
                channel_name = url.split('/c/')[-1].split('/')[0]
                metricas['channel_name'] = channel_name
            elif '/watch?v=' in url:
                video_id = url.split('v=')[-1].split('&')[0]
                metricas['video_id'] = video_id
                metricas['tipo_conteudo'] = 'video'
            
            # Estimativas baseadas em padrões (sem API real)
            metricas['plataforma'] = 'youtube'
            metricas['tipo_perfil'] = 'canal' if '/channel/' in url or '/c/' in url else 'video'
            
        except Exception as e:
            metricas['erro'] = str(e)
        
        return metricas
    
    def _coletar_metricas_instagram(self, url: str) -> Dict:
        """Coleta métricas específicas do Instagram"""
        metricas = {'plataforma': 'instagram'}
        
        try:
            if '/p/' in url:
                metricas['tipo_conteudo'] = 'post'
            elif '/reel/' in url:
                metricas['tipo_conteudo'] = 'reel'
            elif '/stories/' in url:
                metricas['tipo_conteudo'] = 'story'
            else:
                metricas['tipo_conteudo'] = 'perfil'
            
            # Extrai username
            parts = url.split('/')
            for i, part in enumerate(parts):
                if part == 'instagram.com' and i + 1 < len(parts):
                    username = parts[i + 1]
                    if username and not username.startswith('p'):
                        metricas['username'] = username
                    break
                    
        except Exception as e:
            metricas['erro'] = str(e)
        
        return metricas
    
    def _coletar_metricas_linkedin(self, url: str) -> Dict:
        """Coleta métricas específicas do LinkedIn"""
        metricas = {'plataforma': 'linkedin'}
        
        try:
            if '/company/' in url:
                metricas['tipo_perfil'] = 'empresa'
            elif '/in/' in url:
                metricas['tipo_perfil'] = 'pessoa'
            elif '/school/' in url:
                metricas['tipo_perfil'] = 'escola'
            else:
                metricas['tipo_perfil'] = 'desconhecido'
                
        except Exception as e:
            metricas['erro'] = str(e)
        
        return metricas
    
    def _coletar_metricas_website(self, url: str) -> Dict:
        """Coleta métricas básicas de website"""
        metricas = {}
        
        try:
            # Análise da estrutura da URL
            parsed = urlparse(url)
            metricas['dominio'] = parsed.netloc
            metricas['path_depth'] = len([p for p in parsed.path.split('/') if p])
            metricas['has_query'] = bool(parsed.query)
            metricas['has_fragment'] = bool(parsed.fragment)
            
            # Estimativa de tipo de página
            path = parsed.path.lower()
            if any(about in path for about in ['/about', '/empresa', '/company', '/quem-somos']):
                metricas['tipo_pagina'] = 'sobre'
            elif any(contact in path for contact in ['/contact', '/contato', '/fale-conosco']):
                metricas['tipo_pagina'] = 'contato'
            elif any(product in path for product in ['/product', '/produto', '/servico']):
                metricas['tipo_pagina'] = 'produto'
            elif any(blog in path for blog in ['/blog', '/news', '/noticias']):
                metricas['tipo_pagina'] = 'blog'
            else:
                metricas['tipo_pagina'] = 'geral'
                
        except Exception as e:
            metricas['erro'] = str(e)
        
        return metricas
    
    def _extrair_contato_info(self, url: str, titulo: str, descricao: str) -> Dict:
        """Extrai informações de contato quando disponíveis"""
        contato = {}
        texto_completo = f"{titulo} {descricao}".lower()
        
        # Padrões de email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, texto_completo)
        if emails:
            contato['emails'] = emails[:3]  # Máximo 3 emails
        
        # Padrões de telefone brasileiro
        phone_pattern = r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}'
        phones = re.findall(phone_pattern, texto_completo)
        if phones:
            contato['telefones'] = phones[:2]  # Máximo 2 telefones
        
        # Redes sociais mencionadas
        social_patterns = {
            'instagram': r'@[\w.]+|instagram\.com/[\w.]+',
            'twitter': r'@[\w.]+|twitter\.com/[\w.]+',
            'facebook': r'facebook\.com/[\w.]+',
            'linkedin': r'linkedin\.com/[\w/.]+'
        }
        
        for rede, pattern in social_patterns.items():
            matches = re.findall(pattern, texto_completo)
            if matches:
                contato[f'{rede}_profiles'] = matches[:2]
        
        return contato
    
    def _calcular_relevancia(self, url: str, titulo: str, descricao: str, metricas: Dict) -> str:
        """Calcula relevância da fonte"""
        score = 0
        
        # Fatores de relevância
        if titulo and len(titulo) > 10:
            score += 1
        
        if descricao and len(descricao) > 50:
            score += 1
        
        # Tipo de fonte
        tipo = metricas.get('tipo_fonte', '')
        if tipo in ['youtube', 'instagram', 'linkedin']:
            score += 2
        elif tipo in ['website', 'empresa']:
            score += 1
        
        # HTTPS
        if metricas.get('https_enabled', False):
            score += 1
        
        # Domínio conhecido
        dominio = self._extrair_dominio(url)
        dominios_relevantes = ['youtube.com', 'instagram.com', 'linkedin.com', 'facebook.com']
        if any(dom in dominio for dom in dominios_relevantes):
            score += 1
        
        # Classificação
        if score >= 5:
            return 'alta'
        elif score >= 3:
            return 'media'
        else:
            return 'baixa'
    
    def _extrair_tags(self, url: str, titulo: str, descricao: str, contexto: str) -> List[str]:
        """Extrai tags relevantes"""
        texto_completo = f"{titulo} {descricao} {contexto}".lower()
        
        # Tags predefinidas por categoria
        tags_categorias = {
            'tecnologia': ['tech', 'software', 'app', 'digital', 'tecnologia', 'inovação'],
            'marketing': ['marketing', 'publicidade', 'branding', 'social media', 'seo'],
            'negócios': ['business', 'empresa', 'negócio', 'startup', 'empreendedorismo'],
            'educação': ['educação', 'curso', 'treinamento', 'ensino', 'aprendizado'],
            'saúde': ['saúde', 'medicina', 'wellness', 'fitness', 'nutrição'],
            'entretenimento': ['entretenimento', 'diversão', 'jogos', 'música', 'filme']
        }
        
        tags_encontradas = []
        
        for categoria, palavras in tags_categorias.items():
            for palavra in palavras:
                if palavra in texto_completo:
                    tags_encontradas.append(categoria)
                    break
        
        # Tags baseadas no tipo de fonte
        tipo = self._identificar_tipo(url, self._extrair_dominio(url))
        tags_encontradas.append(tipo)
        
        # Remove duplicatas e limita
        return list(set(tags_encontradas))[:8]
    
    def _coletar_conteudo_sample(self, url: str, titulo: str, descricao: str) -> str:
        """Coleta amostra de conteúdo"""
        conteudo_parts = []
        
        if titulo:
            conteudo_parts.append(f"Título: {titulo}")
        
        if descricao:
            # Limita descrição a 300 caracteres
            desc_limitada = descricao[:300] + "..." if len(descricao) > 300 else descricao
            conteudo_parts.append(f"Descrição: {desc_limitada}")
        
        # Adiciona informações da URL
        dominio = self._extrair_dominio(url)
        conteudo_parts.append(f"Domínio: {dominio}")
        
        return " | ".join(conteudo_parts)
    
    def _extrair_titulo_url(self, url: str) -> str:
        """Extrai título baseado na URL quando não fornecido"""
        try:
            parsed = urlparse(url)
            dominio = parsed.netloc
            
            # Remove www. e extensões
            titulo = dominio.replace('www.', '').split('.')[0]
            
            # Capitaliza primeira letra
            return titulo.capitalize()
            
        except:
            return "Fonte sem título"
    
    def _encontrar_fonte_por_url(self, url: str) -> Optional[FonteColetada]:
        """Encontra fonte já coletada por URL"""
        for fonte in self.fontes_coletadas:
            if fonte.url == url:
                return fonte
        return None
    
    def _criar_fonte_erro(self, url: str, erro: str) -> FonteColetada:
        """Cria fonte com erro"""
        return FonteColetada(
            url=url,
            titulo="Erro na coleta",
            descricao=f"Erro: {erro}",
            tipo="erro",
            categoria="erro",
            relevancia="baixa",
            status="inativa",
            seguidores=None,
            engajamento=None,
            data_coleta=datetime.now().isoformat(),
            tags=["erro"],
            metricas={},
            conteudo_sample="Erro ao coletar conteúdo",
            contato_info={}
        )
    
    def organizar_por_categoria(self) -> Dict[str, List[FonteColetada]]:
        """Organiza fontes por categoria"""
        organizacao = {}
        
        for fonte in self.fontes_coletadas:
            categoria = fonte.categoria
            if categoria not in organizacao:
                organizacao[categoria] = []
            organizacao[categoria].append(fonte)
        
        # Ordena por relevância dentro de cada categoria
        for categoria in organizacao:
            organizacao[categoria].sort(key=lambda x: {'alta': 3, 'media': 2, 'baixa': 1}[x.relevancia], reverse=True)
        
        return organizacao
    
    def organizar_por_tipo(self) -> Dict[str, List[FonteColetada]]:
        """Organiza fontes por tipo"""
        organizacao = {}
        
        for fonte in self.fontes_coletadas:
            tipo = fonte.tipo
            if tipo not in organizacao:
                organizacao[tipo] = []
            organizacao[tipo].append(fonte)
        
        return organizacao
    
    def filtrar_por_relevancia(self, relevancia: str) -> List[FonteColetada]:
        """Filtra fontes por relevância"""
        return [fonte for fonte in self.fontes_coletadas if fonte.relevancia == relevancia]
    
    def filtrar_por_status(self, status: str) -> List[FonteColetada]:
        """Filtra fontes por status"""
        return [fonte for fonte in self.fontes_coletadas if fonte.status == status]
    
    def gerar_relatorio_coleta(self) -> Dict:
        """Gera relatório completo de coleta"""
        total_fontes = len(self.fontes_coletadas)
        
        # Estatísticas básicas
        stats_tipo = {}
        stats_categoria = {}
        stats_relevancia = {}
        stats_status = {}
        
        for fonte in self.fontes_coletadas:
            stats_tipo[fonte.tipo] = stats_tipo.get(fonte.tipo, 0) + 1
            stats_categoria[fonte.categoria] = stats_categoria.get(fonte.categoria, 0) + 1
            stats_relevancia[fonte.relevancia] = stats_relevancia.get(fonte.relevancia, 0) + 1
            stats_status[fonte.status] = stats_status.get(fonte.status, 0) + 1
        
        relatorio = {
            'resumo': {
                'total_fontes_coletadas': total_fontes,
                'data_relatorio': datetime.now().isoformat(),
                'urls_processadas': len(self.urls_processadas)
            },
            'estatisticas': {
                'por_tipo': stats_tipo,
                'por_categoria': stats_categoria,
                'por_relevancia': stats_relevancia,
                'por_status': stats_status
            },
            'fontes_organizadas': {
                'por_categoria': {k: [asdict(f) for f in v] for k, v in self.organizar_por_categoria().items()},
                'por_tipo': {k: [asdict(f) for f in v] for k, v in self.organizar_por_tipo().items()}
            },
            'top_fontes': {
                'alta_relevancia': [asdict(f) for f in self.filtrar_por_relevancia('alta')[:10]],
                'concorrentes': [asdict(f) for f in self.fontes_coletadas if f.categoria == 'concorrente'][:10],
                'influencers': [asdict(f) for f in self.fontes_coletadas if f.categoria == 'influencer'][:10]
            },
            'metricas_gerais': self._calcular_metricas_gerais()
        }
        
        return relatorio
    
    def _calcular_metricas_gerais(self) -> Dict:
        """Calcula métricas gerais da coleta"""
        if not self.fontes_coletadas:
            return {}
        
        # Contadores
        total_com_contato = sum(1 for f in self.fontes_coletadas if f.contato_info)
        total_https = sum(1 for f in self.fontes_coletadas if f.url.startswith('https://'))
        
        # Tags mais comuns
        todas_tags = []
        for fonte in self.fontes_coletadas:
            todas_tags.extend(fonte.tags)
        
        tag_count = {}
        for tag in todas_tags:
            tag_count[tag] = tag_count.get(tag, 0) + 1
        
        top_tags = dict(sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return {
            'fontes_com_contato': total_com_contato,
            'percentual_https': (total_https / len(self.fontes_coletadas)) * 100,
            'tags_mais_comuns': top_tags,
            'media_tags_por_fonte': len(todas_tags) / len(self.fontes_coletadas) if self.fontes_coletadas else 0
        }
    
    def salvar_relatorio(self, caminho: str = None) -> str:
        """Salva relatório em arquivo JSON"""
        if not caminho:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho = f"relatorios_intermediarios/fontes_coletadas_{timestamp}.json"
        
        relatorio = self.gerar_relatorio_coleta()
        
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Relatório de fontes coletadas salvo: {caminho}")
            return caminho
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")
            return ""
    
    def limpar_coleta(self):
        """Limpa todas as fontes coletadas"""
        self.fontes_coletadas.clear()
        self.urls_processadas.clear()
        logger.info("🧹 Coleta de fontes limpa")
    
    def adicionar_fontes_em_lote(self, fontes_data: List[Dict]) -> int:
        """Adiciona múltiplas fontes de uma vez"""
        contador = 0
        
        for fonte_data in fontes_data:
            try:
                url = fonte_data.get('url', '')
                titulo = fonte_data.get('titulo', '')
                descricao = fonte_data.get('descricao', '')
                contexto = fonte_data.get('contexto', '')
                
                if url and url not in self.urls_processadas:
                    self.coletar_fonte(url, titulo, descricao, contexto)
                    contador += 1
                    
            except Exception as e:
                logger.error(f"❌ Erro ao adicionar fonte em lote: {e}")
        
        logger.info(f"✅ {contador} fontes adicionadas em lote")
        return contador