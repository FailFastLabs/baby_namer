from langchain.output_parsers import PydanticOutputParser
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.chat_models import ChatOpenAI
from .models import FamousPerson, BabyName
from .examples import EXAMPLE_BABY_NAMES
import json
import wikipediaapi
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import RetryWithErrorOutputParser
from enum import Enum
from typing import List
from copy import deepcopy
from .utils import USER_AGENT
import requests
from bs4 import BeautifulSoup

chat = ChatOpenAI(temperature=0, model='gpt-3.5-turbo')


def get_famous_people(name):
    # Set up a parser + inject instructions into the prompt template.
    parser = PydanticOutputParser(pydantic_object=FamousPerson)
    output_format = parser.get_format_instructions()
    example = """[{
    "name": "George Orwell",
    "first_name": "George",
    "description": "George Orwell was an English novelist, essayist, journalist, and critic. His work is characterized by lucid prose, biting social criticism, opposition to totalitarianism, and outspoken support of democratic socialism.",
    "wikipedia_link": "https://en.wikipedia.org/wiki/George_Orwell"
    },
    {
    "name": "George R.R. Martin",
    "first_name": "George",    
    "description": "George R.R. Martin is an American novelist and screenwriter. He is best known for his series of epic fantasy novels, A Song of Ice and Fire, which was adapted into the HBO series Game of Thrones.",
    "wikipedia_link": "https://en.wikipedia.org/wiki/}
    ]
    """
    output_format = """
    JSON
    {'name': 'Persons Name',
    "first_name": "First Name Only",
    'description': '1 Sentence brief description',
    'wikipedia_link': 'URL for English Wikipedia for the person.'
    }

    Reply in JSON format. All output text should be in JSON.
    """
    messages = [
        SystemMessage(content=f"""You are a helpful assistant that helps research baby names.
                      Output Format: \n {output_format}"""),
        HumanMessage(content=f"Give the top 2 most famous people with first name George"),
        AIMessage(content=example),
        HumanMessage(content=f"Give the top 10 most famous people with first name {name}")
    ]

    out = chat(messages)
    try:
        l = []
        for person in json.loads(out.content):
            try:
                fp = FamousPerson(**person)
            except ValueError as e:
                # print(e)
                pass
            l.append(fp)
    except:
        return out
    return l


def extract_content(url, content_class):
    # Send a GET request to the URL
    try:
        response = requests.get(url,timeout=5)
    except requests.exceptions.Timeout:
        # In case of a timeout, return an empty string
        return ""
    # Parse the HTML content of the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all elements with class "t-copy"
    elements = soup.find_all(class_=content_class)

    # Extract and return the text content of these elements
    return '\n'.join([element.text for element in elements])

def get_gt_data(name):
    content = []
    for url, c in [['https://nameberry.com/babyname/{name}','t-copy'],
                       ['https://www.thebump.com/b/{name}-baby-name','contentBody']]:
        url = url.format(name=name)
        content.append(extract_content(url,c)[0:500])
    wiki_wiki = wikipediaapi.Wikipedia(USER_AGENT, 'en')
    page_py = wiki_wiki.page(f'{name} (name)') # TODO include other forms of this

    content.append(page_py.text.split('\n\n')[0])
    return '\n'.join([c[0:500] for c in content])

def get_name_description(name):
    content = get_gt_data(name)

    def clean_text(text):
        import string
        printable = set(string.printable)
        return''.join(filter(lambda x: x in printable, content))

    messages = [
        SystemMessage(content=f"""You are a helpful assistant that summarizes and enriches Wikipedia content for helping choose baby names. Take the wikiepdia description for this name {name}
        and enrich it to give a good description for parents who may want to name their child.
        
        Include origins, meaning, popular culture examples, attributes embodied by the name.
                      """),
        HumanMessage(content=f"Give a helpful summary for parents of the name `Matthew`"),
        AIMessage(content="""
        Matthew is one of the many classic boy names that have stood the test of time. The name has been around for centuries, originating from the Hebrew word "Mattityahu," which means "gift of God."

    Matthew goes all the way back to Biblical times in the first century. According to the New Testament of the Bible, Matthew, also known as Matthew the Apostle and Saint Matthew, was one of Jesus' twelve chosen apostles. Many believe Matthew was the nickname given to the apostle by Jesus himself (Matthew was also known as Levi).

    Matthew is traditionally a masculine name.

    Though still widespread, Matthew isn't as popular as it once was in the United States. According to data from the Social Security Administration, Matthew peaked in 1995 and 1996, when it was the second-most-popular name for boys in the United States. More recently, it's fallen to spot 30 for boys on the SSA list.

    Among parents, Matthew is in the top 50 baby boy names. 

    A true classic, Matthew has endured as a baby name since the Christian apostle and saint walked the earth. With a beautiful meaning and easy nicknames, it's a safe but solid choice for modern parents, too.
    """),
        SystemMessage(content=f"""From Wikipedia {clean_text(content)}"""),
        HumanMessage(content=f"Give a helpful summary for parents of the name `{name}`")
    ]
    out = chat(messages)
    return out.content


def get_string_form(o):
    if isinstance(o, Enum):
        return o.value
    elif isinstance(o, List) and all(isinstance(i, Enum) for i in o):
        return [i.value for i in o]
    else:
        return o


def get_instructions_bulk(schema, examples, name_list_str):
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
    messages = [
        {"role": "system", "content": sys_message},
        {"role": "system", "content": "Complete the task for all listed names"},
        {"role": "user", "content": example_input},
        {"role": "assistant", "content": example_output},
        {"role": "user", "content": name_list_str}
    ]

    return messages


def get_basic_details(name):
    description = get_name_description(name)

    query = f"Generate the requested meta-data associated with the baby name"

    parser = PydanticOutputParser(pydantic_object=BabyName)

    prompt = PromptTemplate(
        template="""Fill out the required information for the desired baby name.
         Use common knowledge to fill out as many fields as possible.
         {format_instructions}
         {query}
         Examples""",
        input_variables=["query"],
        partial_variables={
            "format_instructions": parser.get_format_instructions(),
        },
    )

    _input = prompt.format_prompt(query=query)
    example_messages = []
    keys = (BabyName.schema().get('properties')).items()
    for baby_name in EXAMPLE_BABY_NAMES:
        json_data = {}
        for k in keys:
            k = k[0]
            val = get_string_form(getattr(baby_name, k))
            if val is not None:
                json_data[k] = val
        json_data = json.dumps(json_data)

        example_messages.append(HumanMessage(content=baby_name.name))
        example_messages.append(SystemMessage(content=json_data))

    messages = [SystemMessage(content=_input.to_string())]
    messages += example_messages
    messages += [HumanMessage(content=name)]

    out = chat(messages)

    out_json = json.loads(out.content)
    out_json['description'] = description

    parser = PydanticOutputParser(pydantic_object=BabyName)
    retry_parser = RetryWithErrorOutputParser.from_llm(
        parser=parser, llm=ChatOpenAI()
    )
    return retry_parser.parse_with_prompt(json.dumps(out_json), _input)
