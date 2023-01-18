![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)

# greenbone-feed-sync <!-- omit in toc -->

New script for syncing the Greenbone Community Feed

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Install using pip](#install-using-pip)
  - [Install using poetry](#install-using-poetry)
- [Settings](#settings)
- [Development](#development)
- [Maintainer](#maintainer)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Requirements

Python 3.9 and later is supported.

### Install using pip

You can install the latest stable release of **greenbone-feed-sync** from the
Python Package Index (pypi) using [pip]

    python3 -m pip install --user greenbone-feed-sync

### Install using poetry

Because **pontos** is a Python library you most likely need a tool to
handle Python package dependencies and Python environments. Therefore we
strongly recommend using [poetry].

You can install the latest stable release of **pontos** and add it as
a dependency for your current project using [poetry]

    poetry add pontos

## Settings

| Argument | Setting | Environment | Default | Description |
|----------|---------|-------------|---------|-------------|
| `--verbose, -v` | | | | Log verbosity. `-vvv` for maximum verbosity. |
| `--config, -c` | | | `~/.config/greenbone-feed-sync.toml` and `/etc/gvm/greenbone-feed-sync.toml` | TOML config file to load settings from. |
| `--private-directory` | | | | (Sub-)Directory to exclude from the sync which will never get deleted automatically. |
| `--compression-level` | | | 9 | rsync compression level 0-9. (0 - no compression, 9 - high compression) |
| `--type` | | | all | Specifies which feed(s) should be synced. |
| `--feed-url` | `feed_url` | GREENBONE_FEED_URL | rsync://feed.community.greenbone.net/community | URL to download the feed data from. |
| | `destination-prefix` | GREENBONE_FEED_DESTINATION_PREFIX | /var/lib/ | Directory prefix to use for feed data download destinations |
| `--notus-destination` | notus-destination | GREENBONE_FEED_NOTUS_DESTINATION | /var/lib/notus | Destination of the downloaded notus data. Overrides `--destination-prefix`. |
| `--notus-url` | notus-url | GREENBONE_FEED_NOTUS_URL | rsync://feed.community.greenbone.net/community/vulnerability-feed/22.04/vt-data/notus/ | URL to download the notus data from. Overrides `--feed-url`. |
| `--nasl-destination` | nasl-destination | GREENBONE_NASL_DESTINATION | /var/lib/openvas/plugins | Destination of the downloaded nasl data. Overrides `--destination-prefix`. |
| `--nasl-url` | nasl-url | GREENBONE_FEED_NASL_URL | rsync://feed.community.greenbone.net/community/vulnerability-feed/22.04/vt-data/nasl/ | URL to download the nasl data from. Overrides `--feed-url`. |
| `--scap-data-destination` | scap-data-destination | GREENBONE_FEED_SCAP_DATA_DESTINATION | /var/lib/gvm/scap-data | Destination of the downloaded SCAP data. Overrides `--destination-prefix`. |
| `--scap-data-url` | scap-data-url | GREENBONE_FEED_SCAP_DATA_URL | rsync://feed.community.greenbone.net/community/vulnerability-feed/22.04/scap-data | URL to download the SCAP data from. Overrides `--feed-url`. |
| `--cert-data-destination` | cert-data-destination | GREENBONE_FEED_CERT_DATA_DESTINATION | /var/lib/gvm/cert-data | Destination of the downloaded CERT data. Overrides `--destination-prefix`. |
| `--cert-data-url` | cert-data-url | GREENBONE_FEED_CERT_DATA_URL | rsync://feed.community.greenbone.net/community/vulnerability-feed/22.04/cert-data | URL to download the CERT data from. Overrides `--feed-url`. |
| `--report-formats-destination` | report-formats-destination | GREENBONE_FEED_REPORT_FORMATS_DESTINATION| /var/lib/gvm/data-objects/gvmd/22.04/report-formats | Destination of the downloaded report format data. Overrides `--destination-prefix`. |
| `--report-formats-url` | report-formats-url | GREENBONE_FEED_REPORT_FORMATS_URL | rsync://feed.community.greenbone.net/community/data-feed/22.04/report-formats | URL to download the report format data from. Overrides `--feed-url` |
| `--scan-configs-destination` | scan-configs-destination | GREENBONE_FEED_SCAN_CONFIGS_DESTINATION | /var/lib/gvm/data-objects/gvmd/22.04/scan-configs | Destination of the downloaded scan config data. Overrides `--destination-prefix`. |
| `--scan-configs-url` | scan-configs-url | GREENBONE_FEED_SCAN_CONFIGS_URL | rsync://feed.community.greenbone.net/community/data-feed/22.04/scan-configs | URL to download the scan config data from. Overrides `--feed-url`. |
| `--port-lists-destination` | port-lists-destination | GREENBONE_FEED_PORT_LISTS_DESTINATION | /var/lib/gvm/data-objects/gvmd/22.04/port-lists | Destination of the downloaded port list data. Overrides `--destination-prefix`. |
| `--port-lists-url` | port-lists-url | GREENBONE_FEED_PORT_LISTS_URL | rsync://feed.community.greenbone.net/community/data-feed/22.04/port-lists | URL to download the port list data from. Overrides `--feed-url`. |
| `--lock-file, --lockfile` | lock-file | GREENBONE_FEED_LOCK_FILE | /var/lib/ | File to use for locking the feed synchronization. Used to avoid that more then one process accesses the feed data at the same time. |
| `--fail-fast, --failfast` | | | | Stop after a first error has occurred. Otherwise the script tries to download additional data if specified. |
| `--no-wait` | | | | Fail directly if the lock file can't be acquired. |
| `--wait-interval` | wait-interval | GREENBONE_FEED_LOCK_WAIT_INTERVAL | 5 | Time to wait in seconds after failed lock attempt before re-trying to lock the file. |

## Development

**greenbone-feed-sync** uses [poetry] for its own dependency management and
build process.

First install poetry via pip

    python3 -m pip install --user poetry

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

This project is maintained by [Greenbone Networks GmbH][Greenbone Networks]

## Contributing

Your contributions are highly appreciated. Please
[create a pull request](https://github.com/greenbone/greeenbon-feed-sync/pulls)
on GitHub. Bigger changes need to be discussed with the development team via the
[issues section at GitHub](https://github.com/greenbone/greenbone-feed-sync/issues)
first.

## License

Copyright (C) 2022-2023 [Greenbone Networks GmbH][Greenbone Networks]

Licensed under the [GNU General Public License v3.0 or later](LICENSE).

[Greenbone Networks]: https://www.greenbone.net/
[poetry]: https://python-poetry.org/
[pip]: https://pip.pypa.io/
[autohooks]: https://github.com/greenbone/autohooks
