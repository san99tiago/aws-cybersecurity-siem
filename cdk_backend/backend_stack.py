# External imports
from aws_cdk import (
    Stack,
    CfnOutput,
)
from constructs import Construct

# Own imports
from cdk_backend.asg.infrastructure import ASG
from cdk_backend.security_groups.infrastructure import SecurityGroups
from cdk_backend.nlb.infrastructure import NLB
from cdk_backend.vpc.infrastructure import VPC
from cdk_backend.vpc_flow_logs.infrastructure import VPCFlowLogs
from cdk_backend.vpc_endpoints.infrastructure import VPCEndpoints


class NetworkingStack(Stack):
    """
    Class to create the networking stack and resources for the VPC Networking demo.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        main_resources_name: str,
        app_config: dict[str],
        **kwargs,
    ) -> None:
        """
        :param scope (Construct): Parent of this stack, usually an 'App' or a 'Stage', but could be any construct.
        :param construct_id (str): The construct ID of this stack (same as aws-cdk Stack 'construct_id').
        :param main_resources_name (str): The main unique identified of this stack.
        :param app_config (dict[str]): Dictionary with relevant configuration values for the stack.
        """
        super().__init__(scope, construct_id, **kwargs)

        # Input parameters
        self.construct_id = construct_id
        self.main_resources_name = main_resources_name
        self.app_config = app_config
        self.deployment_environment = self.app_config["deployment_environment"]
        self.app_config_networking = self.app_config["networking"]
        self.app_config_siem = self.app_config.get("siem")

        # Main methods
        self.create_vpc_resources()
        if self.app_config_siem:
            self.create_siem_resources()

        # Create CloudFormation outputs
        self.generate_cloudformation_outputs()

    def create_vpc_resources(self):
        """
        Method to create and configure the VPC resources for the networking stack.
        """
        # Create the Network resources
        self.vpc_construct = VPC(
            self,
            "NetworkVPC",
            vpc_name=self.app_config_networking["vpc_name"],
            vpc_cidr=self.app_config_networking["vpc_cidr"],
            enable_nat_gateway=self.app_config_networking["enable_nat_gateway"],
            public_subnet_mask=self.app_config_networking["public_subnet_mask"],
            private_subnet_mask=self.app_config_networking["private_subnet_mask"],
        )

        # Configure VPC Flow Logs and Endpoints (if enabled)
        if self.app_config_networking["enable_vpc_flow_logs"]:
            VPCFlowLogs(self, "NetworkLogs", vpc_construct=self.vpc_construct)

        # Create the VPC Endpoints (if enabled)
        if self.app_config_networking["enable_vpc_endpoints"]:
            VPCEndpoints(self, "NetworkEndpoints", vpc_construct=self.vpc_construct)

    def create_siem_resources(self):
        """
        Method to create and configure the SIEM resources for the networking stack.
        """
        # Create the security groups for the SIEM
        self.security_groups = SecurityGroups(
            self,
            "SecurityGroups",
            vpc=self.vpc_construct.vpc,
            sg_name=self.app_config_siem["short_name"],
            sg_cidrs_list=self.app_config_siem["sg_cidrs_list"],
        )

        # Create the Auto Scaling Group for the SIEM
        self.asg = ASG(
            self,
            "ASG",
            vpc=self.vpc_construct.vpc,
            short_name=self.app_config_siem["short_name"],
            instance_type=self.app_config_siem["instance_type"],
            min_capacity=self.app_config_siem["min_capacity"],
            max_capacity=self.app_config_siem["max_capacity"],
            desired_capacity=self.app_config_siem["desired_capacity"],
            security_group=self.security_groups.sg_asg,
            ami_name=self.app_config_siem["ami_name"],
        )

        # Create the Application Load Balancer for the SIEM
        self.nlb = NLB(
            self,
            "NLB",
            vpc=self.vpc_construct.vpc,
            short_name=self.app_config_siem["short_name"],
            security_group=self.security_groups.sg_nlb,
            nlb_target=self.asg.asg,
            hosted_zone_name=self.app_config_siem["hosted_zone_name"],
        )

    def generate_cloudformation_outputs(self):
        """
        Method to generate CloudFormation outputs for the stack.
        """
        CfnOutput(
            self,
            "VPCId",
            description="The ID of the VPC created for the networking stack",
            export_name=f"MainVpcId-{self.deployment_environment}",
            value=self.vpc_construct.vpc.vpc_id,
        )
