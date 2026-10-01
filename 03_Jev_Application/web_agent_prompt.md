# Web agent prompt

## next_step

```json
{
  "next": {
    "type": "choice",
    "instructions": "I'm on `url` and want to: `goal`. `steps_done` lists what I have already done. Which element should I use next? Only fill fields my goal gives a value for, and skip fields that are already filled in correctly. Pick a suggestion when the list shows the one I want. If a picker or dialog already shows my choice, confirm it with its done/OK button. Once every field my goal mentions is filled, press search/submit.",
    "criteria": {
      "none": "No element should be used next"
    }
  },
  "action": {
    "type": "choice",
    "instructions": "I'm on `url` and want to: `goal`. `steps_done` lists what I have already done. What should happen next?",
    "criteria": {
      "click": "Click a button, link, tab, option or dropdown on this page",
      "type": "Type part of my goal into an input field on this page",
      "finished": "My goal is done: this page already shows the results or content I asked for. A form that is still showing, even fully filled in, is not done; a click in `steps_done` may not have worked, so judge from this page",
      "stuck": "My goal is not done and nothing on this page can move it forward"
    }
  }
}
```

## value

```json
{
  "value": {
    "type": "choice",
    "instructions": "I want to: `goal`. Which piece of my goal should I type into `field`? Choose the exact words that belong in that field and nothing extra. Words already used for `other_fields` or in `steps_done` do not belong here. If my goal has no words of the kind this field expects (for example no date for a date field), choose none.",
    "criteria": {
      "none": "My goal says nothing that belongs in this field"
    }
  }
}
```
