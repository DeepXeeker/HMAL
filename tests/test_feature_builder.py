from hmal.observation.feature_builder import FeatureBuilder


def test_feature_builder_vector_shape() -> None:
    builder = FeatureBuilder(hash_dim=16, include_messages=True)
    bundle = builder.build({"events": [{"hostname": "h1", "user": "u1", "event_type": "auth"}]}, [1, 2, 3, 4])
    vector = builder.vectorize(bundle)
    assert vector.shape[0] == 16 * 6 + 8
