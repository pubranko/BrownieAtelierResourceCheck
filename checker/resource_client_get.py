import logging

from azure.core import exceptions
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

import settings


def resource_client_get() -> ResourceManagementClient:
    """
    azure のリソースにアクセスできるかチェックし、リソースクライアントインスタンスを返す。

    azuruと接続するための認証
        https://learn.microsoft.com/ja-jp/azure/developer/java/sdk/identity-azure-hosted-auth
        順序  認証方式
        1 	環境変数
        2 	マネージド ID
        3 	IntelliJ アカウント
        4 	Visual Studio Code
        5 	Azure CLI
    """
    credential = DefaultAzureCredential()

    # リソース情報を取り扱うためのクラスのようだ。
    resource_client = ResourceManagementClient(
        credential=credential,
        subscription_id=settings.AZURE_SUBSCRIPTION_ID,  # azureアカウントのサブスクリプションID
    )

    #######################################################
    # 上記のリソースクライアントが正常かチェックしている。
    #######################################################
    settings.logger.info("リソースグループのチェック")
    try:
        # リソースグループにアクセスできるか確認
        resource_group = resource_client.resource_groups.get(
            settings.AZURE_RESOURCE_GROUP_NAME,
        )
        settings.logger.info(f"リソースグループの存在を確認: {settings.AZURE_RESOURCE_GROUP_NAME}")
    except exceptions.HttpResponseError as e:
        if e.status_code == 404:
            settings.logger.exception(
                f"リソースグループがありませんでした: {settings.AZURE_RESOURCE_GROUP_NAME}"
            )
        else:
            settings.logger.exception(
                f"リソースグループにアクセスできませんでした。 : {e.status_code}"
            )
        raise

    return resource_client

if __name__ == "__main__":
    
    resource_client = resource_client_get()
    print(resource_client.__dict__)