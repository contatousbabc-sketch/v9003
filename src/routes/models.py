# -*- coding: utf-8 -*-
"""
ARQV18 - Rotas para Gerenciamento de Modelos
Sistema completo de download, gerenciamento e otimização de modelos
"""

import os
import json
import psutil
import requests
from pathlib import Path
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from threading import Thread
import time

try:
    import GPUtil
except ImportError:
    GPUtil = None

models_bp = Blueprint('models', __name__)

# Configuração dos modelos disponíveis
AVAILABLE_MODELS = {
    "1": {
        "name": "🚀 Llama 3.2 1B GGUF (Q4_K_M) - ULTRA-RÁPIDO",
        "filename": "llama-3.2-1b-instruct-q4_k_m.gguf",
        "size": "0.8GB",
        "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        "description": "⚡ MAIS RÁPIDO - Ideal para análises rápidas e respostas instantâneas",
        "category": "Ultra-Leve",
        "use_case": "Análises rápidas, resumos, classificação",
        "speed": "⚡⚡⚡⚡⚡",
        "quality": "⭐⭐⭐",
        "memory": "2GB RAM",
        "size_bytes": 858993459  # ~0.8GB
    },
    "2": {
        "name": "🔥 Qwen2.5 0.5B GGUF (Q4_K_M) - MICRO-MODELO",
        "filename": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "size": "0.4GB",
        "url": "https://huggingface.co/bartowski/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",
        "description": "🏃 EXTREMAMENTE RÁPIDO - Perfeito para tarefas simples e fallback",
        "category": "Micro",
        "use_case": "Fallback, classificação básica, tags",
        "speed": "⚡⚡⚡⚡⚡",
        "quality": "⭐⭐",
        "memory": "1GB RAM",
        "size_bytes": 429496730  # ~0.4GB
    },
    "3": {
        "name": "💎 Phi-3.5 Mini GGUF (Q4_K_M) - MICROSOFT",
        "filename": "phi-3.5-mini-instruct-q4_k_m.gguf",
        "size": "2.4GB",
        "url": "https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf",
        "description": "🧠 INTELIGENTE - Excelente para análise de dados e insights",
        "category": "Leve",
        "use_case": "Análise de dados, insights, relatórios",
        "speed": "⚡⚡⚡⚡",
        "quality": "⭐⭐⭐⭐",
        "memory": "4GB RAM",
        "size_bytes": 2576980378  # ~2.4GB
    },
    "4": {
        "name": "🎯 Llama 3.2 3B GGUF (Q4_K_M) - EQUILIBRADO",
        "filename": "llama-3.2-3b-instruct-q4_k_m.gguf",
        "size": "2.0GB",
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "description": "⚖️ BALANCEADO - Ótima relação velocidade/qualidade para análises",
        "category": "Balanceado",
        "use_case": "Análise completa, relatórios detalhados",
        "speed": "⚡⚡⚡⚡",
        "quality": "⭐⭐⭐⭐",
        "memory": "4GB RAM",
        "size_bytes": 2147483648  # ~2.0GB
    },
    "5": {
        "name": "🌟 Qwen2.5 3B GGUF (Q4_K_M) - MULTILÍNGUE",
        "filename": "qwen2.5-3b-instruct-q4_k_m.gguf",
        "size": "2.0GB",
        "url": "https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf",
        "description": "🌍 MULTILÍNGUE - Excelente para português e análises internacionais",
        "category": "Balanceado",
        "use_case": "Análise multilíngue, mercados globais",
        "speed": "⚡⚡⚡⚡",
        "quality": "⭐⭐⭐⭐",
        "memory": "4GB RAM",
        "size_bytes": 2147483648  # ~2.0GB
    },
    "6": {
        "name": "💼 Gemma 2B GGUF (Q4_K_M) - GOOGLE",
        "filename": "gemma-2b-it-q4_k_m.gguf",
        "size": "1.6GB",
        "url": "https://huggingface.co/bartowski/gemma-2b-it-GGUF/resolve/main/gemma-2b-it-Q4_K_M.gguf",
        "description": "🏢 CORPORATIVO - Ideal para análises de negócios e mercado",
        "category": "Leve",
        "use_case": "Análise de negócios, estratégia",
        "speed": "⚡⚡⚡⚡",
        "quality": "⭐⭐⭐⭐",
        "memory": "3GB RAM",
        "size_bytes": 1717986918  # ~1.6GB
    },
    "7": {
        "name": "🏆 Qwen2.5 7B GGUF (Q4_K_M) - PREMIUM",
        "filename": "qwen2.5-7b-instruct-q4_k_m.gguf",
        "size": "4.4GB",
        "url": "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf",
        "description": "👑 PREMIUM - Máxima qualidade para análises complexas e detalhadas",
        "category": "Premium",
        "use_case": "Análises complexas, insights profundos",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 4724464025  # ~4.4GB
    },
    "8": {
        "name": "🧪 Mistral 7B GGUF (Q4_K_M) - CIENTÍFICO",
        "filename": "mistral-7b-instruct-q4_k_m.gguf",
        "size": "4.1GB",
        "url": "https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
        "description": "🔬 CIENTÍFICO - Excelente para análises técnicas e dados complexos",
        "category": "Premium",
        "use_case": "Análise técnica, dados científicos",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 4402341478  # ~4.1GB
    },
    "9": {
        "name": "🇧🇷 Sabiá-3 8B GGUF (Q4_K_M) - PORTUGUÊS",
        "filename": "sabia-3-8b-instruct-q4_k_m.gguf",
        "size": "4.8GB",
        "url": "https://huggingface.co/bartowski/Sabia-3-8B-Instruct-GGUF/resolve/main/Sabia-3-8B-Instruct-Q4_K_M.gguf",
        "description": "🇧🇷 BRASILEIRO - Especializado em português e cultura brasileira",
        "category": "Português",
        "use_case": "Análise em português, mercado brasileiro",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 5153960756  # ~4.8GB
    },
    "10": {
        "name": "🔥 Llama 3.1 8B GGUF (Q4_K_M) - VERSÁTIL",
        "filename": "llama-3.1-8b-instruct-q4_k_m.gguf",
        "size": "4.6GB",
        "url": "https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
        "description": "🎯 VERSÁTIL - Excelente para múltiplas tarefas e análises gerais",
        "category": "Premium",
        "use_case": "Análises gerais, múltiplas tarefas",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 4939212390  # ~4.6GB
    },
    "11": {
        "name": "⚡ TinyLlama 1.1B GGUF (Q4_K_M) - ULTRA-LEVE",
        "filename": "tinyllama-1.1b-chat-q4_k_m.gguf",
        "size": "0.7GB",
        "url": "https://huggingface.co/bartowski/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/TinyLlama-1.1B-Chat-v1.0-Q4_K_M.gguf",
        "description": "⚡ ULTRA-LEVE - Perfeito para sistemas com pouca RAM",
        "category": "Ultra-Leve",
        "use_case": "Sistemas limitados, fallback rápido",
        "speed": "⚡⚡⚡⚡⚡",
        "quality": "⭐⭐",
        "memory": "2GB RAM",
        "size_bytes": 751619276  # ~0.7GB
    },
    "12": {
        "name": "🎨 CodeLlama 7B GGUF (Q4_K_M) - CÓDIGO",
        "filename": "codellama-7b-instruct-q4_k_m.gguf",
        "size": "4.0GB",
        "url": "https://huggingface.co/bartowski/CodeLlama-7b-Instruct-hf-GGUF/resolve/main/CodeLlama-7b-Instruct-hf-Q4_K_M.gguf",
        "description": "💻 CÓDIGO - Especializado em análise de código e programação",
        "category": "Especializado",
        "use_case": "Análise de código, debugging",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 4294967296  # ~4.0GB
    },
    "13": {
        "name": "🌟 Gemma 2 9B GGUF (Q4_K_M) - GOOGLE V2",
        "filename": "gemma-2-9b-it-q4_k_m.gguf",
        "size": "5.4GB",
        "url": "https://huggingface.co/bartowski/gemma-2-9b-it-GGUF/resolve/main/gemma-2-9b-it-Q4_K_M.gguf",
        "description": "🏢 GOOGLE V2 - Versão aprimorada para análises corporativas",
        "category": "Premium",
        "use_case": "Análises corporativas avançadas",
        "speed": "⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "8GB RAM",
        "size_bytes": 5798205850  # ~5.4GB
    },
    "14": {
        "name": "🚀 Phi-3 Medium GGUF (Q4_K_M) - MICROSOFT",
        "filename": "phi-3-medium-4k-instruct-q4_k_m.gguf",
        "size": "8.2GB",
        "url": "https://huggingface.co/bartowski/Phi-3-medium-4k-instruct-GGUF/resolve/main/Phi-3-medium-4k-instruct-Q4_K_M.gguf",
        "description": "🧠 MICROSOFT MEDIUM - Alta qualidade para análises complexas",
        "category": "Premium",
        "use_case": "Análises complexas, insights profundos",
        "speed": "⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "10GB RAM",
        "size_bytes": 8804682957  # ~8.2GB
    },
    "15": {
        "name": "🔬 Mixtral 8x7B GGUF (Q4_K_M) - EXPERT",
        "filename": "mixtral-8x7b-instruct-q4_k_m.gguf",
        "size": "26.4GB",
        "url": "https://huggingface.co/bartowski/Mixtral-8x7B-Instruct-v0.1-GGUF/resolve/main/Mixtral-8x7B-Instruct-v0.1-Q4_K_M.gguf",
        "description": "🎯 EXPERT - Modelo de especialistas para análises ultra-avançadas",
        "category": "Expert",
        "use_case": "Análises ultra-complexas, pesquisa",
        "speed": "⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "32GB RAM",
        "size_bytes": 28372963328  # ~26.4GB
    },
    "16": {
        "name": "🎯 Qwen2.5 14B GGUF (Q4_K_M) - AVANÇADO",
        "filename": "qwen2.5-14b-instruct-q4_k_m.gguf",
        "size": "8.5GB",
        "url": "https://huggingface.co/bartowski/Qwen2.5-14B-Instruct-GGUF/resolve/main/Qwen2.5-14B-Instruct-Q4_K_M.gguf",
        "description": "🎯 AVANÇADO - Modelo grande para análises detalhadas",
        "category": "Avançado",
        "use_case": "Análises detalhadas, relatórios complexos",
        "speed": "⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "12GB RAM",
        "size_bytes": 9126805504  # ~8.5GB
    },
    "17": {
        "name": "🔥 Llama 3.3 70B GGUF (Q4_K_M) - FLAGSHIP",
        "filename": "llama-3.3-70b-instruct-q4_k_m.gguf",
        "size": "39.8GB",
        "url": "https://huggingface.co/bartowski/Llama-3.3-70B-Instruct-GGUF/resolve/main/Llama-3.3-70B-Instruct-Q4_K_M.gguf",
        "description": "👑 FLAGSHIP - O melhor modelo Llama para análises supremas",
        "category": "Flagship",
        "use_case": "Análises supremas, pesquisa avançada",
        "speed": "⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "48GB RAM",
        "size_bytes": 42776558592  # ~39.8GB
    },
    "18": {
        "name": "🌟 Qwen2.5 32B GGUF (Q4_K_M) - ENTERPRISE",
        "filename": "qwen2.5-32b-instruct-q4_k_m.gguf",
        "size": "19.2GB",
        "url": "https://huggingface.co/bartowski/Qwen2.5-32B-Instruct-GGUF/resolve/main/Qwen2.5-32B-Instruct-Q4_K_M.gguf",
        "description": "🏢 ENTERPRISE - Modelo corporativo para análises empresariais",
        "category": "Enterprise",
        "use_case": "Análises empresariais, estratégia",
        "speed": "⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "24GB RAM",
        "size_bytes": 20610662400  # ~19.2GB
    },
    "19": {
        "name": "🔬 DeepSeek Coder 6.7B GGUF (Q4_K_M) - CÓDIGO",
        "filename": "deepseek-coder-6.7b-instruct-q4_k_m.gguf",
        "size": "4.0GB",
        "url": "https://huggingface.co/bartowski/deepseek-coder-6.7b-instruct-GGUF/resolve/main/deepseek-coder-6.7b-instruct-Q4_K_M.gguf",
        "description": "💻 DEEPSEEK - Especialista em código e análise técnica",
        "category": "Especializado",
        "use_case": "Análise de código, desenvolvimento",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 4294967296  # ~4.0GB
    },
    "20": {
        "name": "🎨 Stable Code 3B GGUF (Q4_K_M) - STABLE",
        "filename": "stable-code-3b-q4_k_m.gguf",
        "size": "1.8GB",
        "url": "https://huggingface.co/bartowski/stable-code-3b-GGUF/resolve/main/stable-code-3b-Q4_K_M.gguf",
        "description": "🎨 STABLE - Modelo estável para análise de código",
        "category": "Especializado",
        "use_case": "Análise de código, refatoração",
        "speed": "⚡⚡⚡⚡",
        "quality": "⭐⭐⭐⭐",
        "memory": "4GB RAM",
        "size_bytes": 1932735284  # ~1.8GB
    },
    "21": {
        "name": "🌟 Gemma 2 27B GGUF (Q4_K_M) - GOOGLE LARGE",
        "filename": "gemma-2-27b-it-q4_k_m.gguf",
        "size": "16.1GB",
        "url": "https://huggingface.co/bartowski/gemma-2-27b-it-GGUF/resolve/main/gemma-2-27b-it-Q4_K_M.gguf",
        "description": "🏢 GOOGLE LARGE - Modelo grande do Google para análises avançadas",
        "category": "Avançado",
        "use_case": "Análises avançadas, insights corporativos",
        "speed": "⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "20GB RAM",
        "size_bytes": 17280000000  # ~16.1GB
    },
    "22": {
        "name": "🇧🇷 TeenyTinyLlama 1.1B GGUF (Q4_K_M) - MICRO-BR",
        "filename": "teenytinyllama-1.1b-q4_k_m.gguf",
        "size": "0.6GB",
        "url": "https://huggingface.co/bartowski/TeenyTinyLlama-1.1B-GGUF/resolve/main/TeenyTinyLlama-1.1B-Q4_K_M.gguf",
        "description": "🇧🇷 MICRO-BR - Modelo ultra-leve com suporte ao português",
        "category": "Ultra-Leve",
        "use_case": "Fallback ultra-rápido, classificação",
        "speed": "⚡⚡⚡⚡⚡",
        "quality": "⭐⭐",
        "memory": "1GB RAM",
        "size_bytes": 644245094  # ~0.6GB
    },
    "23": {
        "name": "🔥 Vicuna 7B GGUF (Q4_K_M) - CONVERSACIONAL",
        "filename": "vicuna-7b-v1.5-q4_k_m.gguf",
        "size": "4.1GB",
        "url": "https://huggingface.co/bartowski/vicuna-7b-v1.5-GGUF/resolve/main/vicuna-7b-v1.5-Q4_K_M.gguf",
        "description": "💬 CONVERSACIONAL - Excelente para análises interativas",
        "category": "Premium",
        "use_case": "Análises interativas, conversação",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 4402341478  # ~4.1GB
    },
    "24": {
        "name": "🎯 Orca 2 7B GGUF (Q4_K_M) - MICROSOFT",
        "filename": "orca-2-7b-q4_k_m.gguf",
        "size": "4.1GB",
        "url": "https://huggingface.co/bartowski/Orca-2-7b-GGUF/resolve/main/Orca-2-7b-Q4_K_M.gguf",
        "description": "🐋 ORCA - Modelo Microsoft para raciocínio complexo",
        "category": "Premium",
        "use_case": "Raciocínio complexo, análise lógica",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 4402341478  # ~4.1GB
    },
    "25": {
        "name": "🌟 Solar 10.7B GGUF (Q4_K_M) - UPSTAGE",
        "filename": "solar-10.7b-instruct-q4_k_m.gguf",
        "size": "6.4GB",
        "url": "https://huggingface.co/bartowski/SOLAR-10.7B-Instruct-v1.0-GGUF/resolve/main/SOLAR-10.7B-Instruct-v1.0-Q4_K_M.gguf",
        "description": "☀️ SOLAR - Modelo inovador para análises criativas",
        "category": "Premium",
        "use_case": "Análises criativas, inovação",
        "speed": "⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "8GB RAM",
        "size_bytes": 6871947674  # ~6.4GB
    },
    "26": {
        "name": "🔬 WizardLM 7B GGUF (Q4_K_M) - WIZARD",
        "filename": "wizardlm-7b-v1.0-q4_k_m.gguf",
        "size": "4.1GB",
        "url": "https://huggingface.co/bartowski/WizardLM-7B-V1.0-GGUF/resolve/main/WizardLM-7B-V1.0-Q4_K_M.gguf",
        "description": "🧙 WIZARD - Modelo mágico para análises especializadas",
        "category": "Premium",
        "use_case": "Análises especializadas, insights únicos",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 4402341478  # ~4.1GB
    },
    "27": {
        "name": "🎨 Yi 6B GGUF (Q4_K_M) - 01.AI",
        "filename": "yi-6b-chat-q4_k_m.gguf",
        "size": "3.6GB",
        "url": "https://huggingface.co/bartowski/Yi-6B-Chat-GGUF/resolve/main/Yi-6B-Chat-Q4_K_M.gguf",
        "description": "🎨 01.AI - Modelo chinês para análises multilíngues",
        "category": "Balanceado",
        "use_case": "Análises multilíngues, mercados asiáticos",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐",
        "memory": "5GB RAM",
        "size_bytes": 3865470566  # ~3.6GB
    },
    "28": {
        "name": "🚀 Zephyr 7B GGUF (Q4_K_M) - HUGGINGFACE",
        "filename": "zephyr-7b-beta-q4_k_m.gguf",
        "size": "4.1GB",
        "url": "https://huggingface.co/bartowski/zephyr-7b-beta-GGUF/resolve/main/zephyr-7b-beta-Q4_K_M.gguf",
        "description": "🌪️ ZEPHYR - Modelo rápido da HuggingFace",
        "category": "Premium",
        "use_case": "Análises rápidas, prototipagem",
        "speed": "⚡⚡⚡⚡",
        "quality": "⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 4402341478  # ~4.1GB
    },
    "29": {
        "name": "🔥 Starling 7B GGUF (Q4_K_M) - BERKELEY",
        "filename": "starling-lm-7b-alpha-q4_k_m.gguf",
        "size": "4.1GB",
        "url": "https://huggingface.co/bartowski/Starling-LM-7B-alpha-GGUF/resolve/main/Starling-LM-7B-alpha-Q4_K_M.gguf",
        "description": "⭐ STARLING - Modelo Berkeley para análises acadêmicas",
        "category": "Premium",
        "use_case": "Análises acadêmicas, pesquisa",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 4402341478  # ~4.1GB
    },
    "30": {
        "name": "🌟 OpenHermes 2.5 7B GGUF (Q4_K_M) - NOUS",
        "filename": "openhermes-2.5-mistral-7b-q4_k_m.gguf",
        "size": "4.1GB",
        "url": "https://huggingface.co/bartowski/OpenHermes-2.5-Mistral-7B-GGUF/resolve/main/OpenHermes-2.5-Mistral-7B-Q4_K_M.gguf",
        "description": "🔮 HERMES - Modelo Nous Research para análises versáteis",
        "category": "Premium",
        "use_case": "Análises versáteis, múltiplos domínios",
        "speed": "⚡⚡⚡",
        "quality": "⭐⭐⭐⭐⭐",
        "memory": "6GB RAM",
        "size_bytes": 4402341478  # ~4.1GB
    }
}

