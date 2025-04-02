import boto3
class sns:
    def __init__(self, arnin ='arn:aws:sns:us-east-2:354918395782:train-object-detector-ec2-sns', 
                 message = 'Notification from SNS'):
        """
        Initialize the sns class. This can be used to send notifications to SNS topics.
        """
        self.send_sns = arnin
        self.message = message
        pass
    def send_sns(self, topic_arn, message):
        """
        Send a notification to an SNS topic
        :param topic_arn: The ARN of the SNS topic
        :param message: The message to send
        """
        if topic_arn is None or message is None:
            raise ValueError("topic_arn and message cannot be None")
        sns_client = boto3.client('sns')
        sns_client.publish(
            TopicArn=topic_arn,
            Message=message
        )