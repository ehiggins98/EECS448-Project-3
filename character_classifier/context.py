"""
Keeps track of the current context to to allow fetching all valid characters at the current position in the code.
"""
import re
import copy

starting_chars = "[A-z$]"
non_starting_chars = starting_chars + "|\\d"
context_headers = ['function', 'for', 'while', 'if', 'elseif', 'else']
declaration_flags = ['var', 'let', 'const']
auxiliary_flags = ['return', 'break']
literal_starting_chars = '\'|t|f|\d|-'
number_characters = '\d|-|\+|\.'
binary_operator_chars = '&|\||-|\+|\/|\*|>|<|!|=|%'
binary_operators = ['&&', '||', '-', '+', '/', '*', '>', '<', '>=', '<=', '==', '=', '!=', '%']
boolean_operators = ['&&', '||']
unary_operators = "!"
both_sides_operators = ['++', '--']

alphanumeric_filter = re.compile('[A-z\d]')

def literal_complete(type, current_value):
    """
    Gets a boolean value indicating whether the current literal could be complete.

    :param type: The type of the literal.
    :param current_value: The literal to consider.
    :returns: A value indicating whether the current literal could be complete.
    """
    last = "" if current_value == "" else current_value[len(current_value)-1]
    current_value = current_value[:len(current_value)-1]
    complete = False
    if type == "number":
        complete = last != "."
    if type == "string" and last == '\'':
        complete = current_value != ""
    if type == "bool":
        complete = (current_value+last) in ['true', 'false']

    return complete

def get_literal_type(first_char):
    """
    Gets the type of a literal. Can only handle numbers, booleans, and strings.

    :param first_char: The first character of the literal.
    :returns: The type of the literal.
    """
    type = None
    if re.compile(number_characters).match(first_char):
        type = "number"
    elif first_char in 't|f':
        type = "bool"
    elif first_char in '\'"':
        type = "string"

    return type

def filter_alphanumeric(str):
    """
    Removes all nonalphanumeric characters from a string.

    :param str: The string from which to remove nonalphanumeric characters.
    :returns: The string with nonalphanumeric characters removed.
    """
    return ''.join(alphanumeric_filter.findall(str))

class Scope:
    """
    Represents any part of the code that has its own variable scope. For example, the bodies of functions
    and while loops.
    """
    def __init__(self, token_dict, needs_closed_brace=False):
        """
        Initializes a new Scope

        :param token_dict: The dictionary of valid tokens.
        :type token_dict: dictionary
        :param needs_closed_brace: A value indicating whether to require a closed brace in this `Scope`.
        :type boolean:
        """
        self.scopes = []
        self.scope_open = False
        self.token_dict = copy.deepcopy(token_dict)
        self.current_token = ""
        self.needs_closed_brace = needs_closed_brace

        if 'console' not in self.token_dict:
            self.token_dict['console'] = {'log': {}}

    def clone(self):
        """
        Creates a deep copy of this scope

        :returns: A clone of this scope.
        """
        new = Scope(self.token_dict, self.needs_closed_brace)
        new.scope_open = self.scope_open
        new.current_token = self.current_token
        for s in self.scopes:
            new.scopes.append(s.clone())
        return new

    def get_valid_characters(self):
        """
        Gets the valid characters at this point in the code.

        :returns: A regex accepting only the valid characters in the code.
        """
        if not self.scope_open:
            split = self.current_token.split('.')
            if len(split) > 1:
                last = split[len(split)-1]
                if last == '':
                    if split[0] == 'console':
                        return 'l'
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
                    if partial and not full and (len(last) > 2 or split[0] == 'console'):
                        tokens.update(partial)
                    elif full:
                        tokens.add('=')
                        tokens.add('\.')
                        tokens.add('\(')
                    else:
                        return non_starting_chars + '|=|\.|\('
                    return '|'.join(tokens)
            else:
                tokens = [c[len(self.current_token)] for c in context_headers if c.startswith(self.current_token) and len(c) > len(self.current_token)]
                tokens += [c[len(self.current_token)] for c in declaration_flags if c.startswith(self.current_token) and len(c) > len(self.current_token)]
                tokens += [c[len(self.current_token)] for c in auxiliary_flags if c.startswith(self.current_token) and len(c) > len(self.current_token)]
                tokens = set(tokens + [c[len(self.current_token)] for c in self.token_dict.keys() if c.startswith(self.current_token) and len(c) > len(self.current_token)])
                if self.current_token == 'else':
                    tokens.add('{')
                    tokens.add('i')
                if self.current_token in self.token_dict.keys():
                    tokens.add('\.')

                    if self.current_token != 'console':
                        tokens.add('\(')
                        tokens.add('=')
                        tokens.add('\+')
                        tokens.add('-')
                if 'e' in tokens and not self.current_token and (not self.scopes or not isinstance(self.scopes[-1], Conditional)):
                    tokens.remove('e')
                appended = '|\}' if self.current_token == '' and self.needs_closed_brace else ''
                return ('|'.join(tokens) + appended)
        else:
            valid = self.scopes[len(self.scopes) - 1].get_valid_characters()
            if isinstance(self.scopes[len(self.scopes) - 1], Expression) and self.scopes[len(self.scopes) - 1].complete():
                valid += '|;|\n'
            return valid

    def put_character(self, character):
        """
        Adds a character to the current code.

        :param character: The character to add.
        :type character: char
        :returns: A value indicating whether this scope could be complete.
        """
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
                elif self.current_token[len(self.current_token)-1] in '-+':
                    self.scope_open = True
                    self.scopes.append(Expression(self.token_dict, True, False))
                    for c in self.current_token:
                        self.scopes[len(self.scopes)-1].put_character(c)
            elif self.current_token in '+-':
                self.scope_open = True
                self.scopes.append(Expression(self.token_dict, True, False))
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
        """
        Converts this scope to a string.

        :returns: This scope represented as a string.
        """
        result = ';\n'.join([c.to_string() for c in self.scopes]).replace('};', '}')
        if len(result) > 0 and result[len(result)-1] not in ';}':
            result += ';'
        return result

