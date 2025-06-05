# IMPORTATION DES LIBRAIRES NÉCESSAIRES
from pytube import YouTube # Utilise les outils de recherche de vidéos YouTube et de leur téléchargement
from pydub import AudioSegment # Utilise les outils d'extraction vers le format audio de fichiers
from tkinter import * # Permet la création, l'affichage et les propriétés de la fenêtre
from tkinter import filedialog, Tk, Label # Permet d'utiliser des ressources dérivées de la librarie Tkinter
from tkinter.messagebox import * # Permet d'utiliser les boîtes de messages au sein de la fenêtre
import tkinter as tk # Importe Tkinter au nom de "tk"
from PIL import Image, ImageTk # Permet d'utiliser des icônes au sein de la fenêtre
import pygame # Importe la librairie Pygame, ici utilisée notamment pour gérer le contenu audio de la fenêtre
import time # Gère les notions de délai
import sys # Importe certaines fonctions liées au système-même - librairie utilisée ici principalement pour permettre l'ouverture du fichier menant au site HTML
import subprocess # Permet la réalisation de tâches en arrière-plan
import os # Importe certaines fonctions liées au système-même
import webbrowser # Gère les notions liées à l'exploitation des fichiers menant aux sites web
import json # Permet l'exploitation des fichiers au format JSON
import requests # Permet de faire des requêtes au sein d'une API, ici utilisée pour la récupération de vidéos TikTok
"""import TikTokApi # Utilise l'API de TikTok et fournit des outils de recherche de vidéos TikTok
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import re"""

# IMPORTATION DE DONNÉES DE FICHIERS LOCAUX -------------------------------------------------------------------------------------
from version import app_version # Importation de la version de l'application
from patchnotes import last_update_string, patchnotes_list # Importation des notes de patch de l'application
from settings import Settings


# INITIALISATION DES VARIABLES ET PARAMÈTRES DE LA FENÊTRE ----------------------------------------------------------------------
output_folder_ask = "" # Stocke le dossier vers lequel télécharger
window_exists = True # Vaut "True" si la fenêtre de l'outil est active
content_queue = [] # Liste des contenus à télécharger
videos_download_errors_list = [] # Liste des erreurs survenues lors du téléchargement
application_type = "youtube"

# CRÉATION DE LA FENÊTRE PRINCIPALE ---------------------------------------------------------------------------------------------
root = Tk() # Crée la fenêtre au nom de "root"
root.title("YouTube Local Downloader") # Titre de la fenêtre
root.iconbitmap("ytb_converter_icon_ico_format.ico") # Icône de la fenêtre

screen_width = root.winfo_screenwidth() # Longueur de l'écran
screen_height = root.winfo_screenheight() # Hauteur de l'écran

root_width = round((1080*screen_width)/1920) # Longueur de la fenêtre en fonction de celle de l'écran
root_height = round((520*screen_height)/1080) # Hauteur de la fenêtre en fonction de celle de l'écran
root.geometry(f"{root_width}x{root_height}") # Définit les dimensions de la fenêtre

root.resizable(False, False) # Empêche le redimensionnement de la fenêtre
root['bg']="#FFFFFF" # Couleur de fond de la fenêtre


# CRÉATION DES ICÔNES -----------------------------------------------------------------------------------------------------------

# Icône : Dossier valide
img = Image.open("images/folder_valid.png")
img = img.resize((round((40*screen_width)/1920), round((40*screen_height)/1080)))
folder_valid_icon = ImageTk.PhotoImage(img)

# Icône : Dossier invalide
img = Image.open("images/folder_invalid.png")
img = img.resize((round((40*screen_width)/1920), round((40*screen_height)/1080)))
folder_invalid_icon = ImageTk.PhotoImage(img)

# Icône : Recherche
img = Image.open("images/search_magnificient_glass.png")
img = img.resize((round((50*screen_width)/1920), round((50*screen_height)/1080)))
search_icon = ImageTk.PhotoImage(img)

# Icône : Bouton de téléchargement
img = Image.open("images/download_button.png")
img = img.resize((round((150*screen_width)/1920), round((50*screen_height)/1080)))
download_icon = ImageTk.PhotoImage(img)

# Icône : Ajout à la file
img = Image.open("images/add_to_queue.png")
img = img.resize((round((50*screen_width)/1920), round((50*screen_height)/1080)))
add_to_queue_icon = ImageTk.PhotoImage(img)


# FONCTIONS ---------------------------------------------------------------------------------------------------------------------

pygame.init() # Initialise PyGame pour jouer du son par la suite


def check_ffmpeg_installed():
    global ffmpeg_installed
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        ffmpeg_installed = True
    except subprocess.CalledProcessError:
        ffmpeg_installed = False


# Permet de collecter une donnée d'un fichier JSON selon le chemin d'accès spécifié dans "file_path" et la clé associée à la valeur à chercher
def get_json_data(file_path, datakey=None):
    '''Collects data from a file specified in "file_path", either according to a key specified in "datakey", either collecting the whole file data.'''
    with open(file_path, "r") as f:
        data = json.load(f)
    if datakey != None:
        return data[datakey]
    else:
        return data


# Permet de modifier une donnée d'un fichier JSON selon le chemin d'accès spécifié dans "file_path" et la clé associée à la valeur à modifier
def edit_json_data(filepath, datakey, new_value):
    '''Edits data from a file specified in "file_path" according to a key specified in "datakey".'''
    data = get_json_data(filepath)
    data[datakey] = new_value
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def execute_file(filepath):
    subprocess.run(["python", filepath])


def reset_settings():
    edit_json_data("user_data/settings-user-data.json", "isConfigured", "False")
    edit_json_data("user_data/settings-user-data.json", "TermsOfUseUserAgreement", "False")
    edit_json_data("user_data/settings-user-data.json", "additionalFontsDownload", "True")
    edit_json_data("user_data/settings-user-data.json", "defaultOutputFolder", "")
    edit_json_data("user_data/settings-user-data.json", "sfx", "True")
    edit_json_data("user_data/settings-user-data.json", "renameFilesToDefaultFormat", "False")


def play_sound(path):
    if get_json_data("user_data/settings-user-data.json", "sfx") == "True":
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()


# Ouvre le fichier HTML de la page web de l'outil, avec la librairie Webbrowser
def open_readme_webpage():
    '''Opens the tool web page file using the "Webbrowser" library.'''
    current_dir = os.path.dirname(sys.argv[0])
    readme_dir = os.path.join(current_dir, "readme")
    readme_file_path = os.path.join(readme_dir, "index.html")

    webbrowser.open("file://" + readme_file_path)


# Ouvre le fichier HTML de la page web du guide de téléchargement de FFMPEG, avec la librairie Webbrowser
def open_install_ffmpeg_webpage():
    '''Opens the FFMPEG-download-guide web page file using the "Webbrowser" library.'''
    current_dir = os.path.dirname(sys.argv[0])
    readme_dir = os.path.join(current_dir, "readme")
    readme_file_path = os.path.join(readme_dir, "download-ffmpeg.html")

    webbrowser.open("file://" + readme_file_path)



