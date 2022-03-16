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

# Variable insertion

Variable values are defined in `contents.json`.

In each component in `structure.xml`, use the `<varsource>` tag to specify which top-level key in `contents.json` to use for the variable values in that component. For example:

```html
<!-- template.html -->
<p>This is a paragraph about {{subject}} in the html file.</p>
```

```xml
<component>
  <name>toppost_dogs</name>
  <varsource>blogpost_dogs</varsource>
  <template>template.html</template>
</component>
<component>
  <name>toppost_cats</name>
  <varsource>blogpost_cats</varsource>
  <template>template.html</template>
</component>
```

```json
{
  "blogpost_dogs": {
    "subject": "Husky dogs"
  },
  "blogpost_cats": {
    "subject": "black cats"
  }
}
```

If no `varsource` tag is present in the xml, the `default` key will be used.

# To add a page:

* create html template files for the content of all new components (including variables in `site_structure.json` if necessary)
* in `structure.xml`, create the component(s)
* in `structure.xml`, create a page that uses the component(s) (including variables in `site_structure.json` if necessary)
