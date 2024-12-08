import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime

# Définir la date d'aujourd'hui
DATE = datetime.now().strftime("%d-%m")

# Définir le dossier 'data'
data_folder = os.path.join(os.getcwd(), 'data')

# Vérifier si le dossier 'data' existe, sinon le créer
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

"""------------------------------------- Extraire les numéros EuroMillions ------------------------------------"""
def sauvegarder_html(url, fichier_html):
    """Récupère les données du site web et les enregistre dans un fichier HTML."""
    response = requests.get(url)
    if response.status_code == 200:
        folder_path = os.path.join(data_folder, DATE)

        # Vérifier si le sous-dossier pour la date existe, sinon le créer
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, fichier_html)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Les données ont été sauvegardées dans le fichier", file_path)
    else:
        print("Impossible de récupérer les données du site web.")

def extraire_et_enregistrer(html_source, debut_balise, fin_balise, fichier_sortie):
    """Extrait les données entre les balises spécifiées et les enregistre dans un fichier HTML."""
    with open(html_source, 'r', encoding='utf-8') as f:
        html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        debut = soup.find(debut_balise)
        fin = soup.find(fin_balise)

        if debut and fin:
            contenu = ''.join(str(tag) for tag in debut.find_all_next() if tag != fin)
            folder_path = os.path.join(data_folder, DATE)

            # Vérifier si le sous-dossier pour la date existe, sinon le créer
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            file_path = os.path.join(folder_path, fichier_sortie)

            with open(file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(contenu)
            print("Les données ont été extraites et sauvegardées dans le fichier", file_path)
        else:
            print("Les balises spécifiées n'ont pas été trouvées dans le fichier HTML.")

def extraire_tables(html_source, fichier_table1, fichier_table2):
    """Extrait le contenu de chaque table et l'enregistre dans un fichier HTML distinct."""
    with open(html_source, 'r', encoding='utf-8') as f:
        html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')

        if len(tables) >= 2:
            folder_path = os.path.join(data_folder, DATE)

            # Vérifier si le sous-dossier pour la date existe, sinon le créer
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            fichier_table1_path = os.path.join(folder_path, fichier_table1)
            fichier_table2_path = os.path.join(folder_path, fichier_table2)

            contenu_table1 = str(tables[0])
            if not os.path.exists(fichier_table1_path):
                with open(fichier_table1_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(contenu_table1)
                print("Le contenu de la première table a été extrait et sauvegardé dans le fichier", fichier_table1)
            else:
                print("Le fichier", fichier_table1, "existe déjà.")

            contenu_table2 = str(tables[1])
            if not os.path.exists(fichier_table2_path):
                with open(fichier_table2_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(contenu_table2)
                print("Le contenu de la deuxième table a été extrait et sauvegardé dans le fichier", fichier_table2)
            else:
                print("Le fichier", fichier_table2, "existe déjà.")
        else:
            print("Au moins deux tables doivent être présentes dans le fichier HTML.")

def sauvegarder_html_Reducmiz(url, fichier_html):
    """Récupère les données du site web et les enregistre dans un fichier HTML."""
    response = requests.get(url)
    if response.status_code == 200:
        folder_path = os.path.join(data_folder, DATE)

        # Vérifier si le sous-dossier pour la date existe, sinon le créer
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = os.path.join(folder_path, fichier_html)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Les données ont été sauvegardées dans le fichier", file_path)
    else:
        print("Impossible de récupérer les données du site web.")

def extraire_data(html_file, table_index, output_file):
    """Extrait les données d'une table HTML et les enregistre dans un fichier HTML."""
    with open(html_file, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all("table")

    if len(tables) > table_index:
        table = tables[table_index]
        data = []

        for row in table.find_all("tr"):
            row_data = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
            data.append(row_data)

        folder_path = os.path.join(data_folder, DATE)

        # Vérifier si le sous-dossier pour la date existe, sinon le créer
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        output_file_path = os.path.join(folder_path, output_file)

        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_html(output_file_path, index=False)

        print(f"Les données de la table {table_index} ont été extraites et enregistrées dans {output_file_path}")
    else:
        print(f"La table {table_index} n'existe pas dans le fichier HTML.")

def execute():
    """Exécute l'extraction des données Reducmiz et EuroMillions."""
    urlReducmiz = 'https://www.reducmiz.com/euromillions.php?algorithme=1'
    fichier_html = DATE + '_donnees_reducmiz.html'
    sauvegarder_html_Reducmiz(urlReducmiz, fichier_html)
    extraire_data(os.path.join(data_folder, DATE, fichier_html), 2, DATE + '_TableSortie.html')
    extraire_data(os.path.join(data_folder, DATE, fichier_html), 3, DATE + '_TableRaport.html')

    url_Plus_Moins = 'https://www.tirage-euromillions.net/euromillions/statistiques/numeros-moins-joues/'
    fichier_html_Plus_Moins = DATE + '_plusAuMoinJoue.html'
    sauvegarder_html(url_Plus_Moins, fichier_html_Plus_Moins)

def main():
    """Lance l'extraction des données."""
    print("Début de l'extraction des données...", datetime)
    print("-------------------------------------------------")
    url = 'https://www.tirage-euromillions.net/euromillions/statistiques/nombre-de-sorties-des-numeros/'
    sauvegarder_html(url, DATE + '_donnees_euromillions.html')
    extraire_et_enregistrer(os.path.join(data_folder, DATE, DATE + '_donnees_euromillions.html'), 'h2', 'p', DATE + '_donnees_extraits.html')
    tableNombres = DATE + '_tableNombres.html'
    tableEtoiles = DATE + '_tableEtoiles.html'
    extraire_tables(os.path.join(data_folder, DATE, DATE + '_donnees_extraits.html'), tableEtoiles, tableNombres)
    print("Les données EuroMillions ont été extraites avec succès.")
    execute()
    print("-------------------------------------------------")
    print("Les données Reducmiz ont été extraites avec succès.", datetime)

if __name__ == "__main__":
    main()
