# BIND DNS Server Setup Guide

This README provides instructions on how to install BIND (Berkeley Internet Name Domain) on a headless Ubuntu server and configure it to log all DNS queries, which can help with monitoring your network.

## Prerequisites

- A headless Ubuntu Server (18.04 or later)
- sudo or root privileges

# Simple Installation

Give setup.py executable permissions:

\`\`\`bash
sudo chown +x setup.py
\`\`\`

Run the setup:

\`\`\`bash
./setup.py
\`\`\`

# Detailed installation alternative

## Step 1: Install BIND

First, update your package list and install BIND9:

\`\`\`bash
sudo apt update
sudo apt install bind9 bind9utils bind9-doc -y
\`\`\`

## Step 2: Configure BIND

Back up and then edit the \`/etc/default/named\` file:

\`\`\`bash
sudo cp /etc/default/named /etc/default/named.bak
sudo nano /etc/default/named
\`\`\`

Replace with the following for ipv4:

\`\`\`bash
#
# run resolvconf?
RESOLVCONF=no

# startup options for the server
OPTIONS="-u bind -4"
\`\`\`

Back up and then edit the \`/etc/bind/named.conf.options\` file:

\`\`\`bash
sudo cp /etc/bind/named.conf.options /etc/bind/named.conf.options.bak
sudo nano /etc/bind/named.conf.options
\`\`\`

Replace with the following:

\`\`\`bash
options {
        directory "/var/cache/bind";

        forwarders {
                8.8.8.8;
                8.8.4.4;
        };

        recursion yes;
        allow-query { any; };

        dnssec-validation auto;

        listen-on-v6 { any; };

        // Enable query logging.
        querylog yes;

};
\`\`\`

Create a new file called \`/etc/bind/named.conf.logging\`:

\`\`\`bash
sudo nano /etc/bind/named.conf.logging
\`\`\`

Add the following with the path to where logs should be stored:

\`\`\`bash
logging {
        channel default_log {
                file "/var/log/named/default.log";
                print-time local;
                print-category yes;
                print-severity yes;
                severity info;
        };

        channel query_log {
                file "/var/log/named/query.log";
                print-time local;
                print-category yes;
                print-severity yes;
                severity info;
        };

        category default { default_log; };
        category queries { query_log; };

};
\`\`\`

This configuration sets up log files in \`/var/log/named/\`, keep in mind that it must write logs to this location, anywhere else will cause service to fail.

Back up and then edit the \`/etc/bind/named.conf\` file, to use the new logging configuration:

\`\`\`bash
sudo cp /etc/bind/named.conf /etc/bind/named.conf.bak
sudo nano /etc/bind/named.conf
\`\`\`

Replace with the following:

\`\`\`bash
// This is the primary configuration file for the BIND DNS server named.
//
// Please read /usr/share/doc/bind9/README.Debian for information on the
// structure of BIND configuration files in Debian, *BEFORE* you customize
// this configuration file.
//
// If you are just adding zones, please do that in /etc/bind/named.conf.local

include "/etc/bind/named.conf.options";
include "/etc/bind/named.conf.local";
include "/etc/bind/named.conf.default-zones";
include "/etc/bind/named.conf.logging";
\`\`\`

## Step 3: Set Permissions for the Log File

Create the log file and set the appropriate permissions:

\`\`\`bash
sudo touch /var/log/named/default.log && sudo touch /var/log/named/query.log
sudo chown bind:bind /var/log/named/default.log && sudo chown bind:bind /var/log/named/query.log
\`\`\`

## Step 4: Restart BIND

To apply the changes, restart the BIND9 service:

\`\`\`bash
sudo systemctl restart bind9
\`\`\`

## Step 5: Configure the DNS Resolver

To make use of your new DNS server, configure your network settings to use the server's IP address as the primary DNS resolver. This configuration will depend on your network setup.

## Step 6: Verify the Configuration

Ensure that BIND is correctly logging DNS queries. You can check the log file with:

\`\`\`bash
tail -f /var/log/named/query.log
\`\`\`

This command will display logged queries in real-time. You should see entries appear as devices on your network make DNS requests.

## Troubleshooting

It's a good idea to check the configuration after each modification throughout this installation:

\`\`\`bash
sudo named-checkconf

If BIND is not starting or not logging queries as expected, check the BIND system log for errors:

\`\`\`bash
journalctl -u bind9
\`\`\`

Review any error messages for clues on what might be wrong with your configuration.
