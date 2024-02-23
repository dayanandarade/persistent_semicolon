import os
import ast
import time
import multiprocessing
from transformers import GPT2LMHeadModel , GPT2Tokenizer, pipeline


def generate_doc_string(prompt, model_name="gpt2"):
    """
    Generate test code using Hugging Face's Transformers library based on the provided prompt.
 
    Args:
        prompt (str): The prompt for generating test code.
        model_name (str): The Hugging Face model name (default is "gpt2").
 
    Returns:
        str: The generated test code.
    """
 
    if model_name == "gpt2":

        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        model = GPT2LMHeadModel.from_pretrained(model_name)

    else:
        
        llama_generator = pipeline("text-generation", model=model_name, tokenizer="meta-llama/Llama-2-70b-hf")
 
    if model_name == "gpt2":

        inputs = tokenizer(prompt, return_tensors="pt", max_length=100, truncation=True)
        outputs = model.generate(**inputs, max_length=100, num_return_sequences=1)
        generated_test_code = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    else:

        generated_test_code = llama_generator(prompt, max_length=100, num_return_sequences=1)[0]['generated_text'].strip()
 
    return generated_test_code


print(generate_doc_string(prompt={"what is recursion"}))


def update_file_with_doc_string(file_path):
   
    with open(file_path, 'r') as file:
        content = file.read()

    tree = ast.parse(content)

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef) and (not ast.get_docstring(node)):

            (start_lineno, end_lineno) = (node.lineno, node.end_lineno)

            method_definition = '\n'.join(content.split('\n')[start_lineno - 1:end_lineno])

            docstring = generate_doc_string(method_definition)

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


# root_directory = os.path.dirname(__file__)
# scan_directory(root_directory)














# from openai import OpenAI
# client = OpenAI()
# prompt = 'Hello'
# completion = client.chat.completions.create(model='gpt-3.5-turbo', messages=[{'role': 'user', 'content': f'Create doc string for following python function.                                 {prompt}'}])
# print(completion.choices[0].message)