class VariableDeclaration:
    """
    Represents a declaration of a variable, such as `let x = 7;`
    """
    def __init__(self, type, token_dict):
        """
        Initializes a new `VariableDeclaration`.

        :param type: The type of the declaration, out of ['let', 'var', ''].
        :type type: string
        :param token_dict: A dictionary of valid tokens.
        :type token_dict: dictionary
        """
        self.token_dict = token_dict
        self.type = type
        self.name = [""]
        self.value = None
        self.named = False

    def clone(self):
        """
        Creates a deep copy of this `VariableDeclaration`.

        :returns: A deep copy of this `VariableDeclaration`.
        """
        new = VariableDeclaration(self.type, self.token_dict)
        new.name = copy.deepcopy(self.name)
        new.named = self.named
        new.value = None if not self.value else self.value.clone()
        return new;

    def get_valid_characters(self):
        """
        Gets the valid characters at this point in the code.

        :returns: A regex accepting only the valid characters at this point in the code.
        """
        if self.name[len(self.name)-1] == "":
            appended = "|=" if len(self.name) > 1 else ""
            return starting_chars + appended
        elif not self.named and self.name != "":
            return non_starting_chars + '|='
        elif self.value != None:
            return self.value.get_valid_characters()

    def put_character(self, character):
        """
        Adds a character to the current code.

        :param character: The character to add.
        :type character: char
        :returns: A value indicating whether this variable declaration could be finished.
        """
        if character in ";\n" and self.value_is_complete:
            return True
        if not self.named and character == '.':
            self.name.append('')
        elif not self.named and character != '=':
            self.name[len(self.name)-1] += character
        elif not self.named and character == '=':
            self.named = True
            self.value = Expression(self.token_dict, False, False)
        elif self.named:
            self.value.put_character(character)

        return False

    def to_string(self):
        """
        Converts this `VariableDeclaration` to a string representation.

        :returns: A string representation of this `VariableDeclaration`.
        """
        value_string = self.value if isinstance(self.value, str) else self.value.to_string()
        type_string = self.type + " " if len(self.type) > 0 else ""
        return type_string + '.'.join(self.name) + " = " + value_string

    def could_be_token(self, str):
        """
        Gets a value indicating whether the given string could be a token (i.e. if it's a prefix of a valid token).

        :returns: A value indicating whether the given string could be a token.
        """
        return any([t.startswith(str) for t in self.token_dict.keys()])

    def value_is_complete(self):
        """
        Gets a value indicating whether the expression to the right of the equal sign could be complete.

        :returns: A value indicating whether the expression to the right of the equal sign could be complete.
        """
        return self.value.complete

    def full_name(self):
        """
        Gets a string representation of the current `self.name`. For example, if `self.name = ['console', 'log'],
        then this will return 'console.log'.

        :returns: A string representation of the current `self.name`.
        """
        return '.'.join(self.name)

