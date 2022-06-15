import argparse
import sys
import os
from appsrvdeployer.modules.logger import *
from appsrvdeployer.modules.utils import listZipFiles, decode_json, mkdtempdir
from appsrvdeployer.modules.ftp import *
import textwrap
from appsrvdeployer.modules.provisioning import provisioning
from tempfile import mkstemp
import atexit

def exit_handler(logfile):
    print("Can read log file at: {0}".format(logfile))


def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=textwrap.dedent("""
                                    Provisioning config file to app service.                                    
                                    Take zip file and upload on app service on defined path.
                                """),
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                prog="appsrvdeployer",
                                epilog=textwrap.dedent('''\
                                It's recommended to make dry run before run provisioning 
                                to see what\'s app are selected for deployments\n
                                '''))

    azure = parser.add_argument_group("azure options")
    azure.add_argument("-n", "--app-service-name",
                       dest="appsrv_name", default="",
                       help="App service name or like, to deploy into filtered app services")
    azure.add_argument("--slot",
                       dest="slot", default=False,
                       action="store_true",
                       help="App service name or like, to deploy into filtered app services")   
    azure.add_argument("--resource-group", '-g', 
                       dest="group",
                       default="")
    azure.add_argument("--subscription", '-s', 
                       dest="subscription", 
                       default="", 
                       required=False)
    
    provision = parser.add_argument_group("provisioning options")
    provision.add_argument("--zip", "-z", 
                           dest="zip",
                           required=True)    
    provision.add_argument("--path", "-p", 
                           dest="path", 
                           type=str,
                           required=True)
    provision.add_argument("--dry-run", "-C", 
                           dest="DRY_RUN",
                           default=False,
                           action="store_true")
    
    utils = parser.add_argument_group("utils")
    utils.add_argument(
        "--log",
        dest="logfile",
        type=str,
        default=mkstemp(prefix="logger-appsrvdeployer-", suffix=".log")[1],
        help="Set log file location."
    )

    return parser.parse_args()

def main() -> None:
    """[summary]
    Main function
    """

    # Init parser arguments
    args = init_parser() 
    
    # Register exit handler
    atexit.register(exit_handler, args.logfile)

    # Create App Logger 
    logger = create_logger(
        app_name="appsrvdeployer",
        log_level=os.environ.get("APPSRVDEPLOYER_LOG_LEVEL") 
            if os.environ.get("APPSRVDEPLOYER_LOG_LEVEL") 
            else logging.INFO,
        logfile=args.logfile,
        stdout=True,
        file=True
    )
    
    # Parsing subscription
    if args.subscription != "":
        args.subscription = "--subscription "+ args.subscription
        
    # Parsing resource group
    if args.group != "":
        args.group = "--resource-group "+ args.group       

    if args.appsrv_name:
        j_appsrv = decode_json('az webapp list --query "[?contains(name, \'{0}\')].[name]" \
                                {rg} {sub}'
                               .format(args.appsrv_name,
                                       rg=args.group, 
                                       sub=args.subscription))  
        if len(j_appsrv) == 1:
            j_appsrv = j_appsrv[0] 
    else:
        j_appsrv = decode_json('az webapp list --query "[].name" \
            {rg} {sub}'
            .format(rg=args.group, 
                    sub=args.subscription))

    if args.DRY_RUN:
        logger.info("Will deploy in {0}"
                    .format(j_appsrv))

        for f in listZipFiles(mkdtempdir(), args.zip):
            logger.info("Will upload this: {0}".format(f))

        sys.exit(0)
    
    provisioning(
        j_appsrv,
        args.group,
        args.subscription,
        args.path,
        args.zip,
        args.logfile
    )

if __name__ == "__main__":
    main()