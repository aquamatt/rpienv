# Extras

In this directory find the JSON export of a Grafana dashboard to use with
data from the InfluxDB power monitoring database.

You may need additional plugins such as the D3 Gauge plugin. To install you
need access to the Grafana server, then:

```
  $ grafana-cli plugins install briangann-gauge-panel
  $ service grafana-server restart
```
