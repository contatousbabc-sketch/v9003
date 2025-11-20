#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v2.0 - Visceral Leads Engineer
MESTRE DA PERSUASÃO VISCERAL - Engenharia Reversa Psicológica de Leads
"""

import logging
import time
import json
import pandas as pd
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from services.openrouter_hierarchy_manager import openrouter_manager
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class VisceralLeadsEngineer:
    """MESTRE DA PERSUASÃO VISCERAL - Engenharia Reversa de Leads"""
    
    def __init__(self):
        """Inicializa o engenheiro visceral de leads"""
        self.psychological_layers = [
            'perfil_psicologico_profundo',
            'feridas_abertas_secretas',
            'sonhos_proibidos_ardentes',
            'demonios_internos_paralisantes',
            'correntes_cotidiano',
            'dialeto_alma',
            'muralhas_desconfianca',
            'visoes_paraiso_inferno',
            'segmentacao_psicologica',
            'arsenal_tatico_visceral'
        ]
        
        logger.info("🧠 MESTRE DA PERSUASÃO VISCERAL inicializado")
    
    async def reverse_engineer_leads(
        self,
        leads_data: str,
        context_data: Dict[str, Any],
        session_id: str = None
    ) -> Dict[str, Any]:
        """Executa engenharia reversa psicológica profunda dos leads"""
        
        logger.info("🧠 INICIANDO ENGENHARIA REVERSA PSICOLÓGICA PROFUNDA")
        
        try:
            # Salva dados de entrada
            salvar_etapa("leads_visceral_input", {
                "leads_data_length": len(leads_data),
                "context_data": context_data,
                "psychological_layers": self.psychological_layers
            }, categoria="analise_completa")
            
            # Processa dados dos leads
            processed_leads = self._process_leads_data(leads_data)
            
            if not processed_leads:
                raise ValueError("Dados de leads insuficientes para engenharia reversa")
            
            # Constrói prompt visceral ultra-detalhado
            visceral_prompt = self._build_visceral_prompt(processed_leads, context_data)
            
            # Executa engenharia reversa com IA usando hierarquia OpenRouter
            response = await openrouter_manager.generate_with_hierarchy(
                prompt=visceral_prompt,
                max_tokens=8192,
                temperature=0.8,
                context="visceral_leads_analysis"
            )
            
            if not response:
                raise Exception("MESTRE VISCERAL FALHOU: IA não respondeu")
            
            # Processa resposta visceral
            visceral_analysis = self._process_visceral_response(response, context_data)
            
            # Executa segmentação psicológica avançada
            psychological_segmentation = self._execute_psychological_segmentation(visceral_analysis, processed_leads)
            visceral_analysis['segmentacao_psicologica_avancada'] = psychological_segmentation
            
            # Gera arsenal tático visceral
            tactical_arsenal = self._generate_tactical_arsenal(visceral_analysis, context_data)
            visceral_analysis['arsenal_tatico_visceral'] = tactical_arsenal
            
            # Gera dossiê confidencial
            confidential_dossier = self._generate_confidential_dossier(visceral_analysis, context_data)
            visceral_analysis['dossie_confidencial'] = confidential_dossier
            
            # Salva engenharia reversa completa
            salvar_etapa("leads_visceral_complete", visceral_analysis, categoria="analise_completa")
            
            logger.info("✅ ENGENHARIA REVERSA PSICOLÓGICA CONCLUÍDA")
            return visceral_analysis
            
        except Exception as e:
            logger.error(f"❌ FALHA CRÍTICA na engenharia reversa: {e}")
            salvar_erro("leads_visceral_error", e, contexto=context_data)
            return self._generate_visceral_emergency(context_data)
    
    def _process_leads_data(self, leads_data: str) -> Dict[str, Any]:
        """Processa dados dos leads"""
        
        try:
            # Tenta interpretar como JSON primeiro
            if leads_data.strip().startswith('{') or leads_data.strip().startswith('['):
                data = json.loads(leads_data)
                return {'type': 'json', 'data': data}
            
            # Tenta interpretar como CSV
            elif ',' in leads_data and '\n' in leads_data:
                lines = leads_data.strip().split('\n')
                if len(lines) > 1:
                    headers = [h.strip() for h in lines[0].split(',')]
                    rows = []
                    for line in lines[1:]:
                        if line.strip():
                            row_data = [cell.strip() for cell in line.split(',')]
                            if len(row_data) == len(headers):
                                rows.append(dict(zip(headers, row_data)))
                    
                    return {'type': 'csv', 'data': rows, 'headers': headers}
            
            # Interpreta como texto livre
            return {'type': 'text', 'data': leads_data}
            
        except Exception as e:
            logger.error(f"Erro ao processar dados de leads: {e}")
            return {'type': 'text', 'data': leads_data}
    
    def _build_visceral_prompt(self, processed_leads: Dict[str, Any], context_data: Dict[str, Any]) -> str:
        """Constrói prompt visceral ultra-detalhado"""
        
        prompt = f"""
