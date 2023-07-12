from copy import deepcopy
from .utils import process_json_str, openai_call
import tiktoken
import json
import pandas as pd


def get_bulk_name_instructions(schema, examples: list, names):
    schema_str = []
    keep_list = set()
    for k, v in deepcopy(schema.schema().get('properties')).items():
        if v.get('title') == 'name' or v.get('bulk'):
            keep_list.add(k)
            v['title'] = k
            if v.get('bulk'):
                v.pop('bulk')
            if v.get('items'):
                v.pop('items')
            schema_str.append(v)

    def get_string_form(o):
        if isinstance(o, Enum):
            return o.value
        elif isinstance(o, List) and all(isinstance(i, Enum) for i in o):
            return [i.value for i in o]
        else:
            return o

    sys_message = f"""
    You are a helpful and knowledgeable baby naming consultant.
    For each of the names below, use your common knowledge to fill out the form for each name obeying the JSON schema listed below.

    The output should be formatted as a JSON instance that conforms to the JSON schema below.

    As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}}}
    the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

    OUTPUT SCHEMA:
    {schema_str}
    """
    example_input = json.dumps([i.name for i in examples])

    example_output = []
    for example in examples:
        d = {}
        for k in ['name'] + list(keep_list):
            d[k] = get_string_form(getattr(example, k))
        example_output.append(d)
    example_output = json.dumps(example_output)

    name_list_str = json.dumps(names)

    messages = [
        {"role": "system", "content": sys_message},
        {"role": "system", "content": "Complete the task for all listed names"},
        {"role": "user", "content": example_input},
        {"role": "assistant", "content": example_output},
        {"role": "user", "content": name_list_str}
    ]

    return messages
def num_tokens_from_string(string: str, encoding_name: str = 'gpt-3.5-turbo') -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
def load_names_top_list():
    pass

def kill_tokens(kill_str= '... ...'):
    import tiktoken
    encoding = tiktoken.get_encoding("cl100k_base")
    return encoding.encode(kill_str)


def generate_rand_names(num_names: int = 100) -> list[str]:
    names = ['John', 'Mary', 'Jing', 'Abdul']
    example_str = json.dumps([[idx, name] for idx, name in enumerate(names)])
    messages = [
        {'role': 'system', 'content': """You are a helpful bot to assist in generating names 
        for children from all cultures and genders. You are to generate a list of names of length
        determined by the users inputs.  
        
        OUTPUT MUST BE JSON AND ONLY JSON.
        """},
        {'role': 'user', 'content': f"Generate JSON list of {len(names)} baby names"},
        {'role': 'system', 'content': example_str},
        {'role': 'user', 'content': f"Generate JSON list of  {num_names} baby names"}
    ]
    
    logit_bias_map = dict([(k, -100) for k in kill_tokens('... ...')])
    print('killing it', logit_bias_map)

    out = openai_call(
        model="gpt-3.5-turbo",
        max_tokens=1000,
        temperature=0.1,
        messages=messages,
        logit_bias=logit_bias_map
    )
    print(messages)
    print(out)
    name_list = process_json_str(out.choices[0].message.content)
    return [i[1] for i in name_list]

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def bulk_load_names(names):
    enc = tiktoken.encoding_for_model("cl100k_base") # for gpt 3.5 and 4
    from .models import BabyName
    from .examples import example_baby_names
    baby_name_list = []
    for name_chunk in chunker(names, 25):
        instructions = get_bulk_name_instructions(BabyName, example_baby_names, name_chunk)
        tokens = num_tokens_from_string(instructions)

        out = openai_call(
            model="gpt-3.5-turbo",
            max_tokens=4000 - tokens,
            temperature=0.1,
            messages=instructions
        )

        baby_name_data = process_json_str(out.choices[0].message.content)
        for name in baby_name_data:
            baby_name_list.append(BabyName(**name))


