""" Client utilities for connecting to the model server """
import sys
import logging
import requests
from urllib.parse import quote_plus
#from utils.data import get_env_value
from data import get_env_value, fail

logger = logging.getLogger(__name__)

ENV_MODEL_REGISTRY_URL = "MODEL_REGISTRY_URL"
ENV_MODEL_REGISTRY_TOKEN = "MODEL_REGISTRY_TOKEN"
ENV_MODEL_REGISTRY_AUTHOR = "MODEL_REGISTRY_AUTHOR"

BASE_MODEL_REGISTRY_API = "/api/model_registry/v1alpha3/"

def invoke_model_registry_api(api, query_params = {}, data = {}):
    """ Connect to the configured model registry. """
    url = get_env_value(ENV_MODEL_REGISTRY_URL)
    token = get_env_value(ENV_MODEL_REGISTRY_TOKEN)
    author = get_env_value(ENV_MODEL_REGISTRY_AUTHOR)

    endpoint = url + BASE_MODEL_REGISTRY_API + api
    if len(query_params) > 0:
        endpoint += "?"
        for key, value in query_params.items():
            endpoint += key + "=" + quote_plus(value)
    logger.debug("Invoking Model Registry API.  Endpoint=%s Token=%s Author=%s",
                 endpoint, token, author)

    headers = { "Authorization": f"Bearer {token}" }

    response = requests.get(url=endpoint,
                            headers=headers,
                            data=data)
    if response.status_code != 200:
        fail(f"invoke_model_registry_api() failed! API={api} Code={response.status_code}")

    return response.json()

def get_all_models():
    """ Gets all models configured within the registry """
    results = invoke_model_registry_api("registered_models")
    return results["items"]

def get_all_model_versions():
    """ Gets all model versions configured within the registry """
    results = invoke_model_registry_api("model_versions")
    return results["items"]

# FIXME - doesn't work
def get_all_artifacts():
    """ Gets all model artifacts configured within the registry """
    results = invoke_model_registry_api("artifacts")
    return results

def get_all_model_artifacts():
    """ Gets all model artifacts configured within the registry """
    results = invoke_model_registry_api("model_artifacts")
    return results["items"]

def get_all_inference_services():
    """ Gets all inference services stored in the registry  """
    results = invoke_model_registry_api("inference_services")
    return results["items"]

def get_all_serving_environments():
    """ Gets all serving environments deployed in the platform """
    results = invoke_model_registry_api("serving_environments")
    return results["items"]

def get_model(name):
    """ Gets the model with the specified name.
    
        name - model name
    """
    query_params = \
    {
        "name": name
    }
    results = invoke_model_registry_api("registered_model", query_params=query_params)
    return results

def get_model_versions(model_id):
    """ Gets all versions for the specified model.
    
        model_id - model id
    """
    results = invoke_model_registry_api("registered_models/" + model_id + "/versions")
    return results["items"]

def get_model_version_artifacts(version_id):
    """ Gets all artifacts for the specified model version.
    
        version_id - version id
    """
    results = invoke_model_registry_api("model_versions/" + version_id + "/artifacts")
    return results["items"]


def main():
    # Default to not set
    logging.getLogger().setLevel(logging.NOTSET)

    # Log info and higher to the console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)

    print ("Starting")

    set = get_all_models()
    print ("SET:")
    print(set)
    print ()
    for item in set:
        print ("ITEM:")
        print (item)
        print()

        childset = get_model_versions(item["id"])
        print ("CHILD SET:")
        print(childset)
        print ()

        for childitem in childset:
            print ("CHILD ITEM:")
            print (childitem)
            print()


            grandchildset = get_model_version_artifacts(childitem["id"])
            print ("GRAND CHILD SET:")
            print(grandchildset)
            print ()

            for grandchilditem in grandchildset:
                print ("GRAND CHILD ITEM:")
                print (grandchilditem)
                print()


    

if __name__ == "__main__":
    main()
