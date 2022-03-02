# Azure App service deployer
 
### Simple azure app service file provisioner

<br>

![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/rhslack/appservice-deployer)
[![PyPI](https://img.shields.io/pypi/v/appservice-deployer?logo=python&logoColor=%23cccccc)](https://pypi.org/project/appservice-deployer)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![GitHub issues](https://img.shields.io/github/issues/rhslack/appservice-deployer)](https://github.com/rhslack/appservice-deployer/issues)
[![GitHub license](https://img.shields.io/github/license/rhslack/appservice-deployer)](https://github.com/rhslack/appservice-deployer)

This is a simple app to do provisioning of statics files on multiple app services.

## Installation

appsevdeployer don't required dependencies it use built-in function at moment.

**INSTALL BY PIP**

```bash
pip install appservice-deployer
```

## Usage

The basic utility for this program at now is to provision static file on app service, it's automatically retrive information on *FTPS* connection *USER* and *PASSWORD* of one or more app services.

It's recommended to make dry run before run provisioning to see every changes that the run will be affect and what app are involved.

### Dry run

```bash
python3 -m appsrvdeployer -n <APP_SERVER_NAME> -g <RESOURCE_GROUP> -s <SUBSCRIPTION> -z <ZIP_FILE> --path <ROOT_PATH> -C
```

*-C* option or *--dry-run* will make a dry run

### Real run

```bash
python3 -m appsrvdeployer -n <APP_SERVER_NAME> -g <RESOURCE_GROUP> -s <SUBSCRIPTION> -z <ZIP_FILE> --path <ROOT_PATH>
```

## FAQ

### 1. How should my zip file be built?

At moment the zip file must be built starting not from the source data but from an initial directory, the software will unpack and load everything starting from that directory onwards.

**Ex.**

```tree
init
├── dir1
│   ├── subdir1
│   │   └── subdir1.1
│   │       ├── file1
│   │       └── file2
│   ├── subdir2
│   │   └── file
│   ├── file1
│   ├── file2
│   ├── file3
│   ├── file4
│   ├── file5
│   └── subdir2
│       ├── file1
│       └── file2
└── dir2
    └── subdir1
        ├── file1
        ├── file2
        ├── file3
        ├── file4
        ├── file5
        ├── file6
        └── file7
```

it will unzip dir like this.

```bash
$ tree <ROOT_PATH>
.
├── dir1
│   ├── subdir1
│   │   └── subdir1.1
│   │       ├── file1
│   │       └── file2
│   ├── subdir2
│   │   └── file
│   ├── file1
│   ├── file2
│   ├── file3
│   ├── file4
│   ├── file5
│   └── subdir2
│       ├── file1
│       └── file2
└── dir2
    └── subdir1
        ├── file1
        ├── file2
        ├── file3
        ├── file4
        ├── file5
        ├── file6
        └── file7
```

## License

This project is open sourced under MIT license, see the [LICENSE](LICENSE) file for more details.
