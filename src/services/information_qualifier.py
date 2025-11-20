"""
Sistema de Qualificação de Informação com Tags
Implementa classificação automática e tags visuais para informações
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib

@dataclass
class InformationTag:
    """Tag de qualificação de informação"""
    id: str
    label: str
    description: str
    color: str  # Cor da tag
    icon: str   # Ícone da tag
    confidence_level: str  # high, medium, low
    reliability_score: float  # 0.0 a 1.0
    
@dataclass
class QualifiedInformation:
    """Informação qualificada com tags"""
    content: str
    tags: List[InformationTag]
    confidence_score: float
    data_freshness: str  # fresh, recent, outdated, unknown
    source_quality: str  # verified, unverified, questionable
    verification_status: str  # verified, pending, unverified
    last_updated: Optional[str] = None
    footnote_references: List[int] = None
    
@dataclass
class QualificationSummary:
    """Resumo da qualificação de informações"""
    total_items: int
    tag_distribution: Dict[str, int]
    confidence_distribution: Dict[str, int]
    freshness_distribution: Dict[str, int]
    overall_quality_score: float
    recommendations: List[str]

class InformationQualifier:
    """Sistema principal de qualificação de informação"""
    
    def __init__(self):
        self.tag_definitions = self._load_tag_definitions()
        self.classification_rules = self._load_classification_rules()
        self.freshness_thresholds = self._load_freshness_thresholds()
        
    def _load_tag_definitions(self) -> Dict[str, InformationTag]:
        """Carrega definições das tags de qualificação"""
        tags = {}
        
        # Tags de verificação
        tags['verified'] = InformationTag(
            id='verified',
            label='VERIFICADO',
            description='Informação verificada com múltiplas fontes confiáveis',
            color='#28a745',
            icon='✅',
            confidence_level='high',
            reliability_score=0.9
        )
        
        tags['cross_verified'] = InformationTag(
            id='cross_verified',
            label='VALIDAÇÃO CRUZADA',
            description='Informação confirmada por múltiplas fontes independentes',
            color='#20c997',
            icon='🔄',
            confidence_level='high',
            reliability_score=0.85
        )
        
        tags['unverified'] = InformationTag(
            id='unverified',
            label='NÃO VERIFICADO',
            description='Informação não verificada ou de fonte única',
            color='#6c757d',
            icon='❓',
            confidence_level='low',
            reliability_score=0.3
        )
        
        # Tags de tipo de dados
        tags['statistical'] = InformationTag(
            id='statistical',
            label='DADOS ESTATÍSTICOS',
            description='Informação baseada em dados estatísticos ou pesquisas',
            color='#007bff',
            icon='📊',
            confidence_level='medium',
            reliability_score=0.7
        )
        
        tags['projection'] = InformationTag(
            id='projection',
            label='PROJEÇÃO',
            description='Estimativa ou projeção baseada em modelos',
            color='#fd7e14',
            icon='🔮',
            confidence_level='medium',
            reliability_score=0.6
        )
        
        tags['estimate'] = InformationTag(
            id='estimate',
            label='ESTIMATIVA',
            description='Valor estimado baseado em dados parciais',
            color='#ffc107',
            icon='📏',
            confidence_level='medium',
            reliability_score=0.5
        )
        
        tags['opinion'] = InformationTag(
            id='opinion',
            label='OPINIÃO',
            description='Opinião de especialista ou análise subjetiva',
            color='#6f42c1',
            icon='💭',
            confidence_level='low',
            reliability_score=0.4
        )
        
        # Tags de atualidade
        tags['fresh'] = InformationTag(
            id='fresh',
            label='ATUAL',
            description='Informação recente (últimos 30 dias)',
            color='#28a745',
            icon='🆕',
            confidence_level='high',
            reliability_score=0.8
        )
        
        tags['recent'] = InformationTag(
            id='recent',
            label='RECENTE',
            description='Informação dos últimos 6 meses',
            color='#17a2b8',
            icon='📅',
            confidence_level='medium',
            reliability_score=0.6
        )
        
        tags['outdated'] = InformationTag(
            id='outdated',
            label='DESATUALIZADO',
            description='Informação com mais de 1 ano',
            color='#dc3545',
            icon='⏰',
            confidence_level='low',
            reliability_score=0.3
        )
        
        # Tags de fonte
        tags['official_source'] = InformationTag(
            id='official_source',
            label='FONTE OFICIAL',
            description='Informação de fonte governamental ou institucional oficial',
            color='#155724',
            icon='🏛️',
            confidence_level='high',
            reliability_score=0.95
        )
        
        tags['academic_source'] = InformationTag(
            id='academic_source',
            label='FONTE ACADÊMICA',
            description='Informação de instituição acadêmica ou pesquisa científica',
            color='#004085',
            icon='🎓',
            confidence_level='high',
            reliability_score=0.85
        )
        
        tags['media_source'] = InformationTag(
            id='media_source',
            label='FONTE JORNALÍSTICA',
            description='Informação de veículo de comunicação',
            color='#495057',
            icon='📰',
            confidence_level='medium',
            reliability_score=0.6
        )
        
        tags['blog_source'] = InformationTag(
            id='blog_source',
            label='FONTE INFORMAL',
            description='Informação de blog ou fonte não institucional',
            color='#6c757d',
            icon='📝',
            confidence_level='low',
            reliability_score=0.3
        )
        
        # Tags de confiabilidade
        tags['high_confidence'] = InformationTag(
            id='high_confidence',
            label='ALTA CONFIANÇA',
            description='Informação com alta confiabilidade',
            color='#28a745',
            icon='🎯',
            confidence_level='high',
            reliability_score=0.9
        )
        
        tags['medium_confidence'] = InformationTag(
            id='medium_confidence',
            label='MÉDIA CONFIANÇA',
            description='Informação com confiabilidade moderada',
            color='#ffc107',
            icon='⚖️',
            confidence_level='medium',
            reliability_score=0.6
        )
        
        tags['low_confidence'] = InformationTag(
            id='low_confidence',
            label='BAIXA CONFIANÇA',
            description='Informação com baixa confiabilidade',
            color='#dc3545',
            icon='⚠️',
            confidence_level='low',
            reliability_score=0.3
        )
        
        # Tags especiais
        tags['ai_generated'] = InformationTag(
            id='ai_generated',
            label='GERADO POR IA',
            description='Conteúdo gerado por inteligência artificial',
            color='#e83e8c',
            icon='🤖',
            confidence_level='medium',
            reliability_score=0.5
        )
        
        tags['requires_validation'] = InformationTag(
            id='requires_validation',
            label='REQUER VALIDAÇÃO',
            description='Informação que necessita validação adicional',
            color='#fd7e14',
            icon='🔍',
            confidence_level='low',
            reliability_score=0.4
        )
        
        tags['conflicting_data'] = InformationTag(
            id='conflicting_data',
            label='DADOS CONFLITANTES',
            description='Informação que conflita com outras fontes',
            color='#dc3545',
            icon='⚡',
            confidence_level='low',
            reliability_score=0.2
        )
        
        return tags
    
    def _load_classification_rules(self) -> Dict[str, Dict]:
        """Carrega regras de classificação automática"""
        return {
            'numerical_patterns': {
                'percentage': r'(\d+(?:\.\d+)?)\s*%',
                'currency': r'R\$\s*(\d+(?:\.\d+)?(?:\.\d{3})*(?:,\d{2})?)',
                'large_numbers': r'(\d{1,3}(?:\.\d{3})+)',
                'decimal': r'(\d+,\d+)'
            },
            'source_indicators': {
                'official': ['gov.br', 'ibge', 'bcb', 'cvm', 'anvisa', 'anatel'],
                'academic': ['.edu', 'universidade', 'faculdade', 'instituto', 'pesquisa'],
                'media': ['folha', 'estadao', 'globo', 'uol', 'g1', 'reuters', 'bloomberg'],
                'blog': ['blog', 'wordpress', 'medium', 'linkedin']
            },
            'content_types': {
                'projection': ['projeção', 'previsão', 'estimativa', 'expectativa', 'cenário'],
                'statistical': ['pesquisa', 'estudo', 'dados', 'estatística', 'levantamento'],
                'opinion': ['acredito', 'penso', 'opinião', 'análise', 'perspectiva'],
                'factual': ['segundo', 'conforme', 'de acordo', 'dados mostram']
            },
            'confidence_indicators': {
                'high': ['confirmado', 'verificado', 'comprovado', 'oficial', 'dados oficiais'],
                'medium': ['indica', 'sugere', 'aponta', 'mostra', 'segundo dados'],
                'low': ['pode', 'talvez', 'possivelmente', 'aparentemente', 'parece']
            }
        }
    
    def _load_freshness_thresholds(self) -> Dict[str, int]:
        """Carrega limites de atualidade em dias"""
        return {
            'fresh': 30,      # Últimos 30 dias
            'recent': 180,    # Últimos 6 meses
            'outdated': 365   # Mais de 1 ano
        }
    
    def qualify_information(self, content: str, source_url: str = None, 
                          publication_date: str = None, 
                          source_reliability: float = 0.5) -> QualifiedInformation:
        """Qualifica uma informação específica"""
        
        # Identifica tags aplicáveis
        applicable_tags = self._identify_tags(content, source_url, publication_date, source_reliability)
        
        # Calcula score de confiança
        confidence_score = self._calculate_confidence_score(applicable_tags, source_reliability)
        
        # Determina atualidade dos dados
        data_freshness = self._determine_data_freshness(publication_date)
        
        # Avalia qualidade da fonte
        source_quality = self._evaluate_source_quality(source_url, source_reliability)
        
        # Determina status de verificação
        verification_status = self._determine_verification_status(applicable_tags)
        
        return QualifiedInformation(
            content=content,
            tags=applicable_tags,
            confidence_score=confidence_score,
            data_freshness=data_freshness,
            source_quality=source_quality,
            verification_status=verification_status,
            last_updated=datetime.now().isoformat(),
            footnote_references=[]
        )
    
    def _identify_tags(self, content: str, source_url: str = None, 
                      publication_date: str = None, source_reliability: float = 0.5) -> List[InformationTag]:
        """Identifica tags aplicáveis baseado no conteúdo"""
        tags = []
        content_lower = content.lower()
        
        # Tags baseadas no tipo de conteúdo
        for content_type, keywords in self.classification_rules['content_types'].items():
            if any(keyword in content_lower for keyword in keywords):
                if content_type in self.tag_definitions:
                    tags.append(self.tag_definitions[content_type])
        
        # Tags baseadas em indicadores de confiança
        for confidence_level, indicators in self.classification_rules['confidence_indicators'].items():
            if any(indicator in content_lower for indicator in indicators):
                tag_id = f"{confidence_level}_confidence"
                if tag_id in self.tag_definitions:
                    tags.append(self.tag_definitions[tag_id])
                break  # Usa apenas o primeiro nível encontrado
        
        # Tags baseadas na fonte
        if source_url:
            source_tags = self._classify_source(source_url)
            tags.extend(source_tags)
        
        # Tags baseadas na atualidade
        if publication_date:
            freshness_tag = self._get_freshness_tag(publication_date)
            if freshness_tag:
                tags.append(freshness_tag)
        
        # Tags baseadas em padrões numéricos
        if self._has_numerical_data(content):
            tags.append(self.tag_definitions['statistical'])
        
        # Tag de IA (sempre aplicada)
        tags.append(self.tag_definitions['ai_generated'])
        
        # Remove duplicatas mantendo ordem
        unique_tags = []
        seen_ids = set()
        for tag in tags:
            if tag.id not in seen_ids:
                unique_tags.append(tag)
                seen_ids.add(tag.id)
        
        return unique_tags
    
    def _classify_source(self, source_url: str) -> List[InformationTag]:
        """Classifica fonte baseada na URL"""
        tags = []
        url_lower = source_url.lower()
        
        for source_type, indicators in self.classification_rules['source_indicators'].items():
            if any(indicator in url_lower for indicator in indicators):
                tag_id = f"{source_type}_source"
                if tag_id in self.tag_definitions:
                    tags.append(self.tag_definitions[tag_id])
                break
        
        return tags
    
    def _get_freshness_tag(self, publication_date: str) -> Optional[InformationTag]:
        """Determina tag de atualidade baseada na data"""
        try:
            pub_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00'))
            days_old = (datetime.now() - pub_date).days
            
            if days_old <= self.freshness_thresholds['fresh']:
                return self.tag_definitions['fresh']
            elif days_old <= self.freshness_thresholds['recent']:
                return self.tag_definitions['recent']
            else:
                return self.tag_definitions['outdated']
        except:
            return None
    
    def _has_numerical_data(self, content: str) -> bool:
        """Verifica se o conteúdo contém dados numéricos"""
        for pattern in self.classification_rules['numerical_patterns'].values():
            if re.search(pattern, content):
                return True
        return False
    
    def _calculate_confidence_score(self, tags: List[InformationTag], source_reliability: float) -> float:
        """Calcula score de confiança baseado nas tags"""
        if not tags:
            return source_reliability
        
        # Média ponderada dos scores das tags
        total_score = 0
        total_weight = 0
        
        for tag in tags:
            weight = 1.0
            if tag.confidence_level == 'high':
                weight = 1.5
            elif tag.confidence_level == 'low':
                weight = 0.5
            
            total_score += tag.reliability_score * weight
            total_weight += weight
        
        # Combina com confiabilidade da fonte
        tag_score = total_score / total_weight if total_weight > 0 else 0.5
        combined_score = (tag_score + source_reliability) / 2
        
        return min(1.0, max(0.0, combined_score))
    
    def _determine_data_freshness(self, publication_date: str = None) -> str:
        """Determina atualidade dos dados"""
        if not publication_date:
            return 'unknown'
        
        try:
            pub_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00'))
            days_old = (datetime.now() - pub_date).days
            
            if days_old <= self.freshness_thresholds['fresh']:
                return 'fresh'
            elif days_old <= self.freshness_thresholds['recent']:
                return 'recent'
            else:
                return 'outdated'
        except:
            return 'unknown'
    
    def _evaluate_source_quality(self, source_url: str = None, source_reliability: float = 0.5) -> str:
        """Avalia qualidade da fonte"""
        if not source_url:
            return 'unverified'
        
        if source_reliability >= 0.8:
            return 'verified'
        elif source_reliability >= 0.5:
            return 'unverified'
        else:
            return 'questionable'
    
    def _determine_verification_status(self, tags: List[InformationTag]) -> str:
        """Determina status de verificação baseado nas tags"""
        verification_tags = ['verified', 'cross_verified']
        
        if any(tag.id in verification_tags for tag in tags):
            return 'verified'
        elif any(tag.id == 'requires_validation' for tag in tags):
            return 'pending'
        else:
            return 'unverified'
    
    def qualify_content_batch(self, content_items: List[Dict]) -> List[QualifiedInformation]:
        """Qualifica múltiplos itens de conteúdo"""
        qualified_items = []
        
        for item in content_items:
            qualified = self.qualify_information(
                content=item.get('content', ''),
                source_url=item.get('source_url'),
                publication_date=item.get('publication_date'),
                source_reliability=item.get('source_reliability', 0.5)
            )
            qualified_items.append(qualified)
        
        return qualified_items
    
    def generate_qualification_summary(self, qualified_items: List[QualifiedInformation]) -> QualificationSummary:
        """Gera resumo da qualificação"""
        if not qualified_items:
            return QualificationSummary(
                total_items=0,
                tag_distribution={},
                confidence_distribution={},
                freshness_distribution={},
                overall_quality_score=0.0,
                recommendations=[]
            )
        
        # Distribui tags
        tag_counts = {}
        for item in qualified_items:
            for tag in item.tags:
                tag_counts[tag.label] = tag_counts.get(tag.label, 0) + 1
        
        # Distribui níveis de confiança
        confidence_counts = {'high': 0, 'medium': 0, 'low': 0}
        for item in qualified_items:
            if item.confidence_score >= 0.7:
                confidence_counts['high'] += 1
            elif item.confidence_score >= 0.4:
                confidence_counts['medium'] += 1
            else:
                confidence_counts['low'] += 1
        
        # Distribui atualidade
        freshness_counts = {'fresh': 0, 'recent': 0, 'outdated': 0, 'unknown': 0}
        for item in qualified_items:
            freshness_counts[item.data_freshness] += 1
        
        # Calcula score geral
        overall_score = sum(item.confidence_score for item in qualified_items) / len(qualified_items)
        
        # Gera recomendações
        recommendations = self._generate_quality_recommendations(
            qualified_items, confidence_counts, freshness_counts
        )
        
        return QualificationSummary(
            total_items=len(qualified_items),
            tag_distribution=tag_counts,
            confidence_distribution=confidence_counts,
            freshness_distribution=freshness_counts,
            overall_quality_score=overall_score,
            recommendations=recommendations
        )
    
    def _generate_quality_recommendations(self, items: List[QualifiedInformation],
                                        confidence_dist: Dict[str, int],
                                        freshness_dist: Dict[str, int]) -> List[str]:
        """Gera recomendações baseadas na qualidade"""
        recommendations = []
        total_items = len(items)
        
        # Recomendações baseadas na confiança
        low_confidence_pct = (confidence_dist['low'] / total_items) * 100
        if low_confidence_pct > 30:
            recommendations.append("🔍 Mais de 30% das informações têm baixa confiança - buscar fontes adicionais")
        
        # Recomendações baseadas na atualidade
        outdated_pct = (freshness_dist['outdated'] / total_items) * 100
        if outdated_pct > 25:
            recommendations.append("📅 Mais de 25% das informações estão desatualizadas - buscar dados mais recentes")
        
        unknown_freshness_pct = (freshness_dist['unknown'] / total_items) * 100
        if unknown_freshness_pct > 20:
            recommendations.append("❓ Mais de 20% das informações não têm data conhecida - verificar atualidade")
        
        # Recomendações gerais
        unverified_count = sum(1 for item in items if item.verification_status == 'unverified')
        if unverified_count > total_items * 0.5:
            recommendations.append("⚠️ Mais de 50% das informações não foram verificadas - implementar processo de validação")
        
        # Recomendações específicas
        requires_validation_count = sum(1 for item in items 
                                      if any(tag.id == 'requires_validation' for tag in item.tags))
        if requires_validation_count > 0:
            recommendations.append(f"🔎 {requires_validation_count} informações requerem validação adicional")
        
        if not recommendations:
            recommendations.append("✅ Qualidade geral das informações está adequada")
        
        return recommendations
    
    def generate_qualification_html(self, qualified_items: List[QualifiedInformation], 
                                  summary: QualificationSummary = None) -> str:
        """Gera HTML da qualificação de informações"""
        if not summary:
            summary = self.generate_qualification_summary(qualified_items)
        
        html = ['<div class="information-qualification">']
        html.append('<h3>🏷️ Qualificação de Informações</h3>')
        
        # Resumo geral
        html.append('<div class="qualification-summary">')
        html.append(f'<h4>📊 Resumo da Qualidade</h4>')
        html.append(f'<p><strong>Total de Informações:</strong> {summary.total_items}</p>')
        html.append(f'<p><strong>Score Geral de Qualidade:</strong> {summary.overall_quality_score:.2f}</p>')
        
        # Distribuição de confiança
        html.append('<div class="confidence-distribution">')
        html.append('<h5>Distribuição de Confiança:</h5>')
        for level, count in summary.confidence_distribution.items():
            percentage = (count / summary.total_items) * 100 if summary.total_items > 0 else 0
            level_class = f"confidence-{level}"
            html.append(f'<div class="confidence-bar {level_class}">')
            html.append(f'<span class="confidence-label">{level.upper()}: {count} ({percentage:.1f}%)</span>')
            html.append(f'<div class="confidence-fill" style="width: {percentage}%"></div>')
            html.append('</div>')
        html.append('</div>')
        
        html.append('</div>')
        
        # Tags mais frequentes
        if summary.tag_distribution:
            html.append('<div class="tag-distribution">')
            html.append('<h4>🏷️ Tags Mais Frequentes</h4>')
            html.append('<div class="tags-cloud">')
            
            # Ordena tags por frequência
            sorted_tags = sorted(summary.tag_distribution.items(), key=lambda x: x[1], reverse=True)
            
            for tag_label, count in sorted_tags[:10]:  # Top 10 tags
                # Encontra definição da tag
                tag_def = None
                for tag in self.tag_definitions.values():
                    if tag.label == tag_label:
                        tag_def = tag
                        break
                
                if tag_def:
                    html.append(f'<span class="info-tag" style="background-color: {tag_def.color}; color: white;">')
                    html.append(f'{tag_def.icon} {tag_label} ({count})')
                    html.append('</span>')
            
            html.append('</div>')
            html.append('</div>')
        
        # Exemplos de informações qualificadas
        if qualified_items:
            html.append('<div class="qualification-examples">')
            html.append('<h4>📋 Exemplos de Qualificação</h4>')
            
            # Mostra até 3 exemplos
            for i, item in enumerate(qualified_items[:3]):
                html.append(f'<div class="qualification-example">')
                html.append(f'<h5>Exemplo {i+1}</h5>')
                html.append(f'<p class="example-content">"{item.content[:100]}..."</p>')
                
                # Tags do item
                html.append('<div class="example-tags">')
                for tag in item.tags[:4]:  # Máximo 4 tags por exemplo
                    html.append(f'<span class="info-tag-small" style="background-color: {tag.color}; color: white;">')
                    html.append(f'{tag.icon} {tag.label}')
                    html.append('</span>')
                html.append('</div>')
                
                # Métricas do item
                html.append('<div class="example-metrics">')
                html.append(f'<span class="metric">Confiança: {item.confidence_score:.2f}</span>')
                html.append(f'<span class="metric">Atualidade: {item.data_freshness.upper()}</span>')
                html.append(f'<span class="metric">Status: {item.verification_status.upper()}</span>')
                html.append('</div>')
                
                html.append('</div>')
            
            html.append('</div>')
        
        # Recomendações
        if summary.recommendations:
            html.append('<div class="quality-recommendations">')
            html.append('<h4>💡 Recomendações de Qualidade</h4>')
            html.append('<ul class="recommendations-list">')
            
            for recommendation in summary.recommendations:
                html.append(f'<li>{recommendation}</li>')
            
            html.append('</ul>')
            html.append('</div>')
        
        html.append('</div>')
        
        return '\n'.join(html)
    
    def generate_inline_tags_html(self, qualified_info: QualifiedInformation) -> str:
        """Gera HTML das tags inline para uma informação"""
        if not qualified_info.tags:
            return ''
        
        html = ['<span class="inline-tags">']
        
        for tag in qualified_info.tags[:3]:  # Máximo 3 tags inline
            html.append(f'<span class="info-tag-inline" style="background-color: {tag.color}; color: white;" title="{tag.description}">')
            html.append(f'{tag.icon} {tag.label}')
            html.append('</span>')
        
        if len(qualified_info.tags) > 3:
            html.append(f'<span class="more-tags">+{len(qualified_info.tags) - 3}</span>')
        
        html.append('</span>')
        
        return ''.join(html)
    
    def generate_qualification_css(self) -> str:
        """Gera CSS para visualização da qualificação"""
        return """
        <style>
        .information-qualification {
            margin: 30px 0;
            padding: 25px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px;
            border-left: 5px solid #6c757d;
        }
        
        .qualification-summary {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .confidence-distribution {
            margin-top: 15px;
        }
        
        .confidence-bar {
            position: relative;
            margin: 8px 0;
            height: 30px;
            background-color: #e9ecef;
            border-radius: 15px;
            overflow: hidden;
        }
        
        .confidence-label {
            position: absolute;
            left: 10px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.9em;
            font-weight: 500;
            z-index: 2;
        }
        
        .confidence-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .confidence-high .confidence-fill {
            background: linear-gradient(90deg, #28a745, #20c997);
        }
        
        .confidence-medium .confidence-fill {
            background: linear-gradient(90deg, #ffc107, #fd7e14);
        }
        
        .confidence-low .confidence-fill {
            background: linear-gradient(90deg, #dc3545, #e83e8c);
        }
        
        .tag-distribution {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .tags-cloud {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
        }
        
        .info-tag {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .info-tag-small {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 500;
            margin: 2px;
        }
        
        .info-tag-inline {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 0.7em;
            font-weight: 500;
            margin: 0 2px;
        }
        
        .inline-tags {
            margin-left: 8px;
        }
        
        .more-tags {
            font-size: 0.7em;
            color: #6c757d;
            font-style: italic;
        }
        
        .qualification-examples {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .qualification-example {
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            background-color: #f8f9fa;
        }
        
        .example-content {
            font-style: italic;
            color: #495057;
            margin: 10px 0;
        }
        
        .example-tags {
            margin: 10px 0;
        }
        
        .example-metrics {
            display: flex;
            gap: 15px;
            margin-top: 10px;
        }
        
        .metric {
            font-size: 0.8em;
            padding: 3px 8px;
            background-color: #e9ecef;
            border-radius: 12px;
            color: #495057;
        }
        
        .quality-recommendations {
            background-color: #e7f3ff;
            padding: 20px;
            border-left: 4px solid #007bff;
            border-radius: 8px;
        }
        
        .recommendations-list {
            margin: 15px 0;
            padding-left: 20px;
        }
        
        .recommendations-list li {
            margin-bottom: 8px;
            line-height: 1.5;
        }
        
        .qualification-example h5 {
            color: #495057;
            margin-bottom: 10px;
        }
        </style>
        """
    
    def export_qualification_json(self, qualified_items: List[QualifiedInformation], 
                                summary: QualificationSummary = None) -> str:
        """Exporta qualificação em JSON"""
        if not summary:
            summary = self.generate_qualification_summary(qualified_items)
        
        data = {
            'qualified_items': [asdict(item) for item in qualified_items],
            'summary': asdict(summary),
            'tag_definitions': {tag_id: asdict(tag) for tag_id, tag in self.tag_definitions.items()},
            'export_date': datetime.now().isoformat()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

# Instância global do qualificador
information_qualifier = InformationQualifier()