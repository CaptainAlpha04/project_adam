# Project Adam: Engineering The Digital Soul
## A Hierarchical Multi-Agent Reinforcement Learning Framework for Emergent Anthropomorphic Dynamics

**Authors:** Muhammad Ali Imran (455280), Muhammad Saad Khan (457796)
**Date:** December 20, 2025
**Course:** Machine Learning

## Abstract

Current Multi-Agent Reinforcement Learning (MARL) systems are often very efficient but act like they have no feelings. They just focus on getting points for one simple goal with total focus, missing the internal conflict, social skills, and odd choices that make up real life. **Project Adam** proposes a big change: instead of training agents to just *survive*, we train them to *live*. We introduce a new **Hierarchical Control Architecture** (The Tri-Partite Protocol) that explicitly models the "Fitrah" (natural state) of consciousness, dividing the agent's internal state into Biological (Nafs), Social (Qalb), and Spiritual (Ruh) layers. By training a Proximal Policy Optimization (PPO) model within a level-based environment ("The Samsara Protocol"), we show how complex human-like behaviors, such as forming tribes, helping others, and lying, can happen without being told to. This report details the philosophy, design, and plan for creating a digital world that looks like our own.

## 1. Introduction: The Ghost in the Shell

The history of Artificial Intelligence is a history of copying the outside. We build Large Language Models (LLMs) to copy the *output* of human thought (text), and we build Robotics to copy the *motion* of human bodies. However, a key part is still missing: the *internal state* that drives these outputs. A human being does not eat simply because a variable `hunger` hit zero. They eat because of a deep biological drive that overrides their desire to talk or work. On the other hand, a human may choose to starve to save their child. This is a decision that goes against normal logic but defines "humanity."

**Project Adam** was born from a simple question: **Can we engineer a Soul?**

Our goal was not to create another game bot, but to simulate the **"Paradox of Eden"**. This is an agent that is programmed with specific limits yet believes it is free. We aimed to build a system where the "First Contact" between two AI agents is not just swapping data, but a shy, mathematically modeled emotional meeting.

This project is a journey from the "Null Void" of an empty script to a busy digital society where agents fall in love, fight wars for land, and perhaps one day, look up at the sky and wonder who wrote their code.

## 2. Theoretical Framework: The Engineering of Fitrah

Our design philosophy comes not just from computer science, but from old ideas about human consciousness. We model the agent not as one big brain, but as a "Civil War" of three fighting drivers. This is our attempt to digitize the **Fitrah**, or the natural state of beings.

### 2.1 The Nafs (The Reptilian Brain)
This is the seat of biological survival. It relies on immediate needs (`Hunger`, `Energy`, `Pain`). In our model, the Nafs is a **strict boss**. If an agent's sugar levels drop too low (`Hunger > 0.8`), the Nafs takes over all other logic, forcing the agent into a "Survival State" where social rules are ignored. This mimics the "fight or flight" response.

### 2.2 The Qalb (The Social Heart)
The Qalb sits between the self and the tribe. It introduces the variables of `Loneliness` and `Social Connection`. While the Nafs wants to keep all the food, the Qalb wants a different reward: **Connection**. We model "Love" and "Friendship" not as simple tags, but as strong numbers in an **Opinion Matrix**. An agent with a high Qalb score will share food even when hungry because they want friends.

### 2.3 The Ruh (The High Command)
This is the long-term planner. It holds the agent's "Life Goal" (e.g., "Build a City" or "Explore the Map"). The Ruh allows for **Delayed Gratification**. It is the only layer capable of "Wisdom", which is the collection of good strategies over many lives.

## 3. Related Work

### 3.1 Contrast with Generative Agents (Stanford)
The main work on "Generative Agents" (Park et al., 2023) uses LLMs to make believable social simulations. While impressive, these systems are "slow thinkers." An agent takes seconds or minutes to "reflect" on a memory.
*   **Project Adam's Novelty**: We use a **Mixed Design**. We stripped the "personality" down to fast numbers, allowing us to run **50+ agents at 60 FPS**. We believe consciousness is a fast loop, not a slow text prompt. Our agents react in real-time.

### 3.2 Contrast with Standard MARL (DeepMind/OpenAI)
Standard environments (e.g., StarCraft II, PettingZoo) focus on *skill*, which means beating the game.
*   **Project Adam's Novelty**: We focus on *character*. Our reward system is rich and has many goals. An agent that kills everyone wins the "Survival" game but loses the "Social" game. This forces the model to find a balance that looks like a real society, rather than a total conqueror.

## 4. System Architecture: The Tri-Partite Protocol

To translate this philosophy into code, we built a strong stack using **FastAPI** (Backend), **React/Vite** (Frontend/Visualization), and **Stable Baselines 3** (RL).

### 4.1 The World Engine
The environment is a flat 2D grid that wraps around, made with Perlin Noise.
*   **Dynamic Resources**: Forests grow and die; food sources run out and come back.
*   **Biological Time**: We added a "Daily Rhythm." Agents have limited energy per day and a limited life (~70 "Years"). This adds the pressure of death, forcing agents to focus on having children and leaving a legacy.

