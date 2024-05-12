#!/usr/bin/env python3
'''
This script is used to install and setup the tools 
necessary for using your ubuntu server as a dns server.
'''

import subprocess


def run_command(command):
    ''' Run a shell command and handle exceptions. '''
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')
        return None

def setup_bind():
    ''' Install and setup bind9. '''
    print('Installing BIND...')
    result = run_command('sudo apt update && sudo apt install bind9 bind9utils bind9-doc -y')
    print(result)

def check_configuration():
    ''' Check the configuration of bind9. '''
    print('Checking BIND configuration...')

    result = run_command('sudo named-checkconf')

    # With named-checkconf, no return means your configuration is OK.
    if result:
        # When a failure happens you will be directed to check the journalctl logs.
        issues = run_command('sudo journalctl -xeu named.service')
        print(f'Configuration setup reported issues:\n{issues}')
    else:
        print('Configuration is OK.')

def setup_configuration_files():
    ''' Setup and install bind9. '''
    print('Configuring BIND...')

    # Define source and replacement directories.
    src_dir = '/etc/bind'
    rep_dir = 'configuration_files'

    # Create a dictionary of files to copy and replace.
    files = {
        '/etc/default/named': f'{rep_dir}/named',
        f'{src_dir}/named.conf.options': f'{rep_dir}/named.conf.options',
        f'{src_dir}/named.conf': f'{rep_dir}/named.conf',
    }

    # Backup and replace configuration files.
    for src, rep in files.items():
        result = run_command(f'sudo cp {src} {src}.bak && sudo mv {rep} {src}')
        print(result)

    # There's no logging file by default, so we need to create it here.
    log_cmd = run_command(f'mv {rep_dir}/named.conf.logging {src_dir}/named.conf.logging')
    print(log_cmd)

def create_log_files():
    ''' Create and set permissions for log files.'''
    # Define the log directory.
    log_dir = '/var/log/named'

    # Create the log file directory if it doesn't exist.
    result = run_command(f'sudo mkdir -p {log_dir}')
    print(result)

    # Define log files.
    log_files = ['default.log', 'query.log']

    # Create log files and set permissions.
    for log_file in log_files:
        cmd_result = run_command(
            f'sudo touch {log_dir}/{log_file} &&'
            f'sudo chown bind:bind {log_dir}/{log_file}'
            )
        print(cmd_result)

def restart_service():
    ''' Restart the bind9 service. '''
    restart = 'sudo systemctl restart bind9.service'
    status = 'sudo systemctl status bind9.service'
    result = run_command(f'{restart} && {status}')
    print(result)

def main():
    ''' Main function. '''
    setup_bind()
    check_configuration()
    setup_configuration_files()
    create_log_files()
    check_configuration()
    restart_service()


if __name__ == '__main__':
    main()