# Ouvre l'explorateur de fichiers et permet à l'utilisateur de sélectionner un dossier vers lequel télécharger
def open_folder_dialog():
    '''Opens the directories windows and asks the user to choose a folder to download to.'''
    global output_folder_ask
    output_folder_ask = filedialog.askdirectory()
    
    play_sound("sound/select.ogg")

    if output_folder_ask == "":
        path_entry.config(image=folder_invalid_icon)
        path_entry_widget.config(text=f"Dossier vers lequel télécharger : Aucun dossier sélectionné")
    else:
        path_entry.config(image=folder_valid_icon)
        path_entry_widget.config(text=f"Dossier vers lequel télécharger : {output_folder_ask}")


# Ouvre l'explorateur de fichiers et permet à l'utilisateur de sélectionner un dossier vers lequel télécharger. Fonction spécifique à la configuration de l'outil
def open_folder_dialog_first_use():
    global first_use_default_folder_desctext_widget2
    '''Opens the directories windows and asks the user to choose a folder to download to. Used when initializing the tool.'''
    global output_folder_ask
    output_folder_ask = filedialog.askdirectory()
    
    play_sound("sound/select.ogg")

    if output_folder_ask == "":
        first_use_default_folder_desctext_widget2.config(text=f"Aucun dossier spécifique sélectionné.")
        edit_json_data("user_data/settings-user-data.json", "defaultOutputFolder", "")
    else:
        first_use_default_folder_desctext_widget2.config(text=f"Dossier : {output_folder_ask}")
        edit_json_data("user_data/settings-user-data.json", "defaultOutputFolder", output_folder_ask)



# Ouvre, à la fin du téléchargement, le dossier vers lequel les contenus ont été téléchargés
def open_file_folder():
    """Uses \"OS\" library to open the folder where content has been downloaded."""
    global output_folder_ask
    normalized_path = os.path.normpath(output_folder_ask)
    subprocess.Popen(['explorer', normalized_path])

    play_sound("sound/select.ogg")



# Gère le système de file pour ajouter les objets à télécharger - ajoute dans la file, si trouvée, le nom et l'URL de la vidéo
def add_to_queue():
    '''Adds to a queue (list variable called "content_queue"), if found, the name and URL of a video to download later.'''
    global youtube_video
    global url_ask
    global downloads_list_headtext_widget
    
    for element_url in content_queue: # Permet d'éviter les répétitions en vérifiant si le contenu à ajouter n'est pas déjà présent dans la file
        if url_ask == element_url[1]:
            return
    
    if youtube_video.length > 600:
        if not(askyesno("Taille de vidéo importante", "La vidéo que vous vous apprêtez à ajouter à la file d'attente dépasse 10 minutes et risque d'occuper de la place sur le stockage. Voulez-vous continuer ?")):
            return
        
    content_queue.append([youtube_video.title, url_ask])
    downloads_list_widget_text = "Liste des vidéos à télécharger :\n\n"
    for element in content_queue:
        downloads_list_widget_text = f"{downloads_list_widget_text}\n• {element[0]}"
    downloads_list_headtext_widget.config(text=downloads_list_widget_text)
    play_sound("sound/select.ogg")



