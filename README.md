Main Research Question:
What is the differential effect of lexical-based keyword knowledge base access on the conversational assistant agent's performance and generalization across in-domain (DSTC11-track5) and out-of-domain travel assistance scenarios, as measured by objective and subjective evaluation metrics?

Sub-Research Question 1:
To what extent do the assistant agent's objective (BLEU, ROUGE, BERTScore) and subjective (task success, coherence) evaluation scores degrade when shifting from the in-domain DSTC11-track5 dataset to custom out-of-domain conversation histories, and is this degradation moderated by the presence of the knowledge base?

Sub-Research Question 2:
How does the user agent's behavior (annoying vs. nice) influence the assistant agent's subjective performance scores (pleasantness, coherence, and task success)?

# Environment Setup

Before setting up, make sure Python 3.13 is installed. You also need a C++ compiler. To set that up, follow the final section.


## No Virtual env (pip)
If you don't Poetry to manage dependencies, you can simply use the following command

```bash
pip install requirements.txt
```

## Using Virtual env (recommended)
First, ensure Poetry is installed

```bash
pip install poetry
```

Then, you should move to the directory where you set up the project

```bash
cd ~/path/to/project
```

Now, you should setup the environment

```bash
poetry install
```

And to use it, you call

```bash
$(poetry env activate)
```

Or on Windows

```bash
poetry env activate
# or alternatively:
poetry shell
```

## Setting up C++ compiler

### Unix (macOS/Linux)
For macOS, it is relatively simple, just run the following commands

```bash
xcode-select --install
```

Agree to install. Then, use

```bash
brew install gcc
```

When finished, confirm with

```bash
gcc --version
```

### Windows
Robin moet ff maken dan denk ik


# TODO LIST

1. Nog een manier om te finetune assistant agent
2. Geef 2 persona's aan de user agent
3. Assistant consults knowledge base - how?
4. Design 10 histories voor initialisation van convo - history geeft een context om mee/vanaf te werken
5. Stop mechanism - stop wanner user agent satisfied is
6. Evaluation - LLM-as-judge, Objective metrics (number of tokens, number of turns before completion, etc.)



# Using objective metrics: number of turns before completion, length of the conversation (number of tokens), etc.