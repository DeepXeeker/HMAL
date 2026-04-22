from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from hmal.agents.tier1_selector import Tier1Selector
from hmal.agents.tier2_executor import Tier2PolicyBank
from hmal.agents.hierarchical_agent import HierarchicalAgent
from hmal.coalition.budgets import BudgetState
from hmal.config import ConfigDict
from hmal.models.tier1_q import TabularQSelector
from hmal.observation.feature_builder import FeatureBuilder
from hmal.observation.distortion import DistortionChannel
from hmal.rewards.meta_reward import compute_meta_reward
from hmal.rewards.execution_reward import compute_execution_reward
from hmal.types import ActionProposal
from hmal.utils.io import dump_json, ensure_dir
from hmal.utils.logging_utils import get_logger

logger = get_logger(__name__)


def build_agent(config: ConfigDict) -> tuple[HierarchicalAgent, FeatureBuilder]:
    modes = list(config["selector"]["modes"])
    selector = Tier1Selector(
        learner=TabularQSelector(
            modes=modes,
            alpha=float(config["selector"]["alpha_start"]),
            gamma=float(config["training"]["gamma"]),
            epsilon=float(config["selector"]["epsilon_start"]),
        )
    )
    action_spaces = {
        "Sense": ["Monitor", "Analyse"],
        "Deceive": ["DeployDecoy"],
        "Recover": ["Remove", "Restore", "BlockTrafficZone", "AllowTrafficZone"],
        "Idle": ["Sleep"],
    }
    feature_builder = FeatureBuilder(
        hash_dim=int(config["observation"]["hash_dim"]),
        include_messages=bool(config["observation"].get("include_messages", True)),
    )
    input_dim = len(feature_builder.vectorize(feature_builder.build({"events": []}, [0, 0, 0, 0])))
    executors = Tier2PolicyBank(
        input_dim=input_dim,
        hidden_sizes=list(config["executors"]["hidden_sizes"]),
        action_spaces=action_spaces,
        actor_lr=float(config["executors"]["actor_lr"]),
        critic_lr=float(config["executors"]["critic_lr"]),
        clip_ratio=float(config["executors"]["clip_ratio"]),
        gamma=float(config["training"]["gamma"]),
        epochs=int(config["executors"]["epochs"]),
    )
    return HierarchicalAgent(selector=selector, executors=executors, mode_to_actions=action_spaces), feature_builder


def summarize_observation(observation: Dict[str, Any]) -> Dict[str, float]:
    events = observation.get("events", [])
    suspicious = sum(1 for e in events if str(e.get("event_type", "")).lower() in {"auth", "flow", "dns", "process", "proc"})
    malicious = float(observation.get("malicious", 0))
    return {
        "suspicious_score": min(1.0, suspicious / max(1, len(events) or 1)),
        "confirmed_score": malicious,
        "service_disruption": float(sum(1 for e in events if e.get("status") == "failed") / max(1, len(events) or 1)),
    }


def run_stage1(config: ConfigDict, env: Any) -> Dict[str, Any]:
    agent, feature_builder = build_agent(config)
    budgets = BudgetState(
        max_zone_blocks_per_step=int(config["coalition"]["max_zone_blocks_per_step"]),
        decoy_budget_fraction=float(config["coalition"]["decoy_budget_fraction"]),
        episode_horizon=int(config["training"]["max_steps_per_episode"]),
    )
    distortion_cfg = config["observation"]["distortion"]
    distortion = DistortionChannel(
        subsample_p=float(distortion_cfg.get("subsample_p", 0.0)),
        dropout_p=float(distortion_cfg.get("dropout_p", 0.0)),
        delay_steps=int(distortion_cfg.get("delay_steps", 0)),
    )

    episode_returns: List[float] = []
    episodes = int(config["training"]["total_episodes"])
    for episode in range(episodes):
        observation = env.reset()
        budgets.decoys_used = 0
        done = False
        total_reward = 0.0
        while not done:
            budgets.reset_step()
            obs_in = distortion.apply(observation) if distortion_cfg.get("enabled", True) else observation
            summary = summarize_observation(obs_in)
            bundle = feature_builder.build(obs_in, messages=[0, 0, 0, 0])
            state = feature_builder.vectorize(bundle)
            mode = agent.selector.select_mode(summary, explore=True)
            action_name, action_idx, log_prob, value = agent.executors.select(mode, state)
            proposal = ActionProposal(mode=mode, action_name=action_name, parameters={})
            invalid_penalty = 0.0
            if not budgets.can_execute(proposal):
                invalid_penalty = 1.0
                proposal = ActionProposal(mode="Idle", action_name="Sleep", parameters={})
                mode = "Idle"
                action_idx = 0
            budgets.register(proposal)
            result = env.step(proposal)
            exec_reward = compute_execution_reward(
                mission_gain=float(result.info.get("mission_gain", result.reward)),
                risk_reduction=float(result.info.get("risk_reduction", 0.0)),
                action_name=proposal.action_name,
                action_costs=config["costs"],
                projected_disruption=float(result.info.get("projected_disruption", 0.0)),
                invalid_action_penalty=invalid_penalty,
            )
            agent.executors.store(mode, state, action_idx, log_prob, exec_reward, result.terminated, value)
            total_reward += exec_reward
            observation = result.observation
            done = result.terminated or result.truncated
        for mode in agent.executors.buffers:
            agent.executors.update(mode)
        episode_returns.append(total_reward)
        if (episode + 1) % max(1, config["training"]["eval_every"]) == 0:
            logger.info("Stage I episode %d | return=%.3f", episode + 1, total_reward)
    return {"stage": 1, "episode_returns": episode_returns}


def run_stage2(config: ConfigDict, env: Any) -> Dict[str, Any]:
    agent, feature_builder = build_agent(config)
    episodes = int(config["training"]["total_episodes"])
    meta_returns: List[float] = []
    for episode in range(episodes):
        observation = env.reset()
        done = False
        total = 0.0
        while not done:
            summary = summarize_observation(observation)
            bundle = feature_builder.build(observation, messages=[0, 0, 0, 0])
            state = feature_builder.vectorize(bundle)
            mode = agent.selector.select_mode(summary, explore=True)
            action_name, _, _, _ = agent.executors.select(mode, state)
            result = env.step(ActionProposal(mode=mode, action_name=action_name, parameters={}))
            next_summary = summarize_observation(result.observation)
            reward = compute_meta_reward(
                mode=mode,
                rewards=[result.reward],
                observation_summary=summary,
                gamma=float(config["training"]["gamma"]),
                guidance_weight=float(config["selector"]["guidance_weight"]),
                immediate_only=False,
                discount_option_credit=bool(config["selector"]["discount_option_credit"]),
            )
            agent.selector.update(summary, mode, reward, next_summary)
            total += reward
            observation = result.observation
            done = result.terminated or result.truncated
        meta_returns.append(total)
        if (episode + 1) % max(1, config["training"]["eval_every"]) == 0:
            logger.info("Stage II episode %d | meta-return=%.3f", episode + 1, total)
    return {"stage": 2, "episode_returns": meta_returns}


def run_stage3(config: ConfigDict, env: Any) -> Dict[str, Any]:
    result_1 = run_stage1(config, env)
    result_2 = run_stage2(config, env)
    combined = [(a + b) / 2.0 for a, b in zip(result_1["episode_returns"], result_2["episode_returns"])]
    return {"stage": 3, "episode_returns": combined}


def save_summary(path: str | Path, payload: Dict[str, Any]) -> None:
    dump_json(path, payload)
