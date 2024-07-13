import yaml
 
# with open('Source/env.yml') as file:
#     env = yaml.load(file, Loader=yaml.FullLoader)

import os

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Load environment variables from env.yml file
with open(os.path.join(PROJECT_PATH+'/Source/env.yml')) as file:
    env = yaml.load(file, Loader=yaml.FullLoader)

print(env)