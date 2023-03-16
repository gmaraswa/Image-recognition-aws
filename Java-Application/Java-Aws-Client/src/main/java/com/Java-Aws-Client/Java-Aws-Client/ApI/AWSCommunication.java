package com.ImageId.ImageId.ApI;


import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.PutObjectRequest;
import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.AmazonSQSClientBuilder;
import com.amazonaws.services.sqs.model.*;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.codec.digest.DigestUtils;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class AWSCommunication {
    private static ConcurrentHashMap<String, String> responseMap = new ConcurrentHashMap<>();

    public String process(MultipartFile filePart) throws IOException {
        //Upload to S3
        String imageUrl = uploadToS3(filePart);
        String key = UUID.randomUUID().toString();
        sendMessage(key, imageUrl, Constants.REQUEST_QUEUE);
        String classificationResult = null;
        do {
            classificationResult = getResponseFromQueueOrMap(key, Constants.RESPONSE_QUEUE);
        } while (classificationResult == null);
        return classificationResult;
    }

    public void purgeMessage(String queueUrl, String receiptHandle) {
        getSQSClient().deleteMessage(
                queueUrl,
                receiptHandle
        );
    }

    private String getResponseFromQueueOrMap(String key, String responseQueue) {
        if (responseMap.containsKey(key)) {
            return responseMap.get(key);
        } else {
            String queueUrl = getSQSClient().getQueueUrl(responseQueue).getQueueUrl();
            ReceiveMessageRequest receiveMessageRequest = new ReceiveMessageRequest(queueUrl);
            ReceiveMessageResult receiveMessageResult = getSQSClient().receiveMessage(receiveMessageRequest.withMessageAttributeNames("key"));
            receiveMessageResult.getMessages().forEach(message -> {
                String receivedKey = message.getMessageAttributes().get("key").getStringValue();
                responseMap.put(receivedKey, message.getBody());
                purgeMessage(queueUrl, message.getReceiptHandle());
            });
            return null;
        }

    }

    public void sendMessage(String key, String messageBody, String queueName) {
        String queueUrl = getSQSClient().getQueueUrl(queueName).getQueueUrl();
        Map<String, MessageAttributeValue> messageAttributes = new HashMap<>();
        messageAttributes.put("key", new MessageAttributeValue().withDataType("String")
                .withStringValue(key));
        SendMessageRequest sendMessageRequest = new SendMessageRequest().withQueueUrl(queueUrl)
                .withMessageBody(messageBody)
                .withMessageAttributes(messageAttributes);
        getSQSClient().sendMessage(sendMessageRequest);
    }

    public BasicAWSCredentials basicAWSCredentials() {
        return new BasicAWSCredentials(Constants.ACCESSKEY, Constants.SECRETKEY);
    }

    public AmazonS3 getS3Client() {
        return AmazonS3ClientBuilder.standard().withRegion(Constants.REGION)
                .withCredentials(new AWSStaticCredentialsProvider(basicAWSCredentials())).build();
    }

    public AmazonSQS getSQSClient() {
        return AmazonSQSClientBuilder.standard().withRegion(Constants.REGION)
                .withCredentials(new AWSStaticCredentialsProvider(basicAWSCredentials())).build();
    }

    private String uploadToS3(MultipartFile filePart) throws IOException {
        AmazonS3 s3Client = getS3Client();
        byte[] resultByte = DigestUtils.md5(filePart.getInputStream());
        String streamMD5 = new String(Base64.encodeBase64(resultByte));
        ObjectMetadata meta = new ObjectMetadata();
        meta.setContentMD5(streamMD5);
        s3Client.putObject(new PutObjectRequest(Constants.BUCKET_NAME, filePart.getOriginalFilename(),
                filePart.getInputStream(), meta));
        return s3Client.getUrl(Constants.BUCKET_NAME, filePart.getOriginalFilename()).toString();
    }
}