# Recherche si le lien renseigné correspond à une vidéo sur YouTube, et vérifie également si le dossier de téléchargement est bien inscrit
def search_for_results():
    '''Searches if the URL entered is associated to a YouTube video, and checks if the downloading folder is valid.'''
    # Variables globales
    global url_ask
    global output_folder_ask
    global video_info_label
    global mp3_selected
    global mp4_selected
    global download_button_frame
    global video_error_label
    global add_to_queue_button

    # Vérifie si les cases MP4 / MP3 sont cochées et modifie leurs variables associées en conséquence
    url_ask = ytb_link_entry.get()
    mp3_format_checkbox_var_check = mp3_format_checkbox_var.get()
    mp4_format_checkbox_var_check = mp4_format_checkbox_var.get()
    # Case MP3
    if mp3_format_checkbox_var_check == 1:
        mp3_selected = True
    else:
        mp3_selected = False
    # Case MP4
    if mp4_format_checkbox_var_check == 1:
        mp4_selected = True
    else:
        mp4_selected = False
    print(url_ask, output_folder_ask)

    # Efface le label des informations sur la vidéo s'il existe déjà dans la fenêtre
    try:
        video_info_label.destroy()
    except:
        pass

    # Vérifie si l'entrée de lien est vide, et envoie un message d'erreur le cas échéant
    if url_ask == "":
        video_info_label = Label(root, text=f"Inscrivez le lien d'une vidéo à télécharger.", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((12*screen_height)/1080)))
        video_info_label.place(x=round((25*screen_width)/1920), y=round((300*screen_height)/1080))
        try:
            add_to_queue_button.destroy()
        except:
            pass
        play_sound("sound/warning.ogg")
        return

    if application_type == "youtube":
        # RECHERCHE SI TOUTES LES ENTRÉES SONT CORRECTEMENT INSCRITES, ET AFFICHE UN MESSAGE D'ERREUR DANS LA FENÊTRE SI CE N'EST PAS LE CAS
        try:
            # Crée un objet "youtube_video" de la classe "YouTube", correspondant à la vidéo cherchée, et répertoriant toutes ses informations
            global youtube_video
            youtube_video = YouTube(url_ask) # Recherche la vidéo avec le lien fourni dans "url_ask" pour que "youtube_video" soit un objet de la classe "YouTube"
            try:
                video_error_label.destroy() # Efface le label d'erreur s'il existe déjà dans la fenêtre
            except:
                pass
        

            # SI L'OBJET VIDÉO N'EST PAS VIDE ET QUE LE DOSSIER VERS LEQUEL TÉLÉCHARGER EST SÉLECTIONNÉ, AFFICHE LES INFORMATIONS DE LA VIDÉO DANS LA FENÊTRE SELON LES FORMATS COCHÉS (MP4 / MP3)
            if output_folder_ask != "" and youtube_video != "":
                if mp3_selected == False:
                    video_info_label = Label(root, text=f"Titre de la vidéo : {youtube_video.title}\nAuteur : {youtube_video.author}\nFormat MP4 uniquement - Dossier : {output_folder_ask}\nAjouter cette vidéo à la liste des téléchargements ?", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((11*screen_height)/1080)), anchor="w", justify="left")
                elif mp4_selected:
                    video_info_label = Label(root, text=f"Titre de la vidéo : {youtube_video.title}\nAuteur : {youtube_video.author}\nFormats MP4 et MP3 - Dossier : {output_folder_ask}\nAjouter cette vidéo à la liste des téléchargements ?", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((11*screen_height)/1080)), anchor="w", justify="left")
                else:
                 video_info_label = Label(root, text=f"Titre de la vidéo : {youtube_video.title}\nAuteur : {youtube_video.author}\nFormat MP3 uniquement - Dossier : {output_folder_ask}\nAjouter cette vidéo à la liste des téléchargements ?", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((11*screen_height)/1080)), anchor="w", justify="left")
            
                video_info_label.place(x=round((25*screen_width)/1920), y=round((300*screen_height)/1080))
                print(f"Télécharger la vidéo : {youtube_video.title} dans le répertoire : {output_folder_ask} ?")

                # Crée la frame correspondant au bouton "Télécharger"
                download_button_frame = Frame(root, relief=FLAT, bg="#FFFFFF", borderwidth=2)

                # Crée le contour du bouton "Télécharger"
                download_button=Button(download_button_frame, image=download_icon, relief=FLAT, bg="#FFFFFF", width=150, height=50, command=init_variables_for_download)
                download_button.pack(padx=0)
            
                # Crée le texte affiché dans le bouton "Télécharger"
                download_txt_label = Label(download_button_frame, text="Télécharger", fg="#FFFFFF", bg="#2255D5", font=("Nexa Heavy", round((10*screen_height)/1080)))
                download_txt_label.bind("<Button-1>", init_variables_for_download)
                download_txt_label.place(x=round((56*screen_width)/1920), y=round((16*screen_height)/1080))

                download_button_frame.place(x=round((100*screen_width)/1920), y=round((400*screen_height)/1080))

                # Crée le bouton "Ajouter à la file"
                add_to_queue_button=Button(root, image=add_to_queue_icon, relief=FLAT, bg="#FFFFFF", command=add_to_queue)
                add_to_queue_button.place(x=round((25*screen_width)/1920), y=round((400*screen_height)/1080))

                # Joue un son en cas de succès
                play_sound("sound/search_success.ogg")


            # DANS LE CAS OÙ L'ENTRÉE POUR LE LIEN DE LA VIDÉO EST VIDE
            elif youtube_video == "":
                video_info_label = Label(root, text=f"Inscrivez le lien d'une vidéo à télécharger.", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((12*screen_height)/1080))) # Affiche le message d'erreur dans les informations de la vidéo
                video_info_label.place(x=round((25*screen_width)/1920), y=round((300*screen_height)/1080))
                try:
                    add_to_queue_button.destroy() # Efface le bouton "Ajouter à la file" s'il existe déjà dans la fenêtre
                except:
                    pass
                pygame.mixer.music.load("sound/warning.ogg")
                pygame.mixer.music.play()

            # DANS LE CAS OÙ AUCUN DOSSIER N'EST SÉLECTIONNÉ POUR LE TÉLÉCHARGEMENT
            elif output_folder_ask == "":
                video_info_label = Label(root, text=f"Sélectionnez un dossier vers lequel télécharger la vidéo.", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((12*screen_height)/1080))) # Affiche le message d'erreur dans les informations de la vidéo
                video_info_label.place(x=round((25*screen_width)/1920), y=round((300*screen_height)/1080))
                try:
                    add_to_queue_button.destroy() # Efface le bouton "Ajouter à la file" s'il existe déjà dans la fenêtre
                except:
                    pass
                play_sound("sound/warning.ogg")

            # DANS LE CAS OÙ L'ENTRÉE POUR LE LIEN DE LA VIDÉO EST VIDE MAIS QUE LE DOSSIER VERS LEQUEL TÉLÉCHARGER EST SÉLECTIONNÉ
            elif youtube_video == "" and output_folder_ask != "":
                video_info_label = Label(root, text=f"Inscrivez le lien d'une vidéo à télécharger.", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((12*screen_height)/1080))) # Affiche le message d'erreur dans les informations de la vidéo
                video_info_label.place(x=round((25*screen_width)/1920), y=round((300*screen_height)/1080))
                try:
                    add_to_queue_button.destroy() # Efface le bouton "Ajouter à la file" s'il existe déjà dans la fenêtre
                except:
                    pass
                play_sound("sound/warning.ogg")

        # SI UNE ERREUR EST SURVENUE PENDANT LA PHASE DE RECHERCHE ET D'AFFICHAGE DES INFORMATIONS (GÉNÉRALEMENT LORSQUE LA VIDÉO N'A PAS ÉTÉ TROUVÉE)
        except Exception as err:
            video_info_label = Label(root, text=f"La vidéo n'a pas été trouvée. Assurez-vous d'avoir renseigné le bon lien.", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((12*screen_height)/1080))) # Affiche le message d'erreur dans les informations de la vidéo
            video_info_label.place(x=round((25*screen_width)/1920), y=round((300*screen_height)/1080))
            video_error_label = Label(root, text=f"Code d'erreur : {err}", bg="#FFFFFF", fg="#000000", font=("Arial", round((8*screen_height)/1080))) # Affiche le code d'erreur
            video_error_label.place(x=round((100*screen_width)/1920), y=round((248*screen_height)/1080))
            try:
                add_to_queue_button.destroy() # Efface le bouton "Ajouter à la file" s'il existe déjà dans la fenêtre
            except:
                pass
            play_sound("sound/warning.ogg") # Joue le son d'erreur
            print(f"Erreur : {err}")


    """elif application_type == "tiktok": # NON FONCTIONNEL
        parsed_url = urlparse("https://vm.tiktok.com/ZGe9yerWC/")
        query_params = parse_qs(parsed_url.query)
        video_url = query_params.get('video', None)
        print(video_url)
        if video_url:
            return video_url[0]
        else:
            raise ValueError("Lien TikTok non valide ou vidéo introuvable")
        response = requests.get("https://vm.tiktok.com/ZGe9yerWC/")
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        video_tag = soup.find('video')
        
        if video_tag:
            video_url = video_tag['src']
            return video_url
        else:
            raise ValueError("Lien TikTok non valide ou vidéo introuvable")"""



# PRÉPARE LE TÉLÉCHARGEMENT EN INITIALISANT CERTAINES VARIABLES NÉCESSAIRES À CELUI-CI
def init_variables_for_download(event=""):
    '''Initializes downloading-relative content, such as variables, lists, widgets and downloads each content.'''
    global video_download_progress_label
    global video_downloading_number
    global download_button_frame
    global add_to_queue_button
    try:
        add_to_queue_button.destroy() # Efface le bouton "Ajouter à la file" s'il existe déjà dans la fenêtre
    except:
        pass
    try:
        video_download_progress_label.destroy() # Efface le label de progression du téléchargement s'il existe déjà dans la fenêtre
    except:
        pass
    try:
        download_button_frame.destroy() # Efface le bouton de téléchargement s'il existe déjà dans la fenêtre
    except:
        pass
    try:
        open_folder_button.destroy() # Efface le bouton d'ouverture de dossiers (post-download) s'il existe déjà dans la fenêtre
    except:
        pass
    video_download_progress_label = Label(root, text=f"Téléchargement en cours...", bg="#FFFFFF", fg="#000000", font=("Arial", round((12*screen_height)/1080)), anchor="w", justify="left") # Affiche le label de progression du téléchargement
    video_download_progress_label.place(x=round((25*screen_width)/1920), y=round((400*screen_height)/1080))

    if content_queue == []: # Dans le cas où un seul est contenu est téléchargé et qu'il n'a pas été placé dans la liste de téléchargements, l'insère
        add_to_queue()

    root.update()
    play_sound("sound/select.ogg")

    # Utilise une boucle pour télécharger chaque contenu de la liste un par un
    video_downloading_number = 0
    for video_object in content_queue:
        root.update()
        video_downloader(video_object[1], output_folder_ask) # Fonction de téléchargement
        video_downloading_number += 1
    
    print(f"Téléchargement des vidéos terminé. Les fichiers ont été enregistrés dans le dossier : {output_folder_ask}")
    play_sound("sound/success.ogg") # Joue le son de succès une fois le téléchargement terminé

    download_end_page() # Affiche la page des résultats du téléchargement


# FONCTION S'EXÉCUTANT À CHAQUE PROGRESSION DU TÉLÉCHARGEMENT
def on_download_progress(stream, chunck, bytes_remaining):
    '''Updates the downloading progress label for each progress recall.'''
    global video_download_progress_label
    percentage = 100 - round((bytes_remaining / stream.filesize) * 100)
    video_download_progress_label.config(text=f"Téléchargement de : {content_queue[video_downloading_number][0]}...\n{percentage}% complétés.") # Modifie le label de progression du téléchargement et affiche le pourcentage complété
    root.update()
    print(f"{percentage}% complétés.")


