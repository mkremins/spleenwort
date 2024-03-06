from clingo.control import Control
from clingo.symbol import SymbolType
from openai import OpenAI
import random

### Clingo/ASP functionality

def exprify_symbol(sym):
  if sym.type == SymbolType.Number:
    return sym.number
  elif sym.type == SymbolType.String:
    return sym.string
  elif sym.type == SymbolType.Function and len(sym.arguments) == 0:
    return sym.name
  elif sym.type == SymbolType.Function:
    return [sym.name, *[exprify_symbol(arg) for arg in sym.arguments]]
  else:
    raise ["BAD SYMBOL", sym]

def generate_outlines():
  # helper callback to collect valid story outlines as they're generated
  all_outlines = []
  def collect_outline(model):
    # get shown symbols from the model and translate them to lispy exprs
    syms = model.symbols(shown=True)
    exprs = [exprify_symbol(sym) for sym in syms]
    # assume all exprs are of the form ["scene_performs_function", idx, fn];
    # extract a story outline consisting of fns sorted by idx
    exprs.sort(key=lambda expr: expr[1])
    outline = [expr[2] for expr in exprs]
    all_outlines.append(outline)
    print(outline)
  # invoke clingo to start solving
  ctl = Control()
  ctl.configuration.solve.models = 0 # enumerate all models
  ctl.load("./plotgen.lp")
  ctl.ground()
  ctl.solve(on_model=collect_outline, on_unsat=lambda: print("UNSAT"))
  # when clingo finishes, return collected outlines
  return all_outlines

### OpenAI/LLM functionality

oai_api_key = open("openai_api_key.txt").read()
oai_client = OpenAI(api_key=oai_api_key)

# outline-based story generation: translate an ASP-generated outline
# and a brief user input text into a sequence of LLM prompts

init_prompt = """
I'm trying to write a story. Here's some notes on what I want it to be about:

{{user_input_text}}

Write the first paragraph of the story. In this paragraph, {{follow_instruction}}.
""".strip()

followup_prompt = """
Write the next paragraph of the story. In this paragraph, {{follow_instruction}}.
""".strip()

instructions_by_function = {
  "introduce_character":
    "introduce a character we haven't introduced already",
  "describe_setting":
    "describe the place where the characters are",
  "add_conflict_between_characters":
    "describe a source of conflict between two previously introduced characters",
  "make_reader_sad":
    "convey an atmosphere of sadness",
  "make_reader_happy":
    "convey an atmosphere of happiness",
  "make_reader_angry":
    "convey an atmosphere of anger",
}

def promptify_outline(outline, user_input_text):
  prompts = []
  for i in range(len(outline)):
    is_first_paragraph = i == 0
    function = outline[i]
    instruction = instructions_by_function[function]
    prompt_template = init_prompt if is_first_paragraph else followup_prompt
    prompt = prompt_template.replace("{{follow_instruction}}", instruction)
    if is_first_paragraph:
      prompt = prompt.replace("{{user_input_text}}", user_input_text)
    prompts.append(prompt)
  return prompts

# naive baseline story generation: translate a number of paragraphs
# and a brief user input text into a sequence of LLM prompts

naive_init_prompt = """
I'm trying to write a story. Here's some notes on what I want it to be about:

{{user_input_text}}

Write the first paragraph of the story.
""".strip()

naive_followup_prompt = """
Write the next paragraph of the story.
""".strip()

def promptify_naively(num_paras, user_input_text):
  prompts = []
  for i in range(num_paras):
    is_first_paragraph = i == 0
    function = outline[i]
    instruction = instructions_by_function[function]
    prompt = naive_init_prompt if is_first_paragraph else naive_followup_prompt
    if is_first_paragraph:
      prompt = prompt.replace("{{user_input_text}}", user_input_text)
    prompts.append(prompt)
  return prompts

# run a sequence of LLM prompts generated by one of the above approaches,
# and extract the finished story from the LLM responses

def storify_prompts(prompts):
  # translate a sequence of LLM prompts into a story
  messages = []
  sentences = []
  for prompt in prompts:
    # prompt the LLM for the next paragraph
    messages.append({"role": "user", "content": prompt})
    completion = oai_client.chat.completions.create(
      messages=messages, model="gpt-3.5-turbo"
    )
    # append response message as context for future paragraphs
    paragraph = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": paragraph})
    print(paragraph + "\n")
    # ask for a summary of the previous paragraph
    messages.append({
      "role": "user",
      "content": "Summarize the previous paragraph as a single sentence."
    })
    summary = oai_client.chat.completions.create(
      messages=messages, model="gpt-3.5-turbo"
    ).choices[0].message.content
    sentences.append(summary)
    print("SUMMARY: " + summary + "\n")
  # parse story out of messages
  #paragraphs = [msg["content"] for msg in messages if msg["role"] == "assistant"]
  return "\n".join(sentences)

# Function to read pre-generated outlines from a file
def read_pre_generated_outlines(file_path):
    outlines = []
    with open(file_path, 'r') as file:
        for line in file:
            # Assuming each line is a valid Python list in string format
            outline = eval(line.strip())
            outlines.append(outline)
    return outlines

### tie it all together

# generate story outlines
#outlines = generate_outlines()
#print(outlines)

#read outlines from pre-generated outlines
outlines = read_pre_generated_outlines('pregenerated_outlines.txt')

# storify an outline
print("### OUTLINE")
outline = random.choice(outlines) # TODO pick at random?>> is it not random? 
print(outline)
user_input_text = "cat pirates"
outline_prompts = promptify_outline(outline, user_input_text)
print(storify_prompts(outline_prompts))

# storify naively (same number of paragraphs)
print("### NAIVE")
naive_prompts = promptify_naively(len(outline), user_input_text)
print(storify_prompts(naive_prompts))
