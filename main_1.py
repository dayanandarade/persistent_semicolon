import os
import threading
import importlib
from queue import Queue
from typing import List
from dataclasses import dataclass, field
from inspect import getmembers, isfunction, getsource, isclass
module_lists = []

@dataclass
class Modules:
    module_name: str
    modules_list: List = field(default_factory=[])

    def add_module(self, module_name):
        """
                :param1 value1
                :param1 value1
                :param2 value2

                """
        self.modules_list.append(module_name)

    def get_modules(self):
        """
                :param1 value1
                :param1 value1
                :param2 value2

                """
        return self.modules_list

@dataclass
class ModuleDetails:
    module_name: str
    module_files_list: List = field(default_factory=[])

    def add_file(self, file_name):
        """
                :param1 value1
                :param1 value1
                :param2 value2

                """
        self.module_files_list.append(file_name)

    def get_files(self):
        """
                :param1 value1
                :param1 value1
                :param2 value2

                """
        return self.module_files_list

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


root_directory = os.path.dirname(__file__)
project_directory_name = root_directory.split('/')[-1]
print(f'Root Directory {root_directory}')
print(f'Project Directory Name {project_directory_name}')
get_all_modules_and_files(root_directory)
for module in module_lists:
    if not module.module_name == project_directory_name:
        for file in module.get_files():
            full_module_name = f"{module.module_name}.{file.replace('.py', '')}"
            module_ = importlib.import_module(full_module_name)
            functions_list = getmembers(module_, isfunction)
            classes = getmembers(module_, isclass)
            for func in functions_list:
                if func[1].__doc__ is None:
                    print(f'Module Name {full_module_name} Function Name {func[0]} {func[1].__code__.co_firstlineno} \n\n{getsource(func[1])}')
                else:
                    print(f'----- DOC STRING FOUND----- \nModule Name {full_module_name} Function Name {func[0]} doc string {func[1].__doc__}')
'\nimport boto3, json\n\nbed_rock_runtime = boto3.client(service_name="bedrock-runtime",\n                                region_name="us-west-2")\n\n\nprompt = "Hello"\n\nkwargs = {"modelId": "ai21.j2-ultra-v1",\n          "contentType": "application.json",\n          "accept": "*/*",\n          "body": ""}\n\nresponse = bed_rock_runtime.invoke_model(**kwargs)\n\nresponse_json = json.loads(response["body"].read())\n\ncompletion = response_json["completions"][0]["data"]["text"]\n\nprint(completion)\n\n'
'\n\ndef insert_content(file_path, content, line_number):\n    with open(file_path, \'r\') as file:\n        lines = file.readlines()\n \n    # Insert content at the specified line number\n    lines.insert(line_number - 1, content)\n    \n    with open(file_path, \'w\') as file:\n        file.writelines(lines)\n \n# Example usage:\nfile_path = \'root_module/main2.py\'\ncontent_to_insert = "print(\'line at 55\')\n"\nline_number = 55\n \ninsert_content(file_path, content_to_insert, line_number)\n\n'