# FONCTION PRINCIPALE DE TÉLÉCHARGEMENT
def video_downloader(url, output_folder):
    '''Finds then downloads the video referenced in URL, then extracts the audio file if setting is enabled.'''
    global download_button_frame
    global open_folder_button
    if application_type == "youtube":
        try:
            # Instancier un objet YouTube avec l'URL de la vidéo
            youtube_video = YouTube(url) # Crée un objet "youtube_video" appartenant à la classe "YouTube" et contenant les informations de la vidéo à télécharger (cette variable est ici locale, donc différente de celle utilisée dans la fonction search_for_results())

            youtube_video.register_on_progress_callback(on_download_progress) # Vérifie si une progression a eu lieu lors du téléchargement, et exécute la fonction "on_download_progress" le cas échéant

            # Sélectionner le flux vidéo avec la résolution spécifique
            video = youtube_video.streams.get_highest_resolution()  # Place la résolution de la vidéo à télécharger sur la plus haute

            print("Téléchargement en cours...")
            # TÉLÉCHARGE LA VIDÉO DANS LE DOSSIER SPÉCIFIÉ
            video.download(output_folder)

            # FONCTION DE CONVERSION AU FORMAT MP3 GRÂCE À PYDUB (ET FFMPEG)
            if mp3_selected == True:
                # Récupère les chemins d'accès aux fichiers MP4 et MP3
                video_file_path = f"{output_folder}/{video.default_filename}"
                audio_file_path = video_file_path[:-4] + ".mp3"

                video_to_audio = AudioSegment.from_file(video_file_path, format="mp4")
                video_to_audio.export(audio_file_path, format="mp3")
        
            # Si la case "MP4" n'a pas été cochée, efface la vidéo téléchargée précédemment et conserve le fichier MP3
            if mp4_selected == False:
                os.remove(video_file_path)

        # SI UNE ERREUR EST SURVENUE LORS DU TÉLÉCHARGEMENT
        except Exception as e:
            videos_download_errors_list.append([youtube_video.title, e]) # Ajoute à la liste d'erreurs à afficher celle qui est survenue pour un contenu
            print(f"Une erreur est survenue :\n{str(e)}")




# FONCTIONS D'EFFACEMENT DES WIDGETS

# Efface tous les widgets présents sur la fenêtre - fonction de rafraîchissement de la fenêtre
def clear_screen(root):
    '''Clears the whole window.'''
    for widget in root.winfo_children():
        widget.destroy()

# Réinitialise les variables associées au téléchargement
def reset_downloads():
    '''Resets downloading-relatives variables and lists.'''
    global output_folder_ask
    global content_queue
    global videos_download_errors_list
    output_folder_ask = ""
    content_queue = []
    videos_download_errors_list = []

    # Efface tous les widgets puis affiche la page principale de téléchargement
    clear_screen(root)
    main_widgets_reset()



# CONFIGURATIONS DES PAGES DE LA FENÊTRE ----------------------------------------------------------------------------------------

# CONFIGURATION DE LA PAGE DES NOTES DE MISE À JOUR
def patchnotes_page():
    '''Displays the patch notes content in the window.'''
    clear_screen(root)

    global headtext_patch_widget
    global patch_date_widget
    global patchnotes_widget
    global credits_widget_patch
    global back_button

    # Gros texte en haut de page affichant "Notes de mise à jour"
    headtext_patch_widget = Label(root, text="Notes de mise à jour", bg="#FFFFFF", fg="#000000", font=("MADE Soulmaze", round((15*screen_height)/1080)))
    headtext_patch_widget.place(x=round((25*screen_width)/1920), y=round((20*screen_height)/1080))

    # Affiche la date de la dernière mise à jour ainsi que la version de l'outil
    patch_date_widget = Label(root, text=f"Dernière mise à jour : {last_update_string}.\nVersion {app_version}", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((12*screen_height)/1080)), justify="left", anchor="w")
    patch_date_widget.place(x=round((25*screen_width)/1920), y=round((70*screen_height)/1080))

    # Sélectionne dans "patchnotes_list" (variable présente dans le fichier patchnotes.py) toutes les notes de mise à jour
    patchnotes_text = f""
    for element in patchnotes_list:
        patchnotes_text = f"{patchnotes_text}\n• {element}"

    # Affiche toutes les notes de changement listées
    patchnotes_widget = Label(root, text=patchnotes_text, bg="#FFFFFF", fg="#000000", font=("Arial", round((11*screen_height)/1080)), anchor="w", justify="left")
    patchnotes_widget.place(x=round((25*screen_width)/1920), y=round((130*screen_height)/1080))

    # Affiche les crédits de l'outil en bas à gauche de la fenêtre
    credits_widget_patch = Label(root, text=f"Créé par Screan. Reproduction du service interdite.", bg="#FFFFFF", fg="#000000", font=("Arial", round((9*screen_height)/1080)), anchor="w", justify="left")
    credits_widget_patch.place(x=round((4*screen_width)/1920), y=round((495*screen_height)/1080))

    # Bouton de retour à la page principale
    back_button=Button(root, text="Retour", height=round((1*screen_height)/1080), font=("Arial", round((9*screen_height)/1080)), command=main_widgets_reset)
    back_button.place(x=round((350*screen_width)/1920), y=round((20*screen_height)/1080))


# -----------------------------------------------------


# CONFIGURATION DE LA PAGE DE FIN DE TÉLÉCHARGEMENT
def download_end_page():
    '''Displays the download-end content in the window.'''
    clear_screen(root)

    # Gros texte en haut de page affichant "YouTube Local Downloader"
    headtext_title_widget = Label(root, text="YouTube Local Downloader", bg="#FFFFFF", fg="#000000", font=("MADE Soulmaze", round((15*screen_height)/1080)))
    headtext_title_widget.place(x=round((25*screen_width)/1920), y=round((20*screen_height)/1080))

    # Affiche les crédits de l'outil en bas à gauche de la fenêtre
    credits_widget = Label(root, text=f"Créé par Screan. Reproduction du service interdite.\nVersion {app_version}", bg="#FFFFFF", fg="#000000", font=("Arial", round((9*screen_height)/1080)), anchor="w", justify="left")
    credits_widget.place(x=round((4*screen_width)/1920), y=round((480*screen_height)/1080))

    # Affiche l'emplacement des contenus téléchargés
    video_download_progress_label = Label(root, text=f"Téléchargement des vidéos terminé.\nLes fichiers ont été enregistrés dans le dossier : {output_folder_ask}.", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((12*screen_height)/1080)), anchor="w", justify="left")
    video_download_progress_label.place(x=round((25*screen_width)/1920), y=round((70*screen_height)/1080))
    
    # Si des erreurs sont survenues lors de certains téléchargements, ajoute chacune d'entre elles dans un texte "videos_download_errors_list"
    if videos_download_errors_list != []:
        videos_download_errors_text = "Des erreurs sont survenues lors du téléchargement de certaines vidéos. Celles-ci sont listées ci-dessous :"
        for error in videos_download_errors_list:
            videos_download_errors_text = f"{videos_download_errors_text}\n• {error[0]} : {error[1]}"
        # Crée un label avec pour texte la liste des erreurs inscrites dans "videos_download_errors_list"
        video_error_label = Label(root, text=videos_download_errors_text, bg="#FFFFFF", fg="#000000", font=("Arial", round((10*screen_height)/1080)))
        video_error_label.place(x=round((25*screen_width)/1920), y=round((180*screen_height)/1080))
    else:
        # Crée un label pour afficher qu'aucune erreur n'est survenue
        video_error_label = Label(root, text="Aucune erreur n'est survenue.", bg="#FFFFFF", fg="#000000", font=("Arial", round((10*screen_height)/1080)))
        video_error_label.place(x=round((25*screen_width)/1920), y=round((180*screen_height)/1080))

    # Bouton d'ouverture du dossier vers lequel les contenus ont été téléchargés
    open_folder_button = Button(root, text="Ouvrir le dossier", width=round((30*screen_height)/1080), height=round((1*screen_height)/1080), font=("Arial", round((9*screen_height)/1080)), command=open_file_folder)
    open_folder_button.place(x=round((25*screen_width)/1920), y=round((135*screen_height)/1080))

    # Bouton permettant de revenir à la page principale pour télécharger d'autres vidéos
    return_to_download_page_button = Button(root, text="Télécharger d'autres vidéos", width=round((30*screen_height)/1080), height=round((1*screen_height)/1080), font=("Arial", round((9*screen_height)/1080)), command=reset_downloads)
    return_to_download_page_button.place(x=round((300*screen_width)/1920), y=round((135*screen_height)/1080))


