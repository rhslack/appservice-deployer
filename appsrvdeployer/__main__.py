from cmath import log
from ftplib import error_perm
import argparse
import sys
from tempfile import TemporaryDirectory
from datetime import datetime
from appsrvdeployer.modules.logger import *
from appsrvdeployer.modules.utils import *
from appsrvdeployer.modules.ftp import *


def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="""
                                    Provisioning config file to app service.                                    
                                    Take zip file and upload on app service on defined path.
                                """,
                                prog="appsrvdeployer")
    azure = parser.add_argument_group("azure options")
    azure.add_argument("--resource-group", '-g', 
                       dest="group")
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

    return parser.parse_args()

def uploadFiles(ftp, path, logger, location=None):
    """[summary]

        Upload exctracted file on app services
    Args:
        ftp (FTP): Ftp connection
        path (str): Extracted file zip path
    """
    
    # Change ftp dir
    if location:
        ftp.cwd(location) 
    
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        if os.path.isfile(localpath):
            logger.info("STOR %s %s" % (name, localpath))
            ftp.storbinary('STOR ' + name, open(localpath,'rb'))
        elif os.path.isdir(localpath):
            logger.info("MKD %s" % (name))

            try:
                ftp.mkd(name)

            # ignore "directory already exists"
            except error_perm as e:
                if not e.args[0].startswith('550'): 
                    raise

            logger.info("CWD %s" % (name))
            ftp.cwd(name)
            uploadFiles(ftp, localpath, logger)           
            logger.debug("CWD ..")
            ftp.cwd("..")

def main() -> None:
    """[summary]
    Main function
    """

    # Create App Logger 
    logger = create_logger(
        app_name="appsrvdeployer",
        log_level=os.environ.get("APPSRVDEPLOYER_LOG_LEVEL") 
            if os.environ.get("APPSRVDEPLOYER_LOG_LEVEL") 
            else logging.INFO,
        stdout=True,
        file=True
    )
    
    # Init parser arguments
    args = init_parser() 
    
    # Init temporary dir to storage zip file
    dirpath = TemporaryDirectory(
            prefix="appsrvdeployer-", 
            suffix=datetime.today().strftime('-%Y%m%d%H%M')
        ) 
    
    # Set command to execute
    command = "az appservice plan list --query [].name"

    j = decode_json(command)
    j_appsrv = decode_json('az webapp list --query "[].name"')
    
    # Print app service list 
    logger.info("App service plan list")
    for plan in j:
        logger.info("Found plan: {0}".format(plan))
    
    for app in j_appsrv:
                    
        # Create App Logger 
        logger = create_logger(
            app_name=app,
            log_level=os.environ.get("APPSRVDEPLOYER_LOG_LEVEL") 
                if os.environ.get("APPSRVDEPLOYER_LOG_LEVEL") 
                else logging.INFO,
            stdout=True,
            file=True
        )
        
        logger.info("Retrive information from {0}...".format(app))
        
        url = decode_json(
                'az webapp deployment list-publishing-profiles --resource-group {rg} {sub} --name {0} --query "[1].publishUrl"'
                .format(app, rg=args.group, sub=args.subscription)
            )
        user = decode_json(
                'az webapp deployment list-publishing-profiles --resource-group {rg} {sub} --name {0} --query "[1].userName"'
                .format(app, rg=args.group, sub=args.subscription)
            )
        passwd = decode_json(
                'az webapp deployment list-publishing-profiles --resource-group {rg} {sub} --name {0} --query "[1].userPWD"'
                .format(app, rg=args.group, sub=args.subscription)
            )
        
        logger.debug("App service [{app}] connection url [{conn}] : user: {user} pass: {passwd}".format(
                app=app,
                conn=url,
                user=user,
                passwd=passwd,
            )
        )
    
        try:    
            logger.info("Try to create ftp connection to -> {0}".format(url))
            conn = init_ftp(url, ssl=True)
        except Exception as e:
            logger.error("Error while creating connection to -> {0}: {e}".format(url, e=e))
            
        conn.login(user=user, passwd=passwd)
        
        # Case selector
        if args.path:
            try:
                conn.retrlines("LIST %s" % (args.path))
            except error_perm as e_perm:
                logger.error("Failed to retrive path on app service, please select anthor destination: {e}"
                    .format(e=e_perm))
                        
                choice = input("Want crete this path? -> {0} ( 'Yes' or 'No') $ "
                    .format(args.path))

                if choice.lower() == "y" or choice.lower() == "yes":
                    conn.mkd(args.path)
                else:
                    sys.exit(550)
                    
        if args.zip:
            try:
                exctdir = unzipFiles(dirpath.name, args.zip)
            except Exception as e:
                logger.error("Error while unzip files: {e}".format(e=e))
                
            try: 
                uploadFiles(conn, dirpath.name + "/" + exctdir, logger, location=args.path)
            except Exception as e:
                logger.error("Error while upload files: {e}".format(e=e))
            
        conn.close()

if __name__ == "__main__":
    main()