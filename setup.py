from cx_Freeze import setup, Executable
import os.path
from version import app_version

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] =  os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] =  os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

icon_path = os.path.abspath("ytb_converter_icon_ico_format.ico")

base = "Win32GUI"

options = {
    'build_exe': {
        'include_files': [
            (icon_path, "ytb_converter_icon_ico_format.ico"),
            ('E:/Documents/youtube_local_downloader_folder/additional_downloads'),
            ('E:/Documents/youtube_local_downloader_folder/fonts'),
            ('E:/Documents/youtube_local_downloader_folder/images'),
            ('E:/Documents/youtube_local_downloader_folder/readme'),
            ('E:/Documents/youtube_local_downloader_folder/sound'),
            ('E:/Documents/youtube_local_downloader_folder/user_data'),
            ('E:/Documents/youtube_local_downloader_folder/patchnotes.py', 'patchnotes.py'),
            ('E:/Documents/youtube_local_downloader_folder/READ ME.txt', 'READ ME.txt'),
            ('E:/Documents/youtube_local_downloader_folder/settings.py', 'settings.py'),
            ('E:/Documents/youtube_local_downloader_folder/version.py', 'version.py'),
            ('E:/Documents/youtube_local_downloader_folder/version.txt', 'version.txt'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
        ]
    }
}

executables = [Executable('youtube_local_downloader.py', base=base, icon="ytb_converter_icon_ico_format.ico")]

setup(name='YouTube Local Downloader',
      options = options,
      author = "Screan",
      version=app_version,
      description='Un outil vous permettant de télécharger des vidéos YouTube aux formats MP4 et MP3 sur votre ordinateur. Requiert une connexion à Internet.',
      executables=executables)