# -----------------------------------------------------
    
def first_use():
    global first_use_step
    global first_use_default_folder_desctext_widget2
    clear_screen(root)

    def first_use_previous_page():
        global first_use_step
        first_use_step -= 2
        play_sound("sound/back.ogg")
        first_use()
    
    def first_use_next_page():
        play_sound("sound/select.ogg")
        first_use()

    def install_fonts():
        install_fonts_check = get_json_data("user_data/settings-user-data.json", "additionalFontsDownload")
        if install_fonts_check == "True":
            next_button.config(text="Téléchargement...")
            next_button.configure(state=tk.DISABLED)
            execute_file("additional_downloads/additional-fonts-download.py")
        play_sound("sound/select.ogg")
        first_use()

    def update_install_fonts_setting():
        first_use_download_extra_fonts_checkbox_var_check = first_use_download_extra_fonts_checkbox_var.get()
        if first_use_download_extra_fonts_checkbox_var_check == 1:
            edit_json_data("user_data/settings-user-data.json", "additionalFontsDownload", "False")
            next_button.config(text="Suivant")
        else:
            edit_json_data("user_data/settings-user-data.json", "additionalFontsDownload", "True")
            next_button.config(text="Suivant (installer les polices d'écriture)")

    def reset_default_folder():
        edit_json_data("user_data/settings-user-data.json", "defaultOutputFolder", "")
        first_use_default_folder_desctext_widget2.config(text=f"Aucun dossier spécifique sélectionné.")
        play_sound("sound/select.ogg")
    
    def default_folder_last_one():
        edit_json_data("user_data/settings-user-data.json", "defaultOutputFolder", "lastSelected")
        first_use_default_folder_desctext_widget2.config(text=f"Dernier dossier sélectionné.")
        play_sound("sound/select.ogg")

    
    def update_rename_files_setting():
        first_use_rename_files_checkbox_var_check = first_use_rename_files_checkbox_var.get()
        if first_use_rename_files_checkbox_var_check == 1:
            edit_json_data("user_data/settings-user-data.json", "renameFilesToDefaultFormat", "True")
            first_use_rename_files_checkbox.config(text="Renommage de fichiers activé")
        else:
            edit_json_data("user_data/settings-user-data.json", "renameFilesToDefaultFormat", "False")
            first_use_rename_files_checkbox.config(text="Renommage de fichiers désactivé")
    
    def update_user_agreement_of_legal_info():
        user_agreement_of_legal_info_var_check = user_agreement_of_legal_info_var.get()
        if user_agreement_of_legal_info_var_check == 1:
            next_button.configure(state=tk.NORMAL)
            edit_json_data("user_data/settings-user-data.json", "TermsOfUseUserAgreement", "True")
        else:
            next_button.configure(state=tk.DISABLED)
            edit_json_data("user_data/settings-user-data.json", "TermsOfUseUserAgreement", "False")
        return user_agreement_of_legal_info_var_check
    
    def first_use_end():
        play_sound("sound/welcome.ogg")
        clear_screen(root)
        img = Image.open("images/ytb_converter_icon_png_format.png")
        img = img.resize((round((90*screen_width)/1920), round((90*screen_height)/1080)))
        tool_icon_img = ImageTk.PhotoImage(img)

        first_use_img_widget = Label(root, image=tool_icon_img, bg="#FFFFFF", fg="#000000", justify="left", font=("MADE Soulmaze", round((20*screen_height)/1080)))
        first_use_headtext_title_widget = Label(root, text="Bienvenue sur\nYouTube Local Downloader !", bg="#FFFFFF", fg="#000000", justify="left", font=("MADE Soulmaze", round((20*screen_height)/1080)))
        
        widget_pos = round((0*screen_width)/1920)
        for tick in range(300):
            widget_pos += ((round((100*screen_width)/1920))-widget_pos)/20
            first_use_headtext_title_widget.place(x=200+widget_pos, y=220)
            first_use_img_widget.place(x=80+widget_pos, y=220)
            time.sleep(0.01)
            root.update()
        edit_json_data("user_data/settings-user-data.json", "isConfigured", "True")
        
        play_sound("sound/app_init.ogg")
        main_widgets_reset()


    if first_use_step == 0:
        # Texte affichant le gros texte en haut de page
        first_use_headtext_title_widget = Label(root, text="Bienvenue !", bg="#FFFFFF", fg="#000000", font=("MADE Soulmaze", round((15*screen_height)/1080)))
        first_use_headtext_title_widget.place(x=round((25*screen_width)/1920), y=round((20*screen_height)/1080))

        # Texte de description générale
        first_use_desc_text_widget = Label(root, text="Merci d'avoir choisi YouTube Local Downloader (ci-après : YLD).\nYLD est un outil de téléchargement de vidéos YouTube gratuit et à usage illimité.\nTéléchargez autant de contenus que vous souhaitez sans la moindre publicité, puis extrayez-en l'audio pour obtenir\nvotre vidéo téléchargée au format MP3 (nécessite le module FFMPEG) !", bg="#FFFFFF", fg="#000000", justify="left", font=("Nexa Heavy", round((11*screen_height)/1080)))
        first_use_desc_text_widget.place(x=round((25*screen_width)/1920), y=round((70*screen_height)/1080))

        next_button = Button(root, text="Suivant", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=first_use_next_page)
        next_button.place(x=round((25*screen_width)/1920), y=round((168*screen_height)/1080))
    
    elif first_use_step == 1:
        first_use_headtext_title_widget = Label(root, text="Contenu complémentaire à installer", bg="#FFFFFF", fg="#000000", font=("MADE Soulmaze", round((15*screen_height)/1080)))
        first_use_headtext_title_widget.place(x=round((25*screen_width)/1920), y=round((20*screen_height)/1080))

        first_use_desc_text_widget = Label(root, text="Afin d'assurer la bonne mise en forme de l'interface, nous avons besoin d'installer sur le système des polices d'écriture.\nCes polices d'écriture seront stockées dans un fichier temporaire et ne seront utilisées que lorsque l'outil est actif.\nSi vous ne souhaitez pas procéder à cette installation supplémentaire, vous pouvez cliquer sur\n\"Ne pas installer le contenu complémentaire\".\nSachez cependant que la mise en forme de l'interface risque d'être affectée si vous n'installez ces polices d'écriture.", bg="#FFFFFF", fg="#000000", justify="left", font=("Nexa Heavy", round((11*screen_height)/1080)))
        first_use_desc_text_widget.place(x=round((25*screen_width)/1920), y=round((70*screen_height)/1080))

        if get_json_data("user_data/settings-user-data.json", "additionalFontsDownload") == "True":
            first_use_download_extra_fonts_checkbox_var = tk.IntVar()
        else:
            first_use_download_extra_fonts_checkbox_var = tk.IntVar(value=1)
        first_use_download_extra_fonts_checkbox = Checkbutton(root, text="Ne pas installer le contenu complémentaire", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((10*screen_height)/1080)), variable=first_use_download_extra_fonts_checkbox_var, command=update_install_fonts_setting)
        first_use_download_extra_fonts_checkbox.place(x=round((25*screen_width)/1920), y=round((180*screen_height)/1080))

        previous_button = Button(root, text="← Retour", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=first_use_previous_page)
        previous_button.place(x=round((25*screen_width)/1920), y=round((220*screen_height)/1080))

        if get_json_data("user_data/settings-user-data.json", "additionalFontsDownload") == "True":
            next_button = Button(root, text="Suivant (installer les polices d'écriture)", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=install_fonts)
            next_button.place(x=round((140*screen_width)/1920), y=round((220*screen_height)/1080))
        else:
            next_button = Button(root, text="Suivant", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=install_fonts)
            next_button.place(x=round((140*screen_width)/1920), y=round((220*screen_height)/1080))

    elif first_use_step == 2:
        check_ffmpeg_installed()
        if ffmpeg_installed == True:
            # Texte affichant le gros texte en haut de page
            first_use_headtext_title_widget = Label(root, text="Recherche du module FFMPEG réussie", bg="#FFFFFF", fg="#000000", font=("MADE Soulmaze", round((15*screen_height)/1080)))
            first_use_headtext_title_widget.place(x=round((25*screen_width)/1920), y=round((20*screen_height)/1080))

            # Texte de description générale
            first_use_desc_text_widget = Label(root, text="Il semble que vous disposiez du module FFMPEG sur votre appareil. Super !\nFFMPEG vous permet de convertir les vidéos que vous téléchargez au format MP3.\nSi vous souhaitez télécharger des musiques à partir d'une vidéo YouTube, YLD vous simplifiera bien la tâche.\n\nVeillez à ne pas supprimer le module, sinon vous risquez d'obtenir des erreurs en essayant de convertir des contenus au format audio.", bg="#FFFFFF", fg="#000000", justify="left", font=("Nexa Heavy", round((11*screen_height)/1080)))
            first_use_desc_text_widget.place(x=round((25*screen_width)/1920), y=round((70*screen_height)/1080))

            previous_button = Button(root, text="← Retour", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=first_use_previous_page)
            previous_button.place(x=round((25*screen_width)/1920), y=round((180*screen_height)/1080))

            next_button = Button(root, text="Suivant", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=first_use_next_page)
            next_button.place(x=round((140*screen_width)/1920), y=round((180*screen_height)/1080))
        else:
            first_use_headtext_title_widget = Label(root, text="Recherche du module FFMPEG : module manquant", bg="#FFFFFF", fg="#000000", font=("MADE Soulmaze", round((15*screen_height)/1080)))
            first_use_headtext_title_widget.place(x=round((25*screen_width)/1920), y=round((20*screen_height)/1080))

            # Texte de description générale
            first_use_desc_text_widget = Label(root, text="On dirait que le module FFMPEG n'est pas installé sur cet appareil.\nCelui-ci est pourtant nécessaire pour utiliser la fonction de conversion des vidéos téléchargées au format MP3.\n\nEn essayant de convertir un contenu au format audio, vous risquez d'obtenir une erreur.\n\nSi vous ne souhaitez pas installer le module, vous pourrez tout de même utiliser l'outil de téléchargement de vidéos,\nmais vous n'aurez pas accès à la fonction d'extraction de l'audio.", bg="#FFFFFF", fg="#000000", justify="left", font=("Nexa Heavy", round((11*screen_height)/1080)))
            first_use_desc_text_widget.place(x=round((25*screen_width)/1920), y=round((70*screen_height)/1080))

            first_use_headtext_how_to_install_ffmpeg__widget = Label(root, text="Comment installer FFMPEG ?", bg="#FFFFFF", fg="#000000", font=("MADE Soulmaze", round((12*screen_height)/1080)))
            first_use_headtext_how_to_install_ffmpeg__widget.place(x=round((25*screen_width)/1920), y=round((230*screen_height)/1080))

            first_use_desc_text_widget2 = Label(root, text="Suivez le guide sur la page web de l'outil pour installer FFMPEG. Cliquez sur le bouton ci-dessous pour vous y rendre.", bg="#FFFFFF", fg="#000000", justify="left", font=("Nexa Heavy", round((11*screen_height)/1080)))
            first_use_desc_text_widget2.place(x=round((25*screen_width)/1920), y=round((280*screen_height)/1080))
        
            download_ffmpeg_button = Button(root, text="Guide d'installation de FFMPEG", bg="#FFFFFF", command=open_install_ffmpeg_webpage)
            download_ffmpeg_button.place(x=round((25*screen_width)/1920), y=round((315*screen_height)/1080))

            previous_button = Button(root, text="← Retour", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=first_use_previous_page)
            previous_button.place(x=round((25*screen_width)/1920), y=round((380*screen_height)/1080))

            next_button = Button(root, text="Suivant", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=first_use_next_page)
            next_button.place(x=round((140*screen_width)/1920), y=round((380*screen_height)/1080))
    
    elif first_use_step == 3:
        first_use_headtext_title_widget = Label(root, text="Configuration des paramètres", bg="#FFFFFF", fg="#000000", font=("MADE Soulmaze", round((15*screen_height)/1080)))
        first_use_headtext_title_widget.place(x=round((25*screen_width)/1920), y=round((20*screen_height)/1080))

        first_use_desc_text_widget = Label(root, text="Configurez les paramètres de l'outil pour plus de simplicité lors de son usage.\nCes derniers pourront à tout moment être modifiés dans la page des options.", bg="#FFFFFF", fg="#000000", justify="left", font=("Nexa Heavy", round((11*screen_height)/1080)))
        first_use_desc_text_widget.place(x=round((25*screen_width)/1920), y=round((70*screen_height)/1080))
        
        first_use_default_folder_headtext_widget = Label(root, text="Dossier de téléchargement par défaut", bg="#FFFFFF", fg="#000000", justify="left", font=("Comixo", round((14*screen_height)/1080)))
        first_use_default_folder_headtext_widget.place(x=round((25*screen_width)/1920), y=round((130*screen_height)/1080))

        first_use_default_folder_desctext_widget = Label(root, text="Ce dossier sera automatiquement sélectionné au démarrage de l'outil. Cliquez sur le bouton \"Sans sélection\" pour ne choisir aucun dossier par défaut.\nVous pouvez également configurer le dossier de téléchargement de sorte à ce que le dernier dossier sélectionné soit choisi.", bg="#FFFFFF", fg="#000000", justify="left", font=("Arial", round((9*screen_height)/1080)))
        first_use_default_folder_desctext_widget.place(x=round((25*screen_width)/1920), y=round((155*screen_height)/1080))

        default_folder_button = Button(root, text="Choisir un dossier", bg="#FFFFFF", command=open_folder_dialog_first_use)
        default_folder_button.place(x=round((25*screen_width)/1920), y=round((200*screen_height)/1080))

        reset_default_folder_button = Button(root, text="Sans sélection", bg="#FFFFFF", command=reset_default_folder)
        reset_default_folder_button.place(x=round((150*screen_width)/1920), y=round((200*screen_height)/1080))

        default_folder_last_one_button = Button(root, text="Dernier sélect.", bg="#FFFFFF", command=default_folder_last_one)
        default_folder_last_one_button.place(x=round((250*screen_width)/1920), y=round((200*screen_height)/1080))

        if get_json_data("user_data/settings-user-data.json", "defaultOutputFolder") == "":
            first_use_default_folder_desctext_widget2 = Label(root, text="Aucun dossier spécifique sélectionné.", bg="#FFFFFF", fg="#000000", justify="left", font=("Nexa Heavy", round((11*screen_height)/1080)))
            first_use_default_folder_desctext_widget2.place(x=round((350*screen_width)/1920), y=round((200*screen_height)/1080))
        else:
            first_use_default_folder_desctext_widget2 = Label(root, text=f"Dossier : {get_json_data('user_data/settings-user-data.json', 'defaultOutputFolder')}", bg="#FFFFFF", fg="#000000", justify="left", font=("Nexa Heavy", round((11*screen_height)/1080)))
            first_use_default_folder_desctext_widget2.place(x=round((250*screen_width)/1920), y=round((200*screen_height)/1080))

        first_use_rename_files_headtext_widget = Label(root, text="Utiliser le renommage de fichiers ?", bg="#FFFFFF", fg="#000000", justify="left", font=("Comixo", round((14*screen_height)/1080)))
        first_use_rename_files_headtext_widget.place(x=round((25*screen_width)/1920), y=round((260*screen_height)/1080))

        first_use_rename_files_desctext_widget = Label(root, text="Si activé, les fichiers téléchargés seront renommés selon le formatage suivant : <Titre> - <Auteur>.", bg="#FFFFFF", fg="#000000", justify="left", font=("Arial", round((9*screen_height)/1080)))
        first_use_rename_files_desctext_widget.place(x=round((25*screen_width)/1920), y=round((285*screen_height)/1080))

        if get_json_data("user_data/settings-user-data.json", "renameFilesToDefaultFormat") == "False":
            first_use_rename_files_checkbox_var = tk.IntVar()
            first_use_rename_files_checkbox = Checkbutton(root, text="Renommage de fichiers désactivé", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((10*screen_height)/1080)), variable=first_use_rename_files_checkbox_var, command=update_rename_files_setting)
        else:
            first_use_rename_files_checkbox_var = tk.IntVar(value=1)
            first_use_rename_files_checkbox = Checkbutton(root, text="Renommage de fichiers activé", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((10*screen_height)/1080)), variable=first_use_rename_files_checkbox_var, command=update_rename_files_setting)
        first_use_rename_files_checkbox.place(x=round((25*screen_width)/1920), y=round((310*screen_height)/1080))

        previous_button = Button(root, text="← Retour", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=first_use_previous_page)
        previous_button.place(x=round((25*screen_width)/1920), y=round((360*screen_height)/1080))

        next_button = Button(root, text="Suivant", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=first_use_next_page)
        next_button.place(x=round((140*screen_width)/1920), y=round((360*screen_height)/1080))
    
    elif first_use_step == 4:
        first_use_headtext_title_widget = Label(root, text="Informations importantes", bg="#FFFFFF", fg="#000000", font=("MADE Soulmaze", round((15*screen_height)/1080)))
        first_use_headtext_title_widget.place(x=round((25*screen_width)/1920), y=round((20*screen_height)/1080))

        first_use_desc_text_widget = Label(root, text="En utilisant YLD, vous acceptez les conditions d'utilisation et la politique de confidentialité de l'outil, consultables sur la page web de YLD.\nCliquez sur le bouton ci-dessous pour y accéder.", bg="#FFFFFF", fg="#000000", justify="left", font=("Nexa Heavy", round((11*screen_height)/1080)))
        first_use_desc_text_widget.place(x=round((25*screen_width)/1920), y=round((70*screen_height)/1080))

        read_me_page_button = Button(root, text="Voir les informations légales", bg="#FFFFFF", command=open_readme_webpage)
        read_me_page_button.place(x=round((25*screen_width)/1920), y=round((120*screen_height)/1080))

        if get_json_data("user_data/settings-user-data.json", "TermsOfUseUserAgreement") == "False":
            user_agreement_of_legal_info_var = tk.IntVar()
        else:
            user_agreement_of_legal_info_var = tk.IntVar(value=1)
        user_agreement_of_legal_info_checkbox = Checkbutton(root, text="J'accepte la politique de confidentialité et les conditions d'utilisation de l'outil", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((10*screen_height)/1080)), variable=user_agreement_of_legal_info_var, command=update_user_agreement_of_legal_info)
        user_agreement_of_legal_info_checkbox.place(x=round((25*screen_width)/1920), y=round((170*screen_height)/1080))

        previous_button = Button(root, text="← Retour", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=first_use_previous_page)
        previous_button.place(x=round((25*screen_width)/1920), y=round((220*screen_height)/1080))

        next_button = Button(root, text="Terminer", bg="#FFFFFF", font=("Comixo", round((12*screen_height)/1080)), command=first_use_end)
        next_button.place(x=round((140*screen_width)/1920), y=round((220*screen_height)/1080))

        update_user_agreement_of_legal_info()



    first_use_steps_text_widget = Label(root, text=f"Étape {first_use_step+1} / 5", bg="#FFFFFF", fg="#000000", justify="left", font=("Arial", round((11*screen_height)/1080)))
    first_use_steps_text_widget.place(x=round((4*screen_width)/1920), y=round((450*screen_height)/1080))

    credits_widget = Label(root, text=f"Créé par Screan. Reproduction du service interdite.\nVersion {app_version}", bg="#FFFFFF", fg="#000000", font=("Arial", round((9*screen_height)/1080)), anchor="w", justify="left")
    credits_widget.place(x=round((4*screen_width)/1920), y=round((480*screen_height)/1080))

    first_use_step += 1




