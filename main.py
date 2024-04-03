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

# def generate_outlines():
#   # helper callback to collect valid story outlines as they're generated
#   all_outlines = []
#   def collect_outline(model):
#     # get shown symbols from the model and translate them to lispy exprs
#     syms = model.symbols(shown=True)
#     exprs = [exprify_symbol(sym) for sym in syms]
#     # assume all exprs are of the form ["scene_performs_function", idx, fn];
#     # added character personality for introduction, looks like, scene_performs_function(1, introduce_character),scene_introduce_personality(1, cold)
#     # extract a story outline consisting of fns sorted by idx
#     exprs.sort(key=lambda expr: expr[1])
#     outline = [expr[2] for expr in exprs]
#     all_outlines.append(outline)
#     print(outline)
#   # invoke clingo to start solving
#   ctl = Control()
#   ctl.configuration.solve.models = 0 # enumerate all models
#   ctl.load("./plotgen.lp")
#   ctl.ground()
#   ctl.solve(on_model=collect_outline, on_unsat=lambda: print("UNSAT"))
#   # when clingo finishes, return collected outlines
#   return all_outlines

#update the generate outline function with new output format
def generate_outlines():
    # helper callback to collect valid story outlines as they're generated
    all_outlines = []

    def collect_outline(model):
        # get shown symbols from the model
        syms = model.symbols(shown=True)

        # create a dictionary to store scene information
        scene_info = {}

        # extract the symbols and their arguments
        for sym in syms:
            # check if the symbol represents a scene performing a function
            if sym.name == "scene_performs_function":
                # extract the scene index from the first argument
                scene_index = sym.arguments[0].number
                # extract the function name from the second argument
                function_name = sym.arguments[1].name
                # add the function name to the corresponding scene index in the scene_info dictionary
                scene_info.setdefault(scene_index, []).append(function_name)
            # check if the symbol represents a scene introducing a personality
            elif sym.name == "scene_introduce_personality":
                # extract the scene index from the first argument
                scene_index = sym.arguments[0].number
                # extract the personality from the second argument
                personality = sym.arguments[1].name
                # add the personality to the corresponding scene index in the scene_info dictionary
                scene_info.setdefault(scene_index, []).append(personality)

        # create the outline list in the desired format
        outline = []
        # iterate over the sorted scene indices in the scene_info dictionary
        for scene_index in sorted(scene_info.keys()):
            # get the scene functions and personalities for the current scene index
            scene_functions = scene_info[scene_index]
            # check if the scene has more than one function/personality
            if len(scene_functions) > 1:
                # join the function name and personality with a comma and append to the outline list
                outline.append(f"{scene_functions[0]},{scene_functions[1]}")
            else:
                # append the single function name to the outline list
                outline.append(scene_functions[0])

        # append the outline list to the all_outlines list
        all_outlines.append(outline)
        # print the outline for debugging purposes
        print(outline)

    # create a Clingo control object
    ctl = Control()
    # set the configuration to enumerate all models
    ctl.configuration.solve.models = 0
    # load the ASP program from the "plotgen.lp" file
    ctl.load("./plotgen.lp")
    # ground the ASP program
    ctl.ground()
    # solve the ASP program, passing the collect_outline function as a callback for each model
    ctl.solve(on_model=collect_outline, on_unsat=lambda: print("UNSAT"))

    # return the collected outlines when Clingo finishes solving
    return all_outlines

### OpenAI/LLM functionality

oai_api_key = open("openai_api_key.txt").read()
oai_client = OpenAI(api_key=oai_api_key)

# outline-based story generation: translate an ASP-generated outline
# and a brief user input text into a sequence of LLM prompts

init_prompt = """
You're writing a story about:

{{user_input_text}}

Write the first paragraph of the story. In this paragraph, {{follow_instruction}}.
""".strip()

followup_prompt = """
Write the next paragraph of the story. In this paragraph, {{follow_instruction}}.
""".strip()

instructions_by_function = {
  "introduce_character":
    "introduce a character we haven't introduced already",
  "introduce_character,cold":
    "introduce a character whose personality is Cold and Solitary, have a soft side deep down,very powerful",
  "introduce_character,sunny":
    "introduce a character whose personality is Optimistic and Brave,Strong Sense of Justice",
  "describe_setting":
    "describe the place where the characters are",
  "add_conflict_between_characters":
    "introduce an event that adds conflicts between two previously introduced characters",
  "make_reader_sad":
    "convey an atmosphere of sadness",
  "make_reader_angry":
    "convey an atmosphere of anger",
  "add_bonding_between_characters":
    "introduce an event that deepen the bonding between two previously introduced characters",
  "add_obstacle_towards_major_goal":
    "introduce an obstacle that blocks the major goal of the protagonist",
  "add_breakthrough_towards_major_goal":
    "introduce a breakthrough that helps the major goal of the protagonist",
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
You're writing a story about:

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
  # adding a system prompt to make the language precise
  messages.append({
      "role": "system",
      "content": "You'\''re a fiction writer. You use simple and clear language that best conveys your meaning. You don'\''t use big words just to sound impressive. You are also a master of the writing skill -  \"Show, don'\''t tell.\" You use details, actions, and dialogues to show the characters and events. "
    })
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
  return "\n".join(sentences)

# Function to read pre-generated outlines from a file
# def read_pre_generated_outlines(file_path):
#     outlines = []
#     with open(file_path, 'r') as file:
#         for line in file:
#             # Assuming each line is a valid Python list in string format
#             outline = eval(line.strip())
#             outlines.append(outline)
#     return outlines

### tie it all together

# generate story outlines
outlines = generate_outlines()
print(outlines)

#read outlines from pre-generated outlines
#outlines = read_pre_generated_outlines('pregenerated_outlines0306.txt')

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