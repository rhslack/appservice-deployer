import os
import subprocess
import shlex
from io import StringIO
import json
from ftplib import FTP, FTP_TLS, error_perm
import argparse
import sys
from tempfile import TemporaryDirectory, mkdtemp
from datetime import datetime
from typing import List
import zipfile
import time
from pathlib import Path

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


def decode_json(command) -> str:
    """[summary]

        Return Azure data in json decoded version
        
    Args:
        command (str): Command argument given

    Returns:
        [json]: JSON encoded
    """
    # Converto command to popen format
    args = shlex.split(command)
    
    ## Get app service list
    #  Open process
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    
    # Create IO data reader
    io = StringIO(p.stdout.read().decode())
    
    # Formato io data reader in JSON
    return json.load(io)

def unzipFiles(path, zip) -> List:
    """[summary]

        Extract zip file on defined path and return exctract file location

    Args:
        path (str): Path where zip file will be stored
    """
    if zip.endswith('.zip'):
        filePath=zip
        zip_file = zipfile.ZipFile(filePath)
        for names in zip_file.namelist():
            zip_file.extract(names,path)
        zip_file.close() 
        return zip_file.namelist()[0]

def uploadFiles(ftp, path, location=None):
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
            print("STOR", name, localpath)
            ftp.storbinary('STOR ' + name, open(localpath,'rb'))
        elif os.path.isdir(localpath):
            print("MKD", name)

            try:
                ftp.mkd(name)

            # ignore "directory already exists"
            except error_perm as e:
                if not e.args[0].startswith('550'): 
                    raise

            print("CWD", name)
            ftp.cwd(name)
            uploadFiles(ftp, localpath)           
            print("CWD", "..")
            ftp.cwd("..")

def init_ftp(url, ssl=False) -> FTP:
    """[summary]

    Generate FTP Connection
    
    Args:
        url (str): Url to connect

    Returns:
        FTP: FTP Connection
    """
    url = url.replace("ftp://", "")
    url = url.replace("/site/wwwroot", "")
    
    if ssl:
        try:
            return FTP_TLS(url)
        except Exception as error:
            print("Cannot estabilish TLS connection: {0}"
                  .format(error))
    else:
        try:
            return FTP(url)
        except Exception as error:
            print("Cannot estabilish connection: {0}"
                  .format(error))

def main() -> None:
    """[summary]
    Main function
    """
    
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
    
    #TEST 
    print("App service plan {j}".format(j=j))
    
    for app in j_appsrv:
        
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
        
        print("App service [{app}] connection url [{conn}] : \n{user}\n{passwd}\n".format(
                app=app,
                conn=url,
                user=user,
                passwd=passwd,
            )
        )
        
    conn = init_ftp(url, ssl=True)
    conn.login(user=user, passwd=passwd)
    
    # Set data protection to private
   # if conn.context.protocol.PROTOCOL_TLS.name == 'PROTOCOL_TLS':
   #     conn.prot_p()
   #     print("Set %s" % (conn.context.protocol.PROTOCOL_TLS.name))
        
    # Case selector
    if args.path:
        try:
            print(conn.retrlines("LIST %s" % (args.path)))
        except error_perm as e_perm:
            print("Failed to retrive path on app service, please select anthor destination: {e}"
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
            print("Error while unzip files: {e}".format(e=e))
            
        try: 
            uploadFiles(conn, dirpath.name + "/" + exctdir, args.path)
        except Exception as e:
            print("Error while upload files: {e}".format(e=e))
        
    conn.close()

if __name__ == "__main__":
    main()