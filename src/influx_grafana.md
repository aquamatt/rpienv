# Notes on configuring your InfluxDB/Grafana host

Influx cloud is great, but likely expensive. Linode, Digital Ocean and similar
offer VPSs at low cost which makes them a better bet for the poor-man's data
logger.

We like InfluxDB and Grafana at the moment. Your mileage may vary! These notes
are bullet points to help get things setup on an Ubuntu server.

## Install InfluxDB

Go to https://portal.influxdata.com/downloads and click on **InfluxDB**.
Log onto your host and copy/paste the instructions which are something like:

``` bash
  > wget https://dl.influxdata.com/influxdb/releases/influxdb_1.2.0_amd64.deb
  > sudo dpkg -i influxdb_1.2.0_amd64.deb
```

Version numbers will change.

If you find yourself missing some dependencies, dpkg will complain and you can
install all with:

``` bash
  > sudo apt-get install -f
```

which will install dependencies and finish installing InfluxDB. Type `influx`
at the prompt to start a local client and confirm that things are working.

Start with:

``` bash
  > systemctl start influxdb
```

### Configure

Works out of the box, though if you want SSL you need to create and install
a certificate.

You will need to create a database and, for that database, an admin user and,
possibly, a general user.

## Install Grafana

Grafana installation instructions are found here:
http://docs.grafana.org/installation/debian/ and you can install via apt.

Alternatively follow the downloads link in the header, get the package and
install with `dpkg -i`.

SystemD can setup and start grafana:

``` bash
  > systemctl daemon-reload
  > systemctl enable influxdb
  > systemctl start influxdb
```

### Configure

Works out of the box, though if you want SSL you need to create and install
a certificate.

Connect to http://<hostname>:3000/ to register and use.

The default admin user is 'admin', password 'admin'. Login as the admin, set
your new user to have admin rights, login as your user, and delete the default
admin account.

Once registered you may want to disable registration by setting `allow_sign_up
= False` in `/etc/grafana/grafana.ini`.
