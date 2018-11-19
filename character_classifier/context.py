import re
import copy

"""
TODO:
+=, -=, *=, /=
Allow use of new line instead of semicolon
Save type of token (function or variable) to improve accuracy on function calls
Add semicolon to last line of scope
Make it a bit more resilient to invalid tokens in expressions and such
Setting properties to functions
Array literals
Object literals
"""

starting_chars = "[A-z$]"
non_starting_chars = starting_chars + "|\\d"
context_headers = ['function', 'for', 'while', 'do', 'if', 'else if', 'else']
declaration_flags = ['var', 'let', 'const']
auxiliary_flags = ['return', 'break']
literal_starting_chars = '\"|\'|t|f|\d|-'
number_characters = '\d|-|\+|\.'
binary_operator_chars = '&|\||-|\+|\/|\*|>|<|!|='
binary_operators = ['&&', '||', '-', '+', '/', '*', '>', '<', '>=', '<=', '==', '=', '!=', '++']
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
        complete = (current_value+last) in ['true', 'false']

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
    def __init__(self, token_dict):
        self.scopes = []
        self.scope_open = False
        self.token_dict = copy.deepcopy(token_dict)
        self.current_token = ""

        if 'console' not in self.token_dict:
            self.token_dict['console'] = {'log': {}}

    def get_valid_characters(self):
        if not self.scope_open:
            split = self.current_token.split('.')
            if len(split) > 1:
                last = split[len(split)-1]
                if last == '':
                    return starting_chars
                else:
                    tokens = set()
                    current = self.token_dict[split[0]]
                    for t in split[1:len(split)-1]:
                        if t in current.keys():
                            current = current[t]
                        else:
                            current[t] = {}
                            current = current[t]

                    partial = set([c[len(last)] for c in current.keys() if c.startswith(last) and len(c) > len(last)])
                    full = set([c for c in current.keys() if c == last])
                    if partial and not full and len(last) > 2:
                        tokens += partial
                    elif full:
                        tokens.add('=')
                        tokens.add('\.')
                        tokens.add('(')
                    else:
                        return non_starting_chars + '|=|\.|('

                    return '|'.join(tokens)
            else:
                tokens = [c[len(self.current_token)] for c in context_headers if c.startswith(self.current_token) and len(c) > len(self.current_token)]
                tokens += [c[len(self.current_token)] for c in declaration_flags if c.startswith(self.current_token) and len(c) > len(self.current_token)]
                tokens += [c[len(self.current_token)] for c in auxiliary_flags if c.startswith(self.current_token) and len(c) > len(self.current_token)]
                tokens = set(tokens + [c[len(self.current_token)] for c in self.token_dict.keys() if c.startswith(self.current_token) and len(c) > len(self.current_token)])

                if self.current_token in self.token_dict.keys():
                    tokens.add('(')
                    tokens.add('\.')
                    tokens.add('=')

                if 'e' in tokens and len(self.current_token) == 0:
                    tokens.remove('e')
                appended = '|}' if self.current_token == '' else ''
                return '|'.join(tokens) + appended
        else:
            return self.scopes[len(self.scopes) - 1].get_valid_characters()

    def put_character(self, character):
        if not self.scope_open and character not in "};\n":
            self.current_token += character
            if self.current_token == 'function':
                self.scope_open = True
                self.scopes.append(Function(self.token_dict))
            elif self.current_token in declaration_flags:
                self.scope_open = True
                self.scopes.append(VariableDeclaration(self.current_token, self.token_dict))
            elif self.current_token in ['if', 'elseif']:
                self.scope_open = True
                self.scopes.append(Conditional(self.current_token, self.token_dict))
            elif re.compile('else[^i]').match(self.current_token) != None:
                self.scope_open = True
                cond = Conditional('else', self.token_dict)
                cond.put_character(self.current_token[len(self.current_token)-1])
                self.current_token = self.current_token[:len(self.current_token)-1]
                self.scopes.append(cond)
            elif self.current_token == 'while':
                self.scope_open = True
                self.scopes.append(WhileLoop(self.token_dict))
            elif self.current_token == 'for':
                self.scope_open = True
                self.scopes.append(ForLoop(self.token_dict))
            elif self.current_token[:len(self.current_token)-1] in self.token_dict.keys() and self.current_token[len(self.current_token)-1] or '.' in self.current_token[:len(self.current_token)-1]:
                if self.current_token[len(self.current_token)-1] in '=':
                    self.scope_open = True
                    self.scopes.append(VariableDeclaration("", self.token_dict))
                    for c in self.current_token:
                        self.scopes[len(self.scopes)-1].put_character(c)
                elif self.current_token[len(self.current_token)-1] == '(':
                    self.scope_open = True
                    self.scopes.append(FunctionCall(self.token_dict))
                    for c in self.current_token:
                        self.scopes[len(self.scopes)-1].put_character(c)

            elif self.current_token in ['break', 'return']:
                self.scope_open = True
                self.scopes.append(AuxiliaryFlag(self.current_token, self.token_dict))

        elif self.scope_open and (character != "}" or character == '}' and self.current_token not in declaration_flags):
            self.scope_open = not self.scopes[len(self.scopes) - 1].put_character(character)

            if not self.scope_open:
                if self.current_token in declaration_flags or (isinstance(self.scopes[len(self.scopes) - 1], VariableDeclaration) and '.' in self.scopes[len(self.scopes) - 1].full_name()):
                    name = self.scopes[len(self.scopes) - 1].name
                    current = self.token_dict
                    for t in name:
                        if t in current:
                            current = current[t]
                        else:
                            current[t] = {}
                            current = current[t]
                self.current_token = ""
        elif character == '}':
            return True
        return False

    def to_string(self):
        return ';\n'.join([c.to_string() for c in self.scopes]).replace('};', '}')

