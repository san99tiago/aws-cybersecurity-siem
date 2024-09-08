# Built-in imports
import os, enum
from typing import Optional

# External imports
from aws_cdk import (
    aws_autoscaling,
    aws_ec2,
    aws_iam,
)
from constructs import Construct


class ASGType(enum.Enum):
    """
    Enum to define the different types of ASG resources.
    """

    WAZUH_SERVER = "wazuh_server"
    WAZUH_AGENT = "wazuh_agent"


class ASG(Construct):
    """
    Class to create the Auto Scaling Group resources for the servers.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: aws_ec2.Vpc,
        short_name: str,
        instance_type: str,
        min_capacity: str,
        max_capacity: str,
        desired_capacity: str,
        security_group: aws_ec2.SecurityGroup,
        ami_name: str,
        asg_type: Optional[ASGType] = ASGType.WAZUH_SERVER,
    ) -> None:
        """
        :param scope (Construct): Parent of this stack, usually an 'App' or a 'Stage', but could be any construct.
        :param construct_id (str): The construct ID of this stack (same as aws-cdk Stack 'construct_id').
        :param vpc (aws_ec2.Vpc): The VPC where the Security Group will be created.
        :param short_name (str): The short name for the ASG resources.
        :param instance_type (str): The instance type for the ASG.
        :param min_capacity (str): The minimum capacity for the ASG.
        :param max_capacity (str): The maximum capacity for the ASG.
        :param desired_capacity (str): The desired capacity for the ASG.
        :param security_group (aws_ec2.SecurityGroup): The Security Group for the ASG.
        :param ami_name (str): The name of the AMI to use for the ASG (e.g. "Amazon Linux 2").
        :param asg_type (ASGType): The type of ASG resource to create (default: ASGType.WAZUH_SERVER).
        """
        super().__init__(scope, construct_id)

        self.instance_role = aws_iam.Role(
            self,
            "InstanceRole",
            role_name=f"{short_name}-instance-role",
            description=f"Role for {short_name} servers",
            assumed_by=aws_iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                # aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                #     "EC2InstanceConnect"
                # ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "CloudWatchAgentServerPolicy"
                ),
            ],
        )

        self.asg = aws_autoscaling.AutoScalingGroup(
            self,
            "AutoScaling",
            auto_scaling_group_name=f"{short_name}v1",
            vpc=vpc,
            vpc_subnets=aws_ec2.SubnetSelection(
                subnet_type=aws_ec2.SubnetType.PUBLIC,
            ),
            instance_type=aws_ec2.InstanceType(instance_type),
            machine_image=aws_ec2.MachineImage.lookup(
                name=ami_name,
            ),
            min_capacity=min_capacity,
            max_capacity=max_capacity,
            desired_capacity=desired_capacity,
            security_group=security_group,
            role=self.instance_role,
        )

        # Add user data Environment Variables to the ASG/EC2 initialization
        self.asg.add_user_data(f"echo export VPC_ID={vpc.vpc_id} >> /etc/profile")

        if asg_type == ASGType.WAZUH_SERVER:
            PATH_TO_USER_DATA = os.path.join(
                os.path.dirname(__file__), "user_data_script_server.sh"
            )
        elif asg_type == ASGType.WAZUH_AGENT:
            PATH_TO_USER_DATA = os.path.join(
                os.path.dirname(__file__), "user_data_script_agents.sh"
            )
        else:
            raise ValueError("Invalid ASGType provided.")

        with open(PATH_TO_USER_DATA, "r") as file:
            user_data_script = file.read()
            self.asg.add_user_data(user_data_script)
