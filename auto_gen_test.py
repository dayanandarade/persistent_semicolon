import ast
import importlib
from inspect import getmembers, isclass, isfunction
from dataclasses import dataclass, field
from html.parser import HTMLParser
import time
from typing import List
import multiprocessing
import subprocess
import os

module_lists = []

coverage_file_path = "/htmlcov"

@dataclass
class FileDetails:
    file_name: str
    file_fucntions_list: List = field(default_factory=[])
    file_fucntions_list: List = field(default_factory=[])


    def add_file(self, file_name):
        self.file_fucntions_list.append(file_name)

    def get_files(self):
        return self.file_fucntions_list


@dataclass
class LineNumbersList:
    def __init__(self, file_name, line_numbers):
        self.file_name:str = file_name
        self.line_numbers: List = line_numbers


class CoverageFileParser(HTMLParser):
    
    def __init__(self):
        super().__init__()
        self.inside_p_tag = False
        self.inside_span_tag = False
        self.inside_a_tag = False
        self.line_numbers = []
 
    def handle_starttag(self, tag, attrs):
        if tag == "p":
            for attr in attrs:
                if attr[0] == "class" and "mis" in attr[1] and "show_mis" in attr[1]:
                    # print(f" inside required P tag")
                    self.inside_p_tag = True
        elif tag == "span" and self.inside_p_tag:
            for attr in attrs:
                if attr[0] == "class" and "n" in attr[1]:
                    # print(f" inside required span tag")
                    self.inside_span_tag = True
        elif tag == "a" and self.inside_p_tag and self.inside_span_tag:
            # print(f" inside required a tag")
            self.inside_a_tag = True

    def handle_data(self, data: str):
        if self.inside_p_tag and self.inside_span_tag and self.inside_a_tag:
            # print(f" gor data in a tag")
            self.line_numbers.append(data)
  
    def handle_endtag(self, tag):
        if self.inside_a_tag:
            self.inside_p_tag,self.inside_span_tag,self.inside_a_tag= False,False,False


class IndexFileParser(HTMLParser):
    # add logic to check missing lines count is 0 or not if it is then ignore file name
    def __init__(self):
        super().__init__()
        self.inside_td_tag = False
        self.inside_a_tag = False
        self.filename_in_href:str = ""
        self.href_file_names = {}
 
    def handle_starttag(self, tag, attrs):
        if tag == "td":
            for attr in attrs:
                if attr[0] == "class" and "name" in attr[1] and "left" in attr[1]:
                    self.inside_td_tag = True
        elif tag == "a" and self.inside_td_tag:
            for attr in attrs:
                if attr[0] == "href":
                    self.filename_in_href = str(attr[1])
                    self.inside_a_tag = True

    def handle_data(self, data: str):
        if self.inside_a_tag and self.inside_td_tag:
            self.href_file_names[data] = self.filename_in_href
            self.filename_in_href = ""

    def handle_endtag(self, tag):
        if tag == "td":
            self.inside_td_tag = False
        elif tag == "a":
            self.inside_td_tag = False


def read_index_file(coverage_file_path):

    with open(coverage_file_path, 'r') as index:
        index_html_content = index.read()

    parser = IndexFileParser()
    parser.feed(index_html_content)
    parser_result = parser.href_file_names

    py_to_html_mapping = {}

    for i in parser_result.keys():
        file_path = i
        file_path_splitted = file_path.split("/")
        
        if not((file_path_splitted[0] in ("tests", "test")) or (file_path_splitted[-1].startswith("__")) or (file_path_splitted[-1].endswith("pycache") or file_path == "Total")):
            py_to_html_mapping[i] = parser_result[i]

    return py_to_html_mapping


def get_line_numbers(py_to_html_mapping):
    
    py_file_name = py_to_html_mapping[0]
    py_html_file_name = py_to_html_mapping[1]

    with open(os.path.join(f"{project_directory_name}{coverage_file_path}", py_html_file_name), 'r') as html_file:
        py_html_content = html_file.read()
    
    parser = CoverageFileParser()
    parser.feed(py_html_content)

    return LineNumbersList(py_file_name, parser.line_numbers)


@dataclass
class ModuleDetails:
    module_name: str
    module_files_list: List = field(default_factory=[])

    def add_file(self, file_name):
        self.module_files_list.append(file_name)

    def get_files(self):
        return self.module_files_list


