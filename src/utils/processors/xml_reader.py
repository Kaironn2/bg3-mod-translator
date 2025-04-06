from xml.etree import ElementTree as ET


class XMLReader:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.root = self.get_xml_root()
        self.content = self.get_content()


    def get_xml_root(self) -> ET.Element:
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        return root


    def get_content(self):
        temp = []
        for content in self.root.findall('content'):
            temp.append(content.text)
        return temp
    
