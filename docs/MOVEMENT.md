# Trajectory: Developer-Controlled Intermediates

## Overview

MCP cabinets is part of a broader movement within the AI/Agent ecosystem toward **developer-controlled intermediates** - shifting intermediate processing and control away from opaque AI systems toward developers and users. This approach is gaining significant traction as teams building AI agents and LLM-powered applications recognize that intermediate layers should be controllable and transparent rather than hidden behind algorithmic abstractions.

## Timeline & Examples in AI/Agent Tooling

**Email & Communication for Agents (2024)**: [AgentMail](https://agentmail.to/) provides dedicated email infrastructure built specifically for autonomous agents, addressing the fundamental problem that existing email infrastructure was built for humans, not AI agents. Rather than forcing developers to work around Gmail's limitations like "poor API support, expensive subscriptions, rate limits, sending limits" and "overall terrible developer experience", AgentMail gives developers API-first control with flexible inbox provisioning and integration with agent frameworks.

**Agent Workflow Orchestration (2019-2024)**: Platforms like [n8n](https://n8n.io/) (2019), [Pipedream](https://pipedream.com/) (~2020), and [Make.com](https://www.make.com/) have evolved beyond simple automation to support AI agent workflows. These tools provide code-first approaches where developers can implement custom agent logic, API integrations, and decision trees rather than being constrained by pre-built agent templates or black-box AI routing.

**LLM Infrastructure & Tooling (2020-present)**: The rise of tools like LangChain, CrewAI, and AutoGen represents a shift toward giving developers granular control over LLM interactions, prompt management, and agent behavior rather than accepting monolithic AI solutions. Developers can now compose custom agent architectures, control context flow, and implement domain-specific reasoning patterns.

**AI Context Management (2024)**: The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) exemplifies this trend - providing standardized primitives for connecting AI systems to external tools and data sources, giving developers control over context management rather than relying on black-box integrations. Tools like MCP cabinets extend this philosophy to knowledge curation itself.

## Academic Foundation

Recent academic research validates this movement toward developer-controlled agent architectures:

**"AI Agents: Evolution, Architecture, and Real-World Applications" (Krishnan, 2025)** provides a comprehensive analysis of modular agent architectures where developers select, manage, and compose agent modules (perception, reasoning, action). The paper contrasts these composable systems with monolithic, opaque AI systems and emphasizes the critical importance of context management and persistent memory as core agent features. Krishnan's research directly supports the philosophy behind tools like LangChain, CrewAI, and AutoGen, demonstrating that transparent, composable intermediate layers enable domain experts to design better logic and workflows than black-box AI systems.

**"AI Agents vs. Agentic AI: A Conceptual Taxonomy, Applications and Challenges" (Sapkota et al., 2025)** distinguishes between traditional single-agent systems (often LLM-based, task-specific, prompt-driven) and newer Agentic AI frameworks that emphasize multi-agent orchestration, persistent context, and developer- or domain-expert-managed workflows. The paper chronicles the evolution from generative agents to modular, tool-augmented systems, then to agentic architectures capable of dynamic task decomposition and coordinated workflows. Their taxonomy directly mirrors the arguments for composability over monoliths, human-guided context delivery, and predictable deterministic agent actions that drive platforms like MCP cabinets and similar tools.

Both papers validate that real-world deployment success comes from transparent, developer-curated intermediate layers, collaborative workflows, and sophisticated context management—not brute-force LLM approaches.

This trend reflects a broader recognition within the AI community that **intermediate layers in agent systems should be controllable and transparent** rather than hidden behind algorithmic abstractions. AI developers and teams building autonomous systems often have domain-specific insights that surpass general-purpose AI routing and decision-making.

The movement is driven by several key insights specific to AI/Agent development:

1. **Agent behavior should be deterministic**: Developers need predictable, controllable agent actions rather than black-box AI decision-making
2. **Context is king**: Human curation of context and knowledge often outperforms algorithmic retrieval for specialized domains
3. **Composability over monoliths**: Modular agent architectures with developer-controlled components outperform all-in-one AI solutions
4. **Domain expertise in AI workflows**: Subject matter experts can design better agent logic than general-purpose AI systems

## The Context Optimization Era in AI

As we pivot towards optimizing context and away from pure brute-force LLMs, this movement becomes increasingly relevant for AI developers. The next frontier in AI performance isn't just bigger models, but **smarter context delivery and agent orchestration**. 

This evolution recognizes that better agent performance often comes from thoughtful, human-guided context optimization and workflow design rather than flooding AI systems with raw data and hoping algorithmic relevance scoring finds the signal in the noise.

Modern AI development is shifting from "throw everything at the LLM" to "carefully curate what the AI sees and how it processes information" - exactly the philosophy that drives tools like MCP cabinets, AgentMail, and MCP itself.