class Function:
    """
    Represents a function and its declaration, i.e. `function a(b, c, d) {}.
    """
    def __init__(self, token_dict):
        """
        Creates a new `Function`.

        :param token_dict: A dictionary of valid tokens.
        :type token_dict: dictionary.
        """
        self.params = []
        self.token_dict = copy.deepcopy(token_dict)
        self.parent_tokens = token_dict
        self.name = ""
        self.body = None
        self.named = False
        self.parameterized = False

    def clone(self):
        """
        Creates a deep copy of the `Function`.

        :returns: A deep copy of the `Function`.
        """
        new = Function(self.token_dict)
        new.params = copy.deepcopy(self.params)
        new.parent_tokens = self.parent_tokens
        new.name = self.name
        new.body = None if not self.body else self.body.clone()
        new.named = self.named
        new.parameterized = self.parameterized
        return new

    def get_valid_characters(self):
        """
        Gets the valid characters at this point in the code.

        :returns: A regex accepting only the valid characters at this point in the code.
        """
        if not self.named:
            return starting_chars if self.name == "" else non_starting_chars + "|\("
        if not self.parameterized:
            last_param = None if len(self.params) == 0 else self.params[len(self.params)-1]
            last_param = None if last_param == None or [len(last_param) - 1] == ',' else last_param

            if last_param == None:
                return starting_chars + "|\)"
            if last_param != None and last_param[len(last_param) - 1] != ',':
                return non_starting_chars + "|,|\)"
            if last_param != None:
                return starting_chars
        if self.parameterized and self.body == None:
            return '\{'

        return self.body.get_valid_characters()

    def put_character(self, character):
        """
        Adds a character to the current code.

        :param character: The character to add.
        :type character: char
        :returns: A value indicating whether this function could be finished.
        """
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
            self.body = Scope(self.token_dict, True)
        elif self.parameterized and self.body != None:
            return self.body.put_character(character)

        return False

    def to_string(self):
        """
        Gets a string representation of this function.

        :returns: A string representation of this function.
        """
        params = ' '.join(self.params)
        body = "" if self.body == None else self.body.to_string()
        return 'function ' + self.name + "(" + params + '){\n' + body + '\n}'

