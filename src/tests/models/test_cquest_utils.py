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


def test_flatten_folder():
    # Create the structure
    create_folder_structure()

    # Call the function tested
    flatten_folder("test_folder")

    # Check content
    assert sorted(os.listdir("test_folder")) == ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt']

    # Delete folder
    shutil.rmtree("test_folder")
