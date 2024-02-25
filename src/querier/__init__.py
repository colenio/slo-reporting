import dataclasses
from dataclasses import dataclass
import datetime
from json import JSONEncoder
import json

from azure.identity import DefaultAzureCredential
from azure.mgmt.alertsmanagement import AlertsManagementClient
from azure.mgmt.alertsmanagement.models import MonitorCondition
from prometheus_api_client import PrometheusConnect


@dataclass
class Alert:
    name: str
    description: str
    url: str
    startTimestamp: str


class AlertJsonEncoder(JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


class QuerierOrchestrator:
    def __init__(self, querierConfig):
        queriers = []
        # Create Azure queriers
        for azureConfig in querierConfig.azure:
            queriers.append(AzureQuerier(
                azureConfig.name,
                azureConfig.subscriptionID,
            ))

        for prometheusConfig in querierConfig.prometheus:
            queriers.append(PrometheusQuerier(
                prometheusConfig.name,
                prometheusConfig.url,
                prometheusConfig.user,
                prometheusConfig.password,
                prometheusConfig.ssl_verify,
                prometheusConfig.query
            ))
        self.queriers = queriers

    def execute(self):  # TODO: create Alert model
        alerts = []
        for querier in self.queriers:
            for alert in querier.query():
                alerts.append(alert)

        with open('alerts.json', 'w') as fp:
            json.dump(alerts, indent=2, cls=AlertJsonEncoder, fp=fp)


class Querier:
    def query(self):
        raise NotImplementedError("Please implement this method in a child-class")


class AzureQuerier(Querier):
    def __init__(self, name, subscriptionID):
        self.name = name
        self.resourceID = subscriptionID

    def query(self) -> list[Alert]:
        result = []

        # TODO: check handling in azure,identity. Will a new credential be created each run?
        credential = DefaultAzureCredential()
        client = AlertsManagementClient(
          credential=credential,
          subscription_id=self.resourceID,
        )

        response = client.alerts.get_all(monitor_condition=MonitorCondition.FIRED)
        for item in response:
            result.append(Alert(
                item.name,
                item.properties.essentials.additional_properties['description'],
                item.properties.essentials.alert_rule,
                item.properties.essentials.start_date_time
            ))

        print("Azure-Querier: " + self.name + " successfully queried")
        return result


class PrometheusQuerier(Querier):
    def __init__(self, name, url, user, password, ssl_verify, query):
        self.name = name
        self.queryString = query
        auth = (user, password)
        self.client = PrometheusConnect(url=url, auth=auth, disable_ssl=ssl_verify)

    def query(self) -> list[Alert]:
        result = []
        queryResults = self.client.custom_query(self.queryString)
        for queryResult in queryResults:
            #TODO: There's no description nor URL in prom ALERT metric. Those are only present in Alertmanager
            result.append(Alert(queryResult['metric']['alertname'], "", "", datetime.datetime.now()))

        print("Prom-Querier: " + self.name + " successfully queried")
        return result


