import boto3
import json

def validate(event, context, rds_client):
    try:
        print("***** Validation Started *****")

        response = rds_client.describe_global_clusters(
            GlobalClusterIdentifier = event['GlobalClusterIdentifier'],
        )
        print("Describe global cluster response: ", response)

        validation = None
        for member in response['GlobalClusters'][0]['GlobalClusterMembers']:
            if member['DBClusterArn'] == event['TargetDbClusterIdentifier']:
                print("Target database cluster identifier matched")
                validation = True
                break
            else:
                print("Global cluster members validation failed")
                validation = False

        print("***** Validation Completed *****")
        return validation

    except Exception as e:
        print(f"An unexpected error occurred in validation: {str(e)}")
        return "Exception"

def failover(event, context, rds_client):
    try:
        print("***** Failover Started *****")

        response = rds_client.failover_global_cluster(
            GlobalClusterIdentifier = event['GlobalClusterIdentifier'],
            TargetDbClusterIdentifier = event['TargetDbClusterIdentifier'],
            AllowDataLoss = True
        )
        print("Failover global cluster response: ", response)

        print("***** Failover Completed *****")
        return True

    except Exception as e:
        print(f"An unexpected error occurred in failover: {str(e)}")
        return "Exception"

def failback(event, context, rds_client):
    try:
        print("***** Failback Started *****")

        response = rds_client.switchover_global_cluster(
            GlobalClusterIdentifier = event['GlobalClusterIdentifier'],
            TargetDbClusterIdentifier = event['TargetDbClusterIdentifier']
        )
        print("Failback global cluster response: ", response)

        print("***** Failback Completed *****")
        return True

    except Exception as e:
        print(f"An unexpected error occurred in failback: {str(e)}")
        return "Exception"

def status(event, context, rds_client):
    try:
        print("***** Polling Started *****")

        response = rds_client.describe_global_clusters(
            GlobalClusterIdentifier = event['GlobalClusterIdentifier'],
        )
        print("Global cluster status: ", response['GlobalClusters'][0]['Status'])

        status = None
        for member in response['GlobalClusters'][0]['GlobalClusterMembers']:
            if member['DBClusterArn'] == event['TargetDbClusterIdentifier']:
                if member['IsWriter'] == False:
                    print("Target database cluster identifier is not writer yet")
                    status = False
                elif member['IsWriter'] == True:
                    print("No failover/failback/failback is required as target database cluster identifier is already the writer")
                    if response['GlobalClusters'][0]['Status'] == "available":
                        response = rds_client.describe_db_clusters(
                            DBClusterIdentifier = event['TargetDbClusterIdentifier']
                        )
                        print("Target database cluster status: ", response['DBClusters'][0]['Status'])
                        if response['DBClusters'][0]['Status'] == "available":
                            status = True
                        else:
                            print("Target database cluster status is not available")
                            status = False
                    else:
                        print("Global database cluster status is not available")
                        status = False
                    break

        print("***** Polling Completed *****")
        return status

    except Exception as e:
        print(f"An unexpected error occurred in polling: {str(e)}")
        return "Exception"

def lambda_handler(event, context):
    try:
        print("Event received: ", str(event))

        region = event['TargetDbClusterIdentifier'].split(':')[3]
        rds_client = boto3.client('rds', region_name = region)

        validate_response = validate(event, context, rds_client)
        print("Validate response:", validate_response)

        if validate_response == "Exception":
            response_data = {
                "Message": "Validation failed with exception"
            }
            response_body = json.dumps(response_data)

            return {
                'statusCode': 500,
                'body': response_body
            }
        elif validate_response == False:
            response_data = {
                "Message": "Validation failed"
            }
            response_body = json.dumps(response_data)

            return {
                'statusCode': 500,
                'body': response_body
            }
        elif event['Action'] == "failover":
            failover_response = failover(event, context, rds_client)
            print("Failover response:", failover_response)

            response_data = {
                "Message": "Failover action completed",
                "Output": failover_response
            }
            response_body = json.dumps(response_data)

            return {
                'statusCode': 200,
                'body': response_body
            }
        elif event['Action'] == "failback":
            failback_response = failback(event, context, rds_client)
            print("Failback response:", failback_response)

            response_data = {
                "Message": "Failback action completed",
                "Output": failback_response
            }
            response_body = json.dumps(response_data)

            return {
                'statusCode': 200,
                'body': response_body
            }
        elif event['Action'] == "status":
            status_response = status(event, context, rds_client)
            print("Status response:", status_response)

            response_data = {
                "Message": "Polling action completed",
                "Output": status_response
            }
            response_body = json.dumps(response_data)

            return {
                'statusCode': 200,
                'body': response_body
            }
        else:
            response_data = {
                "Message": "No action matched",
            }
            response_body = json.dumps(response_data)

            return {
                'statusCode': 200,
                'body': response_body
            }

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")