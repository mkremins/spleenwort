from datetime import datetime
from openai import OpenAI
from pathlib import Path
import random

### OpenAI/LLM functionality

oai_api_key = open("openai_api_key.txt").read()
oai_client = OpenAI(api_key=oai_api_key)
# Define the GPT model to use
GPT_MODEL = "gpt-3.5-turbo"# or "gpt-4-turbo"

# outline-based story generation: translate an ASP-generated outline
# and a brief user input text into a sequence of LLM prompts

init_prompt = """
You're writing a story about:

{{user_input_text}}

Write the first paragraph of the story. In this paragraph, {{follow_instruction}}.
""".strip()

followup_prompt = """
Write the next paragraph of the story. Remember the story is about: {{user_input_text}}. In this paragraph, {{follow_instruction}}.
""".strip()

# add an extra prompts for obstacles
obstacle_prompt = """
Given the story theme: {{user_input_text}}

Write a list of five obstacles that could block the protagonist's major goal in the story. Use less than 5 words for each obstacle.
""".strip()

instructions_by_function = {
  "introduce_character":
    "introduce a character we haven't introduced already",
  "introduce_rival_character":
    #"introduce a rival character to a previous introduced character. Establish the reasons behind their rivalry, which may stem from differing upbringings, conflicting interests, or a history of antagonism between them. Ensure that the rival's introduction contributes to the progression of the plot, the development of the existing character, or the overall theme of the story. Seamlessly integrate the rival character into the ongoing narrative, maintaining the story's cohesion and flow",
    "introduce an enemy character to a previous introduced character. Establish a clear and convincing reason for their hatred or antagonism towards the existing character. This could stem from a past betrayal, ideological differences, or a long-standing rivalry. Provide enough context to make the enemy's feelings and actions understandable. Ensure that the enemy's introduction contributes to the progression of the plot, the development of the existing character, or the overall theme of the story. Seamlessly integrate the enemy character into the ongoing narrative, maintaining the story's cohesion and flow",
  "introduce_character:cold":
    "introduce a new, cold, and solitary character would fit organically. Consider how this character's presence can be connected to the current plot, setting, or other characters. Craft a scene or situation that allows for a smooth integration of this character, ensuring that their introduction doesn't feel forced or disconnected from the narrative. Provide context for their cold and solitary nature through their actions, dialogue, or the reactions of other characters, while maintaining the flow and consistency of the story. This character's introduction should contribute to the development of the plot or the growth of other characters in a meaningful way, while maintaining the flow and consistency of the story",
  "introduce_character:sunny":
    "introduce an optimistic and brave character who would fit organically. Consider how this character's presence can be connected to the current plot, setting, or other characters. Craft a scene or situation that allows for a smooth integration of this character, ensuring that their introduction doesn't feel forced or disconnected from the narrative. Provide context for their sunny and brave nature through their actions, dialogue, or the reactions of other characters, while maintaining the flow and consistency of the story. This character's introduction should contribute to the development of the plot or the growth of other characters in a meaningful way, while maintaining the flow and consistency of the story",
  "introduce_character:clumsy":
    "introduce a character who is innocent and adorable, often acts in a laughably naive way. Show their personality through their actions, dialogue, or the reactions of other characters. This character's introduction should contribute to the development of the plot or the growth of other characters in a meaningful way, while maintaining the flow and consistency of the story",
  "introduce_character:smart":
    "introduce a character who is intellectually agile, skilled in strategy and planning, provides wisdom and support at crucial moments. Show their personality through their actions, dialogue, or the reactions of other characters. This character's introduction should contribute to the development of the plot or the growth of other characters in a meaningful way, while maintaining the flow and consistency of the story",
  "introduce_character:mysterious":
    "introduce a character who is full of mysteries, difficult to understand, whose true motives are hard to read. Show their personality through their actions, dialogue, or the reactions of other characters. This character's introduction should contribute to the development of the plot or the growth of other characters in a meaningful way, while maintaining the flow and consistency of the story",
  "introduce_character:quirky":
    "introduce a character who is quirky and eccentric, marches to the beat of their own drum, highly imaginative with unusual habits and mannerisms. Show their personality through their actions, dialogue, or the reactions of other characters. This character's introduction should contribute to the development of the plot or the growth of other characters in a meaningful way, while maintaining the flow and consistency of the story",
  "describe_setting":
    "describe the place where the characters are",
  "make_reader_sad":
    "convey an atmosphere of sadness",
  "make_reader_angry":
    "convey an atmosphere of anger",
  "add_conflict_between_characters":
    "introduce an event that adds conflicts between two previously introduced characters",  
  "add_bonding_between_characters":
    "introduce a shared experience, challenge, or moment of vulnerability that strengthens the emotional connection and understanding between two previously established characters. This event should reveal new depths to their relationship, highlight their complementary qualities, or demonstrate their ability to support and rely on one another in meaningful ways. Ensure the event flows naturally from the story's preceding events and character development, and that it contributes to the overall narrative arc",
  "add_obstacle_towards_major_goal":
    "introduce an obstacle that blocks the major goal of the protagonist, for example: {{obstacle_hint}}",
  "add_breakthrough":
    "introduce a significant development, discovery, or event that naturally advances the protagonist's primary objective or helps them overcome a major obstacle in their journey. Ensure this breakthrough feels organic to the story and aligns with the established plot, characters, and setting",
  "add_twist":
    "add a plot twist",
  "add_obstacle:betrayal":
    "introduces an obstacle for a previously established character where they face a betrayal by someone they trusted. The betrayal should arise organically from the plot and character dynamics you have already built in the preceding paragraphs. Describe how the character discovers this betrayal and their initial reaction to it. The betrayal should drive the story forward, while maintaining the flow and cohesion of the story",
  "add_obstacle:supernatural":
    "introduce a new obstacle for a previously established character in the story. The obstacle should involve the character encountering a supernatural power or force or entity. Describe the nature of this supernatural element, how it manifests, and the immediate impact it has on the character. Show the character's initial reaction, whether it's shock, fear, confusion, or curiosity. Ensure that the obstacle is relevant to the character's established traits, backstory, and narrative arc, and that it creates genuine tension and challenges for them to face, thereby driving the story forward and contributing to their overall development, while maintaining the flow and consistency of the story",
  "add_obstacle:forbidden_love":
    "introduces an obstacle for a previously established character, where character starts to fall in love with someone they are not supposed to, such as a rival character or someone from a very different social class or group that makes the love forbidden or problematic. Introduce this forbidden love interest and the character's feelings in a way that feels natural and interesting given the story so far. Maintain the flow and cohesion of the story",
  "add_obstacle:opposition":
    "introduce a new obstacle for a previously established character in the story. The obstacle should involve the character facing significant opposition or conflict from other characters, society, or nature. Ensure that the obstacle is relevant to the character's established traits, backstory, and narrative arc, and that it creates genuine tension and challenges for them to face, thereby driving the story forward and contributing to their overall development",
  "add_obstacle:guilt":
    "introduce a situation where a previously established character confronts a moral dilemma or the consequences of a past mistake that evokes a deep sense of guilt and inner turmoil. This obstacle should stem from a choice, action, or inaction in the character's past that they deeply regret, and which now haunts them. The character's guilt should manifest through introspection, self-doubt, and a struggle to reconcile their past actions with their present moral compass. Ensure that this obstacle and the character's emotional struggle are woven cohesively into the narrative, building upon their established traits, relationships, and arc, while also creating opportunities for profound character development and driving the story forward",
  "level_up_obstacle":
    "introduce an event that levels up or intensify the previously introduced obstacle in an interesting way that fits with the story so far",
}

