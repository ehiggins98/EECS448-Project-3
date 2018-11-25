import unittest
import context

starting_chars = "[A-z$]"
non_starting_chars = starting_chars + "|\\d"
number_characters = '\\d|-|\+'
literal_starting_chars = '\'|t|f|\d|-'
binary_operator_chars = '&|\||-|\+|\/|\*|>|<|!|=|%'

class TestFunction(unittest.TestCase):
    def setUp(self):
        self.function = context.Function({})

    def test_should_return_correct_initial_characters(self):
        valid = self.function.get_valid_characters()
        self.assertEqual(starting_chars, valid)

    def test_should_return_correct_noninitial_characters(self):
        self.put_string('a')
        valid = self.function.get_valid_characters()
        self.assertEqual(non_starting_chars + '|\(', valid)

    def test_should_return_correct_initial_parameters_characters(self):
        self.put_string('a(')
        valid = self.function.get_valid_characters()
        self.assertEqual(starting_chars + "|\)", valid)

    def test_should_return_correct_characters_in_parameter(self):
        self.put_string('a(a')
        valid = self.function.get_valid_characters()
        self.assertEqual(non_starting_chars + "|,|\)", valid)

    def test_should_return_correct_characters_after_comma(self):
        self.put_string('a(a,')
        valid = self.function.get_valid_characters()
        self.assertEqual(starting_chars, valid)

    def test_should_return_correct_characters_after_second_param(self):
        self.put_string('a(a,a')
        valid = self.function.get_valid_characters()
        self.assertEqual(non_starting_chars + "|,|\)", valid)

    def test_should_return_correct_characters_after_closed_parenthesis(self):
        self.put_string('a()')
        valid = self.function.get_valid_characters()
        self.assertEqual("\{", valid)

    def test_should_be_able_to_print_to_string(self):
        function_string = 'abc(a,b,c){}'
        self.put_string(function_string)
        string = self.function.to_string()
        self.assertEqual('function abc(a, b, c){\n\n}', string)

    def put_string(self, str):
        for c in str:
            self.function.put_character(c)

