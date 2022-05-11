import json

from xmltodict3 import XmlTextToDict

def main():
    with open('../assets/TestFiles/site1_correction.xml') as file:
        text = file.read()
        result = XmlTextToDict(text, ignore_namespace=True).get_dict()

        print(json.dumps(result))

main()