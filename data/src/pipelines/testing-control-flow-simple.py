import subprocess
import kfp
import kfp.client
from kfp import dsl, components
from kfp.dsl import InputPath, Output, Artifact, Model
from kfp import compiler

@dsl.component
def step1(param: str):
    print (f"STEP 1: {param}")

@dsl.component
def step2():
    print ("STEP 2")

@dsl.component
def step3():
    print ("STEP 3")

@dsl.pipeline(name="Testing Control Flow Pipeline")
def control_flow_simple_pipeline(param: str):
    task1 = step1(param=param)
    task1.set_display_name("step1")

    task2 = step2()
    task2.set_display_name("step2")
    task2.after(step1)

    task3 = step3()
    task3.set_display_name("step3")
    task3.after(step2)


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
    control_flow_simple_pipeline,
    experiment_name="Testing Control Flow Simple Pipeline v1",
    arguments={
        "param": "test string",
    }
)

# Compile Pipeline
print ("Compiling Pipeline")
compiler.Compiler().compile(control_flow_simple_pipeline, 'testing-control-flow-simple.yaml')
