import os
import kfp
from kfp import compiler, dsl
from kfp.dsl import Dataset, Input, Model, Output, Artifact
from jupyter_client import KernelManager
import nbformat

# by default, when run from inside a Kubernetes cluster:
#  - the token is read from the `KF_PIPELINES_SA_TOKEN_PATH` path
#  - the host is set to `http://ml-pipeline-ui.kubeflow.svc.cluster.local`
kfp_client = kfp.Client("https://ml-pipeline.baseball.svc.cluster.local:8888", verify_ssl=False)

# Environment Variables for configuration
#ENV_S3_URL = "S3_URL"

@dsl.component
def run_notebook() -> str:
    """ Runs the specified Jupyter notebook.

        notebook - notebook contents
    """
    # Load the notebook
    test_filename = f"./src/train/test.ipynb"
    print("TEST FILENAME")
    print(test_filename)
    test_notebook_artifact = Artifact(name="test_notebook", uri=test_filename)
    with open(test_notebook_artifact.path) as f:
        nb = nbformat.read(f, as_version=4)
    if nb is None:
        raise ValueError(f"Unable to open notebook! {notebook_path}")

    # Create a kernel manager
    km = KernelManager()
    km.start_kernel()

    # Execute each cell
    for cell in nb.cells:
        if cell.cell_type == 'code':
            # Execute the code cell
            km.execute_cell(cell.source)

    # Stop the kernel
    km.shutdown_kernel()
    return notebook_path

@dsl.component
def square(x: float) -> float:
    return x ** 2

@dsl.component
def add(x: float, y: float) -> float:
    return x + y

@dsl.component
def square_root(x: float) -> float:
    return x ** .5

@dsl.pipeline
def baseball_training_pipeline() -> float:
    run_nb_task_test = run_notebook()

    a_sq_task = square(x=1.1)
    b_sq_task = square(x=2.2)
    sum_task = add(x=a_sq_task.output, y=b_sq_task.output)
    return square_root(x=sum_task.output).output

compiler.Compiler().compile(baseball_training_pipeline, package_path='pipeline.yaml')

kfp_client.create_run_from_pipeline_func(
    baseball_training_pipeline,
    arguments={}
)
