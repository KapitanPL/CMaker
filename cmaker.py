import argparse
import os

parser = argparse.ArgumentParser(description="Generate a CMakeLists.txt for a C++ shared library project.")
parser.add_argument("target_directory", type=str, help="The target directory for CMakeLists.txt")
parser.add_argument("project_name", type=str, help="The project name")
parser.add_argument("library_name", type=str, help="The name of the library to build")

args = parser.parse_args()

class Cmaker:
    self.target_directory = ""
    self.project_name = ""
    self.library_name = ""

    def __init__(self, target_directory: str, project_name: str, library_name: str):
        self.target_directory = target_directory
        self.project_name = project_name
        self.library_name = library_name

    def setFiles():


    def write(self):
        cmake_path = os.path.join(target_directory, 'CMakeLists.txt')
    
        with open(cmake_path, 'w') as cmake_file:
            cmake_file.write(self.getHead())
            cmake_file.write(self.getTail())
    
        print(f'CMakeLists.txt has been created at {cmake_path}')

    def getHead(self):
        return f"""cmake_minimum_required(VERSION 3.14)
project({self.project_name})

# Specify the C++ standard
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

"""
    
    def getTail(self):
        return f"""
# Add a library target
add_library({self.library_name}  SHARED ${{{{SOURCE_FILES}}}} ${{{{HEADER_FILES}}}})    

# Link libraries (if any)
target_link_libraries({self.library_name} PRIVATE some_other_library)

# Include directories
target_include_directories({self.library_name} PUBLIC ${{PROJECT_SOURCE_DIR}}/include)
"""







def create_cmake_lists(target_directory, project_name, library_name):


    cmake_path = os.path.join(target_directory, 'CMakeLists.txt')
    
    with open(cmake_path, 'w') as cmake_file:
        cmake_file.write(content)
    
    print(f'CMakeLists.txt has been created at {cmake_path}')

# Create the CMakeLists.txt
create_cmake_lists(args.target_directory, args.project_name, args.library_name)