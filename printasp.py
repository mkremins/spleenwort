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

if __name__ == "__main__":
    main()