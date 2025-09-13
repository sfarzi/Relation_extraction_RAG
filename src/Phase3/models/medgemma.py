from transformers import AutoProcessor, AutoModelForImageTextToText
import transformers
import torch


class MedGemma:
    def __init__(self, model_path, device_map):
        transformers.logging.set_verbosity_error()

        print(f'Loading [{model_path}] ...')
        self.processor = AutoProcessor.from_pretrained(model_path)
        self.model = AutoModelForImageTextToText.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map=device_map
        )


    def generate(self, user_prompt, system_prompt, max_new_tokens, temperature=None):
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": system_prompt}]
            },
            {
                    "role": "user",
                    "content": [{"type": "text", "text": user_prompt}]
            }
        ]
        inputs = self.processor.apply_chat_template(
            messages, add_generation_prompt=True, tokenize=True,
            return_dict=True, return_tensors="pt"
            ).to(self.model.device, dtype=torch.bfloat16)
        
        input_len = inputs["input_ids"].shape[-1]
        with torch.inference_mode():
            generation = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=True, temperature=temperature)
            generation = generation[0][input_len:]
        decoded = self.processor.decode(generation, skip_special_tokens=True)
        
        return decoded































# model_id = "models/google/medgemma-4b-it"

# model = AutoModelForImageTextToText.from_pretrained(
#     model_id,
#     torch_dtype=torch.bfloat16,
#     device_map="auto",
# )
# processor = AutoProcessor.from_pretrained(model_id)

# query = "give meshDescriptor code of 'Adrenaline arrhythmia'."

# messages = [
#     {
#         "role": "system",
#         "content": [{"type": "text", "text": "You are an expert in medical terms."}]
#     },
#     {
#         "role": "user",
#         "content": [
#             {"type": "text", "text": query},
#         ]
#     }
# ]

# inputs = processor.apply_chat_template(
#     messages, add_generation_prompt=True, tokenize=True,
#     return_dict=True, return_tensors="pt"
# ).to(model.device, dtype=torch.bfloat16)

# input_len = inputs["input_ids"].shape[-1]

# with torch.inference_mode():
#     generation = model.generate(**inputs, max_new_tokens=200, do_sample=False)
#     generation = generation[0][input_len:]

# decoded = processor.decode(generation, skip_special_tokens=True)
# print(decoded)

