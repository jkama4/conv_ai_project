import torch
import json
import uuid

from datetime import datetime
from datasets import Dataset
from pathlib import Path
from typing import List, Dict

from .data_sets import setup_repo

def pick_bf16():
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
    
    with open(data_path / "knowledge.json", "r") as f:
        knowledge_base=json.load(f)

    return knowledge_base


def get_history(
    ds: Dataset,
    n: int,
) -> Dict:
    
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
    metadata: Dict | None =None
) -> str:
    
    print("SAVING conversation ...")
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
