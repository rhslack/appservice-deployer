import argparse
from cmath import log
from email.policy import default
import sys
from tempfile import TemporaryDirectory
from datetime import datetime
from appsrvdeployer.modules.logger import *
from appsrvdeployer.modules.utils import *
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
    
    # Init temporary dir to storage zip file
    dirpath = TemporaryDirectory(
            prefix="appsrvdeployer-", 
            suffix=datetime.today().strftime('-%Y%m%d%H%M')
        ) 
    
    # Set command to execute
    if args.appsrv_name:
        j = decode_json('az appservice plan list --query "[?contains(name, \'{0}\')].[name]" \
                        {rg} {sub}'
                        .format(args.appsrv_name,
                                rg=args.group, 
                                sub=args.subscription))
        j = j[0]
    else:
        j = decode_json("az appservice plan list --query [].name \
                        {rg} {sub}"
                        .format(rg=args.group, 
                                sub=args.subscription))
            

    if args.appsrv_name:
        j_appsrv = decode_json('az webapp list --query "[?contains(name, \'{0}\')].[name]" \
                                {rg} {sub}'
                               .format(args.appsrv_name,
                                       rg=args.group, 
                                       sub=args.subscription))  
        j_appsrv = j_appsrv[0] 
    else:
        j_appsrv = decode_json('az webapp list --query "[].name" \
            {rg} {sub}'
            .format(rg=args.group, 
                    sub=args.subscription))

    
    # Print app service list 
    logger.info("App service plan list")
    for plan in j:
        logger.info("Found plan: {0}".format(plan))

    if args.DRY_RUN:
        logger.info("Will deploy in {0}"
                    .format(j_appsrv))
        sys.exit(0)
    
    provisioning(
        j_appsrv,
        args.group,
        args.subscription,
        args.path,
        args.zip,
        dirpath,
        args.log
    )

if __name__ == "__main__":
    main()