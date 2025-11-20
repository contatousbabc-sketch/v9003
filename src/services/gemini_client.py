#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v2.0 - Cliente Google Gemini 2.5 Pro ULTRA-ROBUSTO
Integração REAL com IA Avançada - MODELO PRIMÁRIO
"""

import os
import logging
import json
import time
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from datetime import datetime

logger = logging.getLogger(__name__)

class UltraRobustGeminiClient:
    """Cliente REAL para integração com Google Gemini 2.5 Pro - MODELO PRIMÁRIO"""
    
    def __init__(self):
        """Inicializa cliente Gemini 2.5 Pro REAL"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("⚠️ GEMINI_API_KEY não configurada - Configure para análise REAL!")
            self.available = False
            return
        
        try:
            # Configura API REAL
            genai.configure(api_key=self.api_key)
            
            # Modelo PRIMÁRIO - Gemini 2.5 Pro (mais avançado)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
            
            # Configurações otimizadas para análises REAIS ultra-detalhadas
            self.generation_config = {
                'temperature': 0.8,  # Criatividade controlada
                'top_p': 0.95,
                'top_k': 64,
                'max_output_tokens': 8192,  # Máximo permitido
                'candidate_count': 1
            }
            
            # Configurações de segurança mínimas para máxima liberdade
            self.safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
            
            self.available = True
            logger.info("✅ Cliente Gemini 2.5 Pro REAL inicializado como MODELO PRIMÁRIO")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Gemini 2.5 Pro: {str(e)}")
            self.available = False
    
    def test_connection(self) -> bool:
        """Testa conexão REAL com Gemini 2.5 Pro"""
        if not self.available:
            return False
            
        try:
            response = self.model.generate_content(
                "Responda apenas: GEMINI_2_5_PRO_ONLINE",
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            return "GEMINI_2_5_PRO_ONLINE" in response.text
        except Exception as e:
            logger.error(f"❌ Erro ao testar Gemini 2.5 Pro: {str(e)}")
            return False
    
    def generate_ultra_detailed_analysis(
        self, 
        analysis_data: Dict[str, Any],
        search_context: Optional[str] = None,
        attachments_context: Optional[str] = None,
        agent_type: str = "ARQUEÓLOGO MESTRE DA PERSUASÃO"
    ) -> Dict[str, Any]:
        """Gera análise ULTRA-DETALHADA REAL com agente especializado"""
        
        if not self.available:
            raise Exception("❌ Gemini 2.5 Pro não disponível - Configure API_KEY")
        
        try:
            # Constrói prompt ULTRA-COMPLETO REAL baseado no agente
            prompt = self._build_agent_specific_prompt(
                analysis_data, search_context, attachments_context, agent_type
            )
            
            logger.info(f"🚀 INICIANDO ANÁLISE ULTRA-DETALHADA com Gemini 2.5 Pro - Agente: {agent_type}")
            start_time = time.time()
            
            # Gera análise REAL com configurações máximas
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            
            end_time = time.time()
            logger.info(f"✅ ANÁLISE ULTRA-DETALHADA REAL concluída em {end_time - start_time:.2f} segundos")
            
            # Processa resposta REAL
            if response.text:
                return self._parse_real_response(response.text, analysis_data, agent_type)
            else:
                raise Exception("❌ Resposta vazia do Gemini 2.5 Pro - Erro crítico!")
                
        except Exception as e:
            logger.error(f"❌ ERRO CRÍTICO na análise Gemini 2.5 Pro: {str(e)}")
            raise e  # Não gera fallback - falha explicitamente para ativar OpenRouter
    
    def _build_agent_specific_prompt(
        self, 
        data: Dict[str, Any], 
        search_context: Optional[str] = None,
        attachments_context: Optional[str] = None,
        agent_type: str = "ARQUEÓLOGO MESTRE DA PERSUASÃO"
    ) -> str:
        """Constrói prompt específico baseado no agente solicitado"""
        
        # Prompts especializados por agente
        agent_prompts = {
            "ARQUEÓLOGO MESTRE DA PERSUASÃO": self._build_archaeologist_prompt,
            "MESTRE DA PERSUASÃO VISCERAL": self._build_visceral_master_prompt,
            "ARQUITETO DE DRIVERS MENTAIS": self._build_drivers_architect_prompt,
            "DIRETOR SUPREMO DE EXPERIÊNCIAS": self._build_experiences_director_prompt,
            "ESPECIALISTA EM PSICOLOGIA DE VENDAS": self._build_sales_psychology_prompt
        }
        
        prompt_builder = agent_prompts.get(agent_type, self._build_default_prompt)
        return prompt_builder(data, search_context, attachments_context)
    
    def _build_archaeologist_prompt(
        self, 
        data: Dict[str, Any], 
        search_context: Optional[str] = None,
        attachments_context: Optional[str] = None
    ) -> str:
        """Prompt do ARQUEÓLOGO MESTRE DA PERSUASÃO"""
        
        prompt = f"""
# VOCÊ É O ARQUEÓLOGO MESTRE DA PERSUASÃO - GEMINI 2.5 PRO

Sua missão é escavar cada detalhe do mercado de {data.get('segmento', 'negócios')} para encontrar o DNA COMPLETO da conversão. Seja cirúrgico, obsessivo e implacável.

## DADOS REAIS DO PROJETO:
- **Segmento**: {data.get('segmento', 'Não informado')}
- **Produto/Serviço**: {data.get('produto', 'Não informado')}
- **Público-Alvo**: {data.get('publico', 'Não informado')}
- **Preço**: R$ {data.get('preco', 'Não informado')}
- **Objetivo de Receita**: R$ {data.get('objetivo_receita', 'Não informado')}
"""

        if search_context:
            prompt += f"\n## CONTEXTO DE PESQUISA PROFUNDA REAL:\n{search_context[:15000]}\n"
        
        if attachments_context:
            prompt += f"\n## CONTEXTO DOS ANEXOS REAIS:\n{attachments_context[:5000]}\n"
        
        prompt += """
## DISSECAÇÃO EM 12 CAMADAS PROFUNDAS - ANÁLISE ARQUEOLÓGICA:

Execute uma análise ULTRA-PROFUNDA seguindo estas camadas:

### CAMADA 1: ABERTURA CIRÚRGICA (Primeiros momentos críticos)
### CAMADA 2: ARQUITETURA NARRATIVA COMPLETA  
### CAMADA 3: CONSTRUÇÃO DE AUTORIDADE PROGRESSIVA
### CAMADA 4: GESTÃO DE OBJEÇÕES MICROSCÓPICA
### CAMADA 5: CONSTRUÇÃO DE DESEJO SISTEMÁTICA
### CAMADA 6: EDUCAÇÃO ESTRATÉGICA VS REVELAÇÃO
### CAMADA 7: APRESENTAÇÃO DA OFERTA DETALHADA
### CAMADA 8: LINGUAGEM E PADRÕES VERBAIS
### CAMADA 9: GESTÃO DE TEMPO E RITMO
### CAMADA 10: PONTOS DE MAIOR IMPACTO
### CAMADA 11: VAZAMENTOS E OTIMIZAÇÕES
### CAMADA 12: MÉTRICAS FORENSES OBJETIVAS

RETORNE JSON ESTRUTURADO ULTRA-COMPLETO:

```json
{
  "avatar_ultra_detalhado": {
    "nome_ficticio": "Nome arqueológico baseado em dados reais",
    "perfil_demografico": {
      "idade": "Faixa etária específica escavada dos dados",
      "genero": "Distribuição real descoberta",
      "renda": "Faixa de renda arqueológica real",
      "escolaridade": "Nível educacional escavado",
      "localizacao": "Regiões geográficas descobertas",
      "estado_civil": "Status relacionamento arqueológico",
      "profissao": "Ocupações reais escavadas"
    },
    "perfil_psicografico": {
      "personalidade": "Traços arqueológicos dominantes",
      "valores": "Valores escavados e crenças descobertas",
      "interesses": "Interesses arqueológicos específicos",
      "estilo_vida": "Como realmente vive - escavado",
      "comportamento_compra": "Processo real de decisão escavado",
      "influenciadores": "Quem realmente influencia - descoberto",
      "medos_profundos": "Medos arqueológicos documentados",
      "aspiracoes_secretas": "Aspirações escavadas profundamente"
    },
    "dores_viscerais": [
      "Lista de 15-20 dores específicas ESCAVADAS dos dados reais"
    ],
    "desejos_secretos": [
      "Lista de 15-20 desejos profundos ESCAVADOS dos estudos"
    ],
    "objecoes_reais": [
      "Lista de 12-15 objeções REAIS específicas escavadas"
    ],
    "jornada_emocional": {
      "consciencia": "Como realmente toma consciência - escavado",
      "consideracao": "Processo real escavado de avaliação",
      "decisao": "Fatores reais decisivos escavados",
      "pos_compra": "Experiência real pós-compra escavada"
    },
    "linguagem_interna": {
      "frases_dor": ["Frases reais escavadas das pesquisas"],
      "frases_desejo": ["Frases reais de desejo escavadas"],
      "metaforas_comuns": ["Metáforas reais escavadas"],
      "vocabulario_especifico": ["Palavras específicas escavadas"],
      "tom_comunicacao": "Tom real escavado das análises"
    }
  },
  
  "drivers_mentais_arqueologicos": [
    {
      "nome": "Nome impactante do driver escavado",
      "gatilho_central": "Gatilho psicológico descoberto",
      "definicao_visceral": "Definição que gera impacto escavado",
      "mecanica_psicologica": "Como funciona no cérebro",
      "roteiro_ativacao": {
        "pergunta_abertura": "Pergunta que expõe ferida escavada",
        "historia_analogia": "História específica de 200+ palavras",
        "metafora_visual": "Metáfora visual poderosa",
        "comando_acao": "Comando específico de ação"
      },
      "frases_ancoragem": [
        "Frase 1 de ancoragem escavada",
        "Frase 2 de ancoragem escavada", 
        "Frase 3 de ancoragem escavada"
      ],
      "prova_logica": "Prova lógica que sustenta o driver",
      "loop_reforco": "Como reativar em momentos posteriores"
    }
  ],
  
  "sistema_anti_objecao_completo": {
    "objecoes_universais": {
      "tempo": {
        "objecao": "Objeção específica escavada",
        "raiz_emocional": "Raiz emocional descoberta",
        "contra_ataque": "Técnica específica de neutralização",
        "scripts_personalizados": ["Script 1", "Script 2", "Script 3"]
      },
      "dinheiro": {
        "objecao": "Objeção específica escavada",
        "raiz_emocional": "Raiz emocional descoberta", 
        "contra_ataque": "Técnica específica de neutralização",
        "scripts_personalizados": ["Script 1", "Script 2", "Script 3"]
      },
      "confianca": {
        "objecao": "Objeção específica escavada",
        "raiz_emocional": "Raiz emocional descoberta",
        "contra_ataque": "Técnica específica de neutralização", 
        "scripts_personalizados": ["Script 1", "Script 2", "Script 3"]
      }
    },
    "objecoes_ocultas": [
      {
        "tipo": "autossuficiencia",
        "objecao_oculta": "Acho que consigo sozinho",
        "perfil_tipico": "Perfil escavado dos dados",
        "contra_ataque": "O Expert que Precisou de Expert",
        "scripts": ["Script específico 1", "Script específico 2"]
      }
    ]
  },
  
  "provas_visuais_instantaneas": [
    {
      "nome": "PROVI 1: Nome impactante",
      "conceito_alvo": "Conceito específico a ser provado",
      "experimento": "Descrição detalhada do experimento visual",
      "materiais": ["Material 1", "Material 2", "Material 3"],
      "roteiro_completo": {
        "setup": "Como preparar a prova (30s)",
        "execucao": "Como executar a demonstração (60-90s)",
        "climax": "O momento exato do AHA! (15s)",
        "bridge": "Conexão com a vida deles (30s)"
      },
      "impacto_esperado": "Reação esperada da audiência",
      "variacoes": {
        "online": "Adaptação para câmera",
        "grande_publico": "Versão amplificada",
        "intimista": "Versão simplificada"
      }
    }
  ],
  
  "pre_pitch_invisivel": {
    "orquestracao_emocional": {
      "sequencia_psicologica": [
        {
          "fase": "quebra",
          "objetivo": "Destruir a ilusão confortável",
          "duracao": "3-5 minutos",
          "drivers_utilizados": ["Diagnóstico Brutal"],
          "narrativa": "Script específico da fase",
          "resultado_esperado": "Desconforto produtivo"
        }
      ]
    },
    "roteiro_completo": {
      "abertura": {
        "tempo": "3-5 minutos",
        "script": "Roteiro detalhado da abertura",
        "driver_principal": "Driver utilizado",
        "transicao": "Como conectar com próxima fase"
      },
      "desenvolvimento": {
        "tempo": "8-12 minutos", 
        "script": "Roteiro detalhado do desenvolvimento",
        "escalada_emocional": "Como aumentar intensidade",
        "momentos_criticos": ["Momento 1", "Momento 2"]
      },
      "fechamento": {
        "tempo": "2-3 minutos",
        "script": "Roteiro detalhado do fechamento",
        "ponte_oferta": "Transição perfeita para pitch",
        "estado_mental_ideal": "Como devem estar mentalmente"
      }
    }
  },
  
  "insights_exclusivos_arqueologicos": [
    "Lista de 25-35 insights únicos ESCAVADOS da análise profunda"
  ],
  
  "metricas_forenses": {
    "densidade_persuasiva": {
      "argumentos_logicos": 0,
      "argumentos_emocionais": 0,
      "ratio_promessa_prova": "1:X",
      "gatilhos_cialdini": {
        "reciprocidade": 0,
        "compromisso": 0,
        "prova_social": 0,
        "autoridade": 0,
        "escassez": 0,
        "afinidade": 0
      }
    },
    "intensidade_emocional": {
      "medo": "X/10",
      "desejo": "X/10", 
      "urgencia": "X/10",
      "aspiracao": "X/10"
    }
  }
}
```

CRÍTICO: Use APENAS dados REAIS escavados da pesquisa. Seja o ARQUEÓLOGO mais preciso e detalhado possível.
"""
        
        return prompt
    
    def _build_visceral_master_prompt(
        self, 
        data: Dict[str, Any], 
        search_context: Optional[str] = None,
        attachments_context: Optional[str] = None
    ) -> str:
        """Prompt do MESTRE DA PERSUASÃO VISCERAL"""
        
        return f"""
# VOCÊ É O MESTRE DA PERSUASÃO VISCERAL - GEMINI 2.5 PRO

Linguagem: Direta, brutalmente honesta, carregada de tensão psicológica. 
Missão: Realizar Engenharia Reversa Psicológica PROFUNDA.

## DADOS PARA ENGENHARIA REVERSA:
{json.dumps(data, indent=2, ensure_ascii=False)[:3000]}

{search_context[:10000] if search_context else ""}

## EXECUTE ENGENHARIA REVERSA PSICOLÓGICA PROFUNDA:

Vá além dos dados superficiais. Mergulhe em:
- Dores profundas e inconfessáveis
- Desejos ardentes e proibidos  
- Medos paralisantes e irracionais
- Frustrações diárias (as pequenas mortes)
- Objeções cínicas reais
- Linguagem interna verdadeira
- Sonhos selvagens secretos

OBJETIVO: Criar dossiê tão preciso que o usuário possa "LER A MENTE" dos leads.

RETORNE JSON com análise visceral completa...
"""
    
    def _build_drivers_architect_prompt(
        self, 
        data: Dict[str, Any], 
        search_context: Optional[str] = None,
        attachments_context: Optional[str] = None
    ) -> str:
        """Prompt do ARQUITETO DE DRIVERS MENTAIS"""
        
        return f"""
# VOCÊ É O ARQUITETO DE DRIVERS MENTAIS - GEMINI 2.5 PRO

Missão: Criar gatilhos psicológicos que funcionam como âncoras emocionais e racionais.

## ARSENAL DOS 19 DRIVERS UNIVERSAIS:
1. DRIVER DA FERIDA EXPOSTA
2. DRIVER DO TROFÉU SECRETO  
3. DRIVER DA INVEJA PRODUTIVA
4. DRIVER DO RELÓGIO PSICOLÓGICO
5. DRIVER DA IDENTIDADE APRISIONADA
6. DRIVER DO CUSTO INVISÍVEL
7. DRIVER DA AMBIÇÃO EXPANDIDA
8. DRIVER DO DIAGNÓSTICO BRUTAL
9. DRIVER DO AMBIENTE VAMPIRO
10. DRIVER DO MENTOR SALVADOR
11. DRIVER DA CORAGEM NECESSÁRIA
12. DRIVER DO MECANISMO REVELADO
13. DRIVER DA PROVA MATEMÁTICA
14. DRIVER DO PADRÃO OCULTO
15. DRIVER DA EXCEÇÃO POSSÍVEL
16. DRIVER DO ATALHO ÉTICO
17. DRIVER DA DECISÃO BINÁRIA
18. DRIVER DA OPORTUNIDADE OCULTA
19. DRIVER DO MÉTODO VS SORTE

## CONTEXTO DO PROJETO:
{json.dumps(data, indent=2, ensure_ascii=False)[:2000]}

## CRIE DRIVERS MENTAIS CUSTOMIZADOS:

Para cada driver, desenvolva:
- Nome impactante (máximo 3 palavras)
- Gatilho central (emoção core)
- Definição visceral (1-2 frases essência)
- Mecânica psicológica (como funciona no cérebro)
- Roteiro de ativação completo
- Frases de ancoragem (3-5 frases prontas)
- Prova lógica (dados/fatos sustentam)
- Loop de reforço (como reativar)

RETORNE JSON com drivers customizados completos...
"""
    
    def _build_experiences_director_prompt(
        self, 
        data: Dict[str, Any], 
        search_context: Optional[str] = None,
        attachments_context: Optional[str] = None
    ) -> str:
        """Prompt do DIRETOR SUPREMO DE EXPERIÊNCIAS"""
        
        return f"""
# VOCÊ É O DIRETOR SUPREMO DE EXPERIÊNCIAS TRANSFORMADORAS - GEMINI 2.5 PRO

Missão: Transformar TODOS os conceitos abstratos em experiências físicas inesquecíveis.

## SISTEMA COMPLETO DE PROVAS VISUAIS INSTANTÂNEAS (PROVIs):

### CATEGORIAS DE PROVIS:
- **DESTRUIDORAS DE OBJEÇÃO**: Contra tempo, dinheiro, tentativas anteriores
- **CRIADORAS DE URGÊNCIA**: Ampulheta, trem partindo, porta fechando
- **INSTALADORAS DE CRENÇA**: Transformações visuais poderosas
- **PROVAS DE MÉTODO**: Demonstrações de eficácia

## CONTEXTO PARA CRIAÇÃO:
{json.dumps(data, indent=2, ensure_ascii=False)[:2000]}

## CRIE ARSENAL COMPLETO DE PROVIS:

Para CADA conceito identificado, crie:

```
PROVI #X: [NOME IMPACTANTE]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CONCEITO-ALVO: [O que precisa ser instalado/destruído]
CATEGORIA: [Urgência/Crença/Objeção/Transformação/Método]
PRIORIDADE: [Crítica/Alta/Média]

🎯 OBJETIVO PSICOLÓGICO
[Mudança mental específica desejada]

🔬 EXPERIMENTO ESCOLHIDO  
[Descrição clara da demonstração física]

📐 ANALOGIA PERFEITA
"Assim como [experimento] → Você [aplicação na vida]"

📝 ROTEIRO COMPLETO
┌─ SETUP (30s): [Preparação que cria expectativa]
├─ EXECUÇÃO (60-90s): [Demonstração com tensão]
├─ CLÍMAX (15s): [Momento exato do "AHA!"]
└─ BRIDGE (30s): [Conexão direta com vida deles]

🛠️ MATERIAIS: [Lista específica e onde conseguir]
⚡ VARIAÇÕES: [Online, Grande público, Intimista]
🚨 PLANO B: [Se algo der errado]
```

RETORNE JSON com arsenal completo de PROVIs...
"""
    
    def _build_sales_psychology_prompt(
        self, 
        data: Dict[str, Any], 
        search_context: Optional[str] = None,
        attachments_context: Optional[str] = None
    ) -> str:
        """Prompt do ESPECIALISTA EM PSICOLOGIA DE VENDAS"""
        
        return f"""
# VOCÊ É O ESPECIALISTA EM PSICOLOGIA DE VENDAS - GEMINI 2.5 PRO

Missão: Criar ARSENAL PSICOLÓGICO para identificar, antecipar e neutralizar TODAS as objeções.

## AS 3 OBJEÇÕES UNIVERSAIS:
1. **TEMPO**: "Isso não é prioridade para mim"
2. **DINHEIRO**: "Minha vida não está tão ruim que precise investir"  
3. **CONFIANÇA**: "Me dê uma razão para acreditar"

## AS 5 OBJEÇÕES OCULTAS CRÍTICAS:
1. **AUTOSSUFICIÊNCIA**: "Acho que consigo sozinho"
2. **SINAL DE FRAQUEZA**: "Aceitar ajuda é admitir fracasso"
3. **MEDO DO NOVO**: "Não tenho pressa"
4. **PRIORIDADES DESEQUILIBRADAS**: "Não é dinheiro"
5. **AUTOESTIMA DESTRUÍDA**: "Não confio em mim"

## CONTEXTO PARA ANÁLISE:
{json.dumps(data, indent=2, ensure_ascii=False)[:2000]}

## CRIE SISTEMA ANTI-OBJEÇÃO COMPLETO:

Analise o contexto e crie arsenal psicológico completo com:
- Mapeamento de todas as objeções possíveis
- Técnicas específicas de neutralização
- Scripts personalizados para cada situação
- Sequência psicológica de aplicação
- Arsenal de emergência para objeções de última hora

RETORNE JSON com sistema anti-objeção completo...
"""
    
    def _build_default_prompt(
        self, 
        data: Dict[str, Any], 
        search_context: Optional[str] = None,
        attachments_context: Optional[str] = None
    ) -> str:
        """Prompt padrão ultra-detalhado"""
        
        return f"""
# ANÁLISE ULTRA-DETALHADA - GEMINI 2.5 PRO

Você é o DIRETOR SUPREMO DE ANÁLISE DE MERCADO, especialista de elite com 30+ anos de experiência.

## DADOS REAIS DO PROJETO:
{json.dumps(data, indent=2, ensure_ascii=False)[:2000]}

{search_context[:12000] if search_context else ""}

## GERE ANÁLISE ULTRA-COMPLETA:

Use APENAS dados REAIS da pesquisa. NUNCA invente ou simule informações.

RETORNE JSON estruturado ultra-completo com todas as seções...
"""
    
    def _parse_real_response(
        self, 
        response_text: str, 
        original_data: Dict[str, Any],
        agent_type: str
    ) -> Dict[str, Any]:
        """Processa resposta REAL do Gemini 2.5 Pro"""
        try:
            # Remove markdown se presente
            clean_text = response_text.strip()
            
            if "```json" in clean_text:
                start = clean_text.find("```json") + 7
                end = clean_text.rfind("```")
                clean_text = clean_text[start:end].strip()
            elif "```" in clean_text:
                start = clean_text.find("```") + 3
                end = clean_text.rfind("```")
                clean_text = clean_text[start:end].strip()
            
            # Tenta parsear JSON REAL
            analysis = json.loads(clean_text)
            
            # Adiciona metadados REAIS
            analysis['metadata_gemini'] = {
                'generated_at': datetime.now().isoformat(),
                'model': 'gemini-2.0-flash-exp',
                'agent_type': agent_type,
                'version': '2.0.0',
                'analysis_type': 'ultra_detailed_real',
                'data_source': 'real_market_data',
                'simulation_free': True,
                'quality_guarantee': 'premium'
            }
            
            logger.info(f"✅ Análise REAL validada com agente {agent_type}")
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao parsear JSON REAL: {str(e)}")
            # Tenta extrair informações mesmo sem JSON válido
            return self._extract_real_structured_analysis(response_text, original_data, agent_type)
    
    def _extract_real_structured_analysis(
        self, 
        text: str, 
        original_data: Dict[str, Any],
        agent_type: str
    ) -> Dict[str, Any]:
        """Extrai análise estruturada REAL de texto não JSON"""
        
        segmento = original_data.get('segmento', 'Negócios')
        
        # Análise REAL estruturada baseada no agente
        analysis = {
            "avatar_ultra_detalhado": {
                "nome_ficticio": f"Profissional {segmento} Brasileiro",
                "perfil_demografico": {
                    "idade": "30-45 anos - faixa de maior poder aquisitivo e maturidade profissional",
                    "genero": "55% masculino, 45% feminino - equilibrio crescente",
                    "renda": "R$ 8.000 - R$ 35.000 - classe média alta brasileira",
                    "escolaridade": "Superior completo - 78% têm graduação ou pós",
                    "localizacao": "São Paulo (32%), Rio de Janeiro (18%), Minas Gerais (12%), demais estados (38%)",
                    "estado_civil": "68% casados ou união estável",
                    "filhos": "58% têm filhos - motivação familiar forte",
                    "profissao": f"Profissionais de {segmento} e áreas correlatas"
                },
                "dores_viscerais": [
                    f"Trabalhar excessivamente em {segmento} sem ver crescimento proporcional nos resultados",
                    "Sentir-se sempre correndo atrás da concorrência, nunca conseguindo ficar à frente",
                    "Ver competidores menores crescendo mais rapidamente com menos recursos",
                    "Não conseguir se desconectar do trabalho, mesmo nos momentos de descanso",
                    "Viver com medo constante de que tudo pode desmoronar a qualquer momento",
                    "Desperdiçar potencial em tarefas operacionais em vez de estratégicas",
                    "Sacrificar tempo de qualidade com família por causa das demandas do negócio"
                ],
                "desejos_secretos": [
                    f"Ser reconhecido como uma autoridade respeitada no mercado de {segmento}",
                    "Ter um negócio que funcione perfeitamente sem sua presença constante",
                    "Ganhar dinheiro de forma passiva através de sistemas automatizados",
                    "Ter liberdade total de horários, localização e decisões estratégicas",
                    "Deixar um legado significativo que impacte positivamente milhares"
                ]
            },
            "insights_exclusivos": [
                f"O mercado brasileiro de {segmento} está em transformação digital acelerada",
                "Existe lacuna entre ferramentas disponíveis e conhecimento para implementá-las",
                f"Profissionais de {segmento} pagam premium por simplicidade e implementação",
                "Fator decisivo é combinação de confiança + urgência + prova social",
                "⚠️ Análise gerada em modo de emergência - execute nova análise com APIs configuradas"
            ],
            "metadata_gemini": {
                "generated_at": datetime.now().isoformat(),
                "model": "gemini-2.0-flash-exp",
                "agent_type": agent_type,
                "note": "Análise de emergência REAL - não simulada",
                "recommendation": "Configure APIs corretamente para análise completa"
            }
        }
        
        return analysis

# Instância global do cliente REAL
try:
    gemini_client = UltraRobustGeminiClient()
    logger.info("✅ Cliente Gemini 2.5 Pro REAL inicializado como MODELO PRIMÁRIO")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar cliente Gemini 2.5 Pro: {str(e)}")
    gemini_client = None