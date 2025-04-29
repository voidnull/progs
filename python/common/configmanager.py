import tomllib
from pathlib import Path
import os.path
from . import log, utils

class Configuration:

    def __init__(self, project=None, filename=None):
        self.config = None
        self.project = project
        if filename is None:
            filename = 'doctools.toml'
            configfile = filename
        # check for local file
        if not os.path.exists(configfile):
            home = str(Path.home())
            configfile = '{}/.config/{}'.format(home, filename)

        if not os.path.exists(configfile):
            log.critical('unable to locate {} path [current dir, $(HOME)/.config/]'.format(filename))
            raise Exception('{} not found'.format(filename))

        log.debug('loading config from: {}'.format(configfile))
        self.config = tomllib.loads(utils.loadfile(configfile))

    def get_full_name(self, section=None, key=None):
        name = [n for n in [self.project, section, key] if n]
        return '.'.join(name)

    def get_section(self, section , default_value = None):
        log.debug('trying to fetch section [{}]'.format(self.get_full_name(section=section)))
        if section is None:
            if self.project and self.project in self.config:
                return self.config[self.project]
            else:
                return self.config

        # here the section has value
        depth = section.split('.')

        defsection = self.config
        for level in depth:
            if level in defsection:
                defsection = defsection[level]
            else:
                # def section not found
                defsection = None
                break

        if self.project:
            if self.project not in self.config:
                log.debug('project [{}] not found in config'.format(self.project))
            else:
                depth.insert(0, self.project)
                projsection = self.config
                for level in depth:
                    if level in projsection:
                        projsection = projsection[level]
                    else:
                        log.debug('{} not found in {}'.format(level, depth))
                        projsection = None
                if projsection: return projsection

        # section with project not found
        # so return the default section
        if defsection:
            log.debug('fetching default section : [{}]'.format(self.get_full_name(section=section)))
            return defsection

        log.debug('unable to find section:[{}]'.format(self.get_full_name(section=section)))
        return default_value

    def get(self, section, key, default_value = None):
        log.debug('trying to fetch key:[{}]'.format(self.get_full_name(section=section,key=key)))
        if self.config is None:
            log.warn('no config file loaded for - [{}]'.format(self.get_full_name(section=section,key=key)))
            return None

        cfgsection = self.get_section(section)

        if not cfgsection:
            log.warn('config section not found for key [{}]'.format(self.get_full_name(section=section,key=key)))
            return default_value

        if key not in cfgsection:
            log.warn('config not found [{}]'.format(self.get_full_name(section=section,key=key)))
            return default_value

        return cfgsection[key]

    def get_key(self, key,  default_value = None):
        return self.get(None, key, default_value)

    def getboolean(self, section, key, default_value = None):
        value = self.get(section, key)

        if value is None:
            return default_value

        if type(value) == bool:
            return value

        if type(value) == str:
            if value.lower() in ['yes', 'ok', 'true'] : return True
            if value.lower() in ['no', 'false'] : return False

        return default_value