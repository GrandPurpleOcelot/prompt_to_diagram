# Diagram types list
diagram_types = [
    "Let AI decide best Diagram",
    "Class Diagram",
    "Use Case Diagram",
    "Sequence Diagram",
    "Activity Diagram",
    "Component Diagram",
    "State Diagram",
    "Object Diagram",
    "Deployment Diagram",
    "Timing Diagram",
    "Interaction Overview Diagram",
    "Wireframe",
    "Archimate Diagram",
    "Gantt Chart",
    "MindMap Diagram",
    "Work Breakdown Structure (WBS) Diagram",
]

sample_plantuml = '''@startuml
participant User
participant "TSLivechat" as TSL
participant "Alice the Chatbot" as Alice
participant "Human Agent" as Agent

User -> TSL: Sends message
TSL -> Alice: Forwards message

alt If escalation is required
    Alice -> User: Notifies about escalation
    Alice -> TSL: Sends escalation signal
    User -> TSL: Sends another message
    TSL -> Agent: Forwards message to human agent
    Agent -> User: Responds to user
    Agent -> TSL: Sends de-escalation signal
else No escalation required
    Alice -> User: Directly responds to query
end

@enduml
'''

sample_plantuml_agent = '''@startuml
skinparam BoxPadding 15
skinparam ParticipantPadding 0
autonumber

title Solution Agent

participant "Client" AS C
participant "Backend" AS B
participant "Decision Engine" AS D
participant "Agent" AS A
participant "Database" AS DB

== Initial Session == 
C -> B: input question
B -> D: get engine by issue question
B --> B: extract jira_ticket, sample_pull_request
B -> DB: store problem in session context
B -> A: generate issue template 
A --> B: generated template
B --> DB: update issue template
B --> C: return issue template

== Q&A Flow ==

C -> B: user send message
B -> D: get next_action and output
D --> D: choose the engine type
note left
There are 2 engine types:
- CommandEngine: if user start message with allowed command: /retrieve, /search, /url, ...
- AgentEngine: if user sent normal message
end note

alt engine is CommandEngine
B --> B: execute command
B -> DB: update repo context if needed
B --> C: show result to user
B -> A: generate new question
A --> B: question
B --> C: send question to user
else engine is AgentEngine
D --> B: next_action and output
B --> B: invoke specific handler base on next_action
note left
next_action:
- Clarification: output has question to user
- Completed: imply that user provided all information to generate issue 
end note

alt next_action is Clarification
B -> A: generate question and suggested answer
A --> B: questions and suggested answer
B --> C: send questions to user
else next_action is Enrich_Issue
B -> A: generate issue base on provided information
A --> B: enriched issue
B --> C: send enriched issue to user
end
end

B -> DB: store messages
@enduml
'''

in_the_beginning = '''Explain the 12 Apostles of Chris and the meaning of their names in a sentence,
and their relationship to Chris.
In the notes describe their stories'''