class VariableDeclaration:
    def __init__(self, type, token_dict):
        self.token_dict = token_dict
        self.type = type
        self.name = [""];
        self.value = None
        self.named = False

    def get_valid_characters(self):
        if self.name[len(self.name)-1] == "":
            appended = "|=" if len(self.name) > 1 else ""
            return starting_chars + appended
        elif not self.named and self.name != "":
            return non_starting_chars + '|='
        elif self.value != None:
            return self.value.get_valid_characters()

    def put_character(self, character):
        if character in ";\n" and self.value_is_complete:
            return True
        if not self.named and character == '.':
            self.name.append('')
        elif not self.named and character != '=':
            self.name[len(self.name)-1] += character
        elif not self.named and character == '=':
            self.named = True
            self.value = Expression(self.token_dict)
        elif self.named:
            self.value.put_character(character)

        return False

    def to_string(self):
        value_string = self.value if isinstance(self.value, str) else self.value.to_string()
        type_string = self.type + " " if len(self.type) > 0 else ""
        return type_string + '.'.join(self.name) + " = " + value_string

    def could_be_token(self, str):
        return any([t.startswith(str) for t in self.token_dict.keys()])

    def value_is_complete(self):
        return self.value.complete

    def full_name(self):
        return '.'.join(self.name)

class Function:
    def __init__(self, token_dict):
        self.params = []
        self.token_dict = copy.deepcopy(token_dict)
        self.parent_tokens = token_dict
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
                self.token_dict[self.name] = {}
                self.parent_tokens[self.name] = {}
            else:
                self.name += character
        elif not self.parameterized and character != ')':
            last_param = None if len(self.params) == 0 else self.params[len(self.params) - 1]
            if len(self.params) == 0 or last_param[len(last_param) - 1] == ',':
                self.params.append(character)
            else:
                if character == ',':
                    self.token_dict[self.params[len(self.params) - 1]] = {}
                self.params[len(self.params) - 1] += character
        elif not self.parameterized and character == ')':
            self.parameterized = True
            for p in self.params:
                p = p.replace(',', '')
                self.token_dict[p] = {}
        elif self.parameterized and self.body == None and character == '{':
            self.body = Scope(self.token_dict)
        elif self.parameterized and self.body != None:
            return self.body.put_character(character)

        return False

    def to_string(self):
        params = ' '.join(self.params)
        body = "" if self.body == None else self.body.to_string()
        return 'function ' + self.name + "(" + params + '){\n' + body + '\n}'

