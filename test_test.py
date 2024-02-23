import ast

def get_method_code_from_file(file_path, line_number):
    
    with open(file_path, 'r') as file:
        content = file.read()
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            (start_lineno, end_lineno) = (node.lineno, node.end_lineno)
            if start_lineno < line_number <= end_lineno:
                return '\n'.join(content.split('\n')[start_lineno - 1:end_lineno])

def get_methods_code_from_file(file_path, line_numbers):
    
    functions_list = []
    with open(file_path, 'r') as file:
        content = file.read()
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            (start_lineno, end_lineno) = (node.lineno, node.end_lineno)
            for line in line_numbers:
                if start_lineno < line <= end_lineno:
                    functions_list.append('\n'.join(content.split('\n')[start_lineno - 1:end_lineno]))
    return functions_list

# print(get_methods_code_from_file('index.py', [20, 74, 105]))


def mock_gen_ai_response():

    return """def test_2_yayayayaya():
                \"\"\"
                :param1 value1
                :param1 value1
                :param2 value2

                \"\"\"
    pass"""


print(mock_gen_ai_response())

def find_test_cases(file_path):

    with open(file_path, 'r') as file:
        content = file.read()

    tree = ast.parse(content)

    test_cases = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):

            test_cases.append(node.name)
            
    return test_cases

def insert_test_cases(test_case):

    with open('test_case.py', 'a') as file:
        file.write(test_case)


print(find_test_cases('tests/test_main.py'))