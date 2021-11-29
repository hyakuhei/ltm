
grammar = """
    start: scene | dataflow

    scene: "scene:" [WS] ESCAPED_STRING                       -> scene

    dataflow: _actor WS _actor ":" [WS] flow                 -> dataflow
    _actor: WORD                                             
    flow: [ESCAPED_STRING | protocol]                      
    protocol: WORD "(" [ESCAPED_STRING | protocol] ")"

    %import common.WS
    %import common.WORD
    %import common.ESCAPED_STRING

"""

from lark import Token
from lark import Lark
from lark.tree import Tree
parser = Lark(grammar)

currentScene = None

scenes = {'currentScene':"default"}

def _addScene(title):    
    scenes['currentScene'] = title
    scenes[scenes['currentScene']] = []
    
    print(scenes)

def run_instruction(t):
    if t.data == 'scene':
        for c in t.children:
            if c is not None:
                if c.type == "ESCAPED_STRING":
                    _addScene(str(c))
       
    if t.data == 'dataflow':
        # actor actor: <Protocol>("message") 
        # Protocol is optional
        # Protocol can be nested

        left = None #will be string
        right = None #will be string
        flow = None #will be string or Protocol()
        for c in t.children:
            if isinstance(c, Token):
                if c.type == "WORD":
                    if left is None:
                        left = str(c)
                    else:
                        right = str(c)

            if isinstance(c, Tree):
                print(c.children)
                for tc in c.children:
                    if isinstance(tc, Token):
                        if tc.type == "ESCAPED_STRING":
                            flow = str(tc)
                        else:
                            print(f"Found some other type {flow}")


        print(f"left: {left}, right: {right}, flow: {flow}")

def run_ltm(program):
    parse_tree = parser.parse(program)
    print(parser.parse(program).pretty())
    for inst in parse_tree.children:
        run_instruction(inst)

def main():
    while True:
        code = input('> ')
        try:
            run_ltm(code)
        except Exception as e:
            print(e)

def test():
    textSimple = '''
        scene:"jeff"
        user service:TCP(TLS(HTTP("GET /")))
    '''

    print(parser.parse(textSimple).pretty())

if __name__ == '__main__':
    test()
    #main()