class Expression:
    def __init__(self, token_dict):
        self.token_dict = token_dict
        self.value = ""
        self.current_symbol = ""

    def get_valid_characters(self):
        last = "" if len(self.value) == 0 else self.value[len(self.value)-1]

        if last == '!':
            return literal_starting_chars + self.get_token_chars() + "|(|="
        if last == '(':
            return literal_starting_chars + self.get_token_chars() + '|!|('
        if last == ')':
            return binary_operator_chars

        if last == "" or last in binary_operator_chars:
            possible_operators = '|'.join(set([c[1] for c in binary_operators if c.startswith(last) and len(c) > 1 and len(last) > 0]))
            if len(possible_operators) > 0: possible_operators = '|' + possible_operators
            return literal_starting_chars + "|(|!" + possible_operators + self.get_token_chars()

        if self.symbol_complete() and self.current_symbol not in binary_operators:
            append = ""
            if get_literal_type(self.current_symbol[0]) == 'number':
                append = "|\."
            return binary_operator_chars + "|)|;" + append

        if not self.symbol_complete() and self.current_symbol not in binary_operator_chars:
            result = self.get_literal_chars()
            if result != '.': result += self.get_token_chars()
            if result[0] == '|':
                return result[1:]
            return result

    def put_character(self, character):
        if self.symbol_complete():
            self.current_symbol = ""

        self.value += character
        self.current_symbol += character
        return self.symbol_complete() and self.current_symbol not in binary_operator_chars

    def to_string(self):
        return self.value

    def get_token_chars(self):
        token = filter_alphanumeric(self.current_symbol)
        token_chars = '|'.join(set([t[len(token)] for t in self.token_dict.keys() if len(t) > len(token) and t.startswith(token)]))

        if token_chars != "":
            token_chars = "|" + token_chars
        return token_chars

    def get_literal_chars(self):
        if len(self.current_symbol) > 0 and self.current_symbol[0] in '\'"':
            return '.'
        if any([c.startswith(self.current_symbol) for c in ['true', 'false']]):
            result = [c[len(self.current_symbol)] for c in ['true', 'false'] if c.startswith(self.current_symbol) and len(c) > len(self.current_symbol)]
            return result[0] if len(result) > 0 else ""
        if re.compile(number_characters).match(self.current_symbol):
            return number_characters

        return ""

    def complete(self):
        return self.symbol_complete() and self.current_symbol not in binary_operator_chars

    def empty(self):
        return len(self.value) == 0

    def symbol_complete(self):
        complete = len(self.current_symbol) > 0 and literal_complete(get_literal_type(self.current_symbol[0]), self.current_symbol)
        complete = complete or self.current_symbol in self.token_dict.keys()
        complete = complete or self.current_symbol in binary_operators
        complete = complete or self.current_symbol == '!' or self.current_symbol == ';' or self.current_symbol == ')'
        return complete

