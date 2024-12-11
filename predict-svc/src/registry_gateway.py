""" Client utilities for connecting to the model server """
import sys
import logging
from urllib.parse import quote_plus
import urllib3
import requests
from kubernetes import client, config
from utils import fail
from config import get_config_str, ConfigSections, ConfigKeys

logger = logging.getLogger(__name__)

BASE_MODEL_REGISTRY_API = "/api/model_registry/v1alpha3/"

REG_API_TIMEOUT = 30 # seconds

def invoke_model_registry_api(api, query_params = None, data = None):
    """ Connect to the configured model registry. 
    
        api - model registry api to invoke
        query_params - optional query string parameters
        data - optional post parameters
    """
    # get config values
    url = get_config_str(ConfigSections.REGISTRY, ConfigKeys.URL)
    token = get_config_str(ConfigSections.REGISTRY, ConfigKeys.TOKEN)
    author = get_config_str(ConfigSections.REGISTRY, ConfigKeys.NAME)

    # validate config
    if url is None or len(url) == 0 or token is None or len(token) == 0 or \
        author is None or len(author) == 0:
        fail("Registry config not set.  URL, Token, and Author must all be set.")

    # trim config values
    url = url.strip()
    token = token.strip()
    author = author.strip()

    # set parameter defaults in a more safe way according to pylint
    if query_params is None:
        query_params = {}
    if data is None:
        data = {}

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
                            data=data,
                            timeout=REG_API_TIMEOUT)
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
    # validate parameters
    if name is None or len(name) == 0:
        fail("get_model() - No model name provided.")

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
    if model_id is None or len(model_id) == 0:
        fail("get_model_versions() - ID for Model with name is empty!")
    results = invoke_model_registry_api("registered_models/" + model_id + "/versions")
    return results["items"]

def get_model_version_artifacts(version_id):
    """ Gets all artifacts for the specified model version.
    
        version_id - version id
    """
    results = invoke_model_registry_api("model_versions/" + version_id + "/artifacts")
    return results["items"]

def get_inference_services(namespace, model_id, model_version_id, inference_label_selector=None):
    """ Gets the inference URL for the specified model.

        model_id - model id
        model_version_id - model version id
        inference_label_selector - additional inference label selectors
    """
    # setup kubernetes connection
    config_file = get_config_str(ConfigSections.REGISTRY, ConfigKeys.KUBECONFIG)
    if config_file is None or len(config_file) == 0:
        logger.warning("KubeConfig is required for registry queries and has not been set.  Using local")
        config_file = None
    config.load_kube_config(config_file=config_file)

    # build label selector string
    label_selector = f"modelregistry.opendatahub.io/model-version-id = {model_version_id}, " + \
                     f"modelregistry.opendatahub.io/registered-model-id = {model_id}"
    if inference_label_selector is not None:
        label_selector += ", " + inference_label_selector

    # query kubernetes api
    v1 = client.CustomObjectsApi()
    results = v1.list_namespaced_custom_object(group="serving.kserve.io",
                                               version="v1beta1",
                                               namespace=namespace,
                                               plural="inferenceservices",
                                               label_selector=label_selector,
                                               watch=False,
                                               pretty="true")

    return results["items"]

def do_labels_match(ref_labels, obj_labels):
    """ Analyzes label inputs to determine if there is a match in obj.
    
        ref_labels - master reference values
        obj_labels - object labels
    """
    # null or no reference labels is assumed to be a match
    if ref_labels is None or len(ref_labels) == 0:
        logger.debug("No reference labels provided.  Assuming match.")
        return True

    # null or no object labels is assumed to be a mismatch
    if obj_labels is None or len(obj_labels) == 0:
        logger.debug("No object labels provided.  Assumed a mismatch since ref labels exist.")
        return False

    # Create a list of label keys that must be matched to be considered matching overall
    keys = []
    if ref_labels is not None:
        keys = list(ref_labels.keys())

    # search labels
    for custom_property in obj_labels:
        pname = custom_property
        pvalue = obj_labels[custom_property]["string_value"]

        # remove from list if found
        if pname in ref_labels:
            expected_value = ref_labels[pname]
            if expected_value == pvalue:
                keys.remove(pname)

    # determine if match
    match = len(keys) == 0
    logger.debug("Was match?  %s", match)
    return match

