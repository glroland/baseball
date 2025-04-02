import subprocess
import kfp
import kfp.client
from kfp import dsl, components
from kfp.dsl import InputPath, Output, Artifact, Model
from kfp import compiler

simple_pipeline = components.load_component_from_file('testing-control-flow-simple.yaml')

@dsl.pipeline(name="Testing Control Flow Pipeline")
def control_flow_pipeline():

    import os
    files = os.listdir("/Users/lroland/Projects/github.com/sbc-chatbot/samples")

    with dsl.ParallelFor(files) as item:
        simple_pipeline(param=item)



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
