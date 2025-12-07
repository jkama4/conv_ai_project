# Environment Setup

Before setting up, make sure Python 3.13 is installed.

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
```

# TODO LIST

1. Nog een manier om te finetune assistant agent
2. Geef 2 persona's aan de user agent
3. Assistant consults knowledge base - how?
4. Design 10 histories voor initialisation van convo - history geeft een context om mee/vanaf te werken
5. Stop mechanism - stop wanner user agent satisfied is
6. Evaluation - LLM-as-judge, Objective metrics (number of tokens, number of turns before completion, etc.)