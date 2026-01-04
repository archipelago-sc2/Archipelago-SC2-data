#!/usr/bin/env python3
# Verifies localization files to contain all the keys
# Detects possibly outdated translations using Git blame
# Fills missing translations with the English texts, so the player will at least see some text

import os
from pathlib import Path
from typing import NamedTuple

from git import *

# Supported localizations
SOURCE_LOCALIZATION = "enUS"
TARGET_LOCALIZATIONS = ["deDE"]

# Files and paths
CHECKED_FILES = ["GameStrings.txt", "GameHotkeys.txt"]
CAMPAIGN_PATHS = ["WoL", "HotS", "LotV", "NCO"]

repo = Repo("./", search_parent_directories=True)
assert not repo.bare
project_dir = repo.working_tree_dir

def checked_files(basepath: str, localization: str) -> list[str]:
    return [basepath + os.sep + localization + ".SC2Data" + os.sep + "LocalizedData" + os.sep + checked_file for checked_file in CHECKED_FILES]

class LocalizationEntry(NamedTuple):
    commit: Commit
    value: str

def process_document(document):
    if document.is_dir():
        document_relative_path = document.relative_to(project_dir)
        document_data = dict()
        for file in checked_files(document.as_posix(), SOURCE_LOCALIZATION):
            filepath = Path(file)
            if filepath.exists() and filepath.is_file():
                filename = filepath.name
                document_data[filename] = dict()
                for commit, lines in repo.blame('HEAD', file):
                    for line in lines:
                        key, value = line.split("=", maxsplit=1)
                        document_data[filename][key] = LocalizationEntry(commit, value)
        for target_localization in TARGET_LOCALIZATIONS:
            localization_path = Path(document.as_posix() + os.sep + target_localization + ".SC2Data")
            if localization_path.exists() and localization_path.is_dir():
                ignored_files = list()
                for file in checked_files(document.as_posix(), target_localization):
                    file_path = Path(file)
                    filename = Path(file).name
                    present_keys_commits = dict()
                    try:
                        if file_path.exists() and file_path.is_file():
                            (repo.head.commit.tree / file_path.relative_to(project_dir).as_posix())
                            for commit, lines in repo.blame('HEAD', file):
                                for line in lines:
                                    key, value = line.split("=", maxsplit=1)
                                    present_keys_commits[key] = commit
                        else:
                            ignored_files.append(filename)
                    except KeyError as e:
                        ignored_files.append(filename)
                    for key, commit in present_keys_commits.items():
                        if key in document_data[filename] and filename not in ignored_files:
                            source_commit = document_data[filename][key].commit
                            if not repo.is_ancestor(source_commit, commit):
                                print(f"{document_relative_path}: {target_localization}: {filename}:{key} might be outdated")
                    if filename in document_data and filename not in ignored_files:
                        for key, holder in document_data[filename].items():
                            if key not in present_keys_commits.keys():
                                with open(file_path, "a+") as f:
                                    f.write(f"{key}={holder.value}\n")
                                    print(
                                        f"{document_relative_path}: {target_localization}: {filename}:{key} is missing. Filling the default localization.")


for mod in Path(project_dir + os.sep + "Mods").iterdir():
    process_document(mod)

for campaign in CAMPAIGN_PATHS:
    for sc2_map in Path(project_dir + os.sep + "Maps" + os.sep + "ArchipelagoCampaign" + os.sep + campaign).iterdir():
        process_document(sc2_map)