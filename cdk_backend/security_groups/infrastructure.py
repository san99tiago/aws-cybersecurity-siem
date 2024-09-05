# Built-in imports
from typing import List

# External imports
from aws_cdk import (
    aws_ec2,
)
from constructs import Construct

# Own imports
from cdk_backend.common.constants import (
    DASHBOARD_PORT,
    INDEXER_PORT,
    MANAGER_PORT_1,
    MANAGER_PORT_2,
    MANAGER_PORT_3,
)


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

        # NLB Security Group on port 443 (HTTPS)
        self.sg_nlb = aws_ec2.SecurityGroup(
            self,
            "SG-NLB",
            vpc=vpc,
            security_group_name=f"{sg_name}-NLB",
            description=f"Security group for {sg_name} NLB",
            allow_all_outbound=True,
        )
        for cidr in sg_cidrs_list:
            # Wazuh uses 443 for the Dashboard
            self.sg_nlb.add_ingress_rule(
                peer=aws_ec2.Peer.ipv4(cidr),
                connection=aws_ec2.Port.tcp(DASHBOARD_PORT),
                description=f"Allow HTTPS traffic to NLB for {cidr} CIDR",
            )

            # # Wazuh uses 9200 for the Indexer
            # self.sg_nlb.add_ingress_rule(
            #     peer=aws_ec2.Peer.ipv4(cidr),
            #     connection=aws_ec2.Port.tcp(INDEXER_PORT),
            #     description=f"Allow Indexer traffic to NLB for {cidr} CIDR",
            # )

            # Wazuh uses multiple ports for the Manager
            self.sg_nlb.add_ingress_rule(
                peer=aws_ec2.Peer.ipv4(cidr),
                connection=aws_ec2.Port.tcp(MANAGER_PORT_1),
                description=f"Allow Manager remoted traffic to NLB for {cidr} CIDR",
            )
            self.sg_nlb.add_ingress_rule(
                peer=aws_ec2.Peer.ipv4(cidr),
                connection=aws_ec2.Port.tcp(MANAGER_PORT_2),
                description=f"Allow Manager authd traffic to NLB for {cidr} CIDR",
            )
            self.sg_nlb.add_ingress_rule(
                peer=aws_ec2.Peer.ipv4(cidr),
                connection=aws_ec2.Port.tcp(MANAGER_PORT_3),
                description=f"Allow Manager cluster traffic to NLB for {cidr} CIDR",
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

        # Allow inbound traffic from NLB to ASG
        self.sg_asg.connections.allow_from(
            self.sg_nlb,
            port_range=aws_ec2.Port.tcp(DASHBOARD_PORT),
            description="Allow HTTP traffic from NLB to ASG",
        )
        self.sg_asg.connections.allow_from(
            self.sg_nlb,
            port_range=aws_ec2.Port.tcp(MANAGER_PORT_1),
            description="Allow Manager remoted traffic from NLB to ASG",
        )
        self.sg_asg.connections.allow_from(
            self.sg_nlb,
            port_range=aws_ec2.Port.tcp(MANAGER_PORT_2),
            description="Allow Manager authd traffic from NLB to ASG",
        )
        self.sg_asg.connections.allow_from(
            self.sg_nlb,
            port_range=aws_ec2.Port.tcp(MANAGER_PORT_3),
            description="Allow Manager cluster traffic from NLB to ASG",
        )
