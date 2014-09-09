zabbix_scripts
==============

This is a collection of scripts for use with Zabbix.

* zbxwmi
Connects to a Windows server using WMI to discover and collect WMI data. It uses Low-Level Discovery.
```
Usage:
  zbxwmi [-d] get <host> <item> <class> [-f <filter>] [-z <server>] [-D <domain>] [-U <username>] [-P <password] [-o <logfile>]
  zbxwmi [-d] (bulk|discover) <host> <keys> <items> <class> [-f <filter>] [-z <server>] [-D <domain>] [-U <username>] [-P <password] [-o <logfile>]
  zbxwmi [-d] <host> <keys> <items> <class> [-f <filter>] [-z <server>] [-D <domain>] [-U <username>] [-P <password] [-o <logfile>]
  zbxwmi --help
  zbxwmi --version
```
Actions:
get: query a specific WMI item.
```
zbxwmi get SVR1 FreeSpace "Win32_LogicalDisk" -f "MediaType = 12 AND Name = 'C:'"
4079554560
```

discover : outputs a JSON-formatted output for LLD discovery.
```
zbxwmi discover SVR1 Name Name,Size,FreeSpace "Win32_LogicalDisk" -f "MediaType = 12"
{
    "data": [
        {
            "{#WMIINDEX0}": "C:"
        },
        {
            "{#WMIINDEX0}": "D:"
        },
        {
            "{#WMIINDEX0}": "E:"
        }
    ]
}
```

bulk: bulk sends item values to Zabbix using the Zabbix sender protocol.
```
zbxwmi bulk SVR1 Name Name,Size,FreeSpace "Win32_LogicalDisk" -f "MediaType = 12"
```

both (default action): combines the discover and bulk actions to create the discovered items in Zabbix using LLD and get their values.
zbxwmi SVR1 Name Name,Size,FreeSpace "Win32_LogicalDisk" -f "MediaType = 12" -D MYDOMAIN -U wmiuser -P secret
{
    "data": [
        {
            "{#WMIINDEX0}": "C:"
        },
        {
            "{#WMIINDEX0}": "D:"
        },
        {
            "{#WMIINDEX0}": "E:"
        }
    ]
}
