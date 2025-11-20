"""
Serviço de Verificação de Fontes
Analisa, classifica e valida fontes coletadas durante a pesquisa
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import requests
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class FonteAnalise:
    """Estrutura para análise de fonte"""
    url: str
    titulo: str
    dominio: str
    tipo_fonte: str  # 'site', 'blog', 'rede_social', 'canal_youtube', 'empresa', 'influencer'
    categoria: str  # 'concorrente', 'fornecedor', 'cliente', 'parceiro', 'midia'
    relevancia_score: float  # 0-10
    confiabilidade_score: float  # 0-10
    status: str  # 'aprovada', 'rejeitada', 'pendente'
    motivo_status: str
    data_analise: str
    conteudo_resumo: str
    palavras_chave: List[str]
    metricas: Dict[str, any]

class FonteVerificationService:
    """Serviço para verificação e classificação de fontes"""
    
    def __init__(self):
        self.fontes_aprovadas = []
        self.fontes_rejeitadas = []
        self.fontes_pendentes = []
        self.criterios_aprovacao = self._definir_criterios()
        
    def _definir_criterios(self) -> Dict:
        """Define critérios para aprovação de fontes"""
        return {
            'dominios_confiaveis': [
                'gov.br', 'edu.br', 'org.br',
                'wikipedia.org', 'linkedin.com',
                'youtube.com', 'instagram.com',
                'facebook.com', 'twitter.com',
                'medium.com', 'forbes.com',
                'estadao.com.br', 'folha.uol.com.br',
                'g1.globo.com', 'bbc.com',
                'reuters.com', 'bloomberg.com'
            ],
            'dominios_suspeitos': [
                'blogspot.com', 'wordpress.com',
                'wix.com', 'weebly.com'
            ],
            'palavras_spam': [
                'click here', 'buy now', 'limited time',
                'miracle cure', 'get rich quick',
                'compre agora', 'oferta limitada'
            ],
            'min_relevancia': 6.0,
            'min_confiabilidade': 7.0
        }
    
    def analisar_fonte(self, url: str, titulo: str = "", conteudo: str = "", contexto: str = "") -> FonteAnalise:
        """Analisa uma fonte e retorna classificação completa"""
        try:
            dominio = self._extrair_dominio(url)
            tipo_fonte = self._classificar_tipo_fonte(url, dominio)
            categoria = self._classificar_categoria(url, titulo, conteudo, contexto)
            
            # Scores de análise
            relevancia_score = self._calcular_relevancia(url, titulo, conteudo, contexto)
            confiabilidade_score = self._calcular_confiabilidade(url, dominio, conteudo)
            
            # Determinar status
            status, motivo = self._determinar_status(relevancia_score, confiabilidade_score, dominio, conteudo)
            
            # Extrair palavras-chave
            palavras_chave = self._extrair_palavras_chave(titulo, conteudo)
            
            # Métricas adicionais
            metricas = self._coletar_metricas(url, dominio)
            
            fonte_analise = FonteAnalise(
                url=url,
                titulo=titulo or "Título não disponível",
                dominio=dominio,
                tipo_fonte=tipo_fonte,
                categoria=categoria,
                relevancia_score=relevancia_score,
                confiabilidade_score=confiabilidade_score,
                status=status,
                motivo_status=motivo,
                data_analise=datetime.now().isoformat(),
                conteudo_resumo=self._gerar_resumo(conteudo),
                palavras_chave=palavras_chave,
                metricas=metricas
            )
            
            # Adicionar à lista apropriada
            self._categorizar_fonte(fonte_analise)
            
            logger.info(f"✅ Fonte analisada: {dominio} - Status: {status} - Relevância: {relevancia_score:.1f}")
            return fonte_analise
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar fonte {url}: {e}")
            return self._criar_fonte_erro(url, str(e))
    
    def _extrair_dominio(self, url: str) -> str:
        """Extrai domínio da URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return "dominio_invalido"
    
    def _classificar_tipo_fonte(self, url: str, dominio: str) -> str:
        """Classifica o tipo da fonte"""
        url_lower = url.lower()
        dominio_lower = dominio.lower()
        
        if 'youtube.com' in dominio_lower or 'youtu.be' in dominio_lower:
            return 'canal_youtube'
        elif any(social in dominio_lower for social in ['instagram.com', 'facebook.com', 'twitter.com', 'linkedin.com', 'tiktok.com']):
            return 'rede_social'
        elif any(blog in dominio_lower for blog in ['blog', 'medium.com', 'blogspot', 'wordpress']):
            return 'blog'
        elif any(empresa in dominio_lower for empresa in ['.com.br', '.com', '.org', '.net']):
            if 'about' in url_lower or 'empresa' in url_lower or 'company' in url_lower:
                return 'empresa'
            return 'site'
        else:
            return 'site'
    
    def _classificar_categoria(self, url: str, titulo: str, conteudo: str, contexto: str) -> str:
        """Classifica a categoria da fonte"""
        texto_completo = f"{titulo} {conteudo} {contexto}".lower()
        
        # Palavras-chave para cada categoria
        categorias = {
            'concorrente': ['concorrente', 'competitor', 'rival', 'similar', 'alternativa', 'versus'],
            'fornecedor': ['fornecedor', 'supplier', 'vendor', 'parceiro', 'distribuidor'],
            'cliente': ['cliente', 'customer', 'consumidor', 'usuário', 'comprador'],
            'midia': ['notícia', 'news', 'jornal', 'revista', 'imprensa', 'mídia'],
            'influencer': ['influencer', 'youtuber', 'blogger', 'creator', 'personalidade']
        }
        
        scores = {}
        for categoria, palavras in categorias.items():
            score = sum(1 for palavra in palavras if palavra in texto_completo)
            scores[categoria] = score
        
        # Retorna categoria com maior score, ou 'geral' se empate
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                return max(scores, key=scores.get)
        
        return 'geral'
    
    def _calcular_relevancia(self, url: str, titulo: str, conteudo: str, contexto: str) -> float:
        """Calcula score de relevância (0-10)"""
        score = 5.0  # Base
        
        # Fatores positivos
        if titulo and len(titulo) > 10:
            score += 1.0
        
        if conteudo and len(conteudo) > 100:
            score += 1.0
        
        if contexto:
            score += 0.5
        
        # Domínio confiável
        dominio = self._extrair_dominio(url)
        if any(conf in dominio for conf in self.criterios_aprovacao['dominios_confiaveis']):
            score += 1.5
        
        # Conteúdo relevante
        texto_completo = f"{titulo} {conteudo}".lower()
        palavras_relevantes = ['mercado', 'análise', 'estratégia', 'negócio', 'empresa', 'produto', 'serviço']
        relevancia_conteudo = sum(1 for palavra in palavras_relevantes if palavra in texto_completo)
        score += min(relevancia_conteudo * 0.3, 2.0)
        
        return min(score, 10.0)
    
    def _calcular_confiabilidade(self, url: str, dominio: str, conteudo: str) -> float:
        """Calcula score de confiabilidade (0-10)"""
        score = 5.0  # Base
        
        # Domínio confiável
        if any(conf in dominio for conf in self.criterios_aprovacao['dominios_confiaveis']):
            score += 3.0
        elif any(susp in dominio for susp in self.criterios_aprovacao['dominios_suspeitos']):
            score -= 2.0
        
        # HTTPS
        if url.startswith('https://'):
            score += 1.0
        
        # Conteúdo spam
        if conteudo:
            conteudo_lower = conteudo.lower()
            spam_count = sum(1 for spam in self.criterios_aprovacao['palavras_spam'] if spam in conteudo_lower)
            score -= spam_count * 0.5
        
        # Estrutura da URL
        if len(url.split('/')) > 6:  # URL muito longa pode ser suspeita
            score -= 0.5
        
        return max(min(score, 10.0), 0.0)
    
    def _determinar_status(self, relevancia: float, confiabilidade: float, dominio: str, conteudo: str) -> Tuple[str, str]:
        """Determina status da fonte e motivo"""
        
        # Critérios de rejeição automática
        if confiabilidade < 3.0:
            return 'rejeitada', 'Confiabilidade muito baixa'
        
        if relevancia < 3.0:
            return 'rejeitada', 'Relevância muito baixa'
        
        # Spam detection
        if conteudo:
            spam_count = sum(1 for spam in self.criterios_aprovacao['palavras_spam'] if spam.lower() in conteudo.lower())
            if spam_count > 2:
                return 'rejeitada', 'Conteúdo identificado como spam'
        
        # Critérios de aprovação
        if (relevancia >= self.criterios_aprovacao['min_relevancia'] and 
            confiabilidade >= self.criterios_aprovacao['min_confiabilidade']):
            return 'aprovada', f'Relevância: {relevancia:.1f}, Confiabilidade: {confiabilidade:.1f}'
        
        # Casos intermediários
        if relevancia >= 5.0 and confiabilidade >= 5.0:
            return 'pendente', 'Requer análise manual adicional'
        
        return 'rejeitada', f'Scores insuficientes - R: {relevancia:.1f}, C: {confiabilidade:.1f}'
    
    def _extrair_palavras_chave(self, titulo: str, conteudo: str) -> List[str]:
        """Extrai palavras-chave relevantes"""
        texto = f"{titulo} {conteudo}".lower()
        
        # Remove pontuação e divide em palavras
        palavras = re.findall(r'\b[a-záàâãéêíóôõúç]{3,}\b', texto)
        
        # Remove stop words
        stop_words = {
            'que', 'para', 'com', 'uma', 'por', 'são', 'mais', 'como', 'seu', 'sua',
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his'
        }
        
        palavras_filtradas = [p for p in palavras if p not in stop_words and len(p) > 3]
        
        # Conta frequência
        freq = {}
        for palavra in palavras_filtradas:
            freq[palavra] = freq.get(palavra, 0) + 1
        
        # Retorna top 10 palavras mais frequentes
        return sorted(freq.keys(), key=freq.get, reverse=True)[:10]
    
    def _gerar_resumo(self, conteudo: str, max_chars: int = 200) -> str:
        """Gera resumo do conteúdo"""
        if not conteudo:
            return "Conteúdo não disponível"
        
        # Remove HTML tags se houver
        conteudo_limpo = re.sub(r'<[^>]+>', '', conteudo)
        
        # Pega primeiras frases até o limite
        if len(conteudo_limpo) <= max_chars:
            return conteudo_limpo
        
        resumo = conteudo_limpo[:max_chars]
        ultimo_ponto = resumo.rfind('.')
        if ultimo_ponto > max_chars * 0.7:  # Se há um ponto próximo ao final
            resumo = resumo[:ultimo_ponto + 1]
        else:
            resumo += "..."
        
        return resumo
    
    def _coletar_metricas(self, url: str, dominio: str) -> Dict:
        """Coleta métricas adicionais da fonte"""
        metricas = {
            'data_coleta': datetime.now().isoformat(),
            'url_length': len(url),
            'domain_age_estimate': self._estimar_idade_dominio(dominio),
            'https_enabled': url.startswith('https://'),
            'subdomain_count': len(dominio.split('.')) - 2
        }
        
        return metricas
    
    def _estimar_idade_dominio(self, dominio: str) -> str:
        """Estima idade do domínio baseado em padrões conhecidos"""
        dominios_antigos = ['google.com', 'yahoo.com', 'microsoft.com', 'amazon.com', 'facebook.com']
        dominios_conhecidos = ['youtube.com', 'instagram.com', 'twitter.com', 'linkedin.com']
        
        if any(antigo in dominio for antigo in dominios_antigos):
            return 'muito_antigo'
        elif any(conhecido in dominio for conhecido in dominios_conhecidos):
            return 'antigo'
        elif '.gov' in dominio or '.edu' in dominio:
            return 'institucional'
        else:
            return 'desconhecido'
    
    def _categorizar_fonte(self, fonte: FonteAnalise):
        """Adiciona fonte à lista apropriada"""
        if fonte.status == 'aprovada':
            self.fontes_aprovadas.append(fonte)
        elif fonte.status == 'rejeitada':
            self.fontes_rejeitadas.append(fonte)
        else:
            self.fontes_pendentes.append(fonte)
    
    def _criar_fonte_erro(self, url: str, erro: str) -> FonteAnalise:
        """Cria fonte com erro para casos de falha"""
        return FonteAnalise(
            url=url,
            titulo="Erro na análise",
            dominio=self._extrair_dominio(url),
            tipo_fonte="erro",
            categoria="erro",
            relevancia_score=0.0,
            confiabilidade_score=0.0,
            status="rejeitada",
            motivo_status=f"Erro na análise: {erro}",
            data_analise=datetime.now().isoformat(),
            conteudo_resumo="Erro ao processar conteúdo",
            palavras_chave=[],
            metricas={}
        )
    
    def gerar_relatorio_verificacao(self) -> Dict:
        """Gera relatório completo de verificação de fontes"""
        total_fontes = len(self.fontes_aprovadas) + len(self.fontes_rejeitadas) + len(self.fontes_pendentes)
        
        relatorio = {
            'resumo': {
                'total_fontes_analisadas': total_fontes,
                'fontes_aprovadas': len(self.fontes_aprovadas),
                'fontes_rejeitadas': len(self.fontes_rejeitadas),
                'fontes_pendentes': len(self.fontes_pendentes),
                'taxa_aprovacao': (len(self.fontes_aprovadas) / total_fontes * 100) if total_fontes > 0 else 0,
                'data_relatorio': datetime.now().isoformat()
            },
            'fontes_aprovadas': [asdict(fonte) for fonte in self.fontes_aprovadas],
            'fontes_rejeitadas': [asdict(fonte) for fonte in self.fontes_rejeitadas],
            'fontes_pendentes': [asdict(fonte) for fonte in self.fontes_pendentes],
            'estatisticas': self._gerar_estatisticas(),
            'criterios_utilizados': self.criterios_aprovacao
        }
        
        return relatorio
    
    def _gerar_estatisticas(self) -> Dict:
        """Gera estatísticas detalhadas"""
        todas_fontes = self.fontes_aprovadas + self.fontes_rejeitadas + self.fontes_pendentes
        
        if not todas_fontes:
            return {}
        
        # Estatísticas por tipo
        tipos = {}
        categorias = {}
        dominios = {}
        
        for fonte in todas_fontes:
            tipos[fonte.tipo_fonte] = tipos.get(fonte.tipo_fonte, 0) + 1
            categorias[fonte.categoria] = categorias.get(fonte.categoria, 0) + 1
            dominios[fonte.dominio] = dominios.get(fonte.dominio, 0) + 1
        
        # Scores médios
        relevancia_media = sum(f.relevancia_score for f in todas_fontes) / len(todas_fontes)
        confiabilidade_media = sum(f.confiabilidade_score for f in todas_fontes) / len(todas_fontes)
        
        return {
            'distribuicao_tipos': tipos,
            'distribuicao_categorias': categorias,
            'top_dominios': dict(sorted(dominios.items(), key=lambda x: x[1], reverse=True)[:10]),
            'scores_medios': {
                'relevancia': round(relevancia_media, 2),
                'confiabilidade': round(confiabilidade_media, 2)
            },
            'motivos_rejeicao': self._analisar_motivos_rejeicao()
        }
    
    def _analisar_motivos_rejeicao(self) -> Dict:
        """Analisa motivos de rejeição mais comuns"""
        motivos = {}
        for fonte in self.fontes_rejeitadas:
            motivo = fonte.motivo_status
            motivos[motivo] = motivos.get(motivo, 0) + 1
        
        return dict(sorted(motivos.items(), key=lambda x: x[1], reverse=True))
    
    def salvar_relatorio(self, caminho: str = None) -> str:
        """Salva relatório em arquivo JSON"""
        if not caminho:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho = f"relatorios_intermediarios/verificacao_fontes_{timestamp}.json"
        
        relatorio = self.gerar_relatorio_verificacao()
        
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Relatório de verificação salvo: {caminho}")
            return caminho
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")
            return ""
    
    def limpar_fontes(self):
        """Limpa todas as listas de fontes"""
        self.fontes_aprovadas.clear()
        self.fontes_rejeitadas.clear()
        self.fontes_pendentes.clear()
        logger.info("🧹 Listas de fontes limpas")