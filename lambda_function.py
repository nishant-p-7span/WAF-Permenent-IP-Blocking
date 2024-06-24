# function to add ip permently to block list.
import json
import boto3
import logging
import os

wafv2_client = boto3.client('wafv2')

def update_custom_ipset(log, new_ipv4_blocked_list):
    try:
        # Fetch the current IPs in the custom IP set
        ip_set_id = os.getenv('IP_SET_ID_CUSTOM_V4')
        ip_set_name = os.getenv('IP_SET_NAME_CUSTOM_V4')
        current_ip_set = wafv2_client.get_ip_set(
            Scope=os.getenv('SCOPE'),
            Name=ip_set_name,
            Id=ip_set_id
        )
        
        current_ipv4_blocked_list = current_ip_set['IPSet']['Addresses']
        
        # Merge the current IPs with the new IPs
        updated_ipv4_blocked_list = list(set(current_ipv4_blocked_list + new_ipv4_blocked_list))
        
        # Get lock token for updating the IP set
        lock_token = current_ip_set['LockToken']
        
        # Update the IP set with the merged list
        update_ip_set(
            log, wafv2_client,
            ip_set_id,
            updated_ipv4_blocked_list,
            lock_token,
            ip_set_name
        )
    except Exception as e:
        log.error("[update_custom_ipset] Error updating custom ipset.")
        raise e

def get_lock_token(log, wafv2_client, ip_set_id, name):
    try:
        response = wafv2_client.get_ip_set(
            Scope=os.getenv('SCOPE'),
            Name=name,
            Id=ip_set_id
        )
        return response['LockToken']
    except Exception as e:
        log.error(f"Error in get_lock_token: {e}")
        raise

def update_ip_set(log, wafv2_client, ip_set_id, addresses, lock_token, name):
    try:
        wafv2_client.update_ip_set(
            Scope=os.getenv('SCOPE'),
            Name=name,
            Id=ip_set_id,
            Addresses=addresses,
            LockToken=lock_token
        )
    except Exception as e:
        log.error("Error in update_ip_set: {}".format(e))
        raise

def get_rbr_managed_ip_list(log):
    try:
        response = wafv2_client.get_rate_based_statement_managed_keys(
            Scope=os.getenv('SCOPE'),
            WebACLName=os.getenv('WEB_ACL_NAME'),
            WebACLId=os.getenv('WEB_ACL_ID'),
            RuleName=os.getenv('RATE_BASED_RULE_NAME')
        )
        return response
    except Exception as e:
        log.error("[get_rbr_managed_ip_list] Error to get the list of IP blocked by rate based rule")
        log.error(e)
        raise e

def lambda_handler(event, context):
    log = logging.getLogger()

    try:
        # Set Log Level
        log.setLevel(logging.ERROR)

        # Get the list of IP blocked by rate based rule
        rbr_managed_list = get_rbr_managed_ip_list(log)

        # Get the list of IPv4 addresses from the rate based rule list
        latest_ipv4_blocked_list = rbr_managed_list['ManagedKeysIPV4']['Addresses']

        # Update latest blocked list to WAF IPset
        update_custom_ipset(log, latest_ipv4_blocked_list)

        return {
            'statusCode': 200,
            'body': json.dumps('Update Success!')
        }
    except Exception as e:
        log.error(e)
        return {
            'statusCode': 500,
            'body': str(e)
        }