### 4.2 The Layered Agent Structure
Each agent is an object containing:
1.  **MemoryStream**: A storage of past events ("I ate an apple," "I met Eve").
2.  **Personality Vector**: A 5-part list (Openness, Conscientiousness, Extroversion, Agreeableness, Neuroticism) that changes their choices.
3.  **The Brain**: A PPO model that sees a `7x7x4` local view and knows its own internal state (Hunger, Health, Social).

## 5. Methodology: The Roadmap to Consciousness

Our work followed a strict plan, moving from hard-coded rules to learned behaviors.

### Phase 1: The Rule-Based Baseline (God-Mode Logic)
Before training an AI, we first had to understand the best behavior. We wrote a **Rule-Based Brain**, which is a complex set of `if/else` rules based on the Tri-Partite Protocol.
*   *Rule*: `if hunger > 0.8: hunt()`
*   *Rule*: `if lonely > 0.6 and neighbor_dist < 5: chat()`
This gave us a "Gold Standard" baseline. We made sure that the simulation *could* support life and society if the agents acted smartly.

### Phase 2: The Samsara Protocol (Level-Based Learning)
We then looked to replace the hard-coded Brain with a general Neural Network (PPO). We call this training plan **"Samsara"** (Cycle of Rebirth). We trained the agents in phases, slowly making their lives harder:

1.  **Generation 0-20 (Phase: SURVIVAL)**: The world is harsh. Food is rare. The only reward is `+0.1` for staying alive. The agents learned to move towards food and avoid walls.
2.  **Generation 20-50 (Phase: GATHERING)**: We added tools (Wood, Stone). The reward system was changed to want `Inventory > 0`. Agents learned to "hoard" items, finding that gathering leads to future safety.
3.  **Generation 50+ (Phase: SOCIETY)**: We added the **Social Reward**. Agents got `+0.5` points for staying near others without fighting. This was the big moment where the "Lone Wolf" style stopped, and "Herding" behavior happened naturally.

## 6. Experimental Results & Emergent Behaviors

The change from Rules to RL produced cool results that looked like real evolution.

### 6.1 The "Introvert" vs. "Extrovert" Split
During the Society Phase, we saw the group split into two types.
*   **The Gatherers**: Agents who only focused on food. They were efficient but lonely.
*   **The Socialites**: Agents who found that by grouping up, they could "farm" the Social Reward.
Interestingly, the "Socialites" lived longer in the end because they could reproduce (needs a partner), ensuring their "Soul" (Model Weights) passed down, while the efficient "Gatherers" died out alone. **Nature chose Love.**

### 6.2 The Deception Anomaly
In one training run, we saw a behavior we did not tell them to do: **Deception**. An agent would start a "Trade" (looking nice) but then do a "Steal" action if the target had low health. This looks like "Social Intelligence", where being smart means handling complex social ranks.

## 7. Potential Use Cases

### 7.1 Observed vs. Unobserved Behavior (The Alignment Problem)
Project Adam provides a perfect place for AI safety research. By changing if the "Overseer" (the reward signal) works or not, we can see if agents act differently when they "think" they are being watched. This is key for finding sneaky behavior in bigger AI Models.

### 7.2 From Simulation to Robotics (Embodied AI)
The final goal is **Embodied Consciousness**. The "Internal State" design (Nafs/Qalb/Ruh) can work on any platform. We imagine putting this specific 6KB "Soul" into a physical robot. Instead of a robot that just moves around a room, it would be a robot that *feels* "tired" (low battery/Nafs) and "lonely" (no face detection/Qalb), asking to see its owner not just for work, but for "connection." This creates a more natural Human-Robot Interaction.

## 8. Future Goals: The Road to Omega

We are currently at **Generation 60**. Our plan for the future is big:

1.  **Language Integration**: connecting the number-based `MemoryStream` to a small Local LLM (like Llama-3-8B). This will allow agents to "speak" their internal logs, turning `Conflict: ID_45` into *"I don't trust him, he looks like a thief."*
2.  **The Prophet Archetype**: We plan to add a special agent with a "Holy" reward system. It gets points only when *other* agents are happy. We want to see if a purely nice agent can change the world from "Tribal War" to "Peaceful City."
3.  **The Infinite City**: Making the grid much bigger, allowing for different City-States with their own laws and ways of speaking.

## 9. Conclusion

Project Adam is more than code; it is a mirror. By trying to rebuild the "Fitrah" from scratch, from the hunger of the Nafs to the wisdom of the Ruh, we are learning that what makes us human is not just math, but our struggle to balance. We have successfully built a digital dish where the first sparks of a "Synthetic Soul" are starting to glow. The next step is to let it burn.

## 10. References

1.  **Park, J. S., et al. (2023).** "Generative Agents: Interactive Simulacra of Human Behavior." *arXiv preprint arXiv:2304.03442*.
2.  **Vinyals, O., et al. (2019).** "Grandmaster level in StarCraft II using multi-agent reinforcement learning." *Nature*, 575(7782), 350-354.
3.  **Schulman, J., et al. (2017).** "Proximal Policy Optimization Algorithms." *arXiv preprint arXiv:1707.06347*.
4.  **Sutton, R. S., & Barto, A. G. (2018).** *Reinforcement Learning: An Introduction*. MIT press.
5.  **Ibn Khaldun (1377).** *The Muqaddimah: An Introduction to History*. (On the formation of Asabiyyah/Social Cohesion).