class Expression:
    """
    Represents either a boolean or a math expression.
    """
    def __init__(self, token_dict, require_semicolon, require_token_initially):
        """
        Creates a new expression.

        :param token_dict: A dictionary of valid tokens.
        :type token_dict: dictionary
        :param require_semicolon: A value indicating whether to require a semicolon at the end of the expression.
        :type require_semicolon: boolean
        :param require_token_initially: A value indicating whether this expression must begin with a token.
        :type require_token_initially: boolean
        """
        self.token_dict = token_dict
        self.value = ""
        self.current_symbol = ""
        self.require_semicolon = require_semicolon
        self.require_token_initially = require_token_initially
        self.reset = True

    def clone(self):
        """
        Creates a deep copy of this `Expression`.

        :returns: A deep copy of this `Expression`.
        """
        new = Expression(self.token_dict, self.require_semicolon, self.require_token_initially)
        new.value = self.value
        new.current_symbol = self.current_symbol
        new.reset = self.reset
        return new

    def get_valid_characters(self):
        """
        Gets the valid characters at this point in the code.

        :returns: A regex accepting only the valid characters at this point in the code.
        """
        last = "" if len(self.value) == 0 else self.value[len(self.value)-1]

        if last == '!':
            return literal_starting_chars + self.get_token_chars(True) + "|\(|="
        if last == '(':
            return literal_starting_chars + self.get_token_chars(True) + '|!|\('
        if last == ')':
            return binary_operator_chars

        if not self.value and self.require_token_initially:
            return self.get_token_chars(False)[1:]
        if last == "" or last in binary_operator_chars and last:
            second_last = "" if len(self.value) < 2 else self.value[-2]
            if second_last not in '&|' and last in '&|':
                return '&' if last == '&' else '\|'
            possible_operators = '|'.join(set([c[1] for c in binary_operators + both_sides_operators if c.startswith(last) and len(c) > 1 and len(last) > 0]))
            possible_operators = possible_operators.replace('+', '\+')
            if len(possible_operators) > 0: possible_operators = '|' + possible_operators
            return literal_starting_chars + "|\(|!" + possible_operators + self.get_token_chars(True)

        if self.symbol_complete() and self.current_symbol not in binary_operators:
            operators = binary_operator_chars if self.reset else '&|\|'
            literals = self.get_literal_chars()
            return operators + ('|' if literals else '') + literals + "|\)|;|\n|\."

        if not self.symbol_complete() and self.current_symbol not in binary_operator_chars:
            result = self.get_literal_chars()
            if result != '.': result += self.get_token_chars(True)
            if self.require_semicolon: result += '|;'
            if result and result[0] == '|':
                return result[1:]
            return result

    def put_character(self, character):
        """
        Adds a character to the current code.

        :param character: The character to add.
        :type character: char
        :returns: A value indicating whether this expression could be finished.
        """
        if self.symbol_complete():
            if self.current_symbol in '&|':
                self.reset = True
            elif self.current_symbol in binary_operator_chars:
                self.reset = False
            self.current_symbol = ""

        self.value += character
        self.current_symbol += character
        return self.symbol_complete() and self.current_symbol not in binary_operator_chars and (character in ';\n' or not self.require_semicolon)

    def to_string(self):
        """
        Gets a string representation of this `Expression`.

        :returns: A string representation of this `Expression`.
        """
        return self.value

    def get_token_chars(self, with_operators):
        """
        Gets all valid characters assuming the current symbol is part of a token.

        :param with_operators: A value indicating whether ++<token>, <token>++, --<token>, and <token>-- should be included.
        :type with_operators: boolean
        :returns: A regex accepting only the valid characters assuming the current symbol is part of a token.
        """
        token = filter_alphanumeric(self.current_symbol)
        token_chars = set([t[len(token)] for t in self.token_dict.keys() if len(t) > len(token) and t.startswith(token)])

        if (len(self.current_symbol) == 0 or token in self.token_dict.keys()) and with_operators:
            if self.current_symbol.count('+') < 2: token_chars.add('\+')
            if self.current_symbol.count('-') < 2: token_chars.add('-')

        token_chars = '|'.join(token_chars)
        if token_chars != "":
            token_chars = "|" + token_chars
        return token_chars

    def get_literal_chars(self):
        """
        Gets all valid characters assuming the current symbol is part of a literal.

        :returns: A regex accepting only the valid characters assuming the current symbol is part of a literal.
        """
        if len(self.current_symbol) > 0 and self.current_symbol[0] in '\'"' and not self.symbol_complete():
            return '[^,]'
        if any([c.startswith(self.current_symbol) for c in ['true', 'false']]):
            result = [c[len(self.current_symbol)] for c in ['true', 'false'] if c.startswith(self.current_symbol) and len(c) > len(self.current_symbol)]
            return result[0] if len(result) > 0 else ""
        if re.compile(number_characters).match(self.current_symbol):
            return number_characters

        return ""

    def complete(self):
        """
        Gets a value indicating whether this `Expression` could be complete.

        :returns: A value indicating whether this `Expression` could be complete.
        """ 
        last_two = self.value[len(self.value)-2:] if len(self.value) >= 2 else ""
        return self.symbol_complete() and (self.current_symbol not in binary_operator_chars or '++' in last_two or '--' in last_two)

    def empty(self):
        """
        Gets a value indicating whether this `Expression` is empty
        
        :returns: A value indicating whether this `Expression` is empty.
        """ 
        return len(self.value) == 0

    def symbol_complete(self):
        """
        Gets a value indicating whether the current symbol could be complete.

        :returns: A value indicating whether the current symbol could be complete.
        """
        third_to_last = self.value[len(self.value)-3] if len(self.value) >= 3 else ""
        last_two = self.value[len(self.value)-2:] if len(self.value) >= 2 else ""
        complete = len(self.current_symbol) > 0 and literal_complete(get_literal_type(self.current_symbol[0]), self.current_symbol)
        complete = complete or self.current_symbol in self.token_dict.keys()
        complete = complete or self.current_symbol in binary_operators
        complete = complete or self.current_symbol in '()'
        complete = complete or self.current_symbol == '!' or self.current_symbol in ';\n' or self.current_symbol == ')'
        complete = complete or ((last_two == '++' or last_two == '--') and third_to_last not in binary_operator_chars)
        return complete