class TestScope(unittest.TestCase):
    def setUp(self):
        self.scope = context.Scope({})

    def test_should_return_correct_initial_characters_with_no_tokens(self):
        expected = {'i', 'w', 'l', 'v', 'c', 'f', 'r', 'b'}
        valid = self.scope.get_valid_characters()
        valid = set([c for c in valid if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_return_correct_initial_characters_with_tokens(self):
        expected = {'i', 'w', 'l', 'v', 'c', 'f', 'b', 'r'}
        c = context.Scope({'bar': {}})
        valid = c.get_valid_characters()
        valid = set([c for c in valid if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_return_correct_characters_in_middle_of_token(self):
        expected = {'u', 'o'}
        c = context.Scope({'bar': {}})
        c.put_character('f')
        valid = c.get_valid_characters()
        valid = set([c for c in valid if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_return_correct_characters_after_opening_function(self):
        self.put_string('function a')
        valid = self.scope.get_valid_characters()
        self.assertEqual(non_starting_chars + '|\(', valid)

    def test_should_be_able_to_enter_multiple_variable_declarations(self):
        self.put_string('varx=5;')
        valid = self.scope.get_valid_characters()
        expected = {'i', 'w', 'l', 'v', 'c', 'f', 'x', 'b', 'r'}
        valid = set([c for c in valid if  c != '|'])
        self.assertEqual(expected, valid)

        self.put_string('lety=')
        valid = set([c for c in self.scope.get_valid_characters() if c != '|'])
        expected = {'\'', 't', 'f', '\\', 'd', '-', '(', '!', 'c', 'x', '+'}
        self.assertEqual(expected, valid)

    def test_should_be_able_to_put_declaration_inside_function(self):
        self.put_string('functionabc(a){')
        expected = {'i', 'w', 'l', 'v', 'c', 'f', '\\', '}', 'a', 'b', 'r'}
        valid = set([c for c in self.scope.get_valid_characters() if c != '|'])
        self.assertEqual(expected, valid)

        self.put_string('varx')
        valid = self.scope.get_valid_characters()
        self.assertEqual(non_starting_chars + "|=", valid)

    def test_should_be_able_to_use_if_else(self):
        self.put_string('if(5==5){varx=7;}elseif(6==6){varx=8;}else{varx=3;}')
        self.assertEqual('if(5==5){\nvar x = 7;\n}\nelse if(6==6){\nvar x = 8;\n}\nelse{\nvar x = 3;\n}', self.scope.to_string())

    def test_should_be_able_to_use_while_loop(self):
        self.put_string('while(5==5){')
        expected = {'i', 'w', 'l', 'v', 'c', 'f', '\\', '}', 'b', 'r'}
        valid = set([c for c in self.scope.get_valid_characters() if c != '|'])
        self.assertEqual(expected, valid)

        self.put_string('}varx=7;')
        valid = set([c for c in self.scope.get_valid_characters() if c != '|'])
        expected.add('x')
        expected.remove('}')
        expected.remove('\\')
        self.assertEqual(expected, valid)

    def test_should_be_able_to_use_for_loop(self):
        self.put_string('letz=8;for(letx=7;x<5;x++){')
        expected = {'i', 'w', 'l', 'v', 'c', 'f', '\\', '}', 'x', 'z', 'b', 'r'}
        valid = set([c for c in self.scope.get_valid_characters() if c != '|'])
        self.assertEqual(expected, valid)

        self.put_string('lety=3;}for(z=1;z<5;z++){letu=3;}')
        str = self.scope.to_string()
        self.assertEqual('let z = 8;\nfor(let x = 7; x<5; x++){\nlet y = 3;\n}\nfor(z = 1; z<5; z++){\nlet u = 3;\n}', str)

    def test_tokens_should_not_get_passed_up_scope(self):
        self.put_string('if(true){letx=5;}')
        self.assertEqual({'console': {'log': {}}}, self.scope.token_dict)

    def test_function_should_be_token_in_parent_scope(self):
        self.put_string('functionabc(a,b,c){varx=8;}')
        valid = set([c for c in self.scope.get_valid_characters() if c != '|'])
        self.assertTrue('a' in valid and 'x' not in valid)

    def test_should_allow_function_call(self):
        self.put_string('functionabc(a,b,c){varx=8;}abc')
        valid = set([c for c in self.scope.get_valid_characters() if c != '|'])
        self.assertTrue('(' in valid)

        self.put_string('(')
        self.assertTrue(')' in self.scope.get_valid_characters())

    def test_should_allow_return(self):
        self.put_string('ret')
        valid = self.scope.get_valid_characters()
        self.assertEqual('u', valid)

    def test_should_be_able_to_use_return_with_no_value(self):
        self.put_string('functionabc(a,b,c){retu')
        valid = self.scope.get_valid_characters()
        self.assertEqual('r', valid)

        self.put_string('rn;}')
        result = self.scope.to_string()
        self.assertEqual('function abc(a, b, c){\nreturn;\n}', result)

    def test_should_be_able_to_use_break(self):
        self.put_string('for(letx=0;x<5;x++){lety=8;brea')
        valid = self.scope.get_valid_characters()
        self.assertEqual('k', valid)

        self.put_string('k;}')
        result = self.scope.to_string()
        self.assertEqual('for(let x = 0; x<5; x++){\nlet y = 8;\nbreak;\n}', result)

    def test_should_be_able_to_return_value(self):
        self.put_string('letx=7;return')
        valid = self.scope.get_valid_characters()
        expected = literal_starting_chars + '|\(|!|c|x|;|\n|+'
        expected = set([c for c in expected if c != '|'])
        valid = set([c for c in valid if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_allow_dot_assignment(self):
        self.put_string('varx=8;')
        self.put_string('x.')
        valid = self.scope.get_valid_characters()
        self.assertEqual(starting_chars, valid)

        self.put_string('y')
        valid = self.scope.get_valid_characters()
        self.assertTrue('=' in valid)

    def test_should_add_property_to_token_tree(self):
        self.put_string('varx=8;')
        self.put_string('x.y=7;')
        self.assertEqual({'y': {}}, self.scope.token_dict['x'])

    def test_should_be_able_to_call_console_log(self):
        self.put_string('console.log')
        valid = self.scope.get_valid_characters()
        self.assertTrue('(' in valid)

        self.put_string('(')
        valid = set([c for c in self.scope.get_valid_characters() if c != '|'])
        expected = set([c for c in literal_starting_chars + '|\(|!|c|\)|+|-' if c != '|'])
        self.assertEqual(expected, valid)

        self.put_string("'here');")
        str = self.scope.to_string()
        self.assertEqual('console.log(\'here\');', str)

    def test_valid_should_be_not_comma_after_opening_string_literal(self):
        self.put_string('console.log(\'')
        valid = self.scope.get_valid_characters()
        self.assertEqual('[^,]|c', valid)

    def test_valid_should_include_equals_after_for_loop_initializer(self):
        self.put_string('for(letx')
        valid = self.scope.get_valid_characters()
        self.assertTrue('=' in valid)

    def test_valid_should_be_e_after_beginning_let_initializer_in_for_loop(self):
        self.put_string('for(l')
        valid = self.scope.get_valid_characters()
        self.assertEqual('e', valid)

    def test_should_allow_completion_of_plus_plus_x(self):
        self.put_string('varx=8;++x')
        valid = self.scope.get_valid_characters()
        self.assertTrue(';' in valid)

    def test_should_allow_x_plus_plus(self):
        self.put_string('varx=8;x')
        valid = self.scope.get_valid_characters()
        self.assertTrue('+' in valid)

        self.put_string('+')
        valid = self.scope.get_valid_characters()
        self.assertTrue('+' in valid)

    def test_should_include_semicolon_at_last_line_of_scope(self):
        self.put_string('varx=9;x++')
        str = self.scope.to_string()
        self.assertTrue(str[len(str)-1] == ';')

    def test_should_not_include_semicolon_if_last_character_is_brace(self):
        self.put_string('if(true){console.log(x);}')
        str = self.scope.to_string()
        self.assertTrue(str[len(str)-1] != ';')

    def test_should_allow_else(self):
        self.put_string('letx=7;if(true){console.log(x);}')
        self.assertTrue('e' in self.scope.get_valid_characters())

    def put_string(self, str):
        for c in str:
            self.scope.put_character(c)

class TestVariableDeclaration(unittest.TestCase):
    def setUp(self):
        self.declaration = context.VariableDeclaration("var", {})

    def test_should_return_correct_characters_after_declarator_flag(self):
        valid = self.declaration.get_valid_characters()
        self.assertEqual(starting_chars, valid)

    def test_should_return_correct_characters_after_first_character(self):
        self.declaration.put_character('a')
        valid = self.declaration.get_valid_characters()
        self.assertEqual(non_starting_chars + '|=', valid)

    def test_should_return_correct_characters_after_equal_sign(self):
        self.put_string('a=')
        valid = set([c for c in self.declaration.get_valid_characters() if c != '|'])
        expected = set([c for c in '\'|t|f|\d|-|\(|!|+' if c != '|'])

        self.assertEqual(expected, valid)

    def test_should_return_correct_characters_after_starting_num_value(self):
        self.put_string('a=5')
        valid = self.declaration.get_valid_characters()
        self.assertEqual("&|\\||-|\\+|\\/|\\*|>|<|!|=|%|\\d|-|\\+|\\.|\\)|;|\n|\\.", valid)

    def test_should_return_correct_characters_after_starting_string_literal(self):
        self.put_string('a="')
        valid = self.declaration.get_valid_characters()
        self.assertEqual('[^,]', valid)

    def test_should_return_correct_value_after_starting_boolean_literal(self):
        self.put_string('a=t')
        valid = self.declaration.get_valid_characters()
        self.assertEqual('r', valid)

        declaration = context.VariableDeclaration('var', {'test': {}, 'asdf':{}})
        expected = {'e', 'r'}
        declaration.put_character('a')
        declaration.put_character('=')
        declaration.put_character('t')
        valid = declaration.get_valid_characters()
        valid = set([c for c in valid if c != '|'])
        self.assertEqual(expected, valid)

        declaration.put_character('r')
        valid = declaration.get_valid_characters()
        self.assertEqual('u', valid)

    def test_should_be_able_to_print_to_string(self):
        self.put_string('x=5;')
        str = self.declaration.to_string()
        self.assertEqual('var x = 5', str)

    def test_should_allow_setting_properties(self):
        declaration = context.VariableDeclaration('', {'x': {}})
        str = 'x.'

        for c in str:
            declaration.put_character(c)

        valid = declaration.get_valid_characters()
        self.assertEqual(starting_chars + '|=', valid)

        declaration.put_character('y')
        valid = declaration.get_valid_characters()
        self.assertTrue('=' in valid)

    def put_string(self, str):
        for c in str:
            self.declaration.put_character(c)

class TestExpression(unittest.TestCase):
    def setUp(self):
        self.exp = context.Expression({}, False, False)

    def test_should_require_token_literal_or_not_to_start(self):
        exp = context.Expression({'obama': {}}, False, False)
        valid = set([c for c in exp.get_valid_characters() if c != '|'])
        expected = set([c for c in literal_starting_chars + "|\(|!|o|+|-" if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_require_token_literal_or_open_paren_after_unary_op(self):
        exp = context.Expression({'truman': {}}, False, False)
        exp.put_character('!')
        valid = exp.get_valid_characters()
        self.assertEqual(literal_starting_chars + '|t|\(|=', valid)

    def test_should_require_parens_or_binary_op_after_token_and_literal(self):
        exp = context.Expression({'drumpf': {}}, False, False)
        exp.put_character('d')
        exp.put_character('r')
        exp.put_character('u')
        exp.put_character('m')
        exp.put_character('p')
        exp.put_character('f')
        valid = exp.get_valid_characters()
        self.assertEqual(binary_operator_chars + '|\)|;|\n|\.', valid)

    def test_should_require_literal_token_or_unary_after_open_paren(self):
        exp = context.Expression({'coolidge': {}}, False, False)
        exp.put_character('(')
        valid = set([c for c in exp.get_valid_characters() if c != '|'])
        expected = set([c for c in literal_starting_chars + 'c|!|\(' if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_require_binary_op_after_close_paren(self):
        exp = context.Expression({'adams': {}}, False, False)
        exp.put_character(')')
        valid = exp.get_valid_characters()
        self.assertEqual(binary_operator_chars, valid)

    def test_should_require_finishing_token_in_middle_of_token(self):
        exp = context.Expression({'mckinley': {}}, False, False)
        exp.put_character('m')
        valid = exp.get_valid_characters()
        self.assertEqual('c', valid)

    def test_should_require_finishing_operator_in_middle_of_binary_op(self):
        exp = context.Expression({'roosevelt2': {}}, False, False)
        exp.put_character('>')
        valid = exp.get_valid_characters()
        self.assertEqual(literal_starting_chars + "|\(|!|=|r", valid, valid)

    def test_should_require_numbers_in_middle_of_num_literal(self):
        exp = context.Expression({'teddyyyyy': {}}, False, False)
        exp.put_character('5')
        valid = exp.get_valid_characters()
        self.assertEqual('&|\\||-|\\+|\\/|\\*|>|<|!|=|%|\\d|-|\\+|\\.|\\)|;|\n|\\.', valid)

    def test_should_require_any_char_in_string_literal(self):
        self.put_string('"')
        valid = self.exp.get_valid_characters()
        self.assertEqual('[^,]', valid)

    def test_should_require_finish_literal_in_bool_literal(self):
        self.put_string('tr')
        valid = self.exp.get_valid_characters()
        self.assertEqual('u', valid)

    def test_should_require_operator_after_string_literal(self):
        self.put_string('\'abc\'')
        valid = self.exp.get_valid_characters()
        self.assertEqual(binary_operator_chars + '|\)|;|\n|\.', valid)

    def test_should_be_able_to_print_to_string(self):
        value = "'abc' == 5 || 32 == 7"
        self.put_string(value)
        self.assertEqual(value, self.exp.to_string())

    def test_should_allow_plus_as_initial_character(self):
        valid = self.exp.get_valid_characters()
        self.assertTrue('+' in valid)

    def test_symbol_should_be_complete_with_plus_plus(self):
        self.put_string('x++')
        self.assertTrue(self.exp.complete())

    def test_should_allow_plus_after_first_plus(self):
        self.put_string('x+')
        self.assertTrue('+' in self.exp.get_valid_characters())

    def test_should_be_able_to_use_mod_operator(self):
        exp = context.Expression({'x': {}}, False, False)
        exp.put_character('x')
        valid = exp.get_valid_characters()
        self.assertTrue('%' in valid)

    def put_string(self, str):
        for c in str:
            self.exp.put_character(c)

class TestConditional(unittest.TestCase):
    def setUp(self):
        self.condition = context.Conditional('if', {})

    def test_should_require_open_paren_to_start(self):
        valid = self.condition.get_valid_characters()
        self.assertEqual('\(', valid)

    def test_should_require_literal_token_or_unary_after_open_paren(self):
        condition = context.Conditional('if', {'taylor': {}, 'nixon': {}})
        condition.put_character('(')
        valid = set([c for c in condition.get_valid_characters() if c != '|'])
        expected = set([c for c in literal_starting_chars + "(|!|t|n|+" if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_allow_closed_paren_after_opening_condition(self):
        self.put_string('(5==5')
        valid = self.condition.get_valid_characters()
        self.assertTrue(')' in valid)

    def test_should_return_literal_and_token_starting_chars_after_open_body(self):
        condition = context.Conditional('if', {'quincy_adams': {}})
        for c in '(5==5){':
            condition.put_character(c)

        valid = condition.get_valid_characters()
        expected = {'i', 'w', 'l', 'v', 'c', 'f', 'q', '\\', '}', 'b', 'r'}
        valid = set([c for c in valid if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_be_able_to_convert_to_string(self):
        condition = context.Conditional('if', {'quincy_adams': {}})
        str = '(5==5){varx=7}'
        for c in str:
            condition.put_character(c)

        self.assertEqual('if(5==5){\nvar x = 7;\n}', condition.to_string())

    def test_should_allow_brace_after_closing_condition(self):
        self.put_string('(5==5)')
        valid = self.condition.get_valid_characters()
        self.assertTrue('{' in valid)

    def put_string(self, str):
        for c in str:
            self.condition.put_character(c)

class TestWhileLoop(unittest.TestCase):
    def setUp(self):
        self.loop = context.WhileLoop({})

    def test_should_require_paren_to_start(self):
        valid = self.loop.get_valid_characters()
        self.assertEqual('\(', valid)

    def test_should_require_starting_expression_characters_after_open_paren(self):
        self.loop.put_character('(')
        valid = set([c for c in self.loop.get_valid_characters() if c != '|'])
        expected = set([c for c in literal_starting_chars + "|\(|!|+|-" if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_require_body_starting_chars_after_open_body(self):
        loop = context.WhileLoop({'taft': {}})
        for c in '(5==5){':
            loop.put_character(c)

        expected = {'i', 'w', 'l', 'v', 'c', 'f', 't', '\\', '}', 'b', 'r'}
        valid = loop.get_valid_characters()
        valid = set([c for c in valid if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_allow_closed_paren_after_opening_condition(self):
        self.put_string('(5==5')
        valid = self.loop.get_valid_characters()
        self.assertTrue(')' in valid)

    def test_should_allow_brace_after_closing_condition(self):
        self.put_string('(5==5)')
        valid = self.loop.get_valid_characters()
        self.assertTrue('{' in valid)

    def test_should_be_able_to_convert_to_string(self):
        self.put_string('(6==6){varx=7;vary=8;}')
        result = self.loop.to_string()
        self.assertEqual('while(6==6){\nvar x = 7;\nvar y = 8;\n}', result)

    def put_string(self, str):
        for c in str:
            self.loop.put_character(c)

class TestForLoop(unittest.TestCase):
    def setUp(self):
        self.loop = context.ForLoop({})

    def test_should_require_paren_to_start(self):
        valid = self.loop.get_valid_characters()
        self.assertEqual('\(', valid)

    def test_should_require_token_or_initializer_in_initializer(self):
        loop = context.ForLoop({'johnson': {}})
        loop.put_character('(')
        loop.put_character('j')
        valid = loop.get_valid_characters()
        self.assertEqual('o', valid)

    def test_should_require_expression_in_condition(self):
        loop = context.ForLoop({'bush': {}})
        initializer = '(letx=0;'

        for c in initializer:
            loop.put_character(c)

        valid = set([c for c in loop.get_valid_characters() if c != '|'])
        expected = set(['x', 'b'])
        self.assertEqual(expected, valid)

    def test_should_require_expression_in_increment(self):
        loop = context.ForLoop({'dubbya_bush': {}})
        starter = '(letx=0;x<7;'

        for c in starter:
            loop.put_character(c)

        valid = set([c for c in loop.get_valid_characters() if c != '|'])
        expected = set(['d', 'x'])
        self.assertEqual(expected, valid)

    def test_should_require_body_starting_chars_in_body(self):
        loop = context.ForLoop({'ford': {}})
        starter = '(letx=0;x<7;x++){'

        for c in starter:
            loop.put_character(c)

        valid = loop.get_valid_characters()
        expected = {'i', 'w', 'l', 'v', 'c', 'f', '\\', '}', 'x', 'b', 'r'}
        valid = set([c for c in valid if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_require_open_brace_or_new_line_after_header(self):
        loop = context.ForLoop({'eisenhower': {}})
        starter = '(letx=0;x<7;x++)'

        for c in starter:
            loop.put_character(c)

        valid = loop.get_valid_characters()
        self.assertEqual('\{|\n', valid)

    def test_should_be_able_to_print_to_string(self):
        loop = context.ForLoop({'van_buren': {}})
        str = '(letx=0;x<7;x++){lety=8;}'

        for c in str:
            loop.put_character(c)

        self.assertEqual('for(let x = 0; x<7; x++){\nlet y = 8;\n}', loop.to_string())

    def test_valid_should_include_equals_in_initializer(self):
        self.put_string('(letx')
        self.assertTrue('=' in self.loop.get_valid_characters())

    def test_should_allow_plus_plus_in_increment(self):
        self.put_string('for(letx=0;x<10;x++')
        valid = self.loop.get_valid_characters()
        self.assertTrue(')' in valid)

    def put_string(self, str):
        for c in str:
            self.loop.put_character(c)

class TestFunctionCall(unittest.TestCase):
    def setUp(self):
        self.call = context.FunctionCall({'clinton': {}, 'clint': {}})

    def test_should_require_token_to_start(self):
        valid = set([c for c in self.call.get_valid_characters() if c != '|'])
        expected = {'c'}
        self.assertEqual(expected, valid)

        self.call.put_character('c')
        valid = self.call.get_valid_characters()
        self.assertEqual('l', valid)

    def test_should_require_paren_after_function_name(self):
        self.put_string('clint')
        expected = {'\\', '(', 'o'}
        valid = set([c for c in self.call.get_valid_characters() if c != '|'])
        self.assertEqual(expected, valid)

        self.put_string('on')
        self.assertEqual('\(', self.call.get_valid_characters())

    def test_should_require_token_or_literal_as_param(self):
        self.put_string('clinton(')
        valid = set([c for c in self.call.get_valid_characters() if c != '|'])
        expected = set([c for c in '\'|t|f|\d|-|\(|!|c|\)|+|-' if c != '|'])
        self.assertEqual(expected, valid)

        self.put_string('c')
        valid = self.call.get_valid_characters()
        self.assertEqual('l', valid)

    def test_should_be_able_to_take_multiple_params(self):
        self.put_string('clinton(clint,')
        valid = set([c for c in self.call.get_valid_characters() if c != '|'])
        expected = set([c for c in '\'|t|f|\d|-|\(|!|c|+' if c != '|'])
        self.assertEqual(expected, valid)

        self.put_string('c')
        valid = self.call.get_valid_characters()
        self.assertEqual('l', valid)

    def test_should_allow_closing_param_list(self):
        self.put_string('clinton(')
        valid = self.call.get_valid_characters()
        self.assertTrue(')' in valid)

    def test_should_allow_comma_after_each_param(self):
        self.put_string('clinton(clint')
        valid = self.call.get_valid_characters()
        self.assertTrue(',' in valid and ')' in valid)

    def test_should_be_able_to_print_to_string(self):
        self.put_string('clinton(clint);')
        self.assertTrue('clinton(clint);', self.call.to_string())

    def test_should_be_able_to_print_console_log_to_string(self):
        self.put_string('console.log(\'here\');')
        self.assertTrue('console.log(\'here\')', self.call.to_string())

    def put_string(self, str):
        for c in str:
            self.call.put_character(c)

class TestAuxiliaryFlag(unittest.TestCase):
    def setUp(self):
        self.flag = context.AuxiliaryFlag('return', {})

    def test_should_require_literal_semicolon_or_new_line(self):
        expected = set([c for c in '\'|t|f|\\d|-|\(|!|;|\n|+|-' if c != '|'])
        valid = set([c for c in self.flag.get_valid_characters() if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_return_correct_value_in_put_character(self):
        result = self.flag.put_character('x')
        self.assertFalse(result)

        self.setUp()
        result = self.flag.put_character(';')
        self.assertTrue(result)

        result = self.flag.put_character('\n')
        self.assertTrue(result)

    def test_should_be_able_to_print_to_string(self):
        result = self.flag.to_string()
        self.assertEqual('return', result)

if __name__ == '__main__':
    unittest.main()
