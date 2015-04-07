"""
Add support of `optparse.OptionGroup` for Django commands.

Example:

    class MyCommand(AdvancedCommand):
        option_groups = AdvancedCommand.option_groups + (
            make_option_group(
                'Option group title',
                description='Option group description',
                option_list=(
                    make_option('-option', help='Some option',),
                    # additional group options...
                ),
            ),
            # additional option groups...
        )
"""
from django.core.management import BaseCommand, OptionParser
from optparse import OptionGroup


def make_option_group(title, description=None, option_list=None):
    option_list = option_list or []
    return (title, description), option_list


class AdvancedCommand(BaseCommand):

    """
        Class: AdvancedCommand
        Extended Django's BaseCommand with option groups
    """

    option_groups = ()

    def create_parser(self, prog_name, subcommand, *args, **kwargs):
        parser = OptionParser(prog=prog_name, usage=self.usage(subcommand),
                              # conflict_handler="resolve",
                              version=self.get_version(),
                              option_list=self.option_list)
        for option_group_args, option_list in self.option_groups:
            option_group = OptionGroup(parser, *option_group_args)
            option_group.add_options(option_list)
            parser.add_option_group(option_group)
            option_group = None
        return parser
