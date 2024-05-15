from clingo.control import Control
from clingo.symbol import SymbolType

def print_model(model):
    symbols = model.symbols(shown=True)
    for sym in symbols:
        if sym.type == SymbolType.Function:
            function_name = sym.name
            arguments = []
            for arg in sym.arguments:
                if arg.type == SymbolType.Number:
                    arguments.append(str(arg.number))
                elif arg.type == SymbolType.String:
                    arguments.append(f'"{arg.string}"')
                else:
                    arguments.append(str(arg))
            print(f"{function_name}({', '.join(arguments)})")
        else:
            print(sym)

#test the outline format

def format_outline(model):
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
        # check if the symbol represents a scene introducing a personality
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
            # join the function name and personality/obstacle type with a : and append to the outline list
            outline.append(f"{scene_functions[0]}:{scene_functions[1]}")
        else:
            # append the single function name to the outline list
            outline.append(scene_functions[0])

    # append the outline list to the all_outlines list
    # print the outline for debugging purposes
    #print(outline)
    return outline

def save_outlines(outlines, file_name):
    with open(file_name, 'w') as file:
        for outline in outlines:
            outline_str = ', '.join([f"'{item}'" for item in outline])
            file.write(f"[{outline_str}]\n")
    print(f"Outlines saved to {file_name}")

def main():
    # Create a Clingo control object
    ctl = Control()

    # Load the ASP program from the "plotgen.lp" file
    ctl.load("plotgen.lp")

    # Ground the ASP program
    ctl.ground([("base", [])])

    # Solve the ASP program and print the models
    print("Clingo Output:")
    ctl.solve(on_model=print_model)
    ctl.solve(on_model=format_outline)

    # ## Solve the ASP program and collect all the outlines
    # # set the configuration to enumerate all models
    ctl.configuration.solve.models = 0
    outlines = []
    ctl.solve(on_model=lambda model: outlines.append(format_outline(model)))

    # Save the outlines to a file
    save_outlines(outlines, "outlines05150045.txt")


if __name__ == "__main__":
    main()