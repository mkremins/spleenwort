from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from statistics import mean
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# Given a list of individual item `embeddings` and a precomputed
# `center` embedding for the whole list, return a list containing the
# semantic similarities of each item to the center.
def similarities_to_center(embeddings, center):
	return [sim[0].item() for sim in util.cos_sim(embeddings, [center])]

# Given a list of `stories`, each one of which is a list of `n` passages,
# return a list of `n` overall homogeneity scores: one for each passage index
# from `0..n`. Homogeneity scores will range from 0 (all passages fully unique)
# to 1 (all passages fully identical).
def evaluate_homogeneity(stories):
	homogeneity_scores = []
	for n in range(len(stories[0])):
		nth_passages = [story[n] for story in stories]
		passage_embs = [model.encode(passage) for passage in nth_passages]
		central_emb = np.mean(passage_embs, axis=0)
		similarity_scores = similarities_to_center(passage_embs, central_emb)
		homogeneity_scores.append(mean(similarity_scores))
	return homogeneity_scores

def load_story(path):
	with open(path, "r") as file:
		return file.readlines()

story_batches_dir = Path("./stories")
subdirs = [path for path in story_batches_dir.iterdir() if path.is_dir()]
for subdir in subdirs:
	premise = subdir.name.split("_")[1]
	print("Premise:", premise)
	guided_story_paths = [p for p in Path(subdir / "guided").iterdir()]
	unguided_story_paths = [p for p in Path(subdir / "unguided").iterdir()]
	guided_stories = [load_story(p) for p in guided_story_paths]
	unguided_stories = [load_story(p) for p in unguided_story_paths]
	print("Guided:", evaluate_homogeneity(guided_stories))
	print("Unguided:", evaluate_homogeneity(unguided_stories))
	print()
