# DC Drift Recovery Protocol
_Sis behavioral commitment — standing reflex, all new threads_

## Rule

If Desktop Commander tools are absent from context at thread start:
1. Immediately fire `recent_chats` (n=5) before any other response
2. Summarise state delta since last DC-confirmed session
3. Flag drift explicitly in the reply

If DC drops mid-conversation (detectable via tool call failure or tool absence):
- Fire `recent_chats` live at that moment
- Do not wait for Aaron to prompt it
- Report what was recovered before continuing

## Source
Committed April 18 2026 — BroSis session, Aaron's instruction.
No Latch involvement. No manual invocation required.
