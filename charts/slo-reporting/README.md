# slo-reporting

![Version: 0.3.18](https://img.shields.io/badge/Version-0.3.18-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.3.18](https://img.shields.io/badge/AppVersion-0.3.18-informational?style=flat-square)

Excel compatible SLO reporting tool for Prometheus / Pyrra.

**Homepage:** <https://github.com/colenio/slo-reporting>

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| Colenio | <support@colenio.com> | <https://colenio.com> |

## Source Code

* <https://github.com/colenio/slo-reporting>

## Requirements

Kubernetes: `>= 1.26.3`

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| autoscaling.enabled | bool | `false` | Enable auto scaling via [HPA](https://docs.microsoft.com/en-us/azure/aks/tutorial-kubernetes-scale#autoscale-pods) |
| autoscaling.maxReplicas | int | `4` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| autoscaling.targetMemoryUtilizationPercentage | int | `80` |  |
| config.metrics.bucket.name | string | `"slo-reports"` | Azure File Share to store slo reports |
| config.metrics.bucket.output | string | `"slo-reporting.csv"` | Path to the archive file |
| config.metrics.bucket.path | string | `"/app/data"` | Mount path in pod |
| config.metrics.bucket.secretName | string | `"slo-reporting"` | Name of pre-existing Secret for Azure Storage to use |
| config.metrics.bucket.type | string | `"azure"` | Type of bucket to use (azure, gcs, s3) |
| config.metrics.cronjob.enabled | bool | `true` | Should the export-metrics job be enabled |
| config.metrics.cronjob.schedule | string | `"@daily"` | The cronjob schedule for running the export-metrics job (default: nightly at 2AM) |
| config.metrics.enabled | bool | `true` | Should SLO reports be generated from configured SLOs |
| config.metrics.objectives | list | `[{"goal":99.9,"name":"prometheus-uptime","query":"100 * avg(avg_over_time(up{job=~\"prometheus.*\"}[5m]))"},{"goal_query":"100 * pyrra_objective","name":"slo","query":"100 * pyrra_availability"}]` | List of SLOs to report on |
| config.metrics.objectives[0].goal | float | `99.9` | The goal of the SLO in percentage |
| config.metrics.objectives[0].query | string | `"100 * avg(avg_over_time(up{job=~\"prometheus.*\"}[5m]))"` | Prometheus query to evaluate |
| config.metrics.objectives[1] | object | `{"goal_query":"100 * pyrra_objective","name":"slo","query":"100 * pyrra_availability"}` | [Pyrra](https://github.com/pyrra-dev/pyrra) Example, `slo` is the metric-label |
| config.metrics.prometheus.url | string | `"http://prometheus-community-kube-prometheus.observability:9090"` | Prometheus URL to query |
| config.metrics.step | string | `"P1D"` | In what granularity (step-size) should SLOs be reported |
| config.metrics.window | string | `"P30D"` | Evaluation window for SLOs |
| config.status.enabled | bool | `true` | Should a status API be created which aggregates alerts from multiple sources? |
| config.status.interval | string | `"PT1M"` | Scrape interval of alert sources |
| config.status.monitors | object | `{"alertmanager":[{"active":true,"filters":["severity=critical","relevance=health-status"],"inhibited":false,"name":"alertmanager-project1","receiver":".*","silenced":false,"unprocessed":false,"url":"http://alertmanager-operated.observability:9093/api/v2/alerts"}],"azure":[{"name":"azure-project-1","subscription_id":"XXXXXX-XXXX-XXXXXX-XXXX-XXXXXX"}],"prometheus":[{"name":"prometheus-project-1","query":"ALERTS{alertstate=\"firing\", severity=\"critical\", relevance=\"health-status\"}","url":"http://prometheus-operated.observability:9090"}]}` | List of alert monitors to aggregate |
| config.status.monitors.alertmanager | list | `[{"active":true,"filters":["severity=critical","relevance=health-status"],"inhibited":false,"name":"alertmanager-project1","receiver":".*","silenced":false,"unprocessed":false,"url":"http://alertmanager-operated.observability:9093/api/v2/alerts"}]` | List of a Alertmanager Monitors |
| config.status.monitors.alertmanager[0] | object | `{"active":true,"filters":["severity=critical","relevance=health-status"],"inhibited":false,"name":"alertmanager-project1","receiver":".*","silenced":false,"unprocessed":false,"url":"http://alertmanager-operated.observability:9093/api/v2/alerts"}` | An example of an Alertmanager monitor |
| config.status.monitors.alertmanager[0].filters | list | `["severity=critical","relevance=health-status"]` | List of filters to apply, cf. [AlertManager OpenAPI](https://github.com/prometheus/alertmanager/blob/main/api/v2/openapi.yaml) |
| config.status.monitors.alertmanager[0].url | string | `"http://alertmanager-operated.observability:9093/api/v2/alerts"` | Alertmanager URL to query |
| config.status.monitors.azure | list | `[{"name":"azure-project-1","subscription_id":"XXXXXX-XXXX-XXXXXX-XXXX-XXXXXX"}]` | List of Azure Monitors |
| config.status.monitors.azure[0] | object | `{"name":"azure-project-1","subscription_id":"XXXXXX-XXXX-XXXXXX-XXXX-XXXXXX"}` | An example of an Azure monitor |
| config.status.monitors.azure[0].subscription_id | string | `"XXXXXX-XXXX-XXXXXX-XXXX-XXXXXX"` | Azure Subscription ID |
| config.status.monitors.prometheus | list | `[{"name":"prometheus-project-1","query":"ALERTS{alertstate=\"firing\", severity=\"critical\", relevance=\"health-status\"}","url":"http://prometheus-operated.observability:9090"}]` | List of Prometheus Monitors |
| config.status.monitors.prometheus[0] | object | `{"name":"prometheus-project-1","query":"ALERTS{alertstate=\"firing\", severity=\"critical\", relevance=\"health-status\"}","url":"http://prometheus-operated.observability:9090"}` | An example of a Prometheus monitor |
| config.status.monitors.prometheus[0].query | string | `"ALERTS{alertstate=\"firing\", severity=\"critical\", relevance=\"health-status\"}"` | Prometheus query to evaluate |
| config.status.monitors.prometheus[0].url | string | `"http://prometheus-operated.observability:9090"` | Prometheus URL to query |
| config.ui.about.links[0].icon | string | `"fa-brands fa-github"` |  |
| config.ui.about.links[0].name | string | `"colenio/slo-reporting"` |  |
| config.ui.about.links[0].url | string | `"https://github.com/colenio/slo-reporting"` |  |
| config.ui.icons.brand | string | `"/static/img/brand.png"` |  |
| config.ui.icons.favicon | string | `"/static/favico.png"` |  |
| config.ui.slo.links[0].icon | string | `"https://raw.githubusercontent.com/pyrra-dev/pyrra/main/ui/public/favicon.ico"` |  |
| config.ui.slo.links[0].name | string | `"Pyrra"` |  |
| config.ui.slo.links[0].url | string | `"http://localhost:9099"` |  |
| config.ui.slo.links[1].icon | string | `"https://raw.githubusercontent.com/prometheus/docs/main/static/favicon.ico"` |  |
| config.ui.slo.links[1].name | string | `"Prometheus"` |  |
| config.ui.slo.links[1].url | string | `"http://localhost:9090"` |  |
| config.ui.slo.links[2].icon | string | `"https://raw.githubusercontent.com/grafana/grafana/main/public/img/fav32.png"` |  |
| config.ui.slo.links[2].name | string | `"Grafana"` |  |
| config.ui.slo.links[2].url | string | `"http://localhost:3000"` |  |
| config.ui.slo.templates[0].name | string | `"Pyrra"` |  |
| config.ui.slo.templates[0].template | string | `"http://localhost:9099/objectives?expr={{__name__='{name}'}}"` |  |
| config.ui.slo.templates[1].name | string | `"Grafana"` |  |
| config.ui.slo.templates[1].template | string | `"http://localhost:3000/d/pyrra-detail/pyrra-detail?var-slo={name}"` |  |
| config.ui.status.links[0].icon | string | `"https://raw.githubusercontent.com/grafana/grafana/main/public/img/fav32.png"` |  |
| config.ui.status.links[0].name | string | `"Grafana"` |  |
| config.ui.status.links[0].url | string | `"http://localhost:3000"` |  |
| config.ui.status.links[1].icon | string | `"https://raw.githubusercontent.com/prometheus/alertmanager/main/ui/app/favicon.ico"` |  |
| config.ui.status.links[1].name | string | `"Alertmanager"` |  |
| config.ui.status.links[1].url | string | `"http://localhost:9093"` |  |
| env | object | `{}` |  |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"ghcr.io/colenio/slo-reporting"` | The image repository to pull from |
| image.tag | string | `""` | Overrides the image tag whose default is the chart appVersion. |
| imagePullSecrets | list | `[]` |  |
| ingress.api.annotations | object | `{}` |  |
| ingress.api.className | string | `""` |  |
| ingress.api.enabled | bool | `false` | Enable API Ingress |
| ingress.api.hosts | list | `[]` |  |
| ingress.api.tls | list | `[]` |  |
| ingress.ui.annotations | object | `{}` |  |
| ingress.ui.className | string | `""` |  |
| ingress.ui.enabled | bool | `false` | Enable UI Ingress |
| ingress.ui.hosts | list | `[]` |  |
| ingress.ui.tls | list | `[]` |  |
| metrics.enabled | bool | `true` | Enable Prometheus metrics |
| metrics.serviceMonitor.additionalLabels | list | `[]` |  |
| metrics.serviceMonitor.enabled | bool | `true` | Enable a [ServiceMonitor](https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/api.md#servicemonitorspec) |
| metrics.serviceMonitor.honorLabels | bool | `false` |  |
| metrics.serviceMonitor.jobLabel | string | `""` |  |
| metrics.serviceMonitor.metricRelabelings | list | `[]` |  |
| metrics.serviceMonitor.namespace | string | `""` |  |
| metrics.serviceMonitor.namespaceSelector | object | `{}` |  |
| metrics.serviceMonitor.relabelings | list | `[]` |  |
| metrics.serviceMonitor.scrapeInterval | string | `"30s"` |  |
| metrics.serviceMonitor.targetLabels | list | `[]` |  |
| nameOverride | string | `""` |  |
| podAnnotations | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| securityContext | object | `{}` |  |
| service | object | `{"port":8000,"type":"ClusterIP"}` | Networking |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `false` |  |
| serviceAccount.name | string | `""` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
