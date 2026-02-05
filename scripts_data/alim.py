import traceback
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from PyPDF2 import PdfReader, PdfWriter
import json
import gspread
from gspread_dataframe import get_as_dataframe
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from PyPDF2 import PdfReader, PdfWriter
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
import math
import os
import matplotlib.pyplot as plt
from IPython.display import Image, display
import fitz  # PyMuPDF
from PIL import Image as PILImage
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.ticker as mtick
from matplotlib.patches import Patch
import io
import re
import shutil
import zipfile
from google.colab import drive, files

from google.colab import auth
from google.auth import default
import unicodedata
import re
import torch
from sentence_transformers import SentenceTransformer, util
import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *

## récupération des données
df_alim=get_as_dataframe(gspread_client.open_by_url('https://docs.google.com/spreadsheets/d/1bk_ktsT9hBPJS5EY70teq80NzOs_cm3JfrRkX4AYTF4/edit?gid=0#gid=0').worksheet('Feuille 1'))
df_alim=df_alim[["Dispositif","Structure rattachement",'N° structure']]

## préparation Aide_alimentaire Nb_U2A
df_alim = df_alim. rename(columns={"Dispositif":"dispositif","Stucture rattachement" :"Structure", "N° structure":"#struct"})

if 'U2A' in df_alim.columns:
 # Identifier les doublons dans la colonne 'U2A'
    duplicates = df_alim[df_alim['U2A'].duplicated(keep=False)]
    
# Compter le nombre de doublons
    num_duplicates = duplicates.shape[0]
    
    if num_duplicates > 0:
        print(f"Il y a {num_duplicates} lignes avec des doublons dans la colonne 'U2A'.")
        print("Voici les lignes en doublon (affichant toutes les occurrences des valeurs dupliquées) :")
        display(duplicates.sort_values(by='U2A'))
    else:
        print("Aucun doublon trouvé dans la colonne 'U2A'.")
else:
    print("La colonne 'U2A' n'existe pas dans le DataFrame df_alim.")

    print(f"Taille du DataFrame avant suppression des doublons : {df_alim.shape}")
df_alim_sans_doublons = df_alim.drop_duplicates(subset=['U2A'], keep='first')
print(f"Taille du DataFrame après suppression des doublons : {df_alim_sans_doublons.shape}")

display(df_alim_sans_doublons.head())

df_alim_U2A_sans_doublons = df_alim_sans_doublons.groupby("#struct").size().reset_index(name="Aide_alimentaire Nb_U2A")
print(df_alim_U2A_sans_doublons.head())