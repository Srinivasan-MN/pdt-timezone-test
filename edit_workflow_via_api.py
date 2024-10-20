import requests
import base64
from yaml import load, dump, BaseLoader, SafeLoader, SafeDumper


OWNER = "Srinivasan-MN"
REPO = "pdt-timezone-test"

def push_to_github(path, content, sha):
    try:
        commit_message = "Updated the file"
        content = base64.b64encode(content.encode(encoding="UTF-8")).decode(encoding="UTF-8")
        

        url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"

        header = {
            "Authorization": f"Bearer {personal_access_token}",
            "Accept": "application/vnd.github.v3+json",
            
        }

        data = {
            "message" : commit_message,
            "sha" : sha,
            "content" : content
        }

        response = requests.put(url=url,headers=header,json=data)
        print(response.json())
        
    except Exception as e:
        print(f"Exception occurred while push_to_github: {str(e)}")

def get_git_file_details(path):
    try:
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
        response = requests.get(url)
        # file_content_bytes = response.json()['content'].encode(encoding="UTF-8")
        # decoded_content = base64.b64decode(file_content_bytes).decode(encoding="UTF-8")
        # print(decoded_content)
        return response.json()

    except Exception as e:
        print(f"Exception occurred while getting sha: {str(e)}")

def edit_git_file_content(path):
    try:
        file_details = get_git_file_details(path)
        file_sha = file_details['sha']
        # file_content_bytes = file_details['content'].encode(encoding="UTF-8")
        # decoded_content = base64.b64decode(file_content_bytes).decode(encoding="UTF-8")
        decoded_content = base64.b64decode(file_details['content'])
        print(decoded_content)
        yaml_data = load(decoded_content, Loader=BaseLoader)

        timeout_minutes = yaml_data['jobs']['run-updater']['timeout-minutes']
        yaml_data['jobs']['run-updater']['timeout-minutes'] = int(timeout_minutes)
        yaml_data['on']['schedule'][0]['cron'] = '*/10 * * * *'
        
        with open('test.yml','w') as f:
            dump(yaml_data, f, default_flow_style=False)
        # push_to_github(path, dump(yaml_data), file_sha)        
        
    except Exception as e:
        print(f"Exception occurred while edit_git_file_content: {str(e)}")

path = ".github/workflows/pdt-tz-test.yml"
edit_git_file_content(path)

