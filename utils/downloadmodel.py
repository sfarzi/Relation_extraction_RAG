from huggingface_hub import login, hf_hub_download, list_repo_files
from pathlib import Path
import os

class huggingface:
    def __init__(self):
        self.access_token = input("Enter access Token (it can be 'None'): ")

        if self.access_token == "None" : 
            self.access_token = None

        if self.access_token:
            login(token=self.access_token)
            print('logined to huggingface!\n')
        
    
    def _list_files(self, repo_id:str):
        files = list_repo_files(repo_id=repo_id)
        
        i = 0
        files_dict = {}
        for file in files:
            files_dict[i] = file
            i += 1
        return files_dict
    

    def _download(self, repo_id:str, file_name:str, local_dir:str=None):
        hf_hub_download(repo_id=repo_id, filename=file_name, local_dir=local_dir)
    

    def run(self, repo_id:str, local_dir:str=None):
        local_dir = Path(local_dir)
        
        repo_files = self._list_files(repo_id=repo_id)     
        emoji = {
            'downloaded':'✅' ,
            'not downloaded': '❌'
        }
        
        while True:
            for k,v in repo_files.items():
                local_dir_files = [f.name for f in local_dir.iterdir() if f.is_file()]
                repo_files_status = {
                    file:('downloaded' if file in local_dir_files else 'not downloaded') for file in repo_files.values()
                }

                file_status_emoji = emoji[repo_files_status[v]]
                print(f"{file_status_emoji}  {k}. {v}")
            
            item_to_download = int(input("Enter file number: "))
            selected_file = repo_files[item_to_download]
            try:
                self._download(
                    repo_id=repo_id, 
                    file_name=selected_file,
                    local_dir=local_dir)
            except:
                print(f"download failed!")
                    
            if selected_file in [f for f in local_dir.iterdir() if f.is_file()]:
                print(f"{selected_file} have been downloaded.")




    


if __name__ == "__main__":
    repo_id = 'cambridgeltl/SapBERT-from-PubMedBERT-fulltext'
    local_dir = Path('/home/ubuntu/NLP/Mahdi_Experiments/RE/models/' + repo_id)
    local_dir.mkdir(exist_ok=True, parents=True)



    hf = huggingface()
    hf.run(
        repo_id=repo_id,
        local_dir=local_dir
           )