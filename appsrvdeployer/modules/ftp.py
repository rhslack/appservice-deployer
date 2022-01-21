from ftplib import FTP, FTP_TLS


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
            raise("Cannot estabilish TLS connection: {0}"
                  .format(error))
    else:
        try:
            return FTP(url)
        except Exception as error:
            raise("Cannot estabilish connection: {0}"
                  .format(error))