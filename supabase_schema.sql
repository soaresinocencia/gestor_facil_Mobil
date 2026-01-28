-- Tabela de Produtos
-- Armazena o catálogo e o estoque.
create table if not exists produtos (
    id bigint primary key generated always as identity,
    nome text not null,
    preco_custo numeric,
    preco_venda numeric,
    quantidade integer default 0,
    minimo_alerta integer default 5,
    detalhes text,
    categoria text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
-- Tabela de Vendas
-- Armazena o registro de vendas. Usaremos JSONB para os itens para simplificar a sincronização.
create table if not exists vendas (
    id bigint primary key generated always as identity,
    local_id integer,
    -- ID original no SQLite (para evitar duplicatas)
    data_hora text,
    total_venda numeric,
    lucro_total numeric,
    cliente text,
    vendedor_nome text,
    itens jsonb,
    -- Lista de produtos vendidos: [{"nome": "Coca", "qtd": 1, "preco": 50}, ...]
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
-- Tabela de Usuários
-- Para login e controle de acesso.
create table if not exists usuarios (
    id bigint primary key generated always as identity,
    usuario text unique,
    nome_completo text,
    senha text,
    -- Hash
    cargo text,
    status text default 'ativo',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
-- Habilitar RLS (Row Level Security) é uma boa prática, 
-- mas para este primeiro passo vamos deixar aberto para facilitar a conexão via API Key Anon.
alter table produtos enable row level security;
alter table vendas enable row level security;
alter table usuarios enable row level security;
-- Políticas de acesso (Permitir tudo para quem tem a chave API por enquanto)
create policy "Acesso Total Produtos" on produtos for all using (true);
create policy "Acesso Total Vendas" on vendas for all using (true);
create policy "Acesso Total Usuarios" on usuarios for all using (true);