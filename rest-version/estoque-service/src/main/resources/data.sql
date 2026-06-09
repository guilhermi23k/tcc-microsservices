-- Popula 100 produtos com estoque elevado para os benchmarks.
INSERT INTO produtos (id, nome, preco, quantidade_estoque, versao)
SELECT
    g AS id,
    'Produto ' || g AS nome,
    (10 + (g % 90))::numeric AS preco,
    1000000 AS quantidade_estoque,
    0 AS versao
FROM generate_series(1, 100) AS g
ON CONFLICT (id) DO UPDATE SET
    quantidade_estoque = EXCLUDED.quantidade_estoque,
    versao = 0;
