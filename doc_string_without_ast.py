import os
import ast
import time
import threading
import importlib
import multiprocessing
from queue import Queue
from typing import List
from dataclasses import dataclass, field
from inspect import getmembers, isfunction, getsource, isclass

module_lists = []

@dataclass
class ModuleDetails:
    module_name: str
    module_files_list: List = field(default_factory=[])

    def add_file(self, file_name):
        self.module_files_list.append(file_name)

    def get_files(self):
        return self.module_files_list


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


def get_all_modules_and_files(directory_location):
    
    module_name = directory_location.split(project_directory_name)[-1]

    if module_name == '':

        module_name = project_directory_name

    else:

        module_list = module_name.split('/')

        if len(module_list) == 2:

            module_name = module_list[1]

        elif len(module_list) >= 3:

            module_name = '.'.join(module_list[1:])

    file_list = []

    modules_files = [x for x in os.listdir(directory_location) if not (x.startswith('__') or x.startswith('.'))]

    for dirs in modules_files:

        if os.path.isfile(os.path.join(directory_location, dirs)) and (not dirs.startswith('__')):

            file_list.append(dirs)

        if os.path.isdir(os.path.join(directory_location, dirs)) and (not dirs.startswith('__')):

            get_all_modules_and_files(os.path.join(directory_location, dirs))

    module_lists.append(ModuleDetails(module_name=module_name, module_files_list=file_list))


def get_root_and_project_directory_name(directory_path):

    return os.path.dirname(directory_path), os.path.basename(os.path.dirname(directory_path))


def search_test_case(method_name, module_list):

    for module in module_lists:

        if module.module_name == 'tests':

            for file in module.get_files():

                full_module_name = f"{module.module_name}.{file.replace('.py', '')}"
                module_ = importlib.import_module(full_module_name)
                functions_list = getmembers(module_, isfunction)
                classes = getmembers(module_, isclass)

                for func in functions_list:

                    if func[0] == method_name:

                        print(f'Module Name {full_module_name} Function Name {func[0]} {func[1].__code__.co_firstlineno} \n\n{getsource(func[1])}')

                print(functions_list, classes) 


def add_test_cases(file_path, test_cases):

    with open(file_path, 'a') as file:
        file.write(f"\n{test_cases}\n")


root_directory, project_directory_name = get_root_and_project_directory_name(__file__)

# get_all_modules_and_files(root_directory)

# search_test_case('test_yayayayaya', module_lists)

# scan_directory(root_directory)

# add_test_cases(os.path.join(root_directory, 'tests', 'test_main.py'), t)