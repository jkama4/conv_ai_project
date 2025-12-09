from .user_agent import UserAgent
from .assistant_agent import BaseAssistantAgent, RAGAssistantAgent
from .conversational_utils import determine_subject_dir

from . import utils, config, data_sets

from typing import List, Dict, Tuple

from datasets import Dataset


def run_conversation(
    history: List[Dict],
    user_agent: UserAgent,
    assistant_agent: BaseAssistantAgent,
    true_last: Dict,
    n_simulation_turns: int = 5,
):

    print("PHASE 1 - PREDICTING MISSING MESSAGE")

    predict_role = true_last["role"]

    if predict_role == "assistant":
        predicted_text = assistant_agent._call(history)
    else:
        predicted_text = user_agent._call(history)

    predicted_message = {
        "role": predict_role,
        "content": predicted_text
    }

    history.append(predicted_message)

    print("PHASE 2 - CONTINUE SIMULATION")

    current_role = predicted_message["role"]

    for _ in range(n_simulation_turns):
        if current_role == "assistant":
            next_role = "user"
            response = user_agent._call(history)
        else:
            next_role = "assistant"
            response = assistant_agent._call(history)

        new_msg = {"role": next_role, "content": response}
        history.append(new_msg)

        if "<END>" in response:
            break

        current_role = next_role

    return history, predicted_message


def run_program(
    ds: Dataset = data_sets.TEST_DS,
    n_simulation_turns: int = 5,
):

    personas = ["nice", "annoying"]
    assistant_types = ["rag", "base"]

    results = []

    for persona in personas:
        user_agent = UserAgent(persona=persona)

        for atype in assistant_types:

            if atype == "base":
                assistant_agent, _ = BaseAssistantAgent._load_finetuned()
            else:
                assistant_agent, _ = RAGAssistantAgent._load_finetuned()

            for idx, sample in enumerate(ds):

                subject_dir = determine_subject_dir(
                    persona=persona,
                    rag_based=True if atype == "rag" else False
                )
                print(f"CONVERSATION between \'{user_agent.persona} user\' and \'{type(assistant_agent)} based assistant\'")
                
                if idx >= 20:
                    print("Reached limit of 2 samples. Moving to next configuration.\n")
                    break
                
                full_messages = sample["messages"]
                ground_truth = full_messages[-1]
                history = full_messages[:-1].copy()

                conversation, predicted_last = run_conversation(
                    history=history,
                    user_agent=user_agent,
                    assistant_agent=assistant_agent,
                    true_last=ground_truth,
                    n_simulation_turns=n_simulation_turns
                )

                metadata = {
                    "custom": "false" if ds is data_sets.TEST_DS else "true",
                    "persona": persona,
                    "assistant_type": atype,
                    "dataset_index": idx,
                    "ground_truth": ground_truth["content"],
                    "predicted": predicted_last["content"],
                }

                # utils.save_conversation(
                #     history=conversation,
                #     subject_dir=subject_dir,
                #     metadata=metadata
                # )

                print({
                    "metadata": metadata,
                    "conversation": conversation
                })

                break # remove later

                results.append({
                    "metadata": metadata,
                    "conversation": conversation
                })
            break # remove later
    
        break # remove later

    return results


