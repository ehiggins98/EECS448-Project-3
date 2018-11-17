import unittest
import context

starting_chars = "[A-z$]"
non_starting_chars = starting_chars + "|\\d"
number_characters = '\\d|-|\+'
literal_starting_chars = '\"|\'|t|f|\d|-'
binary_operator_chars = '&|\||-|\+|\/|\*|>|<|!|='

class TestFunction(unittest.TestCase):
    def setUp(self):
        self.function = context.Function([])

    def test_should_return_correct_initial_characters(self):
        valid = self.function.get_valid_characters()
        self.assertEqual(starting_chars, valid)

    def test_should_return_correct_noninitial_characters(self):
        self.put_string('a')
        valid = self.function.get_valid_characters()
        self.assertEqual(non_starting_chars + '|(', valid)

    def test_should_return_correct_initial_parameters_characters(self):
        self.put_string('a(')
        valid = self.function.get_valid_characters()
        self.assertEqual(starting_chars + "|)", valid)

    def test_should_return_correct_characters_in_parameter(self):
        self.put_string('a(a')
        valid = self.function.get_valid_characters()
        self.assertEqual(non_starting_chars + "|,|)", valid)

    def test_should_return_correct_characters_after_comma(self):
        self.put_string('a(a,')
        valid = self.function.get_valid_characters()
        self.assertEqual(starting_chars, valid)

    def test_should_return_correct_characters_after_second_param(self):
        self.put_string('a(a,a')
        valid = self.function.get_valid_characters()
        self.assertEqual(non_starting_chars + "|,|)", valid)

    def test_should_return_correct_characters_after_closed_parenthesis(self):
        self.put_string('a()')
        valid = self.function.get_valid_characters()
        self.assertEqual("{", valid)

    def test_should_be_able_to_print_to_string(self):
        function_string = 'abc(a, b, c){}'
        self.put_string(function_string)
        string = self.function.to_string()
        self.assertEqual('function ' + function_string, string)

    def put_string(self, str):
        for c in str:
            self.function.put_character(c)

