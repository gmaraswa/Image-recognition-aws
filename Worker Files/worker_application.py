import boto3
import time
import image_classification


config ={
    "AWS_ACCESS_KEY_ID": "AKIAUZP4JGMVM5X62UGD", 
    "AWS_SECRET_ACCESS_KEY": "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",
    "BUCKET_NAME": "imageinputbucket"
}

# Create a session and an EC2 client
session = boto3.Session(
    region_name="us-east-1",
    aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"]
)

# Get the SQS client
s3 = session.client("s3")

# Get the SQS client
sqs = session.client("sqs")


def push_result_to_s3(image_name, key, classification_label, bucket_name):
    try:
        image_id = image_name[:-5] + ".txt"
        data = {image_name:classification_label}
        print(data, bucket_name)
        print(type(image_name))
        # convert dictionary to string
        data_str = str(data)

        # create object in S3 bucket
        s3.put_object(Bucket=bucket_name, Key=image_id, Body=data_str)
        return 1
    except Exception as e:
        print("Unable to upload files to S3: ", e)
        exit()


def get_sqs_url(queue_name):
    queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
    return queue_url


def purge_message_from_queue(queue_url, receipt_handle):
    response = sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    print(f'\n\nMessage deleted from queue {queue_url}')


def send_message_to_queue(queue_url, key, message):
    try:
        sqs.send_message(QueueUrl=queue_url,
                         MessageAttributes={
                             'key': {
                                 'DataType': 'String',
                                 'StringValue': str(key)}
                         },
                         MessageBody=message)
    except Exception as e:
        print("Error sending message to queue: ", e)


def get_sqs_url(queue_name):
    queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
    return queue_url


def receive_message_from_queue(queue_url):
    # Receive a message from the SQS queue
    message = sqs.receive_message(QueueUrl=queue_url, MessageAttributeNames=['All'])

    # Print the received message, if any
    if 'Messages' in message:
        message_body = message["Messages"][0]["Body"]
        receipt_handle = message["Messages"][0]["ReceiptHandle"]
        key = message["Messages"][0]["MessageAttributes"]["key"]["StringValue"]
        purge_message_from_queue(queue_url, receipt_handle)
        return (key, message_body)
    # else:
    #     print("\n\nNo message received.")

    return None


def listen():
    request_queue_url = get_sqs_url("request_queue")
    while (1):
        time.sleep(15)
        object = receive_message_from_queue(request_queue_url)
        if object:
            key, object_url = object
            print("\n\nReceived message from queue: ", object_url)
            result = image_classification.image_classification(object_url)
            file_name = str(object_url).split("/")[3].split("?")[0]
            classification_result = result.split(",")[1]
            result = str((file_name, classification_result))
            print("\n\nImage Classification Result: ", result)
            response_queue_url = get_sqs_url("response_queue")
            send_message_to_queue(response_queue_url, key, result)
            push_result_to_s3(file_name, key, classification_result, "imageoutputbucket")


if __name__ == "__main__":
    listen()
