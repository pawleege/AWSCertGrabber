import json
import requests
import os
import boto3
import argparse
# profiles are needed to be setup in ~/.aws/config
# i.e. [profile 000000000000]
# role_arn = arn:aws:iam::0000000000000:role/example-admin-role
# source_profile = default

def get_certs_and_association(profile_name, region):
    _session = boto3.Session(region_name=region, profile_name=profile_name)
    resp = _session.client('acm').list_certificates(
            CertificateStatuses=[
                'ISSUED'
            ],
            MaxItems=500)
    certs = resp.get('CertificateSummaryList')
    fullreturn = []
    for cert in certs:
        certarn = cert['CertificateArn']
        description = _session.client('acm').describe_certificate(CertificateArn=certarn)
        domainname = description['Certificate']['DomainName']
        inuseby = description['Certificate']['InUseBy']
        flatinuse = flatten_list(inuseby)
        readableformat = certarn + ", " + domainname + " used by: " + flatinuse
        fullreturn.append(readableformat)
    return fullreturn

def flatten_list(inputlist):
    returnstring = ", "
    return returnstring.join(inputlist)

def main(accounts, region):
    if type(accounts) is list:
        for account in accounts:
            resp = get_certs_and_association(account,region)
            for item in resp:
                print account + ": " + item
    else:
        resp = get_certs_and_association(account,region)
        for item in resp:
            print account + ": " + item

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--account", nargs='+', help="aws account number", required=True)
    parser.add_argument("-r", "--region", help="aws region", required=True)
    args = parser.parse_args()
    main(args.account, args.region)
