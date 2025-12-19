import torch
import json
import uuid

from datetime import datetime
from datasets import Dataset
from pathlib import Path
from typing import List, Dict

from .data_sets import setup_repo

def pick_bf16():
    """
    Uses bf16 if available
    """
    if torch.cuda.is_available():
        major, _ = torch.cuda.get_device_capability()
        return major >= 8
    return False


def get_knowledge_base(
    data_path: Path = setup_repo(
        repo_url="https://github.com/lkra/dstc11-track5.git", 
        repo_name="dstc11-track5",
    )
) -> Dict:
    """
    Retrieves the information from the knowledge base
    
    :(param) data_path: path to the data source
    :return: returns the knowledge base
    :rtype: Dict
    """
    
    with open(data_path / "knowledge.json", "r") as f:
        knowledge_base=json.load(f)

    return knowledge_base


def get_history(
    ds: Dataset,
    n: int,
) -> Dict:
    """
    Retrieves and formats the history of a conversation
    
    :(param) ds: the dataset that contains the histories
    :(param) n: the number of messages 
    :type n: int
    :return: Description
    :rtype: Dict
    """
    
    history: List[Dict] = []

    start = max(0, len(ds) - n)

    for i in range(start, len(ds)):
        sample = ds[i]["messages"]
        dialogue = sample[:-1]
        history.append(dialogue)

    return history


def save_conversation(
    history: List[Dict],
    subject_dir: str,
    metadata: Dict | None = None,
    custom: bool = False,
) -> str:
    """
    Stores the conversation when finished

    :(param) history: the conversation (or simply, a history) that is being stored
    :(param) subject_dir: the directory of the corresponding source (custom or DSTC11-track5)
    :(param) metadata: if provided, metadata will be stored (often measured metrics)
    :(param) custom: determines whether to gather conversations from the custom or DSTC11-track5 dataset
    :return: file_path to the stored conversation
    :rtype: Path
    """
    
    print("SAVING conversation ...")

    if custom:
        base_dir = Path(__file__).resolve().parent / "data" / "custom_conversations"
    else:
        base_dir = Path(__file__).resolve().parent / "data" / "conversations"

    folder = base_dir / subject_dir
    folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:8]
    filename = f"conversation_{timestamp}_{uid}.json"
    file_path = folder / filename

    data = {
        "metadata": metadata or {},
        "conversation": history
    }

    with open(file_path, "w", encoding="utf-8") as f:
        print("ACCESSED SAVE FILE")
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("SAVED!")

    return str(file_path)


def get_conversations(
    custom: bool = False
) -> Dict:
    """
    Gather the conversations

    :(param) custom: determines whether to gather conversations from the custom or DSTC11-track5 dataset
    """
    
    if custom:
        path: Path = Path(__file__).parent / "data" / "custom_conversations"
    else:
        path: Path = Path(__file__).parent / "data" / "conversations"
    
    conv_dirs: List[Path] = [x for x in path.iterdir() if x.is_dir()]

    conversations: List[Dict] = []

    for dir in conv_dirs:
        for data_file in dir.iterdir():
            if data_file.is_file() and ".json" in str(data_file.name):

                with open(data_file, "r") as f:
                    data = json.load(f)

                conversations.append(data)

    return conversations


def tensor_to_python(obj):
    if isinstance(obj, torch.Tensor):
        return obj.item()
    return obj


def save_evaluations(
    evaluated_conversations: List[Dict],
    custom: bool = False
) -> None:

    save_path: Path = Path(__file__).parent / "data" / "evaluated_conversations"
    
    if custom:
        save_file: Path = f"{save_path}/custom_evaluated.json"
    else:
        save_file: Path = f"{save_path}/evaluated.json"

    with open(save_file, "w") as f:
        json.dump(evaluated_conversations, f, default=tensor_to_python)
    
    return None


def get_evaluated_conversations(
    custom: bool = False
) -> List[Dict]:

    eval_path: Path = Path(__file__).parent / "data" / "evaluated_conversations"

    if custom:
        file_path: Path = f"{eval_path}/custom_evaluated.json"
    else:
        file_path: Path = f"{eval_path}/evaluated.json"

    with open(file_path, "r") as f:
        data = json.load(f)

    return data