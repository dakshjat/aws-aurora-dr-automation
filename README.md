# Amazon Aurora DR Automation (Warm Standby)

Use the AWS CloudFormation template to create an AWS Lambda function to orchestrate Amazon Aurora Global Database Disaster Recovery with a warm standby strategy. The Lambda function simplifies failover and failback operations for an AWS Aurora Global Database cluster using the Python Boto3 library to interact with the AWS RDS service and perform the necessary API calls.
___
![Amazon Aurora DR Automation - Warm Standby](https://github.com/dakshjat/aws-aurora-dr-automation/assets/47545538/e32358bc-9901-443f-ba4a-d053d8f4fa5e)
___

### Solution Overview
* Managing failover and failback operations in an Aurora Global Database cluster can be complex, especially when dealing with multiple AWS accounts and regions. This Lambda function provides a centralized solution that can be used across accounts and regions for Amazon Aurora Disaster Recovery (DR) solutions.

* The Lambda function consists of several functions, each responsible for a specific action:

  * **Validate**: This function validates the global cluster and target database cluster by calling the `describe_global_clusters` API and checking if the target database cluster is a member of the global cluster.

  * **Failover**: This function initiates a failover by calling the `failover_global_cluster` API and specifying the target database cluster identifier.

  * **Failback**: This function initiates a failback by calling the `switchover_global_cluster` API and specifying the target database cluster identifier.

  * **Status**: This function checks the status of the target database cluster and returns the result by calling the `describe_global_clusters` and `describe_db_clusters` APIs.

The lambda_handler function acts as the entry point for the Lambda function. It receives an event as input, which includes the action, the global cluster identifier, and the target database cluster identifier. Based on the action, the function calls the respective action function and returns a response with a status code and a JSON body containing a message and any relevant output.
___

### Use Cases
* **Failover**: By invoking the Lambda function with the action set to `failover`, you can initiate a failover in the Aurora Global Database cluster. This is useful in scenarios where the primary cluster becomes unavailable and you need to switch to the secondary cluster for continued operations.

* **Failback**: After a failover, you can use the Lambda function with the action set to `failback` to initiate a failback process. This involves switching the primary cluster back to the original cluster once it becomes available again. This ensures the resynchronization of data and restores the original cluster's role as the primary.

* **Status Checks**: The Lambda function also provides a status check functionality. By invoking the Lambda function with the action set to `status`, you can retrieve the status of the target database cluster. This is useful for monitoring purposes and ensuring the cluster is in the desired state.
___

### Prerequisites
* An AWS account with the necessary permissions to create and manage Lambda functions and AWS RDS resources.
* An Aurora Global Database cluster set up in your AWS account. Use the [Amazon Aurora Global Database](https://github.com/dakshjat/aws-aurora-global-database) AWS CloudFormation templates to provision and manage Amazon Aurora Global Databases.
___

### Create an AWS CloudFormation stack

**#1.** From the AWS console, create an AWS CloudFormation stack with new resources, specify the template, and enter appropriate parameters.

**#2.** Use the below AWS CLI command to create an AWS CloudFormation stack with a parameter file:

* `aws cloudformation deploy --stack-name aws-aurora-dr-automation --template-file aws-aurora-dr-automation-lambda.yaml --parameter-overrides file://parameters.json --capabilities CAPABILITY_NAMED_IAM`
___

### Sample Event Payload

**#1. To perform failover:**
```json
{
  "Action": "failover",
  "GlobalClusterIdentifier": "<global_cluster_identifier>",
  "TargetDbClusterIdentifier": "<target_db_cluster_identifier_arn>"
}
```

**#2. To perform failback:**
```json
{
  "Action": "failback",
  "GlobalClusterIdentifier": "<global_cluster_identifier>",
  "TargetDbClusterIdentifier": "<target_db_cluster_identifier_arn>"
}
```

**#3. To check the failover/failback status:**
```json
{
  "Action": "status",
  "GlobalClusterIdentifier": "<global_cluster_identifier>",
  "TargetDbClusterIdentifier": "<target_db_cluster_identifier_arn>"
}
```
___

### Function Responses

The Lambda function returns a response using a dictionary with two key-value pairs: 'statusCode' and 'body'. Here's an overview of each component:

**1. 'statusCode':**
* The 'statusCode' key represents the HTTP status code of the response.
* A status code of 200 indicates a successful response, while a status code of 500 indicates an error or failure.
*  Other common status codes include 400 for bad requests and 404 for resource not found.
* The status code helps the caller understand the outcome of the Lambda function execution.

**2. 'body':**
* The 'body' key contains the payload of the response, which is typically a JSON-formatted string.
* The value of 'body' can include relevant data, messages, or errors to be returned to the caller.
* The caller can parse the JSON response to extract the necessary information and take appropriate actions based on the response.

**For example - a response generated by the Lambda function:**

```json
{
  "statusCode": 200,
  "body": "{\"Message\": \"Failover action completed\", \"Output\": true}"
}
```

In this response:
- The 'statusCode' is 200, indicating a successful response.
- The 'body' contains a JSON-formatted string with two key-value pairs: 'Message' and 'Output'.
  - The 'Message' key provides a message indicating that the failover action was completed successfully.
  - The 'Output' key contains the output of the failover action, which is set to 'true'.

The Lambda caller can access the response and retrieve the necessary information based on the keys provided. This information is used to handle the response within the application/system accordingly. By returning a response in this format, the Lambda function provides a standardized way to communicate outcomes, errors, and data to the caller, enabling better integration and interoperability between systems.

___

For more information on failover and failback operations in an Aurora Global Database cluster, visit [Using switchover or failover in an Amazon Aurora global database](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html).