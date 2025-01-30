import subprocess
import kfp
import kfp.client
from kfp import dsl
from kfp.dsl import InputPath, Output, Artifact
from kfp import compiler

@dsl.component
def print_env_variables():
    print ("Printing environment variables for fun:")
    import os
    for env in os.environ:
        print(f"{env}={os.environ[env]}")

@dsl.component(base_image="registry.home.glroland.com/paas/ai-runtime-3.11:20250130-104034",
               packages_to_install=["papermill", "GitPython", "ipykernel", "jupyter"])
def run_notebook(git_url: str,
                 run_from_dir: str,
                 notebook_name: str,
                 db_conn_str: str,
                 parameters: dict,
                 jupyter_nb_output: Output[Artifact],
                 model: Output[Artifact]):
    # setup output directories
    import os
    temp_path = "/tmp"
    temp_repo_path = os.path.join(temp_path, "repo")
    temp_nb_output_dir = os.path.join(temp_path, "nb_output")

    # clone git repo
    print (f"Cloning Git Repo.  URL={git_url} TempRepoPath={temp_repo_path}")
    from git import Repo
    Repo.clone_from(git_url,temp_repo_path)

    # build parameter list
    primary_parameter_list = dict(onnx_path = model.path,
                                  output_dir = temp_nb_output_dir,
                                  db_conn_str = db_conn_str,
                                  roc_path = os.path.join(temp_nb_output_dir, "roc.jpg"),
                                  dataset_size = 50,
                                  neural_network_width = 10)
    primary_parameter_list.update(parameters)
    print (f"Parameters: {primary_parameter_list}")

    # change run directory
    new_dir = os.path.join(temp_repo_path, run_from_dir)
    print (f"Changing directory to: {new_dir}")
    os.chdir(new_dir)

    # run notebook
    print (f"Running notebook.  Filename={notebook_name}")
    import papermill as pm
    pm.execute_notebook(
        notebook_name,
        jupyter_nb_output.path,
        parameters=primary_parameter_list,
        kernel_name=""
    )


@dsl.pipeline(name="Test Pipeline")
def train_model_pipeline(git_url: str, db_conn_str: str):
    test_task = print_env_variables()

    # Train Pitch Prediction Model
    run_notebook_task = run_notebook(git_url=git_url,
                                     run_from_dir="data/src/train",
                                     notebook_name="train_predict_pitch_model.ipynb",
                                     db_conn_str=db_conn_str,
                                     parameters = {
                                     })
    run_notebook_task.set_display_name("train-pitch-model")

    # Train Play Prediction Model
#    run_notebook_task = run_notebook(git_url=git_url,
#                                     run_from_dir="data/src/train",
#                                     notebook_name="train_predict_pitch_model.ipynb",
#                                     parameters = dict(db_conn_str=db_conn_str))
#    run_notebook_task.set_display_name("train-pitch-model")

# Get OpenShift Token
token = subprocess.check_output("oc whoami -t", shell=True, text=True).strip()

# Connect to the pipeline server
print ("Connecting to pipeline server")
kfp_client = kfp.Client(host="https://ds-pipeline-dspa-pipeline-sandbox.apps.ocpprod.home.glroland.com",
                        existing_token=token,
                        verify_ssl=False)

# Create a run for the pipeline
print ("Running Pipeline")
kfp_client.create_run_from_pipeline_func(
    train_model_pipeline,
    experiment_name="Testing",
    arguments={
        "git_url": "https://github.com/glroland/baseball.git",
        "db_conn_str": "postgresql://baseball_app:baseball123@db/baseball_db"
    }
)

# Compile Pipeline
print ("Compiling Pipeline")
compiler.Compiler().compile(train_model_pipeline, 'pipeline.yaml')
