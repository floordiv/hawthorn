import os


def from_folder(folder, file_filter=lambda file: file.endswith('.py') and '__' not in file):
    if not folder.endswith('/'): folder += '/'

    folder_content = os.listdir(folder)
    ignore_list = ['.git', 'ignore', '__init__.py']

    if 'ignore' in folder_content:
        with open(folder + 'ignore') as ignore_list_file:
            ignore_list += [file[:-1] for file in ignore_list_file.readlines()]

    files_list = []

    for file in folder_content:
        if file not in ignore_list and file_filter(file):
            files_list += [file]

    return files_list
