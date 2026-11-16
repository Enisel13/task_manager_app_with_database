# Answer to Task 4: Troubleshooting Scenario

I would investigate the connection timeout step by step, starting with database availability and network connectivity. I would gather evidence before making any changes.

## 1. Check database availability and connectivity

- Verify that the database is running and listening on the expected port.
- Check that the hostname or IP address and port are correct.
- Test network connectivity between the application and database servers.
- Check firewall and NSG rules to ensure the connection is allowed.

For a self-hosted database on Linux:

```sh
sudo systemctl status mysql
sudo ss -lntp | grep ':3306'
```

To test network connectivity:

```sh
nc -vz DATABASE_IP 3306
```

## 2. Check resources and logs

- Check database CPU, memory, and connection usage.
- Review application and database logs for errors.

For a self-hosted database on Linux:

```sh
top
free -h
df -h
```