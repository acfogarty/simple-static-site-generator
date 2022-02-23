# Simple static site generator

Usage:
```
python main.py
```

Website structure is in `structure.xml`.

Variable values are in `contents.json`.

# Pages and components

The two basic building blocks are pages and components.

### Page

Each .html file in the static website corresponds to one <page> block in the structure.xml file.

Specification of a page:
```
<page>
  <name>bloghome</name>
  <filename>blog.html</filename>
  <template>base_template.html</template>
  <varsource>blog_home</varsource>
  <description>Optional </description>
  <include>
    ...
    ...
  </include>
</page>
```

filename: file to which the page will be written

template: file from which the html template will be read

description [optional]: optional description of the page

varsource [optional]: section in contents.json containing values
                      to be substituted for '{{key}}' in html

include [optional]: in the html, replace {% include locationtag}
                    by the concatenation of the html of all the listed
                    components (see below)

A page can contain multiple 'include' blocks.

### Components

Components are snippets of html for insertion into pages.

Specification of a component:
```
<component>
  <name>blog_sidebar</name>
  <template>sidebar_template.html</template>
  <varsource>blog_sidebar</varsource>
  <description>Top Posts sidebar</description>
  <include>
    ...
    ...
  </include>
</component>
```

name: name used to identify the component

template: file from which the html template will be read

description [optional]: optional description of the component

varsource [optional]: section in contents.json containing values
                      to be substituted for '{{key}}' in html

include [optional]: in the html, replace {% include locationtag}
                    by the concatenation of the html of all the listed
                    components (see below)

A component can contain multiple 'include' blocks.

### Include blocks

'include' blocks are used to insert a html string at a specific location in another html string

The html to be inserted can come from another component ('sourcecomponent' mechanism) or be loaded from a html file ('sourcefile' mechanism).

Specification of an include block:
```
<include>
  <locationtag>content</locationtag>
  <sourcecomponent>blog_link1</sourcecomponent>
  <sourcecomponent>blog_link2</sourcecomponent>
<include>
```

The html string of the `blog_link1` and `blog_link2` components will be inserted at `{% include content}` in the parent html.

```
<include>
  <locationtag>content</locationtag>
  <sourcefile>example.txt</sourcefile>
<include>
```

The contents of the file `example.txt` will be inserted at `{% include content}` in the parent html.
