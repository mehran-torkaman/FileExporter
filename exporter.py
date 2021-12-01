import hashlib, os.path, time
import json
from os import environ
from flask import Flask, request, current_app


#######################################################################
#  Define Configuration Class For Variables.
#######################################################################
class Config:

    ######################### Global Configuration #########################

    ENV = environ.get("FILE_EXPORTER_ENV","production")

    DEBUG = int(environ.get("FILE_EXPORTER_DEBUG","0"))

    TESTING = int(environ.get("FILE_EXPORTER_TESTING","0"))

    JSONIFY_PRETTYPRINT_REGULAR = True

    ######################### File Configuration #########################

    EXPORTER_DEFAULT_FILE = environ.get("FILE_EXPORTER_PATH",None)


#######################################################################
#  Define Function For JSONIFY Return.
#######################################################################
DBG_MESSAGE = {
    "100" : "OK",
    "101" : "Unsupported Media Type.",
}

def jsonify(state={}, metadata={}, status=200, code=100, headers={}):
    data = state
    data.update(metadata)
    if current_app.debug:
        data["message"] = DBG_MESSAGE[str(code)]
    data["code"] = code
    return data, status, headers

#######################################################################
#  Define Function For Checking Creation Date Of File.
#######################################################################
def date_create():
    try:
        return time.ctime(os.path.getmtime(Config.EXPORTER_DEFAULT_FILE))
    except:
        return '{"message" : "File Path Not Specified"}'

#######################################################################
#  Define Function For Checking MD5 Hash Of File.
#######################################################################
def md5_check():
    try:
        file_name = Config.EXPORTER_DEFAULT_FILE
        md5_hash = hashlib.md5()
        with open(file_name, 'rb') as f:
            content = f.read()
            md5_hash.update(content)
            digest = md5_hash.hexdigest()
        return digest
    except:
        return '{"message" : "File Path Not Specified"}'

########################################################################
#  Create Flask Application
########################################################################
app = Flask(__name__)

RESULT = {
    "File" : {
        "path" : Config.EXPORTER_DEFAULT_FILE,
        "created_at" : date_create(),
        "md5_check" : md5_check()
    },
    "Modification" : {
        "last_modified" : None,
        "last_update" : date_create(),
        "modified_count" : 0
    },
    "MD5_hash": {
        "md5_checksum" : "OK"
    }
}

app = Flask(__name__)


@app.route('/')
def get_files_list():
    if request.content_type != "application/json":
        return jsonify(status=415, code=101)
    file_name = Config.EXPORTER_DEFAULT_FILE
    try:
        last_modified = time.ctime(os.path.getmtime(file_name))
    except:
        return '{"message" : "File Path Not Specified"}'
    last_update = RESULT["Modification"]["last_update"]
    if last_update != last_modified:
        RESULT["Modification"]["last_update"] = last_modified
        RESULT["Modification"]["last_modified"] = last_modified
        RESULT["Modification"]["modified_count"] += 1
    md5_hash = hashlib.md5()
    with open(file_name, 'rb') as f:
        content = f.read()
        md5_hash.update(content)
        digest = md5_hash.hexdigest()
    if RESULT["File"]["md5_check"] != digest:
        RESULT["MD5_hash"]["md5_checksum"] = "FAILED"
    else:
        RESULT["MD5_hash"]["md5_checksum"] = "OK"
    return json.dumps(RESULT)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
