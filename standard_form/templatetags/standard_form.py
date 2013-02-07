from classytags.arguments import Argument, KeywordArgument, Flag
from classytags.core import Tag, Options
from django import template
from django.forms import TextInput, Select, CheckboxSelectMultiple, SelectMultiple, CheckboxInput, RadioSelect
from django.template.loader import render_to_string

register = template.Library()

def get_input_type(widget_type):
    if widget_type == TextInput:
        input_type = 'text'
    elif widget_type == Select or widget_type == SelectMultiple:
        input_type = 'select'
    elif widget_type == CheckboxSelectMultiple or widget_type == CheckboxInput or widget_type == RadioSelect:
        input_type = 'radiocheck'
    else:
        input_type = 'text'
    return input_type

def booleanify(arg):
    if arg is True or arg.lower() == 'yes' or arg.lower() == 'true' or arg.lower() == 'on':
        return True
    if arg is False or arg.lower() == 'no' or arg.lower() == 'false' or arg.lower() == 'off':
        return False

def get_options(args):
    options = dict()
    if args:
        args = args.split(' ')
        options = {
            'placeholder_from_label': 'placeholder_from_label' in args,
            'no_required': 'no_required' in args,
            'no_required_helper': 'no_required_helper' in args,
            'no_help_text': 'no_help_text' in args,
            'no_error_text': 'no_error_text' in args,
        }
    return options


class StandardWidget(Tag):
    name = 'standard_widget'
    options = Options(
        Argument('field'),
        Argument('options', required=False, default=None),
        KeywordArgument('custom_class', required=False, default=None),
        KeywordArgument('placeholder', required=False, default=None),
        KeywordArgument('input_type', required=False, default=None),
    )

    def render_tag(self, context, field, options, custom_class, placeholder, input_type):
        args = get_options(options)
        placeholder = placeholder.get('placeholder')
        input_type = input_type.get('input_type')
        custom_class = custom_class.get('custom_class')
        custom_classes = custom_class.split(' ')
        attrs = {}
        if placeholder:
            attrs['placeholder'] = placeholder
        elif args.get('placeholder_from_label', False):
            attrs['placeholder'] = field.label
        if not args.get('no_required', False) and field.field.required:
            attrs['required'] = 'required'

        if field.field.show_hidden_initial:
            return field.as_widget(attrs=attrs) + field.as_hidden(only_initial=True)

        # get input type
        if not input_type:
            input_type = get_input_type(type(field.field.widget))

        # set the classes
        classes = ['input-%s' % input_type]
        if input_type == 'radiocheck' and 'input-block' in custom_classes:
            custom_classes.remove('input-block')
        if field.errors:
            classes += ['input-error']
        if custom_classes:
            classes += custom_classes
        attrs['class'] = ' '.join(classes)

        return field.as_widget(attrs=attrs)

register.tag(StandardWidget)


class StandardField(Tag):
    name = 'standard_field'
    options = Options(
        Argument('field'),
        Argument('options', required=False, default=None),
        KeywordArgument('custom_class', required=False, default=None),
        KeywordArgument('placeholder', required=False, default=None),
        KeywordArgument('label', required=False, default=None),
        KeywordArgument('input_type', required=False, default=None),
        'using',
        Argument('template', required=False, default='standard_form/field.html'),
    )

    def render_tag(self, context, field, options, custom_class, placeholder, label, input_type, template):
        placeholder = placeholder.get('placeholder')
        custom_class = custom_class.get('custom_class')
        label = label.get('label')
        if label:
            field.label = label
        if input_type:
            input_type = input_type.get('input_type')
        else:
            input_type = get_input_type(type(field.field.widget))
        args = get_options(options)
        ctx = {
            'field': field,
            'options': options,
            'no_required_helper': args.get('no_required_helper', False),
            'no_help_text': args.get('no_help_text', False),
            'no_error_text': args.get('no_error_text', False),
            'custom_class': custom_class,
            'placeholder': placeholder,
            'input_type': input_type,
        }
        output = render_to_string(template, ctx)
        return output

register.tag(StandardField)


class StandardForm(Tag):
    name = 'standard_form'
    options = Options(
        Argument('form'),
        Argument('options', required=False, default=None),
        KeywordArgument('custom_class', required=False, default=None),
        'using',
        Argument('template', required=False, default='standard_form/form.html'),
    )

    def render_tag(self, context, form, options, custom_class, template):
        custom_class = custom_class.get('custom_class')
        ctx = {
            'form': form,
            'options': options,
            'custom_class': custom_class,
        }
        output = render_to_string(template, ctx)
        return output

register.tag(StandardForm)

