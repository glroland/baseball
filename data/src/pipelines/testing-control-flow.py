import subprocess
import kfp
import kfp.client
from kfp import dsl, components
from kfp.dsl import InputPath, Output, Artifact, Model
from kfp import compiler

@dsl.component
def step1():
    print ("STEP 1")

@dsl.component
def process_item(parameter: int):
    print (f"PROCESS ITEM WITH PARAMETER ({parameter})")

@dsl.component
def step2():
    print ("STEP 2")

    import subprocess

    print ("BEFORE")

    result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)
    print(result.stdout)

    print ("AFTER")


@dsl.component
def step3():
    print ("STEP 3")

@dsl.pipeline(name="Testing Control Flow Pipeline")
def control_flow_pipeline():


    with dsl.ParallelFor([1, 5, 10, 25]) as item:
        process_item(parameter=item)

    # Step 1
    step1_task = step1()
    step1_task.set_display_name("step1")

    # Step 2
    step2_task = step2()
    step2_task.set_display_name("step2")
    step2_task.after(step1_task)

    # Step 3
    step3_task = step3()
    step3_task.set_display_name("step3")
    step3_task.after(step2_task)


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
    control_flow_pipeline,
    experiment_name="Testing Control Flow Pipeline v1",
    arguments={
    }
)

# Compile Pipeline
print ("Compiling Pipeline")
compiler.Compiler().compile(control_flow_pipeline, 'testing-control-flow.yaml')
