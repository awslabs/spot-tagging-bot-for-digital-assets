import boto3


class EcsController:
    """
    Ref:
    https://docs.aws.amazon.com/zh_cn/AmazonECS/latest/developerguide/ECS_AWSCLI_Fargate.html
    https://docs.aws.amazon.com/zh_cn/AmazonECS/latest/developerguide/ecs-cli-tutorial-fargate.html
    https://docs.aws.amazon.com/zh_cn/step-functions/latest/dg/sample-project-container-task-notification.html
    """

    CLUSTER_NAME = "spot_bot_fargate_cluster"

    def __init__(self):
        """
        Ensure the iam role for cluster is created using iam_helper.py
        Ensure the cluster is created.
        """
        self.client = boto3.client("ecs")

    def create_fargate_cluster(self):
        """
        According to test, create cluster is a PUT-like operation, and it can be invoked many times on same cluster.
        :return:
        """
        # TODO dig defaultCapacityProviderStrategy
        response = self.client.create_cluster(
            clusterName=self.CLUSTER_NAME,
            capacityProviders=[
                'FARGATE', 'FARGATE_SPOT'
            ]
        )
        print("<<<< new cluster created with details - " + str(response))
        return response["cluster"]["clusterArn"]

    def get_cluster_status(self) -> str:
        response = self.client.describe_clusters(
            clusters=[self.CLUSTER_NAME]
        )
        # One of ACTIVE, PROVISIONING, DEPROVISIONING, FAILED, INACTIVE
        print("<<< cluster status is " + str(response))
        return response["clusters"][0]["status"]

    def delete_cluster(self):
        response = self.client.delete_cluster(
            cluster=self.CLUSTER_NAME
        )

        print("<<< delete cluster response is: " + str(response))

    def create_service(self, service_name, number_of_instance):
        """
        :param service_name: points to a configuration of the image etc.
        ref:
        https://stackoverflow.com/questions/42960678/what-is-the-difference-between-a-task-and-a-service-in-aws-ecs
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html#ECS.Client.create_service
        https://lobster1234.github.io/2017/12/03/run-tasks-with-aws-fargate-and-lambda/
        """

        response = self.client.create_service(
            desiredCount=number_of_instance,
            serviceName=service_name,
            taskDefinition='hello_world',
        )

        print("<<< create service response is: " + str(response))
