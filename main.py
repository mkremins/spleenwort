from clingo.control import Control
from clingo.symbol import SymbolType
from openai import OpenAI

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
    "introduce a new character",
  "complicate_relationship_between_characters":
    "complicate the relationship between two previously introduced characters",
  "remove_character":
    "write a previously introduced character out of the story",
  "make_reader_sad":
    "write something that will make the reader sad",
  "make_reader_angry":
    "write something that will make the reader happy",
  "make_reader_angry":
    "write something that will make the reader angry",
  "end_the_story":
    "bring the story to a conclusion",
}

def storify_outline(outline, user_input_text):
  # translate one outline into a story
  messages = []
  for i in range(len(outline)):
    # assemble the prompt for the next paragraph of the story
    is_first_paragraph = i == 0
    function = outline[i]
    instruction = instructions_by_function[function]
    prompt_template = init_prompt if is_first_paragraph else followup_prompt
    prompt = prompt_template.replace("{{follow_instruction}}", instruction)
    if is_first_paragraph:
      prompt = prompt.replace("{{user_input_text}}", user_input_text)
    # prompt the LLM for the next paragraph
    messages.append({"role": "user", "content": prompt})
    completion = oai_client.chat.completions.create(
      messages=messages, model="gpt-3.5-turbo"
    )
    # append response message as context for future paragraphs
    paragraph = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": paragraph})
    print(paragraph)
  # TODO parse story out of messages
  return messages

### tie it all together

# generate story outlines
outlines = generate_outlines()
print(outlines)

# storify an outline
user_input_text = "cat pirates"
print(storify_outline(outlines[0], user_input_text))