# try to control the length of each paragraph
def get_random_sentence_count():
    return random.randint(1, 7)

def promptify_outline(outline, user_input_text):
  prompts = []
  obstacle_hint = "" #get llm to generate examples first

  for i in range(len(outline)):
    is_first_paragraph = i == 0
    function = outline[i]

    if function == "add_obstacle_towards_major_goal":
      # Generate the list of possible obstacles
      obstacle_prompt_text = obstacle_prompt.replace("{{user_input_text}}", user_input_text)
      messages = [{"role": "user", "content": obstacle_prompt_text}]
      completion = oai_client.chat.completions.create(
        messages=messages, model=GPT_MODEL
      )
      obstacle_hint = completion.choices[0].message.content.strip()
      print("obstacle_hint:"+obstacle_hint)

    instruction = instructions_by_function[function]

    if function == "add_obstacle_towards_major_goal":
      # Include the obstacle hint in the instruction
      instruction = instruction.replace("{{obstacle_hint}}", obstacle_hint)

    # Generate a random sentence count for each paragraph
    sentence_count = get_random_sentence_count()
    instruction += f" Use {sentence_count} sentences in the paragraph."

    prompt_template = init_prompt if is_first_paragraph else followup_prompt
    prompt = prompt_template.replace("{{follow_instruction}}", instruction)
    if is_first_paragraph:
      prompt = prompt.replace("{{user_input_text}}", user_input_text)
    prompts.append(prompt)
  return prompts

