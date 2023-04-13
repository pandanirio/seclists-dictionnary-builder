from github import Github
import os
import glob
from inquirer import Checkbox, List, Text, prompt
from tqdm import tqdm
import signal
import configparser

config = configparser.ConfigParser()

if os.path.isfile('config.ini'):
    config.read('config.ini')
    token = config.get('github', 'token')
else:
    questions = [
        Text('token', message='Enter your GitHub token :', default=''),
    ]
    answers = prompt(questions)
    token = answers['token']

    config['github'] = {'token': token}

    with open('config.ini', 'w') as config_file:
        config.write(config_file)
        


def handle_sigint(signal, frame):
    print('\nExiting...')
    exit(0)

signal.signal(signal.SIGINT, handle_sigint)

g = Github(token)

answers = prompt([Text('outputFile', message='Enter the output filename :', default='output.txt')])
outputFilename = answers['outputFile']

repo = g.get_repo("danielmiessler/SecLists")

def get_dictionnary_files():
    txt_files = []
    contents = repo.get_contents("")
    pbar = tqdm(total=len(contents), unit=' files', desc='Retrieving file list')
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            if file_content.path.endswith(".txt"):
                txt_files.append(file_content.path)
        pbar.update(1)
    return txt_files

def select_files():
    txt_files = get_dictionnary_files()
    choices = []
    for file_path in txt_files:
        file_parts = file_path.split("/")
        for i in range(len(file_parts)):
            folder_path = "/".join(file_parts[:i+1])
            if i == len(file_parts) - 1:
                choices.append((file_path, file_path))

    questions = [
        Checkbox('files', message='Select files to concatenate', choices=choices),
    ]
    answers = prompt(questions)
    return answers.get('files')

def generate_file(selected_files):
    with open(outputFilename, "w") as outfile:
        for file_path in selected_files:
          try:
            file_content = repo.get_contents(file_path, ref="master").decoded_content.decode('utf-8')
            outfile.write(file_content)
          except:
            print(f"Ignore error on file {file_path}")
            continue

def main():
    selected_files = select_files()
    generate_file(selected_files)
    print(f"{len(selected_files)} files were concatenated into {outputFilename}")

if __name__ == "__main__":
    main()
