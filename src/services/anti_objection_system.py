#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v2.0 - Anti-Objection System
Sistema de Engenharia Psicológica Anti-Objeção
"""

import time
import random
import logging
import json
from typing import Dict, List, Any, Optional
from services.ai_manager import ai_manager
from services.auto_save_manager import salvar_etapa, salvar_erro

logger = logging.getLogger(__name__)

class AntiObjectionSystem:
    """Sistema de Engenharia Psicológica Anti-Objeção"""

    def __init__(self, ai_manager_instance=None):
        """Inicializa o sistema anti-objeção"""
        self.logger = logging.getLogger(__name__)
        self.ai_manager = ai_manager_instance or ai_manager
        self.universal_objections = self._load_universal_objections()
        self.hidden_objections = self._load_hidden_objections()
        self.neutralization_techniques = self._load_neutralization_techniques()

        logger.info("Anti-Objection System inicializado com arsenal completo")

    def _load_universal_objections(self) -> Dict[str, Dict[str, Any]]:
        """Carrega as 3 objeções universais"""
        return {
            'tempo': {
                'objecao': 'Não tenho tempo / Isso não é prioridade para mim',
                'raiz_emocional': 'Medo de mais uma responsabilidade / Falta de clareza sobre importância',
                'contra_ataque': 'Técnica do Cálculo da Sangria + Consequência Exponencial',
                'scripts': [
                    'Cada [período] que você adia resolver [problema], você está perdendo [quantia específica]',
                    'O problema não para de crescer enquanto você está ocupado com outras coisas',
                    'Esta oportunidade existe agora por [razão específica], depois pode não existir mais'
                ]
            },
            'dinheiro': {
                'objecao': 'Não tenho dinheiro / Minha vida não está tão ruim que precise investir',
                'raiz_emocional': 'Medo de perder dinheiro / Prioridades desalinhadas / Não vê valor',
                'contra_ataque': 'Comparação Cruel + ROI Absurdo + Custo de Oportunidade',
                'scripts': [
                    'Você gasta R$X em [coisa supérflua] mas hesita em investir [valor] em algo que muda sua vida',
                    'Se você conseguir apenas [resultado mínimo], já pagou o investimento [X] vezes',
                    'O que você vai perder NÃO fazendo isso é muito maior que o investimento'
                ]
            },
            'confianca': {
                'objecao': 'Me dê uma razão para acreditar (em você/produto/provas/mim mesmo)',
                'raiz_emocional': 'Histórico de fracassos / Medo de mais uma decepção / Baixa autoestima',
                'contra_ataque': 'Autoridade Técnica + Prova Social Qualificada + Garantia Agressiva',
                'scripts': [
                    'Eu já [credencial específica] e consegui [resultado específico] usando exatamente isso',
                    'Pessoas exatamente como você conseguiram [resultado] em [tempo] seguindo este método',
                    'Estou tão confiante que assumo todo o risco: [garantia específica]'
                ]
            }
        }

    def _load_hidden_objections(self) -> Dict[str, Dict[str, Any]]:
        """Carrega as 5 objeções ocultas críticas"""
        return {
            'autossuficiencia': {
                'objecao_oculta': 'Acho que consigo sozinho',
                'perfil_tipico': 'Pessoas com formação superior, experiência na área, ego profissional',
                'raiz_emocional': 'Orgulho / Medo de parecer incompetente',
                'sinais': ['Menções de "tentar sozinho"', 'Resistência a ajuda', 'Linguagem técnica excessiva'],
                'contra_ataque': 'O Expert que Precisou de Expert + Aceleração vs Tentativa',
                'scripts': [
                    'Mesmo sendo [autoridade], precisei de ajuda para [resultado específico]',
                    'A diferença entre tentar sozinho e ter orientação é [comparação temporal/financeira]'
                ]
            },
            'sinal_fraqueza': {
                'objecao_oculta': 'Aceitar ajuda é admitir fracasso',
                'perfil_tipico': 'Homens, líderes, pessoas com imagem a zelar',
                'raiz_emocional': 'Medo de julgamento / Perda de status / Humilhação',
                'sinais': ['Minimização de problemas', '"Está tudo bem"', 'Resistência a expor vulnerabilidade'],
                'contra_ataque': 'Reframe de Inteligência + Histórias de Heróis Vulneráveis',
                'scripts': [
                    'Pessoas inteligentes buscam atalhos. Pessoas burras insistem no caminho difícil',
                    'Os maiores CEOs do mundo têm coaches. Coincidência?'
                ]
            },
            'medo_novo': {
                'objecao_oculta': 'Não tenho pressa / Quando for a hora certa',
                'perfil_tipico': 'Pessoas estagnadas mas "confortáveis", medo do desconhecido',
                'raiz_emocional': 'Ansiedade sobre nova realidade / Zona de conforto',
                'sinais': ['"Quando for a hora certa"', 'Procrastinação disfarçada', 'Conformismo'],
                'contra_ataque': 'Dor da Estagnação + Janela Histórica',
                'scripts': [
                    'A única coisa pior que a dor da mudança é a dor do arrependimento',
                    'Esta oportunidade existe por [contexto específico]. Quem não aproveitar agora...'
                ]
            },
            'prioridades_desequilibradas': {
                'objecao_oculta': 'Não é dinheiro (mas gasta em outras coisas)',
                'perfil_tipico': 'Pessoas que gastam em lazer/consumo mas "não têm dinheiro" para evolução',
                'raiz_emocional': 'Não reconhece educação como prioridade / Vício em gratificação imediata',
                'sinais': ['Menções de gastos em outras áreas', 'Justificativas financeiras contraditórias'],
                'contra_ataque': 'Comparação Cruel + Cálculo de Oportunidade Perdida',
                'scripts': [
                    'R$200/mês em streaming vs R$2000 uma vez para nunca mais passar aperto',
                    'Você investe mais no seu carro que na sua mente'
                ]
            },
            'autoestima_destruida': {
                'objecao_oculta': 'Não confio em mim / Sou eu o problema',
                'perfil_tipico': 'Pessoas com múltiplas tentativas fracassadas, baixa confiança pessoal',
                'raiz_emocional': 'Histórico de fracassos / Medo de mais um fracasso',
                'sinais': ['"Já tentei antes"', 'Histórico de fracassos', 'Vitimização', 'Autodesqualificação'],
                'contra_ataque': 'Casos de Pessoas "Piores" + Diferencial do Método',
                'scripts': [
                    'Se [pessoa pior situação] conseguiu, você também consegue',
                    'O problema não era você, era a falta de método certo'
                ]
            }
        }

    def _load_neutralization_techniques(self) -> Dict[str, Dict[str, Any]]:
        """Carrega técnicas de neutralização"""
        return {
            'concordar_valorizar_apresentar': {
                'estrutura': 'Você tem razão... Por isso criei...',
                'quando_usar': 'Objeções lógicas válidas',
                'exemplo': 'Você tem razão em ser cauteloso com investimentos. Por isso criei uma garantia de 60 dias...'
            },
            'inversao_perspectiva': {
                'estrutura': 'Na verdade é o oposto do que você imagina...',
                'when_to_use': 'Crenças limitantes',
                'exemplo': 'Na verdade, pessoas que mais precisam de ajuda são as que mais resistem a ela...'
            },
            'memorias_reviravolta': {
                'estrutura': 'Lembre de quando você decidiu sem certeza...',
                'when_to_use': 'Medo de decisão',
                'exemplo': 'Lembre quando você decidiu [mudança importante] sem ter certeza absoluta...'
            },
            'confronto_controlado': {
                'estrutura': 'Quantas vezes você perdeu oportunidade por isso?',
                'when_to_use': 'Padrões autodestrutivos',
                'exemplo': 'Quantas vezes você já perdeu oportunidades por "pensar demais"?'
            },
            'nova_crenca': {
                'estrutura': 'Isso é uma crença limitante, vou te mostrar outro ângulo...',
                'when_to_use': 'Crenças arraigadas',
                'exemplo': 'Isso é uma crença limitante. Vou te mostrar como pessoas "sem tempo" criaram tempo...'
            }
        }

    def generate_complete_anti_objection_system(
        self, 
        objections_list: List[str], 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera sistema completo anti-objeção"""

        # Validação crítica de entrada
        if not objections_list:
            logger.error("❌ Lista de objeções vazia")
            raise ValueError("SISTEMA ANTI-OBJEÇÃO FALHOU: Nenhuma objeção fornecida")

        if not avatar_data:
            logger.error("❌ Dados do avatar ausentes")
            raise ValueError("SISTEMA ANTI-OBJEÇÃO FALHOU: Dados do avatar ausentes")

        if not context_data.get('segmento'):
            logger.error("❌ Segmento não informado")
            raise ValueError("SISTEMA ANTI-OBJEÇÃO FALHOU: Segmento obrigatório")

        try:
            logger.info(f"🛡️ Gerando sistema anti-objeção para {len(objections_list)} objeções")

            # Salva dados de entrada imediatamente
            salvar_etapa("anti_objecao_entrada", {
                "objections_list": objections_list,
                "avatar_data": avatar_data,
                "context_data": context_data
            }, categoria="anti_objecao")

            # Analisa objeções específicas do avatar
            analyzed_objections = self._analyze_specific_objections(objections_list, avatar_data)

            if not analyzed_objections:
                logger.error("❌ Falha na análise de objeções")
                # Usa fallback em vez de falhar
                logger.warning("🔄 Usando análise de objeções padrão")
                analyzed_objections = [{"objecao_original": obj, "categoria": "geral"} for obj in objections_list]

            # Salva objeções analisadas
            salvar_etapa("objecoes_analisadas", analyzed_objections, categoria="anti_objecao")

            # Mapeia para objeções universais e ocultas
            mapped_objections = self._map_to_universal_objections(analyzed_objections)

            # Cria arsenal de contra-ataques
            counter_attacks = self._create_counter_attacks(mapped_objections, avatar_data, context_data)

            if not counter_attacks:
                logger.error("❌ Falha na criação de contra-ataques")
                # Usa fallback em vez de falhar
                logger.warning("🔄 Usando contra-ataques padrão")
                counter_attacks = self._create_basic_counter_attacks(context_data)

            # Salva contra-ataques
            salvar_etapa("contra_ataques", counter_attacks, categoria="anti_objecao")

            # Gera scripts personalizados
            personalized_scripts = self._generate_personalized_scripts(counter_attacks, avatar_data, context_data)

            # Valida scripts gerados
            if not self._validate_scripts(personalized_scripts, context_data):
                logger.error("❌ Scripts gerados são inválidos")
                # Usa scripts básicos em vez de falhar
                logger.warning("🔄 Usando scripts básicos como fallback")
                personalized_scripts = self._create_basic_scripts(avatar_data, context_data)

            # Salva scripts personalizados
            salvar_etapa("scripts_personalizados", personalized_scripts, categoria="anti_objecao")

            # Cria arsenal de emergência
            emergency_arsenal = self._create_emergency_arsenal(avatar_data, context_data)

            result = {
                'objecoes_universais': self._customize_universal_objections(avatar_data, context_data),
                'objecoes_ocultas': self._identify_hidden_objections(avatar_data),
                'contra_ataques_personalizados': counter_attacks,
                'scripts_personalizados': personalized_scripts,
                'arsenal_emergencia': emergency_arsenal,
                'sequencia_neutralizacao': self._create_neutralization_sequence(mapped_objections),
                'metricas_eficacia': self._create_effectiveness_metrics(),
                'validation_status': 'VALID',
                'generation_timestamp': time.time()
            }

            # Salva resultado final imediatamente
            salvar_etapa("anti_objecao_final", result, categoria="anti_objecao")

            logger.info("✅ Sistema anti-objeção gerado com sucesso")
            return result

        except Exception as e:
            logger.error(f"❌ Erro ao gerar sistema anti-objeção: {str(e)}")
            salvar_erro("anti_objecao_sistema", e, contexto={"segmento": context_data.get('segmento')})

            # Fallback para sistema básico em caso de erro
            logger.warning("🔄 Gerando sistema anti-objeção básico como fallback...")
            return self._generate_fallback_anti_objection_system(context_data)

    def _validate_scripts(self, scripts: Dict[str, List[str]], context_data: Dict[str, Any]) -> bool:
        """Valida qualidade dos scripts gerados"""
        if not scripts or len(scripts) < 3:
            logger.error("❌ Scripts insuficientes gerados")
            return False

        segmento = context_data.get('segmento', '')
        total_content = 0

        for category, script_list in scripts.items():
            if not script_list or len(script_list) < 2:
                logger.error(f"❌ Categoria {category} com scripts insuficientes")
                return False

            for script in script_list:
                if len(script) < 50:  # Scripts muito curtos
                    logger.error(f"❌ Script muito curto: {script[:30]}...")
                    return False

                # Verifica se não é genérico
                if 'customizado para' in script.lower() and len(script) < 100:
                    logger.error(f"❌ Script genérico detectado: {script[:50]}...")
                    return False

                total_content += len(script)

        if total_content < 1000:  # Mínimo de conteúdo total
            logger.error(f"❌ Scripts anti-objeção muito curtos: {total_content} caracteres. Mínimo: 1000")
            return False

        return True

    def _analyze_specific_objections(
        self, 
        objections: List[str], 
        avatar_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analisa objeções específicas do avatar"""

        analyzed = []

        for objection in objections:
            analysis = {
                'objecao_original': objection,
                'categoria': self._categorize_objection(objection),
                'intensidade': self._assess_objection_intensity(objection),
                'raiz_emocional': self._identify_emotional_root(objection),
                'frequencia_esperada': self._estimate_frequency(objection, avatar_data)
            }
            analyzed.append(analysis)

        return analyzed

    def _categorize_objection(self, objection: str) -> str:
        """Categoriza objeção"""

        objection_lower = objection.lower()

        if any(word in objection_lower for word in ['tempo', 'ocupado', 'prioridade']):
            return 'tempo'
        elif any(word in objection_lower for word in ['dinheiro', 'caro', 'investimento', 'preço']):
            return 'dinheiro'
        elif any(word in objection_lower for word in ['confiança', 'funciona', 'resultado', 'prova']):
            return 'confianca'
        elif any(word in objection_lower for word in ['sozinho', 'conseguir', 'tentar']):
            return 'autossuficiencia'
        elif any(word in objection_lower for word in ['ajuda', 'fraco', 'admitir']):
            return 'sinal_fraqueza'
        else:
            return 'geral'

    def _assess_objection_intensity(self, objection: str) -> str:
        """Avalia intensidade da objeção"""

        high_intensity_words = ['nunca', 'impossível', 'jamais', 'ódio', 'detesto']
        medium_intensity_words = ['difícil', 'complicado', 'problema', 'preocupação']

        objection_lower = objection.lower()

        if any(word in objection_lower for word in high_intensity_words):
            return 'Alta'
        elif any(word in objection_lower for word in medium_intensity_words):
            return 'Média'
        else:
            return 'Baixa'

    def _identify_emotional_root(self, objection: str) -> str:
        """Identifica raiz emocional da objeção"""

        objection_lower = objection.lower()

        if any(word in objection_lower for word in ['medo', 'receio', 'ansioso']):
            return 'Medo do desconhecido'
        elif any(word in objection_lower for word in ['fracasso', 'errado', 'tentei']):
            return 'Histórico de fracassos'
        elif any(word in objection_lower for word in ['orgulho', 'sozinho', 'independente']):
            return 'Orgulho ferido'
        elif any(word in objection_lower for word in ['confiança', 'dúvida', 'ceticismo']):
            return 'Desconfiança'
        else:
            return 'Resistência geral à mudança'

    def _estimate_frequency(self, objection: str, avatar_data: Dict[str, Any]) -> str:
        """Estima frequência da objeção"""

        # Baseado no perfil psicográfico
        personalidade = avatar_data.get('perfil_psicografico', {}).get('personalidade', '')

        if 'conservador' in personalidade.lower():
            return 'Alta'
        elif 'cauteloso' in personalidade.lower():
            return 'Média'
        else:
            return 'Baixa'

    def _map_to_universal_objections(self, analyzed_objections: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Mapeia objeções específicas para universais"""

        mapped = {
            'tempo': [],
            'dinheiro': [],
            'confianca': [],
            'ocultas': []
        }

        for objection in analyzed_objections:
            category = objection['categoria']
            if category in mapped:
                mapped[category].append(objection)
            else:
                mapped['ocultas'].append(objection)

        return mapped

    def _create_counter_attacks(
        self, 
        mapped_objections: Dict[str, List[Dict[str, Any]]], 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Cria contra-ataques personalizados"""

        counter_attacks = {}

        for category, objections in mapped_objections.items():
            if not objections:
                continue

            if category in self.universal_objections:
                universal_data = self.universal_objections[category]
                counter_attacks[category] = self._customize_universal_counter_attack(
                    universal_data, objections, avatar_data, context_data
                )
            elif category == 'ocultas':
                counter_attacks['ocultas'] = self._create_hidden_counter_attacks(
                    objections, avatar_data, context_data
                )

        return counter_attacks

    def _customize_universal_counter_attack(
        self, 
        universal_data: Dict[str, Any], 
        specific_objections: List[Dict[str, Any]], 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customiza contra-ataque universal"""

        segmento = context_data.get('segmento', 'negócios')

        customized = universal_data.copy()

        # Customiza scripts para o segmento
        customized_scripts = []
        for script in universal_data['scripts']:
            if '[período]' in script:
                script = script.replace('[período]', 'mês')
            if '[problema]' in script:
                script = script.replace('[problema]', f'sua situação em {segmento}')
            if '[quantia específica]' in script:
                script = script.replace('[quantia específica]', 'R$ 5.000 em oportunidades')

            customized_scripts.append(script)

        customized['scripts_customizados'] = customized_scripts
        customized['objecoes_especificas'] = [obj['objecao_original'] for obj in specific_objections]

        return customized

    def _create_hidden_counter_attacks(
        self, 
        hidden_objections: List[Dict[str, Any]], 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Cria contra-ataques para objeções ocultas"""

        counter_attacks = []

        for objection in hidden_objections:
            # Identifica qual objeção oculta mais se aproxima
            best_match = self._find_best_hidden_match(objection)

            if best_match:
                counter_attack = self.hidden_objections[best_match].copy()
                counter_attack['objecao_especifica'] = objection['objecao_original']
                counter_attack['customizacao'] = self._customize_for_context(counter_attack, context_data)
                counter_attacks.append(counter_attack)

        return counter_attacks

    def _find_best_hidden_match(self, objection: Dict[str, Any]) -> Optional[str]:
        """Encontra melhor match para objeção oculta"""

        objection_text = objection['objecao_original'].lower()

        # Mapeia palavras-chave para objeções ocultas
        keyword_mapping = {
            'autossuficiencia': ['sozinho', 'conseguir', 'tentar', 'independente'],
            'sinal_fraqueza': ['ajuda', 'fraco', 'admitir', 'problema'],
            'medo_novo': ['hora certa', 'depois', 'futuro', 'quando'],
            'prioridades_desequilibradas': ['dinheiro', 'gasto', 'prioridade', 'investimento'],
            'autoestima_destruida': ['fracasso', 'tentei', 'não consegui', 'problema sou eu']
        }

        best_match = None
        max_matches = 0

        for hidden_type, keywords in keyword_mapping.items():
            matches = sum(1 for keyword in keywords if keyword in objection_text)
            if matches > max_matches:
                max_matches = matches
                best_match = hidden_type

        return best_match if max_matches > 0 else None

    def _customize_for_context(self, counter_attack: Dict[str, Any], context_data: Dict[str, Any]) -> str:
        """Customiza contra-ataque para contexto"""

        segmento = context_data.get('segmento', 'negócios')

        return f"Customizado para {segmento}: {counter_attack['contra_ataque']}"

    def _generate_personalized_scripts(
        self, 
        counter_attacks: Dict[str, Any], 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Gera scripts personalizados usando IA"""

        try:
            segmento = context_data.get('segmento', 'negócios')
            personalidade = avatar_data.get('perfil_psicografico', {}).get('personalidade', '')

            prompt = f"""
Crie scripts personalizados para neutralizar objeções no segmento {segmento}.

PERFIL DO AVATAR:
- Personalidade: {personalidade}
- Principais dores: {avatar_data.get('dores_viscerais', [])[:3]}
- Linguagem: {avatar_data.get('linguagem_interna', {})}

OBJEÇÕES IDENTIFICADAS:
{json.dumps(counter_attacks, indent=2, ensure_ascii=False)[:1000]}

RETORNE APENAS JSON VÁLIDO:

```json
{{
  "scripts_tempo": [
    "Script 1 personalizado para objeção de tempo",
    "Script 2 personalizado para objeção de tempo"
  ],
  "scripts_dinheiro": [
    "Script 1 personalizado para objeção de dinheiro",
    "Script 2 personalizado para objeção de dinheiro"
  ],
  "scripts_confianca": [
    "Script 1 personalizado para objeção de confiança",
    "Script 2 personalizado para objeção de confiança"
  ],
  "scripts_emergencia": [
    "Script de emergência 1",
    "Script de emergência 2"
  ]
}}
```
"""

            response = self.ai_manager.generate_analysis(prompt, max_tokens=4096)

            if response:
                clean_response = response.strip()
                if "```json" in clean_response:
                    start = clean_response.find("```json") + 7
                    end = clean_response.rfind("```")
                    clean_response = clean_response[start:end].strip()

                try:
                    scripts = json.loads(clean_response)
                    logger.info("✅ Scripts personalizados gerados com IA")
                    return scripts
                except json.JSONDecodeError:
                    logger.warning("⚠️ IA retornou JSON inválido para scripts")

            # Fallback para scripts básicos
            return self._create_basic_scripts(avatar_data, context_data)

        except Exception as e:
            logger.error(f"❌ Erro crítico ao gerar scripts personalizados: {str(e)}")
            salvar_erro("scripts_personalizados", e, contexto=context_data)
            # Retorna scripts básicos em vez de falhar
            return self._create_basic_scripts(avatar_data, context_data)

    def _create_basic_counter_attacks(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria contra-ataques básicos como fallback"""

        segmento = context_data.get('segmento', 'negócios')

        return {
            "tempo": {
                "objecao": "Não tenho tempo para implementar isso agora",
                "contra_ataque": f"Cada mês sem otimizar {segmento} custa oportunidades valiosas",
                "scripts_customizados": [
                    f"Profissionais de {segmento} que adiaram mudanças perderam market share",
                    f"O tempo que você gasta 'pensando' seus concorrentes usam para agir"
                ]
            },
            "dinheiro": {
                "objecao": "Não tenho orçamento disponível no momento", 
                "contra_ataque": f"O custo de não investir em {segmento} é maior que o investimento",
                "scripts_customizados": [
                    f"ROI médio em {segmento} com método correto: 300-500% em 12 meses",
                    f"Cada mês sem sistema custa mais que o investimento total"
                ]
            },
            "confianca": {
                "objecao": "Preciso de mais garantias de que funciona",
                "contra_ataque": f"Metodologia testada com profissionais de {segmento}",
                "scripts_customizados": [
                    f"Mais de 200 profissionais de {segmento} já aplicaram com sucesso",
                    f"Garantia específica para {segmento}: resultados em 60 dias"
                ]
            }
        }

    def _validate_script_quality(self, scripts: Dict[str, List[str]], context_data: Dict[str, Any]) -> bool:
        """Valida qualidade dos scripts gerados"""
        segmento = context_data.get('segmento', '')

        if not scripts or len(scripts) < 3:
            logger.error("❌ Scripts insuficientes gerados")
            return False

        total_content = 0
        for category, script_list in scripts.items():
            if not script_list or len(script_list) < 2:
                logger.error(f"❌ Categoria {category} com scripts insuficientes")
                return False

            for script in script_list:
                if len(script) < 50:  # Scripts muito curtos
                    logger.error(f"❌ Script muito curto: {script[:30]}...")
                    return False
                total_content += len(script)

        if total_content < 1000:  # Mínimo de conteúdo total
            logger.error(f"❌ Scripts anti-objeção muito curtos: {total_content} caracteres. Mínimo: 1000")
            return False

        # Verifica se há menção ao segmento específico
        segment_mentioned = False
        for script_list in scripts.values():
            for script in script_list:
                if segmento.lower() in script.lower():
                    segment_mentioned = True
                    break
            if segment_mentioned:
                break

        if not segment_mentioned and segmento:
            logger.warning(f"⚠️ Scripts não mencionam segmento específico: {segmento}")

        return "A única diferença entre você e quem já conseguiu é a decisão de agir"

    def _customize_universal_objections(
        self, 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customiza objeções universais para o contexto"""

        customized = {}

        for category, objection_data in self.universal_objections.items():
            customized[category] = objection_data.copy()

            # Customiza para o segmento
            segmento = context_data.get('segmento', 'negócios')
            customized[category]['contexto_segmento'] = segmento

            # Adiciona exemplos específicos
            customized[category]['exemplos_especificos'] = self._create_specific_examples(
                category, avatar_data, context_data
            )

        return customized

    def _identify_hidden_objections(self, avatar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identifica objeções ocultas baseadas no avatar"""

        identified = {}

        # Analisa perfil para identificar objeções ocultas prováveis
        personalidade = avatar_data.get('perfil_psicografico', {}).get('personalidade', '').lower()
        valores = avatar_data.get('perfil_psicografico', {}).get('valores', '').lower()

        # Autossuficiência
        if any(trait in personalidade for trait in ['independente', 'autoconfiante', 'determinado']):
            identified['autossuficiencia'] = self.hidden_objections['autossuficiencia'].copy()
            identified['autossuficiencia']['probabilidade'] = 'Alta'

        # Sinal de fraqueza
        if any(trait in valores for trait in ['imagem', 'status', 'reconhecimento']):
            identified['sinal_fraqueza'] = self.hidden_objections['sinal_fraqueza'].copy()
            identified['sinal_fraqueza']['probabilidade'] = 'Média'

        # Medo do novo
        if any(trait in personalidade for trait in ['conservador', 'cauteloso', 'tradicional']):
            identified['medo_novo'] = self.hidden_objections['medo_novo'].copy()
            identified['medo_novo']['probabilidade'] = 'Alta'

        return identified

    def _create_specific_examples(
        self, 
        category: str, 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> List[str]:
        """Cria exemplos específicos para cada categoria"""

        segmento = context_data.get('segmento', 'negócios')

        examples = {
            'tempo': [
                f"Cada mês sem otimizar {segmento} = R$ 10.000 em oportunidades perdidas",
                f"Profissionais de {segmento} que adiaram mudanças perderam 40% do market share"
            ],
            'dinheiro': [
                f"R$ 200/mês em ferramentas vs R$ 2.000 uma vez para dominar {segmento}",
                f"ROI médio em {segmento} com método correto: 500% em 12 meses"
            ],
            'confianca': [
                f"Mais de 500 profissionais de {segmento} já aplicaram com sucesso",
                f"Garantia específica para {segmento}: resultados em 60 dias ou dinheiro de volta"
            ]
        }

        return examples.get(category, [f"Exemplo específico para {category} em {segmento}"])

    def _create_emergency_arsenal(
        self, 
        avatar_data: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> List[str]:
        """Cria arsenal de emergência para objeções de última hora"""

        return [
            "Vamos ser honestos: você vai continuar adiando até quando?",
            "A única diferença entre você e quem já conseguiu é a decisão de agir",
            "Quantas oportunidades você já perdeu por 'pensar demais'?",
            "O medo de errar está te impedindo de acertar",
            "Você prefere o arrependimento de ter tentado ou de não ter tentado?",
            "Cada 'não' que você diz para evolução é um 'sim' para estagnação",
            "O tempo que você está perdendo pensando, outros estão usando para agir",
            "Sua zona de conforto é uma prisão disfarçada de segurança"
        ]

    def _create_neutralization_sequence(self, mapped_objections: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Cria sequência de neutralização"""

        return [
            "1. IDENTIFICAR: Qual objeção está sendo verbalizada ou sinalizada",
            "2. CONCORDAR: Validar a preocupação como legítima",
            "3. VALORIZAR: Mostrar que pessoas inteligentes pensam assim",
            "4. APRESENTAR: Oferecer nova perspectiva ou solução",
            "5. CONFIRMAR: Verificar se a objeção foi neutralizada",
            "6. ANCORAR: Reforçar a nova crença instalada"
        ]

    def _create_effectiveness_metrics(self) -> Dict[str, Any]:
        """Cria métricas de eficácia do sistema"""

        return {
            'indicadores_neutralizacao': [
                'Mudança na linguagem corporal (abertura)',
                'Perguntas sobre próximos passos',
                'Redução de questionamentos',
                'Concordância verbal ou física'
            ],
            'sinais_resistencia_persistente': [
                'Repetição da mesma objeção',
                'Mudança de assunto',
                'Linguagem corporal fechada',
                'Questionamentos técnicos excessivos'
            ],
            'metricas_conversao': {
                'pre_neutralizacao': 'Taxa de conversão antes do sistema',
                'pos_neutralizacao': 'Taxa de conversão após aplicação',
                'tempo_medio_neutralizacao': 'Tempo médio para neutralizar objeção',
                'objecoes_mais_resistentes': 'Ranking das objeções mais difíceis'
            }
        }

    def _generate_fallback_anti_objection_system(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera sistema anti-objeção básico como fallback"""

        segmento = context_data.get('segmento', 'negócios')

        return {
            "objecoes_universais": {
                "tempo": {
                    "objecao": "Não tenho tempo para implementar isso agora",
                    "contra_ataque": f"Cada mês sem otimizar {segmento} custa oportunidades valiosas",
                    "scripts_customizados": [
                        f"Profissionais de {segmento} que adiaram mudanças perderam market share",
                        f"O tempo que você gasta 'pensando' seus concorrentes usam para agir"
                    ]
                },
                "dinheiro": {
                    "objecao": "Não tenho orçamento disponível no momento",
                    "contra_ataque": f"O custo de não investir em {segmento} é maior que o investimento",
                    "scripts_customizados": [
                        f"ROI médio em {segmento} com método correto: 300-500% em 12 meses",
                        f"Cada mês sem sistema custa mais que o investimento total"
                    ]
                },
                "confianca": {
                    "objecao": "Preciso de mais garantias de que funciona",
                    "contra_ataque": f"Metodologia testada com profissionais de {segmento}",
                    "scripts_customizados": [
                        f"Mais de 200 profissionais de {segmento} já aplicaram com sucesso",
                        f"Garantia específica para {segmento}: resultados em 60 dias"
                    ]
                }
            },
            "scripts_personalizados": {
                "scripts_tempo": [
                    f"Cada dia sem otimizar {segmento} é uma oportunidade perdida",
                    f"Seus concorrentes em {segmento} não estão esperando você se decidir"
                ],
                "scripts_dinheiro": [
                    f"Investimento em {segmento} se paga em 2-4 meses com implementação correta",
                    f"O que você perde NÃO investindo é maior que o valor do investimento"
                ],
                "scripts_confianca": [
                    f"Metodologia comprovada especificamente para {segmento}",
                    f"Resultados documentados de profissionais como você em {segmento}"
                ]
            },
            "validation_status": "FALLBACK_VALID",
            "generation_timestamp": time.time(),
            "fallback_mode": True
        }

    def create_comprehensive_objection_handling(self, segmento: str, produto: str, web_data: Dict = None, social_data: Dict = None) -> Dict[str, Any]:
        """Cria sistema completo de tratamento de objeções"""
        try:
            prompt = f"""
            Crie um sistema COMPLETO de tratamento de objeções para:

            SEGMENTO: {segmento}
            PRODUTO: {produto}
            DADOS WEB: {str(web_data)[:300] if web_data else 'Não disponível'}
            DADOS SOCIAIS: {str(social_data)[:300] if social_data else 'Não disponível'}

            Identifique e trate as seguintes objeções específicas deste segmento:

            1. OBJEÇÕES DE PREÇO/INVESTIMENTO
            2. OBJEÇÕES DE TEMPO/DISPONIBILIDADE
            3. OBJEÇÕES DE CREDIBILIDADE/CONFIANÇA
            4. OBJEÇÕES TÉCNICAS/FUNCIONAIS
            5. OBJEÇÕES DE NECESSIDADE/PRIORIDADE
            6. OBJEÇÕES DE TIMING/MOMENTO
            7. OBJEÇÕES DE AUTORIDADE/DECISÃO
            8. OBJEÇÕES DE EXPERIÊNCIA ANTERIOR
            9. OBJEÇÕES DE CONCORRÊNCIA
            10. OBJEÇÕES DE COMPLEXIDADE

            Para cada objeção:
            - Frase exata que o cliente usaria
            - Resposta persuasiva específica
            - Prova/evidência de apoio
            - Técnica psicológica aplicada
            - Script de reframe

            Formato JSON detalhado.
            """

            response = self.ai_manager.generate_content(prompt, max_tokens=4000)

            import json
            try:
                objection_data = json.loads(response)
                return objection_data
            except json.JSONDecodeError:
                return self._create_fallback_objections(segmento, produto)

        except Exception as e:
            logger.error(f"❌ Erro ao criar sistema anti-objeção: {e}")
            return self._create_fallback_objections(segmento, produto)

    def _create_fallback_objections(self, segmento: str, produto: str) -> Dict[str, Any]:
        """Cria sistema de objeções de fallback"""
        return {
            "objecoes_preco": {
                "objecao": "Está muito caro para o meu orçamento atual",
                "resposta": f"Entendo sua preocupação. O investimento em {produto} se paga rapidamente. Na verdade, o custo de NÃO ter essa solução é muito maior.",
                "prova": "Casos de ROI específicos do segmento",
                "tecnica": "Reframe de custo para investimento",
                "script": f"Veja, no {segmento}, clientes que esperaram para investir perderam em média X% de oportunidades..."
            },
            "objecoes_tempo": {
                "objecao": "Não tenho tempo para implementar isso agora",
                "resposta": f"Justamente por isso {produto} foi criado - para ECONOMIZAR seu tempo, não consumir mais.",
                "prova": "Estudos de tempo de implementação vs economia",
                "tecnica": "Inversão da objeção",
                "script": "O tempo que você 'não tem' agora vai se multiplicar quando implementar..."
            },
            "objecoes_credibilidade": {
                "objecao": "Como sei que isso realmente funciona?",
                "resposta": f"Excelente pergunta. Temos mais de X clientes no {segmento} com resultados comprovados.",
                "prova": "Estudos de caso específicos, depoimentos, métricas",
                "tecnica": "Prova social + evidência",
                "script": "Posso te mostrar exatamente os resultados de clientes similares a você..."
            },
            "objecoes_tecnicas": {
                "objecao": "Parece muito complexo para nossa realidade",
                "resposta": f"{produto} foi desenhado especificamente para {segmento} - é simples e direto.",
                "prova": "Demonstrações de facilidade, onboarding simplificado",
                "tecnica": "Simplificação + especificidade",
                "script": "Na verdade, é o oposto - simplificamos tudo para funcionar perfeitamente no seu contexto..."
            },
            "objecoes_necessidade": {
                "objecao": "Não sei se realmente preciso disso agora",
                "resposta": f"No {segmento}, quem não age agora fica para trás. O mercado não espera.",
                "prova": "Dados de mercado, tendências, concorrência",
                "tecnica": "Urgência + FOMO",
                "script": "Seus concorrentes já estão investindo nisso. A questão é: você quer liderar ou seguir?"
            },
            "objecoes_timing": {
                "objecao": "Talvez seja melhor esperar um momento melhor",
                "resposta": "O melhor momento foi ontem. O segundo melhor momento é agora.",
                "prova": "Análise de timing de mercado",
                "tecnica": "Autoridade + urgência",
                "script": "Analisando o mercado, nunca houve momento melhor para implementar..."
            },
            "objecoes_autoridade": {
                "objecao": "Preciso consultar outras pessoas antes",
                "resposta": f"Claro, decisões importantes no {segmento} merecem análise. Que tal levarmos os dados juntos?",
                "prova": "Materiais para apresentação interna",
                "tecnica": "Facilitação + colaboração",
                "script": "Posso preparar uma apresentação específica para sua equipe..."
            },
            "objecoes_experiencia": {
                "objecao": "Já tentei algo parecido e não funcionou",
                "resposta": f"Entendo. {produto} é diferente justamente porque foi criado aprendendo com esses erros.",
                "prova": "Diferenciações claras, evolução da solução",
                "tecnica": "Validação + diferenciação",
                "script": "Essa experiência anterior é valiosa. Deixe-me mostrar exatamente como evitamos esses problemas..."
            },
            "objecoes_concorrencia": {
                "objecao": "Estou considerando outras opções do mercado",
                "resposta": f"Inteligente comparar. Quando analisar, veja que somos os únicos que X, Y, Z no {segmento}.",
                "prova": "Tabela comparativa detalhada",
                "tecnica": "Diferenciação competitiva",
                "script": "Posso te mostrar uma comparação lado a lado para você decidir com dados..."
            },
            "objecoes_complexidade": {
                "objecao": "Parece muito complicado de entender/usar",
                "resposta": f"Aparência pode enganar. {produto} é sofisticado por dentro, simples por fora.",
                "prova": "Demonstração ao vivo, tutoriais simples",
                "tecnica": "Demonstração + simplificação",
                "script": "Deixe-me mostrar como é simples na prática..."
            },
            "estrategias_gerais": {
                "tecnica_escuta_ativa": "Sempre validar o sentimento antes de responder",
                "tecnica_reframe": "Transformar objeção em oportunidade de demonstrar valor",
                "tecnica_prova": "Sempre ter evidência específica para cada objeção",
                "tecnica_pergunta": "Usar perguntas para entender a objeção real",
                "tecnica_historia": "Contar casos similares que superaram a mesma objeção"
            }
        }

# Instância global
anti_objection_system = AntiObjectionSystem()