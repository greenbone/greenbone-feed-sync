![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)

# greenbone-feed-sync <!-- omit in toc -->

New script for downloading the Greenbone Community Feed

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Install using pipx](#install-using-pipx)
  - [Install using pip](#install-using-pip)
- [Usage](#usage)
- [Usage on Kali Linux](#usage-on-kali-linux)
- [Settings](#settings)
  - [verbose](#verbose)
  - [quiet](#quiet)
  - [config](#config)
  - [private-directory](#private-directory)
  - [compression-level](#compression-level)
  - [type](#type)
  - [feed-url](#feed-url)
  - [destination-prefix](#destination-prefix)
  - [gvmd-data-destination](#gvmd-data-destination)
  - [gvmd-data-url](#gvmd-data-url)
  - [notus-destination](#notus-destination)
  - [notus-url](#notus-url)
  - [nasl-destination](#nasl-destination)
  - [nasl-url](#nasl-url)
  - [scap-data-destination](#scap-data-destination)
  - [scap-data-url](#scap-data-url)
  - [cert-data-destination](#cert-data-destination)
  - [cert-data-url](#cert-data-url)
  - [report-formats-destination](#report-formats-destination)
  - [report-formats-url](#report-formats-url)
  - [scan-configs-destination](#scan-configs-destination)
  - [scan-configs-url](#scan-configs-url)
  - [port-lists-destination](#port-lists-destination)
  - [port-lists-url](#port-lists-url)
  - [gvmd-lock-file](#gvmd-lock-file)
  - [openvas-lock-file](#openvas-lock-file)
  - [fail-fast](#fail-fast)
  - [no-wait](#no-wait)
  - [wait-interval](#wait-interval)
  - [rsync-timeout](#rsync-timeout)
  - [group](#group)
  - [user](#user)
  - [greenbone-enterprise-feed-key](#greenbone-enterprise-feed-key)
- [Config](#config-1)
- [Development](#development)
- [Maintainer](#maintainer)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Requirements

Python 3.9 and later is supported.

`greenbone-feed-sync` requires the `rsync` tool being installed and available
within the `PATH`.

On Debian based Distributions like Ubuntu and Kali `rsync` can be installed via

    sudo apt install rsync

### Install using pipx

You can install the latest release of **greenbone-feed-sync** from the Python
Package Index (pypi) using [pipx]

    python3 -m pipx install greenbone-feed-sync

On Debian based Distributions like Ubuntu and Kali `pipx` itself can be
installed via

    sudo apt install pipx

### Install using pip

**NOTE:** The `pip install` command does no longer work out-of-the-box in newer
distributions like Ubuntu 23.04 or Debian 12 because of [PEP 668](https://peps.python.org/pep-0668).
Please use the [installation via pipx](#install-using-pipx) instead.

You can install the latest release of **greenbone-feed-sync** from the
Python Package Index ([pypi]) using [pip]

    python3 -m pip install greenbone-feed-sync

## Usage

Most of the time you should just run the script without any arguments to
download the new data for all necessary feed types

**NOTE:** See details about [usage on Kali Linux](#usage-on-kali-linux)

    sudo greenbone-feed-sync

To get verbose progress output during the data download you might increase the
verbosity

    sudo greenbone-feed-sync -vvv


If the script is run in a cron job the output can be turned off via

    sudo greenbone-feed-sync --quiet


To download only a specific feed content the `--type` argument can be used

    sudo greenbone-feed-sync --type nvt

Run `--help` to get information about all possible types and additional argument
options

    greenbone-feed-sync --help

## Usage on Kali Linux

When running `greenbone-feed-sync` as root user, for example via sudo, the
actual user and group of the process are changed to the `gvm` user and group via
[seteuid](https://docs.python.org/3/library/os.html#os.seteuid). This is done to
ensure that [`gvmd`](https://github.com/greenbone/gvmd) and
[`openvas-scanner`](https://github.com/greenbone/openvas-scanner) can read the
downloaded file contents.

When using the Greenbone Community Edition installed via packages on Kali Linux
a different user and group are used. They are both named `_gvm` instead.
Therefore the [group](#group) and [user](#user) settings need to be adjusted.
This can be done by using a [config file](#config-1).

    sudo mkdir /etc/gvm
    sudo chmod +r /etc/gvm
    cat <<EOF | sudo tee /etc/gvm/greenbone-feed-sync.toml
    [greenbone-feed-sync]
    user="_gvm"
    group="_gvm"
    EOF
    sudo chmod +r /etc/gvm/greenbone-feed-sync.toml

## Settings

The `greenbone-feed-sync` script is adjustable for all kind of purposes and very
flexible which content gets downloaded. Most likely you will never need to
adjust the settings because the defaults will suffice. Changing the settings
is only required for experts and testing purposes.

### verbose

| Name                 | Value                                        |
| -------------------- | -------------------------------------------- |
| CLI Argument         | `--verbose, -v`                              |
| Config Variable      | verbose                                      |
| Environment Variable | `GREENBONE_FEED_SYNC_VERBOSE`                |
| Default Value        | 2                                            |
| Description          | Log verbosity. `-vvv` for maximum verbosity. |

### quiet

| Name                 | Value                                                                                    |
| -------------------- | ---------------------------------------------------------------------------------------- |
| CLI Argument         | `--quiet`                                                                                |
| Config Variable      |                                                                                          |
| Environment Variable |                                                                                          |
| Default Value        |                                                                                          |
| Description          | Disable all log output. Same as setting `verbose` or  `GREENBONE_FEED_SYNC_VERBOSE` to 0 |

### config

| Name                 | Value                                                                        |
| -------------------- | ---------------------------------------------------------------------------- |
| CLI Argument         | `--config, -c`                                                               |
| Config Variable      |                                                                              |
| Environment Variable |                                                                              |
| Default Value        | `~/.config/greenbone-feed-sync.toml` and `/etc/gvm/greenbone-feed-sync.toml` |
| Description          | TOML config file to load settings from.                                      |

### private-directory

| Name                 | Value                                                                                |
| -------------------- | ------------------------------------------------------------------------------------ |
| CLI Argument         | `--private-directory`                                                                |
| Config Variable      | private-directory                                                                    |
| Environment Variable | `GREENBONE_FEED_SYNC_PRIVATE_DIRECTORY`                                              |
| Default Value        |                                                                                      |
| Description          | (Sub-)Directory to exclude from the sync which will never get deleted automatically. |

### compression-level

| Name                 | Value                                                                   |
| -------------------- | ----------------------------------------------------------------------- |
| CLI Argument         | `--compression-level`                                                   |
| Config Variable      | compression-level                                                       |
| Environment Variable | `GREENBONE_FEED_SYNC_COMPRESSION_LEVEL`                                 |
| Default Value        | 9                                                                       |
| Description          | rsync compression level 0-9. (0 - no compression, 9 - high compression) |

### type

| Name                 | Value                                                                                                                                                                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLI Argument         | `--type`                                                                                                                                                                                                                           |
| Config Variable      |                                                                                                                                                                                                                                    |
| Environment Variable |                                                                                                                                                                                                                                    |
| Default Value        | all                                                                                                                                                                                                                                |
| Description          | Specifies which feed data should be downloaded. Possible values are `all`, `nvt`/`nvts`, `gvmd-data`, `scap`, `cert`, `notus`, `nasl`, `report-format`/`report-formats`, `scan-config`/`scan-configs` or `port-list`/`port-lists`. |

### feed-url

| Name                 | Value                                                                                                                                                                                                                            |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLI Argument         |                                                                                                                                                                                                                                  |
| Config Variable      | feed-url                                                                                                                                                                                                                         |
| Environment Variable | `GREENBONE_FEED_SYNC_URL`                                                                                                                                                                                                        |
| Default Value        | `rsync://feed.community.greenbone.net/community`                                                                                                                                                                                 |
| Description          | URL to download the feed data from. Other URLs will be relative to this URL by default. For example using `rsync://example.com` as feed url the notus url will be `rsync://example.com/vulnerability-feed/22.04/vt-data/notus/`. |

### destination-prefix

| Name                 | Value                                                                                                                                                                                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLI Argument         |                                                                                                                                                                                                                                                                     |
| Config Variable      | destination-prefix                                                                                                                                                                                                                                                  |
| Environment Variable | `GREENBONE_FEED_SYNC_DESTINATION_PREFIX`                                                                                                                                                                                                                            |
| Default Value        | `/var/lib/`                                                                                                                                                                                                                                                         |
| Description          | Directory prefix to use for default feed data download destinations. Other download destinations will be relative to this path by default. For example using `/opt/lib` as destination prefix will change the default of the notus destination to `/opt/lib/notus`. |

### gvmd-data-destination

| Name                 | Value                                       |
| -------------------- | ------------------------------------------- |
| CLI Argument         | `--gvmd-data-destination`                   |
| Config Variable      | gvmd-data-destination                       |
| Environment Variable | `GREENBONE_FEED_SYNC_GVMD_DATA_DESTINATION` |
| Default Value        | `/var/lib/gvm/data-objects/gvmd/22.04/`     |
| Description          | Destination of the downloaded gvmd data.    |

### gvmd-data-url

| Name                 | Value                                                                                          |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| CLI Argument         | `--gvmd-data-url`                                                                              |
| Config Variable      | gvmd-data-url                                                                                  |
| Environment Variable | `GREENBONE_FEED_SYNC_GVMD_DATA_URL`                                                            |
| Default Value        | `rsync://feed.community.greenbone.net/community/data-feed/22.04/`                              |
| Description          | URL to download the gvmd data from. This includes scan-configs, report-formats and port-lists. |

### notus-destination

| Name                 | Value                                     |
| -------------------- | ----------------------------------------- |
| CLI Argument         | `--notus-destination`                     |
| Config Variable      | notus-destination                         |
| Environment Variable | `GREENBONE_FEED_SYNC_NOTUS_DESTINATION`   |
| Default Value        | `/var/lib/notus`                          |
| Description          | Destination of the downloaded notus data. |

### notus-url

| Name                 | Value                                                                                    |
| -------------------- | ---------------------------------------------------------------------------------------- |
| CLI Argument         | `--notus-url`                                                                            |
| Config Variable      | notus-url                                                                                |
| Environment Variable | `GREENBONE_FEED_SYNC_NOTUS_URL`                                                          |
| Default Value        | `rsync://feed.community.greenbone.net/community/vulnerability-feed/22.04/vt-data/notus/` |
| Description          | URL to download the notus data from.                                                     |

### nasl-destination

| Name                 | Value                                    |
| -------------------- | ---------------------------------------- |
| CLI Argument         | `--nasl-destination`                     |
| Config Variable      | nasl-destination                         |
| Environment Variable | `GREENBONE_FEED_SYNC_NASL_DESTINATION`   |
| Default Value        | `/var/lib/openvas/plugins`               |
| Description          | Destination of the downloaded nasl data. |

### nasl-url

| Name                 | Value                                                                                   |
| -------------------- | --------------------------------------------------------------------------------------- |
| CLI Argument         | `--nasl-url`                                                                            |
| Config Variable      | nasl-url                                                                                |
| Environment Variable | `GREENBONE_FEED_SYNC_NASL_URL`                                                          |
| Default Value        | `rsync://feed.community.greenbone.net/community/vulnerability-feed/22.04/vt-data/nasl/` |
| Description          | URL to download the nasl data from.                                                     |

### scap-data-destination

| Name                 | Value                                       |
| -------------------- | ------------------------------------------- |
| CLI Argument         | `--scap-data-destination`                   |
| Config Variable      | scap-data-destination                       |
| Environment Variable | `GREENBONE_FEED_SYNC_SCAP_DATA_DESTINATION` |
| Default Value        | `/var/lib/gvm/scap-data`                    |
| Description          | Destination of the downloaded SCAP data.    |

### scap-data-url

| Name                 | Value                                                                               |
| -------------------- | ----------------------------------------------------------------------------------- |
| CLI Argument         | `--scap-data-url`                                                                   |
| Config Variable      | scap-data-url                                                                       |
| Environment Variable | `GREENBONE_FEED_SYNC_SCAP_DATA_URL`                                                 |
| Default Value        | `rsync://feed.community.greenbone.net/community/vulnerability-feed/22.04/scap-data` |
| Description          | URL to download the SCAP data from.                                                 |

### cert-data-destination

| Name                 | Value                                       |
| -------------------- | ------------------------------------------- |
| CLI Argument         | `--cert-data-destination`                   |
| Config Variable      | cert-data-destination                       |
| Environment Variable | `GREENBONE_FEED_SYNC_CERT_DATA_DESTINATION` |
| Default Value        | `/var/lib/gvm/cert-data`                    |
| Description          | Destination of the downloaded CERT data.    |

### cert-data-url

| Name                 | Value                                                                               |
| -------------------- | ----------------------------------------------------------------------------------- |
| CLI Argument         | `--cert-data-url`                                                                   |
| Config Variable      | cert-data-url                                                                       |
| Environment Variable | `GREENBONE_FEED_SYNC_CERT_DATA_URL`                                                 |
| Default Value        | `rsync://feed.community.greenbone.net/community/vulnerability-feed/22.04/cert-data` |
| Description          | URL to download the CERT data from.                                                 |

### report-formats-destination

| Name                 | Value                                                 |
| -------------------- | ----------------------------------------------------- |
| CLI Argument         | `--report-formats-destination`                        |
| Config Variable      | report-formats-destination                            |
| Environment Variable | `GREENBONE_FEED_SYNC_REPORT_FORMATS_DESTINATION`      |
| Default Value        | `/var/lib/gvm/data-objects/gvmd/22.04/report-formats` |
| Description          | Destination of the downloaded report format data.     |

### report-formats-url

| Name                 | Value                                                                           |
| -------------------- | ------------------------------------------------------------------------------- |
| CLI Argument         | `--report-formats-url`                                                          |
| Config Variable      | report-formats-url                                                              |
| Environment Variable | `GREENBONE_FEED_SYNC_REPORT_FORMATS_URL`                                        |
| Default Value        | `rsync://feed.community.greenbone.net/community/data-feed/22.04/report-formats` |
| Description          | URL to download the report format data from.                                    |

### scan-configs-destination

| Name                 | Value                                               |
| -------------------- | --------------------------------------------------- |
| CLI Argument         | `--scan-configs-destination`                        |
| Config Variable      | scan-configs-destination                            |
| Environment Variable | `GREENBONE_FEED_SYNC_SCAN_CONFIGS_DESTINATION`      |
| Default Value        | `/var/lib/gvm/data-objects/gvmd/22.04/scan-configs` |
| Description          | Destination of the downloaded scan config data.     |

### scan-configs-url

| Name                 | Value                                                                         |
| -------------------- | ----------------------------------------------------------------------------- |
| CLI Argument         | `--scan-configs-url`                                                          |
| Config Variable      | scan-configs-url                                                              |
| Environment Variable | `GREENBONE_FEED_SYNC_SCAN_CONFIGS_URL`                                        |
| Default Value        | `rsync://feed.community.greenbone.net/community/data-feed/22.04/scan-configs` |
| Description          | URL to download the scan config data from.                                    |

### port-lists-destination

| Name                 | Value                                             |
| -------------------- | ------------------------------------------------- |
| CLI Argument         | `--port-lists-destination`                        |
| Config Variable      | port-lists-destination                            |
| Environment Variable | `GREENBONE_FEED_SYNC_PORT_LISTS_DESTINATION`      |
| Default Value        | `/var/lib/gvm/data-objects/gvmd/22.04/port-lists` |
| Description          | Destination of the downloaded port list data.     |

### port-lists-url

| Name                 | Value                                                                       |
| -------------------- | --------------------------------------------------------------------------- |
| CLI Argument         | `--port-lists-url`                                                          |
| Config Variable      | port-lists-url                                                              |
| Environment Variable | `GREENBONE_FEED_SYNC_PORT_LISTS_URL`                                        |
| Default Value        | `rsync://feed.community.greenbone.net/community/data-feed/22.04/port-lists` |
| Description          | URL to download the port list data from.                                    |

### gvmd-lock-file

| Name                 | Value                                                                                                                                                                  |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLI Argument         | `--gvmd-lock-file`                                                                                                                                                     |
| Config Variable      | gvmd-lock-file                                                                                                                                                         |
| Environment Variable | `GREENBONE_FEED_SYNC_GVMD_LOCK_FILE`                                                                                                                                   |
| Default Value        | `/var/lib/gvm/feed-update.lock`                                                                                                                                        |
| Description          | File to use for locking the feed synchronization for data loaded by the gvmd daemon. Used to avoid that more then one process accesses the feed data at the same time. |

### openvas-lock-file

| Name                 | Value                                                                                                                                                                      |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLI Argument         | `--openvas-lock-file`                                                                                                                                                      |
| Config Variable      | openvas-lock-file                                                                                                                                                          |
| Environment Variable | `GREENBONE_FEED_SYNC_OPENVAS_LOCK_FILE`                                                                                                                                    |
| Default Value        | `/var/lib/openvas/feed-update.lock`                                                                                                                                        |
| Description          | File to use for locking the feed synchronization for data loaded by the openvas scanner. Used to avoid that more then one process accesses the feed data at the same time. |

### fail-fast

| Name                 | Value                                                                                                       |
| -------------------- | ----------------------------------------------------------------------------------------------------------- |
| CLI Argument         | `--fail-fast, --failfast`                                                                                   |
| Config Variable      | fail-fast                                                                                                   |
| Environment Variable | `GREENBONE_FEED_SYNC_FAIL_FAST`                                                                             |
| Default Value        | false                                                                                                       |
| Description          | Stop after a first error has occurred. Otherwise the script tries to download additional data if specified. |

### no-wait

| Name                 | Value                                             |
| -------------------- | ------------------------------------------------- |
| CLI Argument         | `--no-wait`                                       |
| Config Variable      | no-wait                                           |
| Environment Variable | `GREENBONE_FEED_SYNC_NO_WAIT`                     |
| Default Value        | false                                             |
| Description          | Fail directly if the lock file can't be acquired. |

### wait-interval

| Name                 | Value                                                                                |
| -------------------- | ------------------------------------------------------------------------------------ |
| CLI Argument         | `--wait-interval`                                                                    |
| Config Variable      | wait-interval                                                                        |
| Environment Variable | `GREENBONE_FEED_SYNC_LOCK_WAIT_INTERVAL`                                             |
| Default Value        | 5                                                                                    |
| Description          | Time to wait in seconds after failed lock attempt before re-trying to lock the file. |

### rsync-timeout

| Name                 | Value                                                                                                                                                                                  |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLI Argument         | `--rsync-timeout`                                                                                                                                                                      |
| Config Variable      | rsync-timeout                                                                                                                                                                          |
| Environment Variable | `GREENBONE_FEED_SYNC_RSYNC_TIMEOUT`                                                                                                                                                    |
| Default Value        |                                                                                                                                                                                        |
| Description          | Maximum I/O timeout in seconds used for rsync. If no data is transferred for the specified time then rsync will exit. By default no timeout is set and the rsync default will be used. |

### group

| Name                 | Value                                                                                                      |
| -------------------- | ---------------------------------------------------------------------------------------------------------- |
| CLI Argument         | `--group`                                                                                                  |
| Config Variable      | group                                                                                                      |
| Environment Variable | `GREENBONE_FEED_SYNC_GROUP`                                                                                |
| Default Value        | gvm                                                                                                        |
| Description          | If the greenbone-feed-sync script is run as root, the effective group is changed to this group name or ID. |

### user

| Name                 | Value                                                                                                    |
| -------------------- | -------------------------------------------------------------------------------------------------------- |
| CLI Argument         | `--user`                                                                                                 |
| Config Variable      | user                                                                                                     |
| Environment Variable | `GREENBONE_FEED_SYNC_USER`                                                                               |
| Default Value        | gvm                                                                                                      |
| Description          | If the greenbone-feed-sync script is run as root, the effective user is changed to this user name or ID. |

### greenbone-enterprise-feed-key

| Name                 | Value                                                                                                                                                                                                                                                                                                                                                                                                                 |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLI Argument         | `--greenbone-enterprise-feed-key`                                                                                                                                                                                                                                                                                                                                                                                     |
| Config Variable      | greenbone-enterprise-feed-key                                                                                                                                                                                                                                                                                                                                                                                         |
| Environment Variable | `GREENBONE_FEED_SYNC_ENTERPRISE_FEED_KEY`                                                                                                                                                                                                                                                                                                                                                                             |
| Default Value        | /etc/gvm/greenbone-enterprise-feed-key                                                                                                                                                                                                                                                                                                                                                                                |
| Description          | File to read the Greenbone Enterprise Feed key from. The key gives access to additional vulnerability tests for enterprise software among other advantages. See [Greenbone Enterprise Feed and Greenbone Community Feed in Comparison](https://www.greenbone.net/en/feed-comparison/) for more details. The default URLs are adjusted according to the data in the key. If the key file does not exist it is ignored. |

## Config

It is possible to use a config file for loading the settings of the
`greenbone-feed-sync` script. The config file uses the [TOML] format. Without
explicitly passing a config file, `greenbone-feed-sync` tries to load
`~/.config/greenbone-feed-sync.toml` and if that file doesn't exist afterwards
`/etc/gvm/greenbone-feed-sync.toml`.

Example:

```toml
[greenbone-feed-sync]
destination-prefix = "/opt/greenbone-feed"
lock-file = "/opt/greenbone-feed.lock"
no-wait = true
```

## Development

**greenbone-feed-sync** uses [poetry] for its own dependency management and
build process.

First install poetry via pipx

    python3 -m pipx install poetry

Afterwards run

    poetry install

in the checkout directory of **greenbone-feed-sync** (the directory containing
the `pyproject.toml` file) to install all dependencies including the packages
only required for development.

Afterwards activate the git hooks for auto-formatting and linting via
[autohooks].

    poetry run autohooks activate

Validate the activated git hooks by running

    poetry run autohooks check

## Maintainer

This project is maintained by [Greenbone AG][Greenbone Networks]

## Contributing

Your contributions are highly appreciated. Please
[create a pull request](https://github.com/greenbone/greeenbon-feed-sync/pulls)
on GitHub. Bigger changes need to be discussed with the development team via the
[issues section at GitHub](https://github.com/greenbone/greenbone-feed-sync/issues)
first.

## License

Copyright (C) 2022-2024 [Greenbone AG][Greenbone Networks]

Licensed under the [GNU General Public License v3.0 or later](LICENSE).

[Greenbone Networks]: https://www.greenbone.net/
[poetry]: https://python-poetry.org/
[pip]: https://pip.pypa.io/
[pipx]: https://pypa.github.io/pipx/
[autohooks]: https://github.com/greenbone/autohooks
[TOML]: https://toml.io/
[pypi]: https://pypi.org
