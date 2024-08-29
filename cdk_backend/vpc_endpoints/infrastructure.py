# External imports
from aws_cdk import aws_ec2
from constructs import Construct

# Own imports
from cdk_backend.vpc.infrastructure import VPC


class VPCEndpoints(Construct):
    """
    Class to create the VPC Endpoints for a given VPC.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc_construct: VPC,
    ) -> None:
        """
        :param scope (Construct): Parent of this stack, usually an 'App' or a 'Stage', but could be any construct.
        :param construct_id (str): The construct ID of this stack (same as aws-cdk Stack 'construct_id').
        :param vpc_construct (VPC): The VPC construct to be used in this stack.
        """
        super().__init__(scope, construct_id)

        # Create the VPC Endpoints
        self.s3_gateway_endpoint = vpc_construct.vpc.add_gateway_endpoint(
            "S3GatewayEndpoint",
            service=aws_ec2.GatewayVpcEndpointAwsService.S3,
        )
