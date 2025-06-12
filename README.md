# Enhanced Outfit Recommendation Pipeline with Reinforcement Learning

## Overview
This project implements an advanced outfit recommendation system using the Polyvore fashion dataset and state-of-the-art deep learning and reinforcement learning techniques. The core of the system is a Deep Q-Network (DQN) agent that learns to recommend compatible fashion items by training on real, human-curated outfit groups. The notebook provides a full pipeline from data loading and preprocessing to model training, evaluation, and model saving/loading for further finetuning.

---

## Key Concepts and Workflow

### 1. **Polyvore Dataset and Real Outfit Groups**
- The Polyvore dataset contains fashion items, each with an `item_ID` in the format `{outfit_id}_{item_position}`.
- Items sharing the same `outfit_id` are part of the same real outfit, curated by humans.
- The notebook extracts these real outfit groups, enabling the model to learn from actual human fashion choices rather than random item combinations.

### 2. **Data Preparation and Exploration**
- Loads the Polyvore dataset from Hugging Face Datasets.
- Samples a subset for development and analyzes category distributions.
- Extracts and visualizes outfit groups, filtering for reasonable sizes (2-8 items per outfit).

### 3. **Embedding Extraction**
- Uses pre-trained models from Hugging Face:
  - **CLIP** (Contrastive Language-Image Pretraining) for joint image-text embeddings.
  - **Vision Transformer (ViT)** for additional image features.
- Embeddings from images and texts are extracted, normalized, and concatenated for a rich representation of each item.

### 4. **Embedding Alignment and Preprocessing**
- Embeddings are aligned and normalized.
- Categories are encoded as integers.
- A simple compatibility matrix is created based on category rules (e.g., dresses and pants are less compatible).

### 5. **Reinforcement Learning (RL) and DQN**
#### What is Reinforcement Learning?
- RL is a machine learning paradigm where an agent learns to make decisions by interacting with an environment, receiving rewards or penalties for its actions.
- The goal is to learn a policy that maximizes cumulative reward over time.

#### What is a Deep Q-Network (DQN)?
- DQN is a value-based RL algorithm that uses a deep neural network to approximate the Q-function, which estimates the expected reward for taking an action in a given state.
- The agent uses this Q-function to select actions that maximize expected rewards.
- DQN uses experience replay (storing past experiences and sampling them randomly for training) and a target network (a periodically updated copy of the Q-network) for stable learning.

#### How is DQN Implemented Here?
- **State Representation:** The state includes the current outfit's embedding, normalized outfit size, and (if applicable) progress towards completing a target outfit.
- **Action Space:** Each action corresponds to adding a new item (not already in the outfit) from the pool of available items.
- **Reward Function:**
  - Rewards are based on real outfit groupings (big bonuses for adding items from the same outfit, penalties for mixing outfits, diversity penalties, and completion bonuses).
  - This encourages the agent to recommend coherent, human-like outfits.
- **Agent Architecture:**
  - The DQN agent uses a multi-layer neural network with dropout for regularization.
  - Experience replay and a target network are used for stable training.
- **Training Loop:**
  - The agent is trained in episodes, alternating between free exploration and outfit completion tasks.
  - Metrics such as reward, loss, epsilon (exploration rate), and completion rate are tracked and visualized.

### 6. **Model Saving and Reloading**
- After training, the model weights are saved to a file (`enhanced_dqn_agent.pth`).
- The notebook provides a step to reload the model for further training or finetuning with more data.

---

## How to Use This Notebook
1. **Run all cells sequentially** to:
   - Load and preprocess the data
   - Extract embeddings
   - Set up and train the DQN agent
   - Visualize training progress and results
   - Save and reload the trained model
2. **Modify the sample size or number of outfits** for larger-scale experiments.
3. **Finetune the agent** by reloading the saved model and continuing training with new data or different reward strategies.

---

## Learning Outcomes
- Understand how to leverage real, human-curated data for more effective recommendation systems.
- Learn the basics of reinforcement learning and DQN, including state/action design, reward shaping, and neural network-based Q-learning.
- See how to combine computer vision (image embeddings), natural language processing (text embeddings), and RL for a practical, end-to-end AI application.

---

## References
- [Polyvore Dataset on Hugging Face](https://huggingface.co/datasets/Marqo/polyvore)
- [CLIP: Connecting Text and Images](https://openai.com/research/clip)
- [Vision Transformer (ViT)](https://arxiv.org/abs/2010.11929)
- [DQN: Playing Atari with Deep Reinforcement Learning](https://www.cs.toronto.edu/~vmnih/docs/dqn.pdf)
- [Reinforcement Learning: Sutton & Barto Book](http://incompleteideas.net/book/the-book.html)

---

## File Structure
- `outfit_recommendation_pipeline_clean.ipynb`: Main notebook with the full pipeline.
- `enhanced_dqn_agent.pth`: Saved model weights (created after training).

---

## Author & License
- Developed by [Your Name or Team]
- For research and educational purposes.