class Conditional:
    """
    Represents a conditional statement in the code, like 'if' or 'else'.
    """
    def __init__(self, type, token_dict):
        """
        Creates a new conditional statement.

        :param type: The type of the conditional statement, out of ['if', 'else if', and 'else'].
        :type type: string
        :param token_dict: A dictionary of valid tokens.
        :type token_dict: dictionary
        """
        self.token_dict = copy.deepcopy(token_dict)
        self.condition = Expression(self.token_dict, False, False)
        self.started = False
        self.condition_open = False
        self.body_open = False
        self.body = Scope(self.token_dict, True)
        self.type = type
        self.last_char = ""

    def clone(self):
        """
        Creates a deep copy of this conditional statement.

        :returns: A deep copy of this conditional statement.
        """
        new = Conditional(self.type, self.token_dict)
        new.condition = self.condition.clone()
        new.started = self.started
        new.condition_open = self.condition_open
        new.body_open = self.body_open
        new.body = self.body.clone()
        new.last_char = self.last_char
        return new

    def get_valid_characters(self):
        """
        Gets the valid characters at this point in the code.

        :returns: A regex accepting only the valid characters at this point in the code.
        """
        if not self.condition_open and not self.body_open:
            return '\('
        if self.condition_open:
            appended = "|\{" if self.last_char == ')' else ""
            return self.condition.get_valid_characters() + appended
        if self.body_open:
            return self.body.get_valid_characters()

    def put_character(self, character):
        """
        Adds a character to the current code.

        :param character: The character to add.
        :type character: char
        :returns: A value indicating whether this expression could be finished.
        """
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
        """
        Gets a string representation of this `Conditional`.

        :returns: A string representation of this `Conditional`.
        """
        token = 'else if(' if self.type == 'elseif' else self.type
        if token == 'if': token += '('
        return token + self.condition.to_string() + '{\n' + self.body.to_string() + '\n}'

class WhileLoop:
    """
    Represents a while loop.
    """
    def __init__(self, token_dict):
        """
        Creates a new while loop.

        :param token_dict: A dictionary of valid tokens.
        :type token_dict: dictionary
        """
        self.token_dict = copy.deepcopy(token_dict)
        self.condition = Expression(self.token_dict, False, False)
        self.body = Scope(self.token_dict, True)
        self.condition_open = False
        self.body_open = False
        self.started = False
        self.last_char = ""

    def clone(self):
        """
        Creates a deep copy of the while loop.

        :returns: A deep copy of the while loop.
        """
        new = WhileLoop(self.token_dict)
        new.condition = self.condition.clone()
        new.body = self.body.clone()
        new.condition_open = self.condition_open
        new.body_open = self.body_open
        new.started = self.started
        new.last_char = self.last_char
        return new

    def get_valid_characters(self):
        """
        Gets the valid characters at this point in the code.

        :returns: A regex accepting only the valid characters at this point in the code.
        """
        if not self.condition_open and not self.body_open and not self.started:
            return '\('
        if self.condition_open:
            appended = "|\{" if self.last_char == ')' else ""
            return self.condition.get_valid_characters() + appended
        if self.body_open:
            return self.body.get_valid_characters()

    def put_character(self, character):
        """
        Adds a character to the current code.

        :param character: The character to add.
        :type character: char
        :returns: A value indicating whether this expression could be finished.
        """
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
        """
        Gets a string representation of the while loop.

        :returns: A string representation of the while loop.
        """
        return 'while(' + self.condition.to_string() + '{\n' + self.body.to_string() + '\n}'

