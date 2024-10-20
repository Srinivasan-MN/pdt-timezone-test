import os
import requests
import base64
from yaml import load, dump, BaseLoader, SafeLoader, SafeDumper, BaseDumper
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient



OWNER = "Srinivasan-MN"
REPO = "pdt-timezone-test"

class NoQuotesForEmpty(SafeDumper):
    def represent_none(self, _):
        return self.represent_scalar('tag:yaml.org,2002:null', '')

NoQuotesForEmpty.add_representer(type(None), NoQuotesForEmpty.represent_none)

def get_pat():
    try:
        key_vault_name = "devcredentialsmyharvest"
        key_vault_uri = f"https://{key_vault_name}.vault.azure.net/"
        
        client_id = os.getenv("AZURE_CLIENT_ID")
        tenant_id = os.getenv("AZURE_TENANT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")

        if not client_id or not tenant_id or not client_secret:
            raise ValueError("Missing environment variables for Azure authentication.")

        credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
        client = SecretClient(vault_url=key_vault_uri, credential=credential)
        
        secret_name = "github-pat"
        retrieved_secret = client.get_secret(secret_name)
        github_pat = retrieved_secret.value

        print(github_pat)
        return github_pat
    except Exception as e:
        print(f"Exception occurred while get_pat() : {str(e)}")

def push_to_github(path, content, sha):
    try:
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
        yaml_data['on']['schedule'][0]['cron'] = '*/15 * * * *'
        yaml_data['on']['workflow_dispatch'] = None
        
        # with open('test.yml','w') as f:
        #     dump(yaml_data, f, Dumper=SafeDumper)
        push_to_github(path, dump(yaml_data,Dumper=SafeDumper), file_sha)        
        
    except Exception as e:
        print(f"Exception occurred while edit_git_file_content: {str(e)}")

path = ".github/workflows/pdt-tz-test.yml"
edit_git_file_content(path)


    
# get_pat()

