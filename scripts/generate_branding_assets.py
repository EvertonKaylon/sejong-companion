"""
Gerador de Assets de Marca — Saebom Companion (새봄 컴패니언)
Baseado estritamente no Branding Book Oficial v3.1 (Setembro 2026).

Gera:
- Logotipo Principal Dark (SVG, PNG transparente, PNG com fundo Navy)
- Logotipo Negativo Light (SVG, PNG transparente, PNG com fundo Cream)
- Logotipo Horizontal Dark & Light (SVG, PNG transparente, PNG com fundo sólido)
- Símbolo Anéis Concêntricos de Expansão (SVG, PNG)
- Ícone do Aplicativo (App Icon 512, 192, SVG)
- Favicons Web (32x32, 16x16, favicon.ico multi-resolução)
- Splash Banner Vertical (1080x1920 para Mobile/PWA)
"""

import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

# Garantir saída UTF-8 no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# -------------------------------------------------------------
# TOKENS CROMÁTICOS OFICIAIS (BRANDING BOOK v3.1)
# -------------------------------------------------------------
NAVY_HEX = "#02060F"
VIOLET_HEX = "#8B4DFF"
GOLD_HEX = "#FFAB22"
LILAC_HEX = "#B28AFF"
CREAM_HEX = "#F7F4EC"
SLATE_HEX = "#9EA2AE"
WHITE_HEX = "#FFFFFF"

# Tuplas RGBA para o Pillow
NAVY = (2, 6, 15, 255)
VIOLET = (139, 77, 255, 255)
GOLD = (255, 171, 34, 255)
LILAC = (178, 138, 255, 255)
CREAM = (247, 244, 236, 255)
SLATE = (158, 162, 174, 255)
WHITE = (255, 255, 255, 255)
TRANSPARENT = (0, 0, 0, 0)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "branding")
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")

FONT_BOLD = os.path.join(FONTS_DIR, "Pretendard-Bold.otf")
FONT_MEDIUM = os.path.join(FONTS_DIR, "Pretendard-Medium.otf")
FONT_REGULAR = os.path.join(FONTS_DIR, "Pretendard-Regular.otf")


def ensure_dir():
    os.makedirs(ASSETS_DIR, exist_ok=True)


