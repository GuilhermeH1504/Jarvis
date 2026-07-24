# Embeddings locais leves (hashing trick), sem depender de nenhuma API externa
# de embeddings. Nao e tao preciso quanto um embedding de verdade, mas e
# suficiente pra achar memorias parecidas e nao custa tokens nem chamadas de API.

import re
import zlib

import numpy as np

VECTOR_SIZE = 256
_TOKEN_RE = re.compile(r"[a-zA-ZÀ-ÿ0-9]+")


def embed(text: str) -> np.ndarray:
    # zlib.crc32 fica estavel entre execucoes; o hash() embutido do Python e'
    # aleatorizado por processo e quebraria a busca apos salvar/recarregar.
    vector = np.zeros(VECTOR_SIZE, dtype=np.float32)
    for token in _TOKEN_RE.findall(text.lower()):
        index = zlib.crc32(token.encode("utf-8")) % VECTOR_SIZE
        vector[index] += 1.0

    norm = np.linalg.norm(vector)
    return vector / norm if norm > 0 else vector
