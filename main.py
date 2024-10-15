import yaml

print("PDT time zone test...")
class CustomLoader(yaml.SafeLoader):
    pass
def construct_yaml_str(self, node):
    return self.construct_scalar(node)

CustomLoader.add_constructor('tag:yaml.org,2002:bool', construct_yaml_str)

class CustomDumper(yaml.SafeDumper):
    pass

def str_presenter(dumper, data):
    # If the string data is 'on', return it unquoted
    if data in ['on', 'yes', 'no', 'true', 'false']:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

CustomDumper.add_representer(str, str_presenter)


def convert_pdt_to_pst():
    with open('.github/workflows/pdt-tz-test.yml', 'r') as file:
        # yamlData = yaml.safe_load(file)
        # yamlData = yaml.load(stream=file, Loader=yaml.BaseLoader)
        yamlData = yaml.load(file, Loader=CustomLoader)
    
    print(yamlData)
        
    with open('.github/workflows/pdt-tz-test1.yml', 'w') as file:
        yaml.dump(yamlData, file,Dumper=CustomDumper,default_flow_style=False)
    
# convert_pdt_to_pst()    
