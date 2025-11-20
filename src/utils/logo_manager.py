"""
Gerenciador de Logo USB
Utilitário para converter e gerenciar o logo USB em base64
"""

import base64
import os
from pathlib import Path

class LogoManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.logo_path = self.base_dir / "static" / "logo_USB.png"
        self.logo_base64_path = self.base_dir / "static" / "logo_base64.txt"
        
    def get_logo_base64(self):
        """Retorna o logo em formato base64"""
        try:
            if self.logo_base64_path.exists():
                with open(self.logo_base64_path, 'r') as f:
                    return f.read().strip()
            else:
                return self._convert_logo_to_base64()
        except Exception as e:
            print(f"❌ Erro ao carregar logo base64: {e}")
            return None
    
    def _convert_logo_to_base64(self):
        """Converte o logo PNG para base64"""
        try:
            if not self.logo_path.exists():
                print(f"❌ Logo não encontrado em: {self.logo_path}")
                return None
                
            with open(self.logo_path, "rb") as image_file:
                logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Salvar para uso futuro
            with open(self.logo_base64_path, 'w') as f:
                f.write(logo_base64)
            
            print(f"✅ Logo convertido para base64 ({len(logo_base64)} chars)")
            return logo_base64
            
        except Exception as e:
            print(f"❌ Erro ao converter logo: {e}")
            return None
    
    def get_logo_data_url(self):
        """Retorna o logo como data URL para uso em HTML"""
        base64_data = self.get_logo_base64()
        if base64_data:
            return f"data:image/png;base64,{base64_data}"
        return None
    
    def get_logo_html_tag(self, width="200", height="auto", alt="USB MKT AM Logo", css_class=""):
        """Retorna uma tag HTML img com o logo"""
        data_url = self.get_logo_data_url()
        if data_url:
            class_attr = f' class="{css_class}"' if css_class else ''
            return f'<img src="{data_url}" width="{width}" height="{height}" alt="{alt}"{class_attr}>'
        return f'<div class="logo-placeholder">Logo não disponível</div>'

# Instância global para uso em outros módulos
logo_manager = LogoManager()