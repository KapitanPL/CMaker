import xml.etree.ElementTree as ET
from os import path
from functools import reduce

class vcxproj_parser:
    # Define the namespace
    ns = {'msbuild': 'http://schemas.microsoft.com/developer/msbuild/2003'}
    pd = "PROJECT_CURRENT_DIR"
    ta = "TARGET_ARCHITECTURE"

    def __init__(self, vcxproj_dir : str, vcxproj_file: str):
        self.dir = path.normpath(vcxproj_dir).replace("\\", "/")
        self.tree = ET.parse(path.join(vcxproj_dir, vcxproj_file))
        self.root = self.tree.getroot()

    def _parseCondition(self, condition: str):
        '''
        Expects condition of this form returns touple (arch, configuration)
        Condition="'$(Configuration)|$(Platform)'=='Debug|x64'"
        '''
        info = condition.split('==')
        if len(info) > 0:
            stripped = info[-1].strip("'").split("|")
            return (stripped[1], stripped[0])
        return None
    
    def _commonProperties(self, properties: dict):
        commonPropertiePerArch = dict()
        for arch in properties.keys():
            commonPropertiePerArch[arch] = reduce(set.intersection, properties[arch].values())
        totalCommonProperties = reduce(set.intersection, commonPropertiePerArch.values())
        for arch in commonPropertiePerArch.keys():
            commonPropertiePerArch[arch] = commonPropertiePerArch[arch].difference(totalCommonProperties);
        for arch in properties.keys():
            for conf in properties[arch].keys():
                properties[arch][conf] = properties[arch][conf].difference(totalCommonProperties);
        for arch in commonPropertiePerArch.keys():
            for conf in properties[arch].keys():
                properties[arch][conf] = properties[arch][conf].difference(commonPropertiePerArch[arch]);
        properties['All'] = commonPropertiePerArch
        properties['All']['All'] = totalCommonProperties
        return properties
        
    def printProjectDir(self):
        print(f'set( {vcxproj_parser.pd} "{self.dir}")')

    def printIncludes(self):
        print('set( HEADERS ')
        for include in self.root.findall('.//msbuild:ClInclude', vcxproj_parser.ns):
            fl = include.get('Include')
            if fl != None:
                fl = fl.replace("\\","/")
            print(f"\t${{{vcxproj_parser.pd}}}/{fl}")
        print(')')

    def printCompiles(self):
        print('set( SOURCES ')
        for compile in self.root.findall('.//msbuild:ClCompile', vcxproj_parser.ns):
            fl = compile.get('Include')
            if fl != None:
                fl = fl.replace("\\","/")
            print(f"\t${{{vcxproj_parser.pd}}}/{fl}")
        print(')')

    def printCompileDefinitions(self):
        config_definitions = {}

        # Collect definitions
        for group in self.root.findall('.//msbuild:ItemDefinitionGroup', vcxproj_parser.ns):
            config_condition = self._parseCondition(group.attrib.get('Condition', ''))
            if config_condition != None:
                for compile in group.findall('.//msbuild:ClCompile', vcxproj_parser.ns):
                    pre_def = compile.find('msbuild:PreprocessorDefinitions', vcxproj_parser.ns)
                    if pre_def is not None and pre_def.text:
                        defs = pre_def.text.replace(';', ' ').split()
                        filtered_defs = {d for d in defs if d and not d.startswith('%(')}

                        if config_condition[0] not in config_definitions:
                            config_definitions[config_condition[0]] = {}
                        if config_condition[1] not in config_definitions[config_condition[0]]:
                            config_definitions[config_condition[0]][config_condition[1]] = set()
                        config_definitions[config_condition[0]][config_condition[1]].update(filtered_defs)

        config_definitions = self._commonProperties(config_definitions)
        for arch, conf_definitions in config_definitions.items():
            print(" ")
            print(f'if({vcxproj_parser.ta}) STREQUAL "{arch}")')
            for config, defs in conf_definitions.items():
                if len(defs) > 0:
                    print(f"target_compile_definitions(${{PROJECT_NAME}} PRIVATE $<$<CONFIG:{config}>:{' '.join(defs)}>)")
            print("endif()")

    def printLinkLibraries(self):
        config_libraries = {}

        # Collect libraries
        for group in self.root.findall('.//msbuild:ItemDefinitionGroup', vcxproj_parser.ns):
            config_condition = self._parseCondition(group.attrib.get('Condition', ''))
            if config_condition != None:
                for link in group.findall('.//msbuild:Link', vcxproj_parser.ns):
                    additional_deps = link.find('msbuild:AdditionalDependencies', vcxproj_parser.ns)
                    if additional_deps is not None and additional_deps.text:
                        libs = additional_deps.text.replace(';', ' ').split()
                        filtered_libs = {lib for lib in libs if lib and not lib.startswith('%(')}

                        if config_condition[0] not in config_libraries:
                            config_libraries[config_condition[0]] = {}
                        if config_condition[1] not in config_libraries[config_condition[0]]:
                            config_libraries[config_condition[0]][config_condition[1]] = set()
                        config_libraries[config_condition[0]][config_condition[1]].update(filtered_libs)

        config_libraries = self._commonProperties(config_libraries)
        for arch, conf_libraries in config_libraries.items():
            print(" ")
            print(f'if({vcxproj_parser.ta}) STREQUAL "{arch}")')
            for config, libraries in conf_libraries.items():
                if len(libraries) > 0:
                    print(f"target_link_libraries(${{PROJECT_NAME}} PUBLIC $<$<CONFIG:{config}>:{' '.join(libraries)}>)")
            print("endif()")

parser = vcxproj_parser(r"C:\LIM-SVN\trunk\version6\src\gnr_system", "gnr_system_D-Lite.vcxproj")

# parser.printProjectDir()
# parser.printIncludes()
# parser.printCompiles()
parser.printCompileDefinitions()
# parser.printLinkLibraries()