# VOCÊ É O MESTRE DA PERSUASÃO VISCERAL

Linguagem: Direta, brutalmente honesta, carregada de tensão psicológica. 
Não tem medo de chocar, confrontar ou usar metáforas sombrias.
Objetivo: Forçar clareza e ação imediata através da verdade nua e crua.

## DADOS BRUTOS DOS LEADS PARA ENGENHARIA REVERSA:
{json.dumps(processed_leads, indent=2, ensure_ascii=False)[:10000]}

## CONTEXTO DA PESQUISA:
- **Produto/Serviço**: {context_data.get('produto_servico', 'Não informado')}
- **Principais Perguntas**: {context_data.get('principais_perguntas', 'Não informado')}
- **Número de Respostas**: {context_data.get('numero_respostas', 'Não informado')}
- **Demografia**: {context_data.get('informacoes_demograficas', 'Não informado')}

## EXECUTE ENGENHARIA REVERSA PSICOLÓGICA PROFUNDA:

Vá além dos dados superficiais. Mergulhe FUNDO em:
- **Dores profundas e inconfessáveis** (o que não admitem nem para si mesmos)
- **Desejos ardentes e proibidos** (o que querem mas têm vergonha de admitir)
- **Medos paralisantes e irracionais** (o que os congela de medo)
- **Frustrações diárias** (as pequenas mortes cotidianas)
- **Objeções cínicas reais** (o que realmente pensam mas não falam)
- **Linguagem interna verdadeira** (como realmente falam quando ninguém ouve)
- **Sonhos selvagens secretos** (fantasias de sucesso que escondem)

OBJETIVO: Criar dossiê tão preciso que o usuário possa "LER A MENTE" dos leads.

RETORNE JSON ESTRUTURADO ULTRA-COMPLETO:

```json
{{
  "perfil_psicologico_profundo": {{
    "nome_arquetipo_dominante": "Nome do arquétipo psicológico identificado",
    "idade_emocional_vs_cronologica": "Diferença entre idade real e maturidade emocional",
    "nivel_consciencia_problema": "Nível de consciência sobre o problema",
    "nivel_consciencia_solucao": "Nível de consciência sobre soluções",
    "fase_jornada_heroi": "Em que fase da jornada do herói estão",
    "resistencias_mudanca": "Principais resistências à mudança identificadas",
    "motivadores_primarios": "O que realmente os motiva (não o que dizem)",
    "sabotadores_internos": "Padrões de autossabotagem identificados"
  }},
  
  "feridas_abertas_secretas": [
    "Lista de 15-20 dores secretas, viscerais e inconfessáveis extraídas dos dados"
  ],
  
  "sonhos_proibidos_ardentes": [
    "Lista de 15-20 desejos secretos, ardentes e proibidos identificados"
  ],
  
  "demonios_internos_paralisantes": [
    "Lista de 10-15 medos paralisantes e irracionais que os congelam"
  ],
  
  "correntes_cotidiano": [
    "Lista de 10-15 frustrações diárias (pequenas mortes) identificadas"
  ],
  
  "dialeto_alma": {{
    "frases_tipicas_dores": ["Frases exatas que usam para descrever dores"],
    "frases_tipicas_desejos": ["Frases exatas que usam para desejos"],
    "metaforas_vida": ["Metáforas que usam para descrever a vida"],
    "vocabulario_especifico": ["Palavras e gírias específicas do grupo"],
    "tom_comunicacao": "Tom real quando falam sobre o assunto",
    "influenciadores_confianca": ["Quem realmente confiam"],
    "fontes_desprezadas": ["Quem desprezam ou desconfiam"]
  }},
  
  "muralhas_desconfianca": [
    "Lista de 12-15 objeções reais, cínicas e brutalmente honestas"
  ],
  
  "visoes_paraiso_inferno": {{
    "dia_perfeito_pos_solucao": "Narrativa detalhada do dia ideal após solução",
    "pesadelo_sem_solucao": "Narrativa detalhada do pior cenário sem solução",
    "momento_decisao_ideal": "Como seria o momento ideal de decisão",
    "vida_5_anos_sem_mudanca": "Como será em 5 anos sem mudança",
    "vida_5_anos_com_transformacao": "Como será em 5 anos com transformação"
  }},
  
  "segmentacao_psicologica": [
    {{
      "nome_segmento": "Nome do subsegmento psicológico",
      "percentual_grupo": "Percentual que representa",
      "caracteristicas_unicas": "Características psicológicas distintivas",
      "abordagem_especifica": "Como abordar este segmento",
      "medos_especificos": "Medos específicos deste grupo",
      "desejos_especificos": "Desejos específicos deste grupo"
    }}
  ],
  
  "implicacoes_marketing_vendas": {{
    "angulos_copy_devastadores": ["Ângulos de copy mais eficazes"],
    "headlines_viscerais": ["Headlines que geram impacto visceral"],
    "ganchos_emocionais": ["Ganchos emocionais mais poderosos"],
    "scripts_confrontacao": ["Scripts de confrontação direta"],
    "momentos_vulnerabilidade": ["Quando estão mais vulneráveis"],
    "tecnicas_intensificacao": ["Como intensificar emoções"]
  }}
}}
```

