import os
import sys
import logging
from logging import Logger, LoggerAdapter

from decouple import AutoConfig, config

# .envファイルが存在するパスを指定
# config = AutoConfig(search_path="./shared")

# タイムゾーン
TIME_ZONE: str = str(config("TIME_ZONE", default="Asia/Tokyo"))

# azure共通設定
AZURE_SUBSCRIPTION_ID: str = str(config("AZURE_SUBSCRIPTION_ID"))
AZURE_RESOURCE_GROUP_NAME: str = str(config("AZURE_RESOURCE_GROUP_NAME"))
AZURE_LOCATION: str = str(config("AZURE_LOCATION"))

# コンテナーグループ設定
ACI_GROUP_CONTAINER_GROUP_NAME: str = str(
    config("ACI_GROUP_CONTAINER_GROUP_NAME", default="BrownieAtelierGrp")
)

###########################
# MongoDBコンテナー設定
###########################
CONTAINER_MONGO__CONTAINER_GROUP_NAME: str = str(
    config("CONTAINER_MONGO__CONTAINER_GROUP_NAME", default="BrownieAtelierMongo")
)
##################################
# BrownieAtelierNewsCrawlerコンテナー設定
##################################
CONTAINER_NEWS_CRAWLER__CONTAINER_GROUP_NAME: str = str(
    config("CONTAINER_NEWS_CRAWLER__CONTAINER_GROUP_NAME", default="BrownieAtelierNewsCrawler")
)  # news crawlerの自動操作版
CONTAINER_NEWS_CRAWLER__CONTAINER_GROUP_NAME__MANUAL: str = str(
    config(
        "CONTAINER_NEWS_CRAWLER__CONTAINER_GROUP_NAME__MANUAL", default="BrownieAtelierNewsCrawlerManual"
    )
)  # news crawlerのマニュアル操作版

###########################
# loggerを定義
###########################
logger: Logger = logging.getLogger("BrownieAtelierResourceCheck")

logger.setLevel(str(config("BROWNIE_ATELIER_MONGO__LOG_LEVEL", default="INFO")))
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
format = "%(asctime)s %(levelname)s [%(name)s] : %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
handler.setFormatter(logging.Formatter(fmt=format, datefmt=datefmt))
