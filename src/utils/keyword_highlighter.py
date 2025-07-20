"""Sistema de destaque de palavras-chave para legendas.

Este módulo implementa o estilo "highlighted subtitle" que destaca
palavras-chave específicas com fundos coloridos, muito popular em
vídeos para redes sociais (TikTok, Instagram Reels, YouTube Shorts).
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class HighlightConfig:
    """Configuração para destaque de palavras."""
    word: str
    color: str
    background_color: str
    text_color: str = "white"
    
class KeywordHighlighter:
    """Gerenciador de destaque de palavras-chave em legendas."""
    
    # Palavras-chave automáticas por categoria
    KEYWORD_CATEGORIES = {
        "action": {
            "words": ["CREATE", "BUILD", "MAKE", "DO", "START", "GO", "PLAY", "RUN", "MOVE", "WORK"],
            "color": "#007AFF",  # Azul
            "description": "Palavras de ação e criação"
        },
        "success": {
            "words": ["SUCCESS", "WIN", "ACHIEVE", "COMPLETE", "DONE", "PERFECT", "GREAT", "EXCELLENT"],
            "color": "#34C759",  # Verde
            "description": "Palavras de sucesso e positivas"
        },
        "alert": {
            "words": ["STOP", "WARNING", "DANGER", "ALERT", "IMPORTANT", "URGENT", "CRITICAL"],
            "color": "#FF3B30",  # Vermelho
            "description": "Palavras de alerta e importância"
        },
        "highlight": {
            "words": ["NEW", "AMAZING", "INCREDIBLE", "WOW", "AWESOME", "FANTASTIC", "SPECIAL", "UNIQUE"],
            "color": "#FF9500",  # Laranja
            "description": "Palavras de destaque e admiração"
        },
        "creative": {
            "words": ["CREATIVE", "ART", "DESIGN", "BEAUTIFUL", "STYLE", "COOL", "TRENDY", "MODERN"],
            "color": "#AF52DE",  # Roxo
            "description": "Palavras criativas e artísticas"
        }
    }
    
    def __init__(self):
        """Inicializa o destacador de palavras-chave."""
        self.custom_highlights = {}
        self._build_keyword_map()
    
    def _build_keyword_map(self):
        """Constrói mapa de palavras-chave para cores."""
        self.keyword_map = {}
        
        for category, config in self.KEYWORD_CATEGORIES.items():
            for word in config["words"]:
                self.keyword_map[word.upper()] = {
                    "color": config["color"],
                    "category": category
                }
    
    def add_custom_highlight(self, word: str, color: str, text_color: str = "white"):
        """Adiciona destaque personalizado para uma palavra.
        
        Args:
            word: Palavra a ser destacada
            color: Cor de fundo (hex)
            text_color: Cor do texto (padrão: branco)
        """
        self.custom_highlights[word.upper()] = {
            "color": color,
            "text_color": text_color
        }
    
    def detect_keywords(self, text: str) -> List[Tuple[str, str, int, int]]:
        """Detecta palavras-chave automaticamente no texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Lista de tuplas (palavra, cor, posição_início, posição_fim)
        """
        keywords_found = []
        words = re.finditer(r'\b\w+\b', text)
        
        for match in words:
            word = match.group().upper()
            start, end = match.span()
            
            # Verificar highlights personalizados primeiro
            if word in self.custom_highlights:
                keywords_found.append((
                    match.group(),
                    self.custom_highlights[word]["color"],
                    start,
                    end
                ))
            # Verificar palavras-chave automáticas
            elif word in self.keyword_map:
                keywords_found.append((
                    match.group(),
                    self.keyword_map[word]["color"],
                    start,
                    end
                ))
        
        return keywords_found
    
    def parse_manual_markup(self, text: str) -> Tuple[str, List[Tuple[str, str, int, int]]]:
        """Processa marcações manuais no texto.
        
        Sintaxe: {PALAVRA:cor} ou {PALAVRA:categoria}
        
        Args:
            text: Texto com marcações
            
        Returns:
            Tupla (texto_limpo, lista_de_highlights)
        """
        highlights = []
        clean_text = text
        offset = 0
        
        # Padrão para encontrar marcações: {PALAVRA:cor}
        pattern = r'\{([^:}]+):([^}]+)\}'
        
        for match in re.finditer(pattern, text):
            word = match.group(1)
            color_or_category = match.group(2).lower()
            
            # Determinar cor
            if color_or_category.startswith('#'):
                # Cor hex direta
                color = color_or_category
            elif color_or_category in self.KEYWORD_CATEGORIES:
                # Nome de categoria
                color = self.KEYWORD_CATEGORIES[color_or_category]["color"]
            else:
                # Cores nomeadas
                color_map = {
                    'blue': '#007AFF',
                    'green': '#34C759',
                    'red': '#FF3B30',
                    'orange': '#FF9500',
                    'purple': '#AF52DE',
                    'yellow': '#FFCC00',
                    'pink': '#FF2D92'
                }
                color = color_map.get(color_or_category, '#007AFF')
            
            # Calcular posição no texto limpo
            start_in_clean = match.start() - offset
            end_in_clean = start_in_clean + len(word)
            
            highlights.append((word, color, start_in_clean, end_in_clean))
            
            # Remover marcação do texto
            clean_text = clean_text.replace(match.group(), word, 1)
            offset += len(match.group()) - len(word)
        
        return clean_text, highlights
    
    def generate_ass_tags(self, text: str, auto_detect: bool = True) -> str:
        """Gera tags ASS para formatação avançada.
        
        Args:
            text: Texto original
            auto_detect: Se deve detectar palavras-chave automaticamente
            
        Returns:
            Texto com tags ASS para destaque
        """
        # Primeiro processar marcações manuais
        clean_text, manual_highlights = self.parse_manual_markup(text)
        
        # Detectar palavras-chave automáticas se solicitado
        auto_highlights = []
        if auto_detect:
            auto_highlights = self.detect_keywords(clean_text)
        
        # Combinar highlights (manuais têm prioridade)
        all_highlights = manual_highlights + auto_highlights
        
        # Remover sobreposições (manuais têm prioridade)
        final_highlights = self._remove_overlaps(all_highlights)
        
        # Gerar texto com tags ASS
        if not final_highlights:
            return clean_text
        
        # Ordenar por posição
        final_highlights.sort(key=lambda x: x[2])
        
        result = ""
        last_pos = 0
        
        for word, color, start, end in final_highlights:
            # Adicionar texto antes do highlight
            result += clean_text[last_pos:start]
            
            # Adicionar palavra com destaque
            # Converter cor hex para BGR (formato ASS)
            bgr_color = self._hex_to_bgr(color)
            
            # Tags ASS para destaque
            result += f"{{\\c&H{bgr_color}&\\3c&H000000&\\bord2}}{word}{{\\r}}"
            
            last_pos = end
        
        # Adicionar texto restante
        result += clean_text[last_pos:]
        
        return result
    
    def _remove_overlaps(self, highlights: List[Tuple[str, str, int, int]]) -> List[Tuple[str, str, int, int]]:
        """Remove sobreposições de highlights.
        
        Args:
            highlights: Lista de highlights
            
        Returns:
            Lista sem sobreposições
        """
        if not highlights:
            return []
        
        # Ordenar por posição
        sorted_highlights = sorted(highlights, key=lambda x: x[2])
        result = [sorted_highlights[0]]
        
        for current in sorted_highlights[1:]:
            last = result[-1]
            
            # Verificar sobreposição
            if current[2] >= last[3]:  # Não há sobreposição
                result.append(current)
            # Se há sobreposição, manter o primeiro (prioridade)
        
        return result
    
    def _hex_to_bgr(self, hex_color: str) -> str:
        """Converte cor hex para formato BGR do ASS.
        
        Args:
            hex_color: Cor em formato hex (#RRGGBB)
            
        Returns:
            Cor em formato BGR (BBGGRR)
        """
        if not hex_color.startswith('#') or len(hex_color) != 7:
            return "0000FF"  # Azul padrão
        
        # Remover #
        hex_color = hex_color[1:]
        
        # Extrair componentes RGB
        r = hex_color[0:2]
        g = hex_color[2:4]
        b = hex_color[4:6]
        
        # Retornar em formato BGR
        return f"{b}{g}{r}"
    
    def get_available_categories(self) -> Dict[str, Dict]:
        """Retorna categorias disponíveis de palavras-chave.
        
        Returns:
            Dicionário com categorias e suas configurações
        """
        return self.KEYWORD_CATEGORIES.copy()
    
    def get_category_words(self, category: str) -> List[str]:
        """Retorna palavras de uma categoria específica.
        
        Args:
            category: Nome da categoria
            
        Returns:
            Lista de palavras da categoria
        """
        if category in self.KEYWORD_CATEGORIES:
            return self.KEYWORD_CATEGORIES[category]["words"].copy()
        return []

if __name__ == "__main__":
    # Exemplo de uso
    highlighter = KeywordHighlighter()
    
    # Teste de detecção automática
    text1 = "Let's CREATE something AMAZING and BUILD the future!"
    print("Texto original:", text1)
    print("Keywords detectadas:", highlighter.detect_keywords(text1))
    print("ASS tags:", highlighter.generate_ass_tags(text1))
    print()
    
    # Teste de marcação manual
    text2 = "This is a {SPECIAL:blue} moment to {CELEBRATE:green}!"
    print("Texto com marcação:", text2)
    clean, highlights = highlighter.parse_manual_markup(text2)
    print("Texto limpo:", clean)
    print("Highlights manuais:", highlights)
    print("ASS tags:", highlighter.generate_ass_tags(text2, auto_detect=False))
    print()
    
    # Teste combinado
    text3 = "Let's {CREATE:purple} something NEW and AMAZING!"
    print("Texto combinado:", text3)
    print("ASS tags:", highlighter.generate_ass_tags(text3))
    print()
    
    # Mostrar categorias disponíveis
    print("Categorias disponíveis:")
    for cat, config in highlighter.get_available_categories().items():
        print(f"  {cat}: {config['description']} ({config['color']})")
        print(f"    Palavras: {', '.join(config['words'][:5])}...")