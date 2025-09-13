from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from utils.fileUtils import FilesUtils
from schemas.bc5cdr_output_schema import Bc5cdrOutputSchema



class CalculateMetrics:
    def __init__(self, configs:dict): 
        # all evaluation results will be saved in this directory
        self.evaluation_results_file_path = Path(configs['evaluation']['evaluation_results_file_path'])
        
        # Just to make sure parent directories exist
        self.evaluation_results_file_path.parent.mkdir(exist_ok=True, parents=True)
        
        # just to make sure [evaluation_results_file] exists
        if not self.evaluation_results_file_path.exists():
            FilesUtils.write_json(path=self.evaluation_results_file_path, data={})
            print(f"[{self.evaluation_results_file_path.name}] created at [{self.evaluation_results_file_path.parent}].")

        # map dataset to schema 
        self.dataset_schema = {
            "bc5cdr": Bc5cdrOutputSchema
        }

        

    def make_evaluation(self, extracted_relations_output: dict):
        self.dataset_name = extracted_relations_output['dataset']

        # validate extracted_relations_output
        try:
            self.dataset_schema[self.dataset_name.lower()].model_validate(extracted_relations_output)
            print(f"Schema for {self.dataset_name} Validated.")
        except Exception as e:
            raise ValueError(e)


        self.data = extracted_relations_output
        self.phase = f"Phase{extracted_relations_output['phase']}"
        self.model_creator = str(Path(extracted_relations_output['LLM']).parent)
        self.model_id = str(Path(extracted_relations_output['LLM']).name)
        self.method = extracted_relations_output['method']
        self.split = extracted_relations_output['split']
        self.temperature = extracted_relations_output['temperature']
        self.system_prompt = extracted_relations_output['system_prompt']
        self.time = extracted_relations_output['time']

        self.micro_metrics_result = self._micro_metrics(extracted_relations_output)
        self.macro_metrics_result = self._macro_metrics(extracted_relations_output)

        one_evaluation_record = {
            "model_id": self.model_id,
            "split": self.split,
            "temperature": self.temperature,
            "system_prompt": self.system_prompt,
            "time": self.time,
            "metrics": {
                "micro": self.micro_metrics_result,
                "macro": self.macro_metrics_result
            }
        }

        evaluation_results_file_content = FilesUtils.read_json(path=self.evaluation_results_file_path)

        time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        evaluation_results_file_content["update_time"] = str(time)

        phase_block = evaluation_results_file_content.setdefault(self.phase, {"method": self.method})
        dataset_block = phase_block.setdefault(self.dataset_name, {})
        model_block = dataset_block.setdefault(self.model_creator, [])
        model_block.append(one_evaluation_record)

        FilesUtils.write_json(path=self.evaluation_results_file_path, data=evaluation_results_file_content)





        


    def _micro_metrics(self, extracted_relations_output_results:dict):
        tp = 0
        fp = 0
        fn = 0
        self.results = extracted_relations_output_results['results']
        for result in tqdm(self.results, desc="Calculating micro metrics"):
            gold_set = {tuple(relation) for relation in result['gold_relations_mesh']}
            pred_set = {tuple(relation) for relation in result['pred_relations_mesh'] if None not in relation}

            for relation in result['pred_relations_mesh']:
                if None in relation:
                    fp += 1

            tp += len(gold_set & pred_set)
            fp += len(pred_set - gold_set)
            fn += len(gold_set - pred_set)

        micro_precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        micro_recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        micro_f1 =  2 * micro_precision * micro_recall / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0.0

        micro = {
            'micro_precision': round(micro_precision, 3),
            'micro_recall': round(micro_recall, 3),
            'micro_f1': round(micro_f1, 3)
        }
        return micro




    def _macro_metrics(self, extracted_relations_output_results):
        precisions, recalls, f1s = [], [], []
        self.results = extracted_relations_output_results['results']
        for result in tqdm(self.results, desc="Calculating macro metrics"):
            gold_set = {tuple(relation) for relation in result['gold_relations_mesh']}
            pred_set = {tuple(relation) for relation in result['pred_relations_mesh'] if None not in relation}


            for relation in result['pred_relations_mesh']:
                if None in relation:
                    fp += 1
                    
            tp = len(gold_set & pred_set)
            fp = len(pred_set - gold_set)
            fn = len(gold_set - pred_set)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

            precisions.append(precision)
            recalls.append(recall)
            f1s.append(f1)

        macro_precision = sum(precisions) / len(precisions)
        macro_recall = sum(recalls) / len(recalls)
        macro_f1 = sum(f1s) / len(f1s)
        macro = {
            'macro_precision': round(macro_precision, 3),
            'macro_recall': round(macro_recall, 3),
            'macro_f1': round(macro_f1, 3)
        }
        return macro
    

    


if __name__ == '__main__':
    from utils.fileUtils import FilesUtils
    configs = FilesUtils.read_yaml("configs/configs.yaml")
    # extracted_relations_file_path = 'outputs/extracted_relations/BC5CDR/phase1_test_Llama-3.2-3B-Instruct_T_2025-08-25_03-13-22.json'
    extracted_relations_file_path = 'outputs/extracted_relations/BC5CDR/phase3_test_medgemma-4b-it_T_2025-09-13_07-55-37.json'
    extracted_relations_file_content = FilesUtils.read_json(path=extracted_relations_file_path)

    calc_metric = CalculateMetrics(configs=configs)


    calc_metric.make_evaluation(extracted_relations_output=extracted_relations_file_content)


