from hmal.rewards.meta_reward import compute_meta_reward


def test_meta_reward_prefers_discounted_env_term() -> None:
    reward = compute_meta_reward(
        mode="Sense",
        rewards=[1.0, 0.5],
        observation_summary={"suspicious_score": 1.0, "confirmed_score": 0.0, "service_disruption": 0.0},
        gamma=0.99,
        guidance_weight=0.1,
        immediate_only=False,
        discount_option_credit=True,
    )
    assert reward > 1.0
