import os
from datetime import datetime, timedelta, timezone

from azure.identity import DefaultAzureCredential
from azure.storage.blob import (
    BlobClient,
    BlobSasPermissions,
    BlobServiceClient,
    UserDelegationKey,
    generate_blob_sas,
)
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_user_delegation_sas_blob(
    blob_client: BlobClient, user_delegation_key: UserDelegationKey
):
    start_time = datetime.now(timezone.utc)
    expiry_time = start_time + timedelta(days=1)

    sas_token = generate_blob_sas(
        account_name=blob_client.account_name,
        container_name=blob_client.container_name,
        blob_name=blob_client.blob_name,
        user_delegation_key=user_delegation_key,
        permission=BlobSasPermissions(read=True, write=True),
        expiry=expiry_time,
        start=start_time,
    )

    return sas_token


def request_user_delegation_key(
    blob_service_client: BlobServiceClient,
) -> UserDelegationKey:
    delegation_key_start_time = datetime.now(timezone.utc)
    delegation_key_expiry_time = delegation_key_start_time + timedelta(days=1)

    user_delegation_key = blob_service_client.get_user_delegation_key(
        key_start_time=delegation_key_start_time,
        key_expiry_time=delegation_key_expiry_time,
    )

    return user_delegation_key


@app.post("/")
async def root():
    account_url = os.getenv("AZURE_BLOB_URL")
    blob_service_client = BlobServiceClient(
        account_url, credential=DefaultAzureCredential()
    )

    container_name = os.getenv("AZURE_BLOB_CONTAINER")
    container_client = blob_service_client.get_container_client(
        container=container_name
    )

    blob_client = container_client.get_blob_client("test.txt")
    user_delegation_key = request_user_delegation_key(blob_service_client)
    sas_token = create_user_delegation_sas_blob(
        blob_client=blob_client, user_delegation_key=user_delegation_key
    )
    sas_url = f"{blob_client.url}?{sas_token}"

    return {"url": sas_url}
