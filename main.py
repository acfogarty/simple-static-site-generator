from fileinput import filename
import json
import re

import lxml.etree


def main():

    structure_file = "structure.xml"
    variables_file = "contents.json"
    
    with open(variables_file) as f:
        variable_data = json.load(f)
    
    tree = lxml.etree.parse(structure_file)

    components_html = build_components(tree, variable_data)

    build_pages(tree, variable_data, components_html)


def insert_variables(html: str, components_data: dict):
    """
    Replace all instances of {{XXX}} by the value of the
    key XXX in components_data
    """

    pattern = '{{(\w+)}}'
    matches = re.findall(pattern, html)
    for m in matches:
        try:
            value = components_data[m]
        except KeyError:
            message = f'Could not find variable {m} in components_data'
            raise KeyError(message)
        html = html.replace(f'{{{{{m}}}}}', value)

    return html


def include_components(html: str, components_html: dict, include_elem: lxml.etree.Element):
    """
    Replace all instances of {% include XXXX} with the html of the
    components listed in the include tag.

    e.g. for
    <include>
      <locationtag>topposts</locationtag>
      <componentname>toppost_dogs</componentname>
      <componentname>toppost_cats</componentname>
    </include>

    the concatenation of the html of toppost_cats and toppost_dogs is inserted at {% include topposts}

    :param html: html of the component being constructed
    :param components_html: html of all previously constructed components
    """

    locationtag = get_text_from_xml_element(include_elem, 'locationtag')

    # get all sub-components to include
    subcomponentnames = get_text_from_xml_element(include_elem, 'componentname', findall=True)

    # get html of all the sub-components
    concatenatedhtml = ''
    for subcomponentname in subcomponentnames:

        try:
            concatenatedhtml += components_html[subcomponentname]
        except KeyError:
            message = f'No component named {subcomponentname}'
            raise KeyError(message)

    # insert sub-components html in the component html
    pattern = f'({{% include {locationtag}}})'
    matches = re.findall(pattern, html)
    for locationtag_match in matches:
        html = html.replace(locationtag_match, concatenatedhtml)

    return html


def get_text_from_xml_element(element: lxml.etree._Element,
                              tag: str,
                              findall=False,
                              optional=False):
    """
    e.g. element = <outer><inner>word</inner></outer>
         tag = 'inner'
         Returns 'word'

    If findall==True, return list of all tags found.
    If findall==False, only return the first tag.

    :rtype: str or List[str]
    """

    if findall:
        obj = element.findall(tag)
    else:
        obj = element.find(tag)

    if obj is None:
        if optional:
            return 'default'
        else:
            raise KeyError(f"Tag '{tag}' not found in {lxml.etree.tostring(element)}")

    if findall:
        return [o.text for o in obj]
    else:
        return obj.text


def build_component(component: lxml.etree.Element,
                    variable_data: dict,
                    components_html: dict):
    """
    :param variable_data: ???
    :param components_html: all previous constructed components
                            (key = component name, value = html string)
    """

    name = get_text_from_xml_element(component, 'name')
    print(f'Building component {name}')

    template = get_text_from_xml_element(component, 'template')
    # TODO handle file not found
    with open(template) as f:
        html = f.read()

    varsource = get_text_from_xml_element(component, 'varsource', optional=True)
    try:
        component_data = variable_data[varsource]
    except KeyError:
        message = f'Could not find key {varsource} in variables file'
        raise KeyError(message)

    # insert variables in {{}}
    html = insert_variables(html, component_data)

    # for all <include> blocks in structure file, include components in {% include name}
    include_elems = component.findall('include')
    for include_elem in include_elems:
        html = include_components(html, components_html, include_elem)

    return name, html


def build_components(tree, variable_data):

    components_html = {}

    for component in tree.xpath("/root/components/component"):

        name, html = build_component(component, variable_data, components_html)

        components_html[name] = html

    return components_html


def build_pages(tree, variable_data, components_html):

    for page in tree.xpath("/root/pages/page"):

        build_page(page, variable_data, components_html)


def build_page(component: lxml.etree.Element,
               variable_data: dict,
               components_html: dict):

    filename = get_text_from_xml_element(component, 'filename')

    name, html = build_component(component, variable_data, components_html)

    with open(filename, 'w') as f:
        f.write(html)

if __name__ == '__main__':
    main()