# naive baseline story generation: translate a number of paragraphs
# and a brief user input text into a sequence of LLM prompts

naive_init_prompt = """
You're writing a story about:

{{user_input_text}}

Write the first paragraph of the story.
""".strip()

naive_followup_prompt = """
Write the next paragraph of the story. Remember the story is about: {{user_input_text}}.
""".strip()

def promptify_naively(num_paras, user_input_text):
  prompts = []
  for i in range(num_paras):
    is_first_paragraph = i == 0
    prompt = naive_init_prompt if is_first_paragraph else naive_followup_prompt

    # Generate a random sentence count for each paragraph
    sentence_count = get_random_sentence_count()
    prompt += f" Use {sentence_count} sentences in the paragraph."

    if is_first_paragraph:
      prompt = prompt.replace("{{user_input_text}}", user_input_text)
    prompts.append(prompt)
  return prompts

# run a sequence of LLM prompts generated by one of the above approaches,
# and extract the finished story from the LLM responses
def storify_prompts(prompts):
	messages = []
	# adding a system prompt to make the language precise
	messages.append({
	  "role": "system",
	  "content": "You're a fiction writer. You use simple and clear language that best conveys your meaning. You don't use big words just to sound impressive. You are also a master of the writing skill -  \"Show, don't tell.\" You use details, actions, and dialogues to show the characters and events. \n\n- Use simple, concrete words rather than complex, abstract, or vague language. For example, instead of saying \"The weather was unpleasant\", you could say \"Icy rain pelted my face and soaked through my thin jacket.\"\n\n- Pack a high density of information and detail into each sentence. Make every word count. \n\n- Show what's happening through description and action rather than simply telling or summarizing. For example, instead of \"John was angry\", write \"John slammed his fist on the table, his face reddening.\"\n\n- Engage the senses by describing how things look, feel, sound, smell, and taste. Transport the reader into the scene.\n\n- Avoid cliches, well-worn phrases, and generic descriptions. Use unexpected and vivid details to make your story unique."
	})
	for prompt in prompts:
		# prompt the LLM for the next paragraph
		messages.append({"role": "user", "content": prompt})
		completion = oai_client.chat.completions.create(
			messages=messages, model=GPT_MODEL
		)
		# append response message as context for future paragraphs
		paragraph = completion.choices[0].message.content.strip()
		messages.append({"role": "assistant", "content": paragraph})
		#print(paragraph + "\n")
	return [msg["content"] for msg in messages if msg["role"] == "assistant"]

# load outlines from file so we can sample them as needed
all_outlines = []
with open("outlines.csv", "r") as outlines_file:
	lines = outlines_file.read().splitlines()
	all_outlines = [line.split(",") for line in lines if line != ""]

# generate guided and unguided story batches for a given premise
def gen_story_batches(premise, num_stories=10):
	# make directories for story file output
	timestamp = datetime.now().strftime("%Y%m%d%H%M")
	output_dir = timestamp + "_" + premise
	Path(f"./stories/{output_dir}/guided").mkdir(parents=True, exist_ok=True)
	Path(f"./stories/{output_dir}/unguided").mkdir(parents=True, exist_ok=True)
	print(f"Generating ./stories/{output_dir}...")
	# generate stories into appropriate directories
	for i in range(num_stories):
		outline = random.choice(all_outlines)
		print("Using outline:", outline)
		guided_prompts = promptify_outline(outline, premise)
		unguided_prompts = promptify_naively(len(outline), premise)
		guided_story = storify_prompts(guided_prompts)
		unguided_story = storify_prompts(unguided_prompts)
		with open(f"./stories/{output_dir}/guided/{i}.txt", "w") as story_file:
			story_file.write("\n".join(guided_story))
		with open(f"./stories/{output_dir}/unguided/{i}.txt", "w") as story_file:
			story_file.write("\n".join(unguided_story))

# define test set of premises
premise_prompts = [
  "cat pirate",
  "Cold Emu War",
  "tower of eyeballs",
  "dwarven courtroom drama",
  "noir restaurant duel",
  "starships shaped like organs"
]

# generate a 10-story batch for each test premise (takes a while)
for premise in premise_prompts:
  gen_story_batches(premise)
