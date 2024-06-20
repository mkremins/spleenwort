from clingo.control import Control
import random

#update the generate outline function with new output format
def generate_outlines():
	# helper callback to collect valid story outlines as they're generated
	outlines_file = open("outlines.csv", "w")
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
			# check if the symbol represents a scene introducing a obstacle
			elif sym.name == "scene_define_obstacle_type":
				# extract the scene index from the first argument
				scene_index = sym.arguments[0].number
				# extract the obstacle_type from the second argument
				obstacle_type = sym.arguments[1].name
				# add the obstacle_type to the corresponding scene index in the scene_info dictionary
				scene_info.setdefault(scene_index, []).append(obstacle_type)

		# create the outline list in the desired format
		outline = []
		# iterate over the sorted scene indices in the scene_info dictionary
		for scene_index in sorted(scene_info.keys()):
			# get the scene functions and personalities for the current scene index
			scene_functions = scene_info[scene_index]
			# check if the scene has more than one function/personality
			if len(scene_functions) > 1:
				# join the function name and personality with a colon and append to the outline list
				outline.append(f"{scene_functions[0]}:{scene_functions[1]}")
			else:
				# append the single function name to the outline list
				outline.append(scene_functions[0])

		# append the outline list to the all_outlines list
		all_outlines.append(outline)
		outlines_file.write(",".join(outline) + "\n")
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
	outlines_file.close()
	return all_outlines

generate_outlines()
