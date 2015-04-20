# Translate your django apps without gettext

# Why?

Translations in Django are full of thorns:

* You may only use `.po` files
* You have to compile translations after each change (`./manage.py makemessages`)
* Ah and then did you ever have to restart your dev server after running `makemessages`?
* No easy way to debug (does "why translations are not appearing" sounds familiar?)
* If you use plural forms, there is a lot of redundant code to write:

  ```
  {% blocktrans %}
    I have one apple
  {% plural %}
    I have {{ count }} apples
  {% endblocktrans %}
  ```

* You cannot customize much

# Enter django_translate

* It's a wrapper over extensible [python_translate](https://github.com/adamziel/python_translate)
* No gettext dependency
* Use any file format you want to
    * json, yml, po, and mo supported
    * easily add support for your own file format
* No compilation. At all. Ever. Again.
* In DEBUG you may enable auto reloading of translations, never restart dev server again.
* In DEBUG you may enable strict mode - you'll see an exception when translation cannot be found. Guess no more.
* Console command to validate all translations in your project or collect translation strings.
* Simple pluralization:
  ```
  {% tranzchoice "i_have_apples" number 44 %}
  ```
* Customize easily

# Examples:

1. [basic django integration](https://github.com/adamziel/django_translate/tree/master/examples/example_basic)
1. [drop in replacement for django translations*](https://github.com/adamziel/django_translate/tree/master/examples/example_dropin)


* See [Other Notes](https://github.com/adamziel/python_translate#Other_Notes), this functionallity is experimental and may not always work.


# Installation

1. Install the package: `pip install django_translate`
1. Add `django_translate` to `INSTALLED_APPS`
1. Modify `MIDDLEWARE_CLASSES` as such:

```python
MIDDLEWARE_CLASSES = (
    # ... your other middlewares
    
    # required:
    "django.middleware.locale.LocaleMiddleware",

    # add this one somewhere afterthe one above:
    "django_translate.middleware.LocaleMiddleware",
    
    # ... your other middlewares
)
```

Done!


If you want to make django use this application as a backend for all it's translations
(including built-in `{% trans %}` and `{% blocktrans %}` tags), you have to:

1. Make sure that `django_translate` is a **first** app in `INSTALLED_APPS`
1. Set `TRANZ_REPLACE_DJANGO_TRANSLATIONS` to True in settings.py
1. Cross your fingers, this functionallity is experimental and may not always work.


# Quick start

1. Create a file `tranz/messages.en.yml` in your django app directory:

```yml
# tranz/messages.en.yml
"hello_world": "Hello world!"
```

1. Create a view/template pair and use the following code as template.html:

```
{% use tranz %}
{% tranz "hello_world" into "en" %}
```

1. Run dev server and visit a view that renders this template

Ta-da! It works, and you didn't have to compile anything!

# What's next?

Below you will find short and sweet documentation

If it leaves you with any questions, make sure to read `python_translate` docs:  
https://python-translate.readthedocs.org/

A few paragraphs of the following README are derived from Symfony2 documentation:  
https://github.com/symfony/symfony-docs/  
This README is licensed under [CC BY-SA 3.0](http://creativecommons.org/licenses/by-sa/3.0/) while the code is licensed under MIT license (in LICENSE file)

## Domains

Message files are organized into the different locales that they translate. The message files can also
be organized further into “domains”. The default domain is messages.

For example, suppose that, for organization, translations were split into three different domains: messages, admin
and navigation. The French translation would be loaded from the following files:

```
* APP_PATH/tranz/messages.fr.yml:
    "Create new blog post": "Créer un nouveau blog"
* APP_PATH/tranz/admin.fr.yml`
* APP_PATH/tranz/navigation.fr.yml:
    "Go to homepage": "La page d'accueil"
```

When translating strings that are not in the default domain (messages), you must specify the domain:

```python
from django_translate.translations import tranz
tranz('Create new blog post') # loaded from messages.fr.yml
tranz('Go to homepage', domain="navigation") # loaded from navigation.fr.yml
```

## Discovery

Translation files are automatically discovered using this simple algorithm:

* for each app in `INSTALLED_APPS`, scan directory `APP_PATH/tranz`
* load all supported files matching the pattern {domain}.{lang}.{format}

So a file named `navigation.fr.yml` would be loaded using `YamlLoader` into domain `navigation` of locale `fr`.
Note that there is no compilation step. django_translate loads exactly what's in the file.

You may also specify your own scannable paths using the `TRANZ_LOCALE_PATHS` setting in settings.py

Supported formats are specified using the `TRANZ_LOADERS` setting.

## Yaml and other data formats

The recommended format for storing your translations is Yaml. That being said, json, po, and mo file are supported as well.
Yaml has some perks, for example the following files are considered the same:

```yml
blog:
    post:
        delete: "Remove this post"
        create: "Create a new post"
```

```yml
blog.post.delete: "Remove this post"
blog.post.create: "Create a new post"
```

because the first one is flattened using a dot (`.`) as a separator. This way you don't have to repeat yourself so much.
Data provided in other formats is not flattened.
If you want to use a file format that is not supported by django_translate, read this:
https://python-translate.readthedocs.org/en/latest/custom_formats.html

For more information about different data formats, see the `python_translate` documentation:
https://python-translate.readthedocs.org/

## Translating views:

In order to translate messages in your views.py file, you need to use `tranz` function provided by this app:

```python
from django_translate.services import tranz

def my_view(request):
    return tranz("hello_world") # returns Hello world!
```

`tranz` function takes a few arguments:
```python
def tranz(id, parameters=None, domain=None, locale=None):
    # ...
```

Note that it's simply a reference to `Translator.trans` from [python_translate](https://github.com/adamziel/python_translate)
`id` is the message ID - in this case it's `"Hello world!"`
`parameters` is used for formatting the message
`domain` is the message's domain, it defaults to `messages` (note how we stored translations in messages.en.yml)
`locale` gives you the possibility to override current default locale (defaults to `request.LANGUAGE_CODE`)


## Placeholders

You may format your messages using placeholders:

```yml
# APP_PATH/tranz/messages.en.yml
hello: "Hello {name}"
```

```python
# views.py
from django_translate.translations import tranz
tranz('hello', {"Name": "Adam"})
```

For more details about formatting, check `python_translate` documentation:  
https://python-translate.readthedocs.org/en/latest/usage.html#message-placeholders


## Pluralization

When a translation has different forms due to pluralization, you can provide all the forms as a string separated by a pipe (`|`):

```yml
# APP_PATH/tranz/messages.en.yml
posts_count: "You have one post|You have {count} posts"
```

To translate pluralized messages, use the `tranzchoice` function:

```python
# views.py
from django_translate.translations import tranzchoice
tranzchoice('posts_count', 10)
```

The second argument (10 in this example) is the number of objects being described and is used to determine which translation
to use and also to populate the {count} placeholder.

Based on the given number, the translator chooses the right plural form for given locale. Different languages have a different
number of plural forms.

For more details about pluralization, check `python_translate` documentation:  
https://python-translate.readthedocs.org/en/latest/usage.html#pluralization


## Translating templates:

`django_translate` provides two templatetags: `tranz` and `tranzchoice`. They are a simple wrappers for functions with the same name
from `django_translate.services` module.

Example:

```yml
# messages.en.yml:
hello_world: "Hello world!"
hi_name: "Hi {name}!"
posts_count: "You have one post|You have {count} posts"
posts_count_name: "{name} has one post|{name} has {count} posts"
```

```
# template.html:
{% use tranz %}
{% tranz "hello_world" %}

<!-- Specify language -->
{% tranz "hello_world" into "en" %} 

<!-- Specify domain -->
{% tranz "hello_world" from "messages" %}

<!-- Format message -->
{% tranz "hi_name" name="adam" %}

<!-- Everything together -->
{% tranz "hi_name" name="adam" from "messages" into "en" %}

<!-- Pluralization -->
{% tranzchoice "posts_count" number 10 %}

<!-- Pluralization + everything else -->
{% tranzchoice "posts_count_name" number 10 name="adam" from "messages" into "en" %}
```


# Development

## Automatic translations reloading + clear exceptions whenever message is not found:

If you don't want to reload your dev server every time a translation file is changed,
just add this to your settings.py:

```python
# settings.py
from python_translate.translations import DebugTranslator
TRANZ_TRANSLATOR_CLASS = DebugTranslator
```

It will take care of reloading messages for you.


## Collecting translations strings from templates and python files:

Django has the `collectmessages` command, similarly django_translate provides a `tranzdump` command
that will parse your python and html files and collect all translation strings:
```bash
python manage.py tranzdump --app=your_app --format=yml --dump-messages --force
```

For more details about this command, type `python manage.py help tranzdump`.

## Validating your translations:

You may want to check if all translation strings referenced in views and templates. In bare django you need to
manually visit visit every URL. This is unacceptable, so django_translate provides a handy command that parses
your source tree and compares it to translation files:
```bash
python manage.py tranzvalidate --app=your_app
```

For more details about this command, type `python manage.py help tranzvalidate`.


# Other notes

Django Translate may serve as a drop-in replacement for django translations, however at the moment it does not support contextual markers (`msgctxt`).  
Also monkeypatching django translations it is not tested very well, you may run into issues. You have been warned...


# Settings

The following settings are available:

## TRANZ_REPLACE_DJANGO_TRANSLATIONS

If set to True, django_translate will monkeypatch django translations to use `Translator` instance
as a backend for translations. It will still load all your *.po translations, and even those provided
by django. In addition to them, you will be able to use `tranz` templatetag and all other perks.

**Default:** `False`


## TRANZ_TRANSLATOR_CLASS

Translator type used to create `Translator` instance

**Default:** `python_translate.translations.Translator`

## TRANZ_SEARCH_LOCALE_IN_APPS
Should this app look for translation files in every app from `INSTALLED_APPS`?

**Default:** `True`

## TRANZ_DIR_NAME
If `TRANZ_SEARCH_LOCALE_IN_APPS` is set to `True`, `django_translate` will look for translation files in
`APP_DIRECTORY + "/" + TRANZ_DIR_NAME` of every installed application.

**Default:** `"tranz"`


## TRANZ_LOCALE_PATHS
Additional paths to look for translation files in.

**Default:** `[]`


## TRANZ_DEFAULT_LANGUAGE
Global default language for translator. This setting is not useful at all if you use `django_translate.middleware.LocaleMiddleware`
because default language will be picked on per-request basis.

**Default:** `"en"`

## TRANZ_LOADER_CLASS
Loader type used to discover and load translation files. The default one does nothing
besides invoking each loader referenced in `TRANZ_LOADERS`

**Default:**
```python
glue.TransationLoader
```

## TRANZ_LOADERS
Dictionary of `Loader` instances used by TRANZ_LOADER_CLASS

If you want to use `po`/`mo` files, you have to override this setting, and
add `loaders.PoLoader`/`loaders.MoLoader` instances.

If you want to use a file format that is not supported by django_translate, read this:
https://python-translate.readthedocs.org/en/latest/custom_formats.html

**Default:**
```python
{
    "dict": loaders.DictLoader(),
    "json": loaders.JSONFileLoader(),
    "yml": loaders.YamlFileLoader()
}
```

## TRANZ_EXCLUDED_DIRS
List of directories that will never by scanned by `tranzdump` and `tranzvalidate` console commands.

## TRANZ_DUMPERS

Dumpers supported by `tranzdump` command

**Default:**
```python
{
    "yml": dumpers.YamlFileDumper(),
    "json": dumpers.JSONFileDumper(),
}
```

## TRANZ_WRITER_CLASS

TranslatorWriter type used to create `TranslatorWriter` instance used by `tranzdump` console command

**Default:** `python_translate.glue.TranslationWriter`

## TRANZ_EXTRACTOR_CLASS

Extractor type by `tranzdump` and `tranzvalidate` console commands

**Default:** `python_translate.base.ChainExtractor`

## TRANZ_EXTRACTORS

Sub-extractor instances used by TRANZ_EXTRACTOR_CLASS
**Default:**
```python
{
    "template": django_translate.extractors.django_template.DjangoTemplateExtractor(),
    "py": python_translate.extractors.python.PythonExtractor()
}
```
