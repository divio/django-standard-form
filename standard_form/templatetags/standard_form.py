from classytags.arguments import Argument, KeywordArgument
from classytags.core import Tag, Options
from classytags.helpers import InclusionTag
from django import template
from django.forms import (Select, CheckboxSelectMultiple, Textarea, RadioSelect,
                          SelectMultiple, CheckboxInput, MultiWidget)
from django.template.loader import render_to_string

register = template.Library()


def get_input_type(widget_type):
    if widget_type in [Select, SelectMultiple]:
        return 'select'
    if widget_type in [CheckboxSelectMultiple, RadioSelect]:
        return 'radiocheck-list'
    if widget_type is Textarea:
        return 'textarea'
    if widget_type is CheckboxInput:
        return 'radiocheck'
    if issubclass(widget_type, MultiWidget):
        return 'multi'
    return 'text'


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
            'no_label': 'no_label' in args,
            'readonly': 'readonly' in args,
            'disabled': 'disabled' in args,
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
        KeywordArgument('input_id', required=False, default=None),
    )

    def render_tag(self, context, field, options, custom_class, placeholder, input_type, input_id):
        args = get_options(options)
        input_id = input_id.get('input_id')
        placeholder = placeholder.get('placeholder')
        input_type = input_type.get('input_type')
        custom_class = custom_class.get('custom_class')
        custom_classes = []
        if custom_class:
            custom_classes = custom_class.split(' ')

        attrs = {}

        if input_id:
            attrs['id'] = input_id
        if placeholder:
            attrs['placeholder'] = placeholder
        elif args.get('placeholder_from_label', False):
            attrs['placeholder'] = field.label
        if not args.get('no_required', False) and field.field.required:
            attrs['required'] = 'required'
        if args.get('readonly', False):
            attrs['readonly'] = 'readonly'
        if args.get('disabled', False):
            attrs['disabled'] = 'disabled'

        if field.field.show_hidden_initial:
            return field.as_widget(attrs=attrs) + field.as_hidden(only_initial=True)

        # get input type
        if not input_type:
            input_type = get_input_type(type(field.field.widget))

        # multi field has many widgets we don't want to replace attrs in all
        if input_type == 'multi':
            return field.as_widget()

        # set the classes
        input_class = input_type
        if input_type == 'radiocheck-list':
            input_class = 'radiocheck'

        # TODO: we have to get classes from widget in first place
        classes = ['input-%s' % input_class]
        if 'radiocheck' in input_type:
            if 'input-mini' in custom_classes:
                custom_classes.remove('input-mini')
            if 'input-small' in custom_classes:
                custom_classes.remove('input-small')
            if 'input-medium' in custom_classes:
                custom_classes.remove('input-medium')
            if 'input-large' in custom_classes:
                custom_classes.remove('input-large')
            if 'input-block' in custom_classes:
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
        field_classes = ''
        if input_type == 'radiocheck-list':
            field_classes = 'radiocheck-list'
        args = get_options(options)
        ctx = {
            'field': field,
            'options': options,
            'no_required_helper': args.get('no_required_helper', False),
            'no_help_text': args.get('no_help_text', False),
            'no_error_text': args.get('no_error_text', False),
            'no_label': args.get('no_label', False),
            'custom_class': custom_class,
            'placeholder': placeholder,
            'input_type': input_type,
            'field_classes': field_classes,
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


class StandardSubmit(InclusionTag):
    name = 'standard_submit'
    template = 'standard_form/submit.html'
    options = Options(
        KeywordArgument('display_name', required=False, default=None),
    )

    def get_context(self, context, **kwargs):
        """
        Returns the context to render the template with.
        """
        return {'submit_display_name': kwargs['display_name'].get('display_name')}

register.tag(StandardSubmit)
