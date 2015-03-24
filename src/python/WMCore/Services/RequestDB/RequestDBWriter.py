from WMCore.Wrappers.JsonWrapper import JSONEncoder
from WMCore.Services.RequestDB.RequestDBReader import RequestDBReader
from WMCore.Database.CMSCouch import Document

class RequestDBWriter(RequestDBReader):

    def __init__(self, couchURL, couchapp = "ReqMgr"):
        # set the connection for local couchDB call
        # inherited from WMStatsReader
        self._commonInit(couchURL, couchapp)
        self._propertyNeedToBeEncoded = ["RequestTransition",
                                         "SiteWhitelist",
                                         "SiteBlacklist",
                                         "BlockWhitelist",
                                         "SoftwareVersions",
                                         "InputDatasetTypes",
                                         "InputDatasets",
                                         "OutputDatasets",
                                         "Teams"]

    def insertGenericRequest(self, doc):
        
        doc = Document(doc["RequestName"], doc) 
        result = self.couchDB.commitOne(doc)
        self.updateRequestStatus(doc["RequestName"], "new")
        return result

    def updateRequestStatus(self, request, status):
        status = {"RequestStatus": status}
        return self.couchDB.updateDocument(request, self.couchapp, "updaterequest",
                    status)
        
    def updateRequestStats(self, request, stats):
        """
        This functionis only available ReqMgr couch app currutly (not T0)
        WQ specific function
        param: stats: dict of {'total_jobs': 0, 'input_lumis': 0,
                               'input_events': 0, 'input_num_files': 0}
        """
        return self.couchDB.updateDocument(request, self.couchapp, "totalstats",
                    fields = stats)

    def updateRequestProperty(self, request, propDict, dn = None):
        encodeProperty = {}
        for key, value in propDict.items():
            if isinstance(value, list) or isinstance(value, dict):
                encodeProperty[key] = JSONEncoder().encode(value)
            else:
                encodeProperty[key] = value
        if dn:
            encodeProperty["DN"] = dn
        return self.couchDB.updateDocument(request, self.couchapp, "updaterequest",
                    encodeProperty)