def get_methods_code_from_file(file_path, line_numbers):
    
    functions_list = []

    with open(file_path, 'r') as file:
        content = file.read()

    tree = ast.parse(content)

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):

            (start_lineno, end_lineno) = (node.lineno, node.end_lineno)

            for line in line_numbers:

                if start_lineno < int(line) <= end_lineno:

                    functions_list.append('\n'.join(content.split('\n')[start_lineno - 1:end_lineno]))

    return list(set(functions_list))


def add_test_cases(file_path, test_cases, new):

    if new:
 
        with open(f"{root_directory}/tests/{file_path}", 'w') as file:

            for func in test_cases:
                file.write(f"\n{func}\n")

    else:

        with open(f"{root_directory}/tests/{file_path}", 'a') as file:

            for func in test_cases:
                file.write(f"\n{func}\n")
            
            
def search_test_case(file_name, test_case):

    for module in module_lists:

        if module.module_name == 'tests':

            for file in module.get_files():

                test_file_name = f"test_{os.path.basename(file_name)}"

                if file == test_file_name:

                    print("file found",file, test_file_name, file_name)
                    add_test_cases(test_file_name, test_case, False)
                    
            else:

                print("file not found", test_file_name, file_name)
                add_test_cases(test_file_name, test_case, True)




                # os.path.isfile(test_file_name)


            #     full_module_name = f"{module.module_name}.{file.replace('.py', '')}"
            #     module_ = importlib.import_module(full_module_name)
            #     functions_list = getmembers(module_, isfunction)
            #     classes = getmembers(module_, isclass)
 
            #     for func in functions_list:
 
            #         if func[0] == method_name:
 
            #             print(f'Module Name {full_module_name} Function Name {func[0]} {func[1].__code__.co_firstlineno} \n\n{getsource(func[1])}')
 
            #     print(functions_list, classes)


def get_root_and_project_directory_name(directory_path):

    return directory_path, os.path.split(directory_path)[-1]


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


def run_tests_and_generate_report():

  process1 = subprocess.Popen(["coverage", "run", "-m", "pytest"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)   
 
  process2 = subprocess.Popen(["coverage", "html"], stdout=subprocess.PIPE)
   
  process1.wait()
  process2.wait()


def run_multiprocess(index_file_path):

    py_to_html_mapping = read_index_file(index_file_path)
    pool = multiprocessing.Pool(10)
    final_result = pool.map(get_line_numbers, py_to_html_mapping.items())
    pool.close()

    return final_result


def get_methods_from_objects(object_list):
    
    object_lists = []

    for line_obj in object_list:
        # print(f" {line_obj.file_name}: {line_obj.line_numbers}")
        method = get_methods_code_from_file(f"{project_directory_name}/{line_obj.file_name}", line_obj.line_numbers)
        # print(method)
        object_lists.append(FileDetails(file_name=line_obj.file_name, file_fucntions_list=method))

    return object_lists
    

def gen_ai_api_call(object_list):

    for obj in object_list:
        print(obj.file_name, len(obj.file_fucntions_list))

        for function in obj.file_fucntions_list:
            print(function)
            break


def insert_test_cases(func_list):

    for obj in func_list:

        search_test_case(obj.file_name, obj.file_fucntions_list)


root_directory, project_directory_name = get_root_and_project_directory_name("/home/shalu/Desktop/Semicolon/flask")
# get_all_modules_and_files(root_directory)
# object_list = run_multiprocess(f"{root_directory}{coverage_file_path}/index.html")
# a = get_methods_from_objects(object_list)
# # gen_ai_api_call(a)

# insert_test_cases(a)

iterate_count = 3

while iterate_count:

    print("Calling Coverage Command....")
    # run_tests_and_generate_report()

    # get_all_modules_and_files(root_directory)
    # object_list = run_multiprocess(f"{root_directory}{coverage_file_path}/index.html")
    # file_objs = get_methods_from_objects(object_list)

    print("Generating AI API Call....")
    # gen_ai_api_call(a)

    print("Inserting Test Cases in Test Files....")
    # insert_test_cases(file_objs)

    iterate_count -= 1






############# 
## Instead of creating testcases for entire function we should create testcases only for missing lines
## if generated testcase function is already present in the testfile then we should append or create another
#############














