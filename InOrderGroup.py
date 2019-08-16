from typing import Iterable
from typing import Union

import launch

from launch import Action
from launch import LaunchContext
from launch import SomeSubstitutionsType
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.utilities import normalize_to_list_of_substitutions, perform_substitutions


@launch.frontend.expose_action('in_order_group')
class InOrderGroup(Action):

    def __init__(
        self,
        actions: Iterable[Action],
        continue_after_fail: Union[bool, SomeSubstitutionsType]
    ):
        self.__actions = actions
        self.__continue_after_fail = continue_after_fail

    @classmethod
    def parse(cls, entity: launch.frontend.Entity, parser: launch.frontend.Parser):
        _, kwargs = super().parse(entity, parser)
        continue_after_fail = entity.get_attr(
            'continue_after_fail',
            data_type=Union[bool, str],
            optional=True
        )
        if isinstance(continue_after_fail, str):
            continue_after_fail = parser.parse_substitution(continue_after_fail)
        if continue_after_fail is not None:
            kwargs['continue_after_fail'] = continue_after_fail
        kwargs['actions'] = [parser.parse_action(e) for e in entity.children]
        return cls, kwargs

    def execute(self, context: LaunchContext):
        continue_after_fail = self.__continue_after_fail
        if not isinstance(continue_after_fail, bool):
            continue_after_fail = perform_substitutions(
                context,
                normalize_to_list_of_substitutions(continue_after_fail)
            ).lower()
            if continue_after_fail in ['true', 'on', '1']:
                continue_after_fail = True
            elif continue_after_fail in ['false', 'off', '1']:
                continue_after_fail = False
            else:
                raise ValueError(
                    'continue_after_fail should be a boolean, got {}'.format(continue_after_fail)
                )
        on_first_action_exited = OnProcessExit(
            target_action=self.__actions[0],
            on_exit=lambda event, context: (
                [InOrderGroup(self.__actions[1:])] if
                event.exitcode == 0 or continue_after_fail else []
            )
        )
        return [
            self.__actions[0],
            RegisterEventHandler(on_first_action_exited)
        ]
