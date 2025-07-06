from PIL import Image, ImageDraw, ImageFont, ImageOps
from unidecode import unidecode
import os
import io

parentPath = os.path.dirname(os.path.abspath(__file__))

TEMPLATE_PATH = os.path.join(parentPath, "assets/wanted_template.png")
FONT_PATH = os.path.join(parentPath, "assets/font.ttf")
CHARACTER_DIR = os.path.join(parentPath, "assets", "characters")
TEXT_COLOR = (0, 0, 0)

def fit_text(draw, text, font_path, max_width, max_font_size):
    font_size = max_font_size
    while font_size > 10:
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            return font
        font_size -= 1
    return ImageFont.truetype(font_path, 10)

def create_wanted_poster(player_wanted, character, reward, contact_display):
    # Formatage
    player_text = unidecode(player_wanted).upper()
    reward_text = f"GAIN: {unidecode(reward).upper()}"
    contact_text = f"CONTACTEZ {unidecode(contact_display).upper()}"

    image = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(image)

    # Largeurs autorisées
    max_width = 672  # 777 - 105
    center_x = 443

    # Positionnements verticaux
    player_y = 400
    reward_y = 1000
    contact_y = 1190
    contact_max_width = 500  # 600 - 260

    # Fonts adaptés
    player_font = fit_text(draw, player_text, FONT_PATH, max_width, max_font_size=200)
    reward_font = fit_text(draw, reward_text, FONT_PATH, max_width, max_font_size=200)
    contact_font = fit_text(draw, contact_text, FONT_PATH, contact_max_width, max_font_size=150)

    # Dessin des textes centrés
    def draw_centered(text, y, font, center_x, color=TEXT_COLOR):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text((center_x - text_width // 2, y), text, font=font, fill=color)

    draw_centered(player_text, player_y, player_font, center_x, (255, 0, 0))
    
    character_path = os.path.join(CHARACTER_DIR, f"{character.lower().replace(' / ',' ').replace('.','')}.png")
    if os.path.exists(character_path):
        char_img = Image.open(character_path).convert("RGBA")

        # Séparation des canaux
        r, g, b, a = char_img.split()

        # Convertir l’image en niveaux de gris
        gray_rgb = Image.merge("RGB", (r, g, b)).convert("L")

        # Recomposer en RGBA avec l’alpha d’origine
        char_img_bw = Image.merge("RGBA", (gray_rgb, gray_rgb, gray_rgb, a))

        # Calcul du redimensionnement
        max_height = 650  # de 500 à 1020px
        char_w, char_h = char_img_bw.size
        scale = max_height / char_h
        new_width = int(char_w * scale)
        new_height = int(char_h * scale)
        char_img_bw = char_img_bw.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Centrage horizontal
        pos_x = center_x - new_width // 2
        pos_y = 500  # position verticale de départ

        # Collage avec transparence
        image.paste(char_img_bw, (pos_x, pos_y), mask=char_img_bw)
            
    draw_centered(reward_text, reward_y, reward_font, center_x, (255, 0, 0))
    draw_centered(contact_text, contact_y, contact_font, center_x)

    # Output en bytes
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output
