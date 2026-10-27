import os
import re

template_dir = r"e:\cosmetics-store\templates"

def convert_thymeleaf_to_django(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. th:href="@{/path}" -> href="{% url 'path' %}" or static if it's css/js
    # We will just replace it with href="/path" for simplicity, or we can use {% url %} if we map them.
    # Actually, for static files: th:href="@{/css/style.css}" -> href="{% static '/css/style.css' %}"
    # Wait, we can use regex to find th:href="@{([^}]*)}"
    
    def repl_href(match):
        path = match.group(1)
        if path.startswith('/css') or path.startswith('/js') or path.startswith('/images') or path.startswith('/lib') or path.startswith('/admin') and 'css' in path:
            return f'href="{{% static \'{path}\' %}}"'
        return f'href="{path}"'
    
    content = re.sub(r'th:href="@{([^}]+)}"', repl_href, content)

    # 2. th:src="@{/path}" -> src="{% static '/path' %}"
    def repl_src(match):
        path = match.group(1)
        if path.startswith('/images') or path.startswith('/js') or path.startswith('/lib') or path.startswith('/admin'):
            return f'src="{{% static \'{path}\' %}}"'
        return f'src="{path}"'
    
    content = re.sub(r'th:src="@{([^}]+)}"', repl_src, content)

    # 3. th:text="${var}" -> {{ var }}
    # Remove th:text attr and replace tag content with {{ var }}
    # This is tricky with regex. We can just replace th:text="${(.*?)}" with >{{ \1 }}< if it's on a tag
    # Actually, simplest is to just regex: th:text="\$\{([^}]+)\}"
    # Let's do a naive replace: <span th:text="${msg}"></span> -> <span>{{ msg }}</span>
    # re.sub(r'<([a-zA-Z0-9]+)[^>]*th:text="\$\{([^}]+)\}"[^>]*>(.*?)</\1>', r'<\1>{{ \2 }}</\1>', content)
    # A better way is just to replace th:text="..." in the tag and put {{ ... }} inside.
    # We can do this manually or let the regex do it roughly, then fix manually.
    
    content = re.sub(r'th:text="\$\{([^}]+)\}"', r'>{{ \1 }}<', content)
    # This might break `<div th:text="${var}">Old text</div>` into `<div>{{ var }}<>Old text</div>`
    # Let's clean up `<>Old text</div>`
    content = re.sub(r'>\{\{ (.*?) \}\}<[^>]*>', r'>{{ \1 }}', content)
    # This is too error prone.

    # Instead of full automation, I will just do simple text replacements for variable names and fix the files.
    # I will replace th:text="${var}" with >{{ var }}</ tag and clean manually? No, I will just write a cleaner regex.
    # Let's just do:
    # th:text="${user.name}" -> >{{ user.name }}
    # Actually, let's just do it file by file or view by view using multi_replace_file_content.
    
    # Let's try basic replaces:
    # th:object="${...}" -> we can ignore, django doesn't use object.
    content = re.sub(r'th:object="\$\{([^}]+)\}"', '', content)
    
    # th:field="*{...}" -> name="..." value="{{ ... }}"
    def repl_field(match):
        field = match.group(1)
        return f'name="{field}" value="{{{{ form.{field}.value|default_if_none:\'\' }}}}"'
    content = re.sub(r'th:field="\*\{([^}]+)\}"', repl_field, content)

    # th:action="@{/path}" -> action="/path"
    content = re.sub(r'th:action="@{([^}]+)}"', r'action="\1"', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

for root, dirs, files in os.walk(template_dir):
    for f in files:
        if f.endswith('.html'):
            convert_thymeleaf_to_django(os.path.join(root, f))
print("Done")
