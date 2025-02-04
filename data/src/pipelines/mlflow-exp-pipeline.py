import subprocess
import kfp
import kfp.client
from kfp import dsl, components
from kfp import compiler

run_notebook_in_proc = components.load_component_from_file('run-notebook-out-of-proc-component.yaml')

@dsl.pipeline(name="MLFlow Experiment Pipeline")
def mlflow_experiment_pipeline(git_url: str):
    # Run MLFlow Experiment
    run_task = run_notebook_in_proc(git_url=git_url,
                                    run_from_dir="data/src/train",
                                    notebook_name="mlflow_experiment.ipynb",
                                    db_conn_str="",
                                    parameters = {
                                    })
    run_task.set_display_name("mlflow-experiment")
    run_task.set_caching_options(enable_caching=False)

# Get OpenShift Token
token = subprocess.check_output("oc whoami -t", shell=True, text=True).strip()

# Connect to the pipeline server
print ("Connecting to pipeline server")
kfp_client = kfp.Client(host="https://ds-pipeline-dspa-mlflow.apps.ocp.home.glroland.com/",
                        existing_token=token,
                        verify_ssl=False)

# Create a run for the pipeline
print ("Running Pipeline")
kfp_client.create_run_from_pipeline_func(
    mlflow_experiment_pipeline,
    experiment_name="MLFlow Experiment v1",
    arguments={
        "git_url": "https://github.com/glroland/baseball.git"
    }
)

# Compile Pipeline
print ("Compiling Pipeline")
compiler.Compiler().compile(mlflow_experiment_pipeline, 'mlflow-exp-pipeline.yaml')