# -------------------------------------------------------------
# 1. GERADORES DE LOGOTIPO VETORIAL (SVG)
# -------------------------------------------------------------
def generate_logo_dark_svg(filename: str):
    """Gera o logotipo vertical principal para fundos escuros (SVG)."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500">
  <defs>
    <style>
      @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
      .hangul {{ font-family: 'Pretendard', 'NanumSquare', -apple-system, sans-serif; font-weight: 800; font-size: 110px; fill: {WHITE_HEX}; text-anchor: middle; letter-spacing: 4px; }}
      .companion {{ font-family: 'Pretendard', 'NanumSquare', sans-serif; font-weight: 700; font-size: 26px; fill: {GOLD_HEX}; text-anchor: middle; letter-spacing: 14px; }}
      .sub {{ font-family: 'Pretendard', 'NanumBarunGothic', sans-serif; font-weight: 500; font-size: 16px; fill: {SLATE_HEX}; text-anchor: middle; letter-spacing: 8px; }}
    </style>
  </defs>
  <!-- Texto Hangul Principal -->
  <text x="400" y="210" class="hangul">새봄</text>
  <!-- Descriptor de Categoria -->
  <text x="407" y="280" class="companion">COMPANION</text>
  <!-- Assinatura Verbal Latina -->
  <text x="404" y="330" class="sub">SAEBOM COMPANION</text>
</svg>"""
    with open(os.path.join(ASSETS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(svg)


def generate_logo_light_svg(filename: str):
    """Gera o logotipo vertical negativo para fundos claros (SVG)."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500">
  <defs>
    <style>
      @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
      .hangul {{ font-family: 'Pretendard', 'NanumSquare', -apple-system, sans-serif; font-weight: 800; font-size: 110px; fill: {NAVY_HEX}; text-anchor: middle; letter-spacing: 4px; }}
      .companion {{ font-family: 'Pretendard', 'NanumSquare', sans-serif; font-weight: 700; font-size: 26px; fill: {VIOLET_HEX}; text-anchor: middle; letter-spacing: 14px; }}
      .sub {{ font-family: 'Pretendard', 'NanumBarunGothic', sans-serif; font-weight: 500; font-size: 16px; fill: {SLATE_HEX}; text-anchor: middle; letter-spacing: 8px; }}
    </style>
  </defs>
  <!-- Texto Hangul Principal -->
  <text x="400" y="210" class="hangul">새봄</text>
  <!-- Descriptor de Categoria -->
  <text x="407" y="280" class="companion">COMPANION</text>
  <!-- Assinatura Verbal Latina -->
  <text x="404" y="330" class="sub">SAEBOM COMPANION</text>
</svg>"""
    with open(os.path.join(ASSETS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(svg)


def generate_logo_horizontal_svg(filename: str, is_dark: bool = True):
    """Gera a assinatura horizontal da marca (새봄 | COMPANION / SAEBOM COMPANION)."""
    hangul_color = WHITE_HEX if is_dark else NAVY_HEX
    comp_color = GOLD_HEX if is_dark else VIOLET_HEX
    sub_color = LILAC_HEX if is_dark else SLATE_HEX
    line_color = VIOLET_HEX if is_dark else SLATE_HEX

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 160" width="720" height="160">
  <defs>
    <style>
      @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
      .hangul {{ font-family: 'Pretendard', 'NanumSquare', sans-serif; font-weight: 800; font-size: 64px; fill: {hangul_color}; text-anchor: start; }}
      .companion {{ font-family: 'Pretendard', 'NanumSquare', sans-serif; font-weight: 700; font-size: 18px; fill: {comp_color}; text-anchor: start; letter-spacing: 8px; }}
      .sub {{ font-family: 'Pretendard', 'NanumBarunGothic', sans-serif; font-weight: 500; font-size: 12px; fill: {sub_color}; text-anchor: start; letter-spacing: 4px; }}
    </style>
  </defs>
  <!-- Bloco Hangul -->
  <text x="40" y="102" class="hangul">새봄</text>
  <!-- Linha Divisória Hairline -->
  <line x1="200" y1="45" x2="200" y2="115" stroke="{line_color}" stroke-width="2" opacity="0.6"/>
  <!-- Bloco Categoria & Assinatura Latina -->
  <text x="230" y="75" class="companion">COMPANION</text>
  <text x="230" y="105" class="sub">SAEBOM COMPANION</text>
</svg>"""
    with open(os.path.join(ASSETS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(svg)


def generate_expansion_rings_svg(filename: str):
    """Gera os anéis concêntricos de expansão (símbolo oficial do Brand Book)."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <g transform="translate(200, 200)">
    <!-- Anel 4 (Externo - Violet) -->
    <path d="M 0 -130 A 130 130 0 1 1 -112.5 65" fill="none" stroke="{VIOLET_HEX}" stroke-width="14" stroke-linecap="round"/>
    <!-- Anel 3 (Médio-Externo - Lilac) -->
    <path d="M 0 -95 A 95 95 0 1 1 -82.2 47.5" fill="none" stroke="{LILAC_HEX}" stroke-width="14" stroke-linecap="round"/>
    <!-- Anel 2 (Médio-Interno - Gold) -->
    <path d="M 0 -60 A 60 60 0 1 1 -51.9 30" fill="none" stroke="{GOLD_HEX}" stroke-width="14" stroke-linecap="round"/>
    <!-- Núcleo (Ponto de Broto / Semente) -->
    <circle cx="0" cy="0" r="18" fill="{GOLD_HEX}"/>
  </g>
</svg>"""
    with open(os.path.join(ASSETS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(svg)


def generate_app_icon_svg(filename: str):
    """Gera o SVG do ícone do aplicativo com squircle e o monograma 새."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="iconBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8B4DFF"/>
      <stop offset="100%" stop-color="#5A1FFF"/>
    </linearGradient>
    <style>
      @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
      .iconGlyph {{ font-family: 'Pretendard', 'NanumSquare', sans-serif; font-weight: 800; font-size: 260px; fill: #FFFFFF; text-anchor: middle; dominant-baseline: central; }}
    </style>
  </defs>
  <!-- Squircle com raio suave 24% -->
  <rect x="0" y="0" width="512" height="512" rx="120" ry="120" fill="url(#iconBg)"/>
  <!-- Glifo Monograma 새 -->
  <text x="256" y="256" class="iconGlyph">새</text>
</svg>"""
    with open(os.path.join(ASSETS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(svg)


# -------------------------------------------------------------
# 2. GERADORES DE IMAGEM RASTERIZADA (PILLOW SUPERSAMPLED)
# -------------------------------------------------------------
def render_logo_png(filename: str, is_dark: bool = True, with_bg: bool = False):
    """Renderiza o logotipo vertical em alta definição com supersampling 2x."""
    scale = 2
    w, h = 1000 * scale, 600 * scale

    bg_color = TRANSPARENT
    if with_bg:
        bg_color = NAVY if is_dark else CREAM

    img = Image.new("RGBA", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    f_hangul = ImageFont.truetype(FONT_BOLD, 130 * scale)
    f_comp = ImageFont.truetype(FONT_BOLD, 30 * scale)
    f_sub = ImageFont.truetype(FONT_MEDIUM, 18 * scale)

    hangul_color = WHITE if is_dark else NAVY
    comp_color = GOLD if is_dark else VIOLET
    sub_color = SLATE

    # 1. 새봄
    text_hangul = "새봄"
    bbox_h = f_hangul.getbbox(text_hangul)
    tw_h = bbox_h[2] - bbox_h[0]
    x_h = (w - tw_h) // 2 - bbox_h[0]
    y_h = int(140 * scale)
    draw.text((x_h, y_h), text_hangul, font=f_hangul, fill=hangul_color)

    # 2. C O M P A N I O N (espaçado)
    text_comp = "C  O  M  P  A  N  I  O  N"
    bbox_c = f_comp.getbbox(text_comp)
    tw_c = bbox_c[2] - bbox_c[0]
    x_c = (w - tw_c) // 2 - bbox_c[0]
    y_c = int(320 * scale)
    draw.text((x_c, y_c), text_comp, font=f_comp, fill=comp_color)

    # 3. S A E B O M   C O M P A N I O N
    text_sub = "S A E B O M   C O M P A N I O N"
    bbox_s = f_sub.getbbox(text_sub)
    tw_s = bbox_s[2] - bbox_s[0]
    x_s = (w - tw_s) // 2 - bbox_s[0]
    y_s = int(390 * scale)
    draw.text((x_s, y_s), text_sub, font=f_sub, fill=sub_color)

    final = img.resize((1000, 600), Image.Resampling.LANCZOS)
    final.save(os.path.join(ASSETS_DIR, filename))


def render_logo_horizontal_png(filename: str, is_dark: bool = True, with_bg: bool = False):
    """Renderiza a assinatura horizontal em alta definição."""
    scale = 2
    w, h = 900 * scale, 220 * scale

    bg_color = TRANSPARENT
    if with_bg:
        bg_color = NAVY if is_dark else CREAM

    img = Image.new("RGBA", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    f_hangul = ImageFont.truetype(FONT_BOLD, 80 * scale)
    f_comp = ImageFont.truetype(FONT_BOLD, 22 * scale)
    f_sub = ImageFont.truetype(FONT_MEDIUM, 14 * scale)

    hangul_color = WHITE if is_dark else NAVY
    comp_color = GOLD if is_dark else VIOLET
    sub_color = LILAC if is_dark else SLATE
    line_color = VIOLET if is_dark else SLATE

    # 새봄
    draw.text((int(50 * scale), int(60 * scale)), "새봄", font=f_hangul, fill=hangul_color)

    # Linha vertical
    draw.line(
        [(int(260 * scale), int(60 * scale)), (int(260 * scale), int(160 * scale))],
        fill=(line_color[0], line_color[1], line_color[2], 160),
        width=int(2 * scale),
    )

    # COMPANION
    draw.text((int(290 * scale), int(75 * scale)), "C O M P A N I O N", font=f_comp, fill=comp_color)
    # SAEBOM COMPANION
    draw.text((int(290 * scale), int(120 * scale)), "SAEBOM COMPANION", font=f_sub, fill=sub_color)

    final = img.resize((900, 220), Image.Resampling.LANCZOS)
    final.save(os.path.join(ASSETS_DIR, filename))


def render_expansion_rings_png(filename: str, size: int = 512):
    """Renderiza o símbolo de anéis de expansão concêntricos em alta precisão."""
    scale = 3
    s = size * scale
    img = Image.new("RGBA", (s, s), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    cx, cy = s // 2, s // 2

    # Desenha arcos concêntricos abertos
    # Outer (Violet)
    r4 = int(170 * scale)
    bbox4 = [cx - r4, cy - r4, cx + r4, cy + r4]
    draw.arc(bbox4, start=-90, end=150, fill=VIOLET, width=int(18 * scale))

    # Mid-outer (Lilac)
    r3 = int(125 * scale)
    bbox3 = [cx - r3, cy - r3, cx + r3, cy + r3]
    draw.arc(bbox3, start=-90, end=150, fill=LILAC, width=int(18 * scale))

    # Mid-inner (Gold)
    r2 = int(80 * scale)
    bbox2 = [cx - r2, cy - r2, cx + r2, cy + r2]
    draw.arc(bbox2, start=-90, end=150, fill=GOLD, width=int(18 * scale))

    # Center dot (Gold)
    r1 = int(24 * scale)
    draw.ellipse([cx - r1, cy - r1, cx + r1, cy + r1], fill=GOLD)

    final = img.resize((size, size), Image.Resampling.LANCZOS)
    final.save(os.path.join(ASSETS_DIR, filename))


def render_app_icon(size: int = 512) -> Image.Image:
    """Cria a imagem do ícone do app em alta fidelidade com cantos arredondados e glifo 새."""
    scale = 2
    s = size * scale
    img = Image.new("RGBA", (s, s), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Gradiente vertical suave do squircle
    top_color = (139, 77, 255)   # #8B4DFF (Violet)
    bot_color = (90, 31, 255)    # #5A1FFF (Deep Violet)

    grad = Image.new("RGBA", (s, s))
    grad_draw = ImageDraw.Draw(grad)
    for y in range(s):
        ratio = y / s
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * ratio)
        grad_draw.line([(0, y), (s, y)], fill=(r, g, b, 255))

    # Máscara do Squircle (raio 24%)
    mask = Image.new("L", (s, s), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = int(s * 0.235)
    mask_draw.rounded_rectangle([0, 0, s, s], radius=radius, fill=255)

    img.paste(grad, (0, 0), mask)

    # Glifo Monograma 새 em Branco puro
    font_size = int(size * 0.52 * scale)
    font = ImageFont.truetype(FONT_BOLD, font_size)
    bbox = font.getbbox("새")
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    gx = (s - tw) // 2 - bbox[0]
    gy = (s - th) // 2 - bbox[1]

    draw = ImageDraw.Draw(img)
    draw.text((gx, gy), "새", font=font, fill=(255, 255, 255, 255))

    final = img.resize((size, size), Image.Resampling.LANCZOS)
    return final


def render_splash_banner_png(filename: str):
    """Renderiza banner vertical (1080x1920) para splash / loading / mobile cover com elegância editorial."""
    w, h = 1080, 1920
    img = Image.new("RGBA", (w, h), NAVY)
    draw = ImageDraw.Draw(img)

    # 1. Grid editorial sutilíssimo (estilo Blueprint / Kyobo)
    grid_size = 72
    grid_color = (25, 35, 60, 255)
    for x in range(0, w, grid_size):
        draw.line([(x, 0), (x, h)], fill=grid_color, width=1)
    for y in range(0, h, grid_size):
        draw.line([(0, y), (w, y)], fill=grid_color, width=1)

    # 2. Anéis concêntricos de expansão (símbolo oficial Saebom) no quadrante superior
    cx, cy = w // 2, 480
    for radius, stroke_w, color in [
        (240, 14, (139, 77, 255, 220)),   # Violet
        (175, 14, (178, 138, 255, 230)),  # Lilac
        (110, 14, (255, 171, 34, 240)),   # Gold
    ]:
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        draw.arc(bbox, start=-90, end=150, fill=color, width=stroke_w)
    
    # Núcleo semente dourado
    draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(255, 171, 34, 255))

    # 3. Logo Badge central
    f_hangul = ImageFont.truetype(FONT_BOLD, 130)
    f_comp = ImageFont.truetype(FONT_BOLD, 30)
    f_sub = ImageFont.truetype(FONT_MEDIUM, 18)
    f_quote = ImageFont.truetype(FONT_REGULAR, 22)

    # 새봄
    bbox_h = f_hangul.getbbox("새봄")
    draw.text(((w - (bbox_h[2] - bbox_h[0])) // 2 - bbox_h[0], 920), "새봄", font=f_hangul, fill=WHITE)

    # C O M P A N I O N
    text_c = "C  O  M  P  A  N  I  O  N"
    bbox_c = f_comp.getbbox(text_c)
    draw.text(((w - (bbox_c[2] - bbox_c[0])) // 2 - bbox_c[0], 1100), text_c, font=f_comp, fill=GOLD)

    # SAEBOM COMPANION
    text_s = "SAEBOM COMPANION"
    bbox_s = f_sub.getbbox(text_s)
    draw.text(((w - (bbox_s[2] - bbox_s[0])) // 2 - bbox_s[0], 1165), text_s, font=f_sub, fill=SLATE)

    # Citação da professora no rodapé com moldura fina
    quote = "“Uma nova primavera para a aprendizagem.”"
    bbox_q = f_quote.getbbox(quote)
    draw.text(((w - (bbox_q[2] - bbox_q[0])) // 2 - bbox_q[0], 1680), quote, font=f_quote, fill=(158, 162, 174, 200))

    img.save(os.path.join(ASSETS_DIR, filename))


def main():
    ensure_dir()
    print("🎨 Gerando pacote de branding Saebom Companion...")

    # 1. SVGs
    generate_logo_dark_svg("saebom_logo_dark.svg")
    generate_logo_light_svg("saebom_logo_light.svg")
    generate_logo_horizontal_svg("saebom_logo_horizontal_dark.svg", is_dark=True)
    generate_logo_horizontal_svg("saebom_logo_horizontal_light.svg", is_dark=False)
    generate_expansion_rings_svg("symbol_expansion_rings.svg")
    generate_app_icon_svg("app_icon.svg")
    print("  ✓ SVGs gerados com sucesso.")

    # 2. Logotipos PNG
    render_logo_png("saebom_logo_dark.png", is_dark=True, with_bg=False)
    render_logo_png("saebom_logo_dark_solid.png", is_dark=True, with_bg=True)
    render_logo_png("saebom_logo_light.png", is_dark=False, with_bg=False)
    render_logo_png("saebom_logo_light_solid.png", is_dark=False, with_bg=True)
    render_logo_horizontal_png("saebom_logo_horizontal_dark.png", is_dark=True, with_bg=False)
    render_logo_horizontal_png("saebom_logo_horizontal_dark_solid.png", is_dark=True, with_bg=True)
    render_logo_horizontal_png("saebom_logo_horizontal_light.png", is_dark=False, with_bg=False)
    render_logo_horizontal_png("saebom_logo_horizontal_light_solid.png", is_dark=False, with_bg=True)
    render_expansion_rings_png("symbol_expansion_rings.png", size=512)
    print("  ✓ Logotipos e grafismos PNG renderizados com supersampling.")

    # 3. Ícones do Aplicativo e Favicons
    icon_512 = render_app_icon(512)
    icon_512.save(os.path.join(ASSETS_DIR, "app_icon_512.png"))

    icon_192 = render_app_icon(192)
    icon_192.save(os.path.join(ASSETS_DIR, "app_icon_192.png"))

    favicon_32 = render_app_icon(32)
    favicon_32.save(os.path.join(ASSETS_DIR, "favicon_32.png"))

    favicon_16 = render_app_icon(16)
    favicon_16.save(os.path.join(ASSETS_DIR, "favicon_16.png"))

    # Multi-resolution ICO (16, 32, 48, 64, 128, 256)
    icon_512.save(
        os.path.join(ASSETS_DIR, "favicon.ico"),
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    )
    print("  ✓ Pacote de App Icons (512, 192) e Favicon (.ico, 32, 16) gerados.")

    # 4. Splash Banner
    render_splash_banner_png("splash_banner.png")
    print("  ✓ Splash banner Full HD (1080x1920) renderizado.")

    print(f"\n✨ Todos os assets foram salvos em: {ASSETS_DIR}")


if __name__ == "__main__":
    main()
