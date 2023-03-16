package com.ImageId.ImageId.Controller;

import com.ImageId.ImageId.ApI.AWSCommunication;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@EnableAutoConfiguration
@RequestMapping("/")
public class ImageController {
    @Autowired
    private AWSCommunication awsCommunication;

    @RequestMapping(value = "test", method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<String> getInfo() {
        return new ResponseEntity<String>("Project is Running!", HttpStatus.OK);
    }

    @RequestMapping(path = "/upload", method = RequestMethod.POST)
    public String uploadInvoice(@RequestParam("myfile")MultipartFile filePart) throws IOException {
        return awsCommunication.process(filePart);
    }
}
