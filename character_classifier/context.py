import re

"""
TODO
Switch from literal to expression if we see an operator
"""

starting_chars = "[A-z$]"
non_starting_chars = starting_chars + "|\\d"
context_headers = ['function', 'for', 'while', 'do', 'if', 'else if', 'else']
declaration_flags = ['var', 'let', 'const']
literal_starting_chars = '\"|\'|t|f|\d|-'
number_characters = '\d|-|\+'
binary_operator_chars = '&|\||-|\+|\/|\*|>|<|!|='
binary_operators = ['&&', '||', '-', '+', '/', '*', '>', '<', '>=', '<=', '==', '=', '!=']
unary_operators = "!"

alphanumeric_filter = re.compile('[A-z\d]')

def literal_complete(type, current_value):
    last = "" if current_value == "" else current_value[len(current_value)-1]
    current_value = current_value[:len(current_value)-1]
    complete = False
    if type == "number":
        complete = last != "."
    if type == "string" and (last == '\'' or last == '"'):
        complete = current_value != ""
    if type == "bool":
        complete = current_value in ['true', 'false']

    return complete

def get_literal_type(first_char):
    type = None
    if re.compile(number_characters).match(first_char):
        type = "number"
    elif first_char in 't|f':
        type = "bool"
    elif first_char in '\'"':
        type = "string"

    return type

def filter_alphanumeric(str):
    return ''.join(alphanumeric_filter.findall(str))

class Scope:
    def __init__(self, tokens):
        self.scopes = []
        self.scope_open = False
        self.tokens = tokens
        self.current_token = ""

    def get_valid_characters(self):
        if not self.scope_open:
            tokens = [c[len(self.current_token)] for c in context_headers if c.startswith(self.current_token) and len(c) > len(self.current_token)]
            tokens += [c[len(self.current_token)] for c in declaration_flags if c.startswith(self.current_token) and len(c) > len(self.current_token)]
            tokens = set(tokens + [c[len(self.current_token)] for c in self.tokens if c.startswith(self.current_token) and len(c) > len(self.current_token)])

            if 'e' in tokens:
                tokens.remove('e')
            return '|'.join(tokens)
        else:
            return self.scopes[len(self.scopes) - 1].get_valid_characters()

    def put_character(self, character):
        if not self.scope_open and character not in "};\n":
            self.current_token += character
            if self.current_token in context_headers or self.current_token in declaration_flags or self.current_token in self.tokens:
                self.scope_open = True
                if self.current_token == 'function':
                    self.scopes.append(Function(self.tokens))
                elif self.current_token in declaration_flags:
                    self.scopes.append(VariableDeclaration(self.current_token, self.tokens))
        elif self.scope_open:
            self.scope_open = not self.scopes[len(self.scopes) - 1].put_character(character)
            if not self.scope_open:
                self.current_token = ""
        elif character == '}':
            return True
        return False

    def to_string(self):
        return ';\n'.join([c.to_string() for c in self.scopes])

class VariableDeclaration:
    def __init__(self, type, tokens):
        self.tokens = tokens
        self.type = type
        self.name = "";
        self.value = None
        self.named = False

    def get_valid_characters(self):
        if self.name == "":
            return starting_chars
        elif not self.named and self.name != "":
            return non_starting_chars + '|=|.'
        elif self.named and self.value == None:
            return starting_chars + '|' + literal_starting_chars
        else:
            if isinstance(self.value, str):
                valid = set([c[len(self.value)] for c in self.tokens if c.startswith(self.value)] + [c[len(self.value)] for c in ['true', 'false'] if c.startswith(self.value)])
                return '|'.join(valid)
            else:
                return self.value.get_valid_characters()

    def put_character(self, character):
        if character in ";\n" and self.value_is_complete:
            return True
        if not self.named and character != '=':
            self.name += character
        elif not self.named and character == '=':
            self.named = True
        elif self.value == None:
            if re.compile(literal_starting_chars).match(character) and not self.could_be_token(character):
                self.value = Expression(self.tokens)
                self.value.put_character(character)
            else:
                self.value = character
        elif isinstance(self.value, Expression):
            self.value.put_character(character)
        else:
            temp = self.value + character
            if not self.could_be_token(temp) and ('true'.startswith(temp) or 'false'.startswith(temp)):
                self.value = Expression(self.tokens)
                for c in temp:
                    self.value.put_character(c)
            else:
                self.value = temp

        return False

    def to_string(self):
        value_string = self.value if isinstance(self.value, str) else self.value.to_string()
        return self.type + " " + self.name + " = " + value_string + ';'

    def could_be_token(self, str):
        return any([t.startswith(str) for t in self.tokens])

    def value_is_complete(self):
        if isinstance(self.value, str):
            return self.value != ""
        else:
            return self.value.complete