def get_system_specs():
    """Detecta especificações do sistema"""
    try:
        ram_gb = psutil.virtual_memory().total / (1024**3)
        cpu_cores = psutil.cpu_count()
        
        # Verificar GPU básico
        gpu_available = False
        if GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                gpu_available = len(gpus) > 0
            except:
                pass
        
        return {
            'ram_gb': ram_gb,
            'cpu_cores': cpu_cores,
            'gpu_available': gpu_available
        }
    except:
        return {
            'ram_gb': 8.0,
            'cpu_cores': 4,
            'gpu_available': False
        }

def get_model_info(filepath):
    """Obtém informações do modelo"""
    try:
        if not filepath.exists():
            return {'exists': False}
        
        size = filepath.stat().st_size
        size_gb = size / (1024**3)
        modified = datetime.fromtimestamp(filepath.stat().st_mtime)
        
        return {
            'exists': True,
            'size_bytes': size,
            'size_gb': size_gb,
            'modified': modified.isoformat(),
            'filename': filepath.name
        }
    except:
        return {'exists': False}

def get_installed_models():
    """Lista modelos instalados"""
    model_dir = Path("model")
    
    if not model_dir.exists():
        return {'current_model': None, 'other_models': []}
    
    current_model = None
    other_models = []
    
    # Verificar modelo ativo
    main_model = model_dir / "model.gguf"
    if main_model.exists():
        current_model = get_model_info(main_model)
        current_model['is_active'] = True
    
    # Listar outros modelos
    for model_file in model_dir.glob("*.gguf"):
        if model_file.name != "model.gguf":
            info = get_model_info(model_file)
            if info['exists']:
                info['is_active'] = False
                other_models.append(info)
    
    return {
        'current_model': current_model,
        'other_models': other_models
    }

