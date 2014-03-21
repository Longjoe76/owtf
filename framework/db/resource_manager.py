from framework.db import models
from framework.lib.general import cprint, MultipleReplace
import os

class ResourceDB(object):
    def __init__(self, Core):
        self.Core = Core
        self.ResourceDBSession = self.Core.DB.CreateScopedSession(self.Core.Config.FrameworkConfigGetDBPath("RESOURCE_DB_PATH"), models.ResourceBase)
        self.LoadResourceDBFromFile(self.Core.Config.FrameworkConfigGet("DEFAULT_RESOURCES_PROFILE"))

    def LoadResourceDBFromFile(self, file_path): # This needs to be a list instead of a dictionary to preserve order in python < 2.7
        cprint("Loading Resources from: " + file_path + " ..")
        resources = self.GetResourcesFromFile(file_path)
        # resources = [(Type, Name, Resource), (Type, Name, Resource),]
        session = self.ResourceDBSession()
        for Type, Name, Resource in resources:
            # Need more filtering to avoid duplicates
            session.add(models.Resource(resource_type = Type, resource_name = Name, resource = Resource))
        session.commit()
        session.close()

    def GetResourcesFromFile(self, resource_file):
        resources = []
        ConfigFile = open(resource_file, 'r').read().splitlines() # To remove stupid '\n' at the end
        for line in ConfigFile:
            if '#' == line[0]:
                continue # Skip comment lines
            try:
                Type, Name, Resource = line.split('_____')
                # Resource = Resource.strip()
                resources.append((Type, Name, Resource))
            except ValueError:
                cprint("ERROR: The delimiter is incorrect in this line at Resource File: "+str(line.split('_____')))
        return resources

    def GetReplacementDict(self):
        configuration = self.Core.DB.Config.GetAll()
        configuration.update(self.Core.DB.Target.GetTargetConfig())
        return configuration

    def GetRawResources(self, ResourceType):
        ResourceType = ResourceType.upper() # Only upper case
        session = self.ResourceDBSession()
        raw_resources = session.query(models.Resource.resource_name, models.Resource.resource).filter_by(resource_type = ResourceType).all()
        session.close()
        return raw_resources

    def GetResources(self, ResourceType):
        replacement_dict = self.GetReplacementDict()
        resources = self.GetRawResources(ResourceType)
        for resource in resources:
            resource[-1] = MultipleReplace(resource[-1], replacement_dict)
        return resources

    def GetRawResourceList(self, ResourceList):
        session = self.ResourceDBSession()
        raw_resources = session.query(models.Resource.resource_name, models.Resource.resource).filter(models.Resource.resource_type.in_(ResourceList)).all()
        session.close()
        return raw_resources

    def GetResourceList(self, ResourceTypeList):
        replacement_dict = self.GetReplacementDict()
        resources = self.GetRawResourceList(ResourceTypeList)
        for resource in resources:
            resource[-1] = MultipleReplace(resource[-1], replacement_dict)
        return ResourceList