class Literal:
    def __init__(self, tokens):
        self.value = ""
        self.type = None
        self.tokens = tokens
        self.complete = False

    def get_valid_characters(self):
        if self.type == None:
            return literal_starting_chars
        elif self.type == "number":
            return number_characters
        elif self.type == "bool":
            return '|'.join([c[len(self.value)] for c in ['true', 'false'] if c.startswith(self.value)])
        elif self.type == "string":
            return '\'|"' if self.value == "" else "."

    def put_character(self, character):
        if self.value == "":
            self.type = get_literal_type(character)

        self.complete = literal_complete(self.type, self.value + character)

        self.value += "" if character in ";\n" and self.complete else character
        return self.complete and character in ";\n"

    def to_string(self):
        return self.value

class Function:
    def __init__(self, tokens):
        self.params = []
        self.tokens = tokens
        self.name = ""
        self.body = None
        self.named = False
        self.parameterized = False

    def get_valid_characters(self):
        if not self.named:
            return starting_chars if self.name == "" else non_starting_chars + "|("
        if not self.parameterized:
            last_param = None if len(self.params) == 0 else self.params[len(self.params)-1]
            last_param = None if last_param == None or [len(last_param) - 1] == ',' else last_param

            if last_param == None:
                return starting_chars + "|)"
            if last_param != None and last_param[len(last_param) - 1] != ',':
                return non_starting_chars + "|,|)"
            if last_param != None:
                return starting_chars
        if self.parameterized and self.body == None:
            return '{'

        return self.body.get_valid_characters()

    def put_character(self, character):
        if not self.named:
            if character == '(':
                self.named = True
            else:
                self.name += character
        elif not self.parameterized and character != ')':
            last_param = None if len(self.params) == 0 else self.params[len(self.params) - 1]
            if len(self.params) == 0 or last_param[len(last_param) - 1] == ',':
                self.params.append(character)
            else:
                if character == ',':
                    self.tokens.append(self.params[len(self.params) - 1])
                self.params[len(self.params) - 1] += character
        elif not self.parameterized and character == ')':
            self.parameterized = True
        elif self.parameterized and self.body == None and character == '{':
            self.body = Scope(self.tokens)
        elif self.parameterized and self.body != None:
            return self.body.put_character(character)

        return False

    def to_string(self):
        params = ''.join(self.params)
        body = "" if self.body == None else self.body.to_string()
        return 'function ' + self.name + "(" + params + '){' + body + '}'

class Expression:
    def __init__(self, tokens):
        self.tokens = tokens
        self.value = ""
        self.current_symbol = ""

    def get_valid_characters(self):
        last = "" if len(self.value) == 0 else self.value[len(self.value)-1]

        if last == '!':
            return literal_starting_chars + self.get_token_chars() + "|(|="
        if last == '(':
            return literal_starting_chars + self.get_token_chars() + '|!'
        if last == ')':
            return binary_operator_chars

        if last == "" or last in binary_operator_chars:
            possible_operators = '|'.join(set([c[1] for c in binary_operators if c.startswith(last) and len(c) > 1 and len(last) > 0]))
            if len(possible_operators) > 0: possible_operators = '|' + possible_operators
            return literal_starting_chars + "|(|!" + possible_operators + self.get_token_chars()

        if self.symbol_complete() and self.current_symbol not in binary_operators:
            return binary_operator_chars + "|)"

        if not self.symbol_complete() and self.current_symbol not in binary_operator_chars:
            result = self.get_literal_chars() + self.get_token_chars()
            if result[0] == '|':
                return result[1:]
            return result

    def put_character(self, character):
        if self.symbol_complete():
            self.current_symbol = ""

        self.value += character
        self.current_symbol += character
        return self.symbol_complete()

    def to_string(self):
        return self.value

    def get_token_chars(self):
        token = filter_alphanumeric(self.current_symbol)
        token_chars = '|'.join([t[len(token)] for t in self.tokens if len(t) > len(token) and t.startswith(token)])

        if token_chars != "":
            token_chars = "|" + token_chars
        return token_chars

    def get_literal_chars(self):
        symbol = filter_alphanumeric(self.current_symbol)

        if self.current_symbol in '\'"':
            return '.'
        if any([c.startswith(symbol) for c in ['true', 'false']]):
            return [c[len(symbol)] for c in ['true', 'false'] if c.startswith(symbol) and len(c) > len(symbol)][0]
        if re.compile(number_characters).match(symbol):
            return number_characters

        return ""

    def symbol_complete(self):
        complete = len(self.current_symbol) > 0 and literal_complete(get_literal_type(self.current_symbol[0]), self.current_symbol)
        complete = complete or any([t == self.current_symbol for t in self.tokens])
        complete = complete or self.current_symbol in binary_operators
        complete = complete or self.current_symbol == '!'
        return complete
