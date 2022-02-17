from datetime import datetime
from tempfile import TemporaryDirectory
from typing import List
from io import StringIO
import json
import shlex
import subprocess
import zipfile

def decode_json(command) -> json:
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


def listZipFiles(path, zip) -> List:
    """[summary]

        List zip file on defined path and return exctract file location

    Args:
        path (str): Path where zip file will be stored
    """
    if zip.endswith('.zip'):
        filelist = []
        filePath=zip
        zip_file = zipfile.ZipFile(filePath)
        for names in zip_file.namelist():
            filelist.append(path+names)
        zip_file.close() 
        return filelist

def mkdtempdir() -> str:
    """[summary]

        Make temporary dir
    
    return: TemporaryDirectory
    """
    return TemporaryDirectory(
            prefix="appsrvdeployer-", 
            suffix=datetime.today().strftime('-%Y%m%d%H%M')
        ).name