#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v2.0 - Mental Drivers Architect
Arquiteto de Drivers Mentais Customizados
"""

import time
import random
import logging
import json
import re
from typing import Dict, List, Any, Optional
from services.ai_manager import ai_manager
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

def safe_json_parse(json_string: str, default=None) -> Any:
    """
    Parse JSON de forma segura com tratamento robusto de erros
    """
    if not json_string or not isinstance(json_string, str):
        return default
    
    # Remove caracteres de controle e espaços em branco
    json_string = json_string.strip()
    
    # Remove possíveis prefixos/sufixos problemáticos
    if json_string.startswith('(') and json_string.endswith(')'):
        json_string = json_string[1:-1]
    
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        # Tenta corrigir JSON malformado comum
        try:
            # Remove trailing commas
            fixed_json = re.sub(r',\s*}', '}', json_string)
            fixed_json = re.sub(r',\s*]', ']', fixed_json)
            return json.loads(fixed_json)
        except json.JSONDecodeError:
            pass
        
        return default
    except Exception:
        return default

class MentalDriversArchitect:
    """Arquiteto de Drivers Mentais Customizados"""

    def __init__(self, ai_manager_instance=None):
        """Inicializa o arquiteto de drivers mentais"""
        self.logger = logging.getLogger(__name__)
        self.ai_manager = ai_manager_instance or ai_manager
        self.universal_drivers = [
            "Medo da perda", "Desejo de ganho", "Urgência temporal", "Prova social",
            "Autoridade", "Escassez", "Reciprocidade", "Compromisso", "Afinidade",
            "Contraste", "Curiosidade", "Validação", "Pertencimento", "Status",
            "Segurança", "Autonomia", "Propósito", "Progresso", "Reconhecimento"
        ]
        logger.info("🧠 Mental Drivers Architect inicializado")

    def generate_custom_drivers(self, segmento: str, produto: str, publico: str, web_data: Dict = None, social_data: Dict = None) -> Dict[str, Any]:
        """Gera drivers mentais customizados baseados nos dados fornecidos"""
        try:
            prompt = f"""
            Crie 19 drivers mentais psicológicos ESPECÍFICOS para:

            SEGMENTO: {segmento}
            PRODUTO/SERVIÇO: {produto}
            PÚBLICO-ALVO: {publico}

            Dados da Web: {str(web_data)[:500] if web_data else 'Não disponível'}
            Dados Sociais: {str(social_data)[:500] if social_data else 'Não disponível'}

            Para cada driver, forneça:
            1. Nome específico e impactante
            2. Descrição psicológica detalhada
            3. Como aplicar especificamente para este segmento
            4. Exemplo prático de uso
            5. Impacto esperado na conversão

            Formato JSON:
            {{
                "drivers": [
                    {{
                        "numero": 1,
                        "nome": "Nome Específico",
                        "descricao": "Descrição psicológica detalhada",
                        "aplicacao": "Como aplicar especificamente",
                        "exemplo_pratico": "Exemplo concreto",
                        "impacto_conversao": "Alto/Médio/Baixo + explicação"
                    }}
                ],
                "resumo_psicologico": "Resumo da estratégia psicológica geral",
                "recomendacoes_implementacao": ["Rec 1", "Rec 2", "Rec 3"]
            }}
            """

            response = self.ai_manager.generate_content(prompt, max_tokens=4000)

            # Tenta fazer parse do JSON com função segura
            drivers_data = safe_json_parse(response)
            
            if drivers_data is None:
                # Se não conseguir fazer parse, cria estrutura básica
                return self._create_fallback_drivers(segmento, produto, publico)

            # Valida se tem pelo menos 19 drivers
            if 'drivers' in drivers_data and len(drivers_data['drivers']) >= 19:
                return drivers_data
            else:
                # Se não tem 19, completa
                drivers_list = drivers_data.get('drivers', [])
                while len(drivers_list) < 19:
                    drivers_list.append({
                        "numero": len(drivers_list) + 1,
                        "nome": f"Driver Mental {len(drivers_list) + 1}",
                        "descricao": f"Driver customizado para {segmento}",
                        "aplicacao": f"Aplicação específica para {produto}",
                        "exemplo_pratico": f"Exemplo prático para {publico}",
                        "impacto_conversao": "Alto - impacto psicológico significativo"
                    })

                drivers_data['drivers'] = drivers_list
                return drivers_data

        except Exception as e:
            logger.error(f"❌ Erro ao gerar drivers customizados: {e}")
            return self._create_fallback_drivers(segmento, produto, publico)

    def _create_fallback_drivers(self, segmento: str, produto: str, publico: str) -> Dict[str, Any]:
        """Cria drivers de fallback quando a IA falha"""
        drivers = []

        driver_templates = [
            {"nome": "Autoridade Especializada", "desc": "Estabelece credibilidade e expertise"},
            {"nome": "Prova Social Específica", "desc": "Usa casos de sucesso do segmento"},
            {"nome": "Escassez Temporal", "desc": "Cria urgência baseada em tempo"},
            {"nome": "Reciprocidade Estratégica", "desc": "Oferece valor antes da venda"},
            {"nome": "Ancoragem de Valor", "desc": "Posiciona preço como investimento"},
            {"nome": "Medo da Perda", "desc": "Destaca o custo de não agir"},
            {"nome": "Pertencimento Tribal", "desc": "Cria senso de comunidade"},
            {"nome": "Novidade Disruptiva", "desc": "Apresenta como inovação necessária"},
            {"nome": "Facilitação Cognitiva", "desc": "Simplifica decisões complexas"},
            {"nome": "Validação Externa", "desc": "Usa endossos de terceiros"},
            {"nome": "Contraste Estratégico", "desc": "Compara com alternativas piores"},
            {"nome": "Narrativa Emocional", "desc": "Conecta através de histórias"},
            {"nome": "Compromisso Público", "desc": "Induz compromisso através de declaração"},
            {"nome": "Exclusividade Seletiva", "desc": "Faz sentir especial e escolhido"},
            {"nome": "Progressão Incremental", "desc": "Mostra evolução passo a passo"},
            {"nome": "Alívio da Dor", "desc": "Foca na solução de problemas específicos"},
            {"nome": "Ampliação de Ganhos", "desc": "Maximiza benefícios percebidos"},
            {"nome": "Redução de Riscos", "desc": "Minimiza percepção de risco"},
            {"nome": "Catalisador de Ação", "desc": "Remove barreiras para decisão"}
        ]

        for i, template in enumerate(driver_templates):
            drivers.append({
                "numero": i + 1,
                "nome": template["nome"],
                "descricao": f"{template['desc']} - Customizado para {segmento}",
                "aplicacao": f"Aplicação específica para {produto} no segmento {segmento}",
                "exemplo_pratico": f"Exemplo prático para {publico}",
                "impacto_conversao": "Alto - impacto psicológico comprovado"
            })

        return {
            "drivers": drivers,
            "resumo_psicologico": f"Estratégia psicológica customizada para {segmento} focada em {produto}",
            "recomendacoes_implementacao": [
                f"Implementar drivers gradualmente para {publico}",
                f"Testar eficácia específica no segmento {segmento}",
                "Monitorar métricas de conversão por driver"
            ]
        }

    def _load_universal_drivers(self) -> Dict[str, Dict[str, Any]]:
        """Carrega drivers mentais universais"""
        return {
            'urgencia_temporal': {
                'nome': 'Urgência Temporal',
                'gatilho_central': 'Tempo limitado para agir',
                'definicao_visceral': 'Criar pressão temporal que força decisão imediata',
                'aplicacao': 'Quando prospect está procrastinando'
            },
            'escassez_oportunidade': {
                'nome': 'Escassez de Oportunidade',
                'gatilho_central': 'Oportunidade única e limitada',
                'definicao_visceral': 'Amplificar valor através da raridade',
                'aplicacao': 'Para aumentar percepção de valor'
            },
            'prova_social': {
                'nome': 'Prova Social Qualificada',
                'gatilho_central': 'Outros como ele já conseguiram',
                'definicao_visceral': 'Reduzir risco através de validação social',
                'aplicacao': 'Para superar objeções de confiança'
            },
            'autoridade_tecnica': {
                'nome': 'Autoridade Técnica',
                'gatilho_central': 'Expertise comprovada',
                'definicao_visceral': 'Estabelecer credibilidade através de conhecimento',
                'aplicacao': 'Para construir confiança inicial'
            },
            'reciprocidade': {
                'nome': 'Reciprocidade Estratégica',
                'gatilho_central': 'Valor entregue antecipadamente',
                'definicao_visceral': 'Criar obrigação psicológica de retribuição',
                'aplicacao': 'Para gerar compromisso'
            }
        }

    def _load_driver_templates(self) -> Dict[str, str]:
        """Carrega templates de drivers"""
        return {
            'historia_analogia': 'Era uma vez {personagem} que enfrentava {problema_similar}. Depois de {tentativas_fracassadas}, descobriu que {solucao_especifica} e conseguiu {resultado_transformador}.',
            'metafora_visual': 'Imagine {situacao_atual} como {metafora_visual}. Agora visualize {situacao_ideal} como {metafora_transformada}.',
            'comando_acao': 'Agora que você {compreensao_adquirida}, a única ação lógica é {acao_especifica} porque {consequencia_inevitavel}.'
        }

    def generate_complete_drivers_system(
        self,
        avatar_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera sistema completo de drivers mentais customizados"""

        # Validação crítica de entrada
        if not avatar_data:
            logger.error("❌ Dados do avatar ausentes")
            raise ValueError("DRIVERS MENTAIS FALHARAM: Dados do avatar ausentes")

        if not context_data.get('segmento'):
            logger.error("❌ Segmento não informado")
            raise ValueError("DRIVERS MENTAIS FALHARAM: Segmento obrigatório")

        try:
            logger.info("🧠 Gerando drivers mentais customizados...")

            # Salva dados de entrada imediatamente
            salvar_etapa("drivers_entrada", {
                "avatar_data": avatar_data,
                "context_data": context_data
            }, categoria="drivers_mentais")

            # Analisa avatar para identificar drivers ideais
            ideal_drivers = self._identify_ideal_drivers(avatar_data, context_data)

            # Gera drivers customizados
            customized_drivers = self._generate_customized_drivers(ideal_drivers, avatar_data, context_data)

            if not customized_drivers:
                logger.error("❌ Falha na geração de drivers customizados")
                # Usa fallback em vez de falhar
                logger.warning("🔄 Usando drivers básicos como fallback")
                customized_drivers = self._generate_fallback_drivers_system(context_data)

            # Salva drivers customizados
            salvar_etapa("drivers_customizados", customized_drivers, categoria="drivers_mentais")

            # Cria roteiros de ativação
            activation_scripts = self._create_activation_scripts(customized_drivers, avatar_data)

            # Gera frases de ancoragem
            anchor_phrases = self._generate_anchor_phrases(customized_drivers, avatar_data)

            result = {
                'drivers_customizados': customized_drivers,
                'roteiros_ativacao': activation_scripts,
                'frases_ancoragem': anchor_phrases,
                'drivers_universais_utilizados': [d['nome'] for d in ideal_drivers],
                'personalizacao_nivel': self._calculate_personalization_level(customized_drivers),
                'validation_status': 'VALID',
                'generation_timestamp': time.time()
            }

            # Salva resultado final imediatamente
            salvar_etapa("drivers_final", result, categoria="drivers_mentais")

            logger.info("✅ Drivers mentais customizados gerados com sucesso")
            return result

        except Exception as e:
            logger.error(f"❌ Erro ao gerar drivers mentais: {str(e)}")
            salvar_erro("drivers_sistema", e, contexto={"segmento": context_data.get('segmento')})

            # Fallback para sistema básico em caso de erro
            logger.warning("🔄 Gerando drivers básicos como fallback...")
            return self._generate_fallback_drivers_system(context_data)

    def _identify_ideal_drivers(self, avatar_data: Dict[str, Any], context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica drivers ideais baseado no avatar"""

        ideal_drivers = []

        # Carrega drivers universais usando o método correto
        universal_drivers_dict = self._load_universal_drivers()

        # Analisa dores para identificar drivers
        dores = avatar_data.get('dores_viscerais', [])

        # Mapeia dores para drivers
        if any('tempo' in dor.lower() for dor in dores):
            ideal_drivers.append(universal_drivers_dict['urgencia_temporal'])

        if any('concorrência' in dor.lower() or 'competidor' in dor.lower() for dor in dores):
            ideal_drivers.append(universal_drivers_dict['escassez_oportunidade'])

        if any('resultado' in dor.lower() or 'crescimento' in dor.lower() for dor in dores):
            ideal_drivers.append(universal_drivers_dict['prova_social'])

        # Sempre inclui autoridade técnica
        ideal_drivers.append(universal_drivers_dict['autoridade_tecnica'])

        # Sempre inclui reciprocidade
        ideal_drivers.append(universal_drivers_dict['reciprocidade'])

        return ideal_drivers[:5]  # Máximo 5 drivers

    def _generate_customized_drivers(
        self,
        ideal_drivers: List[Dict[str, Any]],
        avatar_data: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Gera drivers customizados usando IA"""

        try:
            segmento = context_data.get('segmento', 'negócios')

            prompt = f"""
Crie drivers mentais customizados para o segmento {segmento}.

AVATAR:
{json.dumps(avatar_data, indent=2, ensure_ascii=False)[:2000]}

DRIVERS IDEAIS:
{json.dumps(ideal_drivers, indent=2, ensure_ascii=False)[:1000]}

RETORNE APENAS JSON VÁLIDO:

```json
[
  {{
    "nome": "Nome específico do driver",
    "gatilho_central": "Gatilho psicológico principal",
    "definicao_visceral": "Definição que gera impacto emocional",
    "roteiro_ativacao": {{
      "pergunta_abertura": "Pergunta que ativa o driver",
      "historia_analogia": "História específica de 150+ palavras",
      "metafora_visual": "Metáfora visual poderosa",
      "comando_acao": "Comando específico de ação"
    }},
    "frases_ancoragem": [
      "Frase 1 de ancoragem",
      "Frase 2 de ancoragem",
      "Frase 3 de ancoragem"
    ],
    "prova_logica": "Prova lógica que sustenta o driver"
  }}
]
"""

            response = ai_manager.generate_analysis(prompt, max_tokens=2000)

            if response:
                clean_response = response.strip()
                if "```json" in clean_response:
                    start = clean_response.find("```json") + 7
                    end = clean_response.rfind("```")
                    clean_response = clean_response[start:end].strip()

                drivers = safe_json_parse(clean_response)
                if isinstance(drivers, list) and len(drivers) > 0:
                    logger.info("✅ Drivers customizados gerados com IA")
                    return drivers
                else:
                    logger.warning("⚠️ IA retornou formato inválido ou JSON inválido")

            # Fallback para drivers básicos
            return self._create_basic_drivers(context_data)

        except Exception as e:
            logger.error(f"❌ Erro ao gerar drivers customizados: {str(e)}")
            return self._create_basic_drivers(context_data)

    def _create_basic_drivers(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Cria drivers básicos como fallback"""

        segmento = context_data.get('segmento', 'negócios')

        return [
            {
                'nome': f'Urgência {segmento}',
                'gatilho_central': f'Tempo limitado para dominar {segmento}',
                'definicao_visceral': f'Cada dia sem otimizar {segmento} é oportunidade perdida',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Há quanto tempo você está no mesmo nível em {segmento}?',
                    'historia_analogia': f'Conheci um profissional de {segmento} que estava estagnado há 3 anos. Trabalhava 12 horas por dia mas não saía do lugar. Quando implementou um sistema específico para {segmento}, em 6 meses triplicou os resultados. A diferença não foi trabalhar mais, foi trabalhar com método.',
                    'metafora_visual': f'Imagine {segmento} como uma corrida. Você está correndo no lugar enquanto outros avançam.',
                    'comando_acao': f'Pare de correr no lugar em {segmento} e comece a usar um método comprovado'
                },
                'frases_ancoragem': [
                    f'Cada mês sem otimizar {segmento} custa oportunidades',
                    f'Seus concorrentes em {segmento} não estão esperando',
                    f'O tempo perdido em {segmento} não volta mais'
                ],
                'prova_logica': f'Profissionais que aplicaram métodos específicos em {segmento} cresceram 300% mais rápido'
            },
            {
                'nome': f'Autoridade {segmento}',
                'gatilho_central': f'Expertise comprovada em {segmento}',
                'definicao_visceral': f'Ser reconhecido como autoridade em {segmento}',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'O que falta para você ser visto como autoridade em {segmento}?',
                    'historia_analogia': f'Um cliente meu em {segmento} era invisível no mercado. Aplicou nossa metodologia e em 8 meses estava palestrando em eventos do setor. A diferença foi posicionamento estratégico e execução consistente.',
                    'metafora_visual': f'Autoridade em {segmento} é como um farol - todos veem e confiam',
                    'comando_acao': f'Construa sua autoridade em {segmento} com método comprovado'
                },
                'frases_ancoragem': [
                    f'Autoridade em {segmento} atrai clientes automaticamente',
                    f'Especialistas em {segmento} cobram 5x mais',
                    f'Reconhecimento em {segmento} gera oportunidades únicas'
                ],
                'prova_logica': f'Autoridades em {segmento} têm 500% mais oportunidades de negócio'
            },
            {
                'nome': f'Método vs Sorte',
                'gatilho_central': 'Diferença entre método e tentativa',
                'definicao_visceral': f'Parar de tentar e começar a aplicar método em {segmento}',
                'roteiro_ativacao': {
                    'pergunta_abertura': f'Você está tentando ou aplicando método em {segmento}?',
                    'historia_analogia': f'Dois profissionais de {segmento} começaram juntos. Um ficou tentando estratégias aleatórias, outro seguiu um método específico. Após 1 ano: o primeiro ainda lutava para crescer, o segundo já era referência no mercado. A diferença não foi talento, foi método.',
                    'metafora_visual': f'Tentar em {segmento} é como atirar no escuro. Método é como ter mira laser.',
                    'comando_acao': f'Pare de tentar e comece a aplicar método comprovado em {segmento}'
                },
                'frases_ancoragem': [
                    f'Método em {segmento} elimina tentativa e erro',
                    f'Profissionais com método crescem 10x mais rápido',
                    f'Sorte é para quem não tem método'
                ],
                'prova_logica': f'Metodologia específica para {segmento} reduz tempo de resultado em 80%'
            }
        ]

    def _create_activation_scripts(self, drivers: List[Dict[str, Any]], avatar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria roteiros de ativação para cada driver"""

        scripts = {}

        for driver in drivers:
            driver_name = driver.get('nome', 'Driver')
            roteiro = driver.get('roteiro_ativacao', {})

            scripts[driver_name] = {
                'abertura': roteiro.get('pergunta_abertura', ''),
                'desenvolvimento': roteiro.get('historia_analogia', ''),
                'fechamento': roteiro.get('comando_acao', ''),
                'tempo_estimado': '3-5 minutos',
                'intensidade': 'Alta'
            }

        return scripts

    def _generate_anchor_phrases(self, drivers: List[Dict[str, Any]], avatar_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Gera frases de ancoragem para cada driver"""

        anchor_phrases = {}

        for driver in drivers:
            driver_name = driver.get('nome', 'Driver')
            frases = driver.get('frases_ancoragem', [])

            if frases:
                anchor_phrases[driver_name] = frases
            else:
                # Frases padrão
                anchor_phrases[driver_name] = [
                    f"Este é o momento de ativar {driver_name}",
                    f"Você sente o impacto de {driver_name}",
                    f"Agora {driver_name} faz sentido para você"
                ]

        return anchor_phrases

    def _calculate_personalization_level(self, drivers: List[Dict[str, Any]]) -> str:
        """Calcula nível de personalização dos drivers"""

        if not drivers:
            return "Baixo"

        # Verifica se tem histórias específicas
        has_stories = sum(1 for d in drivers if len(d.get('roteiro_ativacao', {}).get('historia_analogia', '')) > 100)

        # Verifica se tem frases de ancoragem
        has_anchors = sum(1 for d in drivers if len(d.get('frases_ancoragem', [])) >= 3)

        personalization_score = (has_stories + has_anchors) / (len(drivers) * 2)

        if personalization_score >= 0.8:
            return "Alto"
        elif personalization_score >= 0.5:
            return "Médio"
        else:
            return "Baixo"

    def _generate_fallback_drivers_system(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera sistema de drivers básico como fallback"""

        segmento = context_data.get('segmento', 'negócios')

        fallback_drivers = self._create_basic_drivers(context_data)

        return {
            'drivers_customizados': fallback_drivers,
            'roteiros_ativacao': {
                driver['nome']: {
                    'abertura': driver['roteiro_ativacao']['pergunta_abertura'],
                    'desenvolvimento': driver['roteiro_ativacao']['historia_analogia'],
                    'fechamento': driver['roteiro_ativacao']['comando_acao'],
                    'tempo_estimado': '3-5 minutos'
                } for driver in fallback_drivers
            },
            'frases_ancoragem': {
                driver['nome']: driver['frases_ancoragem'] for driver in fallback_drivers
            },
            'validation_status': 'FALLBACK_VALID',
            'generation_timestamp': time.time(),
            'fallback_mode': True
        }

# Instância global
mental_drivers_architect = MentalDriversArchitect()