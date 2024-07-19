# Spleenwort
Lightweight ASP guidance for LLM story generation. Currently focused on reducing the *homogeneity* of sets of stories generated with the same prompt, but there are potential controllability advantages too.

## Setup
Clone this repo.

Create a file at the repo root called `openai_api_key.txt` and paste your OpenAI API key into it.

Install necessary Python packages:
* `clingo` to run answer set programs (needed by `gen_outlines.py`)
* `openai` to query the OpenAI API (needed by `gen_stories.py`)
* `sentence_transformers` to evaluate semantic similarity (needed by `eval.py`)

## Workflow
1. Use ASP to generate a complete batch of possible story outlines: `python3 gen_outlines.py`
2. Generate story batches: `python3 gen_stories.py` (takes a while)
3. Evaluate batch homogeneity: `python3 eval.py`

## Papers
Want to learn more, or build on this work? Check out [our paper](https://arxiv.org/abs/2406.00554) at [Wordplay 2024](https://wordplay-workshop.github.io/modern/):
```
@misc{Spleenwort,
  title={Guiding and Diversifying LLM-Based Story Generation via Answer Set Programming},
  author={Phoebe J. Wang and Max Kreminski},
  year={2024},
  eprint={2406.00554},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2406.00554}
}
```

## Spleenwort?
When you try to mash "ASP" and "LLM" together phonetically, the result kinda sounds like "asplenium". This turns out to be the genus name for a group of ferns called "spleenworts". Pretty nifty, right?
