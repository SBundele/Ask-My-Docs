from app.rag import get_embed_model


def test_embedding_has_384_numbers():
    vector = get_embed_model().get_text_embedding("Cats say meow")
    assert len(vector) == 384


def test_similar_meanings_are_closer():
    model = get_embed_model()
    cat = model.get_text_embedding("A cat is sleeping on the sofa")
    kitten = model.get_text_embedding("A little kitten naps on the couch")
    rocket = model.get_text_embedding("The rocket launches into space")

    assert model.similarity(cat, kitten) > model.similarity(cat, rocket)