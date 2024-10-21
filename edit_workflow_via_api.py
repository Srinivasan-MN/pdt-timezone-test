import os
import datetime
import requests
import base64
from yaml import load, dump, BaseLoader, SafeLoader, SafeDumper, BaseDumper
# from azure.identity import DefaultAzureCredential, ClientSecretCredential
# from azure.keyvault.secrets import SecretClient


OWNER = "Srinivasan-MN"
REPO = "pdt-timezone-test"

def change_cron_time(cron_time, time_zone):
    try:
        cron_time_str = ""
        cron_time = (cron_time.strip()).split(" ")
        
        if time_zone == "PDT":
            cron_time[1] = str(int(cron_time[1])-1)
        if time_zone == "PST":
            cron_time[1] = str(int(cron_time[1])+1)
        cron_time[1] = str(int(cron_time[1])+1)
        for i in cron_time:
            cron_time_str += i+" "

        print(cron_time_str)
        return cron_time_str.strip()

        
    except Exception as e:
        print(f"Exception occurred while change_cron_time() : {str(e)}")

def get_pat():
    try:
        # key_vault_name = "devcredentialsmyharvest"
        # key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"
        
        # client_id = os.getenv("AZURE_CLIENT_ID")
        # tenant_id = os.getenv("AZURE_TENANT_ID")
        # client_secret = os.getenv("AZURE_CLIENT_SECRET")

        # if not client_id or not tenant_id or not client_secret:
        #     raise ValueError("Missing environment variables for Azure authentication.")

        # credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
        # client = SecretClient(vault_url=key_vault_uri, credential=credential)
        
        # secret_name = "github-pat"
        # retrieved_secret = client.get_secret(secret_name)
        # github_pat = retrieved_secret.value
        github_pat = os.getenv("GITHUB_PAT")
        print(f"Github pat: {github_pat}")
        return github_pat
    except Exception as e:
        print(f"Exception occurred while get_pat() : {str(e)}")

def push_to_github(path, content, sha):
    try:
        print("Entered into push_to_github()")
        commit_message = "Updated the file"
        content = base64.b64encode(content.encode(encoding="UTF-8")).decode(encoding="UTF-8")
        personal_access_token = get_pat()

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
        print("Entered into get_git_file_details()")
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
        print("Entered into edit_git_file_content()")
        date_now = datetime.datetime.now()  
        time_zone = ""      
        file_details = get_git_file_details(path)
        file_sha = file_details['sha']
        # file_content_bytes = file_details['content'].encode(encoding="UTF-8")
        # decoded_content = base64.b64decode(file_content_bytes).decode(encoding="UTF-8")
        decoded_content = base64.b64decode(file_details['content'])
        print(decoded_content)
        yaml_data = load(decoded_content, Loader=BaseLoader)

        timeout_minutes = yaml_data['jobs']['run-updater']['timeout-minutes']
        yaml_data['jobs']['run-updater']['timeout-minutes'] = int(timeout_minutes)
        cron_time = yaml_data['on']['schedule'][0]['cron']
        if date_now.month == 3:
            time_zone = "PDT"
        elif date_now.month == 11:
            time_zone = "PST"
        yaml_data['on']['schedule'][0]['cron'] = change_cron_time(cron_time, time_zone)
        yaml_data['on']['workflow_dispatch'] = None
        
        # with open('test.yml','w') as f:
        #     dump(yaml_data, f, Dumper=SafeDumper)
        push_to_github(path, dump(yaml_data,Dumper=SafeDumper), file_sha)        
        
    except Exception as e:
        print(f"Exception occurred while edit_git_file_content: {str(e)}")

path = ".github/workflows/pdt-tz-test.yml"
edit_git_file_content(path)

# cron_time_str = ""
# cron_time = " 15 4 * * *   "
# cron_time = (cron_time.strip()).split(" ")
# cron_time[1] = str(int(cron_time[1])+1)
# print(cron_time)
# for i in cron_time:
#     cron_time_str += i+" "
# print(cron_time_str)

# date_now = datetime.datetime.now()
# print(type(date_now.month))

# get_pat()

