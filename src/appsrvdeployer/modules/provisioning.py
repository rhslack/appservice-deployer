from ftplib import error_perm
from shutil import rmtree
import sys
from appsrvdeployer.modules.ftp import init_ftp
from appsrvdeployer.modules.logger import *
from appsrvdeployer.modules.utils import decode_json, mkdtempdir, unzipFiles
import os


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
            

def provisioning(
        j_appsrv, 
        rg, 
        subscription, 
        path, 
        zip,
        logfile
    ):
    
    for app in j_appsrv:

        if len(app) == 1:
            app = app[0]

        # Create App Logger 
        logger = create_logger(
            app_name=app,
            log_level=os.environ.get("APPSRVDEPLOYER_LOG_LEVEL") 
                if os.environ.get("APPSRVDEPLOYER_LOG_LEVEL") 
                else logging.INFO,
            logfile=logfile,
            stdout=True,
            file=True
        )
        
        logger.info("Retrive information from {0}...".format(app))
        
        url = decode_json(
                'az webapp deployment list-publishing-profiles {rg} {sub} --name {0} --query "[1].publishUrl"'
                .format(app, rg=rg, sub=subscription)
            )
        user = decode_json(
                'az webapp deployment list-publishing-profiles {rg} {sub} --name {0} --query "[1].userName"'
                .format(app, rg=rg, sub=subscription)
            )
        passwd = decode_json(
                'az webapp deployment list-publishing-profiles {rg} {sub} --name {0} --query "[1].userPWD"'
                .format(app, rg=rg, sub=subscription)
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
        if path:
            try:
                conn.retrlines("LIST %s" % (path))
            except error_perm as e_perm:
                logger.error("Failed to retrive path on app service, please select anthor destination: {e}"
                    .format(e=e_perm))
                        
                choice = input("Want crete this path? -> {0} ( 'Yes' or 'No') $ "
                    .format(path))

                if choice.lower() == "y" or choice.lower() == "yes":
                    conn.mkd(path)
                else:
                    sys.exit(550)

        # Create temporary dir 
        dirpath = mkdtempdir()

        if zip:
            try:
                exctdir = unzipFiles(dirpath, zip)
            except Exception as e:
                logger.error("Error while unzip files: {e}".format(e=e))
                rmtree(dirpath)
                
            try: 
                uploadFiles(conn, dirpath + "/" + exctdir, logger, location=path)
            except Exception as e:
                logger.error("Error while upload files: {e}".format(e=e))
                rmtree(dirpath)
            finally:
                logger.info("Upload completed!")
                rmtree(dirpath)
            
        conn.close()