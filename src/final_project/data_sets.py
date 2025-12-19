import shutil
import subprocess
import json

from datasets import Dataset
from typing import Tuple, List, Dict
from pathlib import Path


def format_dialogue(dialogue: List[Dict]) -> List[Dict]:
    """
    Formats a given dialogue in the expected format for the agent

    :(param) dialogue: a dialogue (history)
    :return: the set of formatted messages
    :rtype: List[Dict]
    """
    messages = []

    for turn in dialogue:
        if turn["speaker"] == "U": # U is converted to "user"
            messages.append({"role": "user", "content": turn["text"]})
        elif turn["speaker"] == "S": # S is converted to "assistant"
            messages.append({"role": "assistant", "content": turn["text"]})
        else:
            raise ValueError("Unknown speaker type")

    return messages



def reformat_dataset(dataset, labels_dataset):
    """
    Reformats a complete dataset
    
    :(param) dataset: the dataset which will be formatted
    :(param) labels_dataset: the labels that correspond to the dataset
    """
    reformatted_dataset = {"messages": []}

    for i in range(len(dataset)):
        try:
            sample_dialogue = format_dialogue(dataset[i])

            sample_dialogue.append({
                "role": "assistant",
                "content": labels_dataset[i]["response"]
            })

            reformatted_dataset["messages"].append(sample_dialogue)

        except Exception:
            continue

    return reformatted_dataset

def setup_repo(
    repo_url: str,
    repo_name: str,
    work_dir: Path | None = None,
) -> Path:
    """
    Sets up the dataset repository, if it isn;'t setup yet
    
    :(param) repo_url: URL to the repository of th e dataset
    :(param) repo_name: name of the repository
    :(param) work_dir: the working directory
    :return: returns the directory where the data is stored
    :rtype: Path
    """

    if work_dir is None:
        work_dir = Path(__file__).parent / "data"

    work_dir.mkdir(exist_ok=True, parents=True)

    repo_path = work_dir / repo_name

    if repo_path.exists():
        shutil.rmtree(repo_path)

    subprocess.run(
        ["git", "clone", repo_url, str(repo_path)],
        check=True
    )

    data_dir = repo_path / "data"
    data_dir.mkdir(exist_ok=True)

    return data_dir

def create_datasets(
    data_path: Path = setup_repo(
        repo_url="https://github.com/lkra/dstc11-track5.git", 
        repo_name="dstc11-track5",
    ),
) -> Tuple[Dataset]:
    """
    Sets up all different datasets (train, test, val)
    
    :(param) data_path: path to the data sources directory
    :return: returns the datasets from
    :rtype: Tuple[Dataset]
    """

    with open(data_path / "train/logs.json", "r") as f:
        train_ds = json.load(f)

    with open(data_path / "train/labels.json", "r") as f:
        train_labels = json.load(f)

    with open(data_path / "val/logs.json", "r") as f:
        validation_ds = json.load(f)

    with open(data_path / "val/labels.json", "r") as f:
        validation_labels = json.load(f)

    with open(data_path / "test/logs.json", "r") as f:
        test_ds = json.load(f)

    with open(data_path / "test/labels.json", "r") as f:
        test_labels = json.load(f)

    return train_ds, train_labels, validation_ds, validation_labels, test_ds, test_labels

def setup_datasets() -> Tuple[Dataset]:
    train_ds, train_labels, validation_ds, validation_labels, test_ds, test_labels = create_datasets()

    return (
        Dataset.from_dict(
            reformat_dataset(dataset=train_ds, labels_dataset=train_labels)
        ),
        Dataset.from_dict(
            reformat_dataset(dataset=validation_ds, labels_dataset=validation_labels)
        ),
        Dataset.from_dict(
            reformat_dataset(dataset=test_ds, labels_dataset=test_labels)
        ),
    )

def get_custom_dataset() -> Dataset:
    """
    Retrieves the custom dataset
    
    :return: custom dataset
    :rtype: Dataset
    """

    file_path: Path = Path(__file__).parent / "data" / "custom_histories.json"

    with open(file_path, "r") as f:

        data = json.load(f)

    return Dataset.from_list(data)

TRAIN_DS, VALIDATION_DS, TEST_DS = setup_datasets()

CUSTOM_DATASET = get_custom_dataset()