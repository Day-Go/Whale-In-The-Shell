
## Overview
Whale in the Shell (WITS) is a crypto trading simulation game leveraging Large Language Models (LLMs) as agents and game masters. The game aims to simulate a dynamic trading environment, where agents, influenced by market news, opinions, and their unique traits, interact and make decisions.

## Features
- **Agent-Based Simulation:** Agents with unique personalities and decision-making processes, simulating diverse market participants.
- **Dynamic Event Generation:** A game master module that creates realistic market scenarios, affecting agent actions and market conditions.
- **Simple World Model:** The world model centers around a social media platform, forming the core of the simulated environment. Interactions and information flow on the platform influence market dynamics and agent decisions.
- **Simulated Crypto Market:** The game features a persistent market environment with a variety of tradable assets created by the game master. Agents can interact with this market, making buying or selling decisions based on their analysis and the evolving market conditions.


## Technical Specifications
- **Frontend:** .NET Blazor server.
- **Backend:** gRPC service written in Python.
- **Database:** Supabase.
- **API Integration:** OpenAI API for agent behavior and decision-making processes.

