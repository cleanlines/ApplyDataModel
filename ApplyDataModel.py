from BaseObject import BaseObject
from CSVHelper import CSVHelper
import glob
import os
import arcpy
import json

class ApplyDataModel(BaseObject):

    # assume folder is schemas - may need to be passed in
    def __init__(self,config_file=None):
        super().__init__()
        self._schema_folder = f"{os.getcwd()}/schemas"
        self._srs = f"{self._schema_folder}/prjs/prjs.gdb"
        #self._con = f"{os.getcwd()}/{self._config.con}"
        self._overwrite = False
        self._envs = None
        self.log(self._schema_folder)
        self.log(self._srs)
        self._connection = None
        self._schema = None
        if config_file:
            self._config.add_config(config_file)
        

    @property
    def environments(self):
        return self._envs

    @environments.setter
    def environments(self, value):
        if not isinstance(value,list):
            raise ValueError("Must be a list")
        self._envs = value

    @property
    def overwrite(self):
        return self._overwrite

    @overwrite.setter
    def overwrite(self, value):
        if not isinstance(value,bool):
            raise ValueError("Must be a boolean")
        self._overwrite = value

    def _process_feature_classes(self,file_name):
        with open(f"{self._schema_folder}/{file_name}", "r", encoding='utf-8-sig',newline="\r\n") as read_file:
            feature_classes = json.load(read_file, strict=False)
            for row in feature_classes:
                self.log(row)
                self._create_feature_class(row)
        self.log("Processing feature classes finished.")

    def process_data_model(self):
        # get a list of schemas
        for wkspc in self._config.workspaces:
            if "exclude" in wkspc and wkspc["exclude"] == "true":
                continue
            else:
                self._overwrite = True if wkspc["overwrite"] == "true" else False
                self._connection = wkspc["workspace"]
                self._schema = wkspc["schema"]
                if "domains" in wkspc:
                    self._process_domains(wkspc["domains"])
                #this one should always be here
                self._process_feature_classes(wkspc["featureclasses"])
                if "subtypes" in wkspc:
                    self._process_subtypes(wkspc["subtypes"])
                if "relationships" in wkspc:
                    self._process_relationship_classes(wkspc["relationships"])

    def _parse_code(self,code,codetype):
        return {
            "TEXT": lambda x: x,
            "FLOAT" :lambda x: float(x),
            "DOUBLE" :lambda x: float(x),
            "SHORT" :lambda x: int(x),
            "LONG" :lambda x: int(x),
            "DATE":lambda x: x
        }[codetype](code)

    def _process_relationship_classes(self,file_name):
        try:
            with open(f"{self._schema_folder}/{file_name}", "r", encoding='utf-8-sig',newline="\r\n") as read_file:
                relationships = json.load(read_file, strict=False)['relationships']
                for a_relationship in relationships:
                    try:
                        if "destinationpk" in a_relationship:
                            arcpy.CreateRelationshipClass_management(f"{self._connection}/{a_relationship['origin']}",f"{self._connection}/{a_relationship['destination']}", a_relationship['outclass'], a_relationship['type'], a_relationship['forwardlabel'], a_relationship['backlabel'], a_relationship['message'], a_relationship['cardinality'], a_relationship['attributed'], a_relationship['originpk'], a_relationship['originfk'], a_relationship['destinationpk'], a_relationship['destinationfk'])
                        else:
                            arcpy.CreateRelationshipClass_management(f"{self._connection}/{a_relationship['origin']}",f"{self._connection}/{a_relationship['destination']}", a_relationship['outclass'], a_relationship['type'], a_relationship['forwardlabel'], a_relationship['backlabel'], a_relationship['message'], a_relationship['cardinality'], a_relationship['attributed'], a_relationship['originpk'], a_relationship['originfk'])
                    except Exception as e:
                        self.log(f"Can't add relationship for to {a_relationship['outclass']}")
                        self.errorlog(e)
        except Exception as e:
            self.log(f"Can't open relationships.json.")
            self.errorlog(e)

    def _process_domains(self,file_name):
        #note Jose will be changing the json from the PIA
        # "AssociatedStructType": {
        #                 "description": "Associated Structures to Cables",
        #                 "type": "SHORT",
        #                 "domaintype": "CODED",
        #                 "split": "DEFAULT",
        #                 "merge": "DEFAULT",
        #                 "codes": {
        #                     "0": {
        #                         "value": "Pole",
        #                         "selected": true,
        #                         "required": true
        #                     },
        #                     "1": {
        #                         "value": "Chamber",
        #                         "selected": true,
        #                         "required": true
        #                     }
        #                 }
        #             },
        try:
            with open(f"{self._schema_folder}/{file_name}", "r", encoding='utf-8-sig',newline="\r\n") as read_file:
                domains = json.load(read_file, strict=False)
                for k,v in domains.items():
                        try:
                            arcpy.CreateDomain_management(self._connection,k,v['description'],v['type'],v['domaintype'],v['split'],v['merge'])
                        except Exception as e:
                            self.log(f"Can't create domain {k}")
                            self.errorlog(e)
                        if v['domaintype'] == "CODED":
                            for dcode,dvalue in v["codes"].items():
                                try:
                                    convert_code = self._parse_code(dcode,v['type'])
                                    arcpy.AddCodedValueToDomain_management(self._connection,k, convert_code, dvalue)
                                except Exception as e:
                                    self.log(f"Can't add coded value {dcode} to {k}")
                                    self.errorlog(e) 
                        elif v['domaintype'] == "RANGE":
                            try:
                                arcpy.SetValueForRangeDomain_management(self._connection,k, v['minrange'], v['maxrange'])
                            except Exception as e:
                                self.log(f"Can't add range value to {k}")
                                self.errorlog(e) 
                    
        except Exception as e:
            self.log(f"Can't open domains.json.")
            self.errorlog(e)

    def _process_subtypes(self,file_name):
        #look for a subtypes file
        try:
            with open(f"{self._schema_folder}/{file_name}", "r", encoding='utf-8-sig',newline="\r\n") as read_file:
                sub_types = json.load(read_file, strict=False)
                #print(sub_types)
                for k,v in sub_types.items():
                    print(k,v)
                    full_fc = f"{self._connection}/{k}"
                    for fd,st_vals in v['field'].items():
                        try:
                            arcpy.SetSubtypeField_management(full_fc, fd)
                        except Exception as e:
                            self.log(f"Setting subtype field {full_fc},{fd} failed")
                            self.errorlog(e)
                        for code in st_vals:
                            try:
                                arcpy.AddSubtype_management(full_fc, code, st_vals[code])
                            except Exception as e:
                                self.log(f"Setting subtype code {full_fc},{fd},{code},{st_vals[code]} failed")
                                self.errorlog(e)
                    if "domains" in v:
                        for sk,dms in v['domains'].items():
                            for dmfd,appdm in dms.items():
                                arcpy.AssignDomainToField_management(full_fc,dmfd,appdm,sk)

        except Exception as e:
            self.log(f"Can't open subtypes.json.")
            self.errorlog(e)

    def _process_fields(self,fc,field_file):
        # https://stackoverflow.com/questions/34399172/why-does-my-python-code-print-the-extra-characters-%C3%AF-when-reading-from-a-tex/34399309 - JSON files have a byte order mark ()
        with open(f"{self._schema_folder}/{field_file}", "r", encoding='utf-8-sig',newline="\r\n") as read_file:
            self.log(f"Applying fields for {fc}")
            fields_object = json.load(read_file, strict=False)#.read())
            if 'fields' in fields_object:
                for fd in fields_object['fields']:
                    self.log(f"Applying {fd['name']}")
                    try:
                        arcpy.AddField_management(fc,fd['name'],fd['type'],fd['precision'],fd['scale'],fd['length'],fd['alias'],fd['nullable'],fd['required'],fd['domain'])
                        self.log(f"Field {fd['name']} added to {fc}")
                    except Exception as e:
                        self.log(f"Adding field {fd['name']} failed")
                        self.errorlog(e)                     

    def _create_database_item(self,config_dic):
        try:
            sr = None
            if 'spatialref' in config_dic and config_dic['spatialref']:
                sr = arcpy.SpatialReference(config_dic['spatialref'])
                # sr = arcpy.Describe(f"{self._srs}/{config_dic['spatialref']}").spatialReference
            #are we creating a fc or a table? Assumption is no sr or geom create a table
            if config_dic['geometry'] and sr:
                self.log(f"Creating feature class {config_dic['name']}")
                arcpy.CreateFeatureclass_management(self._connection,config_dic['name'],config_dic['geometry'],spatial_reference=sr)
            else:
                self.log(f"Creating table {config_dic['name']}")
                arcpy.CreateTable_management(self._connection,config_dic['name'])

            self.log(f"{config_dic['name']} created")
            self._process_fields(f"{self._connection}/{config_dic['name']}", config_dic['fields'])
        except Exception as e:
            self.errorlog(e) 

    def _create_feature_class(self,config_dic):
        full_fc = f"{self._connection}/{config_dic['name']}"
        if arcpy.Exists(full_fc):
            self.log(f"Feature class {config_dic['name']} exists.")
            if self.overwrite:
                self.log("We have clearance to delete Clarence.")
                try:
                    arcpy.Delete_management(full_fc)
                except Exception as e:
                    self.errorlog(e)
                    return
            else:
                self.log("We are NOT deleting - cannot create this feature class as it already exists.")
                return
        
        self._create_database_item(config_dic)
        self._manage_database_item(config_dic)

    def _manage_database_item(self,config_dic):
        full_fc = f"{self._connection}/{config_dic['name']}"
        try:
            if config_dic['globalids'] and config_dic['globalids'] == 'true':
                self.log("Adding Globals Ids.")
                arcpy.AddGlobalIDs_management(full_fc)
                self.log("Global Ids done.")
        except Exception as e:
            self.errorlog(e)
        try:
            if config_dic['editortracking'] and config_dic['editortracking'] == 'true':
                self.log("Adding Editor tracking fields.")
                arcpy.EnableEditorTracking_management(full_fc,"created_user","created_date","last_edited_user","last_edited_date","ADD_FIELDS")
                self.log("Editor tracking enabled.")
        except Exception as e:
            self.errorlog(e)
        try:
            if config_dic['archiving'] and config_dic['archiving'] == 'true':
                self.log("Enabling archiving.")
                arcpy.EnableArchiving_management(full_fc)
                self.log("Archiving enabled.")
        except Exception as e:
            self.errorlog(e)
        try:
            if config_dic['attachments'] and config_dic['attachments'] == 'true':
                self.log("Enabling attachments.")
                arcpy.EnableAttachments_management(full_fc)
                self.log("Attachments enabled.")
        except Exception as e:
            self.errorlog(e)


#TODO: set default subtypes! setdefaultsubtype

if __name__ == "__main__":
    cfc = ApplyDataModel()
    cfc.process_data_model()
