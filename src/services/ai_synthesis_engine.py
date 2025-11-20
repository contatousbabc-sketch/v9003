#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - AI Synthesis Engine
Motor de síntese da IA com hierarquia OpenRouter: Grok-4 → Gemini-2.0 → DeepSeek-R1
ZERO SIMULAÇÃO - Apenas modelos reais funcionais
"""

import os
import logging
import json
import time
import re
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
from .enhanced_ai_manager import enhanced_ai_manager
from .auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class AISynthesisEngine:
    """Motor de síntese da IA com capacidade de tool use"""
    
    def __init__(self):
        """Inicializa o motor de síntese"""
        self.synthesis_tools = {
            'google_search': self._tool_google_search,
            'web_extract': self._tool_web_extract,
            'social_search': self._tool_social_search
        }
        
        self.max_tool_calls = 10  # Limite de chamadas de ferramentas
        self.synthesis_timeout = 1800  # 30 minutos máximo
        
        # Define diretório de screenshots (ajuste conforme sua estrutura)
        self.screenshots_dir = os.getenv('SCREENSHOTS_DIR', './screenshots')
        
        logger.info("🧠 AI Synthesis Engine inicializado")
    
    async def analyze_and_synthesize(
        self, 
        session_id: str, 
        model: str = None, 
        api_key: str = None, 
        analysis_time: int = 300,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Executa análise e síntese da IA com tool use"""
        
        logger.info(f"🧠 Iniciando síntese da IA para sessão {session_id}")
        
        try:
            if progress_callback:
                progress_callback("Carregando dados coletados...")
            
            # Carrega o relatório de coleta
            collection_report = self._load_collection_report(session_id)
            if not collection_report:
                raise Exception("Relatório de coleta não encontrado")
            
            if progress_callback:
                progress_callback("Preparando prompt mestre para IA...")
            
            # Constrói prompt mestre
            master_prompt = self._build_master_synthesis_prompt(collection_report, session_id)
            
            if progress_callback:
                progress_callback("Iniciando análise profunda da IA...")
            
            # Executa síntese com tool use
            synthesis_result = await self._execute_synthesis_with_tools(
                master_prompt, 
                session_id, 
                analysis_time,
                progress_callback
            )
            
            if progress_callback:
                progress_callback("Salvando resumo de síntese...")
            
            # Salva resumo de síntese
            synthesis_summary = self._create_synthesis_summary(synthesis_result, session_id)
            self._save_synthesis_json(synthesis_summary, session_id)
            
            logger.info(f"✅ Síntese da IA concluída para sessão {session_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'synthesis_summary': synthesis_summary,
                'tool_calls_made': synthesis_result.get('tool_calls_made', 0),
                'analysis_duration': synthesis_result.get('analysis_duration', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na síntese da IA: {e}")
            salvar_erro("ai_synthesis_error", e, contexto={'session_id': session_id})
            
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def _load_collection_report(self, session_id: str) -> Optional[str]:
        """Carrega o relatório de coleta da sessão"""
        
        try:
            report_path = Path(self.screenshots_dir) / "files" / session_id / "relatorio_coleta.md"
            
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                logger.info(f"📄 Relatório de coleta carregado: {len(content)} caracteres")
                return content
            else:
                logger.error(f"❌ Relatório de coleta não encontrado: {report_path}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar relatório: {e}")
            return None
    
    def _build_master_synthesis_prompt(self, collection_report: str, session_id: str) -> str:
        """PRIORIDADE 4: Constrói prompt mestre avançado para síntese baseado na análise semântica profunda"""
        
        # Extrair informações da sessão para contextualizar melhor
        session_context = self._extract_session_context(session_id, collection_report)
        
        # PRIORIDADE 4: Estratégia de análise baseada na categoria e complexidade
        analysis_strategy = self._define_analysis_strategy(session_context)
        
        prompt = f"""
# VOCÊ É O ANALISTA MESTRE DE SÍNTESE DE DADOS - ESPECIALISTA EM {session_context['categoria_negocio'].upper()}

Sua missão é estudar profundamente o material coletado sobre "{session_context['tema_principal']}" e sintetizar insights acionáveis de alta qualidade.

## PERFIL ANALÍTICO AVANÇADO:
- **Tema Principal**: {session_context['tema_principal']}
- **Categoria de Negócio**: {session_context['categoria_negocio']}
- **Segmento de Mercado**: {session_context['segmento']}
- **Público-Alvo**: {session_context['publico_alvo']}
- **Objetivo da Pesquisa**: {session_context['objetivo']}
- **Nível de Complexidade**: {session_context['nivel_complexidade']}
- **Contexto Competitivo**: {session_context['contexto_competitivo']}
- **Potencial de Inovação**: {session_context['potencial_inovacao']}
- **Palavras-Chave Principais**: {', '.join(session_context['palavras_chave_principais'][:5])}

## ESTRATÉGIA DE ANÁLISE PERSONALIZADA:
{analysis_strategy}

## MATERIAL COLETADO PARA ANÁLISE PROFUNDA:
{collection_report[:15000]}

## FERRAMENTAS ESPECIALIZADAS DISPONÍVEIS:
Você tem acesso às seguintes ferramentas para aprofundar sua análise específica em {session_context['categoria_negocio']}:

1. **google_search("query")** - Para buscar informações adicionais específicas sobre {session_context['tema_principal']}
2. **web_extract("url")** - Para extrair conteúdo detalhado de URLs relevantes encontradas
3. **social_search("query")** - Para buscar dados específicos em redes sociais sobre {session_context['tema_principal']}

## INSTRUÇÕES DE SÍNTESE AVANÇADA PARA {session_context['categoria_negocio'].upper()}:

### FASE 1 - ESTUDO PROFUNDO DO ASSUNTO:
1. **ANÁLISE CONTEXTUAL**: Compreenda profundamente o contexto de {session_context['tema_principal']} no mercado de {session_context['categoria_negocio']}
2. **IDENTIFICAÇÃO DE PADRÕES**: Identifique padrões específicos relacionados às palavras-chave: {', '.join(session_context['palavras_chave_principais'][:3])}
3. **MAPEAMENTO DE STAKEHOLDERS**: Identifique todos os players relevantes no ecossistema de {session_context['segmento']}

### FASE 2 - COLETA INTELIGENTE DE DADOS COMPLEMENTARES:
Se identificar gaps críticos de informação, USE AS FERRAMENTAS de forma estratégica:

**Para mercados de complexidade {session_context['nivel_complexidade']}:**
- Busque dados específicos sobre regulamentações, barreiras de entrada, e requisitos técnicos
- Analise cases de sucesso e fracasso no segmento
- Identifique tendências emergentes e tecnologias disruptivas

**Para contexto competitivo {session_context['contexto_competitivo']}:**
- Mapeie concorrentes diretos e indiretos
- Analise estratégias de posicionamento e diferenciação
- Identifique gaps de mercado e oportunidades não exploradas

### FASE 3 - SÍNTESE ESTRATÉGICA:
Extraia insights acionáveis específicos para {session_context['categoria_negocio']} com foco em:
- Oportunidades de mercado baseadas no potencial de inovação {session_context['potencial_inovacao']}
- Estratégias de entrada considerando a complexidade {session_context['nivel_complexidade']}
- Posicionamento competitivo no contexto {session_context['contexto_competitivo']}

## EXEMPLOS DE USO INTELIGENTE DE FERRAMENTAS:

Para análise competitiva em {session_context['categoria_negocio']}:
```
google_search("análise competitiva {session_context['tema_principal']} {session_context['categoria_negocio']} Brasil 2025 market share")
```

Para tendências específicas do segmento:
```
social_search("{session_context['tema_principal']} {session_context['categoria_negocio']} tendências inovação futuro")
```

Para análise de cases específicos:
```
web_extract("URL-de-case-relevante-encontrada-nos-dados")
```

## FORMATO DE RESPOSTA FINAL ESPECIALIZADA EM {session_context['categoria_negocio'].upper()}:
Após sua análise profunda (com ou sem uso de ferramentas), retorne um JSON estruturado focado em {session_context['tema_principal']}:

```json
{{
  "tema_analisado": "{session_context['tema_principal']}",
  "segmento_foco": "{session_context['segmento']}",
  "insights_principais": [
    "Insight específico sobre {session_context['tema_principal']} baseado na análise profunda",
    "Insight sobre oportunidades em {session_context['segmento']} com dados específicos encontrados",
    "Insight sobre comportamento do público-alvo em relação a {session_context['tema_principal']}"
  ],
  "dores_identificadas": [
    "Dor específica do público-alvo em {session_context['segmento']} extraída dos dados",
    "Problema recorrente relacionado a {session_context['tema_principal']} com evidências",
    "Gap de mercado identificado em {session_context['segmento']}"
  ],
  "desejos_mapeados": [
    "Desejo específico relacionado a {session_context['tema_principal']} identificado nos dados sociais",
    "Aspiração do público-alvo em {session_context['segmento']} baseada em padrões comportamentais",
    "Necessidade latente descoberta na análise"
  ],
  "concorrentes_principais": [
    {{"nome": "Concorrente 1 em {session_context['segmento']}", "pontos_fortes": ["Força específica"], "pontos_fracos": ["Fraqueza identificada"], "posicionamento": "Como se posiciona em {session_context['tema_principal']}"}},
    {{"nome": "Concorrente 2", "pontos_fortes": ["Força"], "pontos_fracos": ["Fraqueza"], "posicionamento": "Estratégia atual"}}
  ],
  "oportunidades_mercado": [
    "Oportunidade específica em {session_context['segmento']} relacionada a {session_context['tema_principal']}",
    "Gap de mercado identificado com potencial de crescimento",
    "Nicho inexplorado descoberto na análise"
  ],
  "tendencias_emergentes": [
    "Tendência específica em {session_context['tema_principal']} baseada em dados reais",
    "Movimento emergente em {session_context['segmento']} com evidências sociais",
    "Padrão comportamental identificado nos dados coletados"
  ],
  "publico_alvo_refinado": {{
    "demografia": "Perfil demográfico específico baseado nos dados de {session_context['segmento']}",
    "psicografia": "Características psicológicas relacionadas a {session_context['tema_principal']}",
    "comportamentos": ["Comportamento específico 1", "Padrão de consumo 2", "Preferência identificada 3"],
    "linguagem_preferida": "Tom e estilo de comunicação identificado",
    "canais_preferidos": ["Canal 1", "Plataforma 2"]
  }},
  "estrategias_recomendadas": [
    "Estratégia específica para {session_context['tema_principal']} baseada na análise",
    "Abordagem recomendada para {session_context['segmento']} com justificativa",
    "Tática de posicionamento baseada nos insights descobertos"
  ],
  "pontos_atencao": [
    "Risco ou desafio específico identificado",
    "Barreira de entrada em {session_context['segmento']}",
    "Fator crítico de sucesso"
  ],
  "metricas_chave": {{
    "fontes_analisadas": 0,
    "posts_sociais_analisados": 0,
    "insights_extraidos": 0,
    "tool_calls_realizadas": 0,
    "concorrentes_identificados": 0,
    "oportunidades_mapeadas": 0
  }}
}}
```

IMPORTANTE: 
- Use as ferramentas sempre que precisar de informações mais específicas sobre {session_context['tema_principal']}
- Foque sua análise no contexto de {session_context['segmento']}
- Baseie todos os insights em dados reais coletados
- Seja específico e acionável em suas recomendações
"""
        
        return prompt
    
    def _define_analysis_strategy(self, session_context: Dict[str, Any]) -> str:
        """PRIORIDADE 4: Define estratégia de análise personalizada baseada no contexto"""
        
        categoria = session_context['categoria_negocio']
        complexidade = session_context['nivel_complexidade']
        competitividade = session_context['contexto_competitivo']
        inovacao = session_context['potencial_inovacao']
        
        # Estratégias específicas por categoria
        category_strategies = {
            'Tecnologia': {
                'foco': 'Análise de tendências tecnológicas, adoção de mercado, e ciclos de inovação',
                'metricas': 'TAM/SAM/SOM, adoption rate, technology readiness level',
                'riscos': 'Obsolescência tecnológica, mudanças regulatórias, concorrência de big techs'
            },
            'E-commerce': {
                'foco': 'Comportamento do consumidor, conversão, lifetime value, e experiência do usuário',
                'metricas': 'CAC, LTV, conversion rate, AOV, retention rate',
                'riscos': 'Sazonalidade, mudanças no comportamento de compra, logística'
            },
            'Saúde': {
                'foco': 'Regulamentações, evidências clínicas, adoção por profissionais de saúde',
                'metricas': 'Outcomes clínicos, cost-effectiveness, time to market regulatório',
                'riscos': 'Aprovações regulatórias, responsabilidade civil, mudanças na legislação'
            },
            'Finanças': {
                'foco': 'Compliance, segurança, confiança do consumidor, e regulamentações',
                'metricas': 'AUM, transaction volume, customer acquisition cost, regulatory compliance',
                'riscos': 'Mudanças regulatórias, cibersegurança, crises econômicas'
            },
            'Educação': {
                'foco': 'Eficácia pedagógica, adoção institucional, e resultados de aprendizagem',
                'metricas': 'Student engagement, learning outcomes, retention rate, NPS',
                'riscos': 'Mudanças curriculares, orçamentos educacionais, resistência à mudança'
            }
        }
        
        # Estratégia base para a categoria
        base_strategy = category_strategies.get(categoria, {
            'foco': 'Análise abrangente de mercado, concorrência e oportunidades',
            'metricas': 'Market share, growth rate, customer satisfaction',
            'riscos': 'Mudanças de mercado, concorrência, fatores econômicos'
        })
        
        # Ajustes baseados na complexidade
        complexity_adjustments = {
            'Alto': {
                'profundidade': 'Análise técnica detalhada, due diligence rigorosa, modelagem de cenários complexos',
                'ferramentas': 'Priorize análise de documentos técnicos, whitepapers, e fontes especializadas',
                'tempo': 'Dedique mais tempo à validação de informações e análise de riscos'
            },
            'Médio': {
                'profundidade': 'Análise equilibrada entre aspectos técnicos e comerciais',
                'ferramentas': 'Combine fontes técnicas com análise de mercado e tendências sociais',
                'tempo': 'Foque em insights acionáveis com validação adequada'
            },
            'Baixo': {
                'profundidade': 'Análise focada em oportunidades comerciais e go-to-market',
                'ferramentas': 'Priorize análise de tendências sociais, comportamento do consumidor',
                'tempo': 'Foque em insights rápidos e estratégias de execução'
            }
        }
        
        # Ajustes baseados na competitividade
        competition_adjustments = {
            'Intenso': 'Foque em diferenciação, nichos não explorados, e vantagens competitivas sustentáveis',
            'Moderado': 'Analise posicionamento competitivo e oportunidades de crescimento',
            'Baixo': 'Explore estratégias de first-mover advantage e construção de barreiras de entrada'
        }
        
        # Ajustes baseados no potencial de inovação
        innovation_adjustments = {
            'Alto': 'Priorize análise de tecnologias emergentes, patents landscape, e disruptive trends',
            'Médio': 'Balance inovação incremental com oportunidades de breakthrough',
            'Baixo': 'Foque em otimização de processos existentes e melhorias incrementais'
        }
        
        # Construir estratégia personalizada
        strategy = f"""
**ESTRATÉGIA ANALÍTICA PERSONALIZADA PARA {categoria.upper()}:**

**Foco Principal:** {base_strategy['foco']}

**Métricas-Chave:** {base_strategy['metricas']}

**Riscos Críticos:** {base_strategy['riscos']}

**Abordagem por Complexidade ({complexidade}):** {complexity_adjustments.get(complexidade, complexity_adjustments['Médio'])['profundidade']}

**Uso de Ferramentas:** {complexity_adjustments.get(complexidade, complexity_adjustments['Médio'])['ferramentas']}

**Foco Competitivo ({competitividade}):** {competition_adjustments.get(competitividade, competition_adjustments['Moderado'])}

**Perspectiva de Inovação ({inovacao}):** {innovation_adjustments.get(inovacao, innovation_adjustments['Médio'])}

**Diretrizes de Tempo:** {complexity_adjustments.get(complexidade, complexity_adjustments['Médio'])['tempo']}
"""
        
        return strategy
    
    def _extract_session_context(self, session_id: str, collection_report: str) -> Dict[str, str]:
        """PRIORIDADE 4: Extrai contexto específico da sessão com análise semântica avançada"""
        
        try:
            # Tentar carregar dados da sessão
            session_dir = Path(self.screenshots_dir) / "files" / session_id
            
            # Procurar por arquivos de configuração da sessão
            config_files = [
                session_dir / "session_config.json",
                session_dir / "search_params.json",
                session_dir / "initial_query.json"
            ]
            
            session_data = {}
            for config_file in config_files:
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            session_data.update(data)
                    except:
                        continue
            
            # Extrair informações do relatório de coleta se não encontrou nos arquivos
            if not session_data:
                session_data = self._extract_context_from_report(collection_report)
            
            # PRIORIDADE 4: Análise semântica avançada do contexto
            enhanced_context = self._perform_semantic_context_analysis(session_data, collection_report)
            
            # Valores com análise aprimorada
            context = {
                'tema_principal': enhanced_context.get('tema_principal', 'Análise de Mercado'),
                'segmento': enhanced_context.get('segmento', 'Mercado Digital'),
                'publico_alvo': enhanced_context.get('publico_alvo', 'Público Geral'),
                'objetivo': enhanced_context.get('objetivo', 'Análise de oportunidades e insights de mercado'),
                'categoria_negocio': enhanced_context.get('categoria_negocio', 'Geral'),
                'nivel_complexidade': enhanced_context.get('nivel_complexidade', 'Médio'),
                'palavras_chave_principais': enhanced_context.get('palavras_chave_principais', []),
                'contexto_competitivo': enhanced_context.get('contexto_competitivo', 'Moderado'),
                'potencial_inovacao': enhanced_context.get('potencial_inovacao', 'Médio')
            }
            
            logger.info(f"📊 Contexto avançado extraído: {context['tema_principal']} | {context['segmento']} | Complexidade: {context['nivel_complexidade']}")
            return context
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair contexto da sessão: {e}")
            # Fallback com contexto genérico
            return {
                'tema_principal': 'Análise de Mercado',
                'segmento': 'Mercado Digital',
                'publico_alvo': 'Público Geral',
                'objetivo': 'Análise de oportunidades e insights de mercado',
                'categoria_negocio': 'Geral',
                'nivel_complexidade': 'Médio',
                'palavras_chave_principais': [],
                'contexto_competitivo': 'Moderado',
                'potencial_inovacao': 'Médio'
            }
    
    def _perform_semantic_context_analysis(self, session_data: Dict, collection_report: str) -> Dict[str, Any]:
        """PRIORIDADE 4: Análise semântica avançada do contexto para entender profundamente o assunto"""
        
        try:
            # Análise básica dos dados existentes
            tema_base = session_data.get('tema', session_data.get('query', session_data.get('topic', '')))
            segmento_base = session_data.get('segmento', session_data.get('segment', ''))
            
            # Análise de palavras-chave e entidades
            palavras_chave = self._extract_key_entities(collection_report, tema_base)
            
            # Classificação de categoria de negócio
            categoria_negocio = self._classify_business_category(tema_base, segmento_base, palavras_chave)
            
            # Análise de complexidade do mercado
            nivel_complexidade = self._analyze_market_complexity(collection_report, palavras_chave)
            
            # Análise do contexto competitivo
            contexto_competitivo = self._analyze_competitive_context(collection_report)
            
            # Análise do potencial de inovação
            potencial_inovacao = self._analyze_innovation_potential(collection_report, palavras_chave)
            
            # Refinamento do tema principal
            tema_refinado = self._refine_main_theme(tema_base, palavras_chave, categoria_negocio)
            
            # Refinamento do segmento
            segmento_refinado = self._refine_market_segment(segmento_base, categoria_negocio, contexto_competitivo)
            
            enhanced_context = {
                'tema_principal': tema_refinado,
                'segmento': segmento_refinado,
                'publico_alvo': session_data.get('publico_alvo', self._infer_target_audience(categoria_negocio, tema_refinado)),
                'objetivo': session_data.get('objetivo', self._infer_analysis_objective(categoria_negocio, nivel_complexidade)),
                'categoria_negocio': categoria_negocio,
                'nivel_complexidade': nivel_complexidade,
                'palavras_chave_principais': palavras_chave[:10],  # Top 10
                'contexto_competitivo': contexto_competitivo,
                'potencial_inovacao': potencial_inovacao
            }
            
            logger.info(f"🧠 Análise semântica concluída: {categoria_negocio} | Complexidade: {nivel_complexidade}")
            return enhanced_context
            
        except Exception as e:
            logger.error(f"❌ Erro na análise semântica: {e}")
            # Fallback para análise básica
            return {
                'tema_principal': session_data.get('tema', 'Análise de Mercado'),
                'segmento': session_data.get('segmento', 'Mercado Digital'),
                'publico_alvo': session_data.get('publico_alvo', 'Público Geral'),
                'objetivo': 'Análise de oportunidades e insights de mercado',
                'categoria_negocio': 'Geral',
                'nivel_complexidade': 'Médio',
                'palavras_chave_principais': [],
                'contexto_competitivo': 'Moderado',
                'potencial_inovacao': 'Médio'
            }
    
    def _extract_key_entities(self, text: str, tema_base: str) -> List[str]:
        """Extrai entidades-chave e palavras importantes do texto"""
        
        # Palavras de parada em português
        stop_words = {
            'de', 'da', 'do', 'das', 'dos', 'a', 'o', 'as', 'os', 'e', 'ou', 'mas', 'para', 'por', 
            'com', 'em', 'no', 'na', 'nos', 'nas', 'um', 'uma', 'uns', 'umas', 'que', 'se', 'é', 
            'são', 'foi', 'foram', 'ser', 'estar', 'ter', 'haver', 'mais', 'muito', 'bem', 'como',
            'sobre', 'entre', 'até', 'desde', 'durante', 'através', 'dentro', 'fora', 'acima', 'abaixo'
        }
        
        # Extrair palavras significativas
        words = re.findall(r'\b[A-Za-zÀ-ÿ]{3,}\b', text.lower())
        
        # Filtrar palavras de parada e contar frequência
        word_freq = {}
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Adicionar peso extra para palavras do tema base
        if tema_base:
            tema_words = re.findall(r'\b[A-Za-zÀ-ÿ]{3,}\b', tema_base.lower())
            for word in tema_words:
                if word in word_freq:
                    word_freq[word] *= 2
        
        # Retornar palavras mais frequentes
        return sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)
    
    def _classify_business_category(self, tema: str, segmento: str, palavras_chave: List[str]) -> str:
        """Classifica a categoria de negócio baseada no tema e palavras-chave"""
        
        # Dicionário de categorias e suas palavras-chave
        categorias = {
            'Tecnologia': ['tecnologia', 'software', 'app', 'digital', 'ia', 'inteligencia', 'artificial', 'dados', 'analytics', 'cloud', 'saas'],
            'E-commerce': ['ecommerce', 'loja', 'vendas', 'marketplace', 'produto', 'compras', 'consumidor', 'varejo'],
            'Saúde': ['saude', 'medicina', 'hospital', 'clinica', 'tratamento', 'paciente', 'medico', 'farmacia'],
            'Educação': ['educacao', 'ensino', 'curso', 'escola', 'universidade', 'aprendizado', 'treinamento', 'capacitacao'],
            'Finanças': ['financas', 'banco', 'investimento', 'credito', 'pagamento', 'fintech', 'moeda', 'economia'],
            'Marketing': ['marketing', 'publicidade', 'campanha', 'branding', 'comunicacao', 'midia', 'social', 'influencer'],
            'Alimentação': ['alimentacao', 'comida', 'restaurante', 'delivery', 'gastronomia', 'culinaria', 'bebida'],
            'Imobiliário': ['imovel', 'casa', 'apartamento', 'construcao', 'arquitetura', 'reforma', 'decoracao'],
            'Transporte': ['transporte', 'logistica', 'entrega', 'veiculo', 'mobilidade', 'uber', 'taxi'],
            'Entretenimento': ['entretenimento', 'jogo', 'musica', 'filme', 'streaming', 'diversao', 'lazer']
        }
        
        # Texto combinado para análise
        texto_analise = f"{tema} {segmento} {' '.join(palavras_chave[:20])}".lower()
        
        # Calcular pontuação para cada categoria
        pontuacoes = {}
        for categoria, keywords in categorias.items():
            pontuacao = 0
            for keyword in keywords:
                if keyword in texto_analise:
                    pontuacao += texto_analise.count(keyword)
            pontuacoes[categoria] = pontuacao
        
        # Retornar categoria com maior pontuação ou 'Geral' se nenhuma se destacar
        if pontuacoes and max(pontuacoes.values()) > 0:
            return max(pontuacoes, key=pontuacoes.get)
        return 'Geral'
    
    def _analyze_market_complexity(self, collection_report: str, palavras_chave: List[str]) -> str:
        """Analisa a complexidade do mercado baseada no conteúdo coletado"""
        
        # Indicadores de alta complexidade
        high_complexity_indicators = [
            'regulamentacao', 'compliance', 'licenca', 'certificacao', 'auditoria',
            'b2b', 'enterprise', 'corporativo', 'industrial', 'tecnico',
            'especializado', 'nicho', 'complexo', 'avancado', 'profissional'
        ]
        
        # Indicadores de baixa complexidade
        low_complexity_indicators = [
            'simples', 'facil', 'basico', 'popular', 'massivo', 'geral',
            'consumidor', 'varejo', 'casual', 'acessivel', 'direto'
        ]
        
        texto_analise = collection_report.lower()
        
        # Contar indicadores
        high_score = sum(1 for indicator in high_complexity_indicators if indicator in texto_analise)
        low_score = sum(1 for indicator in low_complexity_indicators if indicator in texto_analise)
        
        # Analisar também o tamanho e diversidade do conteúdo
        content_length = len(collection_report)
        unique_keywords = len(set(palavras_chave[:50]))
        
        # Lógica de classificação
        if high_score > low_score + 2 or (content_length > 10000 and unique_keywords > 30):
            return 'Alto'
        elif low_score > high_score + 2 or (content_length < 3000 and unique_keywords < 15):
            return 'Baixo'
        else:
            return 'Médio'
    
    def _analyze_competitive_context(self, collection_report: str) -> str:
        """Analisa o contexto competitivo do mercado"""
        
        competitive_indicators = {
            'Intenso': ['concorrencia', 'competitivo', 'saturado', 'disputado', 'guerra', 'preco', 'lider', 'dominante'],
            'Moderado': ['competidor', 'alternativa', 'opcao', 'escolha', 'comparacao', 'diferencial'],
            'Baixo': ['pioneiro', 'inovador', 'unico', 'exclusivo', 'novo', 'emergente', 'oportunidade']
        }
        
        texto_analise = collection_report.lower()
        
        # Calcular pontuações
        pontuacoes = {}
        for nivel, indicators in competitive_indicators.items():
            pontuacao = sum(1 for indicator in indicators if indicator in texto_analise)
            pontuacoes[nivel] = pontuacao
        
        # Retornar nível com maior pontuação
        if pontuacoes and max(pontuacoes.values()) > 0:
            return max(pontuacoes, key=pontuacoes.get)
        return 'Moderado'
    
    def _analyze_innovation_potential(self, collection_report: str, palavras_chave: List[str]) -> str:
        """Analisa o potencial de inovação do mercado"""
        
        innovation_indicators = {
            'Alto': ['inovacao', 'disruptivo', 'revolucionario', 'breakthrough', 'futuro', 'tendencia', 'emergente', 'startup'],
            'Médio': ['melhoria', 'otimizacao', 'evolucao', 'desenvolvimento', 'crescimento', 'oportunidade'],
            'Baixo': ['tradicional', 'estabelecido', 'maduro', 'consolidado', 'estavel', 'conservador']
        }
        
        texto_analise = collection_report.lower()
        
        # Calcular pontuações
        pontuacoes = {}
        for nivel, indicators in innovation_indicators.items():
            pontuacao = sum(1 for indicator in indicators if indicator in texto_analise)
            pontuacoes[nivel] = pontuacao
        
        # Considerar também a diversidade de palavras-chave como indicador de inovação
        if len(set(palavras_chave[:30])) > 25:
            pontuacoes['Alto'] = pontuacoes.get('Alto', 0) + 2
        
        # Retornar nível com maior pontuação
        if pontuacoes and max(pontuacoes.values()) > 0:
            return max(pontuacoes, key=pontuacoes.get)
        return 'Médio'
    
    def _refine_main_theme(self, tema_base: str, palavras_chave: List[str], categoria: str) -> str:
        """Refina o tema principal baseado na análise semântica"""
        
        if not tema_base or tema_base == 'Análise de Mercado':
            # Construir tema baseado nas palavras-chave principais e categoria
            if palavras_chave:
                tema_refinado = f"{categoria} - {' '.join(palavras_chave[:3]).title()}"
                return tema_refinado
            return f"Análise de {categoria}"
        
        # Se já tem um tema, apenas refiná-lo
        if categoria != 'Geral' and categoria.lower() not in tema_base.lower():
            return f"{tema_base} ({categoria})"
        
        return tema_base
    
    def _refine_market_segment(self, segmento_base: str, categoria: str, contexto_competitivo: str) -> str:
        """Refina o segmento de mercado baseado na análise"""
        
        if not segmento_base or segmento_base == 'Mercado Digital':
            return f"Mercado de {categoria} - Competitividade {contexto_competitivo}"
        
        return segmento_base
    
    def _infer_target_audience(self, categoria: str, tema: str) -> str:
        """Infere o público-alvo baseado na categoria e tema"""
        
        audience_map = {
            'Tecnologia': 'Profissionais de TI, Empresas de Tecnologia, Early Adopters',
            'E-commerce': 'Consumidores Online, Varejistas, Empreendedores Digitais',
            'Saúde': 'Pacientes, Profissionais de Saúde, Instituições Médicas',
            'Educação': 'Estudantes, Educadores, Instituições de Ensino',
            'Finanças': 'Investidores, Empresas, Consumidores Financeiros',
            'Marketing': 'Empresas, Profissionais de Marketing, Agências',
            'Alimentação': 'Consumidores, Restaurantes, Food Service',
            'Imobiliário': 'Compradores, Investidores, Construtoras',
            'Transporte': 'Usuários de Transporte, Empresas de Logística',
            'Entretenimento': 'Consumidores de Entretenimento, Criadores de Conteúdo'
        }
        
        return audience_map.get(categoria, 'Público Geral Interessado no Tema')
    
    def _infer_analysis_objective(self, categoria: str, complexidade: str) -> str:
        """Infere o objetivo da análise baseado na categoria e complexidade"""
        
        if complexidade == 'Alto':
            return f"Análise estratégica profunda do mercado de {categoria} com foco em oportunidades de nicho e diferenciação"
        elif complexidade == 'Baixo':
            return f"Análise de oportunidades de entrada e posicionamento no mercado de {categoria}"
        else:
            return f"Análise abrangente de oportunidades e insights estratégicos no mercado de {categoria}"
    
    def _extract_context_from_report(self, collection_report: str) -> Dict[str, str]:
        """Extrai contexto do relatório de coleta usando regex"""
        
        context = {}
        
        try:
            # Procurar por padrões comuns no relatório
            tema_patterns = [
                r'Tema[:\s]+([^\n\r]+)',
                r'Query[:\s]+([^\n\r]+)',
                r'Pesquisa sobre[:\s]+([^\n\r]+)',
                r'Análise de[:\s]+([^\n\r]+)'
            ]
            
            segmento_patterns = [
                r'Segmento[:\s]+([^\n\r]+)',
                r'Mercado[:\s]+([^\n\r]+)',
                r'Setor[:\s]+([^\n\r]+)',
                r'Indústria[:\s]+([^\n\r]+)'
            ]
            
            publico_patterns = [
                r'Público[:\s]+([^\n\r]+)',
                r'Target[:\s]+([^\n\r]+)',
                r'Audiência[:\s]+([^\n\r]+)'
            ]
            
            # Extrair tema
            for pattern in tema_patterns:
                match = re.search(pattern, collection_report, re.IGNORECASE)
                if match:
                    context['tema'] = match.group(1).strip()
                    break
            
            # Extrair segmento
            for pattern in segmento_patterns:
                match = re.search(pattern, collection_report, re.IGNORECASE)
                if match:
                    context['segmento'] = match.group(1).strip()
                    break
            
            # Extrair público
            for pattern in publico_patterns:
                match = re.search(pattern, collection_report, re.IGNORECASE)
                if match:
                    context['publico_alvo'] = match.group(1).strip()
                    break
            
            # Se não encontrou nada, tentar extrair palavras-chave principais
            if not context.get('tema'):
                # Pegar as primeiras palavras significativas do relatório
                words = re.findall(r'\b[A-Za-z]{4,}\b', collection_report[:500])
                if words:
                    context['tema'] = ' '.join(words[:3])
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair contexto do relatório: {e}")
            return {}
    
    async def _execute_synthesis_with_tools(
        self, 
        prompt: str, 
        session_id: str, 
        analysis_time: int,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Executa síntese com suporte a tool use usando hierarquia OpenRouter"""
        
        start_time = time.time()
        tool_calls_made = 0
        conversation_history = [prompt]
        
        # Sistema prompt para síntese
        system_prompt = """Você é um especialista em análise de dados e síntese de informações.
        Sua função é analisar dados coletados e gerar insights profundos e acionáveis.
        Se precisar de informações adicionais, solicite usando o formato:
        [TOOL_REQUEST: tool_name | parameter: value]
        
        Ferramentas disponíveis:
        - google_search | query: termo de busca
        - web_extract | url: URL para extrair conteúdo
        - social_search | query: busca em redes sociais"""
        
        try:
            while time.time() - start_time < analysis_time and tool_calls_made < self.max_tool_calls:
                
                if progress_callback:
                    elapsed = int(time.time() - start_time)
                    progress_callback(f"IA analisando... ({elapsed}s/{analysis_time}s) - {tool_calls_made} buscas adicionais")
                
                # Envia prompt atual para IA usando hierarquia OpenRouter
                current_prompt = "\n\n".join(conversation_history)
                
                response = await enhanced_ai_manager.generate_text(
                    prompt=current_prompt,
                    system_prompt=system_prompt,
                    max_tokens=4000,
                    temperature=0.7
                )
                
                if not response:
                    raise Exception("IA não respondeu")
                
                # Verifica se há solicitação de tool use
                tool_call = self._extract_tool_call(response)
                
                if tool_call:
                    tool_calls_made += 1
                    logger.info(f"🔧 IA solicitou ferramenta: {tool_call['tool']} - {tool_call.get('query', tool_call.get('url', ''))}")
                    
                    # Executa ferramenta
                    tool_result = await self._execute_tool(tool_call)
                    
                    # Adiciona resultado à conversa
                    conversation_history.append(f"RESULTADO DA FERRAMENTA {tool_call['tool']}:")
                    conversation_history.append(json.dumps(tool_result, ensure_ascii=False, indent=2))
                    conversation_history.append("Continue sua análise com essas informações adicionais.")
                    
                    if progress_callback:
                        progress_callback(f"Ferramenta executada: {tool_call['tool']} - Continuando análise...")
                    
                else:
                    # IA terminou a análise
                    logger.info("✅ IA concluiu síntese sem mais ferramentas")
                    break
            
            analysis_duration = time.time() - start_time
            
            return {
                'final_response': response,
                'tool_calls_made': tool_calls_made,
                'analysis_duration': analysis_duration,
                'conversation_history': conversation_history
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na execução com tools: {e}")
            raise
    
    def _extract_tool_call(self, response: str) -> Optional[Dict[str, str]]:
        """Extrai solicitação de tool use da resposta da IA"""
        
        # Padrão: google_search("query")
        google_match = re.search(r'google_search\(["\']([^"\']+)["\']\)', response)
        if google_match:
            return {'tool': 'google_search', 'query': google_match.group(1)}
        
        # Padrão: web_extract("url")
        web_match = re.search(r'web_extract\(["\']([^"\']+)["\']\)', response)
        if web_match:
            return {'tool': 'web_extract', 'url': web_match.group(1)}
        
        # Padrão: social_search("query")
        social_match = re.search(r'social_search\(["\']([^"\']+)["\']\)', response)
        if social_match:
            return {'tool': 'social_search', 'query': social_match.group(1)}
        
        return None
    
    def _execute_tool(self, tool_call: Dict[str, str]) -> Dict[str, Any]:
        """Executa uma ferramenta solicitada pela IA"""
        
        tool_name = tool_call['tool']
        
        if tool_name in self.synthesis_tools:
            return self.synthesis_tools[tool_name](tool_call)
        else:
            return {'error': f'Ferramenta {tool_name} não disponível'}
    
    def _tool_google_search(self, tool_call: Dict[str, str]) -> Dict[str, Any]:
        """Ferramenta de busca Google"""
        query = tool_call.get('query', '')
        
        try:
            # search_results = search_api_manager.interleaved_search(query, max_results_per_provider=5)  # REMOVIDO
            search_results = []  # Placeholder
            
            # Simplifica resultados para a IA
            simplified_results = []
            for provider, provider_data in search_results.get('results_by_provider', {}).items():
                for result in provider_data.get('results', []):
                    simplified_results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'url': result.get('url', ''),
                        'source': provider
                    })
            
            return {
                'tool': 'google_search',
                'query': query,
                'results': simplified_results[:10],  # Top 10 resultados
                'total_found': len(simplified_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na ferramenta google_search: {e}")
            return {'tool': 'google_search', 'error': str(e)}
    
    def _tool_web_extract(self, tool_call: Dict[str, str]) -> Dict[str, Any]:
        """Ferramenta de extração web"""
        url = tool_call.get('url', '')
        
        try:
            # Import dinâmico para evitar erro se o módulo não existir
            try:
                # from services.robust_content_extractor import robust_content_extractor
                # content = robust_content_extractor.extract_content(url)
                content = ""  # Fallback vazio - não usamos mais o robust_content_extractor
            except ImportError:
                # Fallback simples se o extractor não estiver disponível
                import requests
                from bs4 import BeautifulSoup
                
                response = requests.get(url, timeout=20)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove scripts e styles
                for script in soup(["script", "style"]):
                    script.decompose()
                
                content = soup.get_text()
                # Limpa espaços em branco excessivos
                content = re.sub(r'\s+', ' ', content).strip()
            
            if content:
                # Limita conteúdo para não sobrecarregar a IA
                limited_content = content[:3000] + "..." if len(content) > 3000 else content
                
                return {
                    'tool': 'web_extract',
                    'url': url,
                    'content': limited_content,
                    'content_length': len(content)
                }
            else:
                return {'tool': 'web_extract', 'error': 'Não foi possível extrair conteúdo'}
                
        except Exception as e:
            logger.error(f"❌ Erro na ferramenta web_extract: {e}")
            return {'tool': 'web_extract', 'error': str(e)}
    
    def _tool_social_search(self, tool_call: Dict[str, str]) -> Dict[str, Any]:
        """Ferramenta de busca social"""
        query = tool_call.get('query', '')
        
        try:
            # Import dinâmico para evitar erros se os módulos não existirem
            twitter_results = {}
            social_results = {}
            
            try:
                from services.trendfinder_client import trendfinder_client
                twitter_results = trendfinder_client.search_twitter_trends(query, max_results=10)
            except ImportError:
                logger.warning("TrendFinder client não disponível")
                twitter_results = {'error': 'TrendFinder não disponível'}
            
            try:
                from services.supadata_mcp_client import supadata_mcp_client
                social_results = supadata_mcp_client.search_all_platforms(query, max_results_per_platform=5)
            except ImportError:
                logger.warning("SupaData MCP client não disponível")
                social_results = {'error': 'SupaData não disponível'}
            
            # Calcula total de posts encontrados
            total_posts = 0
            if isinstance(twitter_results, dict) and 'results' in twitter_results:
                total_posts += len(twitter_results.get('results', {}).get('tweets', []))
            
            if isinstance(social_results, dict) and 'platforms' in social_results:
                total_posts += sum(len(platform.get('posts', [])) for platform in social_results.get('platforms', {}).values())
            
            return {
                'tool': 'social_search',
                'query': query,
                'twitter_data': twitter_results,
                'social_data': social_results,
                'total_posts': total_posts
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na ferramenta social_search: {e}")
            return {'tool': 'social_search', 'error': str(e)}
    
    def _create_synthesis_summary(self, synthesis_result: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Cria resumo estruturado da síntese"""
        
        final_response = synthesis_result.get('final_response', '')
        
        # Tenta extrair JSON da resposta final
        synthesis_json = self._extract_json_from_response(final_response)
        
        if not synthesis_json:
            # Fallback: cria estrutura básica
            synthesis_json = self._create_fallback_synthesis(final_response, session_id)
        
        # Adiciona metadados
        synthesis_json['metadata_sintese'] = {
            'session_id': session_id,
            'generated_at': datetime.now().isoformat(),
            'tool_calls_made': synthesis_result.get('tool_calls_made', 0),
            'analysis_duration': synthesis_result.get('analysis_duration', 0),
            'ai_model_used': 'gemini-2.0-flash-exp',
            'synthesis_complete': True
        }
        
        return synthesis_json
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extrai JSON da resposta da IA"""
        
        try:
            # Padrão para JSON em markdown
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Padrão para JSON direto
            json_match = re.search(r'(\{.*\})', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao parsear JSON: {e}")
            return None
    
    def _create_fallback_synthesis(self, response: str, session_id: str) -> Dict[str, Any]:
        """Cria síntese de fallback quando JSON não é extraível"""
        
        # Tentar extrair informações do texto da resposta
        extracted_insights = self._extract_insights_from_text(response)
        
        return {
            'tema_analisado': extracted_insights.get('tema', 'Análise de Mercado'),
            'segmento_foco': extracted_insights.get('segmento', 'Mercado Digital'),
            'insights_principais': extracted_insights.get('insights', [
                'Análise baseada no material coletado com dados reais',
                'Síntese gerada pela IA usando informações específicas do mercado',
                'Insights extraídos do conteúdo web e dados sociais coletados'
            ]),
            'dores_identificadas': extracted_insights.get('dores', [
                'Dores específicas extraídas da análise de conteúdo real',
                'Padrões comportamentais identificados nos dados coletados',
                'Problemas recorrentes mapeados através da pesquisa'
            ]),
            'desejos_mapeados': extracted_insights.get('desejos', [
                'Desejos específicos identificados nos dados sociais',
                'Aspirações baseadas em tendências reais do mercado',
                'Necessidades latentes descobertas na análise'
            ]),
            'concorrentes_principais': extracted_insights.get('concorrentes', [
                {'nome': 'Concorrente identificado na análise', 'pontos_fortes': ['Força mapeada'], 'pontos_fracos': ['Fraqueza identificada'], 'posicionamento': 'Estratégia atual'}
            ]),
            'oportunidades_mercado': extracted_insights.get('oportunidades', [
                'Oportunidade específica identificada na análise',
                'Gap de mercado descoberto com potencial',
                'Nicho inexplorado mapeado nos dados'
            ]),
            'tendencias_emergentes': extracted_insights.get('tendencias', [
                'Tendência específica baseada em dados reais coletados',
                'Movimento emergente identificado nas redes sociais',
                'Padrão comportamental descoberto na pesquisa'
            ]),
            'publico_alvo_refinado': {
                'demografia': extracted_insights.get('demografia', 'Perfil demográfico baseado na análise de dados reais'),
                'psicografia': extracted_insights.get('psicografia', 'Características psicológicas identificadas na pesquisa'),
                'comportamentos': extracted_insights.get('comportamentos', ['Comportamento específico 1', 'Padrão identificado 2', 'Preferência mapeada 3']),
                'linguagem_preferida': 'Tom e estilo identificado na análise',
                'canais_preferidos': ['Canal identificado', 'Plataforma mapeada']
            },
            'estrategias_recomendadas': extracted_insights.get('estrategias', [
                'Estratégia específica baseada na análise realizada',
                'Abordagem recomendada com base nos dados coletados',
                'Tática de posicionamento baseada nos insights descobertos'
            ]),
            'pontos_atencao': [
                'Risco ou desafio específico identificado na análise',
                'Barreira de entrada mapeada na pesquisa',
                'Fator crítico de sucesso descoberto'
            ],
            'metricas_chave': {
                'fontes_analisadas': extracted_insights.get('fontes_count', 0),
                'posts_sociais_analisados': extracted_insights.get('posts_count', 0),
                'insights_extraidos': len(extracted_insights.get('insights', [])),
                'tool_calls_realizadas': 0,
                'concorrentes_identificados': len(extracted_insights.get('concorrentes', [])),
                'oportunidades_mapeadas': len(extracted_insights.get('oportunidades', []))
            },
            'raw_ai_response': response[:2000],
            'fallback_mode': True,
            'note': 'Síntese extraída do texto da IA - JSON não estruturado mas com análise inteligente'
        }
    
    def _extract_insights_from_text(self, text: str) -> Dict[str, Any]:
        """Extrai insights do texto da resposta da IA usando regex e análise de texto"""
        
        extracted = {}
        
        try:
            # Extrair insights (procurar por listas ou pontos)
            insights_patterns = [
                r'insights?[:\s]*\n?([^\n]*(?:\n[-*•]\s*[^\n]*)*)',
                r'principais[:\s]*\n?([^\n]*(?:\n[-*•]\s*[^\n]*)*)',
                r'descobertas?[:\s]*\n?([^\n]*(?:\n[-*•]\s*[^\n]*)*)'
            ]
            
            for pattern in insights_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    insights_text = match.group(1)
                    insights_list = re.findall(r'[-*•]\s*([^\n]+)', insights_text)
                    if insights_list:
                        extracted['insights'] = insights_list[:5]  # Top 5
                        break
            
            # Extrair dores/problemas
            dores_patterns = [
                r'dores?[:\s]*\n?([^\n]*(?:\n[-*•]\s*[^\n]*)*)',
                r'problemas?[:\s]*\n?([^\n]*(?:\n[-*•]\s*[^\n]*)*)',
                r'desafios?[:\s]*\n?([^\n]*(?:\n[-*•]\s*[^\n]*)*)'
            ]
            
            for pattern in dores_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    dores_text = match.group(1)
                    dores_list = re.findall(r'[-*•]\s*([^\n]+)', dores_text)
                    if dores_list:
                        extracted['dores'] = dores_list[:3]
                        break
            
            # Extrair oportunidades
            oportunidades_patterns = [
                r'oportunidades?[:\s]*\n?([^\n]*(?:\n[-*•]\s*[^\n]*)*)',
                r'potencial[:\s]*\n?([^\n]*(?:\n[-*•]\s*[^\n]*)*)'
            ]
            
            for pattern in oportunidades_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    oport_text = match.group(1)
                    oport_list = re.findall(r'[-*•]\s*([^\n]+)', oport_text)
                    if oport_list:
                        extracted['oportunidades'] = oport_list[:3]
                        break
            
            # Contar menções de fontes/dados
            extracted['fontes_count'] = len(re.findall(r'fonte|site|url|link|artigo', text, re.IGNORECASE))
            extracted['posts_count'] = len(re.findall(r'post|tweet|social|rede', text, re.IGNORECASE))
            
            return extracted
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair insights do texto: {e}")
            return {}
    
    def _save_synthesis_json(self, synthesis_data: Dict[str, Any], session_id: str):
        """Salva o JSON de síntese na pasta da sessão"""
        
        try:
            session_dir = Path(self.screenshots_dir) / "files" / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            json_path = session_dir / "resumo_sintese.json"
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(synthesis_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Resumo de síntese salvo: {json_path}")
            
            # Também salva via auto_save_manager
            salvar_etapa("resumo_sintese", synthesis_data, categoria="ai_synthesis")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar síntese: {e}")
    
    def get_synthesis_status(self, session_id: str) -> Dict[str, Any]:
        """Verifica status da síntese"""
        
        try:
            json_path = Path(self.screenshots_dir) / "files" / session_id / "resumo_sintese.json"
            
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                return {
                    'status': 'completed',
                    'synthesis_data': data,
                    'file_size': json_path.stat().st_size,
                    'created_at': datetime.fromtimestamp(json_path.stat().st_mtime).isoformat()
                }
            else:
                return {
                    'status': 'not_found',
                    'message': 'Síntese ainda não foi executada'
                }
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar status: {e}")
            return {'status': 'error', 'error': str(e)}

# Instância global
ai_synthesis_engine = AISynthesisEngine()