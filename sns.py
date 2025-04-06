import boto3
import logging

class sns:
    def __init__(self, arnin='arn:aws:sns:us-east-2:354918395782:train-object-detector-ec2-sns', 
                 message='Notification from SNS', region_name='us-east-2'):
        """
        Initialize the sns class. This can be used to send notifications to SNS topics.
        """
        self.default_arn = arnin  # Renamed from send_sns to default_arn
        self.default_message = message  # Renamed from message
        self.region_name = region_name  # Added region_name attribute

    def send_sns(self, topic_arn, message):
        """
        Send a notification to an SNS topic
        :param topic_arn: The ARN of the SNS topic
        :param message: The message to send
        """
        if topic_arn is None or message is None:
            raise ValueError("topic_arn and message cannot be None")
        logging.info(f"Sending SNS message to topic: {topic_arn}")
        logging.info(f"Message: {message}")
        sns_client = boto3.client('sns', region_name=self.region_name)  # Specify region_name
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message
        )
        logging.info(f"SNS publish response: {response}")