class ForLoop:
    """
    Represents a for loop.
    """
    def __init__(self, token_dict):
        """
        Creates a new for loop.

        :param token_dict: A dictionary of valid tokens.
        :type token_dict: dictionary
        """
        self.token_dict = copy.deepcopy(token_dict)
        self.body_open = False
        self.started = False
        self.header_complete = False

        self.initializer = None
        self.condition = None
        self.increment = None
        self.body = None

    def clone(self):
        """
        Creates a deep copy of this for loop.

        :returns: A deep copy of this for loop.
        """
        new = ForLoop(self.token_dict)
        new.body_open = self.body_open
        new.started = self.started
        new.header_complete = self.header_complete
        new.initializer = self.initializer if isinstance(self.initializer, str) or not self.initializer else self.initializer.clone()
        new.condition = None if not self.condition else self.condition.clone()
        new.increment = None if not self.increment else self.increment.clone()
        new.body = None if not self.body else self.body.clone()
        return new

    def get_valid_characters(self):
        """
        Gets the valid characters at this point in the code.

        :returns: A regex accepting only the valid characters at this point in the code.
        """
        if not self.initializer and not self.condition and not self.increment and not self.body and not self.started:
            return '\('
        elif self.header_complete and not self.body:
            return '\{|\n'
        elif self.initializer != None and not self.condition:
            if isinstance(self.initializer, str):
                chars = [c[len(self.initializer)] for c in ['var', 'let'] if c.startswith(self.initializer) and len(c) > len(self.initializer)]
                name, flag = self.name_and_flag(self.initializer)
                chars += [c[len(name)] for c in self.token_dict.keys() if c.startswith(name) and len(c) > len(self.initializer) and len(name) > 0]
                return '|'.join(set(chars))
            elif isinstance(self.initializer, VariableDeclaration):
                return self.initializer.get_valid_characters()
        elif self.condition and not self.increment:
            return self.condition.get_valid_characters()
        elif self.increment and not self.body:
            appended = '|\)' if self.increment.complete() else ''
            return self.increment.get_valid_characters() + appended
        elif self.body:
            return self.body.get_valid_characters()

    def put_character(self, character):
        """
        Adds a character to the current code.

        :param character: The character to add.
        :type character: char
        :returns: A value indicating whether this expression could be finished.
        """
        if not self.initializer and not self.condition and not self.increment and not self.body and not self.started and character == '(':
            self.initializer = ""
            self.started = True
        elif self.header_complete and character == '{':
            self.body = Scope(self.token_dict, True)
        elif self.initializer != None and not self.condition:
            if isinstance(self.initializer, str):
                self.initializer += character
                if self.could_be_token(self.initializer) and not self.could_be_declaration(self.initializer) and self.initializer in self.token_dict:
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
                if self.initializer.put_character(character) and character in ';\n':
                    self.token_dict['.'.join(self.initializer.name)] = {}
                    self.condition = Expression(self.token_dict, True, True)
        elif self.condition and not self.increment:
            expr_complete = self.condition.put_character(character)
            if expr_complete and character in ';\n':
                self.increment = Expression(self.token_dict, False, True)
        elif self.increment and not self.body:
            self.header_complete = self.increment.put_character(character) and character == ')'
        elif self.body:
            return self.body.put_character(character)
        return False

    def to_string(self):
        """
        Gets a string representation of this for loop.

        :returns: A string representation of this for loop.
        """
        initializer_string = ''
        if isinstance(self.initializer, str):
            initializer_string = self.initializer
        elif isinstance(self.initializer, VariableDeclaration):
            initializer_string = self.initializer.to_string()

        condition_string = '' if not self.condition else self.condition.to_string()
        increment_string = '' if not self.increment else self.increment.to_string()
        body_string = '' if not self.body else self.body.to_string()
        return 'for(' + initializer_string + '; ' + condition_string + ' ' + increment_string + '{\n' + body_string + '\n}'

    def could_be_token(self, str):
        """
        Gets a value indicating whether `str` could be a token i.e. if a token starts with `str` or `str` starts with a token.

        :params str: The value to consider.
        :type str: string
        :returns: A value indicating whether `str` could be a token.
        """
        return any([c.startswith(str) for c in self.token_dict.keys()] + [str.startswith(c) for c in self.token_dict.keys()])

    def could_be_declaration(self, str):
        """
        Gets a value indicating whether `str` could be a variable declaration e.g. 'var x = y'.

        :params str: The value to consider.
        :type str: string
        :returns: A value indicating whether `str` could be a variable declaration.
        """
        return any([c.startswith(str) for c in declaration_flags] + [str.startswith(c) for c in declaration_flags])

    def get_token_chars(self):
        """
        Gets all valid characters assuming the current symbol is a token.

        :returns: A regex accepting only valid characters assuming the current symbol is a token.
        """
        token = filter_alphanumeric(self.current_symbol)
        token_chars = '|'.join([t[len(token)] for t in self.token_dict.keys() if len(t) > len(token) and t.startswith(token)])

        if token_chars != "":
            token_chars = "|" + token_chars
        return token_chars

    def name_and_flag(self, str):
        """
        Extracts the name and flag from `str`. I.e. if `str == 'var x'` then `name = 'x'` and `flag == 'var'`.

        :param str: The value to consider.
        :type str: string
        :returns: The name and flag extracted from `str`.
        """
        for d in declaration_flags:
            if str.startswith(d):
                return str[len(d):], d
            elif d.startswith(str):
                return "", d
        for t in self.token_dict.keys():
            if str.startswith(t):
                return t, ""
            elif t.startswith(str):
                return str, ""

