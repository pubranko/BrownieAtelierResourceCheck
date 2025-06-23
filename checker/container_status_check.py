from typing import Any, Dict

from azure.core import exceptions
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models._models_py3 import ContainerGroup
from azure.identity import DefaultAzureCredential

from checker.resource_client_get import resource_client_get
import settings

""" statusの種類
Creating: コンテナーが作成中
Waiting: コンテナーが起動を待機中
Pulling: Dockerイメージを取得中
Pulled: Dockerイメージの取得が完了
Starting: コンテナーの起動処理中
Running: コンテナーが実行中
Terminating: コンテナーが終了処理中
Stopped: コンテナーが停止されている
Failed: コンテナーの作成や実行が失敗
Unknown: コンテナーの状態が不明
空文字: コンテナーが存在しない。
"""


def container_status_check() -> Dict[str, str]:
    """
    リソースグループ内の全コンテナーグループのステータスを取得し返す。
    存在しない場合は空のdictを返す。
    """
    # azureのリソースグループ情報を取得。
    resource_client = resource_client_get()
    resource_group = resource_client.resource_groups.get(
        settings.AZURE_RESOURCE_GROUP_NAME,
    )

    credential = DefaultAzureCredential()
    aci_client = ContainerInstanceManagementClient(
        credential, settings.AZURE_SUBSCRIPTION_ID
    )

    status_dict: Dict[str, str] = {}
    try:
        container_groups = aci_client.container_groups.list_by_resource_group(
            resource_group_name=str(resource_group.name)
        )
        for group in container_groups:
            if not group.name:
                continue  # 名前がない場合はスキップ
            group_status = ""
            try:
                cg = aci_client.container_groups.get(
                    resource_group_name=str(resource_group.name),
                    container_group_name=group.name,
                )
                # 各コンテナーの詳細状態を確認
                container_states = []
                for container in getattr(cg, "containers", []):
                    instance_view = getattr(container, "instance_view", None)
                    if instance_view and hasattr(instance_view, "current_state"):
                        state = getattr(instance_view.current_state, "state", "")
                        if state:
                            container_states.append(state)
                # 優先度順でグループ全体の状態を判定
                # Pulling > Starting > Waiting > Running > Succeeded > Stopped > Failed > Unknown
                priority = [
                    "Pulling", "Starting", "Waiting", "Running", "Succeeded", "Stopped", "Failed", "Unknown"
                ]
                for p in priority:
                    if p in container_states:
                        group_status = p
                        break
                if not group_status and hasattr(cg, "instance_view") and cg.instance_view and hasattr(cg.instance_view, "state"):
                    group_status = cg.instance_view.state
            except Exception as e:
                settings.logger.warning(f"{group.name} のステータス取得に失敗: {e}")
            status_dict[group.name] = group_status
        settings.logger.info(f"コンテナーグループ一覧: {status_dict}")
    except exceptions.HttpResponseError as e:
        if e.status_code == 404:
            settings.logger.info(f"リソースグループがありません : {settings.AZURE_RESOURCE_GROUP_NAME}")
        else:
            settings.logger.exception(
                f"リソースグループにアクセスできません : {e.status_code}"
            )
            raise
    return status_dict


if __name__ == "__main__":
    status_dict = container_status_check()
    print(status_dict)