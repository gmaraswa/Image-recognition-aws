from flask import Flask, request, session
import boto3
import uuid

config = {
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


app = Flask(__name__)


app.config['TIMEOUT'] = 3600


map = {}


def upload_file_to_s3(file_name, bucket_name, object_key):
    try:
        s3.upload_fileobj(file_name, bucket_name, object_key)
        print("\n\nUploaded " + str(file_name) + " to S3...")
        return True
    except Exception as e:
        print("Unable to upload files to S3: ", e)
        exit()


def generate_object_url(bucket_name, object_key):
    url = s3.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_key}, ExpiresIn=3600)
    return url


def send_message_to_queue(queue_url, key, message):
    try:
        sqs.send_message(QueueUrl=queue_url,
                         MessageAttributes={
                             'key': {
                                 'DataType': 'String',
                                 'StringValue': key}
                         },
                         MessageBody=message)
        print("\n\nSent " + str(message) + " to " + str(queue_url))
        return True
    except Exception as e:
        print("Unable to send messages to queue: ", e)


def get_sqs_url(queue_name):
    queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
    return queue_url


def purge_message_from_queue(queue_url, receipt_handle):
    response = sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    print(f'Message deleted from queue {queue_url}')


def is_sqs_empty(queue_url):
    response = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['ApproximateNumberOfMessages']
    )

    num_messages = int(response['Attributes']['ApproximateNumberOfMessages'])

    if num_messages == 0:
        return 1
    else:
        return 0


def receive_message_from_queue(key, queue_url):
    message = sqs.receive_message(QueueUrl=queue_url, MessageAttributeNames=['All'])
    # if some other thread has already given you the result in the map use it
    if key in map.keys():
        res = map[key]
        map.pop(key)
        return res
    if 'Messages' in message:
        # read the response queue and populate the map so the respective thread can access the
        # value directly
        for i in range(0, len(message["Messages"])):
            message_obj = message["Messages"][i]
            received_key = message_obj["MessageAttributes"]["key"]["StringValue"]
            message_body = message_obj["Body"]
            print("Message body received from response queue: ", str(message_body))
            receipt_handle = message_obj["ReceiptHandle"]
            purge_message_from_queue(queue_url, receipt_handle)
            map[received_key] = message_body
    else:
        return False


@app.route("/", methods=["POST"])
def post_data():
    
    session.permanent = True

    if "myfile" not in request.files:
        return "No file found"

    img = request.files["myfile"]

    bucket_name = config["BUCKET_NAME"]

    object_key = img.filename

    if upload_file_to_s3(img, bucket_name, object_key):
        url = generate_object_url(bucket_name, object_key)
        key = str(uuid.uuid4())
        request_queue_url = get_sqs_url("request_queue")
        if send_message_to_queue(request_queue_url, key, url):
            print("\n\nSent " + url + " to queue...")
            response_queue_url = get_sqs_url("response_queue")
            while True:
                classification_result = receive_message_from_queue(key, response_queue_url)
                if classification_result:
                    print("Sending " + classification_result + " to workload generator...")
                    return "Classification Result for " + str(classification_result.split("'")[1]) + " is " + str(
                        classification_result.split("'")[3])
    
    return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
