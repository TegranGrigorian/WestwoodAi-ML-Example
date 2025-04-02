import logging
import os
from data_manager import S3DataHandler
from train_yolo import YOLOTrainer
from sns import sns
from ec2_shutdown import Ec2Shutdown

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("main.log"),
            logging.StreamHandler()
        ]
    )

def main():
    # Configuration
    bucket_name = os.getenv('S3_BUCKET_NAME', 'train-object-detector-ec2-bucket') #TODO change you actually bucket name here or set it in your environment variables
    data_in_path = os.getenv('S3_DATA_IN_PATH', "in/roofsegment.zip") #TODO these are examples please change to your actual S3 paths
    output_zip_file = 'data.zip'
    extracted_data_dir = './'
    model_path = "yolov8n.pt"
    yaml_file = "data.yaml" #associate this with your dataset
    epochs = 1
    sns_topic_arn = os.getenv('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-2:354918395782:train-object-detector-ec2-sns')
    sns_message = "Training completed for YOLO model."
    results_zip_path = './runs.zip'
    s3_results_key = 'roofsegment.zip'
    ec2_instance_id = os.getenv('EC2_INSTANCE_ID', 'your-ec2-instance-id')

    # Initialize handlers
    data_handler = S3DataHandler(bucket_name)
    trainer = YOLOTrainer(model_path, yaml_file, epochs, bucket_name)
    sns_instance = sns()
    ec2_shutdown = Ec2Shutdown(instance_id=ec2_instance_id)

    try:
        logging.info("Step 1: Downloading data from S3...")
        data_handler.download_file(data_in_path, output_zip_file)
        logging.info("Step 2: Extracting data...")
        data_handler.extract_zip(output_zip_file, extract_to=extracted_data_dir)

        logging.info("Step 3: Starting YOLO training...")
        trainer.train_model()

        logging.info("Step 4: Zipping training results...")
        trainer.zip_results(runs_dir='./runs', zip_path=results_zip_path)
        logging.info("Step 5: Uploading results to S3...")
        trainer.upload_results(zip_path=results_zip_path, s3_key=s3_results_key)

        logging.info("Step 6: Sending SNS notification...")
        sns_instance.send_sns(topic_arn=sns_topic_arn, message=sns_message)

        logging.info("Step 7: Shutting down EC2 instance...")
        logging.info("Process completed successfully, and EC2 instance is shutting down.")

        #shutdown, any code after this will not be executed after shutdown command is called
        ec2_shutdown.shutdown()


    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    configure_logging()
    main()
