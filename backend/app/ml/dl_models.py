"""
Deep learning model architectures for sequence-based stock price prediction.

Each function builds and COMPILES a Keras model, ready to .fit(). We keep
architecture definitions separate from training logic (app/ml/train_dl.py)
for the same reason Phase 5 separated get_model() from train_model(): one
clear place to adjust architecture/hyperparameters later.
"""

from tensorflow import keras
from tensorflow.keras import layers


def build_lstm_model(window_size: int = 60) -> keras.Model:
    """
    LSTM (Long Short-Term Memory) architecture.

    Architecture:
    - LSTM layer (64 units): processes the sequence step-by-step, maintaining
      an internal memory state that decides what to keep/forget at each step.
    - Dropout (0.2): randomly disables 20% of neurons during training to
      prevent overfitting -- a standard regularization technique for deep
      learning, conceptually similar in PURPOSE to Random Forest's
      max_depth/min_samples_leaf limits from Phase 5, even though the
      mechanism is completely different.
    - LSTM layer (32 units): a second, smaller LSTM layer to learn
      higher-level temporal patterns from the first layer's output.
    - Dense layer (1 unit): the final output -- a single predicted price.

    Why 64 then 32 units? A common, sensible default: the first layer
    captures broader patterns, the second narrows down to what's most
    relevant for the final prediction. There's no universally "correct"
    size -- this is a reasonable starting point, not a law of nature.
    """
    model = keras.Sequential([
        layers.Input(shape=(window_size, 1)),
        layers.LSTM(64, return_sequences=True),
        layers.Dropout(0.2),
        layers.LSTM(32, return_sequences=False),
        layers.Dropout(0.2),
        layers.Dense(1),
    ])
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


def build_gru_model(window_size: int = 60) -> keras.Model:
    """
    GRU (Gated Recurrent Unit) architecture -- structurally similar to LSTM
    above, but using GRU layers instead. GRUs have fewer internal gates than
    LSTMs (no separate "cell state"), making them faster to train with often
    comparable accuracy. We use the same layer sizes as LSTM for a fair
    architecture-vs-architecture comparison later.
    """
    model = keras.Sequential([
        layers.Input(shape=(window_size, 1)),
        layers.GRU(64, return_sequences=True),
        layers.Dropout(0.2),
        layers.GRU(32, return_sequences=False),
        layers.Dropout(0.2),
        layers.Dense(1),
    ])
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


class PositionalEncoding(layers.Layer):
    """
    Adds positional information to each timestep so the Transformer can
    tell WHERE in the sequence a value occurred (day 1 vs day 60), not just
    WHAT the value was.

    Why this matters: LSTM/GRU process the sequence one step at a time, so
    order is built into their architecture automatically. A Transformer's
    attention mechanism looks at all 60 days at once and has NO inherent
    sense of order unless we explicitly add it -- without this, "price was
    180 three days ago" and "price was 180 fifty days ago" look identical
    to the model. This was the missing piece in our first version, and
    likely the main reason it failed to learn (R2 of -6.05).

    We use the standard sine/cosine encoding from the original "Attention
    Is All You Need" paper: each position gets a unique pattern built from
    sine and cosine waves at different frequencies, added directly onto the
    input values before they enter the attention layer.
    """
    def __init__(self, sequence_length, d_model, **kwargs):
        super().__init__(**kwargs)
        self.sequence_length = sequence_length
        self.d_model = d_model

        import numpy as np
        position = np.arange(sequence_length)[:, np.newaxis]
        div_term = np.exp(np.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))

        pe = np.zeros((sequence_length, d_model))
        pe[:, 0::2] = np.sin(position * div_term)
        pe[:, 1::2] = np.cos(position * div_term)

        self.pos_encoding = keras.ops.convert_to_tensor(pe[np.newaxis, ...], dtype="float32")

    def call(self, x):
        return x + self.pos_encoding

    def get_config(self):
        config = super().get_config()
        config.update({"sequence_length": self.sequence_length, "d_model": self.d_model})
        return config


def build_transformer_model(window_size: int = 60) -> keras.Model:
    """
    A simplified Transformer encoder for time series, NOW WITH positional
    encoding (see the PositionalEncoding class above for why this matters).

    Architecture:
    - Dense projection: lifts the single price value per timestep into a
      32-dimensional representation.
    - PositionalEncoding: injects order information (the fix).
    - MultiHeadAttention: each of the 4 "heads" learns to focus on different
      patterns in the window.
    - LayerNormalization + residual connection: stabilizes training.
    - GlobalAveragePooling1D: condenses the sequence into a single vector.
    - Dense layers: final prediction.

    Honest expectation-setting still applies: even with this fix,
    Transformers typically need more data than LSTM/GRU to show their full
    advantage. This fix addresses a genuine bug (missing positional info),
    but doesn't guarantee the Transformer will outperform LSTM/GRU on a
    dataset this size -- that's still an open, honest question we'll
    answer by testing, not by assuming either outcome.
    """
    d_model = 32
    inputs = keras.Input(shape=(window_size, 1))

    x = layers.Dense(d_model)(inputs)
    x = PositionalEncoding(window_size, d_model)(x)

    attention_output = layers.MultiHeadAttention(num_heads=4, key_dim=d_model)(x, x)
    x = layers.LayerNormalization()(x + attention_output)

    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dense(32, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(1)(x)

    model = keras.Model(inputs, outputs)
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


def get_dl_model(model_type: str, window_size: int = 60) -> keras.Model:
    """Factory function, mirroring Phase 5's get_model() pattern."""
    builders = {
        "lstm": build_lstm_model,
        "gru": build_gru_model,
        "transformer": build_transformer_model,
    }
    if model_type not in builders:
        raise ValueError(
            f"Unknown model_type '{model_type}'. Expected one of: {list(builders.keys())}."
        )
    return builders[model_type](window_size)
