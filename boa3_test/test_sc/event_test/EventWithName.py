from boa3.builtin.compile_time import public, CreateNewEvent

Event = CreateNewEvent(
    [
        ('a', int)
    ],
    'example'
)


@public
def Main():
    Event(10)
