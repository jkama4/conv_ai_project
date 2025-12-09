def determine_subject_dir(persona: str, rag_based: bool) -> str:
    if persona == "annoying" and not rag_based:
        return "annoying_base"
    if persona == "annoying" and rag_based:
        return "annoying_rag"
    if persona != "annoying" and not rag_based:
        return "nice_base"
    if persona != "annoying" and rag_based:
        return "nice_rag"
    return "failed"
