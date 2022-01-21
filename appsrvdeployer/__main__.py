import subprocess
import shlex
from io import StringIO
import json
from ftplib import FTP, FTP_TLS, error_perm
import argparse

def init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="""
                                    Provisioning config file to app service.                                    
                                    Take zip file and upload on app service on defined path.
                                """)
    azure = parser.add_argument_group("azure options")
    azure.add_argument("--resource-group", '-g', 
                       dest="group")
    azure.add_argument("--subscription", '-s', 
                       dest="subscription", 
                       default="", 
                       required=False)
    
    provision = parser.add_argument_group("provisioning options")
    provision.add_argument("--zip", "-z", 
                           dest="zip")
    provision.add_argument("--path", "-p", 
                           dest="path", 
                           type=str)

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
    if conn.context.protocol.PROTOCOL_TLS.name == 'PROTOCOL_TLS':
        conn.prot_p()
        print("Set %s" % (conn.context.protocol.PROTOCOL_TLS.name))
    
    print(conn.retrlines("LIST"))
    
    # Case selector
    if args.path:
        try:
            print(conn.retrlines("LIST %s" % (args.path)))
        except error_perm as e_perm:
            conn.mkd(args.path)
            print("Failed to retrive path on app service, please select anthor destination: {e}"
                  .format(e=e_perm))
    
    conn.close()

if __name__ == "__main__":
    main()