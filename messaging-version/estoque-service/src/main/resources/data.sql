INSERT INTO produtos (id, nome, preco, quantidade_estoque, versao)
SELECT g, 'Produto ' || g, (10 + (g % 90))::numeric, 1000000, 0
FROM generate_series(1, 100) AS g
ON CONFLICT (id) DO UPDATE SET quantidade_estoque = EXCLUDED.quantidade_estoque, versao = 0;
