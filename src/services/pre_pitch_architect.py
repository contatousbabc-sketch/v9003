#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v2.0 - Pre-Pitch Architect
Arquiteto do Pré-Pitch Invisível - Orquestração Psicológica
"""

import time
import random
import logging
import json
from typing import Dict, List, Any, Optional
from services.ai_manager import ai_manager
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class PrePitchArchitect:
    """Arquiteto do Pré-Pitch Invisível - Orquestração Psicológica"""

    def __init__(self):
        """Inicializa o arquiteto de pré-pitch"""
        from .ai_manager import ai_manager
        self.ai_manager = ai_manager
        logger.info("Pre-Pitch Architect inicializado")

    def create_pre_pitch_strategy(self, segmento: str, produto: str, web_data: Dict = None, social_data: Dict = None) -> Dict[str, Any]:
        """Cria estratégia completa de pré-pitch invisível"""
        try:
            prompt = f"""
            Crie uma estratégia COMPLETA de PRÉ-PITCH INVISÍVEL para:

SEGMENTO: {segmento}
PRODUTO: {produto}
DADOS WEB: {str(web_data)[:300] if web_data else 'Não disponível'}
DADOS SOCIAIS: {str(social_data)[:300] if social_data else 'Não disponível'}

Desenvolva:

1. ESTRATÉGIA DE AQUECIMENTO (30 dias antes)
2. CONTEÚDO EDUCATIVO SEQUENCIAL
3. PROVA SOCIAL PROGRESSIVA
4. CRIAÇÃO DE NECESSIDADE SUTIL
5. POSICIONAMENTO COMO AUTORIDADE
6. ELIMINAÇÃO DE OBJEÇÕES ANTECIPADAS
7. CONSTRUÇÃO DE RELACIONAMENTO
8. TIMING IDEAL PARA OFERTA
9. PONTE EMOCIONAL
10. GATILHOS DE URGÊNCIA NATURAL

Para cada elemento:
- Cronograma específico
- Conteúdo detalhado
- Canal de distribuição
- Métrica de sucesso
- Próximo passo

