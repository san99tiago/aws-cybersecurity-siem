# Built-in imports
from typing import List

# External imports
from aws_cdk import (
    aws_ec2,
)
from constructs import Construct

# Own imports
from cdk_backend.common.constants import APP_PORT, ALB_PORT


class SecurityGroups(Construct):
    """
    Class to create the Security Group resources for the ASG and EC2 instances.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: aws_ec2.Vpc,
        sg_name: str,
        sg_cidrs_list: List[str],
    ) -> None:
        """
        :param scope (Construct): Parent of this stack, usually an 'App' or a 'Stage', but could be any construct.
        :param construct_id (str): The construct ID of this stack (same as aws-cdk Stack 'construct_id').
        :param vpc (aws_ec2.Vpc): The VPC where the Security Group will be created.
        :param sg_name (str): The name of the Security Group.
        :param sg_cidrs_list (List[str]): The list of CIDR blocks for the Security Group.
        """
        super().__init__(scope, construct_id)

        # ALB Security Group on port 443 (HTTPS)
        self.sg_alb = aws_ec2.SecurityGroup(
            self,
            "SG-ALB",
            vpc=vpc,
            security_group_name=f"{sg_name}-ALB",
            description=f"Security group for {sg_name} ALB",
            allow_all_outbound=True,
        )
        for cidr in sg_cidrs_list:
            self.sg_alb.add_ingress_rule(
                peer=aws_ec2.Peer.ipv4(cidr),
                connection=aws_ec2.Port.tcp(ALB_PORT),
                description=f"Allow HTTPS traffic to ALB for {cidr} CIDR",
            )

        # ASG Security Group
        self.sg_asg = aws_ec2.SecurityGroup(
            self,
            "SG",
            vpc=vpc,
            security_group_name=f"{sg_name}-ASG",
            description=f"Security group for {sg_name} ASG",
            allow_all_outbound=True,
        )

        # Allow inbound traffic from ALB to ASG on application's port
        self.sg_alb.connections.allow_from(
            self.sg_asg,
            port_range=aws_ec2.Port.tcp(APP_PORT),
            description="Allow HTTP traffic from ALB to ASG",
        )

        # TODO: Remove these rules when stabilization is finished
        self.sg_asg.add_ingress_rule(
            peer=aws_ec2.Peer.any_ipv4(),
            connection=aws_ec2.Port.all_traffic(),
            description="Allow all traffic from any source",
        )
