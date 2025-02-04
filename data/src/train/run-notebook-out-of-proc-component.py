import subprocess
import kfp
import kfp.client
from kfp import dsl
from kfp.dsl import InputPath, Output, Artifact, Model, ClassificationMetrics
from kfp import compiler

@dsl.component(base_image="registry.home.glroland.com/paas/ai-runtime-3.11:20250130-104034",
               packages_to_install=["papermill", "GitPython", "ipykernel", "jupyter"])
def run_notebook_out_of_proc(git_url: str,
                             run_from_dir: str,
                             notebook_name: str,
                             db_conn_str: str,
                             parameters: dict,
                             jupyter_nb_output: Output[Artifact],
                             model: Output[Model]):
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

# Compile Component
print ("Compiling Component")
compiler.Compiler().compile(run_notebook_out_of_proc, 'run-notebook-out-of-proc-component.yaml')