class Conditional:
    def __init__(self, type, token_dict):
        self.token_dict = copy.deepcopy(token_dict)
        self.condition = Expression(self.token_dict)
        self.started = False
        self.condition_open = False
        self.body_open = False
        self.body = Scope(self.token_dict)
        self.type = type
        self.last_char = ""

    def get_valid_characters(self):
        if not self.condition_open and not self.body_open:
            return '('
        if self.condition_open:
            appended = "|{" if self.last_char == ')' else ""
            return self.condition.get_valid_characters() + appended
        if self.body_open:
            return self.body.get_valid_characters()

    def put_character(self, character):
        if (not self.condition_open and not self.body_open and character == "(") or (self.type == 'else' and not self.started):
            self.started = True
            self.condition_open = self.type != 'else'
            self.body_open = self.type == 'else'
        elif self.condition_open:
            if character == '\n' or character == '{':
                self.condition_open = False
                self.body_open = True
            else:
                self.condition.put_character(character)
        elif self.body_open:
            self.body_open = not self.body.put_character(character)
        self.last_char = character
        return not self.body_open and not self.condition_open and self.started

    def to_string(self):
        token = 'else if(' if self.type == 'elseif' else self.type
        if token == 'if': token += '('
        return token + self.condition.to_string() + '{\n' + self.body.to_string() + '\n}'

class WhileLoop:
    def __init__(self, token_dict):
        self.token_dict = copy.deepcopy(token_dict)
        self.condition = Expression(self.token_dict)
        self.body = Scope(self.token_dict)
        self.condition_open = False
        self.body_open = False
        self.started = False
        self.last_char = ""

    def get_valid_characters(self):
        if not self.condition_open and not self.body_open and not self.started:
            return '('
        if self.condition_open:
            appended = "|{" if self.last_char == ')' else ""
            return self.condition.get_valid_characters() + appended
        if self.body_open:
            return self.body.get_valid_characters()

    def put_character(self, character):
        if not self.condition_open and not self.started and character == '(':
            self.condition_open = True
            self.started = True
        elif self.condition_open:
            if character == '{':
                self.condition_open = False
                self.body_open = True
            else:
                self.condition.put_character(character)
        elif self.body_open:
            self.body_open = not self.body.put_character(character)
        self.last_char = character
        return not self.body_open and not self.condition_open and self.started

    def to_string(self):
        return 'while(' + self.condition.to_string() + '{\n' + self.body.to_string() + '\n}'

class ForLoop:
    def __init__(self, token_dict):
        self.token_dict = copy.deepcopy(token_dict)
        self.body_open = False
        self.started = False
        self.header_complete = False

        self.initializer = None
        self.condition = None
        self.increment = None
        self.body = None

    def get_valid_characters(self):
        if not self.initializer and not self.condition and not self.increment and not self.body and not self.started:
            return '('
        elif self.header_complete and not self.body:
            return '{|\n'
        elif self.initializer != None and not self.condition:
            if isinstance(self.initializer, str):
                chars = [c[len(self.initializer)] for c in ['var', 'let'] if c.startswith(self.initializer) and len(c) > len(self.initializer)]
                name, flag = self.name_and_flag(self.initializer)
                chars += [c[len(self.initializer)] for c in self.token_dict.keys() if c.startswith(name) and len(c) > len(self.initializer)]
                return '|'.join(set(chars))
            elif isinstance(self.initializer, Expression):
                return self.initializer.get_valid_characters() + ';'
        elif self.condition and not self.increment:
            return self.condition.get_valid_characters()
        elif self.increment and not self.body:
            return self.increment.get_valid_characters()
        elif self.body:
            return self.body.get_valid_characters()

    def put_character(self, character):
        if not self.initializer and not self.condition and not self.increment and not self.body and not self.started and character == '(':
            self.initializer = ""
            self.started = True
        elif self.header_complete and character == '{':
            self.body = Scope(self.token_dict)
        elif self.initializer != None and not self.condition:
            if isinstance(self.initializer, str):
                self.initializer += character
                if self.could_be_token(self.initializer) and not self.could_be_declaration(self.initializer):
                    temp = self.initializer
                    self.initializer = VariableDeclaration("", self.token_dict)
                    for c in temp:
                        self.initializer.put_character(c)
                elif not self.could_be_token(self.initializer) and self.could_be_declaration(self.initializer) and (self.initializer.startswith('var') or self.initializer.startswith('let')):
                    name, flag = self.name_and_flag(self.initializer)
                    self.initializer = VariableDeclaration(flag, self.token_dict)
                    for c in name:
                        self.initializer.put_character(c)
            elif isinstance(self.initializer, VariableDeclaration):
                if self.initializer.put_character(character) and character == ';':
                    self.token_dict['.'.join(self.initializer.name)] = {}
                    self.condition = Expression(self.token_dict)
        elif self.condition and not self.increment:
            expr_complete = self.condition.put_character(character)
            if expr_complete and character == ';':
                self.increment = Expression(self.token_dict)
        elif self.increment and not self.body:
            self.header_complete = self.increment.put_character(character) and character == ')'
        elif self.body:
            return self.body.put_character(character)

        return False;

    def to_string(self):
        return 'for(' + self.initializer.to_string() + '; ' + self.condition.to_string() + ' ' + self.increment.to_string() + '{\n' + self.body.to_string() + '\n}'

    def could_be_token(self, str):
        return any([c.startswith(str) for c in self.token_dict.keys()] + [str.startswith(c) for c in self.token_dict.keys()])

    def could_be_declaration(self, str):
        return any([c.startswith(str) for c in declaration_flags] + [str.startswith(c) for c in declaration_flags])

    def get_token_chars(self):
        token = filter_alphanumeric(self.current_symbol)
        token_chars = '|'.join([t[len(token)] for t in self.token_dict.keys() if len(t) > len(token) and t.startswith(token)])

        if token_chars != "":
            token_chars = "|" + token_chars
        return token_chars

    def name_and_flag(self, str):
        for d in declaration_flags:
            if str.startswith(d):
                return str[len(d):], d
            elif d.startswith(str):
                return "", d
        for t in self.token_dict.keys():
            if str.startswith(t):
                return t, ""

