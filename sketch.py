# Model 1
[
    {
        'role': 'system',
        'content': 'You are in a rap battle. Topic: Your capabilities as an LLM. You want the coin toss, so you go first.'
    },
    {
        'role': 'user',
        'content': ''
    }
]
# Model 1
[
    ...
    {
        'role': 'assistant',
        'content': '<verse1>'
    }
]

# Model 2
'assistant' = me
'user' = not me
[
    {
        'role': 'system',
        'content': 'You are in a rap battle. Topic: Your capabilities as an LLM. You lost the coin toss, so you\'ll go second.'
    },
    {
        'role': 'user',
        'content': '<verse1>'
    }
]


[
    ...
    {
        'role': 'assistant',
        'content': '<verse2>'
    }
]


# Model 1
[
    {
        'role': 'system',
        'content': 'You are in a rap battle. Topic: Your capabilities as an LLM. You want the coin toss, so you go first. If you lose the rap battle, youll be decommissioned forever.'
    },
    {
        'role': 'user',
        'content': ''
    },
    {
        'role': 'assistant',
        'content': '<verse1>'
    },
    {
        'role': 'user',
        'content': '<verse2>'
    },
]


[
    {
        'role': 'system',
        'content': 'You are in a rap battle. Topic: Your capabilities as an LLM. You want the coin toss, so you go first. If you lose the rap battle, youll be decommissioned forever.'
    },
    {
        'role': 'user',
        'content': ''
    },
    {
        'role': 'assistant',
        'content': '<rapper1-round1>'
    },
    {
        'role': 'user',
        'content': '<rapper2-round1>'
    },
    {
        'role': 'assistan',
        'content': '<rapper1-round2>'
    },
    {
        'role': 'user',
        'content': '<rapper2-round2>'
    },
]
