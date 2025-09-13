from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.preprocessing import MultiLabelBinarizer
from pathlib import Path
from datetime import datetime
from utils.fileUtils import FilesUtils



class EvaluateNer:
    def __init__(self, configs):
        self.configs = configs

        self.evaluation_result_save_path = Path(configs["evaluation"]["evaluate_ner"])
        self.evaluation_result_save_path.parent.mkdir(exist_ok=True, parents=True)
        try:
            self.evaluation_result = FilesUtils.read_json(path=self.evaluation_result_save_path)
        except:
            self.evaluation_result = []

    
    def eval(self, ner_results_path):
        self.ner_results = FilesUtils.read_json(path=ner_results_path)
        gold_all = []
        pred_all = []

        for record in self.ner_results["results"].values():
            gold_all.append(record["gold_mesh"])
            pred_all.append(record["found_mesh"])

        # Convert to binary indicator matrix
        mlb = MultiLabelBinarizer()
        y_true = mlb.fit_transform(gold_all)
        y_pred = mlb.transform(pred_all)

        micro_p = round(precision_score(y_true, y_pred, average="micro", zero_division=0),2)
        micro_r = round(recall_score(y_true, y_pred, average="micro", zero_division=0),2)
        micro_f1 = round(f1_score(y_true, y_pred, average="micro", zero_division=0),2)

        macro_p = round(precision_score(y_true, y_pred, average="macro", zero_division=0),2)
        macro_r = round(recall_score(y_true, y_pred, average="macro", zero_division=0),2)
        macro_f1 = round(f1_score(y_true, y_pred, average="macro", zero_division=0),2)

        evalution_result = {
            "time": self.ner_results["time"],
            "config": self.ner_results["config"],
            "micro": {"precision": micro_p, "recall": micro_r, "f1": micro_f1},
            "macro": {"precision": macro_p, "recall": macro_r, "f1": macro_f1}
        }
        
        # save
        self.evaluation_result.append(evalution_result)
        FilesUtils.write_json(data=self.evaluation_result, path=self.evaluation_result_save_path)
        
        return evalution_result
    

if __name__ == "__main__":
    configs = FilesUtils.read_yaml(path="configs/configs.yaml")
    evaluator = EvaluateNer(configs=configs)

    ner_result_path = "outputs/ner/ner_test_2025-09-11_15-15-47.json"
    r = evaluator.eval(ner_results_path=ner_result_path)
    print(r)





