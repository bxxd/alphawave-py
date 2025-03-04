from peft import PeftModel    
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
import accelerate
import torch
from accelerate import load_checkpoint_and_dispatch
import datetime
import os
import traceback
from alphawave_pyexts import serverUtils as sv

# Load the model.
model_name = "mosaicml/mpt-30b-instruct"
print('devices', torch.cuda.device_count(), torch.cuda.current_device())
print(f"Loading {model_name}")

tokenizer = AutoTokenizer.from_pretrained(model_name, skip_special_tokens=True)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    load_in_8bit=True,
    trust_remote_code=True
)
model.tie_weights()
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    trust_remote_code=True,
    device_map="auto",
)

print(f"server started {model_name} into memory, use mpt_instruct")
if __name__ == '__main__':
    sv.server(pipeline=pipeline, tokenizer=tokenizer, stop_str=['<|endoftext|>', '<|im_end|>', '###', '#if'])
