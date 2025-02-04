import subprocess
import kfp
import kfp.client
from kfp import dsl, components
from kfp.dsl import InputPath, Output, Artifact, Model
from kfp import compiler

pitch_model_pipeline = components.load_component_from_file('pitch-model-pipeline.yaml')

play_model_pipeline = components.load_component_from_file('play-model-pipeline.yaml')

@dsl.component
def print_env_variables():
    print ("Printing environment variables for fun:")
    import os
    for env in os.environ:
        print(f"{env}={os.environ[env]}")

@dsl.component
def store_assets():
    pass

@dsl.component
def register_models():
    pass

@dsl.pipeline(name="Model Lifecycle Pipeline")
def train_model_pipeline(git_url: str, db_conn_str: str):
    diag_task = print_env_variables()

    # Train Pitch Prediction Model
    pitch_model_pipeline(git_url=git_url, db_conn_str=db_conn_str)

    # Train Play Prediction Model
    play_model_pipeline(git_url=git_url, db_conn_str=db_conn_str)

    # Store Assets
    store_assets_task = store_assets()
    store_assets_task.set_display_name("store-assets")
    store_assets_task.after(pitch_model_pipeline)
    store_assets_task.after(play_model_pipeline)

    # Register Models
    register_models_task = register_models()
    register_models_task.set_display_name("register-models")
    register_models_task.after(store_assets_task)


# Get OpenShift Token
token = subprocess.check_output("oc whoami -t", shell=True, text=True).strip()

# Connect to the pipeline server
print ("Connecting to pipeline server")
kfp_client = kfp.Client(host="https://ds-pipeline-dspa-baseball.apps.ocp.home.glroland.com/",
                        existing_token=token,
                        verify_ssl=False)

# Create a run for the pipeline
print ("Running Pipeline")
kfp_client.create_run_from_pipeline_func(
    train_model_pipeline,
    experiment_name="Baseball Model Pipeline v1",
    arguments={
        "git_url": "https://github.com/glroland/baseball.git",
        "db_conn_str": "postgresql://baseball_app:baseball123@db/baseball_db"
    }
)

# Compile Pipeline
print ("Compiling Pipeline")
compiler.Compiler().compile(train_model_pipeline, 'train-and-deploy-models-pipeline.yaml')
