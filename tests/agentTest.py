from dataclasses import dataclass
import os, asyncio
from alphawave.JSONResponseValidator import JSONResponseValidator
from alphawave.AlphaWave import AlphaWave
from alphawave.OpenAIClient import OpenAIClient
from jsonschema import validate, ValidationError
from promptrix.promptrixTypes import Message
from alphawave.alphawaveTypes import PromptCompletionOptions
from promptrix.Prompt import Prompt
from promptrix.UserMessage import UserMessage
from promptrix.ConversationHistory import ConversationHistory
from promptrix.SystemMessage import SystemMessage
from promptrix.VolatileMemory import VolatileMemory
from promptrix.FunctionRegistry import FunctionRegistry
from promptrix.GPT3Tokenizer import GPT3Tokenizer
from jsonschema import validate

import json

class AgentThoughts:
    def __init__(self, thoughts, command):
        self.thoughts = thoughts
        self.command = command

class Thoughts:
    def __init__(self, thought, reasoning, plan):
        self.thought = thought
        self.reasoning = reasoning
        self.plan = plan

class Command:
    def __init__(self, name, input):
        self.name = name
        self.input = input

agent_thoughts_schema = {
    "type": "object",
    "properties": {
        "thoughts": {
            "type": "object",
            "properties": {
                "thought": {"type": "string"},
                "reasoning": {"type": "string"},
                "plan": {"type": "string"}
            },
            "required": ["thought", "reasoning", "plan"]
        },
        "command": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "input": {"type": "object"}
            },
            "required": ["name", "input"]
        }
    },
    "required": ["thoughts", "command"]
}

class ThoughtValidator:
    def __init__(self, schema):
        self.schema = schema

    def validate_response(self, memory, functions, tokenizer, response, remaining_attempts):
        try:
            validate(instance=response['message'], schema=self.schema)
            return {
                'type': 'Validation',
                'valid': True,
                'value': response['message'] 
            }
            return True
        except ValidationError as e:
            print(e)
            return False

#thought_validator = ThoughtValidator(agent_thoughts_schema)
thought_validator = JSONResponseValidator(agent_thoughts_schema)

# Create a wave
client = OpenAIClient(apiKey=os.getenv("OPENAI_API_KEY"))
prompt = Prompt([
    SystemMessage('You are helpful, creative, clever, and very friendly.'),
    ConversationHistory('history', .5),
    UserMessage('{{$input}}', 100)
])

prompt_options = PromptCompletionOptions(completion_type='chat', model='gpt-3.5-turbo')
memory = VolatileMemory()
memory.set('history', [])
memory.set('input',
"""what is 3 times 5. use this format for your response:
{
    "type": "object",
    "properties": {
        "thoughts": {
            "type": "object",
            "properties": {
                "thought": {"type": "string"},
                "reasoning": {"type": "string"},
                "plan": {"type": "string"}
            },
            "required": ["thought", "reasoning", "plan"]
        },
        "command": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "input": {"type": "object"}
            },
            "required": ["name", "input"]
        }
    },
    "required": ["thoughts", "command"]
}
""")
functions = FunctionRegistry()
tokenizer = GPT3Tokenizer()
max_tokens=500
wave = AlphaWave(client=client, prompt=prompt, prompt_options=prompt_options, memory=memory, functions=functions, tokenizer=tokenizer, validator=thought_validator, history_variable='history', input_variable='input', max_repair_attempts=3, max_history_messages=20)
wave = AlphaWave(
    client=client,
    prompt=prompt,
    prompt_options=prompt_options,
    validator=thought_validator
)

async def ask():
    global wave
    response = await wave.completePrompt()
    print(response['status'])

if __name__ == '__main__':
    asyncio.run(ask())
