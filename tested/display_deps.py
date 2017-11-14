import os.path
import glob
import re

files = glob.glob('languages/python3/*.py')
with open('deps.dot','w') as outfile:
    outfile.write("digraph modules {\n")
    for filename in files:
        with open(filename,'r') as f:
            basename = os.path.splitext(os.path.basename(filename))[0]
            for line in f:
                match = re.search(r"from \. import (.*)$", line)
                if match:
                    linked_modules = match.group(1).split(',')
                    for module in linked_modules:
                        text = "  {} -> {};\n".format(basename, module.strip())
                        outfile.write(text)
                match = re.search(r"from \.(.+) import", line)
                if match:
                    module = match.group(1)
                    text = "  {} -> {};\n".format(basename, module.strip())
                    outfile.write(text)                                        
    outfile.write("}")

