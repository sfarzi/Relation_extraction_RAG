from openai import OpenAI
import os
import time


class Chatgpt:
    def __init__(self, model, instruction: str):
        print(f"model: {model}")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.instruction = instruction

    def generate(self, user_prompt, max_new_tokens:int, temperature:int):
        for attempt in range(5):
            # print(f"attempt {attempt}")
            try:
                response = self.client.responses.create(
                    model=self.model, 
                    max_output_tokens = max_new_tokens,
                    instructions=self.instruction,
                    input=user_prompt, 
                    temperature=temperature,
                    # reasoning = {
                    #     "effort":"minimal"
                    # }
                )

                return response.output_text
            except:
                wait_time = 1 * (2 ** attempt)
                time.sleep(wait_time)
        
        raise RuntimeError(f"Failed after 5 retries.")

    

if __name__ == "__main__":
    from utils.fileUtils import FilesUtils

    configs = FilesUtils.read_yaml(path="configs\\configs.yaml")

    model = configs['openai']['model']
    instruction = configs['openai']['instructions']

    model = Chatgpt(model=model, instruction=instruction)
    title = "Naloxone reverses the antihypertensive effect of clonidine."
    abstract = "In unanesthetized, spontaneously hypertensive rats the decrease in blood pressure and heart rate produced by intravenous clonidine, 5 to 20 micrograms/kg, was inhibited or reversed by nalozone, 0.2 to 2 mg/kg. The hypotensive effect of 100 mg/kg alpha-methyldopa was also partially reversed by naloxone. Naloxone alone did not affect either blood pressure or heart rate. In brain membranes from spontaneously hypertensive rats clonidine, 10(-8) to 10(-5) M, did not influence stereoselective binding of [3H]-naloxone (8 nM), and naloxone, 10(-8) to 10(-4) M, did not influence clonidine-suppressible binding of [3H]-dihydroergocryptine (1 nM). These findings indicate that in spontaneously hypertensive rats the effects of central alpha-adrenoceptor stimulation involve activation of opiate receptors. As naloxone and clonidine do not appear to interact with the same receptor site, the observed functional antagonism suggests the release of an endogenous opiate by clonidine or alpha-methyldopa and the possible role of the opiate in the central control of sympathetic tone."
    prompt = f"Title: {title}\nAbstract: {abstract}"

    res = model.generate(user_prompt=prompt)
    print(res)