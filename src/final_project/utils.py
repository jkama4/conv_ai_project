import torch
import json
import subprocess
import shutil

from datasets import Dataset

from pathlib import Path

from typing import Tuple, List, Dict

def pick_bf16():
    if torch.cuda.is_available():
        major, _ = torch.cuda.get_device_capability()
        return major >= 8
    return False


def setup_repo(
    repo_url: str,
    repo_name: str,
    work_dir: Path | None = None,
) -> Path:

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


def format_dialogue(dialogue: List[Dict]) -> List[Dict]:
    messages = []

    messages.append({
        "role": "system",
        "content": "You are a traveler expressing preferences to an assistant."
    })

    for turn in dialogue:
        if turn["speaker"] == "U":
            messages.append({"role": "user", "content": turn["text"]})
        else:
            messages.append({"role": "assistant", "content": turn["text"]})

    return messages


def reformat_dataset(dataset, labels_dataset): 
    reformatted_dataset = {
        "messages": []
    }
    for sample_index in range(len(dataset)): 
        # Your solution here
        try:
            sample_dialogue = format_dialogue(dialogue=dataset[sample_index])
            sample_response = labels_dataset[sample_index]["response"]
            sample_dialogue.append({"role": "system", "content": sample_response})
            
            reformatted_dataset["messages"].append(sample_dialogue)
        except Exception as e:
            continue

    return reformatted_dataset


def get_knowledge_base(
    data_path: Path = setup_repo(
        repo_url="https://github.com/lkra/dstc11-track5.git", 
        repo_name="dstc11-track5",
    )
) -> Dict:
    
    with open(data_path / "knowledge.json", "r") as f:
        knowledge_base=json.load(f)

    return knowledge_base


def create_datasets(
    data_path: Path = setup_repo(
        repo_url="https://github.com/lkra/dstc11-track5.git", 
        repo_name="dstc11-track5",
    ),
) -> Tuple[Dataset]:

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