# CONFIGURATION DE LA FENÊTRE PRINCIPALE DE TÉLÉCHARGEMENT


# -----------------------------------------------------


# CONFIGURATION DE LA FENÊTRE PRINCIPALE DE TÉLÉCHARGEMENT

def main_widgets_reset():
    '''Displays the main page of the window.'''
    clear_screen(root)
    global headtext_title_widget
    global credits_widget
    global ytb_link_entry_widget
    global ytb_link_entry
    global path_entry_widget
    global path_entry
    global mp3_format_checkbox
    global mp3_format_checkbox_var
    global mp4_format_checkbox_var
    global search_button
    global patchnotes_button
    global downloads_list_headtext_widget

    # Gros texte en haut de page affichant "YouTube Local Downloader"
    headtext_title_widget = Label(root, text="YouTube Local Downloader", bg="#FFFFFF", fg="#000000", font=("MADE Soulmaze", round((15*screen_height)/1080)))
    headtext_title_widget.place(x=round((25*screen_width)/1920), y=round((20*screen_height)/1080))

    # Affiche les crédits de l'outil en bas à gauche de la fenêtre
    credits_widget = Label(root, text=f"Créé par Screan. Reproduction du service interdite.\nVersion {app_version}", bg="#FFFFFF", fg="#000000", font=("Arial", round((9*screen_height)/1080)), anchor="w", justify="left")
    credits_widget.place(x=round((4*screen_width)/1920), y=round((480*screen_height)/1080))

    # Texte affichant "Lien de la vidéo" au dessus de l'entrée d'URL
    ytb_link_entry_widget = Label(root, text="Lien de la vidéo", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((12*screen_height)/1080)))
    ytb_link_entry_widget.place(x=round((25*screen_width)/1920), y=round((70*screen_height)/1080))

    # Entrée de texte pour l'URL de la vidéo à télécharger
    ytb_link_entry = Entry(root, width=round((65*screen_height)/1080), bg="#EBEBEB", relief=FLAT, font=("Arial", round((12*screen_height)/1080)))
    ytb_link_entry.place(x=round((25*screen_width)/1920), y=round((95*screen_height)/1080))

    # Texte affichant "Dossier vers lequel télécharger" au dessus du bouton de choix du dossier
    path_entry_widget = Label(root, text="Dossier vers lequel télécharger", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((12*screen_height)/1080)))
    path_entry_widget.place(x=round((25*screen_width)/1920), y=round((140*screen_height)/1080))

    # Bouton permettant d'afficher l'explorateur de fichiers afin de sélectionner le dossier vers lequel télécharger - exécute la fonction "open_folder_dialog"
    path_entry = Button(root, image=folder_invalid_icon, relief=FLAT, bg="#FFFFFF", command=open_folder_dialog)
    path_entry.place(x=round((25*screen_width)/1920), y=round((168*screen_height)/1080))

    # Case à cocher pour conserver ou non le fichier MP4 à la fin du téléchargement
    mp4_format_checkbox_var = tk.IntVar()
    mp4_format_checkbox = Checkbutton(root, text="MP4 ?", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((10*screen_height)/1080)), variable=mp4_format_checkbox_var)
    mp4_format_checkbox.place(x=round((80*screen_width)/1920), y=round((175*screen_height)/1080))

    # Fonction permettant d'empêcher la désactivation de la case à cocher "MP4" si la case à cocher "MP3" est désactivée (si le téléchargement au format MP3 n'est pas activé, celui au format MP4 doit être effectué)
    def mp4_checkbox_permission():
        mp3_format_checkbox_var_check = mp3_format_checkbox_var.get()
        if mp3_format_checkbox_var_check == 1:
            mp4_format_checkbox.configure(state=tk.NORMAL)
        else:
            mp4_format_checkbox.configure(state=tk.DISABLED)
            mp4_format_checkbox_var.set(1)

    # Case à cocher pour télécharger également la vidéo au format MP3 - exécute la fonction "mp4_checkbox_permission"
    mp3_format_checkbox_var = tk.IntVar()
    mp3_format_checkbox = Checkbutton(root, text="MP3 ?", bg="#FFFFFF", fg="#000000", font=("Nexa Heavy", round((10*screen_height)/1080)), variable=mp3_format_checkbox_var, command=mp4_checkbox_permission)
    mp3_format_checkbox.place(x=round((150*screen_width)/1920), y=round((175*screen_height)/1080))

    # Bouton de recherche de la vidéo grâce à l'URL - exécute la fonction "search_for_results"
    search_button=Button(root, image=search_icon, relief=FLAT, bg="#FFFFFF", command=search_for_results)
    search_button.place(x=round((25*screen_width)/1920), y=round((230*screen_height)/1080))

    # Bouton permettant d'afficher la page des notes de mise à jour - exécute la fonction "patchnotes_page"
    patchnotes_button=Button(root, text="Notes de MÀJ", height=round((1*screen_height)/1080), font=("Arial", round((9*screen_height)/1080)), command=patchnotes_page)
    patchnotes_button.place(x=round((540*screen_width)/1920), y=round((20*screen_height)/1080))

    # Permet d'ouvrir dans le navigateur la page web de l'outil - exécute la fonction "open_readme_page"
    readme_button=Button(root, text="Plus d'informations", height=round((1*screen_height)/1080), font=("Arial", round((9*screen_height)/1080)), command=open_readme_webpage)
    readme_button.place(x=round((350*screen_width)/1920), y=round((480*screen_height)/1080))

    # Label affichant la liste des vidéos à télécharger sur la droite de la fenêtre
    downloads_list_headtext_widget = Label(root, text="Liste des vidéos à télécharger", bg="#FFFFFF", fg="#000000", font=("Arial", round((10*screen_height)/1080)), justify="left", anchor="w")
    downloads_list_headtext_widget.place(x=round((650*screen_width)/1920), y=round((20*screen_height)/1080))

    mp4_checkbox_permission() # Pour correctement initialiser les permissions de modification de la case à cocher "MP4" lors du retour à la page principale



