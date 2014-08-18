import os
import yaml
from logbeam import config


class CreateConfig:
    _KEYS = ['HOSTNAME', 'PORT', 'USERNAME', 'PASSWORD', 'BASE_DIRECTORY', 'UPLOAD_TRANSPORT', 'COMPRESS']

    def under(self, under):
        if config.BASE_DIRECTORY is None:
            config.BASE_DIRECTORY = under
        else:
            config.BASE_DIRECTORY = os.path.join(config.BASE_DIRECTORY, under)

    def contents(self):
        asDict = dict()
        for key in self._KEYS:
            asDict[key] = getattr(config, key)
        return yaml.dump(asDict, default_flow_style=False)