def get_model_inference_endpoint(namespace, model_name, version_name=None, version_dict=None,
                                 inference_label_selector=None):
    """ Gets the inference endpoint for the specified model matching the provided selectors.
    
        namespace - namespace
        model_name - name of model
        version_name - (optional) version number
        version_dict - dictionary of strings containing property, value values for the label
        inference_label_selector - k8s selector string for the inference service
    """
    logger.info("get_model_inference_endpoint() NS=%s Model=%s Version=%s VLs=%s, ILs=%s",
                namespace, model_name, version_name, version_dict, inference_label_selector)

    # get model id - validations occuring in get_model
    model = get_model(model_name)
    if model is None:
        fail(f"get_model_inference_endpoint() - Could not find model matching name. {model_name}")
    model_id = model["id"]

    # get model_version - validations in get_model_versions
    model_versions = get_model_versions(model_id)
    if model_versions is None or len(model_versions) == 0:
        fail("get_model_inference_endpoint() No matching model versions available for the " + \
             f"specified model. {model_id}")

    # find matching version
    matching_model_version = None
    for model_version in model_versions:
        # match version name
        if model_version["state"] != "ARCHIVED" and \
                    do_labels_match(version_dict, model_version["customProperties"]):
            logger.debug("Labels Matched...  MN=%s", model_name)

            # if version name is provided, it must also match
            if version_name is not None and len(version_name) > 0:
                logger.debug("Name provided - must also match.  In=%s Out=%s",
                             version_name, model_version["name"])
                if version_name == model_version["name"]:
                    logger.debug("Version Name provided and matches.")
                    if matching_model_version is None:
                        logger.info("Matching Model Version.  MV=%s", model_version)
                        matching_model_version = model_version
                    else:
                        fail("get_model_inference_endpoint() - multiple matching model " + \
                             f"versions! {model_id}")
            else:
                logger.debug("No name provided and we have a match.")
                if matching_model_version is None:
                    logger.debug("Matching Model Version.  MV=%s", model_version)
                    matching_model_version = model_version
                else:
                    fail("get_model_inference_endpoint() - multiple matching model versions! " + \
                         f"{model_id}")

    # ensure that a matching version was found
    if matching_model_version is None:
        fail(f"get_model_inference_endpoint() - no matching model version found!  M={model_id}")
    model_version_id = matching_model_version["id"]
    logger.debug("Matching Model Version # %s", model_version_id)

    # get inference services
    inference_services = get_inference_services(namespace,
                                                model_id,
                                                model_version_id,
                                                inference_label_selector)
    urls = []
    for svc in inference_services:
        url = svc["status"]["address"]["url"]
        urls.append(url)

    # validate list
    if len(urls) == 0:
        logger.debug("No match - empty urls list")
        return None
    if len(urls) > 1:
        fail("get_model_inference_endpoint - Multiple urls available for model/version! " + \
             f"M={model_id} MV={model_version_id}")

    logger.info("Matching Inference URL:  %s", urls[0])
    return urls[0], inference_services[0]["metadata"]["name"]


def main():
    """ Main Method for Testing Purposes """
    # Default to not set
    logging.getLogger().setLevel(logging.NOTSET)

    # Log info and higher to the console
    console = logging.StreamHandler(sys.stdout)
#    console.setLevel(logging.DEBUG)
    console.setLevel(logging.INFO)
    logging.getLogger().addHandler(console)

    # disable urllib warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print ("Starting")

    results = get_model_inference_endpoint(namespace="fraud-detection",
                                           model_name="Fraud Detection",
                                           version_name="1")
    print ("Test #1 Results - " + str(results))

    version_labels = { "baseball_release": "production" }
    results = get_model_inference_endpoint(namespace="fraud-detection",
                                           model_name="Fraud Detection",
                                           version_dict=version_labels)
    print ("Test #2 Results - " + str(results))


if __name__ == "__main__":
    main()