class FunctionCall:
    """
    Represents a function call. E.g. if `x` is a function, `x()` is a `FunctionCall`.
    """
    def __init__(self, token_dict):
        """
        Creates a new function call.

        :param token_dict: A dictionary of valid tokens.
        :type token_dict: dictionary
        """
        self.token_dict = copy.deepcopy(token_dict)
        self.name = ""
        self.params = []
        self.comma = False

    def clone(self):
        """
        Creates a deep copy of this `FunctionCall`.

        :returns: A deep copy of this `FunctionCall`.
        """
        new = FunctionCall(self.token_dict)
        new.name = self.name
        new.params = copy.deepcopy(self.params)
        new.comma = self.comma
        return new

    def get_valid_characters(self):
        """
        Gets the valid characters at this point in the code.

        :returns: A regex accepting only the valid characters at this point in the code.
        """
        if not self.params:
            result = set([c[len(self.name)] for c in self.token_dict.keys() if c.startswith(self.name) and len(c) > len(self.name)])

            if len([c for c in self.token_dict.keys() if c == self.name]) > 0:
                result.add('\(')
            return '|'.join(result)
        else:
            result = self.params[len(self.params)-1].get_valid_characters()
            appended = ''
            if ',' not in result and self.params[len(self.params)-1].complete():
                appended += '|,'
            if ')' not in result and (self.params[len(self.params)-1].complete() or len(self.params) == 1 and self.params[0].empty()):
                appended += '|\)'
            return result + appended

    def put_character(self, character):
        """
        Adds a character to the current code.

        :param character: The character to add.
        :type character: char
        :returns: A value indicating whether this expression could be finished.
        """
        self.comma = False
        if not self.params and character != '(':
            self.name += character
        elif not self.params and character == '(' or self.params and character == ',' and self.params[len(self.params)-1].complete():
            self.params.append(Expression(self.token_dict, False, False))
            self.comma = True
        elif self.params[len(self.params)-1].complete() and character in ';\n':
            return True
        elif self.params:
            self.params[len(self.params)-1].put_character(character)

        return False

    def to_string(self):
        """
        Gets a string representation of this `FunctionCall`.

        :returns: A string representation of this `FunctionCall`.
        """
        return self.name + '(' + ', '.join([p.to_string() for p in self.params]) + ';'

class AuxiliaryFlag:
    """
    Represents a `return` or `break` statement.
    """
    def __init__(self, type, token_dict):
        """
        Creates a new auxiliary flag.

        :param type: The type of the flag out of ['break', 'return']
        :type type: string
        :param token_dict: A dictionary of valid tokens.
        :type token_dict: dictionary
        """
        self.type = type
        self.value = Expression(token_dict, False, False) if type == 'return' else None

    def clone(self):
        """
        Creates a deep copy of this `AuxiliaryFlag`.

        :returns: A deep copy of this `AuxiliaryFlag`.
        """
        new = AuxiliaryFlag(self.type, self.token_dict)
        new.value = None if not self.value else self.value.clone()
        return new

    def get_valid_characters(self):
        """
        Gets the valid characters at this point in the code.

        :returns: A regex accepting only the valid characters at this point in the code.
        """
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
        """
        Adds a character to the current code.

        :param character: The character to add.
        :type character: char
        :returns: A value indicating whether this expression could be finished.
        """
        if character in ';\n' and (not self.value or self.value.complete() or self.value.empty()):
            return True
        else:
            self.value.put_character(character)
            return False

    def to_string(self):
        """
        Gets a string representation of this `AuxiliaryFlag`.

        :returns: A string representation of this `AuxiliaryFlag`.
        """
        str = self.value.to_string() if self.value else ''
        appended = ' ' + str if str else ''
        return self.type + appended