class TestScope(unittest.TestCase):
    def setUp(self):
        self.scope = context.Scope([])

    def test_should_return_correct_initial_characters_with_no_tokens(self):
        expected = {'d', 'i', 'w', 'l', 'v', 'c', 'f'}
        valid = self.scope.get_valid_characters()
        valid = set([c for c in valid if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_return_correct_initial_characters_with_tokens(self):
        expected = {'d', 'i', 'w', 'l', 'v', 'c', 'f', 'b'}
        c = context.Scope(['bar'])
        valid = c.get_valid_characters()
        valid = set([c for c in valid if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_return_correct_characters_in_middle_of_token(self):
        expected = {'u', 'o'}
        c = context.Scope(['bar'])
        c.put_character('f')
        valid = c.get_valid_characters()
        valid = set([c for c in valid if c != '|'])
        self.assertEqual(expected, valid)

    def test_should_return_correct_characters_after_opening_function(self):
        self.put_string('function a')
        valid = self.scope.get_valid_characters()
        self.assertEqual(non_starting_chars + '|(', valid)

    def test_should_be_able_to_enter_multiple_variable_declarations(self):
        self.put_string('varx=5;')
        valid = self.scope.get_valid_characters()
        expected = {'d', 'i', 'w', 'l', 'v', 'c', 'f'}
        valid = set([c for c in valid if  c != '|'])
        self.assertEqual(expected, valid)

        self.put_string('lety=')
        valid = self.scope.get_valid_characters()
        expected = starting_chars + '|"|\'|t|f|\\d|-'
        self.assertEqual(expected, valid)

    def test_should_be_able_to_put_declaration_inside_function(self):
        self.put_string('function abc(a){')
        expected = {'d', 'i', 'w', 'l', 'v', 'c', 'f'}
        valid = set([c for c in self.scope.get_valid_characters() if c != '|'])
        self.assertEqual(expected, valid)

        self.put_string('varx')
        valid = self.scope.get_valid_characters()
        self.assertEqual(non_starting_chars + "|=|.", valid)

    def put_string(self, str):
        for c in str:
            self.scope.put_character(c)

class TestVariableDeclaration(unittest.TestCase):
    def setUp(self):
        self.declaration = context.VariableDeclaration("var", [])

    def test_should_return_correct_characters_after_declarator_flag(self):
        valid = self.declaration.get_valid_characters()
        self.assertEqual(starting_chars, valid)

    def test_should_return_correct_characters_after_first_character(self):
        self.declaration.put_character('a')
        valid = self.declaration.get_valid_characters()
        self.assertEqual(non_starting_chars + '|=|.', valid)

    def test_should_return_correct_characters_after_equal_sign(self):
        self.put_string('a=')
        valid = self.declaration.get_valid_characters()
        self.assertEqual(starting_chars + '|"|\'|t|f|\\d|-', valid)

    def test_should_return_correct_characters_after_starting_num_value(self):
        self.put_string('a=5')
        valid = self.declaration.get_valid_characters()
        self.assertEqual("&|\||-|\+|\/|\*|>|<|!|=|)", valid)

    def test_should_return_correct_characters_after_starting_string_literal(self):
        self.put_string('a="')
        valid = self.declaration.get_valid_characters()
        self.assertEqual('.', valid)

    def test_should_return_correct_value_after_starting_boolean_literal(self):
        self.put_string('a=t')
        valid = self.declaration.get_valid_characters()
        self.assertEqual('r', valid)

        declaration = context.VariableDeclaration('var', ['test', 'asdf'])
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
        self.assertEqual('var x = 5;', str)

    def put_string(self, str):
        for c in str:
            self.declaration.put_character(c)

class TestExpression(unittest.TestCase):
    def setUp(self):
        self.exp = context.Expression([])

    def test_should_require_token_literal_or_not_to_start(self):
        exp = context.Expression(['obama'])
        valid = exp.get_valid_characters()
        self.assertEqual(literal_starting_chars + "|(|!|o", valid)

    def test_should_require_token_literal_or_open_paren_after_unary_op(self):
        exp = context.Expression(['truman'])
        exp.put_character('!')
        valid = exp.get_valid_characters()
        self.assertEqual(literal_starting_chars + '|t|(|=', valid)

    def test_should_require_parens_or_binary_op_after_token_and_literal(self):
        exp = context.Expression(['drumpf'])
        exp.put_character('d')
        exp.put_character('r')
        exp.put_character('u')
        exp.put_character('m')
        exp.put_character('p')
        exp.put_character('f')
        valid = exp.get_valid_characters()
        self.assertEqual(binary_operator_chars + '|)', valid)

    def test_should_require_literal_token_or_unary_after_open_paren(self):
        exp = context.Expression(['coolidge'])
        exp.put_character('(')
        valid = exp.get_valid_characters()
        self.assertEqual(literal_starting_chars + '|c|!', valid)

    def test_should_require_binary_op_after_close_paren(self):
        exp = context.Expression(['adams'])
        exp.put_character(')')
        valid = exp.get_valid_characters()
        self.assertEqual(binary_operator_chars, valid)

    def test_should_require_finishing_token_in_middle_of_token(self):
        exp = context.Expression(['mckinley'])
        exp.put_character('m')
        valid = exp.get_valid_characters()
        self.assertEqual('c', valid)

    def test_should_require_finishing_operator_in_middle_of_binary_op(self):
        exp = context.Expression(['roosevelt2'])
        exp.put_character('>')
        valid = exp.get_valid_characters()
        self.assertEqual(literal_starting_chars + "|(|!|=|r", valid, valid)

    def test_should_require_numbers_in_middle_of_num_literal(self):
        exp = context.Expression(['teddyyyyy'])
        exp.put_character('5')
        valid = exp.get_valid_characters()
        self.assertEqual('&|\||-|\+|\/|\*|>|<|!|=|)', valid)

    def test_should_require_any_char_in_string_literal(self):
        self.put_string('"')
        valid = self.exp.get_valid_characters()
        self.assertEqual('.', valid)

    def test_should_require_finish_literal_in_bool_literal(self):
        self.put_string('tr')
        valid = self.exp.get_valid_characters()
        self.assertEqual('u', valid)

    def test_should_require_operator_after_string_literal(self):
        self.put_string('"abc"')
        valid = self.exp.get_valid_characters()
        self.assertEqual(binary_operator_chars + '|)', valid)

    def test_should_be_able_to_print_to_string(self):
        value = "'abc' == 5 || 32 == 7"
        self.put_string(value)
        self.assertEqual(value, self.exp.to_string())

    def put_string(self, str):
        for c in str:
            self.exp.put_character(c)

if __name__ == '__main__':
    unittest.main()