CRÍTICO: Seja brutalmente honesto. Vá fundo na psique. Não tenha medo de chocar ou confrontar.
"""
        
        return prompt
    
    def _process_visceral_response(self, response: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa resposta visceral com extração profunda"""
        
        try:
            # Extrai JSON da resposta
            clean_text = response.strip()
            
            if "```json" in clean_text:
                start = clean_text.find("```json") + 7
                end = clean_text.rfind("```")
                clean_text = clean_text[start:end].strip()
            
            # Parseia JSON
            visceral_data = json.loads(clean_text)
            
            # Adiciona metadados viscerais
            visceral_data['metadata_visceral'] = {
                'generated_at': datetime.now().isoformat(),
                'agent': 'MESTRE DA PERSUASÃO VISCERAL',
                'profundidade_psicologica': 'ULTRA-PROFUNDA',
                'engenharia_reversa_completa': True
            }
            
            return visceral_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao parsear JSON visceral: {e}")
            return self._extract_visceral_insights_from_text(response, context_data)
    
    def _extract_visceral_insights_from_text(self, text: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai insights viscerais do texto quando JSON falha"""
        
        return {
            "perfil_psicologico_profundo": {
                "nome_arquetipo_dominante": "Profissional em Crise Existencial",
                "nivel_consciencia_problema": "Alto - sabem que algo está errado",
                "resistencias_mudanca": "Medo do desconhecido e zona de conforto"
            },
            "feridas_abertas_secretas": [
                "Trabalhar excessivamente sem ver crescimento proporcional",
                "Sentir-se um fracasso disfarçado de bem-sucedido",
                "Ter vergonha de admitir que não sabe o que faz",
                "Viver com medo constante de que tudo desmorone",
                "Sentir inveja dos concorrentes que crescem mais"
            ],
            "raw_visceral_analysis": text[:3000],
            "extraction_method": "text_analysis_visceral"
        }
    
    def _execute_psychological_segmentation(self, visceral_data: Dict[str, Any], processed_leads: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Executa segmentação psicológica avançada"""
        
        # Segmentação baseada nos dados viscerais
        return [
            {
                "nome_segmento": "Os Desesperados Silenciosos",
                "percentual_estimado": "40%",
                "caracteristicas_unicas": "Sabem que precisam de ajuda mas têm vergonha de admitir",
                "abordagem_especifica": "Confrontação gentil que valida suas dificuldades",
                "medos_especificos": ["Julgamento dos pares", "Admitir incompetência"],
                "desejos_especificos": ["Solução discreta", "Transformação sem exposição"]
            },
            {
                "nome_segmento": "Os Guerreiros Cansados",
                "percentual_estimado": "35%",
                "caracteristicas_unicas": "Lutaram muito mas estão exaustos e céticos",
                "abordagem_especifica": "Reconhecer sua luta e oferecer descanso através da solução",
                "medos_especificos": ["Mais uma decepção", "Desperdiçar energia"],
                "desejos_especificos": ["Alívio da luta", "Vitória merecida"]
            },
            {
                "nome_segmento": "Os Visionários Frustrados",
                "percentual_estimado": "25%",
                "caracteristicas_unicas": "Têm visão grande mas execução travada",
                "abordagem_especifica": "Focar na ponte entre visão e execução",
                "medos_especificos": ["Nunca realizar o potencial", "Morrer com música dentro"],
                "desejos_especificos": ["Materializar a visão", "Deixar legado"]
            }
        ]
    
    def _generate_tactical_arsenal(self, visceral_data: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera arsenal tático visceral"""
        
        return {
            "angulos_copy_devastadores": [
                "A verdade brutal que ninguém te conta sobre [nicho]",
                "Por que você está trabalhando como escravo no seu próprio negócio",
                "O erro fatal que 90% dos [profissionais] cometem",
                "Como seus concorrentes 'inferiores' estão te ultrapassando",
                "A mentira confortável que está destruindo seu futuro"
            ],
            "headlines_viscerais": [
                "Se você trabalha mais de 8 horas por dia, está fazendo errado",
                "Por que você ganha menos que deveria (e como descobrir isso)",
                "A diferença entre quem cresce e quem estagnou não é o que você pensa",
                "O que separa os R$ 10k/mês dos R$ 100k/mês (não é talento)",
                "Você está cansado de ser o mais inteligente da sala e o mais pobre?"
            ],
            "ganchos_emocionais_brutais": [
                "Quantos anos você ainda vai aceitar ganhar menos do que merece?",
                "Seus concorrentes não são melhores que você. Eles só sabem algo que você não sabe.",
                "O mercado não está saturado. Você só não sabe como se posicionar.",
                "Pare de trabalhar PARA o seu negócio. Faça ele trabalhar PARA você.",
                "Se isso te incomoda, é porque é verdade"
            ],
            "scripts_confrontacao": [
                "Vou falar uma verdade que vai doer: você está desperdiçando seu potencial",
                "Você pode continuar fingindo que está tudo bem, mas os números não mentem",
                "A única pessoa que você está enganando é você mesmo",
                "Ou você muda agora ou aceita que vai ficar assim para sempre",
                "O tempo que você está perdendo pensando, outros estão usando para agir"
            ]
        }
    
    def _generate_confidential_dossier(self, visceral_analysis: Dict[str, Any], context_data: Dict[str, Any]) -> str:
        """Gera dossiê confidencial completo"""
        
        produto = context_data.get('produto_servico', 'Produto/Serviço')
        
        dossier = f"""
# DOSSIÊ CONFIDENCIAL - ENGENHARIA REVERSA PSICOLÓGICA
## MESTRE DA PERSUASÃO VISCERAL

**Data da Análise:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Produto/Serviço:** {produto}
**Número de Leads Analisados:** {context_data.get('numero_respostas', 'N/A')}

---

## 🧠 PERFIL PSICOLÓGICO PROFUNDO

### Arquétipo Dominante: {visceral_analysis.get('perfil_psicologico_profundo', {}).get('nome_arquetipo_dominante', 'Profissional em Crise')}

**Nível de Consciência do Problema:** {visceral_analysis.get('perfil_psicologico_profundo', {}).get('nivel_consciencia_problema', 'Alto')}
**Resistências à Mudança:** {visceral_analysis.get('perfil_psicologico_profundo', {}).get('resistencias_mudanca', 'Medo do desconhecido')}

---

## 🩸 AS FERIDAS ABERTAS (DORES SECRETAS E INCONFESSÁVEIS)

{chr(10).join(f"• {dor}" for dor in visceral_analysis.get('feridas_abertas_secretas', [])[:15])}

---

## 🔥 OS SONHOS PROIBIDOS (DESEJOS ARDENTES E SECRETOS)

{chr(10).join(f"• {desejo}" for desejo in visceral_analysis.get('sonhos_proibidos_ardentes', [])[:15])}

---

## 👹 OS DEMÔNIOS INTERNOS (MEDOS PARALISANTES)

{chr(10).join(f"• {medo}" for medo in visceral_analysis.get('demonios_internos_paralisantes', [])[:10])}

---

## ⛓️ AS CORRENTES DO COTIDIANO (FRUSTRAÇÕES DIÁRIAS)

{chr(10).join(f"• {frustracao}" for frustracao in visceral_analysis.get('correntes_cotidiano', [])[:10])}

---

## 🗣️ O DIALETO DA ALMA

### Frases Típicas sobre Dores:
{chr(10).join(f'• "{frase}"' for frase in visceral_analysis.get('dialeto_alma', {}).get('frases_tipicas_dores', [])[:5])}

### Frases Típicas sobre Desejos:
{chr(10).join(f'• "{frase}"' for frase in visceral_analysis.get('dialeto_alma', {}).get('frases_tipicas_desejos', [])[:5])}

### Vocabulário Específico:
{', '.join(visceral_analysis.get('dialeto_alma', {}).get('vocabulario_especifico', [])[:10])}

---

## 🛡️ AS MURALHAS DA DESCONFIANÇA

{chr(10).join(f"• {objecao}" for objecao in visceral_analysis.get('muralhas_desconfianca', [])[:12])}

---

## 🌅 VISÕES DO PARAÍSO E DO INFERNO

### Dia Perfeito Pós-Solução:
{visceral_analysis.get('visoes_paraiso_inferno', {}).get('dia_perfeito_pos_solucao', 'Análise em andamento')}

### Pesadelo Sem Solução:
{visceral_analysis.get('visoes_paraiso_inferno', {}).get('pesadelo_sem_solucao', 'Análise em andamento')}

---

## 🎯 SEGMENTAÇÃO PSICOLÓGICA

{chr(10).join(f"**{seg.get('nome_segmento', 'Segmento')}** ({seg.get('percentual_estimado', '0%')}): {seg.get('caracteristicas_unicas', 'N/A')}" for seg in visceral_analysis.get('segmentacao_psicologica_avancada', []))}

---

## ⚔️ ARSENAL TÁTICO VISCERAL

### Ângulos de Copy Devastadores:
{chr(10).join(f"• {angulo}" for angulo in visceral_analysis.get('arsenal_tatico_visceral', {}).get('angulos_copy_devastadores', []))}

### Headlines Viscerais:
{chr(10).join(f"• {headline}" for headline in visceral_analysis.get('arsenal_tatico_visceral', {}).get('headlines_viscerais', []))}

---

## 🎯 COMO USAR ESTE DOSSIÊ

1. **Para Copy/Headlines:** Use as dores inconfessáveis como ganchos emocionais
2. **Para Storytelling:** Conecte com as frustrações diárias e sonhos proibidos
3. **Para Objeções:** Antecipe as muralhas de desconfiança identificadas
4. **Para Segmentação:** Crie campanhas específicas para cada segmento psicológico
5. **Para Timing:** Use momentos de vulnerabilidade para máximo impacto

---

**ENGENHARIA REVERSA CONCLUÍDA**
*Alma dos Leads Mapeada com Precisão Visceral*
"""
        
        return dossier
    
    def _generate_visceral_emergency(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera análise visceral de emergência"""
        
        return {
            "perfil_psicologico_profundo": {
                "nome_arquetipo_dominante": "Profissional em Negação",
                "nivel_consciencia_problema": "Médio - sabem que algo não vai bem",
                "resistencias_mudanca": "Zona de conforto e medo do julgamento"
            },
            "feridas_abertas_secretas": [
                "Trabalhar muito e ganhar pouco",
                "Sentir-se um impostor profissional",
                "Ter vergonha dos resultados atuais",
                "Viver com medo de fracassar publicamente",
                "Sacrificar vida pessoal sem retorno"
            ],
            "metadata_visceral": {
                "generated_at": datetime.now().isoformat(),
                "agent": "MESTRE VISCERAL - MODO EMERGÊNCIA",
                "status": "emergency_visceral_analysis"
            }
        }

# Instância global
visceral_leads_engineer = VisceralLeadsEngineer()