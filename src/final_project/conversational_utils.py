def determine_subject_dir(persona: str, rag_based: bool) -> str:
    """
    Determines which conversation pair should be retrieved
    
    :(param) persona: the persona of the user (nice or annoying)
    :(param) rag_based: the version of the assistant (lexical based or non-lexical based)
    :return: returns the name of the directory (agent pair)
    :rtype: str
    """

    if persona == "annoying" and not rag_based:
        return "annoying_base"
    if persona == "annoying" and rag_based:
        return "annoying_rag"
    if persona != "annoying" and not rag_based:
        return "nice_base"
    if persona != "annoying" and rag_based:
        return "nice_rag"
    return "failed"
