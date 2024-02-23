import os
import ast
import time
import multiprocessing

def get_openapi_doc(method_definition):
    
    return '\n:param1 value1\n:param1 value1\n:param2 value2\n\n'

def update_file_with_doc_string(file_path):
    
    with open(file_path, 'r') as file:
        content = file.read()
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and (not ast.get_docstring(node)):
            (start_lineno, end_lineno) = (node.lineno, node.end_lineno)
            method_definition = '\n'.join(content.split('\n')[start_lineno - 1:end_lineno])
            docstring = get_openapi_doc(method_definition)
            if docstring:
                node.body.insert(0, ast.Expr(ast.Constant(docstring)))
    with open(file_path, 'w') as file:
        file.write(ast.unparse(tree))

def scan_directory(directory):
    
    start_time = time.time()
    for (root, _, files) in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.py'):
                file_path = os.path.join(root, file_name)
                multiprocessing.Process(target=update_file_with_doc_string, args=(file_path,)).start()
    print(f'Time Taken {time.time() - start_time:.03} sec')

root_directory = os.path.dirname(__file__)

scan_directory(root_directory)