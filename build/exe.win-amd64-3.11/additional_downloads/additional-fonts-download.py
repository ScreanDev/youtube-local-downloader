import os
import win32api
import matplotlib.font_manager
import ctypes
import win32con
import shutil


root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SCRIPT À MODIFIER. DES ERREURS SE PRODUISENT.
def is_font_installed(font_name):
    temp_dir = os.path.join(os.environ['TEMP'], 'temp_fonts')
    available_fonts = matplotlib.font_manager.findSystemFonts(fontpaths=temp_dir)
    for font_path in available_fonts:
        font_info = matplotlib.font_manager.FontProperties(fname=font_path)
        if str(font_info.get_name().lower()) == font_name.lower():
            return True
    return False


def install_font(font_path, font_name):
    if not os.path.exists(font_path):
        print("ERROR: Specified font-file path doesn't exist.")
        return

    font_filename = os.path.basename(font_path)
    
    if is_font_installed(font_name):
        print(f"Font {font_filename} is already downloaded on this device.")
        return


    try:
        temp_dir = os.path.join(os.environ['TEMP'], 'temp_fonts')
        os.makedirs(temp_dir, exist_ok=True)

        shutil.copy(font_path, temp_dir)

        temp_font_path = os.path.join(temp_dir, font_filename)

        ctypes.windll.gdi32.AddFontResourceW(temp_font_path)

        print("Successful installation.")
    
    except Exception as e:
        print(f"An error has occurred when trying to download resource from: {font_path}\n\n{e}")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


fonts_dict = {os.path.join(root_dir, "fonts", "a-big-deal.ttf"): "a Big Deal",
              os.path.join(root_dir, "fonts", "comixo-regular.otf"): "Comixo",
              os.path.join(root_dir, "fonts", "made-soulmaze.otf"): "MADE Soulmaze",
              os.path.join(root_dir, "fonts", "nexa-heavy.ttf"): "Nexa"}


for font in fonts_dict:
    install_font(font, fonts_dict[font])