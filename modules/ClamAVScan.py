from __future__ import division, absolute_import, with_statement, print_function, unicode_literals

__author__ = 'Mike Long'

DEFAULTCONF ={
    "ENABLED":True,
    "alt_path": "/etc/clam.d/clamd.conf"
}

def check(conf=DEFAULTCONF):
    return conf["ENABLED"]
    # or we can always run be uncommenting below
    # return True


def scan(filelist, conf=DEFAULTCONF):
    import pyclamd
    results = []

    try:
        clamScanner = pyclamd.ClamdUnixSocket()
        clamScanner.ping()
    except:
        clamScanner = pyclamd.ClamdNetworkSocket()
        try:
            clamScanner.ping()
        except:
            raise ValueError("Connection configuration: Unable to connect to clamd server")

    # common error string, if pyclamd cannot scan as file
    error_str = "[('ERROR', 'lstat() failed: No such file or directory.')]"


    # Scan each file from filelist for virus
    for f in filelist:
        # Rest temp placeholders
        output = None
        file_results = None
        msg = None

        output = clamScanner.scan_file(f)
        file_results = output.values()
        msg = str(file_results[0:1])

        # Check to for the error_str message
        if error_str in msg:
            # IF BUFFER IS LARGER THAN ACCEPTED BUFFER SIZE MAY NOT BE IDEAL
            # Since file was not found load contents in buffer and scan as buffer
            file_as_buffer = open(f, 'rU').read()
            buffer_results = clamScanner.scan_stream(file_as_buffer)

            if buffer_results is not None:
                # Assumes virus is found
                # place results in results[]
                results.append((f, buffer_results.values()))

        elif file_results is not None:
            # Assumes virus is found
            # place results in results[]
            results.append((f, file_results.values()))

    # Set metadata tags
    metadata = {
        'Name': "Anti-virus",
        'Type': "ClamAV",
    }

    return (results, metadata)