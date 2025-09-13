import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM

class Llama:
    def __init__(self, model_path, device_map, system_prompt):
        transformers.logging.set_verbosity_error()
        self.system_prompt = system_prompt

        print(f'Loading [{model_path}] ...')
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map=device_map
        )


    def generate(self, user_prompt, max_new_tokens, temperature):
        messages = [
        {"role": "system", "content": self.system_prompt},
        {"role": "user", "content": user_prompt}
        ]
        # print(f'\nmessages= {messages}\n')
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature
        )
        return self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    
if __name__ == '__main__':
    from utils.fileUtils import FilesUtils

    config_path = 'configs/configs.yaml'
    configs = FilesUtils.read_yaml(config_path)

    model = Llama(
        model_path='models/meta-llama/Llama-3.2-3B-Instruct',
        device_map = 'auto',
        system_prompt = configs['prompts']['Phase1']['bc5cdr']['system']['v4']
    )

    model.generate(
        user_prompt='This is A, This is B',
        max_new_tokens=512,
        temperature=0.7
    )