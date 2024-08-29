# External imports
from aws_cdk import (
    aws_ec2,
)
from constructs import Construct


class VPC(Construct):
    """
    Class to create the VPC resources.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc_name: str,
        vpc_cidr: str,
        enable_nat_gateway: bool,
        public_subnet_mask: int,
        private_subnet_mask: int,
    ) -> None:
        """
        :param scope (Construct): Parent of this stack, usually an 'App' or a 'Stage', but could be any construct.
        :param construct_id (str): The construct ID of this stack (same as aws-cdk Stack 'construct_id').
        :param vpc_name (str): The name of the VPC.
        :param vpc_cidr (str): The CIDR block for the VPC.
        :param enable_nat_gateway (bool): Flag to enable NAT Gateways in the VPC.
        :param public_subnet_mask (int): The mask for the public subnets.
        :param private_subnet_mask (int): The mask for the private subnets.
        """
        super().__init__(scope, construct_id)

        # Create the main VPC with public and private subnets
        self.vpc = aws_ec2.Vpc(
            self,
            "VPC",
            vpc_name=vpc_name,
            ip_addresses=aws_ec2.IpAddresses.cidr(vpc_cidr),
            max_azs=2,
            create_internet_gateway=True,
            # Only 1 or 0 NATs to reduce costs ... 0.045 USD/hour
            nat_gateways=1 if enable_nat_gateway else 0,
            subnet_configuration=[
                aws_ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=aws_ec2.SubnetType.PUBLIC,
                    cidr_mask=public_subnet_mask,
                ),
                aws_ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=private_subnet_mask,
                ),
            ],
        )