@models_bp.route('/api/models/available')
def get_available_models():
    """Retorna lista de modelos disponíveis para download"""
    try:
        # Agrupar por categoria
        categories = {}
        for key, model in AVAILABLE_MODELS.items():
            category = model['category']
            if category not in categories:
                categories[category] = []
            
            model_data = model.copy()
            model_data['id'] = key
            categories[category].append(model_data)
        
        return jsonify({
            'success': True,
            'models': AVAILABLE_MODELS,
            'categories': categories,
            'system_specs': get_system_specs()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@models_bp.route('/api/models/installed')
def get_installed_models_api():
    """Retorna lista de modelos instalados"""
    try:
        models = get_installed_models()
        
        # Adicionar estatísticas
        model_dir = Path("model")
        backup_dir = model_dir / "backup"
        
        total_models = len([f for f in model_dir.glob("*.gguf")]) if model_dir.exists() else 0
        total_backups = len([f for f in backup_dir.glob("*.gguf")]) if backup_dir.exists() else 0
        
        total_size = 0
        backup_size = 0
        
        if model_dir.exists():
            for f in model_dir.glob("*.gguf"):
                total_size += f.stat().st_size
        
        if backup_dir.exists():
            for f in backup_dir.glob("*.gguf"):
                backup_size += f.stat().st_size
        
        return jsonify({
            'success': True,
            'current_model': models['current_model'],
            'other_models': models['other_models'],
            'stats': {
                'total_models': total_models,
                'total_backups': total_backups,
                'total_size_gb': total_size / (1024**3),
                'backup_size_gb': backup_size / (1024**3)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@models_bp.route('/api/models/download', methods=['POST'])
def download_model():
    """Inicia download de um modelo"""
    try:
        data = request.get_json()
        model_id = data.get('model_id')
        
        if model_id not in AVAILABLE_MODELS:
            return jsonify({'success': False, 'error': 'Modelo não encontrado'})
        
        model = AVAILABLE_MODELS[model_id]
        
        # Criar diretório se não existir
        model_dir = Path("model")
        model_dir.mkdir(exist_ok=True)
        
        filepath = model_dir / model['filename']
        
        # Verificar se já existe
        if filepath.exists():
            return jsonify({
                'success': False, 
                'error': 'Modelo já existe',
                'existing': True
            })
        
        # Iniciar download em thread separada
        download_thread = Thread(
            target=download_model_file,
            args=(model['url'], filepath, model_id)
        )
        download_thread.daemon = True
        download_thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Download iniciado: {model["name"]}',
            'model_id': model_id,
            'filename': model['filename']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def download_model_file(url, filepath, model_id):
    """Função para download do arquivo em thread separada"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # Atualizar progresso (pode ser implementado com WebSocket)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        # TODO: Enviar progresso via WebSocket
        
        # Verificar se é o primeiro modelo
        main_model = filepath.parent / "model.gguf"
        if not main_model.exists():
            filepath.rename(main_model)
            
    except Exception as e:
        # Remover arquivo parcial em caso de erro
        if filepath.exists():
            filepath.unlink()
        print(f"Erro no download: {e}")

@models_bp.route('/api/models/switch', methods=['POST'])
def switch_model():
    """Troca o modelo ativo"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'success': False, 'error': 'Nome do arquivo não fornecido'})
        
        model_dir = Path("model")
        new_model_path = model_dir / filename
        main_model = model_dir / "model.gguf"
        backup_dir = model_dir / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        if not new_model_path.exists():
            return jsonify({'success': False, 'error': 'Modelo não encontrado'})
        
        # Fazer backup do modelo atual
        if main_model.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"model_backup_{timestamp}.gguf"
            backup_path = backup_dir / backup_name
            main_model.rename(backup_path)
        
        # Copiar novo modelo
        import shutil
        shutil.copy2(str(new_model_path), str(main_model))
        
        return jsonify({
            'success': True,
            'message': f'Modelo trocado para: {filename}',
            'backup_created': True
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@models_bp.route('/api/models/delete', methods=['POST'])
def delete_model():
    """Remove um modelo"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'success': False, 'error': 'Nome do arquivo não fornecido'})
        
        if filename == "model.gguf":
            return jsonify({'success': False, 'error': 'Não é possível remover o modelo ativo'})
        
        model_dir = Path("model")
        model_path = model_dir / filename
        
        if not model_path.exists():
            return jsonify({'success': False, 'error': 'Modelo não encontrado'})
        
        model_path.unlink()
        
        return jsonify({
            'success': True,
            'message': f'Modelo removido: {filename}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@models_bp.route('/api/models/optimize')
def optimize_model():
    """Retorna configurações otimizadas baseadas no modelo ativo"""
    try:
        model_path = Path("model/model.gguf")
        
        if not model_path.exists():
            return jsonify({
                'success': False,
                'error': 'Nenhum modelo ativo encontrado'
            })
        
        # Obter tamanho do modelo
        model_size_gb = model_path.stat().st_size / (1024**3)
        system_specs = get_system_specs()
        
        # Gerar configurações otimizadas
        settings = generate_optimized_settings(model_size_gb, system_specs)
        
        return jsonify({
            'success': True,
            'model_size_gb': model_size_gb,
            'system_specs': system_specs,
            'optimized_settings': settings,
            'recommendations': generate_recommendations(model_size_gb, system_specs)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def generate_optimized_settings(model_size_gb, system_specs):
    """Gera configurações otimizadas"""
    ram_gb = system_specs['ram_gb']
    cpu_cores = system_specs['cpu_cores']
    gpu_available = system_specs['gpu_available']
    
    settings = {}
    
    if model_size_gb <= 1.0:  # Modelos pequenos
        settings.update({
            'max_tokens': 4096,
            'context_length': 4096,
            'batch_size': 512,
            'threads': min(cpu_cores, 8),
            'gpu_layers': 35 if gpu_available else 0,
            'memory_map': True,
            'use_mlock': ram_gb >= 8,
            'low_vram': False
        })
    elif model_size_gb <= 2.5:  # Modelos médios
        settings.update({
            'max_tokens': 4096,
            'context_length': 4096,
            'batch_size': 256,
            'threads': min(cpu_cores, 6),
            'gpu_layers': 30 if gpu_available else 0,
            'memory_map': True,
            'use_mlock': ram_gb >= 12,
            'low_vram': ram_gb < 8
        })
    elif model_size_gb <= 5.0:  # Modelos grandes
        settings.update({
            'max_tokens': 4096,
            'context_length': 4096,
            'batch_size': 128,
            'threads': min(cpu_cores, 4),
            'gpu_layers': 25 if gpu_available and ram_gb >= 8 else 0,
            'memory_map': True,
            'use_mlock': ram_gb >= 16,
            'low_vram': ram_gb < 12
        })
    else:  # Modelos muito grandes
        settings.update({
            'max_tokens': 4096,
            'context_length': 2048,
            'batch_size': 64,
            'threads': min(cpu_cores, 4),
            'gpu_layers': 20 if gpu_available and ram_gb >= 16 else 0,
            'memory_map': True,
            'use_mlock': ram_gb >= 24,
            'low_vram': ram_gb < 16
        })
    
    # Ajustes para RAM limitada
    if ram_gb < 8:
        settings.update({
            'max_tokens': min(settings['max_tokens'], 2048),
            'context_length': min(settings['context_length'], 2048),
            'batch_size': min(settings['batch_size'], 64),
            'gpu_layers': 0,
            'low_vram': True
        })
    
    return settings

def generate_recommendations(model_size_gb, system_specs):
    """Gera recomendações específicas"""
    recommendations = []
    
    if system_specs['ram_gb'] < 8:
        recommendations.append("⚠️ RAM limitada - considere usar modelos menores")
    
    if not system_specs['gpu_available']:
        recommendations.append("🔧 GPU não detectada - usando apenas CPU")
    
    if model_size_gb > system_specs['ram_gb'] * 0.5:
        recommendations.append("📊 Modelo grande para sua RAM - pode haver lentidão")
    
    if system_specs['gpu_available']:
        recommendations.append("🚀 GPU configurada - performance otimizada")
    
    return recommendations

@models_bp.route('/api/models/recommendation')
def get_model_recommendation():
    """Retorna recomendação personalizada de modelo"""
    try:
        ram_choice = request.args.get('ram', 'medium')  # low, medium, high
        priority = request.args.get('priority', 'balanced')  # speed, quality, balanced
        use_case = request.args.get('use_case', 'general')  # general, complex, code, portuguese
        
        recommendations = []
        
        if ram_choice == 'low':  # RAM limitada
            if priority == 'speed':
                recommendations = ['1', '2', '12']
            elif priority == 'quality':
                recommendations = ['3', '4', '6']
            else:  # balanced
                recommendations = ['1', '4', '2']
        elif ram_choice == 'medium':  # RAM média
            if priority == 'speed':
                recommendations = ['4', '5', '6']
            elif priority == 'quality':
                recommendations = ['7', '8']
            else:  # balanced
                recommendations = ['4', '5', '7']
        else:  # RAM alta
            if use_case == 'code':
                recommendations = ['8', '7']
            elif use_case == 'portuguese':
                recommendations = ['7', '5']
            elif priority == 'quality':
                recommendations = ['7', '8']
            else:
                recommendations = ['7', '8']
        
        # Pegar apenas os 3 primeiros
        recommendations = recommendations[:3]
        
        recommended_models = []
        for rec_id in recommendations:
            if rec_id in AVAILABLE_MODELS:
                model = AVAILABLE_MODELS[rec_id].copy()
                model['id'] = rec_id
                recommended_models.append(model)
        
        return jsonify({
            'success': True,
            'recommendations': recommended_models,
            'criteria': {
                'ram': ram_choice,
                'priority': priority,
                'use_case': use_case
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
