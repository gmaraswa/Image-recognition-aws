# Cloud_project_1 - IaaS
This project is a part of course work CSE 546: Cloud Computing.
Professor - Yuli Deng.


## Team Members
- Sai Vikhyath Kudhroli - 1225432689
- Gautham Maraswami - 1225222063
- Abhilash Subhash Sanap - 1225222362



## Project Requirements


### Software Requirements
    Python3
    Boto3 - AWS SDK for python
    Flask - REST service
    
### AWS CLI
    Install aws-cli from 
    https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

### AWS Configuration.
    Use command: aws configure
    ACCESS_KEY_ID = ####
    SECRET_ACCESS_KEY_ID = ####
    REGION = us-east-1
    OUTPUT = JSON

    PEM key file for SSH Access: cc.pem

### Installing requirements

Download Python from ``https://www.python.org/downloads/``

#### Installing packages:
    boto3         : pip install boto3
    flask         : pip install flask

### Running the application
    Make sure to install all the requirements before running the application.
#### WebTier:
- Create an EC2 instance using the script or via AWS console, use ubuntu as the operating system.
- Install flask and boto3 libraries.
- Configure security and firewall for the instance so as to allow traffic only in port 5000
- Configure SSH access in the EC2 instance, and add your public key to the allowed list.
- Configure Mobaxterm in your local system so you will be able to do SCP via GUI.
- Upload web_tier.py to the EC2 instance using Mobaxterm
- Run the script using nohup 
- Create cron jobs using the no hang up (nohup) process to start the applications automatically when the instances are booted.
#### AppTier:
- Create an EC2 instance using the script or via AWS console, using ubuntu as the operating system.
- Install Boto3 library.
- Configure the security group to allow SSH on port 22.
- Perform SSH key-gen to access the EC2 instance using SSH.
- Perform SCP to copy the app_tier.py to the EC2 instance.
- Enter the directory where the file has been copied.
- Run the script using the following command
  - nohup python3 app_tier.py > app_tier.log 2>&1 &
- Create a cron job using the below command to start the script automatically when the instances are booted.
  - @reboot nohup python3 app_tier.py > app_tier.log 2>&1 &

### Member tasks
#### Sai Vikhyath Kudhroli
- Devised an approach to integrate the image classification code with the app tier.
- Implemented the app-tier application.
Implemented a method to retrieve the queue URL, and retrieve the image URL, and the unique key from the request queue and delete it on reception.
- Modified the image classifier to directly use the image URL to classify the image without downloading the image locally, which saves enormous storage space.
- Form a key-value pair of the image name and the classification result and push it to the output S3 bucket.
- Map the classification result with the unique key and send this response to the response queue.
- Write cron jobs using the no hang up (nohup) process in the web tier and app tier to start the applications automatically when the instances are booted.
- Configure the security groups for EC2 instances and set up user policies to allow privileged access to the instances and enable SSH access and TCP connections to instances to allow requests to be sent to the web tier.
- Configure the S3 bucket policy for the objects to be accessible to the application.

#### Gautham Maraswami (1225222063)
- Designed methods to write to SQS write queue and read from SQS read queue.
- Developed a Flask application to handle REST requests from workload-generator/ web browser.
- When the controller receives the image file, the file will be uploaded to the S3 bucket using the credentials.
- Once the file is uploaded successfully, the URL is generated for further processing.
- Designed a UUID-based key-value pair to map the request sent from the web tier and the response received from the app tier so that even though processing at the app tier happens asynchronously, the web tier is able to return the right results.
- Developed methodology so the messages in the response queue are accessed only once.
- Created a web tier instance and installed all relevant packages like Flask, and Boto3 for the application to run.
- End-to-end testing of the application was performed to make sure that there is no request loss, and no idle instances.
#### Abhilash Subhash Sanap (1225222362)
- Set up EC2 instances for app and web tier, request and response queues, and S3 input and output buckets to start off the project.  
- Created an Amazon Machine Image (AMI) from a running app-tier EC2 instance
- Created a launch template from the AMI created in step 2. 
- Created an AWS Autoscaling Group (ASG) using the launch template in step 3.
- Configured the parameters of the ASG to meet the requirements as stated in the project guide.
- Defined a custom metric ApproximateNumberOfMessagesVisible - GroupInServiceInstances with a math logic using AWS CloudWatch.
- Defined an alarm each for Scale-Out and Scale In 
- Defined a Scale-Out Step Scaling policy and a Scale-In Step Scaling policy
- Tested the setup End to End to ensure that the execution finishes well within the stipulated time of 7 minutes.