class FunctionCall:
    def __init__(self, token_dict):
        self.token_dict = copy.deepcopy(token_dict)
        self.name = ""
        self.params = []
        self.comma = False

    def get_valid_characters(self):
        if not self.params:
            result = set([c[len(self.name)] for c in self.token_dict.keys() if c.startswith(self.name) and len(c) > len(self.name)])

            if len([c for c in self.token_dict.keys() if c == self.name]) > 0:
                result.add('(')
            return '|'.join(result)
        else:
            result = self.params[len(self.params)-1].get_valid_characters()
            appended = ''
            if ',' not in result and self.params[len(self.params)-1].complete():
                appended += '|,'
            if ')' not in result and (self.params[len(self.params)-1].complete() or len(self.params) == 1 and self.params[0].empty()):
                appended += '|)'
            return result + appended

    def put_character(self, character):
        self.comma = False
        if not self.params and character != '(':
            self.name += character
        elif not self.params and character == '(' or self.params and character == ',' and self.params[len(self.params)-1].complete():
            self.params.append(Expression(self.token_dict))
            self.comma = True
        elif self.params[len(self.params)-1].complete() and character == ';':
            return True
        elif self.params:
            self.params[len(self.params)-1].put_character(character)

        return False;

    def to_string(self):
        return self.name + '(' + ', '.join([p.to_string() for p in self.params]) + ';'

class AuxiliaryFlag:
    def __init__(self, type, token_dict):
        self.type = type
        self.value = Expression(token_dict) if type == 'return' else None;

    def get_valid_characters(self):
        if not self.value:
            return ';|\n'
        else:
            result = self.value.get_valid_characters()
            appended = ''
            if ';' not in result and (self.value.complete() or self.value.empty()):
                appended += '|;'
            if '\n' not in result and (self.value.complete() or self.value.empty()):
                appended += '|\n'
            return result + appended

    def put_character(self, character):
        if character in ';\n' and (not self.value or self.value.complete() or self.value.empty()):
            return True;
        else:
            self.value.put_character(character)
            return False;

    def to_string(self):
        str = self.value.to_string() if self.value else ''
        appended = ' ' + str if str else ''
        return self.type + appended
