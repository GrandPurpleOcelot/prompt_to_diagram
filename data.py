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

in_the_beginning = '''Explain the 12 Apostles of Chris and the meaning of their names in a sentence,
and their relationship to Chris.
In the notes describe their stories'''