#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV18 Enhanced v18.0 - Credit Dashboard Integration
Integração do sistema de créditos com dashboard web
"""

from flask import Blueprint, jsonify, render_template_string
from utils.advanced_credit_manager import advanced_credit_manager

credit_dashboard = Blueprint('credit_dashboard', __name__)

@credit_dashboard.route('/api/credits/overview')
def credits_overview():
    """Endpoint para visão geral dos créditos"""
    try:
        overview = advanced_credit_manager.get_system_overview()
        return jsonify(overview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@credit_dashboard.route('/api/credits/provider/<provider>')
def provider_status(provider):
    """Endpoint para status de um provider específico"""
    try:
        status = advanced_credit_manager.get_provider_status(provider)
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@credit_dashboard.route('/api/credits/optimize')
def optimize_costs():
    """Endpoint para sugestões de otimização"""
    try:
        suggestions = advanced_credit_manager.optimize_costs()
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@credit_dashboard.route('/credits/dashboard')
def dashboard():
    """Dashboard visual dos créditos"""
    
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ARQV18 - Credit Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .card { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .success { color: green; }
            .warning { color: orange; }
            .error { color: red; }
            .stats { display: flex; gap: 20px; }
            .stat-box { background: #f5f5f5; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>🔍 ARQV18 Enhanced v18.0 - Credit Dashboard</h1>
        
        <div id="overview" class="card">
            <h2>📊 Visão Geral</h2>
            <div id="overview-content">Carregando...</div>
        </div>
        
        <div id="providers" class="card">
            <h2>🔑 Status dos Providers</h2>
            <div id="providers-content">Carregando...</div>
        </div>
        
        <div id="optimization" class="card">
            <h2>💡 Sugestões de Otimização</h2>
            <div id="optimization-content">Carregando...</div>
        </div>
        
        <script>
            async function loadDashboard() {
                try {
                    // Carregar visão geral
                    const overviewResponse = await fetch('/api/credits/overview');
                    const overview = await overviewResponse.json();
                    
                    document.getElementById('overview-content').innerHTML = `
                        <div class="stats">
                            <div class="stat-box">
                                <strong>Total de Chaves:</strong> ${overview.total_keys}
                            </div>
                            <div class="stat-box">
                                <strong>Chaves Ativas:</strong> ${overview.active_keys}
                            </div>
                            <div class="stat-box">
                                <strong>Taxa de Sucesso:</strong> ${(overview.overall_success_rate * 100).toFixed(1)}%
                            </div>
                            <div class="stat-box">
                                <strong>Custo Total:</strong> $${overview.total_cost.toFixed(2)}
                            </div>
                        </div>
                    `;
                    
                    // Carregar providers
                    let providersHtml = '';
                    for (const [provider, status] of Object.entries(overview.providers)) {
                        const healthClass = status.health_status === 'healthy' ? 'success' : 'error';
                        providersHtml += `
                            <div class="card">
                                <h3>${provider.toUpperCase()}</h3>
                                <p>Status: <span class="${healthClass}">${status.health_status}</span></p>
                                <p>Chaves: ${status.active_keys}/${status.total_keys}</p>
                                <p>Requests: ${status.total_requests}</p>
                                <p>Taxa de Sucesso: ${(status.success_rate * 100).toFixed(1)}%</p>
                            </div>
                        `;
                    }
                    document.getElementById('providers-content').innerHTML = providersHtml;
                    
                    // Carregar otimizações
                    const optimizationResponse = await fetch('/api/credits/optimize');
                    const optimization = await optimizationResponse.json();
                    
                    let optimizationHtml = `<p><strong>Custo Total:</strong> $${optimization.total_cost.toFixed(2)}</p>`;
                    
                    if (optimization.suggestions.length > 0) {
                        optimizationHtml += '<h4>Sugestões:</h4><ul>';
                        for (const suggestion of optimization.suggestions) {
                            optimizationHtml += `<li><strong>${suggestion.provider}:</strong> ${suggestion.recommendation}</li>`;
                        }
                        optimizationHtml += '</ul>';
                    } else {
                        optimizationHtml += '<p class="success">✅ Sistema otimizado!</p>';
                    }
                    
                    document.getElementById('optimization-content').innerHTML = optimizationHtml;
                    
                } catch (error) {
                    console.error('Erro ao carregar dashboard:', error);
                }
            }
            
            // Carregar dashboard ao iniciar
            loadDashboard();
            
            // Atualizar a cada 30 segundos
            setInterval(loadDashboard, 30000);
        </script>
    </body>
    </html>
    """
    
    return dashboard_html
