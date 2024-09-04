# Built-in imports
import os

# External imports
import aws_cdk

# Own imports
from cdk_backend.helpers.add_tags import add_tags_to_app
from cdk_backend.backend_stack import NetworkingStack


print("--> Deployment AWS configuration (safety first):")
print("CDK_DEFAULT_ACCOUNT", os.environ.get("CDK_DEFAULT_ACCOUNT"))
print("CDK_DEFAULT_REGION", os.environ.get("CDK_DEFAULT_REGION"))


app: aws_cdk.App = aws_cdk.App()


# Configurations for the deployment (obtained from env vars and CDK context)
DEPLOYMENT_ENVIRONMENT = os.environ[
    "DEPLOYMENT_ENVIRONMENT"
]  # Intentionally not using get() to raise an exception if not set
MAIN_RESOURCES_NAME = app.node.try_get_context("main_resources_name")
# TODO: enhance app_config to be a data class (improve keys/typings)
APP_CONFIG = app.node.try_get_context("app_config")[DEPLOYMENT_ENVIRONMENT]


stack: NetworkingStack = NetworkingStack(
    app,
    f"{MAIN_RESOURCES_NAME}-{DEPLOYMENT_ENVIRONMENT}",
    MAIN_RESOURCES_NAME,
    APP_CONFIG,
    env={
        "account": os.environ.get("CDK_DEFAULT_ACCOUNT"),
        "region": os.environ.get("CDK_DEFAULT_REGION"),
    },
    description=f"Stack for {MAIN_RESOURCES_NAME} infrastructure in {DEPLOYMENT_ENVIRONMENT} environment",
)

add_tags_to_app(
    app,
    MAIN_RESOURCES_NAME,
    DEPLOYMENT_ENVIRONMENT,
)

app.synth()