is_configured = get_json_data("user_data/settings-user-data.json", "isConfigured")
print(is_configured)
if is_configured=="True":
    main_widgets_reset() # Affiche la page principale à l'ouverture de la fenêtre

    # Affiche les crédits de l'outil en bas à gauche de la fenêtre
    loading_down_widget = Label(root, text=f"Chargement du contenu...", bg="#FFFFFF", fg="#000000", font=("Arial", round((9*screen_height)/1080)), anchor="w", justify="left")
    loading_down_widget.place(x=round((4*screen_width)/1920), y=round((460*screen_height)/1080))

    play_sound("sound/app_init.ogg") # Joue le son d'ouverture de la fenêtre lors du lancement du script
    root.update()
    
    if get_json_data("user_data/settings-user-data.json", "additionalFontsDownload") == "True":
        execute_file("additional_downloads/additional-fonts-download.py")
    loading_down_widget.destroy()
else:
    first_use_step = 0
    first_use()


# -----------------------------------------------------


# FONCTION D'EXÉCUTANT LORS DE LA FERMETURE DE LA FENÊTRE
def on_closing():
    '''When window is closed, plays a sound then terminates all current processes.'''
    if get_json_data("user_data/settings-user-data.json", "isConfigured") == "False":
        play_sound("sound/warning.ogg")
        if askyesno("Quitter l'outil ?", "Êtes-vous sûr de vouloir quitter l'outil ? Vous n'avez pas terminé sa configuration. Si vous quittez maintenant, vous devrez recommencer les précédentes étapes de la configuration."):
            reset_settings()
        else:
            return "cancel"
    global window_exists
    # Jouer le son de fermeture
    play_sound("sound/app_quit.ogg")
    root.destroy()
    time.sleep(2)
    window_exists = False # Permet de mettre fin à tous les processus du script lorsque le son de fermeture a fini d'être joué


# Exécute la fonction "on_closing" (permettant de jouer le son de fermeture et de mettre fin aux processus en cours) lorsque l'événement : fermeture de fenêtre est déclenché
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

# Permet de faire tourner le script tant que la variable "window_exists" a pour valeur "True"
while window_exists == True:
    pass