Formato JSON estruturado.
"""

            response = self.ai_manager.generate_content(prompt, max_tokens=4000)

            import json
            try:
                prepitch_data = json.loads(response)
                return prepitch_data
            except json.JSONDecodeError:
                return self._create_fallback_prepitch(segmento, produto)

        except Exception as e:
            logger.error(f"❌ Erro ao criar estratégia pré-pitch: {e}")
            return self._create_fallback_prepitch(segmento, produto)

    def _create_fallback_prepitch(self, segmento: str, produto: str) -> Dict[str, Any]:
        """Cria estratégia pré-pitch de fallback"""
        return {
            "fase_1_aquecimento": {
                "duracao": "Dias 1-10",
                "objetivo": "Estabelecer presença e credibilidade",
                "acoes": [
                    f"Publicar conteúdo educativo sobre desafios do {segmento}",
                    "Compartilhar insights de mercado relevantes",
                    "Interagir genuinamente com prospects",
                    "Estabelecer autoridade no assunto"
                ],
                "conteudo": f"3 posts por semana sobre problemas específicos do {segmento}",
                "canais": ["LinkedIn", "E-mail", "Blog", "Redes sociais"],
                "metricas": ["Engajamento", "Alcance", "Comentários", "Compartilhamentos"]
            },
            "fase_2_educacao": {
                "duracao": "Dias 11-20",
                "objetivo": "Educar sobre soluções sem vender",
                "acoes": [
                    "Webinar educativo gratuito",
                    f"E-book sobre tendências do {segmento}",
                    "Série de vídeos tutoriais",
                    "Cases de sucesso (sem mencionar produto)"
                ],
                "conteudo": f"Série: 'Como {segmento} pode prosperar em 2025'",
                "canais": ["Webinar", "E-mail marketing", "YouTube", "Website"],
                "metricas": ["Downloads", "Participação", "Tempo de consumo", "Shares"]
            },
            "fase_3_necessidade": {
                "duracao": "Dias 21-25",
                "objetivo": "Criar consciência de necessidade específica",
                "acoes": [
                    f"Apresentar estatísticas alarmantes do {segmento}",
                    "Mostrar custo de inação",
                    "Comparar líderes vs atrasados no mercado",
                    "Deadline natural se aproximando"
                ],
                "conteudo": f"'O que separa os líderes dos seguidores no {segmento}'",
                "canais": ["E-mail", "LinkedIn", "Webinar de follow-up"],
                "metricas": ["Abertura e-mail", "Clicks", "Replies", "Agendamentos"]
            },
            "fase_4_autoridade": {
                "duracao": "Dias 26-28",
                "objetivo": "Posicionar como única solução viável",
                "acoes": [
                    "Revelar metodologia única",
                    f"Mostrar resultados específicos no {segmento}",
                    "Endorsements de líderes do setor",
                    "Demonstração técnica exclusiva"
                ],
                "conteudo": f"'A metodologia que está transformando o {segmento}'",
                "canais": ["Webinar exclusivo", "E-mail VIP", "Ligação direta"],
                "metricas": ["Participação qualificada", "Perguntas", "Solicitações demo"]
            },
            "fase_5_oferta": {
                "duracao": "Dias 29-30",
                "objetivo": "Apresentar oferta como oportunidade limitada",
                "acoes": [
                    "Anunciar disponibilidade limitada",
                    "Critérios de seleção rigorosos",
                    "Benefícios exclusivos para early adopters",
                    "Deadline real e justificado"
                ],
                "conteudo": f"'Oportunidade exclusiva para {segmento} - 48h apenas'",
                "canais": ["E-mail direto", "Ligação", "WhatsApp", "Zoom"],
                "metricas": ["Taxa de conversão", "Valor médio", "Closing rate"]
            },
            "elementos_psicologicos": {
                "reciprocidade": "Dar muito valor antes de pedir algo",
                "autoridade": "Estabelecer expertise reconhecida",
                "prova_social": "Mostrar outros fazendo igual",
                "escassez": "Limitação real de acesso",
                "compromisso": "Fazer prospect se comprometer publicamente",
                "simpatia": "Construir relacionamento genuíno"
            },
            "scripts_chave": {
                "abertura": f"Tenho ajudado líderes do {segmento} a [resultado específico]...",
                "transicao": "Baseado no que compartilhei, você vê isso acontecendo no seu negócio?",
                "qualificacao": f"Para {segmento} como o seu, isso significa...",
                "fechamento": "Faz sentido conversarmos sobre como aplicar isso especificamente no seu contexto?"
            },
            "cronograma_execucao": {
                "semana_1": "Aquecimento + estabelecimento autoridade",
                "semana_2": "Educação + construção relacionamento",
                "semana_3": "Criação necessidade + demonstração valor",
                "semana_4": "Posicionamento único + oferta limitada",
                "dia_30": "Fechamento com urgência genuína"
            }
        }

    def _load_psychological_phases(self) -> Dict[str, Dict[str, Any]]:
        """Carrega fases psicológicas da orquestração"""
        return {
            'quebra': {
                'objetivo': 'Destruir a ilusão confortável',
                'duracao': '3-5 minutos',
                'intensidade': 'Alta',
                'drivers_ideais': ['Diagnóstico Brutal', 'Ferida Exposta'],
                'resultado_esperado': 'Desconforto produtivo'
            },
            'exposicao': {
                'objetivo': 'Revelar a ferida real',
                'duracao': '4-6 minutos',
                'intensidade': 'Crescente',
                'drivers_ideais': ['Custo Invisível', 'Ambiente Vampiro'],
                'resultado_esperado': 'Consciência da dor'
            },
            'indignacao': {
                'objetivo': 'Criar revolta produtiva',
                'duracao': '3-4 minutos',
                'intensidade': 'Máxima',
                'drivers_ideais': ['Relógio Psicológico', 'Inveja Produtiva'],
                'resultado_esperado': 'Urgência de mudança'
            },
            'vislumbre': {
                'objetivo': 'Mostrar o possível',
                'duracao': '5-7 minutos',
                'intensidade': 'Esperançosa',
                'drivers_ideais': ['Ambição Expandida', 'Troféu Secreto'],
                'resultado_esperado': 'Desejo amplificado'
            },
            'tensao': {
                'objetivo': 'Amplificar o gap',
                'duracao': '2-3 minutos',
                'intensidade': 'Crescente',
                'drivers_ideais': ['Identidade Aprisionada', 'Oportunidade Oculta'],
                'resultado_esperado': 'Tensão máxima'
            },
            'necessidade': {
                'objetivo': 'Tornar a mudança inevitável',
                'duracao': '3-4 minutos',
                'intensidade': 'Definitiva',
                'drivers_ideais': ['Método vs Sorte', 'Mentor Salvador'],
                'resultado_esperado': 'Necessidade de solução'
            }
        }

    def _load_transition_templates(self) -> Dict[str, str]:
        """Carrega templates de transição"""
        return {
            'quebra_para_exposicao': "Eu sei que isso dói ouvir... Mas sabe o que dói mais?",
            'exposicao_para_indignacao': "E o pior de tudo é que isso não precisa ser assim...",
            'indignacao_para_vislumbre': "Mas calma, não vim aqui só para abrir feridas...",
            'vislumbre_para_tensao': "Agora você vê a diferença entre onde está e onde poderia estar...",
            'tensao_para_necessidade': "A pergunta não é SE você vai mudar, é COMO...",
            'necessidade_para_logica': "Eu sei que você está sentindo isso agora... Mas seu cérebro racional está gritando: 'Será que funciona mesmo?' Então deixa eu te mostrar os números..."
        }

    def generate_complete_pre_pitch_system(
        self,
        drivers_list: List[Dict[str, Any]],
        avatar_analysis: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera sistema completo de pré-pitch invisível"""

        # Validação crítica de entrada
        if not drivers_list:
            logger.error("❌ Lista de drivers vazia")
            raise ValueError("PRÉ-PITCH FALHOU: Nenhum driver mental fornecido")

        if not avatar_analysis:
            logger.error("❌ Análise do avatar ausente")
            raise ValueError("PRÉ-PITCH FALHOU: Análise do avatar ausente")

        if not context_data.get('segmento'):
            logger.error("❌ Segmento não informado")
            raise ValueError("PRÉ-PITCH FALHOU: Segmento obrigatório")

        try:
            logger.info(f"🎯 Gerando pré-pitch invisível com {len(drivers_list)} drivers")

            # Salva dados de entrada imediatamente
            salvar_etapa("pre_pitch_entrada", {
                "drivers_list": drivers_list,
                "avatar_analysis": avatar_analysis,
                "context_data": context_data
            }, categoria="pre_pitch")

            # Seleciona drivers ótimos para pré-pitch
            selected_drivers = self._select_optimal_drivers(drivers_list)

            if not selected_drivers:
                logger.error("❌ Nenhum driver adequado selecionado")
                # Usa drivers básicos em vez de falhar
                logger.warning("🔄 Usando drivers básicos para pré-pitch")
                selected_drivers = self._get_basic_drivers(context_data)

            # Salva drivers selecionados
            salvar_etapa("drivers_selecionados", selected_drivers, categoria="pre_pitch")

            # Cria orquestração emocional
            emotional_orchestration = self._create_emotional_orchestration(selected_drivers, avatar_analysis)

            if not emotional_orchestration or not emotional_orchestration.get('sequencia_psicologica'):
                logger.error("❌ Falha na orquestração emocional")
                # Usa orquestração básica em vez de falhar
                logger.warning("🔄 Usando orquestração emocional básica")
                emotional_orchestration = self._create_basic_orchestration(context_data)

            # Salva orquestração
            salvar_etapa("orquestracao_emocional", emotional_orchestration, categoria="pre_pitch")

            # Gera roteiro completo
            complete_script = self._generate_complete_script(emotional_orchestration, context_data)

            # Valida roteiro gerado
            if not self._validate_script(complete_script, context_data):
                logger.error("❌ Roteiro gerado é inválido")
                # Usa roteiro básico em vez de falhar
                logger.warning("🔄 Usando roteiro básico")
                complete_script = self._create_basic_script(context_data)

            # Salva roteiro
            salvar_etapa("roteiro_completo", complete_script, categoria="pre_pitch")

            # Cria variações por formato
            format_variations = self._create_format_variations(complete_script, context_data)

            # Gera métricas de sucesso
            success_metrics = self._create_success_metrics()

            result = {
                'orquestracao_emocional': emotional_orchestration,
                'roteiro_completo': complete_script,
                'variacoes_formato': format_variations,
                'metricas_sucesso': success_metrics,
                'drivers_utilizados': [driver['nome'] for driver in selected_drivers],
                'duracao_total': self._calculate_total_duration(emotional_orchestration),
                'intensidade_maxima': self._calculate_max_intensity(emotional_orchestration),
                'validation_status': 'VALID',
                'generation_timestamp': time.time()
            }

            # Salva resultado final imediatamente
            salvar_etapa("pre_pitch_final", result, categoria="pre_pitch")

            logger.info("✅ Pré-pitch invisível gerado com sucesso")
            return result

        except Exception as e:
            logger.error(f"❌ Erro ao gerar pré-pitch: {str(e)}")
            salvar_erro("pre_pitch_sistema", e, contexto={"segmento": context_data.get('segmento')})

            # Retorna sistema básico em vez de falhar
            logger.warning("🔄 Retornando pré-pitch básico")
            return self._generate_fallback_pre_pitch_system(context_data)

    def _get_basic_drivers(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retorna drivers básicos como fallback"""

        return [
            {'nome': 'Diagnóstico Brutal'},
            {'nome': 'Relógio Psicológico'},
            {'nome': 'Método vs Sorte'}
        ]

    def _create_basic_orchestration(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria orquestração básica como fallback"""

        return {
            'sequencia_psicologica': [
                {
                    'fase': 'quebra',
                    'objetivo': 'Quebrar padrão e despertar consciência',
                    'duracao': '3-5 minutos',
                    'intensidade': 'Alta',
                    'drivers_utilizados': ['Diagnóstico Brutal'],
                    'resultado_esperado': 'Desconforto produtivo'
                },
                {
                    'fase': 'vislumbre',
                    'objetivo': 'Mostrar possibilidades',
                    'duracao': '5-7 minutos',
                    'intensidade': 'Esperançosa',
                    'drivers_utilizados': ['Método vs Sorte'],
                    'resultado_esperado': 'Desejo de mudança'
                },
                {
                    'fase': 'necessidade',
                    'objetivo': 'Criar urgência',
                    'duracao': '3-4 minutos',
                    'intensidade': 'Definitiva',
                    'drivers_utilizados': ['Relógio Psicológico'],
                    'resultado_esperado': 'Urgência de ação'
                }
            ]
        }

    def _validate_script(self, script: Dict[str, Any], context_data: Dict[str, Any]) -> bool:
        """Valida se o roteiro gerado é válido"""
        if not script:
            return False

        required_sections = ['abertura', 'desenvolvimento', 'fechamento']

        for section in required_sections:
            if section not in script:
                logger.error(f"❌ Seção obrigatória ausente no roteiro: {section}")
                return False

            section_data = script[section]
            if not section_data.get('script') or len(section_data['script']) < 50:
                logger.error(f"❌ Script da seção '{section}' muito curto ou ausente")
                return False

            # Verifica se não é genérico
            script_text = section_data['script'].lower()
            if 'customizado para' in script_text and len(script_text) < 100:
                logger.error(f"❌ Script genérico na seção '{section}'")
                return False

        return True

    def _select_optimal_drivers(self, drivers_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Seleciona drivers ótimos para pré-pitch"""

        # Drivers essenciais para pré-pitch
        essential_drivers = [
            'Diagnóstico Brutal', 'Ambição Expandida', 'Relógio Psicológico',
            'Método vs Sorte', 'Decisão Binária', 'Custo Invisível'
        ]

        selected = []

        # Seleciona drivers essenciais disponíveis
        for driver in drivers_list:
            driver_name = driver.get('nome', '')
            if any(essential in driver_name for essential in essential_drivers):
                selected.append(driver)

        # Se não tem drivers suficientes, pega os primeiros disponíveis
        if len(selected) < 4:
            selected.extend(drivers_list[:6])

        # Remove duplicatas
        seen_names = set()
        unique_selected = []
        for driver in selected:
            name = driver.get('nome', '')
            if name not in seen_names:
                seen_names.add(name)
                unique_selected.append(driver)

        return unique_selected[:7]  # Máximo 7 drivers

    def _create_emotional_orchestration(
        self,
        selected_drivers: List[Dict[str, Any]],
        avatar_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cria orquestração emocional"""

        # Mapeia drivers para fases psicológicas
        phase_mapping = self._map_drivers_to_phases(selected_drivers)

        # Cria sequência psicológica
        psychological_sequence = []

        for phase_name, phase_data in self.psychological_phases.items():
            if phase_name in phase_mapping:
                phase_drivers = phase_mapping[phase_name]

                psychological_sequence.append({
                    'fase': phase_name,
                    'objetivo': phase_data['objetivo'],
                    'duracao': phase_data['duracao'],
                    'intensidade': phase_data['intensidade'],
                    'drivers_utilizados': [driver['nome'] for driver in phase_drivers],
                    'resultado_esperado': phase_data['resultado_esperado'],
                    'tecnicas': self._get_phase_techniques(phase_name, phase_drivers)
                })

        return {
            'sequencia_psicologica': psychological_sequence,
            'escalada_emocional': self._create_emotional_escalation(psychological_sequence),
            'pontos_criticos': self._identify_critical_points(psychological_sequence),
            'transicoes': self._create_phase_transitions(psychological_sequence)
        }

    def _map_drivers_to_phases(self, drivers: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Mapeia drivers para fases psicológicas"""

        mapping = {}

        for driver in drivers:
            driver_name = driver.get('nome', '')

            # Mapeia baseado no tipo de driver
            if any(word in driver_name.lower() for word in ['diagnóstico', 'brutal', 'ferida']):
                mapping.setdefault('quebra', []).append(driver)
            elif any(word in driver_name.lower() for word in ['custo', 'ambiente', 'vampiro']):
                mapping.setdefault('exposicao', []).append(driver)
            elif any(word in driver_name.lower() for word in ['relógio', 'urgência', 'inveja']):
                mapping.setdefault('indignacao', []).append(driver)
            elif any(word in driver_name.lower() for word in ['ambição', 'troféu', 'expandida']):
                mapping.setdefault('vislumbre', []).append(driver)
            elif any(word in driver_name.lower() for word in ['identidade', 'oportunidade']):
                mapping.setdefault('tensao', []).append(driver)
            elif any(word in driver_name.lower() for word in ['método', 'mentor', 'salvador']):
                mapping.setdefault('necessidade', []).append(driver)

        return mapping

    def _get_phase_techniques(self, phase_name: str, phase_drivers: List[Dict[str, Any]]) -> List[str]:
        """Obtém técnicas específicas para cada fase"""

        techniques = {
            'quebra': ['Confronto direto', 'Pergunta desconfortável', 'Estatística chocante'],
            'exposicao': ['Cálculo de perdas', 'Visualização da dor', 'Comparação cruel'],
            'indignacao': ['Urgência temporal', 'Comparação social', 'Consequências futuras'],
            'vislumbre': ['Visualização do sucesso', 'Casos de transformação', 'Possibilidades expandidas'],
            'tensao': ['Gap atual vs ideal', 'Identidade limitante', 'Oportunidade única'],
            'necessidade': ['Caminho claro', 'Mentor necessário', 'Método vs caos']
        }

        return techniques.get(phase_name, ['Técnica padrão'])

    def _generate_complete_script(
        self,
        emotional_orchestration: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera roteiro completo do pré-pitch"""

        try:
            segmento = context_data.get('segmento', 'negócios')

            prompt = f"""
Crie um roteiro completo de pré-pitch invisível para o segmento {segmento}.

ORQUESTRAÇÃO EMOCIONAL:
{json.dumps(emotional_orchestration, indent=2, ensure_ascii=False)[:2000]}

CONTEXTO:
- Segmento: {segmento}
- Produto: {context_data.get('produto', 'Não informado')}
- Público: {context_data.get('publico', 'Não informado')}

RETORNE APENAS JSON VÁLIDO:

```json
{{
  "abertura": {{
    "tempo": "3-5 minutos",
    "objetivo": "Quebrar padrão e despertar consciência",
    "script": "Roteiro detalhado da abertura",
    "frases_chave": ["Frase 1", "Frase 2"],
    "transicao": "Como conectar com próxima fase"
  }},
  "desenvolvimento": {{
    "tempo": "8-12 minutos",
    "objetivo": "Amplificar dor e desejo",
    "script": "Roteiro detalhado do desenvolvimento",
    "momentos_criticos": ["Momento 1", "Momento 2"],
    "escalada_emocional": "Como aumentar intensidade"
  }},
  "pre_climax": {{
    "tempo": "3-4 minutos",
    "objetivo": "Criar tensão máxima",
    "script": "Roteiro detalhado do pré-clímax",
    "ponto_virada": "Momento exato da virada",
    "preparacao_pitch": "Como preparar para oferta"
  }},
  "fechamento": {{
    "tempo": "2-3 minutos",
    "objetivo": "Transição perfeita para pitch",
    "script": "Roteiro detalhado do fechamento",
    "ponte_oferta": "Frase de transição para oferta",
    "estado_mental_ideal": "Como devem estar mentalmente"
  }}
}}
```
"""

            response = ai_manager.generate_analysis(prompt, max_tokens=2500)

            if response:
                clean_response = response.strip()
                if "```json" in clean_response:
                    start = clean_response.find("```json") + 7
                    end = clean_response.rfind("```")
                    clean_response = clean_response[start:end].strip()

                try:
                    script = json.loads(clean_response)
                    logger.info("✅ Roteiro completo gerado com IA")
                    return script
                except json.JSONDecodeError:
                    logger.warning("⚠️ IA retornou JSON inválido para roteiro")

            # Fallback para roteiro básico
            return self._create_basic_script(context_data)

        except Exception as e:
            logger.error(f"❌ Erro ao gerar roteiro: {str(e)}")
            return self._create_basic_script(context_data)

    def _create_basic_script(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria roteiro básico como fallback"""

        segmento = context_data.get('segmento', 'negócios')

        return {
            'abertura': {
                'tempo': '3-5 minutos',
                'objetivo': 'Quebrar padrão e despertar consciência',
                'script': f"Deixa eu te fazer uma pergunta sobre {segmento}... Há quanto tempo você está no mesmo nível?",
                'frases_chave': [
                    f"A verdade sobre {segmento} que ninguém te conta",
                    "Isso vai doer, mas precisa ser dito"
                ],
                'transicao': "E sabe por que isso acontece?"
            },
            'desenvolvimento': {
                'tempo': '8-12 minutos',
                'objetivo': 'Amplificar dor e desejo',
                'script': f"Cada dia que passa sem otimizar {segmento} é dinheiro saindo do seu bolso...",
                'momentos_criticos': [
                    "Cálculo da perda financeira",
                    "Comparação com concorrentes"
                ],
                'escalada_emocional': "Aumentar pressão gradualmente"
            },
            'pre_climax': {
                'tempo': '3-4 minutos',
                'objetivo': 'Criar tensão máxima',
                'script': f"Agora você tem duas escolhas em {segmento}...",
                'ponto_virada': "Momento da decisão binária",
                'preparacao_pitch': "Preparar para revelar solução"
            },
            'fechamento': {
                'tempo': '2-3 minutos',
                'objetivo': 'Transição perfeita para pitch',
                'script': "Eu vou te mostrar exatamente como sair dessa situação...",
                'ponte_oferta': "Mas antes, preciso saber se você está pronto...",
                'estado_mental_ideal': "Ansioso pela solução"
            }
        }

    def _create_format_variations(
        self,
        complete_script: Dict[str, Any],
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cria variações por formato"""

        return {
            'webinar': {
                'duracao_total': '15-20 minutos',
                'adaptacoes': [
                    'Usar chat para engajamento',
                    'Pausas para perguntas retóricas',
                    'Slides de apoio visual'
                ],
                'timing': 'Últimos 20 minutos antes da oferta'
            },
            'evento_presencial': {
                'duracao_total': '25-35 minutos',
                'adaptacoes': [
                    'Interação direta com audiência',
                    'Movimentação no palco',
                    'Provas visuais físicas'
                ],
                'timing': 'Distribuído ao longo do evento'
            },
            'cpl_3_aulas': {
                'duracao_total': '10-15 minutos',
                'adaptacoes': [
                    'Construção gradual ao longo das aulas',
                    'Callbacks entre aulas',
                    'Intensificação na aula 3'
                ],
                'timing': 'Final da aula 3'
            },
            'lives_aquecimento': {
                'duracao_total': '5-8 minutos por live',
                'adaptacoes': [
                    'Sementes em cada live',
                    'Preparação subliminar',
                    'Crescimento de intensidade'
                ],
                'timing': 'Distribuído nas lives'
            }
        }

    def _create_emotional_escalation(self, sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Cria escalada emocional"""

        return {
            'curva_intensidade': [
                {'fase': seq['fase'], 'intensidade': seq['intensidade']}
                for seq in sequence
            ],
            'pontos_pico': [
                seq['fase'] for seq in sequence
                if seq['intensidade'] in ['Máxima', 'Definitiva']
            ],
            'momentos_alivio': [
                seq['fase'] for seq in sequence
                if seq['intensidade'] == 'Esperançosa'
            ]
        }

    def _identify_critical_points(self, sequence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica pontos críticos"""

        critical_points = []

        for seq in sequence:
            if seq['intensidade'] in ['Máxima', 'Definitiva']:
                critical_points.append({
                    'fase': seq['fase'],
                    'momento': f"Durante {seq['objetivo'].lower()}",
                    'risco': 'Perda de audiência se muito intenso',
                    'oportunidade': 'Máximo impacto emocional',
                    'gestao': 'Monitorar reações e ajustar intensidade'
                })

        return critical_points

    def _create_phase_transitions(self, sequence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cria transições entre fases"""

        transitions = []

        for i in range(len(sequence) - 1):
            current_phase = sequence[i]['fase']
            next_phase = sequence[i + 1]['fase']

            transition_key = f"{current_phase}_para_{next_phase}"
            transition_text = self.transition_templates.get(
                transition_key,
                f"Transição de {current_phase} para {next_phase}"
            )

            transitions.append({
                'de': current_phase,
                'para': next_phase,
                'script': transition_text,
                'tempo': '15-30 segundos',
                'tecnica': 'Ponte emocional suave'
            })

        return transitions

    def _create_success_metrics(self) -> Dict[str, Any]:
        """Cria métricas de sucesso"""

        return {
            'indicadores_durante': [
                'Silêncio absoluto durante ativação',
                'Comentários emocionais no chat',
                'Perguntas sobre quando abre inscrições',
                'Concordância física (acenar cabeça)'
            ],
            'indicadores_apos': [
                'Ansiedade visível para a oferta',
                'Perguntas sobre preço/formato',
                'Comentários "já quero comprar"',
                'Objeções minimizadas'
            ],
            'sinais_resistencia': [
                'Questionamentos técnicos excessivos',
                'Mudança de assunto',
                'Objeções imediatas',
                'Linguagem corporal fechada'
            ],
            'metricas_conversao': {
                'engajamento': 'Tempo de atenção por fase',
                'emocional': 'Reações emocionais geradas',
                'comportamental': 'Ações tomadas após ativação',
                'conversao': 'Taxa de conversão pós-pré-pitch'
            }
        }

    def _calculate_total_duration(self, orchestration: Dict[str, Any]) -> str:
        """Calcula duração total"""

        sequence = orchestration.get('sequencia_psicologica', [])

        total_min = 0
        total_max = 0

        for phase in sequence:
            duration = phase.get('duracao', '3-4 minutos')

            # Extrai números da duração
            import re
            numbers = re.findall(r'\d+', duration)
            if len(numbers) >= 2:
                total_min += int(numbers[0])
                total_max += int(numbers[1])
            elif len(numbers) == 1:
                total_min += int(numbers[0])
                total_max += int(numbers[0])

        return f"{total_min}-{total_max} minutos"

    def _calculate_max_intensity(self, orchestration: Dict[str, Any]) -> str:
        """Calcula intensidade máxima"""

        sequence = orchestration.get('sequencia_psicologica', [])

        intensities = [phase.get('intensidade', 'Baixa') for phase in sequence]

        if 'Máxima' in intensities:
            return 'Máxima'
        elif 'Alta' in intensities:
            return 'Alta'
        elif 'Crescente' in intensities:
            return 'Crescente'
        else:
            return 'Média'

    def _generate_fallback_pre_pitch_system(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera sistema de pré-pitch básico como fallback"""

        segmento = context_data.get('segmento', 'negócios')

        return {
            'orquestracao_emocional': {
                'sequencia_psicologica': [
                    {
                        'fase': 'quebra',
                        'objetivo': 'Quebrar padrão e despertar consciência',
                        'duracao': '3-5 minutos',
                        'intensidade': 'Alta',
                        'drivers_utilizados': ['Diagnóstico Brutal'],
                        'resultado_esperado': 'Desconforto produtivo'
                    },
                    {
                        'fase': 'vislumbre',
                        'objetivo': 'Mostrar possibilidades',
                        'duracao': '5-7 minutos',
                        'intensidade': 'Esperançosa',
                        'drivers_utilizados': ['Método vs Sorte'],
                        'resultado_esperado': 'Desejo de mudança'
                    },
                    {
                        'fase': 'necessidade',
                        'objetivo': 'Criar necessidade de solução',
                        'duracao': '3-4 minutos',
                        'intensidade': 'Definitiva',
                        'drivers_utilizados': ['Relógio Psicológico'],
                        'resultado_esperado': 'Urgência de ação'
                    }
                ]
            },
            'roteiro_completo': {
                'abertura': {
                    'tempo': '3-5 minutos',
                    'objetivo': 'Quebrar padrão e despertar consciência',
                    'script': f"Deixa eu te fazer uma pergunta sobre {segmento}... Há quanto tempo você está no mesmo nível? A verdade é que a maioria dos profissionais trabalha muito mas não sai do lugar.",
                    'frases_chave': [
                        f"A verdade sobre {segmento} que ninguém te conta",
                        "Isso vai doer, mas precisa ser dito"
                    ],
                    'transicao': "E sabe por que isso acontece?"
                },
                'desenvolvimento': {
                    'tempo': '8-12 minutos',
                    'objetivo': 'Amplificar dor e mostrar possibilidades',
                    'script': f"Cada dia que passa sem otimizar {segmento} é dinheiro saindo do seu bolso. Enquanto você está 'pensando', seus concorrentes estão agindo. Mas existe um caminho diferente...",
                    'momentos_criticos': [
                        "Cálculo da perda financeira por inação",
                        "Comparação com concorrentes que agem"
                    ],
                    'escalada_emocional': "Aumentar pressão gradualmente, depois mostrar esperança"
                },
                'fechamento': {
                    'tempo': '2-3 minutos',
                    'objetivo': 'Transição para solução',
                    'script': f"Agora você tem duas escolhas em {segmento}: continuar como está ou seguir um método comprovado. Eu vou te mostrar exatamente como sair dessa situação...",
                    'ponte_oferta': "Mas antes, preciso saber se você está realmente pronto para mudar...",
                    'estado_mental_ideal': "Ansioso pela solução, pronto para agir"
                }
            },
            'validation_status': 'FALLBACK_VALID',
            'generation_timestamp': time.time(),
            'fallback_mode': True,
            'duracao_total': '13-20 minutos'
        }

# Instância global
pre_pitch_architect = PrePitchArchitect()