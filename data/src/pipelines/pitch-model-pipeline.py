import subprocess
import kfp
import kfp.client
from kfp import dsl, components
from kfp import compiler

run_notebook_in_proc = components.load_component_from_file('run-notebook-in-proc-component.yaml')

@dsl.pipeline(name="Pitch Prediction Model Lifecycle Pipeline")
def train_model_pipeline(git_url: str, db_conn_str: str):
    # Train Model
    run_task = run_notebook_in_proc(git_url=git_url,
                                    run_from_dir="data/src/train",
                                    notebook_name="train_predict_pitch_model.ipynb",
                                    db_conn_str=db_conn_str,
                                    parameters = {
                                    })
    run_task.set_display_name("train-pitch-model")
    run_task.set_caching_options(enable_caching=False)

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
    experiment_name="Train Pitch Prediction Model Pipeline v1",
    arguments={
        "git_url": "https://github.com/glroland/baseball.git",
        "db_conn_str": "postgresql://baseball_app:baseball123@db/baseball_db"
    }
)

# Compile Pipeline
print ("Compiling Pipeline")
compiler.Compiler().compile(train_model_pipeline, 'pitch-model-pipeline.yaml')
