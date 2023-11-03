import os
import shutil

from models.home import flatten_folder


def create_folder_structure():
    # Create structure
    os.makedirs("test_folder/subfolder1")
    os.makedirs("test_folder/subfolder2")
    os.makedirs("test_folder/subfolder1/subsubfolder1")

    with open("test_folder/file1.txt", "w") as file:
        file.write("Contenu du fichier 1")

    with open("test_folder/subfolder1/file2.txt", "w") as file:
        file.write("Contenu du fichier 2")

    with open("test_folder/subfolder2/file3.txt", "w") as file:
        file.write("Contenu du fichier 3")

    with open("test_folder/subfolder1/subsubfolder1/file4.txt", "w") as file:
        file.write("Contenu du fichier 4")



