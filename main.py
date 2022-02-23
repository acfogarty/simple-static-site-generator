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
            html = html.replace(f'{{{{{m}}}}}', value)
        except KeyError:
            message = f'Warning! Could not find variable {m} in components_data. Will try again in parent component.'
            print(message)

    return html


def include_components(html: str,
                       components_html: dict,
                       include_elem: lxml.etree.Element):
    """
    For one include tag with locationtag XXX, replace all
    instances of {% include XXXX} with the html of the
    components listed in the include tag.

    e.g. for
    <include>
      <locationtag>topposts</locationtag>
      <sourcecomponent>toppost_dogs</sourcecomponent>
      <sourcecomponent>toppost_cats</sourcecomponent>
    </include>

    the concatenation of the html of toppost_cats and toppost_dogs
    is inserted at {% include topposts}

    for
    <include>
      <locationtag>topposts</locationtag>
      <sourcefile>dogs.html</sourcefile>
    </include>

    the contents of the file dogs.html is inserted at {% include topposts}

    :param html: html of the component being constructed
    :param components_html: html of all previously constructed components
    :param include_elem: the xml within the <include> tags
    """

    locationtag = get_text_from_xml_element(include_elem, 'locationtag')

    if include_elem.find('sourcecomponent') is not None:
        html_to_insert = get_html_from_sourcecomponents(include_elem, components_html)
    elif include_elem.find('sourcefile') is not None:
        html_to_insert = get_html_from_sourcefile(include_elem)
    else:
        message = f'Cannot find sourcefile or sourcecomponent in {lxml.etree.tostring(include_elem)}'
        raise KeyError(message)

    # insert new html in the component html
    pattern = f'({{% include {locationtag}}})'
    matches = re.findall(pattern, html)
    for locationtag_match in matches:
        html = html.replace(locationtag_match, html_to_insert)

    return html


def get_html_from_sourcefile(include_elem):
    '''
    :param include_elem: xml element of format:
      <include>
        <sourcefile>nameA</sourcefile>
        <sourcefile>nameB</sourcefile>
      </include>
    '''

    # get all files to include
    filenames = get_text_from_xml_element(include_elem,
                                          'sourcefile',
                                           findall=True)

    html_to_insert = ''
    for filename in filenames:
        with open(filename, 'r') as f:
            html = f.read()
            html_to_insert += html

    return html_to_insert


def get_html_from_sourcecomponents(include_elem, components_html):
    '''
    :param include_elem: xml element of format:
      <include>
        <sourcecomponent>nameA</sourcecomponent>
        <sourcecomponent>nameB</sourcecomponent>
      </include>
    :param components_html: for example
      {'nameA': '<p>stuff</p>', 'nameB': '<h2>heading</h2>'
    '''

    # get all sub-components to include
    subcomponentnames = get_text_from_xml_element(include_elem,
                                                  'sourcecomponent',
                                                  findall=True)

    # get html of all the sub-components
    html_to_insert = ''
    for subcomponentname in subcomponentnames:

        try:
            html_to_insert += components_html[subcomponentname]
        except KeyError:
            message = f'No component named {subcomponentname}'
            raise KeyError(message)

    return html_to_insert


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
        message = f'Could not find key {varsource} in variables file.'
        raise KeyError(message)

    # for all <include> blocks in structure file, include components in {% include name}
    include_elems = component.findall('include')
    for include_elem in include_elems:
        html = include_components(html, components_html, include_elem)

    # insert variables in {{}}
    # Note: we insert variables after including components, so that
    # variables can also be inserted in the included components
    # if not already done
    html = insert_variables(html, component_data)

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

    validate_html(html)

    with open(filename, 'w') as f:
        print(f'Writing to {filename}')
        f.write(html)


def validate_html(html):
    """
    Make sure there are no remaining unreplaced {} tags
    """
    pattern = '({\w+})'
    matches = re.findall(pattern, html)

    for m in matches:
        print(f'Warning! "{m}" not replaced in html')


if __name__ == '__main__':
    main()
